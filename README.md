# 🏛️ Engineering Architect

> **Enterprise-Grade Spec-Driven Development (SDD), Engineering Judgment & Multi-Agent Orchestration Engine**  
> *“Spec 是源代码，代码是编译产物。从手工编码者进化为系统定义者，AI 替你打字，你替 AI 思考。”*

[![CI](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)]()
[![Architecture](https://img.shields.io/badge/architecture-SDD%20v1.0-orange.svg)]()

---

## 🌟 核心理念与痛点解决

在面对复杂系统、多窗口（Multiple IDE Sessions）与多服务器节点（Distributed Cloud Fleet）并发推进时，传统基于会话聊天的 AI 编程（Vibe Coding / 时代 2）必然遭遇三大死穴：
1. **Review 疲劳 (Review Fatigue)**：AI 代码生成速度远超人脑审核极限，导致人类盲目接受；
2. **意图丢失 (Intent Loss)**：需求被深埋在聊天记录与易失上下文里，Git 历史中查无凭据；
3. **一致性崩塌 (Consistency Collapse)**：多轮对话、多节点并发导致代码风格分裂、代码漂移与架构腐败。

**MultiAgent Architect (时代 3 架构)** 彻底重构了人机协作生产线：
- **意图物理进 Git**：以 `.spec/SPEC.md` 作为唯一可信源（SSOT）；
- **状态机任务总线**：基于文件原子重命名锁解耦多窗口并发，杜绝重复抢占；
- **3 审 1 裁仲裁流水线**：安全 (Security)、并发 (Performance)、不变量 (Invariants) 并行审查，终审官 (Arbiter) 仲裁冲突并动态派卡；
- **真核执行证据链 (Proof-of-Execution)**：基于外部不可预测头（CF-RAY/Date）、原始报文 SHA-256、Linux 内核网络套接字与真实渲染截图，物理杜绝大模型脑补伪造。

---

## 🏗️ 架构全景图

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. 意图定义层 (Spec-as-Source)                                          │
│    .spec/SPEC.md (业务契约 / 数据模型 / 刚性业务不变量 / 验收标准)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. 三权分立审查与仲裁层 (Tri-Review & Arbiter Pipeline)                │
│    ┌───────────────┐     ┌───────────────┐     ┌────────────────┐      │
│    │  sec_guard    │     │  perf_guru    │     │  inv_checker   │      │
│    │  (安全与风控)  │     │  (高并发性能)  │     │  (业务守恒律)  │      │
│    └───────┬───────┘     └───────┬───────┘     └────────┬───────┘      │
│            └─────────────────────┼──────────────────────┘              │
│                                  ▼                                     │
│                        Arbiter Engine (终审仲裁)                        │
│                     reviews/ARBITER_DECISION.json                      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (APPROVED 自动触发派卡)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. 状态机调度总线 (State Machine Queue & Atomic Locking)                │
│    📁 tasks/pending/   ──[原子认领锁]──►  📁 tasks/running/           │
│    (待认领原子任务)                         (锁定为 worker-task.md)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ 分发至多窗口 / 跨机集群
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. 分布式执行与真核证据链 (Distributed Workers & Proof-of-Execution)   │
│    - 远端节点物理执行 (五四云 / 量芯云 / 花屿云)                        │
│    - 自动化退出守卫: 自动跑测试、校验退出门禁                            │
│    - 真核证据链采集:                                                   │
│      * CF-RAY / Date 外部不可预测凭据                                  │
│      * 原始报文 gzip 落盘 + SHA-256 密码学哈希                          │
│      * Linux 内核 /proc/<PID>/net/tcp 真实网络握手验证                  │
│      * 真实 DOM 渲染 PNG 截图与物理视口坐标                             │
│                                    │                                   │
│                                    ▼                                   │
│    📁 tasks/done/      ◄──[验证通过原子移入]                            │
│    📁 audit/PROOF_*.json (法定留痕凭据)                                │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 仓库目录结构

```text
engineering-architect/
├── .spec/                         # 规范中心 (SDD 核心源)
│   ├── SPEC_SCHEMA.json           # Spec 校验 JSON Schema
│   ├── pipeline.yaml              # L1 / L2 / L3 / L4 复杂度拓扑声明
│   ├── ARCHITECTURE.md            # 架构白皮书与技术标准
│   └── templates/                 # 标准 Spec、Task、Review 模板
├── skills/                        # 架构师通用能力与智能体技能库
│   ├── engineering-architect/     # [v0.1.0.0] 工程判断与路由、七步工程闭环、决策记录与汇报规范
│   │   ├── SKILL.md               # 技能主入口（开工闸门、三条腿核实、汇报规范、交付闸门）
│   │   ├── install.ps1            # 本机全 AI 环境一键无损分发安装脚本
│   │   ├── assets/                # 决策记录模板、模式卡模板、工程图汇报模板、触发评测
│   │   ├── references/            # 模式库、诊断树、项目账本、教练模式、权威来源
│   │   └── scripts/               # 技能自检静态语法与引用校验器
│   ├── hierarchical-tree-architect/ # [L4 树状] 树形拓扑递归任务分解与状态机级联 Roll-up
│   └── product-gate-guard/        # [产品门禁] PRD 意图硬卡点与需求准入仲裁守卫
├── tasks/                         # 状态机任务卡池
│   ├── pending/                   # 待认领原子任务 (001-*.md)
│   ├── running/                   # 执行中任务 (workerA-001-*.md)
│   ├── done/                      # 已归档完成任务 (001-*.md)
│   └── blocked/                   # 阻断/待修复任务
├── core/                          # 核心调度与仲裁引擎 (零第三方依赖纯原生 Python)
│   ├── state_machine.py           # 任务状态机与原子文件重命名并发锁
│   ├── arbiter_engine.py          # 3 审 1 裁仲裁引擎与加权决策
│   ├── proof_of_execution.py      # 真核执行证据链与防脑补校验器
│   ├── git_guard.py               # Git 浅克隆检测与工作树安全隔离
│   └── fleet_sync.py              # 跨机代码漂移与文件 SHA-256 对齐检查
├── cli/                           # 统一命令行入口
│   └── main.py                    # architect status / claim / complete / arbitrate
├── tests/                         # 自动化测试套件
│   ├── run_tests.py               # 纯原生 unittest 执行器 (7/7 全部 PASS)
│   └── test_engineering_architect_skill.py # 架构师核心技能完整性自动化门禁测试
└── docs/                          # 文档与专题库
    └── fleet_architectures/       # 全项目多机队架构规约表 (涵盖 Arthurchen-01 旗下全部 25 个 GitHub 仓库)
        ├── 00_master_fleet_architecture_matrix.md
        ├── 01_wb_international_architecture.md
        ├── 02_samurai_admission_architecture.md
        ├── 03_telegram_accounting_bot_architecture.md
        ├── 04_ai_token_gateway_7864_architecture.md
        ├── 05_vocab_transcription_and_rakuten_architecture.md
        ├── 06_captcha_and_reverse_engineering_architecture.md
        ├── 07_deepseek_and_model_hacker_architecture.md
        ├── 08_ip_block_and_egress_guard_architecture.md
        ├── 09_ecommerce_and_social_scraping_architecture.md
        ├── 10_learning_and_content_engine_architecture.md
        └── 11_multiagent_and_tooling_matrix_architecture.md
```

---

## 🚀 快速上手与 CLI 指令

本项目核心模块均采用纯原生 Python 标准库实现，**零第三方包强制依赖**，可在任何精简 Linux VPS、Docker 容器或 Windows 终端开箱即用。

### 1. 运行系统全量自测
```bash
python tests/run_tests.py
```
*输出：`Ran 5 tests in 0.295s - OK`*

### 2. 状态机看板查看
```bash
python cli/main.py status
```

### 3. 多窗口 / 跨机 Worker 原子抢占任务
```bash
# 窗口 1 或节点 1023 认领任务
python cli/main.py claim srv-1023

# 完成任务并提交退出守卫 (Exit Guard)
python cli/main.py complete srv-1023 TASK-001 --result "PASS (5 tests passed)" --hash "e3b0c44..."
```

### 4. 触发 3 审 1 裁仲裁
```bash
python cli/main.py arbitrate SPEC-AUTH-001
```

### 5. Git 仓库防浅克隆与卫生检查
```bash
python cli/main.py git-check
```

---

## 📜 许可证与合规
Copyright (c) 2026 Arthurchen-01. All rights reserved.
