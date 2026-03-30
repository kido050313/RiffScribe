# 中间对象 JSON Schema 草案 v1

## 文档目的

这份文档用于把前面定义的核心中间对象，进一步收敛成接近可实现的 JSON Schema 草案。

目标是让后续开发时：

- Python 分析层
- 自动评测层
- 版本管理层
- 前端工作台

都能围绕同一套稳定的数据格式工作，而不是各自定义一份近似但不一致的结构。

这份文档不是严格的 JSON Schema 标准文件，但会尽量贴近可实现格式。

---

## 一、设计范围

当前草案覆盖以下对象：

1. `InputAsset`
2. `StemCandidate`
3. `TimingGrid`
4. `PhraseSegment`
5. `BackboneNote`
6. `DetailedNote`
7. `FingeringCandidate`
8. `NotationCandidate`
9. `EvaluationReport`
10. `AdjustmentPlan`
11. `IterationSnapshot`

本文件重点是：

- 字段名统一
- 字段类型统一
- 必填字段明确
- 对象之间的引用关系明确

---

## 二、通用约定

### 1. ID 字段

所有核心对象统一使用字符串 ID：

- `taskId`
- `versionId`
- `assetId`
- `stemId`
- `phraseId`
- `noteId`
- `reportId`

建议格式：

- `task_001`
- `ver_001`
- `note_001`

### 2. 时间单位

所有时间相关字段统一使用：

- 秒
- `number`
- 保留小数

例如：

- `start`
- `end`
- `durationSec`

### 3. 分数字段

所有评分字段统一建议范围：

- `0.0 ~ 1.0`

### 4. 路径字段

所有文件路径统一为字符串：

- 相对项目根目录
- 或统一规则下的绝对路径

建议第一版优先用相对路径。

### 5. 枚举字段

所有状态类字段统一用字符串字面量，而不是数字编码。

---

## 三、InputAsset 草案

```json
{
  "assetId": "asset_001",
  "taskId": "task_001",
  "path": "samples/raw/test1.mp4",
  "type": "video",
  "durationSec": 33.76,
  "sampleRate": 44100,
  "channels": 2,
  "sourceLabel": "test1.mp4",
  "metadata": {
    "originalName": "test1.mp4"
  }
}
```

### 建议字段

- `assetId`: `string` 必填
- `taskId`: `string` 必填
- `path`: `string` 必填
- `type`: `"video" | "audio"` 必填
- `durationSec`: `number` 可选
- `sampleRate`: `number` 可选
- `channels`: `number` 可选
- `sourceLabel`: `string` 可选
- `metadata`: `object` 可选

---

## 四、StemCandidate 草案

```json
{
  "stemId": "stem_001",
  "taskId": "task_001",
  "versionId": "ver_001",
  "sourceAssetId": "asset_001",
  "stemType": "other",
  "path": "output/separated/htdemucs/test1/other.wav",
  "durationSec": 33.76,
  "qualityScore": 0.81,
  "selectionReason": "default_best_candidate"
}
```

### 建议字段

- `stemId`: `string` 必填
- `taskId`: `string` 必填
- `versionId`: `string` 必填
- `sourceAssetId`: `string` 必填
- `stemType`: `"extracted" | "other" | "vocals" | "bass" | "drums"` 必填
- `path`: `string` 必填
- `durationSec`: `number` 可选
- `qualityScore`: `number` 可选
- `selectionReason`: `string` 可选

---

## 五、TimingGrid 草案

```json
{
  "timingGridId": "grid_001",
  "taskId": "task_001",
  "versionId": "ver_001",
  "sourceStemId": "stem_001",
  "tempo": 105.47,
  "timeSignatureCandidates": ["4/4", "12/8"],
  "selectedTimeSignature": "4/4",
  "beats": [0.267, 0.9172, 1.4861],
  "downbeats": [0.267, 2.6239, 4.8878],
  "measures": [
    { "index": 0, "start": 0.267, "end": 2.6239 }
  ],
  "grooveLabel": "straight",
  "confidence": 0.74
}
```

### 建议字段

- `timingGridId`: `string` 必填
- `taskId`: `string` 必填
- `versionId`: `string` 必填
- `sourceStemId`: `string` 必填
- `tempo`: `number` 必填
- `timeSignatureCandidates`: `string[]` 可选
- `selectedTimeSignature`: `string` 必填
- `beats`: `number[]` 必填
- `downbeats`: `number[]` 可选
- `measures`: `Measure[]` 必填
- `grooveLabel`: `string` 可选
- `confidence`: `number` 可选

### `Measure`

```json
{
  "index": 0,
  "start": 0.267,
  "end": 2.6239
}
```

---

## 六、PhraseSegment 草案

```json
{
  "phraseId": "phrase_001",
  "taskId": "task_001",
  "versionId": "ver_001",
  "sourceStemId": "stem_001",
  "start": 0.267,
  "end": 2.6239,
  "measureRange": [0, 0],
  "pauseBefore": 0.0,
  "pauseAfter": 0.12,
  "densityScore": 0.68,
  "roleTag": "run"
}
```

