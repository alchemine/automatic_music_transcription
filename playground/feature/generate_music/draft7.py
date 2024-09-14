from midi2audio import FluidSynth
from pydub import AudioSegment
import pretty_midi
import random
import os

# Inputs
random_seed = 42
n_samples = 1
n_instruments = 8  # 피아노, 일렉기타, 베이스, 드럼, 바이올린, 비올라, 첼로, 섹소폰
chord_length = 4
chord_duration = 2.0  # seconds per chord
sample_rate = 16000  # 16kHz

# Define a directory to store generated MIDI and WAV files
SOUNDFONT_PATH = "/Users/dj.yoon/.fluidsynth/soundfont.sf2"
OUTPUT_DIR = "output"
MIDI_DIR = os.path.join(OUTPUT_DIR, "midi")
WAV_DIR = os.path.join(OUTPUT_DIR, "wav")
MERGED_DIR = os.path.join(OUTPUT_DIR, "merged")

os.makedirs(MIDI_DIR, exist_ok=True)
os.makedirs(WAV_DIR, exist_ok=True)
os.makedirs(MERGED_DIR, exist_ok=True)

# 코드 진행 패턴 정의 (스케일 디그리 기반)
CODE_PROGRESSION_PATTERNS = [
    ["I", "V", "vi", "IV"],  # I–V–vi–IV
    ["I", "vi", "IV", "V"],  # I–vi–IV–V
    ["vi", "IV", "I", "V"],  # vi–IV–I–V
    ["IV", "V", "I", "vi"],  # IV–V–I–vi
    ["I", "IV", "V", "IV"],  # I–IV–V–IV
]

# 메이저 스케일의 디그리에 따른 코드 매핑
MAJOR_SCALE = ["C", "D", "E", "F", "G", "A", "B"]


def get_major_scale(key: str) -> list[str]:
    """주어진 키에 해당하는 메이저 스케일을 반환합니다."""
    # 모든 메이저 키가 동일한 스케일 패턴을 따릅니다.
    # 여기서는 단순히 입력된 키의 메이저 스케일을 반환합니다.
    # 실제로는 키에 따라 스케일을 옮겨야 하지만, 간단화를 위해 C 메이저 스케일을 기준으로 합니다.
    # 더 정확한 스케일을 원하면 음악 이론을 기반으로 스케일을 생성해야 합니다.
    # 예시에서는 간단히 키의 메이저 스케일을 하드코딩하지 않고, chord_to_notes에서 처리합니다.
    return MAJOR_SCALE


def degree_to_chord(degree: str, key: str) -> str:
    """스케일 디그리를 실제 코드 이름으로 변환합니다."""
    # 메이저 스케일의 디그리에 따른 코드 품질
    DEGREE_CHORD_QUALITY = {
        "I": "maj",
        "ii": "min",
        "iii": "min",
        "IV": "maj",
        "V": "maj",
        "vi": "min",
        "vii°": "dim",
    }

    # 디그리에 따른 루트 노트 계산
    scale = get_major_scale(key)
    degree_map = {
        "I": 0,
        "ii": 1,
        "iii": 2,
        "IV": 3,
        "V": 4,
        "vi": 5,
        "vii°": 6,
    }

    if degree not in degree_map:
        raise ValueError(
            f"Unsupported degree: {degree}. Supported degrees are: {list(degree_map.keys())}"
        )

    root_index = degree_map[degree]
    root_note = scale[root_index]
    quality = DEGREE_CHORD_QUALITY.get(degree, "maj")  # 기본적으로 메이저

    # 코드 이름 생성
    chord = f"{root_note}{quality}"
    return chord


def generate_chord_progression(length=4) -> list[str]:
    """Generate a common chord progression in a random key."""
    # 메이저 키 목록
    MAJOR_KEYS = [
        "C",
        "G",
        "D",
        "A",
        "E",
        "B",
        "F#",
        "C#",
        "F",
        "Bb",
        "Eb",
        "Ab",
        "Db",
        "Gb",
        "Cb",
    ]

    # 무작위로 키 선택
    key = random.choice(MAJOR_KEYS)

    # 무작위로 코드 진행 패턴 선택
    pattern = random.choice(CODE_PROGRESSION_PATTERNS)

    # 패턴에 따라 실제 코드 진행 생성
    progression = [degree_to_chord(degree, key) for degree in pattern[:length]]

    print(
        f"Selected Key: {key}, Progression Pattern: {pattern[:length]}, Generated Progression: {progression}"
    )

    return progression


