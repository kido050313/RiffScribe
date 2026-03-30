# Web

[English](./README.md) | [中文](./README.zh-CN.md)

这个目录放的是基于 Next.js 的前端原型页面。

## 当前页面能做什么

- 读取最新分析 JSON
- 播放分离后的电吉他候选音频
- 展示小节、拍点、音符事件和播放指针
- 播放时自动高亮当前命中的音符
- 设置循环播放区间
- 本地修改音符字段
- 在时间轴上拖动音符块
- 打开五线谱预览页
- 导出 `MIDI`
- 导出 `MusicXML`
- 保存到浏览器
- 导入/导出工程文件

## 当前数据模型

前端类型已经切到统一数据模型，定义位于：
- `web/types/domain.ts`
- `web/types/analysis.ts`

当前页面仍然兼容旧字段读取，因此可以继续使用：
- `sourceName`
- `durationSec`
- `bpm`
- `beats`
- `measures`
- `notes`

同时也已经能识别新结构：
- `inputAsset`
- `stemCandidate`
- `timingGrid`
- `detailedNotes`
- `notationCandidate`

## 如何启动

安装依赖：

```powershell
pnpm install
```

启动开发环境：

```powershell
pnpm dev
```

执行类型检查：

```powershell
pnpm typecheck
```

## 当前数据来源

这个页面当前读取的是：
- `../output/analysis/test1.analysis.json`
- `/api/audio` 路由提供的音频
- `/api/export` 路由提供的导出能力
- `/api/score` 路由提供的 MusicXML 预览数据

其中 `/api/audio` 当前默认服务：
- `../output/separated/htdemucs/test1/other.wav`

## 使用提醒

- 同一时间建议只启动一个 `pnpm dev`
- 如果 Windows 下出现 `.next/trace` 被锁住，先关闭旧的 Node 进程，再重新启动开发服务器
- 当前页面更偏研发工作台，不是最终用户版 UI

## 当前定位

这个页面现在更像“修谱工作台原型”，重点是验证：
- 音频播放与时间轴联动
- 节奏与音符草稿查看
- 局部循环练习
- 导出和本地保存闭环
- 与统一数据模型的前端兼容
