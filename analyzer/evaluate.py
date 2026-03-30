from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median
from typing import Any

from schemas import EvaluationOverall, EvaluationReport


REPORT_SCHEMA_VERSION = "evaluation.v1"
DEFAULT_ALIGNMENT_TOLERANCE = 0.125
DEFAULT_GUITAR_RANGE = (40, 88)


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def load_analysis(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def nearest_distance(value: float, candidates: list[float]) -> float:
    if not candidates:
        return 0.0
    return min(abs(value - candidate) for candidate in candidates)


def derive_rank_hint(score: float) -> str:
    if score >= 0.85:
        return "excellent"
    if score >= 0.7:
        return "usable"
    if score >= 0.5:
        return "weak"
    return "failed"


def summarize(score: float, primary_issues: list[str]) -> str:
    if not primary_issues:
        if score >= 0.7:
            return "The current draft is usable and can move to export or iteration."
        return "The current draft still has obvious issues and should enter another iteration."
    issues_text = ", ".join(primary_issues[:3])
    return f"Primary issues detected: {issues_text}."


def build_rhythm_metrics(analysis: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    beats = [float(beat) for beat in analysis.get("beats", [])]
    notes = analysis.get("detailedNotes") or analysis.get("notes") or []
    measures = analysis.get("measures", [])

    issues: list[str] = []
    if len(beats) < 2:
        return {
            "score": 0.0,
            "beatAlignment": 0.0,
            "measureBoundaryScore": 0.0,
            "negativeBeatOffsetRatio": 1.0 if notes else 0.0,
            "fragmentationRatio": 0.0,
            "onsetDeviationMean": 0.0,
            "onsetDeviationMedian": 0.0,
        }, ["beat_tracking_missing"]

    beat_intervals = [beats[index + 1] - beats[index] for index in range(len(beats) - 1)]
    mean_interval = sum(beat_intervals) / len(beat_intervals)
    interval_variance = (
        sum((interval - mean_interval) ** 2 for interval in beat_intervals) / len(beat_intervals)
        if beat_intervals
        else 0.0
    )
    interval_std = interval_variance**0.5
    beat_alignment = clamp(1 - (interval_std / max(mean_interval, 1e-6)))

    note_distances = [nearest_distance(float(note["start"]), beats) for note in notes]
    onset_deviation_mean = sum(note_distances) / len(note_distances) if note_distances else 0.0
    onset_deviation_median = median(note_distances) if note_distances else 0.0
    onset_alignment = clamp(1 - (onset_deviation_mean / max(DEFAULT_ALIGNMENT_TOLERANCE, 1e-6)))

    negative_beat_offsets = [note for note in notes if float(note.get("beatOffset", 0.0)) < 0]
    negative_ratio = len(negative_beat_offsets) / len(notes) if notes else 0.0

    short_notes = [note for note in notes if float(note.get("durationBeats", 0.0)) <= 0.25]
    fragmentation_ratio = len(short_notes) / len(notes) if notes else 0.0

    expected_measure_count = max(1, round(len(beats) / max(analysis["timeSignature"]["numerator"], 1)))
    measure_boundary_score = clamp(1 - abs(len(measures) - expected_measure_count) / max(expected_measure_count, 1))

    rhythm_score = clamp(
        (beat_alignment * 0.35)
        + (onset_alignment * 0.35)
        + (measure_boundary_score * 0.15)
        + ((1 - negative_ratio) * 0.1)
        + ((1 - fragmentation_ratio) * 0.05)
    )

    if negative_ratio > 0.0:
        issues.append("negative_beat_offset_present")
    if fragmentation_ratio > 0.45:
        issues.append("note_fragmentation_high")
    if onset_deviation_mean > DEFAULT_ALIGNMENT_TOLERANCE:
        issues.append("beat_alignment_low")

    return {
        "score": round(rhythm_score, 4),
        "beatAlignment": round(beat_alignment, 4),
        "measureBoundaryScore": round(measure_boundary_score, 4),
        "negativeBeatOffsetRatio": round(negative_ratio, 4),
        "fragmentationRatio": round(fragmentation_ratio, 4),
        "onsetDeviationMean": round(onset_deviation_mean, 4),
        "onsetDeviationMedian": round(onset_deviation_median, 4),
    }, issues


def build_pitch_metrics(analysis: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    notes = analysis.get("detailedNotes") or analysis.get("notes") or []
    midi_values = [int(note["midiPitch"]) for note in notes if int(note.get("midiPitch", 0)) > 0]
    issues: list[str] = []

    if not midi_values:
        return {
            "score": 0.0,
            "validPitchRatio": 0.0,
            "outlierRatio": 1.0,
            "excessiveLeapRatio": 0.0,
            "contourStability": 0.0,
        }, ["pitch_detection_missing"]

    lower_bound, upper_bound = DEFAULT_GUITAR_RANGE
    in_range_count = sum(lower_bound <= midi <= upper_bound for midi in midi_values)
    valid_pitch_ratio = in_range_count / len(midi_values)
    outlier_ratio = 1 - valid_pitch_ratio

    leaps = [
        abs(midi_values[index + 1] - midi_values[index])
        for index in range(len(midi_values) - 1)
    ]
    excessive_leaps = [leap for leap in leaps if leap > 12]
    excessive_leap_ratio = len(excessive_leaps) / len(leaps) if leaps else 0.0

    contour_stability = clamp(1 - excessive_leap_ratio)
    pitch_score = clamp((valid_pitch_ratio * 0.6) + ((1 - excessive_leap_ratio) * 0.4))

    if outlier_ratio > 0.08:
        issues.append("pitch_outlier_high")
    if excessive_leap_ratio > 0.25:
        issues.append("pitch_contour_unstable")

    return {
        "score": round(pitch_score, 4),
        "validPitchRatio": round(valid_pitch_ratio, 4),
        "outlierRatio": round(outlier_ratio, 4),
        "excessiveLeapRatio": round(excessive_leap_ratio, 4),
        "contourStability": round(contour_stability, 4),
    }, issues


def build_primary_issues(rhythm_issues: list[str], pitch_issues: list[str]) -> list[str]:
    ordered = rhythm_issues + pitch_issues
    deduplicated: list[str] = []
    for issue in ordered:
        if issue not in deduplicated:
            deduplicated.append(issue)
    return deduplicated[:3]


def recommended_actions(primary_issues: list[str]) -> list[str]:
    issue_to_action = {
        "beat_tracking_missing": "retune_beat_tracking",
        "beat_alignment_low": "retune_beat_tracking",
        "negative_beat_offset_present": "fix_measure_alignment",
        "note_fragmentation_high": "increase_min_note_duration",
        "pitch_outlier_high": "limit_pitch_range",
        "pitch_contour_unstable": "smooth_pitch_contour",
        "pitch_detection_missing": "switch_input_stem",
    }
    actions: list[str] = []
    for issue in primary_issues:
        action = issue_to_action.get(issue)
        if action and action not in actions:
            actions.append(action)
    if not actions:
        actions.append("rerun_with_current_parameters")
    return actions


def build_report(analysis: dict[str, Any], analysis_path: Path) -> dict[str, Any]:
    task_id = str(analysis.get("taskId") or "task_unknown")
    version_id = str(analysis.get("versionId") or "ver_001")
    notation_candidate = analysis.get("notationCandidate", {})
    notation_id = str(notation_candidate.get("notationId") or f"notation_{version_id}")

    rhythm_metrics, rhythm_issues = build_rhythm_metrics(analysis)
    pitch_metrics, pitch_issues = build_pitch_metrics(analysis)
    primary_issues = build_primary_issues(rhythm_issues, pitch_issues)
    actions = recommended_actions(primary_issues)

    overall_score = clamp((rhythm_metrics["score"] * 0.6) + (pitch_metrics["score"] * 0.4))
    confidence = clamp(1 - (len(primary_issues) * 0.15))
    rank_hint = derive_rank_hint(overall_score)

    report = EvaluationReport(
        reportId=f"report_{version_id}",
        taskId=task_id,
        versionId=version_id,
        notationId=notation_id,
        overall=EvaluationOverall(
            score=round(overall_score, 4),
            confidence=round(confidence, 4),
            rankHint=rank_hint,
            summary=summarize(overall_score, primary_issues),
        ),
        metrics={
            "rhythm": rhythm_metrics,
            "pitch": pitch_metrics,
        },
        diagnosis={
            "primaryIssues": primary_issues,
            "secondaryIssues": [],
            "riskLevel": "medium" if primary_issues else "low",
        },
        adjustments={
            "recommendedActions": actions,
            "priority": "rhythm_first" if rhythm_metrics["score"] <= pitch_metrics["score"] else "pitch_first",
            "nextStrategy": " -> ".join(actions),
            "parameterHints": {},
        },
        comparison={},
    ).to_dict()

    report["schemaVersion"] = REPORT_SCHEMA_VERSION
    report["analysisPath"] = str(analysis_path)
    report["input"] = {
        "assetPath": analysis.get("inputAsset", {}).get("path"),
        "assetType": analysis.get("inputAsset", {}).get("type"),
        "durationSec": analysis.get("durationSec"),
        "selectedStem": analysis.get("stemCandidate", {}).get("stemType"),
        "sourceName": analysis.get("sourceName"),
    }
    report["candidate"] = {
        "candidateId": version_id,
        "analysisPath": str(analysis_path),
        "noteCount": len(analysis.get("detailedNotes") or analysis.get("notes") or []),
        "measureCount": len(analysis.get("measures") or []),
        "beatCount": len(analysis.get("beats") or []),
        "tempo": analysis.get("bpm"),
        "timeSignature": analysis.get("timingGrid", {}).get("selectedTimeSignature", "4/4"),
    }
    return report


def default_output_path(repo_root: Path, task_id: str, version_id: str) -> Path:
    return repo_root / "output" / "tasks" / task_id / "versions" / version_id / "evaluation-report.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a minimal evaluation report from an analysis JSON file.")
    parser.add_argument("--input", type=Path, required=True, help="Path to the analysis JSON file.")
    parser.add_argument("--output", type=Path, help="Optional path to the evaluation report JSON file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.input.exists():
        raise SystemExit(f"Analysis JSON not found: {args.input}")

    analysis = load_analysis(args.input)
    repo_root = Path(__file__).resolve().parent.parent
    task_id = str(analysis.get("taskId") or "task_unknown")
    version_id = str(analysis.get("versionId") or "ver_001")
    output_path = args.output or default_output_path(repo_root, task_id, version_id)

    report = build_report(analysis, args.input)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote evaluation report to: {output_path}")
    print(
        f"Overall: {report['overall']['score']}, "
        f"rhythm: {report['metrics']['rhythm']['score']}, "
        f"pitch: {report['metrics']['pitch']['score']}"
    )
    print(f"Primary issues: {', '.join(report['diagnosis']['primaryIssues']) or 'none'}")


if __name__ == "__main__":
    main()
