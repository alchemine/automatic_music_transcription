from pydub import AudioSegment
import pretty_midi
import random
import os
import fluidsynth

# Inputs
random_seed = 42
n_samples = 1
n_instruments = 3
chord_length = 4
chord_duration = 2.0  # seconds per chord
sample_rate = 44100

# Define a directory to store generated MIDI and WAV files
SOUNDFONT_PATH = "/Users/dj.yoon/.fluidsynth/soundfont.sf2"
OUTPUT_DIR = "output"
MIDI_DIR = os.path.join(OUTPUT_DIR, "midi")
WAV_DIR = os.path.join(OUTPUT_DIR, "wav")
MERGED_DIR = os.path.join(OUTPUT_DIR, "merged")

os.makedirs(MIDI_DIR, exist_ok=True)
os.makedirs(WAV_DIR, exist_ok=True)
os.makedirs(MERGED_DIR, exist_ok=True)


def generate_chord_progression(length=4) -> list[str]:
    """Generate a random chord progression."""
    chords = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    qualities = ["maj", "min", "dim", "aug"]
    progression = []
    for _ in range(length):
        root = random.choice(chords)
        quality = random.choice(qualities)
        chord = f"{root}{quality}"
        progression.append(chord)
    return progression


def select_instruments(n_instruments: int) -> list[int]:
    """Select n_instruments unique General MIDI program numbers."""
    # General MIDI program numbers range from 0 to 127
    available_instruments = list(range(0, 128))
    selected = random.sample(available_instruments, n_instruments)
    # return selected
    return [0, 24, 32]  # Piano, Acoustic Guitar, Acoustic Bass


def chord_to_notes(chord: str) -> list[int]:
    """Convert a chord string to MIDI note numbers."""
    chord_map = {"maj": [0, 4, 7], "min": [0, 3, 7], "dim": [0, 3, 6], "aug": [0, 4, 8]}
    for quality in ["maj", "min", "dim", "aug"]:
        if chord.endswith(quality):
            root = chord[: -len(quality)]
            intervals = chord_map[quality]
            break
    else:
        # Default to major
        root = chord
        intervals = chord_map["maj"]
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    if root not in note_names:
        root = "C"  # default
    root_index = note_names.index(root)
    root_midi = 60 + root_index  # C4 is 60
    notes = [root_midi + interval for interval in intervals]
    return notes


def generate_midi_instrument(
    chord_progression: list[str], program: int, filename: str, chord_duration=2.0
):
    """Generate a MIDI file for a specific instrument and chord progression."""
    midi = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=program)

    start_time = 0
    for chord_str in chord_progression:
        notes = chord_to_notes(chord_str)
        for note_number in notes:
            note = pretty_midi.Note(
                velocity=100,
                pitch=note_number,
                start=start_time,
                end=start_time + chord_duration,  # 정확히 chord_duration 동안 지속
            )
            instrument.notes.append(note)
        start_time += chord_duration

    midi.instruments.append(instrument)
    midi.write(filename)


def midi_to_wav_pyfluidsynth(midi_file, wav_file, sample_rate):
    """Convert MIDI file to WAV using pyfluidsynth with reverb disabled."""
    fs = fluidsynth.Synth(samplerate=sample_rate)
    fs.start(driver="file", filename=wav_file)
    fs.sfload(SOUNDFONT_PATH)
    fs.program_select(0, 0, 0, 0)  # 채널 0, soundfont 0, bank 0, preset 0

    fs.set_reverb(0.0)  # 리버브 레벨 0.0으로 설정 (가능한 경우)

    fs.midi_file_load(midi_file)
    fs.midi_file_play(midi_file)
    fs.delete()


def ensure_fixed_length(wav_file: str, fixed_length: float):
    """
    Ensure the WAV file has exactly fixed_length seconds.
    If longer, trim it. If shorter, pad with silence.
    """
    audio = AudioSegment.from_wav(wav_file)
    current_length = len(audio) / 1000.0  # milliseconds to seconds

    if current_length > fixed_length:
        # 자르기
        audio = audio[: int(fixed_length * 1000)]
    elif current_length < fixed_length:
        # 패딩
        silence = AudioSegment.silent(duration=(fixed_length - current_length) * 1000)
        audio += silence

    audio.export(wav_file, format="wav")


def merge_wav_files(
    inst_wav_files: list[str], merged_wav_file: str, fixed_length: float
):
    """Merge WAV files by overlaying them and ensure the merged file has fixed_length."""
    mix = None
    for wav_file in inst_wav_files:
        audio = AudioSegment.from_wav(wav_file)
        if mix is None:
            mix = audio
        else:
            mix = mix.overlay(audio)
    # Ensure the merged audio has the fixed_length
    current_length = len(mix) / 1000.0
    if current_length > fixed_length:
        mix = mix[: int(fixed_length * 1000)]
    elif current_length < fixed_length:
        silence = AudioSegment.silent(duration=(fixed_length - current_length) * 1000)
        mix += silence
    mix.export(merged_wav_file, format="wav")


def generate_and_merge_wav_files(
    random_seed, n_samples, n_instruments, sample_rate, chord_length, chord_duration
):
    """Generate and merge WAV files."""
    random.seed(random_seed)

    # Select instruments once
    instruments = select_instruments(n_instruments)
    print(f"Selected instruments (program numbers): {instruments}")

    for sample_idx in range(n_samples):
        print(f"\nGenerating sample {sample_idx+1}/{n_samples}")
        # Generate chord progression
        chord_progression = generate_chord_progression(length=chord_length)
        print(f"Chord progression: {chord_progression}")

        inst_wav_files = []
        for inst_idx, program in enumerate(instruments):
            midi_filename = os.path.join(
                MIDI_DIR, f"sample{sample_idx}_inst{program}.mid"
            )
            wav_filename = os.path.join(
                WAV_DIR, f"sample{sample_idx}_inst{program}.wav"
            )
            # Generate MIDI
            generate_midi_instrument(
                chord_progression, program, midi_filename, chord_duration
            )
            print(f"Generated MIDI for instrument {program}: {midi_filename}")
            # Convert MIDI to WAV using pyfluidsynth
            midi_to_wav_pyfluidsynth(midi_filename, wav_filename, sample_rate)
            print(f"Converted to WAV: {wav_filename}")
            # Ensure WAV has fixed length
            total_duration = chord_length * chord_duration  # 예: 4 * 2.0 = 8.0 초
            ensure_fixed_length(wav_filename, total_duration)
            print(
                f"Ensured fixed length ({total_duration} seconds) for: {wav_filename}"
            )
            inst_wav_files.append(wav_filename)

        # Merge WAV files
        merged_wav_filename = os.path.join(MERGED_DIR, f"sample{sample_idx}_merged.wav")
        total_duration = chord_length * chord_duration  # 예: 4 * 2.0 = 8.0 초
        merge_wav_files(
            inst_wav_files, merged_wav_filename, fixed_length=total_duration
        )
        print(f"Merged WAV saved to: {merged_wav_filename}")


if __name__ == "__main__":
    generate_and_merge_wav_files(
        random_seed, n_samples, n_instruments, sample_rate, chord_length, chord_duration
    )
