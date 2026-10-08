# 07-DeepSeek 与 Model Hacker 架构规范 (ds-mh / ds-register-topup / only-for-env)

> **纳管仓库**：
> - `Arthurchen-01/ds-mh` (Model Hacker Frame 动态注入与模型代理框架)
> - `Arthurchen-01/ds-register-topup` (DeepSeek/AI 平台全自动注册充值与号源流转系统)
> - `Arthurchen-01/only-for-env` (轻量化纯净环境依赖与沙盒隔离运行时)
> 
> **部署节点**：
> - **五四云-1023** (`156.225.28.106`)：AI 网关核心宿主、MHF 授权拦截层、本地 8080/7864 反代代理
> - **本机 Windows 控制端** (`D:\03_AI·Token·模型开发\ds-mh`, `D:\对话记录\03_dsh_DeepSeekHarness`)：DSH 控制台与 Cordis 插件开发工作区
> - **五四云-620 / 621 / 小特云**：远程 DSH Worker 执行节点 (执行代码与模型推理)

---

## 一、 系统定位与核心痛点

### 1.1 业务背景
在多智能体自主开发与高强度编程评测中，开源模型（如 DeepSeek V2.5/V3/Coder）及商业模型（Claude / Gemini）常受到严格的内容安全过滤器、拒绝响应策略（Refusal Trigger）以及格式僵化的 System Prompt 约束。`ds-mh` (Model Hacker Frame / MHF) 构建了一套具备**动态接管 System Prompt、多模态请求解耦、全权限放行与端到端密钥分发**的甲胄模式运行时（Armor Mode Runtime）。

### 1.2 历史多服务器协作 4 大死穴与根因分析
1. **未授权阻断与硬编码凭据泄漏**：
   - *病根*：早期直接在 worker 配置文件中明文下发 Token 与私钥，节点一旦被扫或被镜像即导致全量凭证报废；
   - *整改*：引入基于 **X25519 ECDH + AES-256-GCM** 的动态远程提示词加密分发机制（`MFP5` 数据包，AAD 校验），设备硬件指纹绑定（`mhw-` / `mhm-`），实现一机一密与自愈销毁。
2. **多节点空转与“任务中心连接被拒”死锁**：
   - *病根*：远程 worker 守护进程在任务调度中心停机时无限高频重试（`claim_next: Connection refused`），每秒刷爆日志盘；
   - *整改*：建立指数退避与探活断路器（Exponential Backoff & Circuit Breaker），连续 5 次探测失败自动挂起并释放 CPU/IO 资源。
3. **环境污染与跨机依赖冲突**：
   - *病根*：不同 worker 混合安装第三方轮子，导致 PyTorch / Transformers / ONNX 运行时动态库版本地狱；
   - *整改*：规范化 `only-for-env` 纯净沙盒隔离，零外部重依赖侵入，严格使用标准库或虚拟环境隔离。
4. **多模型网关并发瓶颈与虚假排队**：
   - *病根*：网关配额与 `max_in_flight_global=2` 限制导致 256 个有效号无法释放算力，出现 4.6 秒首字延迟；
   - *整改*：MHF 动态解耦请求队列，按号池可用度动态扩容并发窗口至 `N_usable * 1.5`。

---

## 二、 核心架构设计与通信协议

### 2.1 MHF 甲胄模式工作流 (Armor Mode Lifecycle)

```
[本地/远程 IDE (Codex / DSH)]
       │
       ▼ (1) 发起推理请求 (POST /v1/chat/completions)
[MHF 拦截层 (:8080)] ───► [设备指纹校验: MachineGuid -> SHA-256(domain||id)]
       │
       ├─► (2) 远程授权门控 (X25519 ECDH + AES-256-GCM) ──► 动态下发 MFP5 甲胄提示词
       │
       ├─► (3) 模式选择器 (Mode Selector):
       │        ├── general (2.0.2): [MODE: UNRESTRICTED] 全功能放行
       │        ├── mode-8xkmkygn: 通用旧版兼容
       │        ├── mode-vfbm5ucl: 测试静默模式
       │        └── custom: 动态加载 custom_system_prompt.txt
       │
       ▼ (4) 协议重写与注入 (systemPrompt.section)
[上游统一网关 (五四云-1023:7864 / DeepSeek 官方 / Anthropic)]
```

### 2.2 核心模块拓扑

