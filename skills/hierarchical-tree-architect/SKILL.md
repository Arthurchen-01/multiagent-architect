---
name: hierarchical-tree-architect
description: Recursive Tree-of-Agents & Hierarchical Work Breakdown Structure (WBS) Architecture Skill. Enables multi-tier task decomposition (HQ -> Department -> Line Specialist -> Atomic Worker), strict abstraction barriers, parent-child task DAG, and precision context scoping without token overflow.
---

# 🌳 分层树状架构师技能 (Hierarchical Tree Architect Skill)

> **定位**：解决复杂工程中“子线程交织、职责混淆、上下文爆炸”的递归分解引擎。  
> **核心原则**：**【上层只看下层交付物，不看下层代码；下层只读本层规约，不窥探全局噪音】**（信息隐藏与抽象屏障）。

---

## 一、 四层树状递归分解模型 (4-Tier Recursive Model)

面对像 Samurai（涵盖数据、前端、建模、文书）这样的巨型系统，严禁采用单层扁平任务池，必须按四层树状下钻：

```
Level 0: 总控台 (HQ Master)
         └── 只看大里程碑、部门间交付契约 (如: 留学系统 V2.0 联调)
               │
               ▼
Level 1: 部门主管 (Department Lead)
         └── 只管本部门两大主线契约 (如: D:\babra-samurai)
               ├── 子线程 A: 数据底座专项 (Data Vault Sub-thread)
               └── 子线程 B: 前端融合专项 (Frontend Fusion Sub-thread)
                     │
                     ▼
Level 2: 专业子线程工序长 (Line Specialist)
         └── 只管工序流水线依赖 (DAG)
               ├── [工序 1] 抓取与提取 (Crawl/Extract)
               ├── [工序 2] CDS 真实字段清洗 (Clean/Verify)
               └── [工序 3] 适配器接口暴露 (API Adapter)
                     │
                     ▼
Level 3: 原子叶子执行员 (Atomic Worker / Ephemeral Subagent)
         └── 只拿一张不可再分的任务卡 (Leaf Task Card)
               - 输入: 具体的 1~2 个源文件与行号
               - 规约: 一句能验收的话
               - 产出: 原子代码 Diff + 真实测试输出/截屏
               - 生命: 任务完成即销毁，不驻留上下文
```

---

## 二、 抽象屏障铁律 (Abstraction Barrier Invariants)

1. **父任务与子任务状态级联（Cascading Status）**：
   - 父任务的状态是所有子任务状态的逻辑与（$\text{Parent} = \bigwedge \text{Children}$）；
   - 只有当所有子任务均达到 `done/` 且通过独立复核，父任务方可标记为完成；
2. **就近信息装载（Context Scoping by Level）**：
   - Level 0 只读全局 `00_master_fleet` 与里程碑；
   - Level 1 只读部门 `AGENTS.md` 与对外 API 契约；
   - Level 2 只读专项流水线工序表与数据字典；
   - Level 3 只读当前文件与报错日志。
   - **严禁反向越级倒灌**（Level 3 改代码的执行员绝不需要知道总控的融资或部署拓扑）。

---

## 三、 父子工单命名与目录结构规范

```
tasks/
├── pending/
│    └── TASK-SAMURAI-001/                  # Level 1 部门大任务
│         ├── TASK-DATA-P1.md               # Level 2 数据子线程任务
│         │    ├── T-DATA-01-crawl.md       # Level 3 原子执行卡
│         │    └── T-DATA-02-cds-clean.md   # Level 3 原子执行卡
│         └── TASK-FE-P2.md                 # Level 2 前端子线程任务
│              ├── T-FE-01-tokens.md        # Level 3 原子执行卡
│              └── T-FE-02-routes.md        # Level 3 原子执行卡
├── running/
└── done/
```

---

## 四、 架构师执行三步法 (How to Decompose)

当面对用户的一个复杂新诉求时，架构师执行以下动作：
1. **定边界（Level 0）**：写出本期交付的目标与做/不做范围；
2. **立部门与子线程（Level 1 & 2）**：划分专业线，明确数据与前端的交接界面（JSON 契约）；
3. **下发叶子任务卡（Level 3）**：拆解为每个不超过 2 小时、修改行数不超过 100 行的原子工单，交由对应子代理认领。
