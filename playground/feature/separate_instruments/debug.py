import pandas as pd
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo, tempo2bpm
from midi2audio import FluidSynth
from os.path import join

from src._utils import *


wav_path = join(DATA_PATH, "musicnet", "train_data", "1727.wav")
label_path = join(DATA_PATH, "musicnet", "train_labels", "1727.csv")
mid_path = join(DATA_PATH, "musicnet_midis", "Schubert", "1727_schubert_op114_2.mid")
metadata_path = join(DATA_PATH, "musicnet_metadata.csv")


def get_original_midi_info(mid_path):
    original_midi = MidiFile(mid_path)
    tempo = None
    program_changes = {}

    for track in original_midi.tracks:
        for msg in track:
            if msg.type == "set_tempo":
                tempo = msg.tempo
            elif msg.type == "program_change":
                program_changes[msg.channel] = msg.program

    return tempo, program_changes


def csv_to_midi(csv_path, mid_path, output_dir):
    # Get original MIDI information
    original_tempo, program_changes = get_original_midi_info(mid_path)

    # Create a new MIDI file
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # Set tempo from original MIDI
    track.append(MetaMessage("set_tempo", tempo=original_tempo))

    # Add program change messages
    for channel, program in program_changes.items():
        track.append(
            Message("program_change", channel=channel, program=program, time=0)
        )

    # Process each note in the CSV
    df_full = pd.read_csv(csv_path)
    for channel in df_full.instrument.unique().tolist():
        df = df_full[df_full.instrument == channel]
        for _, row in df.iterrows():
            # Convert beat to ticks (assuming 480 ticks per beat)
            # start_time = int(row["start_beat"] * 480)
            # end_time = int(row["end_beat"] * 480)
            start_time = row["start_time"]
            end_time = row["end_time"]
            duration = end_time - start_time

            # Create note on message (using original velocity if available)
            # velocity = 64  # Default velocity
            # if "velocity" in row:
            velocity = int(row["velocity"])
            track.append(
                Message(
                    "note_on",
                    note=int(row["note"]),
                    velocity=velocity,
                    time=start_time,
                    channel=channel,
                )
            )

            # Create note off message
            track.append(
                Message(
                    "note_off",
                    note=int(row["note"]),
                    velocity=0,
                    time=duration,
                    channel=channel,
                )
            )

        # Save the MIDI file
        path = join(output_dir, f"channel_{channel}.mid")
        mid.save(path)
        print(f"MIDI file saved as {path}")


def midi_to_wav(midi_file, wav_file, soundfont_file=None):
    fs = FluidSynth()
    fs.midi_to_audio(midi_file, wav_file)


csv_to_midi(label_path, mid_path, "example.mid")
midi_to_wav("example.mid", "example.wav")
