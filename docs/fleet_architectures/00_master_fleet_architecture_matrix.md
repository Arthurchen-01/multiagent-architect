# 🌐 全项目多机队架构主控总表 (Master Fleet Architecture Matrix)

> **审计与归档元数据**
> - **编制时间**：2026-10-07
> - **纳管范围**：用户账号 `Arthurchen-01` 旗下全部 **25 个 GitHub 代码仓库** + **9 台在用云服务器机队**
> - **定位**：解决多窗口、多服务器并发调度中的“人肉中继、代码漂移、并发竞争与反复修 Bug”问题，实现全自主规约驱动开发 (SDD)

---

## 一、 机队 13 台服务器总账与生命周期状态表 (9 台在用 / 4 台已过期)

| 机器命名 (旧编号) | 服务商 | 到期日 | 剩余天数 | 规格配置 | IP 与 SSH 端口 | 当前生产角色与端口 | 健康状态 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **五四云-1023** (551) | 五四云 | 10-23 | 16 天 | 16C16G/29G | `156.225.28.106:22` | **唯一 AI 核心网关** (wb2api :7864, Antigravity :8045/8046, 知乎站 :8775, CodeBuddy :7801) | 🟢 正常 (256 号池/107可用) |
| **花屿云-1024** (3883) | 花屿云 | 10-24 | 17 天 | 16C**32G**/97G | `154.219.105.203:22` | **任务指挥中心** (samurai-tc :8790) + wbfarm 分片0 (:8765) + 留学数据 (14G) | 🟡 /tmp 占用高 (需转储) |
| **五四云-620** (1030A) | 五四云 | 10-30 | 23 天 | 16C16G+**200G** | `156.225.28.208:22` | **Babra Replica 4000/54321** + 留痕台 (:8898) + wbfarm 跑号备用 | 🟢 正常 (挂载 200G 盘) |
| **五四云-621** (1030B) | 五四云 | 10-30 | 23 天 | 16C16G+**200G** | `156.225.28.4:22` | **乐天控制台 (:8791)** + `lt` 源站 (80/443) + wbfarm 跑号 + 密正 (:8899) | 🟢 正常 (域名 200 OK) |
| **五四云-1106** (657) ★ | 五四云 | 11-06 | **30 天** | 16C16G/30G+**200G** | `156.225.28.57:22` | **领英/FB反代控制台** (:8799) + **待建云端 DeepSeek Harness 公网服务台** | 🟢 正常 (负载 0.09, 14.5G空闲) |
| **量芯云-1011** (20013) | 量芯云 | 10-11 | **4 天** ⚠️ | 4C4G/39G | `154.94.225.214:22` | **wbfarm 分片 1** (:8765) + 闲鱼自动发货 (:8888) | 🔴 **急需续费** (钱包余额阻断) |
| **量芯云-1030** (19411) | 量芯云 | 10-30 | 23 天 | 4C8G/39G | `156.224.28.101:**22222**` | **Telegram 记账机器人** (:8080) + 订单系统 (:8888) + **全网安全跳板** | 🟢 正常 (独立 22222 端口) |
| **五四云-1021** (531) | 五四云 | 10-21 | 14 天 | 16C16G+**200G** | `156.225.28.62:22` | **词汇转写 vocab 源站** (:8765) + faster-whisper ASR + 乐天 7 分片采集矩阵 | 🟢 正常 (ASR 加速比 1.95x) |
| **小特云-待补** | 小特云 | 待面板查 | ? | 16C16G/29G | `103.236.91.189:**28807**` | **北京 NAT 大内存机**：Goo-Fish 闲鱼实时舱 (:3099) + CodeBuddy (:7801) | 🟢 正常 (盘占用降至 38%) |
| *量芯云-0928A* | 量芯云 | 09-28 | 已过期 | — | `156.225.31.92:22` | 旧网关 (7863) | ❌ 已隔离下线 |
| *量芯云-0928B* | 量芯云 | 09-28 | 已过期 | — | `103.52.152.37:22` | 空机可抛 | ❌ 已隔离下线 |
| *量芯云-0929* | 量芯云 | 09-29 | 已过期 | — | `38.76.174.32:22` | 原业务最重 (约 7GB 待冷备) | ❌ 已隔离待拉取数据 |
| *量芯云-1001* | 量芯云 | 10-01 | 已过期 | — | `162.211.180.242:22` | 密码需面板重置 | ❌ 待面板重置 |

---

## 二、 全项目架构规约库索引表 (Architectural Specifications Index)

用户项目全域共细分为 12 大多服务器架构规约与全景文档，均已物理落盘并完成结构化验证：

