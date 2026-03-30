from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from adjustments import build_adjustment_plan
from evaluate import build_report
from export import build_midi, build_musicxml
from main import build_analysis_result
from task_store import (
    attach_adjustment_plan,
    load_json,
    materialize_version_artifacts,
    save_json,
    task_index_path,
    version_directory,
)


def resolve_path(repo_root: Path, path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return repo_root / path


def ensure_adjustment_plan(
    repo_root: Path,
    task_payload: dict[str, Any],
    source_version_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    version_info = task_payload["versions"][source_version_id]
    version_root = version_directory(repo_root, task_payload["taskId"], source_version_id)
    plan_path = version_root / "adjustment-plan.json"
    next_params_path = version_root / "next-params.json"

    if plan_path.exists() and next_params_path.exists():
        return load_json(plan_path), load_json(next_params_path)

    report_path = resolve_path(repo_root, version_info["paths"]["evaluationReport"])
    params_path = resolve_path(repo_root, version_info["paths"]["params"])
    report = load_json(report_path)
    params = load_json(params_path)
    plan, next_params = build_adjustment_plan(report, params, task_payload)
    attach_adjustment_plan(repo_root, task_payload["taskId"], source_version_id, plan, next_params)
    return plan, next_params


def export_next_version(analysis: dict[str, Any], analysis_output_path: Path) -> dict[str, Path]:
    repo_root = Path(__file__).resolve().parent.parent
    export_dir = repo_root / "output" / "exports"
    stem_name = analysis_output_path.stem.replace(".analysis", "")
    midi_output = export_dir / f"{stem_name}.mid"
    musicxml_output = export_dir / f"{stem_name}.musicxml"
    build_midi(analysis, midi_output)
    build_musicxml(analysis, musicxml_output)
    return {
        "midi": midi_output,
        "musicxml": musicxml_output,
    }


def build_comparison(previous_report: dict[str, Any], next_report: dict[str, Any]) -> dict[str, Any]:
    previous_score = float(previous_report.get("overall", {}).get("score", 0.0))
    next_score = float(next_report.get("overall", {}).get("score", 0.0))
    rhythm_delta = float(next_report["metrics"]["rhythm"]["score"]) - float(previous_report["metrics"]["rhythm"]["score"])
    pitch_delta = float(next_report["metrics"]["pitch"]["score"]) - float(previous_report["metrics"]["pitch"]["score"])
    return {
        "fromVersionId": previous_report["versionId"],
        "toVersionId": next_report["versionId"],
        "previousScore": previous_score,
        "nextScore": next_score,
        "scoreDelta": round(next_score - previous_score, 4),
        "metricDeltas": {
            "rhythm": round(rhythm_delta, 4),
            "pitch": round(pitch_delta, 4),
        },
        "isImproved": next_score >= previous_score,
    }


def update_task_with_iteration(
    repo_root: Path,
    task_payload: dict[str, Any],
    source_version_id: str,
    target_version_id: str,
    comparison: dict[str, Any],
    comparison_path: Path,
) -> None:
    source_entry = task_payload["versions"][source_version_id]
    target_entry = task_payload["versions"][target_version_id]
    target_entry["parentVersionId"] = source_version_id
    target_entry["comparisonPath"] = str(comparison_path)
    target_entry["generatedFromPlanId"] = source_entry.get("adjustmentPlanId")
    task_payload["latestVersionId"] = target_version_id
    save_json(task_index_path(repo_root, task_payload["taskId"]), task_payload)


def run_single_iteration(repo_root: Path, task_payload: dict[str, Any], source_version_id: str) -> dict[str, Any]:
    source_entry = task_payload["versions"][source_version_id]
    source_candidate_path = resolve_path(repo_root, source_entry["paths"]["candidate"])
    source_report_path = resolve_path(repo_root, source_entry["paths"]["evaluationReport"])
    source_analysis = load_json(source_candidate_path)
    source_report = load_json(source_report_path)

    adjustment_plan, next_params = ensure_adjustment_plan(repo_root, task_payload, source_version_id)
    target_version_id = str(adjustment_plan["targetVersionId"])

    source_audio_path = resolve_path(repo_root, source_analysis["inputAsset"]["path"])
    analysis_output_path = repo_root / "output" / "analysis" / f"{task_payload['taskId']}.{target_version_id}.analysis.json"
    analysis_output_path.parent.mkdir(parents=True, exist_ok=True)

    next_analysis = build_analysis_result(
        source_audio_path,
        params=next_params,
        task_id_override=task_payload["taskId"],
        version_id_override=target_version_id,
    )
    save_json(analysis_output_path, next_analysis)

    export_next_version(next_analysis, analysis_output_path)

    target_version_root = version_directory(repo_root, task_payload["taskId"], target_version_id)
    report_output_path = target_version_root / "evaluation-report.json"
    report_output_path.parent.mkdir(parents=True, exist_ok=True)
    next_report = build_report(next_analysis, analysis_output_path)
    save_json(report_output_path, next_report)

    materialize_version_artifacts(repo_root, analysis_output_path, report_output_path)
    save_json(target_version_root / "params.json", next_params)

    comparison = build_comparison(source_report, next_report)
    comparison_dir = repo_root / "output" / "tasks" / task_payload["taskId"] / "comparisons"
    comparison_path = comparison_dir / f"{source_version_id}__{target_version_id}.json"
    save_json(comparison_path, comparison)

    refreshed_task = load_json(task_index_path(repo_root, task_payload["taskId"]))
    update_task_with_iteration(repo_root, refreshed_task, source_version_id, target_version_id, comparison, comparison_path)

    return {
        "sourceVersionId": source_version_id,
        "targetVersionId": target_version_id,
        "analysisPath": str(analysis_output_path),
        "reportPath": str(report_output_path),
        "comparisonPath": str(comparison_path),
        "scoreDelta": comparison["scoreDelta"],
        "isImproved": comparison["isImproved"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the minimum viable transcription iteration engine.")
    parser.add_argument("--task-index", type=Path, required=True, help="Path to task.json.")
    parser.add_argument("--max-rounds", type=int, default=1, help="How many linear rounds to run.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.task_index.exists():
        raise SystemExit(f"Task index not found: {args.task_index}")

    repo_root = Path(__file__).resolve().parent.parent
    task_payload = load_json(args.task_index)
    rounds = max(1, args.max_rounds)
    latest_result: dict[str, Any] | None = None

    for _ in range(rounds):
        current_task = load_json(args.task_index)
        source_version_id = str(current_task["latestVersionId"])
        latest_result = run_single_iteration(repo_root, current_task, source_version_id)

    if latest_result is None:
        raise SystemExit("No iteration was executed.")

    print(f"Created next version: {latest_result['targetVersionId']}")
    print(f"Analysis: {latest_result['analysisPath']}")
    print(f"Report: {latest_result['reportPath']}")
    print(f"Comparison: {latest_result['comparisonPath']}")
    print(f"Improved: {latest_result['isImproved']} (delta={latest_result['scoreDelta']})")


if __name__ == "__main__":
    main()
