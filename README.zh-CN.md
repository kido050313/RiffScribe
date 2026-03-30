# 电吉他自动转谱 PoC

[English](./README.md) | [中文](./README.zh-CN.md)

这是一个面向中文用户的电吉他自动转谱原型项目，目标是把一段本地视频或混合音频，尽快转换成一份可继续修正和导出的谱面草稿。

当前项目已经具备一条最小可跑通链路：
1. 输入本地视频或混合音频
2. 提取音频
3. 通过 Demucs 做 4-stem 分离
4. 默认优先选择 `other.wav` 作为电吉他候选轨道
5. 分析 BPM、拍点、小节和音符事件
6. 自动生成最小评测报告
7. 自动归档任务和版本产物
8. 自动生成调整计划和下一轮参数草案
9. 在网页工作台中播放、查看、循环和导出
10. 导出 `MIDI` 和 `MusicXML`

## 当前阶段

项目现在处于从 PoC 向“自动评测闭环”过渡的阶段。

已完成：
- 视频提音
- 4-stem 分离
- 分析 JSON 生成
- 开发包 A：统一数据模型基础落地
- 开发包 B：最小评测实现
- 开发包 C：版本管理最小实现
- 开发包 D：自动调参最小实现
- `MIDI` 导出
- `MusicXML` 导出
- 网页时间轴工作台
- 网页五线谱预览入口

正在推进：
- 多轮迭代引擎

## 统一数据模型

当前分析输出已升级为统一数据模型，并保留旧字段兼容现有前端与导出流程。

新增的核心对象包括：
- `inputAsset`
- `stemCandidate`
- `timingGrid`
- `detailedNotes`
- `notationCandidate`

兼容保留的旧字段包括：
- `sourceName`
- `durationSec`
- `bpm`
- `timeSignature`
- `beats`
- `measures`
- `notes`

相关代码：
- `analyzer/schemas.py`
- `analyzer/main.py`
- `web/types/domain.ts`
- `web/types/analysis.ts`

## 最小评测报告

当前已新增最小评测能力，用于给自动闭环提供第一版结构化判断。

当前报告包含：
- `overall`
- `metrics.rhythm`
- `metrics.pitch`
- `diagnosis.primaryIssues`
- `adjustments.recommendedActions`

相关代码：
- `analyzer/evaluate.py`
- `output/tasks/<taskId>/versions/<versionId>/evaluation-report.json`

## 最小版本管理

当前已新增任务级和版本级归档能力。

每次运行 `evaluate.py` 后，系统会自动生成：
- `output/tasks/<taskId>/task.json`
- `output/tasks/<taskId>/versions/<versionId>/candidate.json`
- `output/tasks/<taskId>/versions/<versionId>/evaluation-report.json`
- `output/tasks/<taskId>/versions/<versionId>/params.json`
- `output/tasks/<taskId>/versions/<versionId>/iteration-snapshot.json`
- 如果导出文件存在，则同步归档 `export.mid` 和 `export.musicxml`

相关代码：
- `analyzer/task_store.py`

## 最小自动调参

当前已新增调整计划生成能力。

每次运行 `adjustments.py` 后，系统会自动生成：
- `output/tasks/<taskId>/versions/<versionId>/adjustment-plan.json`
- `output/tasks/<taskId>/versions/<versionId>/next-params.json`

当前已实现动作：
- `switch_input_stem`
- `retune_beat_tracking`
- `increase_min_note_duration`
- `limit_pitch_range`
- `fix_measure_alignment`

相关代码：
- `analyzer/adjustments.py`

## 目录说明

- `analyzer/`：Python 分析脚本，负责提音、分离、分析、评测、归档、调参、导出
- `web/`：Next.js 前端原型
- `samples/`：样本说明
- `samples/raw/`：原始视频或混合音频输入
- `output/`：提取音频、分离结果、分析 JSON、评测报告、任务归档、调整计划、导出文件
- `docs/`：产品、方法论和开发拆解文档

## 快速开始

### 1. 创建 Python 环境

```powershell
python -m venv .venv
```

```powershell
.\.venv\Scripts\python.exe -m pip install -r analyzer/requirements.txt
```

### 2. 运行完整分析流水线

先把素材放进 `samples/raw/`，例如 `samples/raw/test1.mp4`。

```powershell
.\.venv\Scripts\python.exe analyzer/pipeline.py --input samples/raw/test1.mp4 --fallback-to-extracted
```

执行后会产出：
- `output/extracted/`：提取出的音频
- `output/separated/`：Demucs 分离结果
- `output/analysis/`：分析 JSON

### 3. 生成评测报告并自动归档版本

```powershell
.\.venv\Scripts\python.exe analyzer/evaluate.py --input output/analysis/test1.analysis.json
```

执行后会产出：
- `output/tasks/task_other/task.json`
- `output/tasks/task_other/versions/ver_001/candidate.json`
- `output/tasks/task_other/versions/ver_001/evaluation-report.json`
- `output/tasks/task_other/versions/ver_001/params.json`
- `output/tasks/task_other/versions/ver_001/iteration-snapshot.json`

### 4. 生成调整计划和下一轮参数草案

```powershell
.\.venv\Scripts\python.exe analyzer/adjustments.py --report output/tasks/task_other/versions/ver_001/evaluation-report.json --params output/tasks/task_other/versions/ver_001/params.json --task-index output/tasks/task_other/task.json
```

执行后会产出：
- `output/tasks/task_other/versions/ver_001/adjustment-plan.json`
- `output/tasks/task_other/versions/ver_001/next-params.json`

### 5. 导出 MIDI 和 MusicXML

```powershell
.\.venv\Scripts\python.exe analyzer/export.py --input output/analysis/test1.analysis.json
```

执行后会产出：
- `output/exports/test1.mid`
- `output/exports/test1.musicxml`

### 6. 启动前端

```powershell
cd web
pnpm install
pnpm dev
```

需要检查类型时运行：

```powershell
pnpm typecheck
```

## 当前推荐用法

这个项目现在最适合用来做：
- 短句节奏检查
- Solo 练习辅助
- 生成一份可继续编辑的初稿
- 比较不同 stem 对分析的影响
- 为后续自动调参与迭代引擎提供结构化评测输入
- 为后续多轮迭代保留完整版本产物
- 为下一轮自动重跑提供参数草案

它还不是最终版自动出谱产品，但已经是一个可继续扩展的研发底座。

## 已验证样例

- 输入：`samples/raw/test1.mp4`
- 提取音频：`output/extracted/test1.wav`
- 候选 stem：`output/separated/htdemucs/test1/other.wav`
- 分析结果：`output/analysis/test1.analysis.json`
- 评测报告：`output/tasks/task_other/versions/ver_001/evaluation-report.json`
- 调整计划：`output/tasks/task_other/versions/ver_001/adjustment-plan.json`
- 下一轮参数：`output/tasks/task_other/versions/ver_001/next-params.json`
- 任务索引：`output/tasks/task_other/task.json`
- MIDI：`output/exports/test1.mid`
- MusicXML：`output/exports/test1.musicxml`
