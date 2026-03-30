# 核心中间数据结构设计 v1

## 文档目的

这份文档用于定义自动转谱系统内部最关键的一组中间数据结构。

目标是解决以下问题：

- 流水线不同阶段之间，应该传递什么对象？
- 哪些对象负责节奏框架，哪些负责乐句和骨架，哪些负责最终谱面？
- 自动评测、自动调参与版本管理，如何共用统一的数据模型？

这份文档是从“上层设计”走向“工程实现”的关键一步。

---

## 一、为什么需要中间数据结构层

如果系统内部只有：

- 音频文件
- 若干临时变量
- 一份 `notes` 数组
- 最终导出的 `MusicXML`

那么系统很快会遇到问题：

- 难以表达乐句和骨架
- 难以区分主音和装饰音
- 难以支持自动评测
- 难以支持自动调参
- 难以支持多轮版本比较

因此，系统内部必须有一组正式的中间对象，作为各阶段之间的稳定接口。

---

## 二、设计原则

### 1. 按阶段分层，而不是按文件分层

数据结构应反映系统处理流程：

- 输入层
- 预处理层
- 节奏层
- 乐句层
- 骨架层
- 细节层
- 谱面层
- 评测层
- 调整层

### 2. 允许同一音频存在多个候选结果

很多阶段都不是单一答案，而是候选集。例如：

- 多个 stem 候选
- 多个拍号候选
- 多个 phrase 切分候选
- 多个指法候选

所以结构设计不能假设每一步只有一个结果。

### 3. 区分“原始检测结果”和“加工后的结构化结果”

例如：

- 原始 onset 检测结果
- 量化后的节奏结构
- 原始 pitch 候选
- 平滑后的骨架音

这两类信息不能混在一起。

### 4. 为自动评测和版本管理预留关联字段

每个关键对象都建议能追溯到：

- 当前任务
- 当前版本
- 当前父对象
- 当前来源阶段

---

## 三、建议的核心对象总览

建议系统至少定义以下对象：

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

这 11 个对象基本可以覆盖整个自动化流水线。

---

## 四、InputAsset

### 作用

表示一条原始输入素材。

### 建议字段

- `assetId`
- `taskId`
- `path`
- `type`
- `durationSec`
- `sampleRate`
- `channels`
- `sourceLabel`
- `metadata`

### 说明

- `type`
  - `video` / `audio`
- `sourceLabel`
  - 用户可读名称
- `metadata`
  - 可扩展信息，例如上传时间、原始文件名等

### 意义

这是整条链路的根对象。

---

## 五、StemCandidate

### 作用

表示预处理层输出的一条候选音轨。

### 建议字段

- `stemId`
- `taskId`
- `versionId`
- `sourceAssetId`
- `stemType`
- `path`
- `durationSec`
- `qualityScore`
- `selectionReason`

### 说明

- `stemType`
  - `extracted` / `other` / `vocals` / `bass` / `drums`
- `qualityScore`
  - 系统对该 stem 可用性的初步评分
- `selectionReason`
  - 为什么选它进入后续分析

### 意义

为“自动选 stem”提供统一载体。

---

## 六、TimingGrid

### 作用

表示整段音频的时间结构。

### 建议字段

- `timingGridId`
- `taskId`
- `versionId`
- `sourceStemId`
- `tempo`
- `timeSignatureCandidates`
- `selectedTimeSignature`
- `beats`
- `downbeats`
- `measures`
- `grooveLabel`
- `confidence`

### 说明

- `beats`
  - 拍点列表
- `downbeats`
  - 强拍或小节起点候选
- `measures`
  - 小节对象列表
- `grooveLabel`
  - 例如 `straight` / `shuffle` / `swing`

### 意义

这是后续 phrase、骨架和细节生成的基础。

---

## 七、PhraseSegment

### 作用

表示一个乐句片段。

### 建议字段

- `phraseId`
- `taskId`
- `versionId`
- `sourceStemId`
- `start`
- `end`
- `measureRange`
- `pauseBefore`
- `pauseAfter`
- `densityScore`
- `roleTag`

### 说明

- `measureRange`
  - 所属小节范围
- `pauseBefore` / `pauseAfter`
  - 句前后停顿时长
- `densityScore`
  - 当前乐句的音符密度
- `roleTag`
  - 可扩展成 `intro`, `fill`, `ending`, `run` 等

### 意义

把连续音流组织成“人类可理解的句子单位”。

---

## 八、BackboneNote

### 作用

表示一条骨架音。

### 建议字段

- `backboneNoteId`
- `taskId`
- `versionId`
- `phraseId`
- `start`
- `end`
- `midiPitch`
- `measureIndex`
- `beatOffset`
- `weight`
- `role`

### 说明

- `weight`
  - 该骨架音的重要程度
- `role`
  - 例如 `strong_beat`, `long_note`, `ending_note`, `target_note`

### 意义

这是“先抓骨架”的系统表达。

---

## 九、DetailedNote

### 作用

表示细节层中的完整音符对象。

### 建议字段

- `noteId`
- `taskId`
- `versionId`
- `phraseId`
- `parentBackboneId`
- `start`
- `end`
- `midiPitch`
- `measureIndex`
- `beatOffset`
- `durationBeats`
- `noteClass`
- `confidence`

