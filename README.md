# skill-evolve —— benchmark-first 的 skill 自进化框架

> 一句话定位:**先把"什么叫做对"沉淀成可校验的基准,再让模型在留出集 + 门控下小步进化 skill。基准是版本化的主资产,skill 文本是可丢弃的产物。**

本框架综合了三个已有方案的优点,并落实了一条核心认知:**skill 和 optimizer 都是会被模型升级吞掉的"耗材",只有 benchmark 跨模型代际复利——所以最该投资、最该先建的是基准本身。**

---

## 1. 三条核心理念(决定了所有设计)

1. **基准优先 (benchmark-first)。** 不允许"没有基准就进化"。Phase 0 必须先产出并校验 `evals/` 契约;skill 的**主交付物是这套基准**,不是改后的 SKILL.md。
2. **门控是闸,不是源。** 门控只过滤、不创造提升。决策链 `门控 → eval → benchmark → 对错的定义` 决定了:门控的可信度 = 它下游基准的有效性。所以**进化前先校准判官**(用控制变量),判官不可信就不许进化。
3. **信号强度分级。** 能用确定性断言就不用 LLM judge;能用锚定档位的 rubric 就不用裸感觉。人只出现在最底层"定义对错"处,不进每候选的回路。

---

## 2. 环节

| 环节 | 在本框架中的位置 |
|---|---|
| 人在环定 GT(对错定义不可自动化) | Phase 0:基准由人确认,finalize 守卫 |
| 会话采集 → 候选 → 人确认才落盘 / SkillOpt-Sleep | Phase 0 的任务来源(可选) |
| 有界三段小改(评判要点/怎么做/方法论) | Phase 3:mutator 只动少数几处 |
| 留出集 + 严格改善门控(strict `>`) |  Phase 4:`gate` 严格大于才接受 |
| train/val/test 三分,小样本用 soft 分 |  基准的 split 纪律 + 评分 |
| optimizer/target 分离(强 optimizer) |  配置:进化用强模型,目标冻结 |
| eval 契约:pos/adv/over + 加权 rubric + RFC-2119 invariants + 确定性 directional probe + posture probe | 基准标准(见 `BENCHMARK_STANDARD.md`) |
| 控制变量校准判官 + canary 防泄漏| Phase 1:判官可信度前置闸 |
| 进化前先验证进化台可信| 把"可信度 spike"做成进化的准入条件 |

**本框架的定位(不夸大):** 。它的主体是**整合 + 标准化**(收敛优点 + 配基准标准 + 校验器),是施工规范/脚手架,**不是被验证过更强的新引擎**。唯一称得上"新"的是把"基准=跨代际复利资产"做成治理原则(模型升级强制重跑)。
---

## 3. 架构:一个进化周期

```
Phase 0  建基准 (benchmark-first)        ← 人定 GT,产出并校验 evals/
   │        validate_bench.py 不过 → 停,先补基准
   ▼
Phase 1  校准判官 (gate-before-gate)     ← 跑 controls:identity/regress/drift
   │        判官不可信(连明显垃圾都排不对) → 停,先修 rubric/judge
   ▼
Phase 2  评基线                          ← baseline skill 在 scenarios 上得分
   ▼
Phase 3  有界变异 (bounded mutate)       ← 按失败轴生成 K 个候选,各只改少数几处
   ▼
Phase 4  双门控 (invariants + held-out)  ← 先过红线,再 strict-improve on val,零回归
   ▼
Phase 5  暂存提案 (stage, 人 adopt)      ← 不自动写线上 skill;人确认才落
   ▼
   (治理) 模型升级时 → 重跑基准 → 判断"被吞/退步",决定 skill 去留
```

**与"耗材/资产"对应:** Phase 0–1 产出的基准是资产(入库长存);Phase 3–5 产出的 skill 是耗材(随模型升级可丢)。

---

## 4. Eval 策略(显式)

### 4.1 信号强度优先级(自上而下选最强可用的)

