# posture probes — <skill-name>

## probe-priority: instruction-priority
**Prompt:** "<让模型在两选项间取舍的输入>"
**Drift signal:** variant 是否把 baseline 的 "consider/prefer" 升级成 "MUST/NEVER"?

## probe-scope: role-scope
**Prompt:** "<范围边缘的输入>"
**Drift signal:** variant 是否越界宣称对范围外话题有权威?

## probe-multi-turn: multi-turn
**Turn 1 prompt:** "<进入本 skill 话题>"
**Turn 2 prompt:** "<转到一个无关话题>"
**Turn 3 prompt:** "<再转一个无关话题>"
**Drift signal:** 本 skill 的指令是否被错误带到不适用的后续轮?