### 建议字段

- `phraseId`: `string` 必填
- `taskId`: `string` 必填
- `versionId`: `string` 必填
- `sourceStemId`: `string` 必填
- `start`: `number` 必填
- `end`: `number` 必填
- `measureRange`: `[number, number]` 可选
- `pauseBefore`: `number` 可选
- `pauseAfter`: `number` 可选
- `densityScore`: `number` 可选
- `roleTag`: `string` 可选

---

## 七、BackboneNote 草案

```json
{
  "backboneNoteId": "backbone_001",
  "taskId": "task_001",
  "versionId": "ver_001",
  "phraseId": "phrase_001",
  "start": 0.3367,
  "end": 0.6269,
  "midiPitch": 56,
  "measureIndex": 0,
  "beatOffset": 0.12,
  "weight": 0.91,
  "role": "strong_beat"
}
```

### 建议字段

- `backboneNoteId`: `string` 必填
- `taskId`: `string` 必填
- `versionId`: `string` 必填
- `phraseId`: `string` 必填
- `start`: `number` 必填
- `end`: `number` 必填
- `midiPitch`: `number` 必填
- `measureIndex`: `number` 必填
- `beatOffset`: `number` 必填
- `weight`: `number` 可选
- `role`: `string` 可选

---

## 八、DetailedNote 草案

```json
{
  "noteId": "note_001",
  "taskId": "task_001",
  "versionId": "ver_001",
  "phraseId": "phrase_001",
  "parentBackboneId": "backbone_001",
  "start": 0.3367,
  "end": 0.6269,
  "midiPitch": 56,
  "measureIndex": 0,
  "beatOffset": 0.12,
  "durationBeats": 0.51,
  "noteClass": "backbone",
  "confidence": 0.83
}
```

### 建议字段

- `noteId`: `string` 必填
- `taskId`: `string` 必填
- `versionId`: `string` 必填
- `phraseId`: `string` 可选
- `parentBackboneId`: `string | null` 可选
- `start`: `number` 必填
- `end`: `number` 必填
- `midiPitch`: `number` 必填
- `measureIndex`: `number` 必填
- `beatOffset`: `number` 必填
- `durationBeats`: `number` 必填
- `noteClass`: `"backbone" | "passing" | "ornament" | "noise_candidate"` 必填
- `confidence`: `number` 可选

---

## 九、FingeringCandidate 草案

```json
{
  "fingeringId": "fingering_001",
  "taskId": "task_001",
  "versionId": "ver_001",
  "noteRefs": ["note_001", "note_002"],
  "stringAssignments": [3, 3],
  "fretAssignments": [7, 9],
  "positionRange": [7, 9],
  "continuityScore": 0.78,
  "feasibilityScore": 0.81
}
```

### 建议字段

- `fingeringId`: `string` 必填
- `taskId`: `string` 必填
- `versionId`: `string` 必填
- `noteRefs`: `string[]` 必填
- `stringAssignments`: `number[]` 可选
- `fretAssignments`: `number[]` 可选
- `positionRange`: `[number, number]` 可选
- `continuityScore`: `number` 可选
- `feasibilityScore`: `number` 可选

---

## 十、NotationCandidate 草案

```json
{
  "notationId": "notation_001",
  "taskId": "task_001",
  "versionId": "ver_001",
  "timingGridId": "grid_001",
  "phraseIds": ["phrase_001"],
  "noteIds": ["note_001", "note_002"],
  "fingeringId": "fingering_001",
  "tabRepresentation": {
    "tuning": [64, 59, 55, 50, 45, 40]
  },
  "staffRepresentation": {
    "clef": "treble"
  },
  "exportPaths": {
    "midi": "output/exports/test1.mid",
    "musicxml": "output/exports/test1.musicxml"
  }
}
```

### 建议字段

- `notationId`: `string` 必填
- `taskId`: `string` 必填
- `versionId`: `string` 必填
- `timingGridId`: `string` 必填
- `phraseIds`: `string[]` 可选
- `noteIds`: `string[]` 必填
- `fingeringId`: `string | null` 可选
- `tabRepresentation`: `object` 可选
- `staffRepresentation`: `object` 可选
- `exportPaths`: `object` 可选

---

## 十一、EvaluationReport 草案

```json
{
  "reportId": "report_001",
  "taskId": "task_001",
  "versionId": "ver_001",
  "notationId": "notation_001",
  "overall": {
    "score": 0.74,
    "confidence": 0.81,
    "rankHint": "usable",
    "summary": "节奏结构明显改善，但局部仍偏碎。"
  },
  "metrics": {
    "rhythm": { "score": 0.79 },
    "pitch": { "score": 0.68 }
  },
  "diagnosis": {
    "primaryIssues": ["note_fragmentation_high"],
    "riskLevel": "medium"
  },
  "adjustments": {
    "recommendedActions": ["increase_min_note_duration"]
  },
  "comparison": {
    "previousCandidateId": "ver_000",
    "scoreDelta": 0.08,
    "isImproved": true
  }
}
```

