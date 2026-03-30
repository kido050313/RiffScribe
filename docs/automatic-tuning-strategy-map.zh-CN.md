# 自动调参策略映射表 v1

## 文档目的

这份文档用于定义自动转谱系统里的“问题 -> 调整动作”映射关系。

目标是回答一个核心问题：

- 当自动评测发现当前候选谱存在问题时，系统下一步应该调什么？

这份文档的作用，是把自动评测报告真正接到自动迭代链路上。

没有这份映射表，系统即使知道“哪里不对”，也仍然不会知道“下一步该做什么”。

---

## 一、为什么需要调参策略映射表

自动评测系统会输出：

- 节奏得分
- 音高轮廓得分
- 乐句边界问题
- 高频异常值
- note 过碎
- 可演奏性差

但这些诊断结果本身还不是动作。

系统必须进一步回答：

- 是先修节奏还是先修音高？
- 是先换 stem，还是先调 note 过滤？
- 是先重切乐句，还是先合并碎音？
- 本轮调整应该只改一个变量，还是改一组变量？

因此，自动调参策略映射表本质上是：

- 诊断层到执行层的桥梁

---

## 二、设计原则

### 1. 优先修结构，不优先修细节

当多个问题同时存在时，优先级建议是：

1. 输入轨道问题
2. 节奏框架问题
3. 乐句与骨架问题
4. 细节音问题
5. 音高细节问题
6. 指法与可演奏性问题

理由是：

- 结构层错了，细节层再准也没用

### 2. 每轮尽量少改

一轮调整不建议同时改太多维度。

建议优先：

- 每轮只针对一个主问题
- 最多改一组强相关参数

否则会导致：

- 不知道到底哪个改动带来了提升或退化

### 3. 先用规则映射，再考虑学习型策略

当前阶段最稳妥的方案是：

- 明确写规则映射表

后续如果数据积累够，再考虑：

- 用历史迭代结果学习更优调参路径

### 4. 所有动作都应可追溯

系统做出的每一个自动调整都应记录：

- 触发原因
- 采用动作
- 参数变化
- 预期改善目标

---

## 三、问题分类总览

建议先把问题分成以下几大类：

1. 输入轨道问题
2. 节奏框架问题
3. 乐句边界问题
4. 骨架音问题
5. 细节碎音问题
6. 音高异常问题
7. 指法与可演奏性问题
8. 收敛停机问题

每一类问题都对应不同的调整动作。

---

## 四、输入轨道问题映射

### 问题类型 A1：当前 stem 质量低

典型表现：

- 节奏评分和音高评分都偏低
- note 数量异常
- pitch outlier 很高
- 原音频和当前候选谱整体差距大

建议动作：

- `switch_input_stem`
- `rerun_full_analysis`

参数建议：

- 从 `other` 切到 `extracted`
- 或从 `other` 切到 `vocals` 候选

适用优先级：

- 最高优先级

说明：

- 输入 stem 明显不行时，后面细修意义很小

### 问题类型 A2：多个 stem 评分接近

典型表现：

- `other` 和 `extracted` 分数差很小
- 当前结果不稳定

建议动作：

- `branch_with_alternative_stem`
- `compare_parallel_candidates`

说明：

- 不一定强行只选一条，可以分支并行试两条

---

## 五、节奏框架问题映射

### 问题类型 B1：beat alignment 低

典型表现：

- onset 偏差大
- 拍点与实际起音明显不对齐

建议动作：

- `retune_beat_tracking`
- `adjust_tempo_estimation`

参数建议：

- 改 beat tracking 权重
- 改 onset 平滑参数
- 重新估 BPM

优先级：

- 很高

### 问题类型 B2：downbeat 错位

典型表现：

- 小节边界整体平移
- 强拍落点长期不稳

建议动作：

- `rerun_downbeat_detection`
- `shift_measure_alignment`

参数建议：

- 调整首小节偏移候选
- 重新尝试小节起点对齐

