# 自动评测报告格式定义 v1

## 文档目的

这份文档用于定义自动评测系统输出的标准报告结构。

目标是让评测结果不再只是一个模糊分数，而是变成一个：

- 机器可读
- 研发可分析
- 系统可用于自动调参
- 产品可展示给用户

的统一中间对象。

这份文档偏工程设计，会更接近后续代码实现。

---

## 一、为什么要定义统一报告格式

如果没有统一格式，评测系统很容易变成：

- 某些分数写在日志里
- 某些问题写在控制台里
- 某些建议写在脑子里
- 每次输出都不一致

这样会导致：

- 无法自动比较多轮结果
- 无法自动生成调整策略
- 无法做版本追踪
- 无法把结果稳定展示给用户

因此，评测报告必须成为系统里的正式数据结构，而不是临时文本输出。

---

## 二、这份报告要服务谁

自动评测报告需要同时服务三类对象。

### 1. 服务算法系统

系统需要从报告里读出：

- 当前结果主要哪里差
- 下一轮优先改哪一层
- 哪个候选版本更优

### 2. 服务研发

研发需要从报告里看到：

- 每次优化是否有效
- 当前瓶颈在哪
- 哪类输入经常失败

### 3. 服务产品与用户

产品层需要从报告里抽取：

- 当前可信度
- 哪些小节问题大
- 是否建议用户重点检查某些位置

因此，这份报告必须同时兼顾：

- 可计算
- 可追踪
- 可展示

---

## 三、报告的总体结构

建议一份完整评测报告由以下几部分组成：

1. 基础元信息
2. 输入信息
3. 当前候选版本信息
4. 总体评分
5. 分项评分
6. 问题诊断
7. 调整建议
8. 版本比较信息
9. 调试附加信息

---

## 四、基础元信息定义

### 目标

记录这份报告是在什么上下文中生成的。

### 建议字段

- `reportId`
- `createdAt`
- `pipelineVersion`
- `evaluationVersion`
- `taskId`
- `iterationIndex`

### 字段说明

- `reportId`
  - 当前报告唯一 ID
- `createdAt`
  - 报告生成时间
- `pipelineVersion`
  - 当前转谱流水线版本
- `evaluationVersion`
  - 当前评测逻辑版本
- `taskId`
  - 当前输入任务 ID
- `iterationIndex`
  - 当前是第几轮候选谱

意义：

- 便于后续追踪同一任务在不同版本算法下的表现

---

## 五、输入信息定义

### 目标

记录当前这份报告评测的是哪份输入，以及用了哪条分析轨道。

### 建议字段

- `input.assetPath`
- `input.assetType`
- `input.durationSec`
- `input.selectedStem`
- `input.availableStems`
- `input.sourceName`

### 字段说明

- `assetPath`
  - 原始输入路径
- `assetType`
  - video / audio
- `durationSec`
  - 输入时长
- `selectedStem`
  - 当前参与分析的 stem
- `availableStems`
  - 当前可选 stem 列表
- `sourceName`
  - 当前实际参与评测的音频文件名

意义：

- 同一输入可能基于不同 stem 得到不同结果，必须记录清楚

---

## 六、候选版本信息定义

### 目标

记录当前评测对象本身的关键信息。

### 建议字段

- `candidate.candidateId`
- `candidate.analysisPath`
- `candidate.exportPaths`
- `candidate.noteCount`
- `candidate.measureCount`
- `candidate.beatCount`
- `candidate.tempo`
- `candidate.timeSignature`

### 字段说明

- `candidateId`
  - 当前候选谱版本 ID
- `analysisPath`
  - 当前候选谱对应的分析 JSON 路径
- `exportPaths`
  - 当前导出的 MIDI / MusicXML 路径
- `noteCount`
  - note 数量
- `measureCount`
  - 小节数量
- `beatCount`
  - 拍点数量
- `tempo`
  - 当前估计 BPM
- `timeSignature`
  - 当前拍号假设

意义：

- 便于快速识别某一版结果的结构特征是否异常

---

## 七、总体评分定义

### 目标

给出一个可用于排序的总体分数，但不替代分项评分。

### 建议字段

- `overall.score`
- `overall.confidence`
- `overall.rankHint`
- `overall.summary`

### 字段说明

- `score`
  - 综合评分，建议范围 0 到 1
- `confidence`
  - 系统对当前评测结论的信心
- `rankHint`
  - 例如 excellent / usable / weak / failed
- `summary`
  - 一句简要摘要

说明：

- `overall.score` 用于多版本排序
- `overall.confidence` 用于避免系统对不稳定结果过度自信

---

## 八、分项评分定义

这是整份报告最核心的部分。

建议至少包含以下维度。

### 1. 节奏结构评分

字段建议：

