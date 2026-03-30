# Analyzer

[English](./README.md) | [中文](./README.zh-CN.md)

这个目录放的是 Python 侧的音频处理流水线。

## 主要职责

- 从本地视频或混合音频中提取 `wav`
- 运行 Demucs 分离
- 把音频分析成 BPM、拍点、小节和音符事件
- 生成最小评测报告
- 将标准化 JSON 写入 `output/analysis/` 和 `output/tasks/`
- 导出 `MIDI` 和 `MusicXML`

## 当前脚本

- `extract.py`：把本地媒体转换为可分析的 `wav`
- `separate.py`：通过 Demucs Python API 做分离，并用 `soundfile` 保存 stem
- `main.py`：把单个音频文件分析成统一结构 JSON
- `evaluate.py`：根据分析 JSON 生成最小评测报告
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

生成评测报告：

```powershell
.\.venv\Scripts\python.exe analyzer/evaluate.py --input output/analysis/test1.analysis.json
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

## 正常输出结果

运行 pipeline 后，你应该能看到：
- `output/extracted/` 中的提取 wav
- `output/separated/` 中的 stem
- `output/analysis/` 中的分析 JSON
- `output/exports/` 中的 MIDI 和 MusicXML

运行 `evaluate.py` 后，你应该能看到：
- `output/tasks/<taskId>/versions/<versionId>/evaluation-report.json`

## 已验证示例

- 输入：`samples/raw/test1.mp4`
- 提取音频：`output/extracted/test1.wav`
- 优先使用的 stem：`output/separated/htdemucs/test1/other.wav`
- 分析输出：`output/analysis/test1.analysis.json`
- 评测报告：`output/tasks/task_other/versions/ver_001/evaluation-report.json`
- MIDI 导出：`output/exports/test1.mid`
- MusicXML 导出：`output/exports/test1.musicxml`