### 问题类型 B3：拍号假设不合理

典型表现：

- measure boundary score 持续偏低
- 某些句子总是在错误小节位置切开

建议动作：

- `try_alternative_time_signature`

参数建议：

- 在 `4/4` 之外尝试 `12/8`、`6/8`、shuffle 风格解释

说明：

- 对布鲁斯和带 swing 的素材特别重要

---

## 六、乐句边界问题映射

### 问题类型 C1：phrase boundary 不稳定

典型表现：

- pause alignment 差
- 乐句开头和结尾不自然
- 句尾总落不到位

建议动作：

- `rerun_phrase_segmentation`
- `increase_pause_weight`

参数建议：

- 提高停顿检测阈值
- 提高句尾长音权重

### 问题类型 C2：乐句密度分布异常

典型表现：

- 某些句子音符异常密集
- 某些句子异常空

建议动作：

- `rebalance_phrase_density`
- `merge_dense_local_notes`

说明：

- 这类问题通常不是单音错误，而是句法层问题

---

## 七、骨架音问题映射

### 问题类型 D1：强拍音命中差

典型表现：

- backbone score 偏低
- 强拍上的主音经常不对

建议动作：

- `increase_strong_beat_weight`
- `reselect_backbone_notes`

参数建议：

- 提高强拍位置的主音候选权重
- 降低短音在骨架层中的影响

### 问题类型 D2：句尾音不稳

典型表现：

- phrase ending note score 低
- 听起来句尾悬空

建议动作：

- `increase_phrase_ending_weight`
- `prefer_long_ending_notes`

说明：

- 句尾音是“像不像人工扒谱结果”的关键之一

---

## 八、细节碎音问题映射

### 问题类型 E1：note fragmentation 高

典型表现：

- note 数量过多
- 短音比例过高
- 谱面看起来很碎

建议动作：

- `increase_min_note_duration`
- `merge_short_notes`
- `suppress_noise_notes`

参数建议：

- 提高最短音符时长阈值
- 合并时间上相邻且 pitch 接近的短 note

优先级：

- 很高

### 问题类型 E2：装饰音过多

典型表现：

- 细节音比骨架音多很多
- 谱子非常拥挤

建议动作：

- `increase_ornament_filter_strength`
- `demote_fast_notes_to_ornaments`

说明：

- 有些 note 不该直接写进主谱，而应降级为装饰候选

---

## 九、音高异常问题映射

### 问题类型 F1：高频异常值过多

典型表现：

- 出现明显不合理高音
- contour 失真

建议动作：

- `limit_pitch_range`
- `increase_pitch_smoothing`
- `recompute_pitch_candidates`

参数建议：

- 降低上限音高
- 提高 pitch 平滑窗口

### 问题类型 F2：旋律轮廓偏差大

典型表现：

- contour similarity 低
- 主旋律走势不像原音频

建议动作：

- `prefer_contour_consistent_candidate`
- `reweight_stable_pitch_segments`

说明：

- 这里不一定逐音修，而是优先修“轮廓”

### 问题类型 F3：跳进异常过多

典型表现：

- excessive leap penalty 高
- 旋律中出现太多不自然大跳

建议动作：

- `penalize_large_pitch_jumps`
- `prefer_neighbor_pitch_continuity`

---

## 十、可演奏性问题映射

### 问题类型 G1：把位连续性差

典型表现：

- 同一句中把位跳来跳去
- playability score 偏低

建议动作：

- `increase_position_continuity_weight`
- `rerank_fingering_candidates`

### 问题类型 G2：不合理指法过多

典型表现：

- impossible fingering count 高

建议动作：

- `filter_impossible_fingerings`
- `constrain_fret_span`

说明：

- 这类问题通常放在节奏和骨架稳定后再处理

---

## 十一、复合问题的优先级策略

现实里常见的不是单个问题，而是多个问题同时出现。

建议用以下优先顺序：

