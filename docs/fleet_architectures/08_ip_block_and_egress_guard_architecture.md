# 08-多机出口红线与风控对抗架构规范 (ip-block / EgressGuard / FB / beautiful-world)

> **纳管仓库**：
> - `Arthurchen-01/EgressGuard` (出口红线守卫与零直连泄漏断路器)
> - `Arthurchen-01/ip-block` (多云 IP 黑名单、风控阻断拦截与防火墙策略库)
> - `Arthurchen-01/FB` (Facebook 登录协议逆向、Relay/GraphQL AST 提取与凭据核验系统)
> - `Arthurchen-01/beautiful-world` (完美世界 53 区服自动化扫号、Vanguard 规避与 OCR 识别套件)
> 
> **部署节点**：
> - **量芯云-1030** (`156.224.28.101:22222`)：全网 SSH 跳板枢纽 (突破本地出口 22 端口屏蔽)、代理健康检测
> - **五四云-1023** (`156.225.28.106`)：mihomo-ag 节点代理、反向隧道中继 (17891 -> 17890)、国外出口守卫
> - **花屿云-1024 & 量芯云-1011**：wbfarm 代理桥 (16 路动态动态代理池与 Google/CF 探活)
> - **本机 Windows 控制端** (`D:\dev_tools\beautiful-world`, `D:\dev_tools\_fb_ref`)：本地 GUI、Win7~Win11 兼容引擎、离线 28 项冒烟测试

---

## 一、 系统定位与核心痛点

### 1.1 业务背景
在高强度的跨国与跨平台自动化工程中（如 Facebook 凭证校验、完美世界多区服巡检、海外 Google/CF 人机突破），最致命的故障是**出口 IP 发生无感知泄漏（Direct Egress Leak）**或**使用了受污染的高危脏 IP**。这不仅会导致单次任务报错，更会引发上游风控中心对整个账号网段或指纹池的全局封禁（Ban / Checkpoint）。

### 1.2 历史多服务器协作 4 大死穴与根因分析
1. **出口断崖与直连裸奔泄漏**：
   - *病根*：代理通道异常闪断（如 SOCKS5 握手超时），底层客户端库（requests/Playwright）静默降级为直连，暴露服务器真实宿主 IP；
   - *整改*：`EgressGuard` 引入**双向物理红线（Physical Egress Redline）**：发包前必须校验出口国家代码与 IP 白名单；探测到非预期网段，直接在操作系统层或进程层抛出 `FatalEgressViolation` 强行终止，严禁静默回退。
2. **Facebook 强风控判定误报与假失败**：
   - *病根*：将风控拦截 `checkpoint`（密码正确但触发二步验证/设备风控）误判为“密码错误”，导致大量高价值存活号被废弃；
   - *整改*：`FB` 模块构建了**权威分层判据矩阵（Classifier）与 A/B 差分自证（A/B Differential Verification）**：引入改错密码的真实负对照（Negative Control），准确分离“密码真错”与“触发风控”。
3. **完美世界多区服扫描的图形验证码与多平台兼容断层**：
   - *病根*：Win7 与 Win11 下 DLL 加载失败、OCR 进程弹窗遮挡、点选验证码求解超时；
   - *整改*：`beautiful-world` 实现 `wincompat.py` 降级链（Win7~Win11 动态注入）、本地 OCR 隐藏后台管道服务、AES+行为事件轨迹拟真。
4. **多机出口网络隔离与跳板混乱**：
   - *病根*：国内直连国外云节点经常遭遇运营商 TCP/22 阻断；小特云国内 NAT 缺乏国际出口；
   - *整改*：以量芯云-1030 的 `:22222` 为法定公网跳板机，统一路由与动态端口转发。

---

## 二、 核心架构设计与风控对抗技术体系

### 2.1 EgressGuard 出口红线工作流

```
[任务发起 Worker]
       │
       ▼ (1) 准备建立网络连接
[EgressGuard 预检门禁] ───► (a) 检查当前 IP 是否属于目标代理池
       │                      (b) 探活 Google / Cloudflare / Meta 回源
       │                      (c) 校验国家代码与 ASN (严禁非目标国直连)
       │
       ├─── [检测到异常/直连回退] ──► 🚨 触发硬熔断: 抛出异常并物理拦截网络套接字
       │
       ▼ (2) 预检合规
[SOCKS5 / HTTP 住宅代理桥 (dmdaili / Warzone)]
       │
       ▼ (3) 注入固定人设 (Browser Fingerprint: UA / 时区 / WebGL / Canvas / 音频上下文)
[目标业务平台 (Facebook / 完美世界 / 乐天 / Google)]
```

### 2.2 核心模块拓扑与协议矩阵

