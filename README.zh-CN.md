# Guitar 转谱 PoC

[English](./README.md) | [中文](./README.zh-CN.md)

这是一个面向电吉他的半自动转谱产品早期原型仓库。

当前目标：
- 接收一段 `30-60 秒` 的本地视频或混合音频片段
- 在分析前先提取并分离出更适合电吉他识别的音频
- 分析节奏与基础音高候选
- 生成可编辑的 `TAB + 五线谱` 初稿

项目结构：
- `web/`：前端原型文件与共享 TypeScript 类型
- `analyzer/`：Python 音频分析入口与依赖
- `samples/`：本地测试音频样本
- `output/`：生成的 JSON 与导出产物
- `docs/`：产品与技术说明

当前已完成范围：
- 创建项目目录
- 定义共享的 `AnalysisResult` 数据结构
- 添加供前端开发使用的 mock 分析数据
- 准备 Python 分析入口
- 增加 Day 2 音频分析脚本，用于输出 BPM、拍点和音符候选

当前下一步：
- 增加 Day 2.1 预处理层，用于视频提音和音源分离
- 将提取音频或分离后的 stem 接入 `analyzer/main.py`
