# Analyzer

[English](./README.md) | [中文](./README.zh-CN.md)

这个目录放的是 Python 侧的音频处理流水线。

## 主要职责

- 从本地视频或混合音频中提取 `wav`
- 运行 Demucs 分离
- 把音频分析成 BPM、拍点、小节和音符事件
- 生成最小评测报告
- 归档任务和版本结果
- 根据评测报告生成自动调整计划和下一轮参数草案
- 运行最小迭代引擎，自动生成下一版本并比较结果
- 导出 `MIDI` 和 `MusicXML`

## 当前脚本

- `extract.py`：把本地媒体转换为可分析的 `wav`
- `separate.py`：通过 Demucs Python API 做分离，并用 `soundfile` 保存 stem
- `main.py`：把单个音频文件分析成统一结构 JSON，支持参数化重跑
- `evaluate.py`：根据分析 JSON 生成最小评测报告，并触发版本归档
- `adjustments.py`：根据评测报告和当前参数生成调整计划与下一轮参数草案
- `iterate.py`：最小迭代引擎，自动从当前版本生成下一版本并输出比较结果
- `task_store.py`：管理 `task.json`、版本目录和各类归档文件
- `pipeline.py`：一条命令串起提音、分离和分析
- `export.py`：把分析 JSON 导出成 `MIDI` 和 `MusicXML`
- `schemas.py`：统一数据模型的数据类定义

## 当前输出结构

`main.py` 现在输出的是统一数据模型，并保留旧字段兼容现有前端和导出流程。

新增结构：
- `schemaVersion`
- `taskId`
- `versionId`
- `inputAsset`
- `stemCandidate`
- `timingGrid`
- `detailedNotes`
- `notationCandidate`

兼容字段：
- `sourceName`
- `durationSec`
- `bpm`
- `timeSignature`
- `beats`
- `measures`
- `notes`

`evaluate.py` 当前会生成最小评测报告，包含：
- `overall`
- `metrics.rhythm`
- `metrics.pitch`
- `diagnosis.primaryIssues`
- `adjustments.recommendedActions`

`adjustments.py` 当前会生成最小调整计划，包含：
- `actions`
- `parameterChanges`
- `expectedGoal`
- `targetVersionId`
- `triggerIssues`

## 开发包 C：版本管理最小实现

现在每次运行 `evaluate.py` 后，会自动完成这些事情：
- 写入 `evaluation-report.json`
- 复制 `candidate.json` 到当前版本目录
- 生成 `params.json`
- 生成 `iteration-snapshot.json`
- 如果已存在导出文件，则复制到当前版本目录
- 更新 `output/tasks/<taskId>/task.json`

## 开发包 D：自动调参最小实现

现在每次运行 `adjustments.py` 后，会自动完成这些事情：
- 读取 `evaluation-report.json`
- 读取当前版本 `params.json`
- 根据问题和优先级映射选择 1 到 2 个动作
- 生成 `adjustment-plan.json`
- 生成 `next-params.json`
- 把计划和目标版本写回 `task.json`

当前已实现动作：
- `switch_input_stem`
- `retune_beat_tracking`
- `increase_min_note_duration`
- `limit_pitch_range`
- `fix_measure_alignment`

## 开发包 E：最小迭代引擎

现在每次运行 `iterate.py` 后，会自动完成这些事情：
- 读取 `task.json` 的 `latestVersionId`
- 确保当前版本已有 `adjustment-plan.json` 和 `next-params.json`
- 使用 `next-params.json` 重跑分析器
- 生成下一版本 `candidate.json`
- 生成下一版本 `evaluation-report.json`
- 生成下一版本 `params.json`
- 导出下一版本 `export.mid` 和 `export.musicxml`
- 生成版本比较文件
- 更新 `task.json` 的 `latestVersionId`、`bestVersionId` 和版本索引

## 推荐使用方式