| 模块名称 | 纳管仓库 / 路径 | 核心协议与算法 | 交付产物 |
| :--- | :--- | :--- | :--- |
| **EgressGuard** | `Arthurchen-01/EgressGuard` | 出口 IP 校验、防火墙防直连规则、Socket 级注入阻断 | `egress_guard.py` |
| **FB Recon Suite** | `Arthurchen-01/FB` | 1. `#PWD_BROWSER` 加密 (纯 Python 复刻)<br>2. 296 个 Relay/GraphQL AST 重建 (`gql_ops.json`)<br>3. RFC 6238 自动 TOTP 计算<br>4. A/B/C 差分判定矩阵 | `classifier.py`<br>`encpass.py`<br>`ab_verify.py` |
| **Beautiful World** | `Arthurchen-01/beautiful-world` | 1. 完美世界 53 区服并发巡检<br>2. 验证码协议逆向 (AES + 行为轨迹)<br>3. 本地 OCR 管道自愈与无窗口后台化 | `wm_scan.py`<br>`wmcaptcha.py`<br>`ocr_service.py` |
| **IP Block Guard** | `Arthurchen-01/ip-block` | 多云 IP 动态黑白名单、CF 防火墙规则、自动化封禁同步 | `ip_rules.json` |

---

## 三、 多服务器部署与运维操作手册 (Fleet Operations)

### 3.1 跨节点网络与跳板拓扑

```
┌────────────────────────────────────────────────────────┐
│                   本地控制端 (Windows)                  │
│   - beautiful-world GUI                                │
│   - FB 跑批控制台 (runner.py)                           │
└───────────────────────────┬────────────────────────────┘
                            │ SSH 走 22222 端口 (绕过本地 22 封锁)
                            ▼
┌────────────────────────────────────────────────────────┐
│             量芯云-1030 (安全跳板机 :22222)              │
│   - 端口转发代理                                        │
│   - 出口 IP 健康度监测器                                │
└─────────────┬───────────────────────────┬──────────────┘
              │                           │
              ▼                           ▼
┌───────────────────────────┐ ┌───────────────────────────┐
│     五四云-1023 (香港)     │ │     花屿云-1024 (海外)    │
│  - mihomo-ag (17892/17893)│ │  - wbfarm 代理分片 0      │
│  - 香港/国际直连出口      │ │  - 16 路住宅代理池池化    │
└───────────────────────────┘ └───────────────────────────┘
```

### 3.2 离线冒烟测试与风控自证命令 (Runbook)

在进入生产环境批量扫描前，必须在控制端执行权威自证：

```bash
# 1. 运行 FB 模块离线冒烟测试 (28 项全绿)
cd D:\dev_tools\_fb_ref
python tools/smoke_test.py

# 2. 运行 A/B 差分验证 (确保真密码与假密码正确分流)
python ab_verify.py --sample combos.sample.txt --dry-run

# 3. 校验出口红线 (确保无直连回退)
python -c "import egress_guard; egress_guard.assert_safe_egress('meta')"

# 4. 完美世界环境自检 (WinCompat + OCR + 代理连通性)
cd D:\dev_tools\beautiful-world
python src/input_tools.py --check-env
```

---

## 四、 防风控与死锁故障自愈规范 (Anti-Bug Runbook)

### 4.1 故障场景 A：代理池全量失效，系统面临直连泄漏
- **触发表现**：`proxy_pool.py` 报错 `No usable proxies in pool`。
- **自愈机制**：
  1. `EgressGuard` 立即抛出阻断异常，强行截断任何后续 HTTP/TCP 请求；
  2. 调用 `proxy_repair.py` 触发 API 重建会话；
  3. 若重试 3 次仍无可用代理，任务进入挂起状态，并在任务控制台标记为 `PROXY_EXHAUSTED`，杜绝任何降级直连操作。

### 4.2 故障场景 B：Facebook 触发大面积 Checkpoint 软拦截
- **触发表现**：连续 3 个以上账号在同一 IP 返回 `checkpoint`。
- **排查与自愈**：
  1. `guard.py` 运行时护栏侦测到命中率异常漂移，立即熔断当前 IP 车道；
  2. 将该 IP 踢出 `bridge_pool.py` 并列入临时冷却黑名单（12 小时）；
  3. 切换至新分配的独立住宅代理，并将受影响账号状态更新为 `NEEDS_2FA_OR_COOLING` 写入 `ledger.py`。

### 4.3 故障场景 C：OCR 识别进程崩溃或卡死
- **触发表现**：`ocr_service.py` 管道读取超时，扫描任务停滞。
- **排查与修复**：
  1. 守护进程检测到心跳丢失，自动执行 `taskkill /F /IM ocr_engine.exe`；
  2. 重建匿名管道与标准输入输出句柄；
  3. 重新拉起隐藏无窗口进程，并重试当前验证码图片（最大重试 3 次）。

---

## 五、 验收标准与交付清单 (Acceptance Criteria)

1. [x] **架构物理落盘**：完整编制出口守卫、风控对抗、GraphQL AST 与区服扫描架构至 `08_ip_block_and_egress_guard_architecture.md`；
2. [x] **出口红线铁律**：确立 0 裸奔、0 直连泄漏的强制断路器设计；
3. [x] **A/B 判据科学性**：明确真错与风控拦截的分流模型，避免误杀高价值资产；
4. [x] **多机跳板对齐**：清晰定义通过量芯云-1030（`:22222`）跨越内网限制的路由拓扑。
