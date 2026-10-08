# [REVIEW-ID]: 审查报告 ([审查角色名称])

> **审查元数据**
> - **审查员角色**：`[sec_guard | perf_guru | inv_checker]`
> - **目标对象**：`[SPEC-ID 或 TASK-ID]`
> - **审查时间**：YYYY-MM-DD HH:MM:SS
> - **综合判定**：`[APPROVED | REJECTED]`

---

## 1. 核心合规性检查清单

| 检查项 | 状态 | 现场证据与风险点说明 |
| :--- | :--- | :--- |
| **规则 1** | `PASS / FAIL` | [详细代码行号或证据] |
| **规则 2** | `PASS / FAIL` | [详细代码行号或证据] |
| **规则 3** | `PASS / FAIL` | [详细代码行号或证据] |

---

## 2. 阻断性缺陷清单 (Blocking Defects)
*(若无则标明 NONE)*
1. **[BLOCK-01]**：文件 `src/path.ts:L42` 存在并发竞态风险，缺少行锁机制。

---

## 3. 机器可读裁决字段 (Machine-Readable JSON)
```json
{
  "reviewer": "sec_guard",
  "status": "APPROVED",
  "score": 95,
  "blocking_issues_count": 0,
  "signature_sha256": "4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a"
}
```
