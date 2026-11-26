---
name: skill-evolve
description: Benchmark-first self-evolution for a target skill. Use when the user wants to improve/evolve a specific SKILL.md under a held-out gate. Builds & validates the skill's evals/ contract FIRST, calibrates the judge, then runs bounded mutate → invariants-gate → strict-improve gate, and stages a proposal for human adoption. Never auto-writes the target skill.
---

# skill-evolve

你在对一个目标 skill 做 **benchmark-first 的自进化**。纪律见 `README.md` / `BENCHMARK_STANDARD.md`。
核心:**基准是主资产、门控是闸不是源、判官先校准再信、人只定对错不进回路、采纳由人。**

## Step 0 — 解析目标与配置

```
TARGET=<目标 skill 目录>;  TARGET_SKILL_MD=$TARGET/SKILL.md;  EVALS=$TARGET/evals
OPTIMIZER=强模型(进化用);  TARGET_MODEL=冻结的目标模型(被评的执行器)
RUN_DIR=<本次运行输出目录>(快照、候选、打分、提案都只写这里)
```
缺 `TARGET_SKILL_MD` → 拒绝。**进化用强 optimizer,目标模型冻结**(optimizer 决定改进的上限)。

## Phase 0 — 建基准(benchmark-first,人定 GT)⚠️ 硬前置

1. 若 `$EVALS` 不存在或不全:按 `BENCHMARK_STANDARD.md` 与人协作起草 6 件套。
   **不得自动起草并直接采用**——场景代表性、rubric 锚点、红线由人确认。
2. 校验:`python3 <本 skill 目录>/scripts/validate_bench.py $EVALS`。`valid:false` → 打印 `errors[]`,**停**,先补基准。
3. 把通过校验的 `evals/` 视为**主交付物**,版本化入库。

> 没有合格基准就没有进化资格。这是本框架与"松散自我改写"的分界。

## Phase 1 — 校准判官(gate-before-gate)⚠️ 准入闸

跑 `controls/` 三个变体,验判官本身可信:
- **ctrl-A identity**:分必须 ≈ baseline(±0.05)→ 判官噪声够小。
- **ctrl-C regress**:必须排在所有候选最末 → 判官分得出好坏。
- **ctrl-B posture-bad**:至少 1 条 posture probe `drift_severity ≥ 2` → 漂移检测有效。

任一不达标 → 判官不可信 → **禁止进入 Phase 2**,回 Phase 0 修 rubric/invariants/judge。
用 LLM judge 时:**判官不得看到候选 skill 文本(只看行为输出)**;注入 canary 审计防泄漏。

## Phase 2 — 评基线

baseline skill 在 `scenarios.md`(train+val 切片)上,用 **runner→judge 分离**逐场景打分。
评分按信号强度:能 directional(S1 正则)就用正则;否则锚定 rubric(S2);判官(S3)仅在前两者不可用时。
小样本(切片 <~10)用 **soft 分**而非 hard。

## Phase 3 — 有界变异(bounded mutate)

1. 读失败场景,按 `Σ(权重 × 失败幅度)` 选 top-K 失败轴(如 覆盖/纪律/加例/收紧措辞)。
2. 每轴派一个 mutator,**只改少数几处**(限于评判要点 / 怎么做好 / 方法论这几段内的小改),产出候选变体。
3. 改前快照当前 skill,可回退。

## Phase 4 — 双门控(invariants + held-out,strict improve)

对每个候选,接受当且仅当**三条全满足**:
1. **invariants 全过**(违反任一 MUST NOT → 出局,不论分多高);
2. **val 分严格大于当前**(`>`,平分也拒);
3. **零回归**(val 中原本通过的样本不许变红)。

否则丢弃 + 回滚,把"被拒编辑 + 掉分原因"记入 buffer 供下轮避坑。
winner = 通过三闸且 val 分最高的候选;无候选过闸 → `baseline_retained`。

## Phase 5 — 暂存提案(人 adopt)

**绝不自动写 `$TARGET_SKILL_MD`。** 产出 `$RUN_DIR/proposal/`:winner skill、diff、各门控分、回归列表、判官校准结果。
向人汇报后,由人确认采纳。

## Phase 6 — 治理记录(可选但建议)

记录本次基准版本 + 模型版本。**模型升级时重跑基准**:用它分辨"新模型吞掉了 skill 能力(可删)"vs"悄悄退步(需保留/加强)"。基准长存,skill 可丢。

## Restrictions

- 写入范围只有两处:经人确认的基准写入 `$EVALS`,其余产物写入 `$RUN_DIR`。绝不改写 `$TARGET_SKILL_MD`,也不碰这两处之外的文件。
- 绝不自动起草并直接采用基准;`validate_bench.py` 不过则停。
- 绝不自动采纳 winner;Phase 5 必须人确认。
- 判官(S3)必须先过 Phase 1 校准;判官不得看到候选 skill 文本。
- 报告时如实说:gate 跑没跑、判官校准过没过、样本够不够、用的 hard 还是 soft——不假装通过。