| 编号 | 架构规约文件与本地链接 | 核心纳管仓库 (GitHub) | 核心业务与抗 Bug 关键点 |
| :--- | :--- | :--- | :--- |
| **01** | [01_wb_international_architecture.md](file:///D:/multiagent-architect/docs/fleet_architectures/01_wb_international_architecture.md) | `Arthurchen-01/wb-international` | 根除 6 大死穴：60 分钟鲜度闸、FleetSync SHA-256 跨机对齐、浅克隆隔离、并发扩容、僵尸守护关闭、mihomo 独立化 |
| **02** | [02_samurai_admission_architecture.md](file:///D:/multiagent-architect/docs/fleet_architectures/02_samurai_admission_architecture.md) | `Arthurchen-01/samurai-admission`<br>`Arthurchen-01/us-admission-model`<br>`Arthurchen-01/00_aplication`<br>`Arthurchen-01/greydolphin` | 41.7 万份高校 HTML 结构化归档、3.0GB SQLite 分布式冷备、AI 对话中转地址纠偏、增量差分防重复抓取 |
| **03** | [03_telegram_accounting_bot_architecture.md](file:///D:/multiagent-architect/docs/fleet_architectures/03_telegram_accounting_bot_architecture.md) | Telegram 记账机器人 (`tg-bookkeeper`)<br>极速接单系统 (`order_system`) | 独立 22222 端口跳板隔离、Webhook 账本幂等哈希防重复记账、PM2 异常重启监控、SQLite WAL 锁保护 |
| **04** | [04_ai_token_gateway_7864_architecture.md](file:///D:/multiagent-architect/docs/fleet_architectures/04_ai_token_gateway_7864_architecture.md) | `wb2api-n11`<br>`pool-curator`<br>`antigravity` (8045/8046) | 256 账号池轮转调度、破除 `max_in_flight_global=2` 排队枷锁、mihomo-ag 脱离 Windows 本机、按 Token 信用动态解冷 |
| **05** | [05_vocab_transcription_and_rakuten_architecture.md](file:///D:/multiagent-architect/docs/fleet_architectures/05_vocab_transcription_and_rakuten_architecture.md) | `vocab_app`<br>`providers/asr_worker.py`<br>`rk055` 分片集群 | 五四云-1021 词汇源站 + faster-whisper 异步转写 (Unix Socket)、7 分片进程矩阵监控、DOCX 完整性校验 |
| **06** | [06_captcha_and_reverse_engineering_architecture.md](file:///D:/multiagent-architect/docs/fleet_architectures/06_captcha_and_reverse_engineering_architecture.md) | `Arthurchen-01/captcha`<br>`Arthurchen-01/wb-pj`<br>`Arthurchen-01/Special-for-Cloud-Server` | 完美世界 DLL 动态劫持、hCaptcha ONNX 本地推理 (5 组回归)、ASAR 逆向补丁、云端无显卡软渲染 Xvfb 管道 |
| **07** | [07_deepseek_and_model_hacker_architecture.md](file:///D:/multiagent-architect/docs/fleet_architectures/07_deepseek_and_model_hacker_architecture.md) | `Arthurchen-01/ds-mh`<br>`Arthurchen-01/ds-register-topup`<br>`Arthurchen-01/only-for-env` | Model Hacker Frame (MHF) 甲胄模式、X25519 ECDH+AES-256-GCM 动态提示词加密分发、硬件指纹鉴权、自动化注册充值 |
| **08** | [08_ip_block_and_egress_guard_architecture.md](file:///D:/multiagent-architect/docs/fleet_architectures/08_ip_block_and_egress_guard_architecture.md) | `Arthurchen-01/ip-block`<br>`Arthurchen-01/EgressGuard`<br>`Arthurchen-01/FB`<br>`Arthurchen-01/beautiful-world` | EgressGuard 出口红线断路器 (0直连泄漏)、Facebook 协议逆向 (`#PWD_BROWSER`+296 Relay AST)、53 区服扫号与 WinCompat 降级 |
| **09** | [09_ecommerce_and_social_scraping_architecture.md](file:///D:/multiagent-architect/docs/fleet_architectures/09_ecommerce_and_social_scraping_architecture.md) | `Arthurchen-01/rakuten-extract`<br>`Arthurchen-01/zhihu-scraper` | 乐天 Akamai 传感器绕过与确定性 `device_fp`、3 机分片矩阵 (1021/620/621)、知乎专栏与评论树深度爬取源站 (`:8775`) |
| **10** | [10_learning_and_content_engine_architecture.md](file:///D:/multiagent-architect/docs/fleet_architectures/10_learning_and_content_engine_architecture.md) | `Arthurchen-01/vocab`<br>`Arthurchen-01/zh-editor`<br>`Arthurchen-01/AP-Learning-Web`<br>`Arthurchen-01/AP-Learning-Web-01`<br>`Arthurchen-01/ap-tracker`<br>`Arthurchen-01/study-pod` | 日语初学者沉浸式听力句型分析（进击的巨人 S1 音轨对齐）、faster-whisper 1.95x 加速比、DOCX/TXT/MD 导出、AP 课程打卡 |
| **11** | [11_multiagent_and_tooling_matrix_architecture.md](file:///D:/multiagent-architect/docs/fleet_architectures/11_multiagent_and_tooling_matrix_architecture.md) | `Arthurchen-01/three-agent-runtime-template`<br>`Arthurchen-01/my-ai-tools`<br>`Arthurchen-01/stock-shanzhang`<br>`Arthurchen-01/Heart-Beat-War--3.28`<br>`Arthurchen-01/achievements`<br>`Arthurchen-01/fighting-achievement`<br>`Arthurchen-01/could-coding`<br>`Arthurchen-01/chromebook-dragonfly-drive`<br>`Arthurchen-01/project-designs` | 三智能体协同闭环 (工程师-评审员-仲裁员)、规约驱动开发 (SDD)、缠论量化指标计算、游戏化成就激励、Chromebook 云开发桥接 |
| **12** | [12_fleet_live_scripts_and_process_matrix.md](file:///D:/multiagent-architect/docs/fleet_architectures/12_fleet_live_scripts_and_process_matrix.md) | 全机队 9 台在用活跃服务器 | 2026-10-07 逐台内核真机探活：常驻脚本、运行进程、监听端口、Cron 定时任务、数据盘与 `/opt/` 目录全景总表 |

---

## 三、 用户全量 25 个 GitHub 仓库多机队拓扑映射表

| # | 仓库名称 (Arthurchen-01) | 业务领域 | 核心文件 / 模块 | 主要运行节点 | 所属架构规约 |
|---|---|---|---|---|---|
| 1 | **`multiagent-architect`** | 顶层中枢 | `core/` (状态机/仲裁/真核证据), `.spec/`, `cli/` | 控制端 Windows / 全机队 | [11_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/11_multiagent_and_tooling_matrix_architecture.md) |
| 2 | **`wb-international`** | 账号工程 | `account_store.py`, `_guard.sh`, `_autopilot.py` | 五四云-1030A, 1030B, 量芯云-1011 | [01_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/01_wb_international_architecture.md) |
| 3 | **`samurai-admission`** | 留学爬虫 | `crawl_pipeline.py`, `sqlite_backup.py`, `.env.local` | 花屿云-1024, 五四云-1023 | [02_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/02_samurai_admission_architecture.md) |
| 4 | **`us-admission-model`** | 录取建模 | `model_eval.py`, `data_pipeline.py` | 花屿云-1024, 小特云-待补 | [02_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/02_samurai_admission_architecture.md) |
| 5 | **`00_aplication`** | 申请管理 | `form_engine.py`, `audit_report.py` | 花屿云-1024 | [02_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/02_samurai_admission_architecture.md) |
| 6 | **`greydolphin`** | 留学中台 | `proxy_bridge.py`, `dolphin_sync.py` | 花屿云-1024 | [02_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/02_samurai_admission_architecture.md) |
| 7 | **`captcha`** | 人机突破 | `onnx_models/`, `hcaptcha_breaker.py`, `solve.py` | 本机 Windows, 五四云-1030A | [06_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/06_captcha_and_reverse_engineering_architecture.md) |
| 8 | **`wb-pj`** | 客户端逆向 | `asar_patch.py`, `wmrecon.py`, `hook.js` | 本机 Windows, 五四云-1023 | [06_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/06_captcha_and_reverse_engineering_architecture.md) |
| 9 | **`Special-for-Cloud-Server`** | 云端适配 | `xvfb_setup.sh`, `cloud_patch.py` | 五四云-1030A, 五四云-1030B | [06_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/06_captcha_and_reverse_engineering_architecture.md) |
| 10 | **`ds-mh`** | 提示词甲胄 | `plugin/`, `lib/client.js`, `settings.json` | 五四云-1023, 本机 Windows | [07_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/07_deepseek_and_model_hacker_architecture.md) |
| 11 | **`ds-register-topup`** | 自动充值 | `register.py`, `topup_flow.py`, `token_gen.py` | 五四云-1023, 量芯云-1030 | [07_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/07_deepseek_and_model_hacker_architecture.md) |
| 12 | **`only-for-env`** | 纯净环境 | `sandbox_init.sh`, `deps_lock.json` | 全机队节点 | [07_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/07_deepseek_and_model_hacker_architecture.md) |
| 13 | **`ip-block`** | 网络安全 | `ip_rules.json`, `cf_firewall_sync.py` | 全机队节点 | [08_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/08_ip_block_and_egress_guard_architecture.md) |
| 14 | **`EgressGuard`** | 出口红线 | `egress_guard.py`, `test_leak.py` | 全机队节点 | [08_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/08_ip_block_and_egress_guard_architecture.md) |
| 15 | **`FB`** | 协议逆向 | `classifier.py`, `encpass.py`, `relay_ops.py` | 本机 Windows, 量芯云-1030 | [08_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/08_ip_block_and_egress_guard_architecture.md) |
| 16 | **`beautiful-world`** | 完美世界 | `src/wm_scan.py`, `wmcaptcha.py`, `wincompat.py` | 本机 Windows | [08_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/08_ip_block_and_egress_guard_architecture.md) |
| 17 | **`rakuten-extract`** | 电商采集 | `probe_akamai.py`, `probe_client_fp.py`, `runner.py` | 五四云-1021, 620, 621 | [09_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/09_ecommerce_and_social_scraping_architecture.md) |
| 18 | **`zhihu-scraper`** | 社交抓取 | `scraper_api.py`, `playwright_stealth.js` | 五四云-1023 (:8775) | [09_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/09_ecommerce_and_social_scraping_architecture.md) |
| 19 | **`vocab`** | 听力学习 | `server.py`, `providers/asr_worker.py` | 五四云-1021 (:8765) | [10_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/10_learning_and_content_engine_architecture.md) |
| 20 | **`zh-editor`** | 内容排版 | `editor_core.js`, `furigana_plugin.js` | 静态分发 / 本地 | [10_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/10_learning_and_content_engine_architecture.md) |
| 21 | **`AP-Learning-Web`** | 课程门户 | `pages/`, `components/CoursePlayer.jsx` | 前端集群托管 | [10_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/10_learning_and_content_engine_architecture.md) |
| 22 | **`AP-Learning-Web-01`**| 课程分支 | `app/`, `components/TrackView.tsx` | 前端集群托管 | [10_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/10_learning_and_content_engine_architecture.md) |
| 23 | **`ap-tracker`** | 学习追踪 | `tracker_service.py`, `ebbinghaus.py` | 五四云-1021 / 本地 | [10_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/10_learning_and_content_engine_architecture.md) |
| 24 | **`study-pod`** | 协作学习舱 | `pod_server.js`, `sync_board.js` | 小特云-待补 / 本地 | [10_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/10_learning_and_content_engine_architecture.md) |
| 25 | **`three-agent-runtime-template`** | 多智能体模板 | `arbiter.py`, `engineer.py`, `reviewer.py` | 全机队节点 | [11_架构规约](file:///D:/multiagent-architect/docs/fleet_architectures/11_multiagent_and_tooling_matrix_architecture.md) |

---

## 四、 跨系统协同 5 大刚性防御原则 (Fleet Anti-Bug Invariants)

1. **绝对禁止代码单节点手工热修（Zero-Ad-hoc Patching）**：
   - 任何代码修复必须在本机或分支工作区编写，通过 `python tests/run_tests.py` 全绿通过后，方可通过 Git 或同步脚本下发；
   - 跨节点发布必须使用 `FleetSync` 核验各节点的 `SHA-256` 绝对对齐，彻底斩断“1011 跑着 4 天前旧代码”的代码漂移死穴。
2. **状态物理外挂与排他认领锁（Atomic Task Claiming）**：
   - 多窗口与跨机执行必须遵循 `tasks/pending/` ➔ `tasks/running/<worker>-<task>.md` 状态机重命名协议；
   - 严禁多个 worker 不加锁同时读取和争抢同一账号/任务。
3. **鲜度闸与排队背压机制（Freshness Gate & Backpressure）**：
   - 任何带有外部生命周期的资源（如 yx-mail 短命号、临时 Token、验证码），入库必须强制携带 `bought_at` 毫秒级时间戳；
   - 超过鲜度窗口（60分钟）自动熔断阻断，进货速度必须严格受限于下游消化速度。
4. **真核执行证据链留痕（Proof-of-Execution）**：
   - 远程节点汇报执行成功，必须随单附带 `CF-RAY` / `Date` 外部凭据、原始报文 `SHA-256`、真实渲染快照及 `/proc` 网络连接记录；
   - 杜绝 AI 在中间由于超时返回空壳 `{"ok": false, status: null}` 或伪造假数据。
5. **出口红线零泄漏守卫（Egress Redline Invariant）**：
   - 任何网络请求发起前必须经由 `EgressGuard` 校验出口 IP 归属；
   - 代理通道异常时绝对禁止静默回退至服务器本机或本地直连网络，宁可抛错阻断，不可暴露真实宿主。