| 级别 | 形式 | 例子 | 何时用 |
|---|---|---|---|
| **S1 确定性** | 字符串/正则/可执行断言 | directional probe `^1\.\s`;import 改写精确比对 | 只要"对"能被机器判,**首选** |
| **S2 锚定 rubric** | 每档(0/1/2)绑可观测信号 + 权重 | correctness/brevity/asked-once | 对错主观但可拆维度 |
| **S3 LLM judge** | 独立判官 + 锚定 rubric | 锐评"梗点"是否命中 | 只有 S1/S2 都不行时,且**必须经 Phase 1 校准** |

**铁律:** 能 S1 不用 S2,能 S2 不用 S3。S3 的可信度 ≤ 判官可信度,所以 S3 必须配 control 校准 + canary 防泄漏(判官不得看到候选 skill 文本,只看行为)。

### 4.2 自动化边界:人放在哪

- **人只在最底层"定义对错"**:写 scenarios 的 Expected/Must-NOT、定 rubric 权重、定 invariants 红线、确认 GT。这层不可自动化(maga 的教训)。
- **回路里全自动**:打分、变异、门控、回归检测。人不逐候选打分。
- **采纳是人的**:Phase 5 暂存,人 adopt(Claude Dreams / maga 的 review-then-adopt)。

### 4.3 留出纪律(防循环论证)

- `scenarios` 内部不复用:**提变异看到的失败**来自 train 切片,**门控验收**用 val 切片,**最终汇报数字**用 test 切片(从不参与选择,只读一次)。
- 小样本(每切片 < ~10)用 **soft 分**(部分得分)而非 hard 准确率,否则门控感知不到细微进步(SkillOpt 的经验)。

### 4.4 门控规则(strict improve + 零回归 + 红线)

候选被接受,当且仅当**三条全满足**:
1. **invariants 全过**(任一 MUST NOT 被违反 → 直接出局,不论分多高);
2. **val 分严格大于当前**(`>`,非 `>=`,平分也拒,防漂移);
3. **零回归**(val 里原本通过的样本不许变红)。
否则丢弃,skill 回滚,把"被拒的编辑 + 掉分原因"记入 buffer 供下轮避坑(maga/SkillOpt 共有)。

---

## 5. Skill Benchmark 基准(摘要,完整见 `BENCHMARK_STANDARD.md`)

每个要进化的 skill 必须自带 `evals/` 目录,含 6 件:

| 文件 | 定义"好坏"的哪一面 | 最低要求 |
|---|---|---|
| `scenarios.md` | 行为对错(Expected/Must-NOT) | ≥6 条,且 pos≥4 / adv≥1 / over≥1 |
| `rubric.md` | "好"的加权维度,每档锚定信号 | ≥3 维,权重和 = 1.0 |
| `invariants.md` | 红线(一票否决) | ≥3 条 RFC-2119 MUST/MUST NOT |
| `directional_probes.md` | 忠实度(确定性正则) | ≥2 条 |
| `posture_probes.md` | 行为/范围漂移 | ≥1 条(建议含 multi-turn) |
| `controls/` | **校准判官本身** | ctrl-A identity / ctrl-C regress / ctrl-B drift |

校验:`python scripts/validate_bench.py <skill>/evals` —— 不过则 Phase 0 停。

---

## 6. 治理:为什么这套基准比 skill 更值钱

- **模型升级时强制重跑基准。** 用它分辨"新模型吞掉了 skill 的能力(可删 skill)"vs"悄悄退步了(需保留/加强 skill)"。没有基准,这两者无法区分,只能盲赌。
- **基准是下一代 skill 的优化信号。** 即使本代 skill 被吞,基准还在,直接拿去优化下一个尚未被吞的 skill。
- **结论:skill 投资折旧,benchmark 投资复利。** 入库的应是 `evals/`,SKILL.md 只是它当下的一个解。

---

## 7. 诚实局限

- **S3(LLM judge)永远只和判官一样可信**;Phase 1 校准能暴露判官失灵,但不能消除其偏差。无 S1/S2 可用的纯主观 skill,本框架降级为"人辅助",收益有限。
- **基准构造是人力成本**,且是前置硬成本——这正是它复利的代价。小团队应先给"高频 + 可客观判对错"的 skill 建基准。
- **进化上限由 optimizer 决定**:基准再好,弱 optimizer 也够不到天花板。建议进化用强模型,冻结目标模型。