- `metrics.rhythm.score`
- `metrics.rhythm.beatAlignment`
- `metrics.rhythm.downbeatAlignment`
- `metrics.rhythm.measureBoundaryScore`
- `metrics.rhythm.onsetDeviationMean`
- `metrics.rhythm.onsetDeviationMedian`

### 2. 乐句结构评分

字段建议：

- `metrics.phrase.score`
- `metrics.phrase.boundarySimilarity`
- `metrics.phrase.pauseAlignment`
- `metrics.phrase.densitySimilarity`

### 3. 骨架音评分

字段建议：

- `metrics.backbone.score`
- `metrics.backbone.strongBeatMatch`
- `metrics.backbone.longNoteMatch`
- `metrics.backbone.endingNoteMatch`

### 4. 细节音评分

字段建议：

- `metrics.detail.score`
- `metrics.detail.ornamentDensityScore`
- `metrics.detail.subdivisionSimilarity`
- `metrics.detail.fastNoteGroupScore`

### 5. 音高评分

字段建议：

- `metrics.pitch.score`
- `metrics.pitch.contourSimilarity`
- `metrics.pitch.stablePitchAccuracy`
- `metrics.pitch.outlierRatio`
- `metrics.pitch.excessiveLeapPenalty`

### 6. 可演奏性评分

字段建议：

- `metrics.playability.score`
- `metrics.playability.fingeringFeasibility`
- `metrics.playability.positionContinuity`
- `metrics.playability.impossibleFingeringCount`

说明：

- 所有一级分项建议都保留一个 `score`
- 下面再拆具体子指标
- 这样既方便前端展示，也方便系统自动决策

---

## 九、问题诊断定义

### 目标

让系统不仅知道“得分低”，还知道“为什么低”。

### 建议字段

- `diagnosis.primaryIssues`
- `diagnosis.secondaryIssues`
- `diagnosis.measureWarnings`
- `diagnosis.noteWarnings`
- `diagnosis.riskLevel`

### 字段说明

#### `primaryIssues`

当前最主要的 1 到 3 个问题。

例如：

- beat_alignment_low
- note_fragmentation_high
- pitch_outlier_high

#### `secondaryIssues`

次级问题列表。

#### `measureWarnings`

按小节记录问题。

例如：

- 第 5 小节音符过密
- 第 8 小节句尾时值不稳
- 第 12 小节 downbeat 偏移大

#### `noteWarnings`

按音符记录异常。

例如：

- 异常高音
- 过短 note
- 与前后音关系不合理

#### `riskLevel`

例如：

- low
- medium
- high
- critical

意义：

- 这是系统自动调参与用户人工复核的关键入口

---

## 十、调整建议定义

### 目标

把问题诊断转成下一轮可执行动作。

### 建议字段

- `adjustments.recommendedActions`
- `adjustments.priority`
- `adjustments.nextStrategy`
- `adjustments.parameterHints`

### 字段说明

#### `recommendedActions`

动作列表，例如：

- retune_beat_tracking
- rerun_downbeat_detection
- increase_min_note_duration
- merge_short_notes
- limit_pitch_range
- switch_input_stem
- rerun_phrase_segmentation

#### `priority`

建议先处理哪一类问题。

例如：

- rhythm_first
- pitch_first
- stem_first
- phrase_first

#### `nextStrategy`

下一轮策略摘要，例如：

- 先换 stem，再重跑节奏层
- 保持 stem 不变，先修 note fragmentation

#### `parameterHints`

具体参数建议，例如：

- `minNoteDuration += 0.03`
- `pitchUpperBound = 84`
- `phrasePauseThreshold += 0.08`

意义：

- 这是报告和自动调参模块之间的直接接口

---

## 十一、版本比较信息定义

### 目标

支持多轮候选谱之间的自动比较。

### 建议字段

- `comparison.previousCandidateId`
- `comparison.previousScore`
- `comparison.scoreDelta`
- `comparison.metricDeltas`
- `comparison.isImproved`

### 字段说明

- `previousCandidateId`
  - 上一轮候选版本
- `previousScore`
  - 上一轮总体评分
- `scoreDelta`
  - 本轮提升或下降多少
- `metricDeltas`
  - 各分项变化
- `isImproved`
  - 当前版本是否优于上一轮

意义：

- 这是迭代系统决定“继续沿这个方向优化还是回退”的基础

---

## 十二、调试附加信息定义

### 目标

为研发保留足够的分析上下文，但不污染用户侧结果。

### 建议字段

- `debug.runtimeMs`
- `debug.modelVersions`
- `debug.parameterSnapshot`
- `debug.intermediatePaths`
- `debug.logs`

说明：

- 用户界面不一定直接展示这些字段
- 但研发和回归分析会依赖这部分信息

---

## 十三、建议的 JSON 结构示例