1. stem 问题
2. 节奏框架问题
3. 乐句边界问题
4. 骨架音问题
5. 细节碎音问题
6. 音高异常问题
7. 指法问题

换句话说：

- 输入层 > 结构层 > 细节层 > 表达层

---

## 十二、每轮动作数量控制

建议每轮自动调整遵守以下规则：

### 规则 1

只处理一个主问题。

### 规则 2

最多同时执行两个强相关动作。

例如：

- `increase_min_note_duration`
- `merge_short_notes`

这是合理组合。

但不要一轮里同时做：

- 换 stem
- 改节奏
- 改 phrase
- 改 pitch
- 改指法

否则无法判断变化来源。

### 规则 3

每次动作后都必须重新评测。

没有评测，就不能进入下一轮。

---

## 十三、停止条件设计

自动迭代不能无限跑，需要停止条件。

建议至少设置这些条件：

### 1. 达到目标分数

例如：

- `overall.score >= targetScore`

### 2. 多轮没有明显提升

例如：

- 连续 2 到 3 轮 `scoreDelta < threshold`

### 3. 进入震荡状态

例如：

- 节奏提升但 pitch 下降
- 总体分数来回波动

### 4. 达到最大迭代次数

例如：

- `maxIterations = 5`

---

## 十四、建议的动作字典

建议先统一一套动作名称，方便后续报告、策略、引擎共用。

### 输入层动作

- `switch_input_stem`
- `branch_with_alternative_stem`
- `rerun_full_analysis`

### 节奏层动作

- `retune_beat_tracking`
- `adjust_tempo_estimation`
- `rerun_downbeat_detection`
- `try_alternative_time_signature`
- `shift_measure_alignment`

### 乐句层动作

- `rerun_phrase_segmentation`
- `increase_pause_weight`
- `rebalance_phrase_density`

### 骨架层动作

- `reselect_backbone_notes`
- `increase_strong_beat_weight`
- `increase_phrase_ending_weight`

### 细节层动作

- `increase_min_note_duration`
- `merge_short_notes`
- `suppress_noise_notes`
- `increase_ornament_filter_strength`
- `demote_fast_notes_to_ornaments`

### 音高层动作

- `limit_pitch_range`
- `increase_pitch_smoothing`
- `recompute_pitch_candidates`
- `penalize_large_pitch_jumps`

### 表达层动作

- `rerank_fingering_candidates`
- `filter_impossible_fingerings`
- `constrain_fret_span`

---

## 十五、最小可用实现建议

当前阶段不需要做一个非常复杂的策略系统。

建议先实现最小可用版本：

### Phase 1

支持以下自动映射：

- stem 问题 -> `switch_input_stem`
- 节奏问题 -> `retune_beat_tracking`
- note 太碎 -> `increase_min_note_duration`
- 高频异常 -> `limit_pitch_range`

### Phase 2

再加：

- 乐句边界重跑
- 骨架重选
- 多动作组合规则

### Phase 3

最后再加：

- 分支并行策略
- 历史最优路径参考
- 更复杂的策略选择逻辑

---

## 十六、与其他文档的关系

这份文档和其他设计文档的关系如下：

- 《自动评测与自查闭环设计》
  - 定义系统如何发现问题
- 《自动评测报告格式定义》
  - 定义问题如何被结构化表达
- 本文档
  - 定义发现问题后应该采取什么动作
- 《多轮候选谱版本管理》
  - 定义动作执行后如何保存新版本
- 《最小可用迭代引擎设计》
  - 定义整个动作执行机制如何运转

因此，这份文档是“系统自动行动”的规则层。

---

## 十七、这份文档的下一步

写完这份文档后，下一步最自然的是继续产出：

1. 《最小可用迭代引擎设计 v1》
2. 《中间对象 JSON Schema 草案 v1》

这样就能从“问题和动作的映射规则”继续走到“引擎如何真正执行这些动作”。
