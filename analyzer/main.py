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

from schemas import DetailedNote, InputAsset, Measure, NotationCandidate, StemCandidate, TimingGrid


SCHEMA_VERSION = "analysis.v2"
DEFAULT_TIME_SIGNATURE = {"numerator": 4, "denominator": 4}
DEFAULT_TIME_SIGNATURE_LABEL = "4/4"
DEFAULT_GROOVE_LABEL = "straight"
DEFAULT_TASK_PREFIX = "task"
DEFAULT_VERSION_PREFIX = "ver"
A4_MIDI = 69
A4_HZ = 440.0


def load_params(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


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


def build_measures(beats: list[float], beat_duration: float, beats_per_measure: int) -> list[Measure]:
    if not beats:
        return []

    measures: list[Measure] = []
    for index in range(0, len(beats), beats_per_measure):
        start = beats[index]
        if index + beats_per_measure < len(beats):
            end = beats[index + beats_per_measure]
        else:
            end = start + beat_duration * beats_per_measure
        measures.append(
            Measure(
                index=len(measures),
                start=round(float(start), 4),
                end=round(float(end), 4),
            )
        )
    return measures


def find_measure_index(start_time: float, measures: list[Measure]) -> int:
    for measure in measures:
        if measure.start <= start_time < measure.end:
            return int(measure.index)
    return max(len(measures) - 1, 0)


def build_notes(
    signal: np.ndarray,
    sample_rate: int,
    onsets: np.ndarray,
    duration_sec: float,
    beat_duration: float,
    measures: list[Measure],
    task_id: str,
    version_id: str,
    params: dict[str, Any],
) -> list[DetailedNote]:
    notes: list[DetailedNote] = []
    if onsets.size == 0:
        return notes

    start_measure_offset_beats = float(
        params.get("beatTracking", {}).get("startMeasureOffsetBeats", 0.0)
    )
    onset_times = librosa.frames_to_time(onsets, sr=sample_rate)
    for index, start_time in enumerate(onset_times):
        next_time = float(onset_times[index + 1]) if index + 1 < len(onset_times) else float(duration_sec)
        raw_duration = max(next_time - float(start_time), beat_duration / 4)

        start_sample = int(start_time * sample_rate)
        end_sample = int(next_time * sample_rate)
        midi_pitch = estimate_pitch_for_segment(signal, sample_rate, start_sample, end_sample)

        measure_index = find_measure_index(float(start_time), measures)
        measure_start = measures[measure_index].start if measures else 0.0
        beat_offset = ((float(start_time) - float(measure_start)) / beat_duration + start_measure_offset_beats) if beat_duration > 0 else 0.0
        duration_beats = raw_duration / beat_duration if beat_duration > 0 else 0.0

        notes.append(
            DetailedNote(
                noteId=f"note_{index + 1:03d}",
                taskId=task_id,
                versionId=version_id,
                start=round(float(start_time), 4),
                end=round(float(next_time), 4),
                midiPitch=midi_pitch,
                measureIndex=measure_index,
                beatOffset=round(float(beat_offset), 4),
                durationBeats=round(float(duration_beats), 4),
                noteClass="backbone",
                confidence=0.5,
            )
        )
    return notes


def postprocess_notes(notes: list[DetailedNote], params: dict[str, Any]) -> list[DetailedNote]:
    filtering = params.get("filtering", {})
    pitch_range = params.get("pitchRange", {})
    min_duration_beats = float(filtering.get("minNoteDurationBeats", 0.25))
    lower_pitch = int(pitch_range.get("lower", 40))
    upper_pitch = int(pitch_range.get("upper", 88))

    filtered = [
        note
        for note in notes
        if note.durationBeats >= min_duration_beats and lower_pitch <= note.midiPitch <= upper_pitch
    ]

    if not filtered:
        filtered = notes

    normalized: list[DetailedNote] = []
    for index, note in enumerate(filtered, start=1):
        normalized.append(
            DetailedNote(
                noteId=f"note_{index:03d}",
                taskId=note.taskId,
                versionId=note.versionId,
                start=note.start,
                end=note.end,
                midiPitch=note.midiPitch,
                measureIndex=note.measureIndex,
                beatOffset=note.beatOffset,
                durationBeats=note.durationBeats,
                phraseId=note.phraseId,
                parentBackboneId=note.parentBackboneId,
                noteClass=note.noteClass,
                confidence=note.confidence,
                stringCandidate=note.stringCandidate,
                fretCandidate=note.fretCandidate,
            )
        )
    return normalized


def infer_asset_type(audio_path: Path) -> str:
    video_suffixes = {".mp4", ".mov", ".mkv", ".avi", ".webm"}
    return "video" if audio_path.suffix.lower() in video_suffixes else "audio"


def derive_task_id(audio_path: Path) -> str:
    return f"{DEFAULT_TASK_PREFIX}_{audio_path.stem}"


def derive_version_id() -> str:
    return f"{DEFAULT_VERSION_PREFIX}_001"


def derive_stem_type(audio_path: Path) -> str:
    stem_name = audio_path.stem.lower()
    if stem_name in {"other", "vocals", "bass", "drums", "extracted"}:
        return stem_name
    if stem_name == "no_vocals":
        return "other"
    return "extracted"


def resolve_audio_path(audio_path: Path, params: dict[str, Any]) -> Path:
    selected_stem = params.get("selectedStem")
    if not selected_stem:
        return audio_path

    current_stem = derive_stem_type(audio_path)
    if selected_stem == current_stem:
        return audio_path

    if selected_stem in {"other", "vocals", "bass", "drums"}:
        sibling = audio_path.with_name(f"{selected_stem}.wav")
        if sibling.exists():
            return sibling

    if selected_stem == "extracted":
        match = next((part for part in audio_path.parts if part.startswith("test")), None)
        if match:
            extracted_path = audio_path.parents[3] / "extracted" / f"{match}.wav"
            if extracted_path.exists():
                return extracted_path

    return audio_path


def build_analysis_result(
    audio_path: Path,
    params: dict[str, Any] | None = None,
    task_id_override: str | None = None,
    version_id_override: str | None = None,
) -> dict[str, Any]:
    params = params or {}
    resolved_audio_path = resolve_audio_path(audio_path, params)

    task_id = task_id_override or derive_task_id(resolved_audio_path)
    version_id = version_id_override or derive_version_id()
    asset_id = f"asset_{resolved_audio_path.stem}"
    stem_id = f"stem_{resolved_audio_path.stem}"
    timing_grid_id = f"grid_{resolved_audio_path.stem}_{version_id}"
    notation_id = f"notation_{resolved_audio_path.stem}_{version_id}"

    signal, sample_rate = librosa.load(resolved_audio_path, sr=None, mono=True)
    duration_sec = float(librosa.get_duration(y=signal, sr=sample_rate))

    tightness = int(params.get("beatTracking", {}).get("tightness", 100))
    tempo, beat_frames = librosa.beat.beat_track(y=signal, sr=sample_rate, units="frames", tightness=tightness)
    bpm = float(tempo.item() if hasattr(tempo, "item") else tempo)
    beat_times = [round(float(beat), 4) for beat in librosa.frames_to_time(beat_frames, sr=sample_rate)]

    onset_frames = librosa.onset.onset_detect(y=signal, sr=sample_rate, units="frames")

    beats_per_measure = DEFAULT_TIME_SIGNATURE["numerator"]
    beat_duration = 60.0 / bpm if bpm > 0 else 0.5
    measures = build_measures(
        beats=beat_times,
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
        task_id=task_id,
        version_id=version_id,
        params=params,
    )
    notes = postprocess_notes(notes, params)

    input_asset = InputAsset(
        assetId=asset_id,
        taskId=task_id,
        path=str(resolved_audio_path),
        type=infer_asset_type(resolved_audio_path),
        durationSec=round(duration_sec, 4),
        sampleRate=sample_rate,
        channels=1,
        sourceLabel=resolved_audio_path.name,
        metadata={"sourceName": resolved_audio_path.name},
    )
    stem_candidate = StemCandidate(
        stemId=stem_id,
        taskId=task_id,
        versionId=version_id,
        sourceAssetId=asset_id,
        stemType=derive_stem_type(resolved_audio_path),
        path=str(resolved_audio_path),
        durationSec=round(duration_sec, 4),
        qualityScore=1.0,
        selectionReason="selected_for_analysis",
    )
    timing_grid = TimingGrid(
        timingGridId=timing_grid_id,
        taskId=task_id,
        versionId=version_id,
        sourceStemId=stem_id,
        tempo=round(bpm, 2),
        selectedTimeSignature=DEFAULT_TIME_SIGNATURE_LABEL,
        timeSignatureCandidates=[DEFAULT_TIME_SIGNATURE_LABEL],
        beats=beat_times,
        downbeats=[measure.start for measure in measures],
        measures=measures,
        grooveLabel=DEFAULT_GROOVE_LABEL,
        confidence=0.5,
    )
    notation_candidate = NotationCandidate(
        notationId=notation_id,
        taskId=task_id,
        versionId=version_id,
        timingGridId=timing_grid_id,
        noteIds=[note.noteId for note in notes],
        tabRepresentation={"tuning": [64, 59, 55, 50, 45, 40]},
        staffRepresentation={"clef": "treble"},
    )

    legacy_measures = [measure.to_dict() for measure in measures]
    legacy_notes = [note.to_dict() for note in notes]

    return {
        "schemaVersion": SCHEMA_VERSION,
        "taskId": task_id,
        "versionId": version_id,
        "inputAsset": input_asset.to_dict(),
        "stemCandidate": stem_candidate.to_dict(),
        "timingGrid": timing_grid.to_dict(),
        "detailedNotes": legacy_notes,
        "notationCandidate": notation_candidate.to_dict(),
        "sourceName": resolved_audio_path.name,
        "durationSec": round(duration_sec, 4),
        "bpm": round(bpm, 2),
        "timeSignature": DEFAULT_TIME_SIGNATURE,
        "beats": beat_times,
        "measures": legacy_measures,
        "notes": legacy_notes,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a guitar audio clip into a structured JSON draft.")
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
    parser.add_argument("--params", type=Path, help="Optional params.json path to influence analysis output.")
    parser.add_argument("--task-id", type=str, help="Optional taskId override.")
    parser.add_argument("--version-id", type=str, help="Optional versionId override.")
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

    params = load_params(args.params)
    result = build_analysis_result(
        input_path,
        params=params,
        task_id_override=args.task_id,
        version_id_override=args.version_id,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Analyzed {result['sourceName']}")
    print(f"Wrote analysis to: {output_path}")
    print(f"BPM: {result['bpm']}, beats: {len(result['beats'])}, notes: {len(result['notes'])}")


if __name__ == "__main__":
    main()
