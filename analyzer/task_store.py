from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def version_directory(repo_root: Path, task_id: str, version_id: str) -> Path:
    return repo_root / "output" / "tasks" / task_id / "versions" / version_id


def task_index_path(repo_root: Path, task_id: str) -> Path:
    return repo_root / "output" / "tasks" / task_id / "task.json"


def export_paths_for_analysis(repo_root: Path, analysis_path: Path) -> dict[str, Path]:
    stem_name = analysis_path.stem.replace(".analysis", "")
    export_dir = repo_root / "output" / "exports"
    return {
        "midi": export_dir / f"{stem_name}.mid",
        "musicxml": export_dir / f"{stem_name}.musicxml",
    }


def copy_if_exists(source: Path, destination: Path) -> str | None:
    if not source.exists():
        return None
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return str(destination)


def build_params_snapshot(analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "selectedStem": analysis.get("stemCandidate", {}).get("stemType"),
        "timeSignature": analysis.get("timingGrid", {}).get("selectedTimeSignature")
        or analysis.get("timeSignature"),
        "grooveLabel": analysis.get("timingGrid", {}).get("grooveLabel"),
        "tempo": analysis.get("bpm"),
        "analysisSchemaVersion": analysis.get("schemaVersion"),
        "evaluationSchemaVersion": "evaluation.v1",
        "pitchRange": {
            "lower": 40,
            "upper": 88,
        },
        "filtering": {
            "minNoteDurationBeats": 0.25,
        },
    }


def build_iteration_snapshot(
    analysis: dict[str, Any],
    report: dict[str, Any],
    artifact_paths: dict[str, str | None],
) -> dict[str, Any]:
    return {
        "snapshotId": f"snapshot_{analysis['versionId']}",
        "taskId": analysis["taskId"],
        "versionId": analysis["versionId"],
        "inputAssetId": analysis.get("inputAsset", {}).get("assetId"),
        "selectedStemId": analysis.get("stemCandidate", {}).get("stemId"),
        "timingGridId": analysis.get("timingGrid", {}).get("timingGridId"),
        "notationId": analysis.get("notationCandidate", {}).get("notationId"),
        "reportId": report.get("reportId"),
        "adjustmentPlanId": None,
        "status": "completed",
        "artifacts": artifact_paths,
        "overallScore": report.get("overall", {}).get("score"),
        "primaryIssues": report.get("diagnosis", {}).get("primaryIssues", []),
    }


def update_task_index(
    repo_root: Path,
    analysis: dict[str, Any],
    report: dict[str, Any],
    version_root: Path,
    artifact_paths: dict[str, str | None],
) -> Path:
    task_id = analysis["taskId"]
    version_id = analysis["versionId"]
    index_path = task_index_path(repo_root, task_id)
    task_payload: dict[str, Any]
    if index_path.exists():
        task_payload = load_json(index_path)
    else:
        task_payload = {
            "taskId": task_id,
            "inputAsset": analysis.get("inputAsset", {}),
            "status": "active",
            "createdFrom": analysis.get("sourceName"),
            "latestVersionId": version_id,
            "bestVersionId": version_id,
            "stableVersionId": version_id,
            "versionIds": [],
            "versions": {},
        }

    if version_id not in task_payload["versionIds"]:
        task_payload["versionIds"].append(version_id)

    current_score = float(report.get("overall", {}).get("score", 0.0))
    best_version_id = task_payload.get("bestVersionId")
    best_score = -1.0
    if best_version_id and best_version_id in task_payload.get("versions", {}):
        best_score = float(task_payload["versions"][best_version_id].get("overallScore", -1.0))

    if current_score >= best_score:
        task_payload["bestVersionId"] = version_id
        task_payload["stableVersionId"] = version_id

    task_payload["latestVersionId"] = version_id
    task_payload["versions"][version_id] = {
        "versionId": version_id,
        "iterationIndex": len(task_payload["versionIds"]),
        "status": "completed",
        "overallScore": current_score,
        "primaryIssues": report.get("diagnosis", {}).get("primaryIssues", []),
        "recommendedActions": report.get("adjustments", {}).get("recommendedActions", []),
        "selectedStem": analysis.get("stemCandidate", {}).get("stemType"),
        "paths": {
            "versionRoot": str(version_root),
            **artifact_paths,
        },
    }

    save_json(index_path, task_payload)
    return index_path


def materialize_version_artifacts(
    repo_root: Path,
    analysis_path: Path,
    report_path: Path,
) -> dict[str, str]:
    analysis = load_json(analysis_path)
    report = load_json(report_path)
    task_id = str(analysis["taskId"])
    version_id = str(analysis["versionId"])
    version_root = version_directory(repo_root, task_id, version_id)
    version_root.mkdir(parents=True, exist_ok=True)

    candidate_path = version_root / "candidate.json"
    save_json(candidate_path, analysis)

    local_report_path = version_root / "evaluation-report.json"
    save_json(local_report_path, report)

    params_path = version_root / "params.json"
    save_json(params_path, build_params_snapshot(analysis))

    export_sources = export_paths_for_analysis(repo_root, analysis_path)
    artifact_paths: dict[str, str | None] = {
        "candidate": str(candidate_path),
        "evaluationReport": str(local_report_path),
        "params": str(params_path),
        "midi": copy_if_exists(export_sources["midi"], version_root / "export.mid"),
        "musicxml": copy_if_exists(export_sources["musicxml"], version_root / "export.musicxml"),
    }

    snapshot_path = version_root / "iteration-snapshot.json"
    save_json(snapshot_path, build_iteration_snapshot(analysis, report, artifact_paths))
    artifact_paths["snapshot"] = str(snapshot_path)

    index_path = update_task_index(repo_root, analysis, report, version_root, artifact_paths)
    artifact_paths["taskIndex"] = str(index_path)

    return {key: value for key, value in artifact_paths.items() if value}
