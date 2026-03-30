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

## 开发包 D：自动调参最小实现

现在每次运行 `analyzer/adjustments.py` 后，系统会自动在当前版本目录中补充：

```txt
output/tasks/<taskId>/versions/<versionId>/
  adjustment-plan.json
  next-params.json
```

## 开发包 E：最小迭代引擎

现在每次运行 `analyzer/iterate.py` 后，系统会自动生成下一轮版本，并补充：

```txt
output/analysis/
  <taskId>.<nextVersionId>.analysis.json

output/tasks/<taskId>/
  comparisons/
    <sourceVersionId>__<targetVersionId>.json
  versions/
    <nextVersionId>/
      candidate.json
      evaluation-report.json
      params.json
      iteration-snapshot.json
      export.mid
      export.musicxml
```

同时 `task.json` 会更新：
- `latestVersionId`
- `bestVersionId`
- `stableVersionId`
- `versionIds`
- 新版本条目及其比较路径、父版本信息

## 当前已验证文件

- `output/extracted/test1.wav`
- `output/separated/htdemucs/test1/other.wav`
- `output/analysis/test1.analysis.json`
- `output/analysis/task_other.ver_002.analysis.json`
- `output/exports/test1.mid`
- `output/exports/test1.musicxml`
- `output/tasks/task_other/task.json`
- `output/tasks/task_other/versions/ver_001/candidate.json`
- `output/tasks/task_other/versions/ver_001/evaluation-report.json`
- `output/tasks/task_other/versions/ver_001/params.json`
- `output/tasks/task_other/versions/ver_001/iteration-snapshot.json`
- `output/tasks/task_other/versions/ver_001/adjustment-plan.json`
- `output/tasks/task_other/versions/ver_001/next-params.json`
- `output/tasks/task_other/versions/ver_002/candidate.json`
- `output/tasks/task_other/versions/ver_002/evaluation-report.json`
- `output/tasks/task_other/versions/ver_002/params.json`
- `output/tasks/task_other/comparisons/ver_001__ver_002.json`

## 这些文件分别代表什么

- 提取 wav：供后续分析使用的中间音频
- 分离 stem：例如 `drums.wav`、`bass.wav`、`other.wav`、`vocals.wav`
- 分析 JSON：供分析器、导出器和前端使用的候选谱结果
- 评测报告：供调参与迭代引擎使用的结构化判断
- 调整计划：供下一轮版本生成参数草案
- 下一轮参数：供后续自动重跑分析时直接使用
- 比较文件：记录相邻两轮版本的得分变化与是否提升
- 任务目录：供自动闭环保存多轮版本和做版本比较的基础结构
- 导出文件：基于分析结果生成的可交换谱面文件