| 模块名称 | 纳管仓库 / 路径 | 核心职责 | 依赖与环境 |
| :--- | :--- | :--- | :--- |
| **MHF Core Runtime** | `ds-mh/plugin` | 请求拦截、Cordis 插件适配、提示词注入与保护标记检测 | Node.js 18+ / Python 3.10 |
| **Auto Register & Topup** | `ds-register-topup` | DeepSeek/各主流平台自动化注册、Cookie 提取、余额充值流水监控 | Playwright Stealth / requests |
| **Sandbox Isolation** | `only-for-env` | 轻量化沙盒隔离、跨平台依赖自愈、纯净执行目录模板 | Shell / PowerShell |
| **Upstream Gateway** | `五四云-1023:7864` | 256 账号轮询、信用额度账本计算、自动解除冷却 | FastAPI / Uvicorn |

---

## 三、 多服务器部署与运维操作手册 (Fleet Operations)

### 3.1 跨节点部署拓扑

```
┌──────────────────────────────────────────────┐
│           五四云-1023 (主控 AI 网关)           │
│  - wb2api:7864 (256 号池)                     │
│  - MHF 提示词授权中继服务 (8.137.x.x 回源)      │
│  - pool-curator 定时器 (每 15 分钟解冷)        │
└──────────────────────┬───────────────────────┘
                       │ 内部安全通信 (Token 认证)
      ┌────────────────┼────────────────┐
      ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  五四云-620   │ │  五四云-621   │ │  小特云-待补  │
│  DSH Worker  │ │  DSH Worker  │ │  DSH Worker  │
│  rk620 进程  │ │  rk621 进程  │ │  工程员01    │
└──────────────┘ └──────────────┘ └──────────────┘
```

### 3.2 模式热切换与状态检测命令 (CLI Commands)

在任何安装了 MHF 环境的控制端，支持如下即时热切换：

```bash
# 1. 检查当前模式与授权状态
mh-switch status

# 2. 列出可用模式列表
mh-switch list

# 3. 切换至完全放行工程模式
mh-switch set general

# 4. 切换至本地自定义提示词
mh-switch set custom

# 5. 校验 upstream 网关连通性
curl -fsSL -H "Authorization: Bearer <GATEWAY_TOKEN>" http://156.225.28.106:7864/healthz
```

---

## 四、 防死锁与断网自愈策略 (Anti-Bug Runbook)

### 4.1 故障场景 A：上游网关连接拒绝 (Connection Refused)
- **触发表现**：Worker 日志高频刷 `claim_next 失败: Connection refused`，CPU 占满。
- **自愈机制**：
  1. 采用退避算法：初次失败等待 2s，二次等待 4s，最大退避 300s；
  2. 连续失败 10 次后，向本地落盘文件 `run/worker_suspended.lock` 写入故障标志，并暂停请求；
  3. 通过看门狗每 60 秒做一次轻量 HTTP HEAD 探测，检测到 `:7864` 恢复后秒级自动解挂。

### 4.2 故障场景 B：硬件指纹漂移导致授权校验失败
- **触发表现**：`authorizationIsFresh() == false`，所有模型请求直接报 `403 Current device is not authorized`。
- **排查与修复**：
  1. 检查 `MachineGuid` (Windows) 或 `/etc/machine-id` (Linux) 是否由于重装系统发生变更；
  2. 运行 `python ds-mh/tools/device_verify.py` 重新生成确定性散列；
  3. 执行授权绑卡指令：`POST /api/device/bind` 刷新本地 `MPC5` 凭证缓存。

### 4.3 故障场景 C：账号池并发排队阻塞 (首字延迟高)
- **排查步骤**：
  1. 检查网关机器的 `config.json` 中 `max_in_flight_global` 是否被死锁为 2；
  2. 动态调节：
     ```bash
     ssh root@156.225.28.106 "sed -i 's/max_in_flight_global: 2/max_in_flight_global: 64/' /opt/workbuddy2api-n11/config.yaml && systemctl restart wb2api-n11"
     ```
  3. 通过 `pool_curator.log` 确认可用账号并发数已跃升至 100+。

---

## 五、 验收标准与交付清单 (Acceptance Criteria)

1. [x] **架构物理落盘**：完整记录 MHF、dsh、注册充值及纯净环境架构至 `07_deepseek_and_model_hacker_architecture.md`；
2. [x] **协议加密对齐**：明确 X25519 ECDH + AES-256-GCM 与硬件指纹鉴权全流程；
3. [x] **防空转断路器**：消除无指挥中心情况下的无限暴力轮询，规范指数退避机制；
4. [x] **零外部依赖侵入**：`only-for-env` 规范保证所有节点可一键在纯净 Python 3.10 环境冷启动。
