# Output

[English](./README.md) | [中文](./README.zh-CN.md)

这个目录用于存放 pipeline 生成出来的结果文件。

## 当前子目录

- `extracted/`：从本地视频或音频中提取出来的 `wav`
- `separated/`：Demucs 分离得到的 stem
- `analysis/`：分析后的 JSON 结果
- `exports/`：基于分析 JSON 导出的 `MIDI` 和 `MusicXML`
- `tasks/`：按任务和版本归档的自动闭环产物

## 开发包 C：版本管理最小实现

现在每次运行 `analyzer/evaluate.py` 后，系统会自动把当前版本归档到：

```txt
output/tasks/<taskId>/
  task.json
  versions/
    <versionId>/
      candidate.json
      evaluation-report.json
      params.json
      iteration-snapshot.json
      export.mid
      export.musicxml
```

其中：
- `task.json`：任务级索引，维护 `latestVersionId`、`bestVersionId`、`stableVersionId` 和版本列表
- `candidate.json`：当前版本对应的候选谱分析结果
- `evaluation-report.json`：当前版本的评测报告
- `params.json`：当前版本的参数快照
- `iteration-snapshot.json`：当前版本的最小状态快照
- `export.mid` / `export.musicxml`：当前版本绑定的导出文件

## 开发包 D：自动调参最小实现

现在每次运行 `analyzer/adjustments.py` 后，系统会自动在当前版本目录中补充：

```txt
output/tasks/<taskId>/versions/<versionId>/
  adjustment-plan.json
  next-params.json
```

其中：
- `adjustment-plan.json`：当前版本针对下一轮的动作计划
- `next-params.json`：当前计划生成的下一轮参数草案

同时 `task.json` 中会补充：
- `adjustmentPlanId`
- `targetVersionId`
- `plannedActions`
- `paths.adjustmentPlan`
- `paths.nextParams`

## 当前已验证文件

- `output/extracted/test1.wav`
- `output/separated/htdemucs/test1/other.wav`
- `output/analysis/test1.analysis.json`
- `output/exports/test1.mid`
- `output/exports/test1.musicxml`
- `output/tasks/task_other/task.json`
- `output/tasks/task_other/versions/ver_001/candidate.json`
- `output/tasks/task_other/versions/ver_001/evaluation-report.json`
- `output/tasks/task_other/versions/ver_001/params.json`
- `output/tasks/task_other/versions/ver_001/iteration-snapshot.json`
- `output/tasks/task_other/versions/ver_001/adjustment-plan.json`
- `output/tasks/task_other/versions/ver_001/next-params.json`

## 这些文件分别代表什么

- 提取 wav：供后续分析使用的中间音频
- 分离 stem：例如 `drums.wav`、`bass.wav`、`other.wav`、`vocals.wav`
- 分析 JSON：供分析器、导出器和前端使用的候选谱结果
- 评测报告：供调参与迭代引擎使用的结构化判断
- 调整计划：供下一轮版本生成参数草案
- 下一轮参数：供后续自动重跑分析时直接使用
- 任务目录：供自动闭环保存多轮版本和做版本比较的基础结构
- 导出文件：基于分析结果生成的可交换谱面文件
