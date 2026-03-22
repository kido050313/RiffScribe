# Analyzer

[English](./README.md) | [中文](./README.zh-CN.md)

这个目录用于放置基于 Python 的音频分析原型。

计划职责：
- 从 `samples/` 或预处理输出目录读取音频
- 从本地视频中提取可供分析的音频
- 为电吉他分析执行音源分离
- 估计时长、BPM、拍点与小节
- 检测基础音高事件
- 将标准化后的分析 JSON 写入 `output/`

Day 1 状态：
- `main.py` 会写出一个占位版 `analysis-result.json`
- Day 2 开始接入真实音频处理

Day 2 用法：
- 使用 `python -m venv .venv` 创建项目级虚拟环境
- 使用 `.\.venv\Scripts\python.exe -m pip install -r analyzer/requirements.txt` 安装依赖
- 将音频片段放入 `samples/`，或通过 `--input` 传入路径
- 运行 `.\.venv\Scripts\python.exe analyzer/main.py`
- 可选：运行 `.\.venv\Scripts\python.exe analyzer/main.py --input samples/your-clip.wav --output output/your-analysis.json`

Day 2.1 目标：
- 增加本地视频输入的预处理支持
- 在分析前先提取 wav 音频
- 对比“原始混音音频”和“分离后 stem”的分析效果

Day 2.1 命令：
- 运行 `.\.venv\Scripts\python.exe analyzer/extract.py`，从 `samples/raw/` 提取 wav 音频
- 可选：运行 `.\.venv\Scripts\python.exe analyzer/extract.py --input samples/raw/your-video.mp4`
- 使用 `.\.venv\Scripts\python.exe -m pip install -r analyzer/requirements.txt` 安装分离依赖
- 运行 `.\.venv\Scripts\python.exe analyzer/separate.py`，从 `output/extracted/` 生成 stem
- 运行 `.\.venv\Scripts\python.exe analyzer/pipeline.py --input samples/raw/your-video.mp4 --fallback-to-extracted`，一条命令完成提音、分离和分析
