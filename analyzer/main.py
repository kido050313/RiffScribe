from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    import librosa
except ImportError as exc:  # pragma: no cover - runtime dependency guard
    raise SystemExit(
        "Missing dependency: librosa. Install analyzer/requirements.txt before running the analyzer."
    ) from exc


DEFAULT_TIME_SIGNATURE = {"numerator": 4, "denominator": 4}
A4_MIDI = 69
A4_HZ = 440.0


def find_default_sample(samples_dir: Path) -> Path | None:
    supported_suffixes = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}
    for path in sorted(samples_dir.iterdir()):
        if path.is_file() and path.suffix.lower() in supported_suffixes:
            return path
    return None


def hz_to_midi(pitch_hz: float) -> int:
    if pitch_hz <= 0:
        return 0
    return int(round(12 * np.log2(pitch_hz / A4_HZ) + A4_MIDI))


def estimate_pitch_for_segment(
    signal: np.ndarray,
    sample_rate: int,
    start_sample: int,
    end_sample: int,
) -> int:
    segment = signal[start_sample:end_sample]
    if segment.size == 0:
        return 0

    pitches, magnitudes = librosa.piptrack(y=segment, sr=sample_rate)
    if pitches.size == 0 or magnitudes.size == 0:
        return 0

    peak_index = np.unravel_index(np.argmax(magnitudes), magnitudes.shape)
    pitch_hz = float(pitches[peak_index])
    return hz_to_midi(pitch_hz)


def build_measures(beats: list[float], beat_duration: float, beats_per_measure: int) -> list[dict[str, Any]]:
    if not beats:
        return []

    measures: list[dict[str, Any]] = []
    for index in range(0, len(beats), beats_per_measure):
        start = beats[index]
        if index + beats_per_measure < len(beats):
            end = beats[index + beats_per_measure]
        else:
            end = start + beat_duration * beats_per_measure
        measures.append(
            {
                "index": len(measures),
                "start": round(float(start), 4),
                "end": round(float(end), 4),
            }
        )
    return measures


def find_measure_index(start_time: float, measures: list[dict[str, Any]]) -> int:
    for measure in measures:
        if measure["start"] <= start_time < measure["end"]:
            return int(measure["index"])
    return max(len(measures) - 1, 0)


def build_notes(
    signal: np.ndarray,
    sample_rate: int,
    onsets: np.ndarray,
    duration_sec: float,
    beat_duration: float,
    measures: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    if onsets.size == 0:
        return notes

    onset_times = librosa.frames_to_time(onsets, sr=sample_rate)
    for index, start_time in enumerate(onset_times):
        next_time = float(onset_times[index + 1]) if index + 1 < len(onset_times) else float(duration_sec)
        raw_duration = max(next_time - float(start_time), beat_duration / 4)

        start_sample = int(start_time * sample_rate)
        end_sample = int(next_time * sample_rate)
        midi_pitch = estimate_pitch_for_segment(signal, sample_rate, start_sample, end_sample)

        measure_index = find_measure_index(float(start_time), measures)
        measure_start = measures[measure_index]["start"] if measures else 0.0
        beat_offset = (float(start_time) - float(measure_start)) / beat_duration if beat_duration > 0 else 0.0
        duration_beats = raw_duration / beat_duration if beat_duration > 0 else 0.0

        notes.append(
            {
                "id": f"n{index + 1}",
                "start": round(float(start_time), 4),
                "end": round(float(next_time), 4),
                "midiPitch": midi_pitch,
                "durationBeats": round(float(duration_beats), 4),
                "measureIndex": measure_index,
                "beatOffset": round(float(beat_offset), 4),
            }
        )
    return notes


def analyze_audio(audio_path: Path) -> dict[str, Any]:
    signal, sample_rate = librosa.load(audio_path, sr=None, mono=True)
    duration_sec = float(librosa.get_duration(y=signal, sr=sample_rate))

    tempo, beat_frames = librosa.beat.beat_track(y=signal, sr=sample_rate, units="frames")
    bpm = float(tempo.item() if hasattr(tempo, "item") else tempo)
    beat_times = librosa.frames_to_time(beat_frames, sr=sample_rate)

    onset_frames = librosa.onset.onset_detect(y=signal, sr=sample_rate, units="frames")

    beats_per_measure = DEFAULT_TIME_SIGNATURE["numerator"]
    beat_duration = 60.0 / bpm if bpm > 0 else 0.5
    measures = build_measures(
        beats=[float(beat) for beat in beat_times],
        beat_duration=beat_duration,
        beats_per_measure=beats_per_measure,
    )

    notes = build_notes(
        signal=signal,
        sample_rate=sample_rate,
        onsets=onset_frames,
        duration_sec=duration_sec,
        beat_duration=beat_duration,
        measures=measures,
    )

    return {
        "sourceName": audio_path.name,
        "durationSec": round(duration_sec, 4),
        "bpm": round(bpm, 2),
        "timeSignature": DEFAULT_TIME_SIGNATURE,
        "beats": [round(float(beat), 4) for beat in beat_times],
        "measures": measures,
        "notes": notes,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a guitar audio clip into a Day 2 JSON draft.")
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to an input audio file. If omitted, the analyzer uses the first supported file in samples/.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to the output JSON file. Defaults to output/analysis-result.json.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    samples_dir = repo_root / "samples"
    output_path = args.output or (repo_root / "output" / "analysis-result.json")

    input_path = args.input or find_default_sample(samples_dir)
    if input_path is None:
        raise SystemExit("No input audio found. Add a sample file to samples/ or pass --input <path>.")

    if not input_path.exists():
        raise SystemExit(f"Input audio not found: {input_path}")

    result = analyze_audio(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Analyzed {input_path.name}")
    print(f"Wrote analysis to: {output_path}")
    print(f"BPM: {result['bpm']}, beats: {len(result['beats'])}, notes: {len(result['notes'])}")


if __name__ == "__main__":
    main()