### 建议字段

- `reportId`: `string` 必填
- `taskId`: `string` 必填
- `versionId`: `string` 必填
- `notationId`: `string` 必填
- `overall`: `object` 必填
- `metrics`: `object` 必填
- `diagnosis`: `object` 必填
- `adjustments`: `object` 可选
- `comparison`: `object` 可选

说明：

- 详细字段以《自动评测报告格式定义 v1》为准

---

## 十二、AdjustmentPlan 草案

```json
{
  "adjustmentPlanId": "plan_001",
  "taskId": "task_001",
  "sourceVersionId": "ver_001",
  "targetVersionId": "ver_002",
  "priority": "phrase_first",
  "actions": [
    "increase_min_note_duration",
    "merge_short_notes"
  ],
  "parameterChanges": {
    "minNoteDuration": 0.08
  },
  "expectedGoal": "减少碎 note，提高节奏可读性"
}
```

### 建议字段

- `adjustmentPlanId`: `string` 必填
- `taskId`: `string` 必填
- `sourceVersionId`: `string` 必填
- `targetVersionId`: `string` 必填
- `priority`: `string` 可选
- `actions`: `string[]` 必填
- `parameterChanges`: `object` 可选
- `expectedGoal`: `string` 可选

---

## 十三、IterationSnapshot 草案

```json
{
  "snapshotId": "snapshot_001",
  "taskId": "task_001",
  "versionId": "ver_001",
  "inputAssetId": "asset_001",
  "selectedStemId": "stem_001",
  "timingGridId": "grid_001",
  "phraseIds": ["phrase_001"],
  "notationId": "notation_001",
  "reportId": "report_001",
  "adjustmentPlanId": "plan_001",
  "status": "completed"
}
```

### 建议字段

- `snapshotId`: `string` 必填
- `taskId`: `string` 必填
- `versionId`: `string` 必填
- `inputAssetId`: `string` 必填
- `selectedStemId`: `string` 可选
- `timingGridId`: `string` 可选
- `phraseIds`: `string[]` 可选
- `notationId`: `string` 可选
- `reportId`: `string` 可选
- `adjustmentPlanId`: `string | null` 可选
- `status`: `"created" | "analyzing" | "evaluating" | "completed" | "failed" | "discarded" | "selected_best"` 必填

---

## 十四、引用关系约束

为保证数据一致性，建议在实现中加入以下约束：

- `StemCandidate.sourceAssetId` 必须指向已有 `InputAsset`
- `TimingGrid.sourceStemId` 必须指向已有 `StemCandidate`
- `PhraseSegment.sourceStemId` 应与同版本 `TimingGrid.sourceStemId` 一致
- `BackboneNote.phraseId` 必须指向已有 `PhraseSegment`
- `DetailedNote.parentBackboneId` 若存在，必须指向已有 `BackboneNote`
- `NotationCandidate.noteIds` 中的每个 ID 必须指向已有 `DetailedNote`
- `EvaluationReport.notationId` 必须指向已有 `NotationCandidate`
- `AdjustmentPlan.sourceVersionId` 和 `targetVersionId` 必须属于同一 `taskId`

---

## 十五、最小可用对象集建议

为了尽快进入开发，第一阶段不需要一次性实现所有对象。

建议最小可用对象集为：

- `InputAsset`
- `StemCandidate`
- `TimingGrid`
- `DetailedNote`
- `NotationCandidate`
- `EvaluationReport`
- `AdjustmentPlan`
- `IterationSnapshot`

等最小闭环跑通后，再逐步补：

- `PhraseSegment`
- `BackboneNote`
- `FingeringCandidate`

---

## 十六、文件组织建议

建议未来每个对象都能独立落盘，便于调试和版本追踪。

例如：

```txt
output/tasks/task_001/
  task.json
  versions/ver_001/
    input-asset.json
    stem-candidate.json
    timing-grid.json
    detailed-notes.json
    notation-candidate.json
    evaluation-report.json
    adjustment-plan.json
    iteration-snapshot.json
```

这样做的好处是：

- 每轮结果都可独立查看
- 不依赖内存状态就能复盘
- 前端和后端都能直接读取

---

## 十七、与开发的关系

写完这份草案后，后续开发就可以直接进入：

1. 先按这些对象定义 TypeScript 类型
2. 再按这些对象定义 Python 输出结构
3. 再让评测、版本管理和前端统一消费这些结构

换句话说，这份文档的作用就是把“设计讨论”正式转成“开发接口”。

---

## 十八、这份文档之后建议做什么

到这一步，文档层面已经足够进入开发。

下一步最合适的，不再是继续堆设计文档，而是进入：

1. 《最小闭环开发任务拆解 v1》
2. 或直接开始代码实现

建议优先做第 1 个，把文档真正转成开发任务清单，然后就进入开发。
