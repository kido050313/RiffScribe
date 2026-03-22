# 电吉他转谱 PoC

[English](./README.md) | [中文](./README.zh-CN.md)

这是一个面向电吉他练习场景的转谱原型项目，目标是把一段本地视频或混合音频，尽快变成一份可继续修正的节奏与音符初稿，帮助用户减少手工扒谱时间。

## 这个项目在做什么

当前主流程是：

1. 输入本地视频或混合音频
2. 提取音频
3. 用 Demucs 做 4-stem 分离
4. 默认优先选择 `other.wav` 作为电吉他候选轨道
5. 分析 BPM、拍点、小节和音符事件
6. 在前端时间轴里播放、查看、循环、微调
7. 导出为 `MIDI` 或 `MusicXML`

## 当前已经完成的能力

- 本地视频提音为 `wav`
- 基于 Demucs 的 4-stem 分离
- 生成分析结果 JSON
- 导出 `MIDI`
- 导出 `MusicXML`
- 前端工作台支持：
  - 播放分离后的候选音频
  - 查看小节、拍点、音符时间轴
  - 播放时高亮当前命中的音符
  - 设置循环区间
  - 本地修改音符字段
  - 在时间轴上左右拖动音符块
  - 保存到浏览器
  - 导入/导出工程文件

## 目录说明

- `analyzer/`：Python 分析脚本，负责提音、分离、分析、导出
- `web/`：Next.js 前端原型
- `samples/`：样本说明
- `samples/raw/`：原始视频或混合音频输入
- `output/`：提取音频、分离结果、分析 JSON、导出文件
- `docs/`：阶段性方案和记录

## 快速开始

### 1. 创建 Python 环境

```powershell
python -m venv .venv
```

```powershell
.\.venv\Scripts\python.exe -m pip install -r analyzer/requirements.txt
```

### 2. 跑完整分析流水线

先把素材放进 `samples/raw/`，例如 `samples/raw/test1.mp4`。

```powershell
.\.venv\Scripts\python.exe analyzer/pipeline.py --input samples/raw/test1.mp4 --fallback-to-extracted
```

执行后会产出：

- `output/extracted/`：提取出的音频
- `output/separated/`：Demucs 分离结果
- `output/analysis/`：分析 JSON

### 3. 导出 MIDI 和 MusicXML

```powershell
.\.venv\Scripts\python.exe analyzer/export.py --input output/analysis/test1.analysis.json
```

执行后会产出：

- `output/exports/test1.mid`
- `output/exports/test1.musicxml`

### 4. 启动前端

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
- solo 练习辅助
- 生成一份可继续修的初稿

它还不是完整的专业打谱软件，但已经能作为“减少手工扒谱时间”的原型工具使用。

## 已验证样例

- 输入：`samples/raw/test1.mp4`
- 提取音频：`output/extracted/test1.wav`
- 候选 stem：`output/separated/htdemucs/test1/other.wav`
- 分析结果：`output/analysis/test1.analysis.json`
- MIDI：`output/exports/test1.mid`
- MusicXML：`output/exports/test1.musicxml`
