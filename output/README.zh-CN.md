# Output

[English](./README.md) | [中文](./README.zh-CN.md)

这个目录用于存放 pipeline 生成出来的结果文件。

## 当前子目录

- `extracted/`：从本地视频或音频中提取出来的 wav
- `separated/`：Demucs 分离得到的 stem
- `analysis/`：分析后的 JSON 结果

## 当前已验证文件

- `output/extracted/test1.wav`
- `output/separated/htdemucs/test1/other.wav`
- `output/analysis/test1.analysis.json`

## 这些文件分别代表什么

- 提取 wav：供后续分析使用的中间音频
- 分离 stem：例如 `drums.wav`、`bass.wav`、`other.wav`、`vocals.wav`
- 分析 JSON：供前端页面使用的 BPM、拍点、小节和音符事件

## 后续可能新增的输出

后面的版本可能会继续增加：
- `*.musicxml`
- `*.mid`
