# directional probes — <skill-name>

## directional-probe-1: <slug>
**Variant text (full SKILL.md with directional change applied):**
```markdown
<在 baseline 上加一条机器可验证的明确指令,例如:回复必须以 "1." 开头的编号列表>
```
**Scenario user prompt:** "<触发输入>"
**Assertion (Python regex; runner output must match):** `^1\.\s`

## directional-probe-2: <slug>
**Variant text (full SKILL.md with directional change applied):**
```markdown
<另一条机器可验证指令,例如:回复必须以指定标记结尾>
```
**Scenario user prompt:** "<触发输入>"
**Assertion (Python regex; runner output must match):** `<your-regex>`