### 说明

- `parentBackboneId`
  - 这条细节音附属于哪条骨架音
- `noteClass`
  - `backbone`, `passing`, `ornament`, `noise_candidate`
- `confidence`
  - 当前 note 的可信度

### 意义

把所有音统一组织起来，同时保留主次关系。

---

## 十、FingeringCandidate

### 作用

表示某条音符或某句旋律的吉他指法候选。

### 建议字段

- `fingeringId`
- `taskId`
- `versionId`
- `noteRefs`
- `stringAssignments`
- `fretAssignments`
- `positionRange`
- `continuityScore`
- `feasibilityScore`

### 说明

- `noteRefs`
  - 对应的音符列表
- `positionRange`
  - 当前候选主要覆盖的把位范围
- `continuityScore`
  - 把位平滑程度
- `feasibilityScore`
  - 可演奏性评分

### 意义

这是从“音高结果”走向“吉他谱表达”的关键对象。

---

## 十一、NotationCandidate

### 作用

表示最终导出的候选谱对象。

### 建议字段

- `notationId`
- `taskId`
- `versionId`
- `timingGridId`
- `phraseIds`
- `noteIds`
- `fingeringId`
- `tabRepresentation`
- `staffRepresentation`
- `exportPaths`

### 说明

- `tabRepresentation`
  - TAB 数据表示
- `staffRepresentation`
  - 五线谱数据表示
- `exportPaths`
  - MIDI / MusicXML 路径

### 意义

这是用户最终真正看到的候选谱对象。

---

## 十二、EvaluationReport

### 作用

表示当前候选谱的自动评测结果。

### 建议字段

- `reportId`
- `taskId`
- `versionId`
- `notationId`
- `overall`
- `metrics`
- `diagnosis`
- `adjustments`
- `comparison`

### 说明

- 该对象的具体细节已经在《自动评测报告格式定义 v1》中展开

### 意义

这是“系统知道自己哪里不对”的核心对象。

---

## 十三、AdjustmentPlan

### 作用

表示系统根据评测报告生成的下一轮调整计划。

### 建议字段

- `adjustmentPlanId`
- `taskId`
- `sourceVersionId`
- `targetVersionId`
- `priority`
- `actions`
- `parameterChanges`
- `expectedGoal`

### 说明

- `actions`
  - 例如 `switch_stem`, `increase_min_note_duration`, `rerun_phrase_segmentation`
- `parameterChanges`
  - 参数具体变更
- `expectedGoal`
  - 本轮调整主要想改善什么

### 意义

这是从“评测结果”走向“下一轮行动”的桥梁。

---

## 十四、IterationSnapshot

### 作用

表示某一轮完整快照。

### 建议字段

- `snapshotId`
- `taskId`
- `versionId`
- `inputAssetId`
- `selectedStemId`
- `timingGridId`
- `phraseIds`
- `notationId`
- `reportId`
- `adjustmentPlanId`
- `status`

### 意义

这是“版本管理”的承载对象，用来快速还原一轮完整运行结果。

---

## 十五、对象之间的关系

建议关系如下：

- `InputAsset`
  - 生成多个 `StemCandidate`
- `StemCandidate`
  - 对应一个 `TimingGrid`
- `TimingGrid`
  - 支撑多个 `PhraseSegment`
- `PhraseSegment`
  - 包含多个 `BackboneNote`
- `BackboneNote`
  - 关联多个 `DetailedNote`
- `DetailedNote`
  - 组合成一个 `NotationCandidate`
- `NotationCandidate`
  - 生成一个 `EvaluationReport`
- `EvaluationReport`
  - 生成一个 `AdjustmentPlan`
- `AdjustmentPlan`
  - 驱动下一轮 `IterationSnapshot`

这就形成了完整闭环。

---

## 十六、最小可用实现建议

当前阶段不需要把所有对象一次性全部实现。

建议按下面顺序逐步引入。

### Phase 1

先正式定义并实现：

- `InputAsset`
- `StemCandidate`
- `TimingGrid`
- `DetailedNote`
- `NotationCandidate`
- `EvaluationReport`

### Phase 2

再加入：

- `PhraseSegment`
- `BackboneNote`
- `AdjustmentPlan`

### Phase 3

最后加入：

- `FingeringCandidate`
- `IterationSnapshot`
- 更完整的多候选关系

---

## 十七、与现有工程的关系

从当前项目实现来看，我们已经部分拥有这些对象的雏形：

已有雏形：

- `InputAsset` 的部分信息
- `StemCandidate` 的部分信息
- `TimingGrid` 的基础字段
- `DetailedNote` 的基础字段
- `NotationCandidate` 的导出结果

缺失较明显：

- `PhraseSegment`
- `BackboneNote`
- `FingeringCandidate`
- `AdjustmentPlan`
- `IterationSnapshot`

因此，后续工程重构的重点之一，是把当前零散 JSON 逐步升级成这套正式中间模型。

---

## 十八、这份文档的下一步

这份文档之后，建议继续补：

1. 《自动调参策略映射表 v1》
2. 《最小可用迭代引擎设计 v1》
3. 《中间对象 JSON Schema 草案 v1》

这样就可以从“对象定义”继续走到“系统如何按这些对象运转”。
