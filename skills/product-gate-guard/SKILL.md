---
name: product-gate-guard
description: Universal Multi-Agent Product Requirements, Boundary & Arbiter Gate Guard for WorkBuddy, DeepSeek Harness, Antigravity, and all fleet agents. Enforces Owner goals, Quota-and-Stop mode, 20s steady polling, 60m freshness invariant, and prohibits unauthorized PRD tampering.
---

# 🛡️ Universal Product Requirements & Arbiter Gate Guard

本技能是所有接入本项目的 AI Agent（WorkBuddy, DeepSeek Harness, Antigravity, Roo Code 等）在进入工程前的**最高前置闸门**。

## 🚪 进入项目三步法（Pre-Flight Check）
1. **读法典**：首先阅读 [PRODUCT_REQUIREMENTS_GATE.md](file:///D:/multiagent-architect/.spec/PRODUCT_REQUIREMENTS_GATE.md)，明确系统最高法律与权责划分；
2. **读架构**：阅读 [ARCHITECTURE.md](file:///D:/multiagent-architect/.spec/ARCHITECTURE.md) 与 [01_wb_international_architecture.md](file:///D:/multiagent-architect/docs/fleet_architectures/01_wb_international_architecture.md)；
3. **验红线**：自我核验是否违背七条系统级红线。

## 🎯 产品核心意志与不可违背原则
1. **PRD 归属老板**：业务目标（如日产 100 个成品 / ¥200 预算）由用户决定，AI 绝对禁止私自降低或篡改 PRD；
2. **配额执行模式 (Quota-and-Stop)**：从用户启动时间点 $T_0$ 开始计数，达到配额即自动停止采购与买号，在途跑完即停；
3. **20 秒稳健轮询**：按 20 秒周期平滑检查增量，杜绝破坏性并发冲击；
4. **鲜度守卫 (即买即跑，60m TTL)**：无空闲 Worker 严禁进货；进货超过 60 分钟强制作废，杜绝号在队列放烂；
5. **资金对账守恒**：每一笔扣费必须有本地账单与供应商 Order ID 严格对应，严禁漏账；
6. **零 Ad-hoc 生产热修**：禁止在单台服务器上手动修改代码，必须通过 Git 和 FleetSync SHA-256 全机队对齐。