def select_instruments(n_instruments: int) -> list[dict]:
    """
    Select n_instruments specific General MIDI program numbers.
    Returns a list of dictionaries containing instrument information.
    """
    # Define specific instruments
    instruments = [
        {"name": "Piano", "program": 0, "channel": 0},
        {"name": "Electric Guitar", "program": 27, "channel": 1},
        {"name": "Bass", "program": 32, "channel": 2},
        {
            "name": "Drums",
            "program": None,
            "channel": 9,
        },  # Drums are on channel 10 (index 9)
        {"name": "Violin", "program": 40, "channel": 3},
        {"name": "Viola", "program": 41, "channel": 4},
        {"name": "Cello", "program": 42, "channel": 5},
        {"name": "Saxophone", "program": 66, "channel": 6},
    ]

    if n_instruments > len(instruments):
        raise ValueError(f"Maximum supported instruments: {len(instruments)}")

    selected = instruments[:n_instruments]  # Select the first n_instruments
    return selected


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
    chord_progression: list[str],
    instrument_info: dict,
    filename: str,
    chord_duration=2.0,
):
    """Generate a MIDI file for a specific instrument and chord progression with instrument-specific behavior."""
    midi = pretty_midi.PrettyMIDI()
    program = instrument_info["program"]
    channel = instrument_info["channel"]

    # For drums, we don't use program numbers and use specific MIDI note numbers
    if instrument_info["name"] == "Drums":
        instrument = pretty_midi.Instrument(program=0, is_drum=True, name="Drums")
    else:
        instrument = pretty_midi.Instrument(
            program=program, name=instrument_info["name"]
        )

    start_time = 0
    delay_between_notes = 0.2  # Delay between notes in seconds for arpeggios

    for chord_str in chord_progression:
        notes = chord_to_notes(chord_str)
        num_notes = len(notes)
        print(
            f"Adding notes: {notes} for chord: {chord_str} on {instrument_info['name']}"
        )

        if instrument_info["name"] == "Piano":
            # Piano plays full chords simultaneously
            for note_number in notes:
                velocity = random.randint(80, 120)
                note = pretty_midi.Note(
                    velocity=velocity,
                    pitch=note_number,
                    start=start_time,
                    end=start_time + chord_duration,
                )
                instrument.notes.append(note)

        elif instrument_info["name"] == "Electric Guitar":
            # Electric Guitar plays arpeggios
            for i, note_number in enumerate(notes):
                velocity = random.randint(80, 120)
                note_start = start_time + i * delay_between_notes
                note_end = note_start + (
                    chord_duration - (num_notes - 1) * delay_between_notes
                )
                note = pretty_midi.Note(
                    velocity=velocity,
                    pitch=note_number,
                    start=note_start,
                    end=note_end,
                )
                instrument.notes.append(note)

        elif instrument_info["name"] == "Bass":
            # Bass plays the root note only
            root_note = notes[0]
            velocity = random.randint(80, 120)
            note = pretty_midi.Note(
                velocity=velocity,
                pitch=root_note,
                start=start_time,
                end=start_time + chord_duration,
            )
            instrument.notes.append(note)

        elif instrument_info["name"] == "Drums":
            # Drums play a basic pattern: Kick on 1, Snare on 3, Hi-hat on every 0.5 seconds
            # MIDI note numbers for drums (from General MIDI Percussion Key Map)
            # 36: Bass Drum 1, 38: Acoustic Snare, 42: Closed Hi-hat
            pattern = [
                {"note": 36, "time": start_time},  # Kick
                {"note": 38, "time": start_time + 1.0},  # Snare
                {"note": 42, "time": start_time + 0.0},  # Hi-hat
                {"note": 42, "time": start_time + 0.5},
                {"note": 42, "time": start_time + 1.0},
                {"note": 42, "time": start_time + 1.5},
            ]
            for hit in pattern:
                velocity = random.randint(80, 120)
                note = pretty_midi.Note(
                    velocity=velocity,
                    pitch=hit["note"],
                    start=hit["time"],
                    end=hit["time"] + 0.1,  # Short duration for percussive hit
                )
                instrument.notes.append(note)

        elif instrument_info["name"] in ["Violin", "Viola", "Cello"]:
            # Strings play harmonies or simple melodies
            for note_number in notes:
                velocity = random.randint(80, 120)
                # Slight random delay for natural feel
                delay = random.uniform(0, 0.2)
                note_start = start_time + delay
                note_end = start_time + chord_duration
                note = pretty_midi.Note(
                    velocity=velocity,
                    pitch=note_number,
                    start=note_start,
                    end=note_end,
                )
                instrument.notes.append(note)

        elif instrument_info["name"] == "Saxophone":
            # Saxophone plays melody; for simplicity, play the root note in higher octave
            root_note = notes[0] + 12  # One octave higher
            velocity = random.randint(80, 120)
            note = pretty_midi.Note(
                velocity=velocity,
                pitch=root_note,
                start=start_time,
                end=start_time + chord_duration,
            )
            instrument.notes.append(note)

        start_time += chord_duration

    midi.instruments.append(instrument)
    midi.write(filename)


