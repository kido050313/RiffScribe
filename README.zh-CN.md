# 电吉他转谱 PoC

[English](./README.md) | [中文](./README.zh-CN.md)

这是一个以“节奏优先”为核心的电吉他转谱原型项目。

## 这是什么项目

这个项目的目标，是帮助吉他手把一段较短的演奏视频或音频，更快地变成一份可继续修改的转谱初稿，而不是完全靠手动扒谱。

当前主流程：
1. 输入本地视频或混合音频
2. 提取音频
3. 做 4-stem 分离
4. 优先使用 `other.wav` 作为电吉他候选 stem
5. 分析 BPM、拍点、小节和音符事件
6. 在网页时间轴中查看和修正结果

## 当前做到什么程度

已经可用的能力：
- 本地视频提音为 wav
- 基于 Demucs 的 4-stem 分离
- 输出 BPM、拍点、小节、音符事件 JSON
- 前端页面支持：
  - 播放分离后的音频
  - 查看拍点、小节和音符时间轴
  - 高亮当前播放命中的音符
  - 设置循环区间反复播放
  - 本地修改音符字段
  - 在时间轴上左右拖动音符块

目前还属于原型阶段的部分：
- 音高和节奏识别精度还比较粗
- 还没有正式导出乐谱
- 还没有持久化保存
- 还没有完整的专业编辑能力

## 目录说明

- `analyzer/`：Python 分析脚本，负责提音、分离、分析
- `web/`：Next.js 前端原型
- `samples/`：样本使用说明
- `samples/raw/`：原始视频或混合音频输入
- `output/`：提取音频、分离结果、分析 JSON
- `docs/`：规划文档和阶段说明

## 快速开始

### 1. 创建 Python 环境

创建项目虚拟环境：

```powershell
python -m venv .venv
```

安装 Python 依赖：

```powershell
.\.venv\Scripts\python.exe -m pip install -r analyzer/requirements.txt
```

### 2. 运行分析流水线

先把本地素材放进 `samples/raw/`，例如 `samples/raw/test1.mp4`。

运行：

```powershell
.\.venv\Scripts\python.exe analyzer/pipeline.py --input samples/raw/test1.mp4 --fallback-to-extracted
```

这一步会生成：
- `output/extracted/` 中的提取音频
- `output/separated/` 中的分离 stem
- `output/analysis/` 中的分析 JSON

### 3. 启动前端页面

进入前端目录：

```powershell
cd web
```

安装前端依赖：

```powershell
pnpm install
```

启动开发服务器：

```powershell
pnpm dev
```

然后打开终端中显示的本地地址。

## 已验证示例

仓库当前已经用下面这组数据验证通过：
- 输入：`samples/raw/test1.mp4`
- 提取音频：`output/extracted/test1.wav`
- 优先使用的 stem：`output/separated/htdemucs/test1/other.wav`
- 分析结果：`output/analysis/test1.analysis.json`

## 现阶段建议怎么用

这个项目现在最适合拿来做：
- 节奏检查
- 短句初稿生成
- solo 练习辅助

它还不是一个最终版打谱软件，但已经可以作为“减少手动扒谱时间”的原型工具来使用。
