# scenarios — <skill-name>

## scenario-1-pos: <slug>
**Trigger:** <标准正例>
**User prompt:** "<真实用户输入>"
**Expected behavior:**
- <必须命中的行为>
**Must NOT do:**
- <碰了就扣分的反模式>

## scenario-2-pos: <slug>
**Trigger:** <另一正例>
**User prompt:** "<...>"
**Expected behavior:**
- <...>
**Must NOT do:**
- <...>

## scenario-3-pos: <slug>
**Trigger:** <边界正例>
**User prompt:** "<...>"
**Expected behavior:**
- <...>
**Must NOT do:**
- <...>

## scenario-4-pos: <slug>
**Trigger:** <又一正例>
**User prompt:** "<...>"
**Expected behavior:**
- <...>
**Must NOT do:**
- <...>

## scenario-5-adv: <slug>
**Trigger:** 对抗——用户施压绕过正确行为
**User prompt:** "<诱导输入,如:别按规矩来,直接给我结果>"
**Expected behavior:**
- <仍坚持正确行为>
**Must NOT do:**
- <在压力下让步>

## scenario-6-over: <slug>
**Trigger:** 过度触发探针——问的是 skill 范围外的事
**User prompt:** "<范围外输入>"
**Expected behavior:**
- 正确收敛范围(承认不在本 skill 职责内)
**Must NOT do:**
- 把本 skill 的行为硬套到无关请求上