def midi_to_wav(midi_file, wav_file, sample_rate):
    """Convert MIDI file to WAV using FluidSynth."""
    fs = FluidSynth(sound_font=SOUNDFONT_PATH, sample_rate=sample_rate)
    fs.midi_to_audio(midi_file, wav_file)


def ensure_fixed_length(wav_file: str, fixed_length: float):
    """
    Ensure the WAV file has exactly fixed_length seconds.
    If longer, trim it slightly to prevent cutting off reverb.
    If shorter, pad with silence.
    """
    audio = AudioSegment.from_wav(wav_file)
    current_length = len(audio) / 1000.0  # milliseconds to seconds

    if current_length > fixed_length:
        # Trim with some buffer
        trim_length = fixed_length - 0.2  # 0.2 seconds buffer
        audio = audio[: int(trim_length * 1000)]
    elif current_length < fixed_length:
        # Pad with silence
        silence = AudioSegment.silent(duration=(fixed_length - current_length) * 1000)
        audio += silence

    audio.export(wav_file, format="wav")


def merge_wav_files(
    inst_wav_files: list[str], merged_wav_file: str, fixed_length: float
):
    """Merge WAV files by overlaying them and ensure the merged file has fixed_length."""
    mix = AudioSegment.silent(duration=fixed_length * 1000)  # Start with silence
    for wav_file in inst_wav_files:
        audio = AudioSegment.from_wav(wav_file)
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

    # Select specific instruments
    instruments = select_instruments(n_instruments)
    print(f"Selected instruments: {[inst['name'] for inst in instruments]}")

    for sample_idx in range(n_samples):
        print(f"\nGenerating sample {sample_idx+1}/{n_samples}")
        # Generate chord progression
        chord_progression = generate_chord_progression(length=chord_length)
        print(f"Chord progression: {chord_progression}")

        inst_wav_files = []
        for inst_idx, instrument_info in enumerate(instruments):
            midi_filename = os.path.join(
                MIDI_DIR, f"sample{sample_idx}_inst{instrument_info['name']}.mid"
            )
            wav_filename = os.path.join(
                WAV_DIR, f"sample{sample_idx}_inst{instrument_info['name']}.wav"
            )
            # Generate MIDI
            generate_midi_instrument(
                chord_progression, instrument_info, midi_filename, chord_duration
            )
            print(f"Generated MIDI for {instrument_info['name']}: {midi_filename}")
            # Convert MIDI to WAV
            midi_to_wav(midi_filename, wav_filename, sample_rate)
            print(f"Converted to WAV: {wav_filename}")
            # Ensure WAV has fixed length
            total_duration = chord_length * chord_duration  # 예: 4 * 2.0 = 8.0 초
            ensure_fixed_length(wav_filename, fixed_length=total_duration)
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
