from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import Element, ElementTree, SubElement

import mido


TYPE_BY_QUARTERS = [
    (4.0, "whole"),
    (2.0, "half"),
    (1.5, "quarter"),
    (1.0, "quarter"),
    (0.75, "eighth"),
    (0.5, "eighth"),
    (0.25, "16th"),
]

STEP_NAMES = ["C", "C", "D", "D", "E", "F", "F", "G", "G", "A", "A", "B"]
ALTERS = [0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0]


def load_analysis(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def quarter_notes_per_beat(time_signature: dict[str, int]) -> float:
    return 4 / time_signature["denominator"]


def note_quarter_length(note: dict[str, Any], time_signature: dict[str, int]) -> float:
    return float(note["durationBeats"]) * quarter_notes_per_beat(time_signature)


def beat_offset_quarters(note: dict[str, Any], time_signature: dict[str, int]) -> float:
    return float(note["beatOffset"]) * quarter_notes_per_beat(time_signature)


def midi_pitch_components(midi_pitch: int) -> tuple[str, int, int]:
    pitch_class = midi_pitch % 12
    step = STEP_NAMES[pitch_class]
    alter = ALTERS[pitch_class]
    octave = (midi_pitch // 12) - 1
    return step, alter, octave


def quantize_divisions(quarter_length: float, divisions: int) -> int:
    return max(1, int(round(quarter_length * divisions)))


def note_type_from_quarters(quarter_length: float) -> str:
    for threshold, note_type in TYPE_BY_QUARTERS:
        if quarter_length >= threshold - 0.001:
            return note_type
    return "16th"


def add_pitch_element(parent: Element, midi_pitch: int) -> None:
    step, alter, octave = midi_pitch_components(midi_pitch)
    pitch = SubElement(parent, "pitch")
    SubElement(pitch, "step").text = step
    if alter:
        SubElement(pitch, "alter").text = str(alter)
    SubElement(pitch, "octave").text = str(octave)


def add_duration_type(parent: Element, quarter_length: float, divisions: int) -> None:
    SubElement(parent, "duration").text = str(quantize_divisions(quarter_length, divisions))
    SubElement(parent, "type").text = note_type_from_quarters(quarter_length)
    if abs(quarter_length - 1.5) < 0.05 or abs(quarter_length - 0.75) < 0.05:
        SubElement(parent, "dot")


def build_musicxml(analysis: dict[str, Any], output_path: Path) -> None:
    time_signature = analysis["timeSignature"]
    divisions = 480
    quarter_per_beat = quarter_notes_per_beat(time_signature)
    measure_quarters = time_signature["numerator"] * quarter_per_beat

    root = Element("score-partwise", version="3.1")
    part_list = SubElement(root, "part-list")
    score_part = SubElement(part_list, "score-part", id="P1")
    SubElement(score_part, "part-name").text = "Electric Guitar Draft"

    part = SubElement(root, "part", id="P1")
    notes_by_measure: dict[int, list[dict[str, Any]]] = {}
    for note in analysis["notes"]:
        notes_by_measure.setdefault(int(note["measureIndex"]), []).append(note)

    for measure in analysis["measures"]:
        measure_index = int(measure["index"])
        measure_element = SubElement(part, "measure", number=str(measure_index + 1))

        if measure_index == 0:
            attributes = SubElement(measure_element, "attributes")
            SubElement(attributes, "divisions").text = str(divisions)
            key = SubElement(attributes, "key")
            SubElement(key, "fifths").text = "0"
            time = SubElement(attributes, "time")
            SubElement(time, "beats").text = str(time_signature["numerator"])
            SubElement(time, "beat-type").text = str(time_signature["denominator"])
            clef = SubElement(attributes, "clef")
            SubElement(clef, "sign").text = "G"
            SubElement(clef, "line").text = "2"

        if analysis.get("bpm") and measure_index == 0:
            direction = SubElement(measure_element, "direction", placement="above")
            direction_type = SubElement(direction, "direction-type")
            metronome = SubElement(direction_type, "metronome")
            SubElement(metronome, "beat-unit").text = "quarter"
            SubElement(metronome, "per-minute").text = str(analysis["bpm"])
            SubElement(direction, "sound", tempo=str(analysis["bpm"]))

        cursor_quarters = 0.0
        measure_notes = sorted(
            notes_by_measure.get(measure_index, []),
            key=lambda note: (float(note["beatOffset"]), float(note["start"])),
        )

        for note in measure_notes:
            start_quarters = max(0.0, beat_offset_quarters(note, time_signature))
            if start_quarters > cursor_quarters + 0.01:
                rest_quarters = start_quarters - cursor_quarters
                rest_note = SubElement(measure_element, "note")
                SubElement(rest_note, "rest")
                add_duration_type(rest_note, rest_quarters, divisions)
                cursor_quarters = start_quarters

            note_element = SubElement(measure_element, "note")
            add_pitch_element(note_element, int(note["midiPitch"]))
            quarter_length = note_quarter_length(note, time_signature)
            add_duration_type(note_element, quarter_length, divisions)
            cursor_quarters += quarter_length

        if cursor_quarters < measure_quarters - 0.01:
            rest_note = SubElement(measure_element, "note")
            SubElement(rest_note, "rest")
            add_duration_type(rest_note, measure_quarters - cursor_quarters, divisions)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    ElementTree(root).write(output_path, encoding="utf-8", xml_declaration=True)


def build_midi(analysis: dict[str, Any], output_path: Path) -> None:
    midi_file = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    midi_file.tracks.append(track)

    bpm = float(analysis.get("bpm") or 120.0)
    tempo = mido.bpm2tempo(bpm)
    track.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))
    track.append(mido.MetaMessage("time_signature", numerator=analysis["timeSignature"]["numerator"], denominator=analysis["timeSignature"]["denominator"], time=0))
    track.append(mido.Message("program_change", program=29, time=0))

    events: list[tuple[int, int, int]] = []
    for note in analysis["notes"]:
        start_tick = int(round(mido.second2tick(float(note["start"]), midi_file.ticks_per_beat, tempo)))
        end_tick = int(round(mido.second2tick(float(note["end"]), midi_file.ticks_per_beat, tempo)))
        midi_pitch = int(note["midiPitch"])
        events.append((start_tick, 0, midi_pitch))
        events.append((max(start_tick + 1, end_tick), 1, midi_pitch))

    events.sort(key=lambda event: (event[0], event[1]))

    current_tick = 0
    for tick, event_type, midi_pitch in events:
        delta = max(0, tick - current_tick)
        if event_type == 0:
            track.append(mido.Message("note_on", note=midi_pitch, velocity=88, time=delta))
        else:
            track.append(mido.Message("note_off", note=midi_pitch, velocity=0, time=delta))
        current_tick = tick

    output_path.parent.mkdir(parents=True, exist_ok=True)
    midi_file.save(output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export analysis JSON to MIDI and MusicXML.")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to the analysis JSON file.",
    )
    parser.add_argument(
        "--midi-output",
        type=Path,
        help="Path to the MIDI output file. Defaults to output/exports/<name>.mid.",
    )
    parser.add_argument(
        "--musicxml-output",
        type=Path,
        help="Path to the MusicXML output file. Defaults to output/exports/<name>.musicxml.",
    )
    parser.add_argument(
        "--skip-midi",
        action="store_true",
        help="Skip MIDI export.",
    )
    parser.add_argument(
        "--skip-musicxml",
        action="store_true",
        help="Skip MusicXML export.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.input.exists():
        raise SystemExit(f"Analysis JSON not found: {args.input}")

    repo_root = Path(__file__).resolve().parent.parent
    export_dir = repo_root / "output" / "exports"
    stem_name = args.input.stem.replace(".analysis", "")

    midi_output = args.midi_output or (export_dir / f"{stem_name}.mid")
    musicxml_output = args.musicxml_output or (export_dir / f"{stem_name}.musicxml")

    analysis = load_analysis(args.input)

    if not args.skip_midi:
        build_midi(analysis, midi_output)
        print(f"Wrote MIDI to: {midi_output}")

    if not args.skip_musicxml:
        build_musicxml(analysis, musicxml_output)
        print(f"Wrote MusicXML to: {musicxml_output}")


if __name__ == "__main__":
    main()
