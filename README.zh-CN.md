# 电吉他自动转谱 PoC

[English](./README.md) | [中文](./README.zh-CN.md)

这是一个面向中文用户的电吉他自动转谱原型项目，目标是把一段本地视频或混合音频，尽快转换成一份可继续修正和导出的谱面草稿。

当前项目已经具备一条最小可跑通链路：
1. 输入本地视频或混合音频
2. 提取音频
3. 通过 Demucs 做 4-stem 分离
4. 默认优先选择 `other.wav` 作为电吉他候选轨道
5. 分析 BPM、拍点、小节和音符事件
6. 在网页工作台中播放、查看、循环和导出
7. 导出 `MIDI` 和 `MusicXML`

## 当前阶段

项目现在处于从 PoC 向“自动评测闭环”过渡的阶段。

已完成：
- 视频提音
- 4-stem 分离
- 分析 JSON 生成
- `MIDI` 导出
- `MusicXML` 导出
- 网页时间轴工作台
- 网页五线谱预览入口
- 开发包 A：统一数据模型基础落地

正在推进：
- 自动评测
- 版本管理
- 自动调参与多轮迭代

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

## 目录说明

- `analyzer/`：Python 分析脚本，负责提音、分离、分析、导出
- `web/`：Next.js 前端原型
- `samples/`：样本说明
- `samples/raw/`：原始视频或混合音频输入
- `output/`：提取音频、分离结果、分析 JSON、导出文件
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
- Solo 练习辅助
- 生成一份可继续编辑的初稿
- 比较不同 stem 对分析的影响

它还不是最终版自动出谱产品，但已经是一个可继续扩展的研发底座。

## 已验证样例

- 输入：`samples/raw/test1.mp4`
- 提取音频：`output/extracted/test1.wav`
- 候选 stem：`output/separated/htdemucs/test1/other.wav`
- 分析结果：`output/analysis/test1.analysis.json`
- MIDI：`output/exports/test1.mid`
- MusicXML：`output/exports/test1.musicxml`