先创建并使用项目虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r analyzer/requirements.txt
```

运行完整流水线：

```powershell
.\.venv\Scripts\python.exe analyzer/pipeline.py --input samples/raw/test1.mp4 --fallback-to-extracted
```

单独运行分析：

```powershell
.\.venv\Scripts\python.exe analyzer/main.py --input output/separated/htdemucs/test1/other.wav --output output/analysis/test1.analysis.json
```

生成评测报告并自动归档版本：

```powershell
.\.venv\Scripts\python.exe analyzer/evaluate.py --input output/analysis/test1.analysis.json
```

生成调整计划和下一轮参数草案：

```powershell
.\.venv\Scripts\python.exe analyzer/adjustments.py --report output/tasks/task_other/versions/ver_001/evaluation-report.json --params output/tasks/task_other/versions/ver_001/params.json --task-index output/tasks/task_other/task.json
```

运行一轮最小迭代：

```powershell
.\.venv\Scripts\python.exe analyzer/iterate.py --task-index output/tasks/task_other/task.json --max-rounds 1
```

导出 MIDI 和 MusicXML：

```powershell
.\.venv\Scripts\python.exe analyzer/export.py --input output/analysis/test1.analysis.json
```

## 当前的重要约定

- 默认采用完整 4-stem 分离，不优先使用 `--two-stems vocals`
- `other.wav` 被视为第一优先级的电吉他候选 stem
- 如果分离效果不可用，pipeline 可以回退到提取出的混合音频继续分析
- 当前分析器已经接入统一数据模型，但节奏和音高质量仍然属于 PoC 阶段
- 当前评测器属于开发包 B 的最小实现，主要用于为后续调参与迭代引擎提供结构化输入
- 当前版本管理器属于开发包 C 的最小实现，主要用于为后续多轮迭代保留任务级和版本级产物
- 当前调整计划器属于开发包 D 的最小实现，主要用于为下一轮版本生成参数草案
- 当前迭代引擎属于开发包 E 的最小实现，先支持单任务、线性迭代、少量动作自动重跑

## 正常输出结果

运行 pipeline 后，你应该能看到：
- `output/extracted/` 中的提取 wav
- `output/separated/` 中的 stem
- `output/analysis/` 中的分析 JSON
- `output/exports/` 中的 MIDI 和 MusicXML

运行 `evaluate.py` 后，你应该能看到：
- `output/tasks/<taskId>/task.json`
- `output/tasks/<taskId>/versions/<versionId>/candidate.json`
- `output/tasks/<taskId>/versions/<versionId>/evaluation-report.json`
- `output/tasks/<taskId>/versions/<versionId>/params.json`
- `output/tasks/<taskId>/versions/<versionId>/iteration-snapshot.json`

运行 `adjustments.py` 后，你应该能看到：
- `output/tasks/<taskId>/versions/<versionId>/adjustment-plan.json`
- `output/tasks/<taskId>/versions/<versionId>/next-params.json`

运行 `iterate.py` 后，你应该能看到：
- `output/analysis/<taskId>.<nextVersionId>.analysis.json`
- `output/tasks/<taskId>/versions/<nextVersionId>/candidate.json`
- `output/tasks/<taskId>/versions/<nextVersionId>/evaluation-report.json`
- `output/tasks/<taskId>/versions/<nextVersionId>/params.json`
- `output/tasks/<taskId>/comparisons/<sourceVersionId>__<targetVersionId>.json`

## 已验证示例

- 输入：`samples/raw/test1.mp4`
- 提取音频：`output/extracted/test1.wav`
- 优先使用的 stem：`output/separated/htdemucs/test1/other.wav`
- 分析输出：`output/analysis/test1.analysis.json`
- 评测报告：`output/tasks/task_other/versions/ver_001/evaluation-report.json`
- 调整计划：`output/tasks/task_other/versions/ver_001/adjustment-plan.json`
- 下一轮参数：`output/tasks/task_other/versions/ver_001/next-params.json`
- 下一轮分析：`output/analysis/task_other.ver_002.analysis.json`
- 下一轮比较：`output/tasks/task_other/comparisons/ver_001__ver_002.json`
- 任务索引：`output/tasks/task_other/task.json`
- MIDI 导出：`output/exports/test1.mid`
- MusicXML 导出：`output/exports/test1.musicxml`
