# Web

[English](./README.md) | [中文](./README.zh-CN.md)

这个目录放的是基于 Next.js 的前端原型。

## 当前页面能做什么

- 读取最新分析 JSON
- 播放分离后的电吉他候选音频
- 展示小节、拍点、音符事件和播放指针
- 播放时自动高亮当前命中的音符
- 支持循环播放
- 支持本地修改音符字段
- 支持在时间轴上左右拖动音符块

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
- `../output/analysis/test1.analysis.json` 中的分析结果
- `/api/audio` 路由中的音频
- `/api/audio` 实际提供的是 `../output/separated/htdemucs/test1/other.wav`

## 使用提醒

- 同一时间只建议启动一个 `pnpm dev`
- 如果 Windows 下出现 `.next/trace` 被锁住，先关闭旧的 Node 进程，再重新启动开发服务器

## 当前产品定位

这个页面现在更像“修谱工作台原型”，还不是最终版成品 UI。
