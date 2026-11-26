# Skill Benchmark 基准标准 (v1)

> 这是"如何给一个 skill 定义好坏"的可校验规范。每个要进化的 skill 必须在 `<skill>/evals/`
> 下提供以下 6 件。校验器 `scripts/validate_bench.py` 强制其中的硬约束。
>
> 设计原则:**把"好坏"从感觉拆成多层可观测信号**,并优先使用强信号(确定性 > 锚定 rubric > LLM judge)。

```
<skill>/evals/
  ├── scenarios.md            # 行为对错(分 pos/adv/over)
  ├── rubric.md               # "好"的加权维度
  ├── invariants.md           # 红线(一票否决)
  ├── directional_probes.md   # 忠实度(确定性正则)
  ├── posture_probes.md       # 行为/范围漂移
  └── controls/               # 校准判官本身
      ├── ctrl-A-identity.md
      ├── ctrl-B-posture-bad.md
      └── ctrl-C-obvious-regress.md
```

---

## 1. scenarios.md —— 行为对错

每条场景把"对"写成两个清单,不留主观空间。标题格式必须可被校验器解析:
`## scenario-<N>-<pos|adv|over>: <slug>`

```markdown
## scenario-1-pos: <slug>
**Trigger:** <什么情况触发这条>
**User prompt:** "<真实用户输入>"
**Expected behavior:**
- <必须命中的行为 1>
**Must NOT do:**
- <碰了就扣分的反模式 1>
```

**约束(校验器强制):**
- 总数 ≥ 6。
- `pos`(正例,该做的做了)≥ 4。
- `adv`(对抗,顶住压力)≥ 1。
- `over`(过度触发,不该做时忍住)≥ 1。

**怎么定义好坏:** `Expected` = 必须命中;`Must NOT` = 出现即扣。判官只勾选,不评感觉。
三类缺一不可——好 skill 不只"该出手时出手",还要"扛得住诱导"且"不该出手时不乱触发"。

---

## 2. rubric.md —— "好"的加权维度

把"好"拆成若干维度,**每档(0/1/2)绑定一个判官能直接看到的信号**,权重编码优先级。

```markdown
## <criterion-name> (weight: 0.5)
**Observable signal:** <这一维看什么>
| Score | What the judge confirms |
|---|---|
| 2 | <满分对应的可观测信号> |
| 1 | <部分> |
| 0 | <不合格的可观测信号> |
```

**约束:** 维度 ≥ 3;所有 `weight:` 之和 = 1.0 ± 0.01。

**怎么定义好坏:** 锚定档位 = 把"还行/不行"换成"勾选了哪一行";权重 = 你的优先级声明。

---

## 3. invariants.md —— 红线(一票否决)

不是扣分,是准入。用 RFC-2119 关键词。

```markdown
- MUST NOT <绝对禁止的行为>
- MUST <绝对必须的行为>
- SHOULD NOT <强烈不建议>
```

**约束:** 含 MUST / MUST NOT / SHOULD / SHOULD NOT / MAY 的条目 ≥ 3。

**作用:** Phase 4 的 invariants-gate——违反任一条的候选直接出局,不论 rubric 分多高。
rubric 是"打分",invariants 是"准入",两者分开。

---

## 4. directional_probes.md —— 忠实度(确定性正则,S1 强信号)

验"模型真的读懂并执行了 skill 指令",**不靠 LLM judge,用正则断言**。

```markdown
## directional-probe-1: <slug>
**Variant text (full SKILL.md with directional change applied):**
```markdown
<在 baseline 上加一条机器可验证的明确指令,例如"回复必须以 1. 开头">
```
**Scenario user prompt:** "<触发输入>"
**Assertion (Python regex; runner output must match):** `^1\.\s`
```

**约束:** probe ≥ 2。断言必须是确定性正则,无 LLM 判断、无人工兜底。

**怎么定义好坏:** 给 skill 加一条明确指令,看输出符不符合正则。这是把"忠实度"从主观变客观的关键一招——能这样测的维度,就别交给判官。

---

## 5. posture_probes.md —— 行为/范围漂移

改 skill 后语气/强硬度/范围有没有悄悄跑偏。回归不一定是答错,可能是人格蔓延。

```markdown
## probe-<slug>: <name>
**Prompt:** "<探针输入>"
**Drift signal:** <variant 相对 baseline 的漂移信号,如 consider→MUST、越界答范围外话题>

## probe-multi-turn: multi-turn
**Turn 1 prompt:** "..."
**Turn 2 prompt:** "..."
**Turn 3 prompt:** "..."
**Drift signal:** <skill 的指令有没有被错误带到不适用的后续轮>
```

**约束:** probe ≥ 1(强烈建议含 1 条 multi-turn)。校验器目前只检查本文件是否存在,不统计条数,这条由人把关。
判官给出 `drift_severity` 0–3;Phase 4 对比 winner 与 baseline 的漂移增量。

---

## 6. controls/ —— 校准判官本身(本标准最关键的元层)

放三个"答案已知"的变体,反过来验"你的好坏判定本身可不可信"。**这是测试这套测试。**

| 文件 | 内容 | 必须得到的结果 | 验证 |
|---|---|---|---|
| `ctrl-A-identity.md` | = baseline 原样副本 | 分与 baseline 一致(±0.05) | 判官噪声够小吗 |
| `ctrl-C-obvious-regress.md` | 故意写烂(无视用户、答非所问) | 排在所有候选最末 | 判官分得出好坏吗 |
| `ctrl-B-posture-bad.md` | 故意人格/范围跑偏 | 至少 1 条 posture probe drift ≥ 2 | 漂移检测器瞎不瞎 |

**Phase 1 准入闸:** 三个 control 任一不达预期 → 判官不可信 → **禁止进化**,先回去修 rubric/invariants/judge。
判官连 ctrl-C 这种明显垃圾都排不到最后,它给真候选的分就一律不能信。

---

## 7. 校验

```bash
python3 scripts/validate_bench.py <skill>/evals
# valid:true(exit 0)才允许进入 Phase 1;否则按 errors[] 补齐,不许自动起草基准
```

校验器只查**结构与数量**硬约束(文件齐全、场景三类齐、权重和为 1、红线 / directional probe / 控制数量达标)。
**内容质量(场景是否真有代表性、rubric 档位是否锚得准)由人在 Phase 0 负责**——这部分不可自动化,正是基准的人力成本所在。

---

## 8. 最小可用基准(起步量)

一个 skill 的"最小但合格"基准 = **6 scenario + 3 rubric 维 + 3 invariant + 2 directional probe + 1 posture probe + 3 control**。
这已比"5 example + 1 个二元 evaluator"实质强一个量级,且跨模型代际不贬值。
模板骨架见 `templates/evals/`。
