# Analyzer

[English](./README.md) | [中文](./README.zh-CN.md)

这个目录放的是 Python 侧的音频处理流水线。

## 主要职责

- 从本地视频或混合音频中提取 wav
- 运行 Demucs 分离
- 把音频分析成 BPM、拍点、小节和音符事件
- 将标准化 JSON 写入 `output/analysis/`

## 主要脚本

- `extract.py`：把本地媒体转换为可分析的 wav
- `separate.py`：通过 Demucs Python API 做分离，并用 `soundfile` 保存 stem
- `main.py`：把单个音频文件分析成 JSON 音符事件
- `pipeline.py`：一条命令串起提音、分离和分析
- `export.py`：把分析 JSON 导出成 MIDI 和 MusicXML

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

导出 MIDI 和 MusicXML：

```powershell
.\.venv\Scripts\python.exe analyzer/export.py --input output/analysis/test1.analysis.json
```

## 当前的重要约定

- 默认采用完整 4-stem 分离，不再优先使用 `--two-stems vocals`
- `other.wav` 被视为第一优先级的电吉他候选 stem
- 如果分离效果不可用，pipeline 可以回退到提取出的混合音频继续分析

## 正常输出结果

运行 pipeline 后，你应该能看到：
- `output/extracted/` 中的提取 wav
- `output/separated/` 中的 stem
- `output/analysis/` 中的分析 JSON
- `output/exports/` 中的 MIDI 和 MusicXML

## 已验证示例

- 输入：`samples/raw/test1.mp4`
- 提取音频：`output/extracted/test1.wav`
- 优先使用的 stem：`output/separated/htdemucs/test1/other.wav`
- 分析输出：`output/analysis/test1.analysis.json`
- MIDI 导出：`output/exports/test1.mid`
- MusicXML 导出：`output/exports/test1.musicxml`