```json
{
  "reportId": "report_001",
  "createdAt": "2026-03-30T12:00:00Z",
  "pipelineVersion": "v1",
  "evaluationVersion": "v1",
  "taskId": "task_001",
  "iterationIndex": 2,
  "input": {
    "assetPath": "samples/raw/test1.mp4",
    "assetType": "video",
    "durationSec": 33.76,
    "selectedStem": "other.wav",
    "availableStems": ["other.wav", "vocals.wav", "bass.wav", "drums.wav"],
    "sourceName": "other.wav"
  },
  "candidate": {
    "candidateId": "candidate_v2",
    "analysisPath": "output/analysis/test1.analysis.json",
    "exportPaths": {
      "midi": "output/exports/test1.mid",
      "musicxml": "output/exports/test1.musicxml"
    },
    "noteCount": 84,
    "measureCount": 15,
    "beatCount": 58,
    "tempo": 105.47,
    "timeSignature": "4/4"
  },
  "overall": {
    "score": 0.74,
    "confidence": 0.81,
    "rankHint": "usable",
    "summary": "节奏结构明显改善，但第 5 至 8 小节仍然偏碎。"
  },
  "metrics": {
    "rhythm": {
      "score": 0.79,
      "beatAlignment": 0.82,
      "downbeatAlignment": 0.74,
      "measureBoundaryScore": 0.78,
      "onsetDeviationMean": 0.041,
      "onsetDeviationMedian": 0.026
    },
    "phrase": {
      "score": 0.69,
      "boundarySimilarity": 0.66,
      "pauseAlignment": 0.71,
      "densitySimilarity": 0.70
    },
    "backbone": {
      "score": 0.76,
      "strongBeatMatch": 0.80,
      "longNoteMatch": 0.72,
      "endingNoteMatch": 0.75
    },
    "detail": {
      "score": 0.61,
      "ornamentDensityScore": 0.55,
      "subdivisionSimilarity": 0.67,
      "fastNoteGroupScore": 0.60
    },
    "pitch": {
      "score": 0.68,
      "contourSimilarity": 0.73,
      "stablePitchAccuracy": 0.65,
      "outlierRatio": 0.09,
      "excessiveLeapPenalty": 0.12
    },
    "playability": {
      "score": 0.72,
      "fingeringFeasibility": 0.77,
      "positionContinuity": 0.70,
      "impossibleFingeringCount": 1
    }
  },
  "diagnosis": {
    "primaryIssues": ["note_fragmentation_high", "phrase_boundary_unstable"],
    "secondaryIssues": ["pitch_outlier_medium"],
    "measureWarnings": [
      "第 5 小节音符过密",
      "第 8 小节句尾时值偏短"
    ],
    "noteWarnings": [
      "检测到 7 个过短音符",
      "检测到 4 个高音异常值"
    ],
    "riskLevel": "medium"
  },
  "adjustments": {
    "recommendedActions": [
      "increase_min_note_duration",
      "merge_short_notes",
      "rerun_phrase_segmentation"
    ],
    "priority": "phrase_first",
    "nextStrategy": "先减少碎 note，再重新切分乐句。",
    "parameterHints": {
      "minNoteDuration": 0.08,
      "phrasePauseThreshold": 0.12
    }
  },
  "comparison": {
    "previousCandidateId": "candidate_v1",
    "previousScore": 0.66,
    "scoreDelta": 0.08,
    "metricDeltas": {
      "rhythm": 0.05,
      "phrase": 0.03,
      "pitch": 0.01
    },
    "isImproved": true
  },
  "debug": {
    "runtimeMs": 1842,
    "modelVersions": {
      "beat": "librosa_v1",
      "pitch": "piptrack_v1"
    },
    "parameterSnapshot": {
      "minNoteDuration": 0.05,
      "pitchUpperBound": 88
    },
    "intermediatePaths": {
      "stem": "output/separated/htdemucs/test1/other.wav"
    },
    "logs": []
  }
}
```

---

## 十四、当前阶段建议先实现哪一部分

不需要一开始把整份报告全部实现完。

建议先做最小可用版：

### Phase 1

先实现：

- `overall`
- `metrics.rhythm`
- `metrics.pitch`
- `diagnosis.primaryIssues`
- `adjustments.recommendedActions`

### Phase 2

再补：

- `phrase`
- `backbone`
- `comparison`

### Phase 3

最后补：

- `playability`
- `debug`
- 完整多轮版本支持

---

## 十五、这份文档的下一步

这份报告结构定义完成后，下一步最适合继续产出：

1. 《多轮候选谱版本管理设计 v1》
2. 《核心中间数据结构设计 v1》
3. 《自动调参策略映射表 v1》

这样就可以从“报告长什么样”继续推进到“系统怎么根据报告行动”。
