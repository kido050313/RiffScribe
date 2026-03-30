from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from schemas import AdjustmentPlan
from task_store import attach_adjustment_plan, load_json, next_version_id_from


ActionHandler = Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], tuple[dict[str, Any], dict[str, Any]]]


STEM_PRIORITY = ["other", "extracted", "vocals", "bass", "drums"]


def switch_input_stem(params: dict[str, Any], report: dict[str, Any], task_payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    current_stem = str(params.get("selectedStem") or "other")
    if current_stem not in STEM_PRIORITY:
        next_stem = STEM_PRIORITY[0]
    else:
        next_stem = STEM_PRIORITY[(STEM_PRIORITY.index(current_stem) + 1) % len(STEM_PRIORITY)]
    next_params = deepcopy(params)
    next_params["selectedStem"] = next_stem
    return next_params, {
        "selectedStem": next_stem,
        "reason": f"switch stem from {current_stem} to {next_stem}",
    }


def retune_beat_tracking(params: dict[str, Any], report: dict[str, Any], task_payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    next_params = deepcopy(params)
    beat_tracking = deepcopy(next_params.get("beatTracking") or {})
    beat_tracking["strategy"] = "librosa_retuned"
    beat_tracking["tightness"] = int(beat_tracking.get("tightness", 100)) + 25
    next_params["beatTracking"] = beat_tracking
    return next_params, {
        "beatTracking": beat_tracking,
        "reason": "increase beat tracking tightness to improve onset alignment",
    }


def increase_min_note_duration(params: dict[str, Any], report: dict[str, Any], task_payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    next_params = deepcopy(params)
    filtering = deepcopy(next_params.get("filtering") or {})
    current_value = float(filtering.get("minNoteDurationBeats", 0.25))
    filtering["minNoteDurationBeats"] = round(current_value + 0.125, 4)
    next_params["filtering"] = filtering
    return next_params, {
        "filtering": filtering,
        "reason": "raise minimum note duration to reduce fragmentation",
    }


def limit_pitch_range(params: dict[str, Any], report: dict[str, Any], task_payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    next_params = deepcopy(params)
    pitch_range = deepcopy(next_params.get("pitchRange") or {"lower": 40, "upper": 88})
    pitch_range["upper"] = min(int(pitch_range.get("upper", 88)), 84)
    next_params["pitchRange"] = pitch_range
    return next_params, {
        "pitchRange": pitch_range,
        "reason": "reduce upper pitch bound to suppress outliers",
    }


def fix_measure_alignment(params: dict[str, Any], report: dict[str, Any], task_payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    next_params = deepcopy(params)
    beat_tracking = deepcopy(next_params.get("beatTracking") or {})
    beat_tracking["startMeasureOffsetBeats"] = round(float(beat_tracking.get("startMeasureOffsetBeats", 0.0)) + 0.25, 4)
    beat_tracking["strategy"] = "measure_reanchored"
    next_params["beatTracking"] = beat_tracking
    return next_params, {
        "beatTracking": beat_tracking,
        "reason": "shift first-measure anchor to absorb negative beat offsets",
    }


ACTION_HANDLERS: dict[str, ActionHandler] = {
    "switch_input_stem": switch_input_stem,
    "retune_beat_tracking": retune_beat_tracking,
    "increase_min_note_duration": increase_min_note_duration,
    "limit_pitch_range": limit_pitch_range,
    "fix_measure_alignment": fix_measure_alignment,
}


PRIORITY_TO_ACTIONS: dict[str, list[str]] = {
    "rhythm_first": ["fix_measure_alignment", "retune_beat_tracking", "increase_min_note_duration"],
    "pitch_first": ["limit_pitch_range", "switch_input_stem"],
}


def choose_actions(report: dict[str, Any]) -> list[str]:
    recommended = [
        action
        for action in report.get("adjustments", {}).get("recommendedActions", [])
        if action in ACTION_HANDLERS
    ]
    if recommended:
        return recommended[:2]

    priority = str(report.get("adjustments", {}).get("priority") or "rhythm_first")
    return PRIORITY_TO_ACTIONS.get(priority, ["retune_beat_tracking"])[:2]


def build_adjustment_plan(
    report: dict[str, Any],
    params: dict[str, Any],
    task_payload: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    task_payload = task_payload or {}
    task_id = str(report["taskId"])
    source_version_id = str(report["versionId"])
    target_version_id = next_version_id_from(source_version_id)
    actions = choose_actions(report)

    next_params = deepcopy(params)
    parameter_changes: dict[str, Any] = {}
    for action in actions:
        handler = ACTION_HANDLERS[action]
        next_params, change = handler(next_params, report, task_payload)
        parameter_changes[action] = change

    priority = report.get("adjustments", {}).get("priority") or "rhythm_first"
    trigger_issues = report.get("diagnosis", {}).get("primaryIssues", [])
    expected_goal = report.get("adjustments", {}).get("nextStrategy") or "apply the selected tuning actions"

    plan = AdjustmentPlan(
        adjustmentPlanId=f"plan_{source_version_id}",
        taskId=task_id,
        sourceVersionId=source_version_id,
        targetVersionId=target_version_id,
        priority=priority,
        actions=actions,
        parameterChanges=parameter_changes,
        expectedGoal=expected_goal,
        triggerIssues=trigger_issues,
    ).to_dict()
    plan["schemaVersion"] = "adjustment.v1"
    return plan, next_params


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a minimal adjustment plan from an evaluation report.")
    parser.add_argument("--report", type=Path, required=True, help="Path to the evaluation-report.json file.")
    parser.add_argument("--params", type=Path, required=True, help="Path to the params.json file.")
    parser.add_argument("--task-index", type=Path, help="Optional task.json path for context.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.report.exists():
        raise SystemExit(f"Evaluation report not found: {args.report}")
    if not args.params.exists():
        raise SystemExit(f"Params file not found: {args.params}")

    report = load_json(args.report)
    params = load_json(args.params)
    task_payload = load_json(args.task_index) if args.task_index and args.task_index.exists() else {}

    plan, next_params = build_adjustment_plan(report, params, task_payload)
    repo_root = Path(__file__).resolve().parent.parent
    artifact_paths = attach_adjustment_plan(
        repo_root=repo_root,
        task_id=str(report["taskId"]),
        version_id=str(report["versionId"]),
        adjustment_plan=plan,
        next_params=next_params,
    )

    print(f"Wrote adjustment plan to: {artifact_paths['adjustmentPlan']}")
    print(f"Wrote next params to: {artifact_paths['nextParams']}")
    print(f"Actions: {', '.join(plan['actions'])}")
    print(f"Target version: {plan['targetVersionId']}")


if __name__ == "__main__":
    main()
