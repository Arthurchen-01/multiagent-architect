# [TASK-ID]: [原子任务名称]

> **任务卡元数据**
> - **所属 Spec**：`[SPEC-ID]`
> - **当前状态**：`PENDING` (待认领) / `RUNNING` (执行中) / `DONE` (已归档)
> - **锁定 Worker**：`null`
> - **创建时间**：YYYY-MM-DD HH:MM:SS
> - **前置依赖任务**：`[]`

---

## 1. 任务范围与执行指令
* **目标文件**：`src/...`
* **执行动作**：
  1. [具体原子动作 1]
  2. [具体原子动作 2]

---

## 2. 自动化退出守卫 (Exit Guard Requirements)
Worker 在宣称本任务完成前，必须在下方自动填充以下真实数据，缺一不可：

```yaml
exit_guard:
  test_command: "pytest tests/test_example.py"
  test_result: "PASS (5 passed in 0.23s)"
  changed_files:
    - "src/module.py"
    - "tests/test_example.py"
  code_hash_sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
```

---

## 3. 运行执行凭据 (由 Worker 在执行完毕后物理写入)
*(由 Worker 自动追加，人类无需手动填写)*
