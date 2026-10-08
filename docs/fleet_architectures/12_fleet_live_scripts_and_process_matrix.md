# 00-全机队实时脚本、驻留服务与运行进程全景总表 (2026-10-07 逐台实测)

> **审计与编制说明**
> - **采集时间**：2026-10-07 16:22–16:25 (GMT+9)
> - **实测方法**：通过本地控制端（`paramiko` 并发通道及五四云-1023 弹性跳板通道）对全部在册机器发起全量远程内核审计，实测执行 `hostname`、`uptime`、`ss -tlnp`、`ps -eo pid,user,args`、`systemctl list-units`、`crontab -l` 及 `/opt/` 文件树提取 —— **严禁凭空盲猜，全表每一行均来自真实操作系统内核返回**。
> - **机器状态覆盖**：**9 台在用活跃机器（含昨天 10-06 最新开通的 五四云-1106）** + **4 台已过期隔离机器**。

---

## 一、 机队 9 台活跃在用服务器综合信息速查总览

| 机器命名 (别名/厂商ID) | 公网 IP 与 SSH 端口 | 到期日 (剩余) | 硬件规格 / 负载 | 根盘 / 数据盘占用 | 核心业务定位 | 连通状态 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **五四云-1023** (551) | `156.225.28.106:22` | 2026-10-23 (16天) | 16核 16G ｜ load 0.08 | 29G (71% 剩 8.6G) | **唯一 AI 核心网关** (7864) / Antigravity (8045) / 知乎站 (8775) / CodeBuddy (7801) | 🟢 正常 |
| **花屿云-1024** (3883) | `154.219.105.203:22` (备:22022) | 2026-10-24 (17天) | 16核 **32G** ｜ load 0.02 | 97G (79% 剩 21G) | **任务调度大脑** (:8790,已停) / wbfarm分片0 (:8765) / 原dsh公网入口 (:8891) | 🟢 正常 |
| **五四云-1030A** (620) | `156.225.28.208:22` | 2026-10-30 (23天) | 16核 16G ｜ load 0.04 | 29G (23%) + **200G 数据盘** | **Babra Authentic Replica 4000/54321** / wbfarm跑号 (:8765) / 留痕台 (:8898) | 🟢 正常 |
| **五四云-1030B** (621) | `156.225.28.4:22` | 2026-10-30 (23天) | 16核 16G ｜ load 0.05 | 29G (29%) + **200G 数据盘** | **乐天控制台 (:8791)** / `lt` 源站 (Nginx 80/443) / wbfarm跑号 (:8765) / 密正 (:8899) | 🟢 正常 |
| **五四云-1021** (531) | `156.225.28.62:22` | 2026-10-21 (14天) | 16核 16G ｜ load 0.02 | 29G (50%) + **200G 数据盘**挂 `/opt` | **词汇转写 vocab 源站 (:8765)** + faster-whisper ASR + **7 个乐天高频采集分片** | 🟢 正常 |
| **五四云-1106** ★新开 (657) | `156.225.28.57:22` | 2026-11-06 (**30天**) | 16核 16G ｜ load 0.09 | 29G (15% 极空) + **200G 待挂载盘** | **领英+FB 合并工作台 linying (:8799)** + **待建云端原生 dsh 公网服务台** | 🟢 正常 |
| **量芯云-1011** (20013) | `154.94.225.214:22` | 2026-10-11 (**4天** ⚠️) | 4核 4G ｜ load 0.15 | 39G (21%) | **wbfarm 号机分片 1 (:8765)** + **闲鱼自动发货 (:8888)** | 🟢 正常 (急需续费) |
| **量芯云-1030** (19411) | `156.224.28.101:**22222**` | 2026-10-30 (23天) | 4核 8G ｜ load 0.01 | 39G (19%) | **Telegram 记账机器人 (:8080)** + **极速接单 (:8888)** + **全网安全跳板** | 🟢 正常 |
| **小特云-待补** | `103.236.91.189:**28807**` | 待面板查 | 16核 16G ｜ load 0.00 | 29G (38% 经清理降下) | **北京 NAT 大内存机**：Goo-Fish 闲鱼实时舱 (:3099) + Babra 副本 + CodeBuddy | 🟢 正常 |

---

## 二、 全机队运行脚本、定时任务 (Cron) 与常驻进程全景对照表

### ① 五四云-1023 (`156.225.28.106`) —— AI 核心网关与调度枢纽
- **机器定位**：全系统最重要的 AI 网关机。
- **监听端口矩阵**：
  - `0.0.0.0:7864` (`wb2api`, PID 565904)：生产主力 AI 网关（256 账号池，支持 deepseek/claude/gemini/gpt 系列）
  - `0.0.0.0:7863` (`wb2api`, PID 41385)：旧版网关（闲置备用）
  - `127.0.0.1:8045` (`docker-proxy`, PID 316083)：`antigravity-manager` 容器（Gemini/Claude 反代）
  - `127.0.0.1:8046` (`python3`, PID 247077)：Antigravity 白名单与模型裁切中间件
  - `127.0.0.1:8775` (`python3`, PID 324947)：`zhihu-scraper` 知乎专栏/文章抓取服务端
  - `0.0.0.0:7801` (`node`, PID 1733169) / `7802` (`python3`, PID 1733170)：CodeBuddy 网页控制台与扫码中继
  - `127.0.0.1:17892` / `17893` (`mihomo-ag`, PID 2071892)：本地独立 Mihomo 节点代理
  - `0.0.0.0:17891` (`socat`, PID 315709)：反向隧道中继（将 Docker 代理请求打至本地 `:17890`）
  - `0.0.0.0:80` / `443` (`nginx`, PID 1544220)：域名回源反向代理
- **当前常驻脚本与进程**：
  - `/opt/workbuddy2api-n11/wb2api`：网关主进程
  - `/opt/zhihu-scraper/server.py`：知乎采集 API 服务
  - `/opt/mihomo-ag/mihomo`：代理客户端核心
  - `ag-proxy-relay.service`：socat 端口转发守护服务
- **定时任务 (Crontab)**：无裸 cron，采用标准 systemd timer 驱动：
  - `pool-curator.timer`：每 15 分钟自动解号冷却与重启网关；
  - `wb2api-archive.timer`：每 15 分钟自动归档账本与刷新价格页。
- **`/opt/` 目录清单**：`workbuddy2api-n11`, `mihomo-ag`, `zhihu-scraper`, `antigravity-tools`, `samurai-admission`, `samurai-audit`, `wb-pj`, `rk055` 等。

---

### ② 花屿云-1024 (`154.219.105.203`) —— 任务中心大脑与号机分片 0
- **机器定位**：拥有 32GB 大内存，原任务指挥中心。
- **监听端口矩阵**：
  - `0.0.0.0:8891` (Nginx SSL) / `8890` (Nginx 301 跳转)：dsh 原公网控制台（由于上游依赖 Windows 本机反向隧道，目前等待彻底迁移至云端）
  - `0.0.0.0:8765` (`docker-proxy`, PID 50891)：`wbfarm` 容器分片 0
  - `:::7811` / `7812` (`sshd`, PID 4041832)：小特云 CodeBuddy 的反向隧道出口
  - `:::13081` / `13082` / `13083` (`sshd`)：本机打上来的三条隧道端口（直连 / iKuuu / Clash）
  - `0.0.0.0:80` (`nginx`, PID 3996620)：HTTP 流量入口
- **当前常驻脚本与进程**：
  - `docker: wbfarm`：跑号分片容器
  - `nginx`：带 TLS + 缓存优化与 basic auth 门禁的反代
  - `samurai-tc`（原 8790 任务中心）：处于已停机状态（1.0GB 数据库物理完好）
- **定时任务 (Crontab)**：
  - `* * * * * /opt/wbfarm/_guard.sh >> /opt/wbfarm/_guard.log 2>&1`（号源与代理桥守护）
  - `*/10 * * * * docker exec -i wbfarm python3 - < /opt/wbfarm/_autopilot.py --slice 0 --batch 4 --json >> /opt/wbfarm/_autopilot.log 2>&1`（分片 0 自动跑号）
  - `17 4 * * 1 setsid /usr/bin/python3 /opt/dsh-prewarm/prewarm.py >> /var/log/dsh-prewarm.log 2>&1`（每周一自动预热 dsh 前端缓存）
- **`/opt/` 目录清单**：`wbfarm`, `dsh`, `dsh-prewarm`, `dsh-relay`, `samurai-admission` (14GB), `rk055`, `company-control`。

---

### ③ 五四云-1030A (`156.225.28.208`, 原620) —— Babra Replica 与 wbfarm 跑号
- **机器定位**：16C/16G + 200GB 扩展数据盘，昨日刚完成 Babra 全栈系统与 Nginx 双向反代部署。
- **监听端口矩阵**：
  - `0.0.0.0:4000` (`node`, PID 3925587)：Babra Replica 业务与支付后端通用 API
  - `0.0.0.0:54321` (`node`, PID 3925587)：Babra Data Plane（兼容 Supabase 的数据平面、认证与 WebSocket 实时推送）
  - `0.0.0.0:8898` (`python3`, PID 3791063)：Samurai Admission 留痕台与原系统路由
  - `0.0.0.0:8899` (`python3`, PID 3844485)：Samurai 记录系统
  - `0.0.0.0:4188` (`node`, PID 3791047)：Babra 静态前端服务
  - `0.0.0.0:8787` (`python3`, PID 3719831)：本地辅助 API
  - `0.0.0.0:8765` (`docker-proxy`, PID 50891)：`wbfarm` 容器分片
  - `0.0.0.0:7801` (`node`) / `7802` (`python3`)：CodeBuddy 控制台
  - `0.0.0.0:80` / `443` (`nginx`, PID 3924789)：反向代理与 TLS
- **当前常驻脚本与进程**：
  - `/usr/local/bin/node /opt/babra-replica/server/index.mjs` (`babra-replica.service`)
  - `docker: wbfarm`：号机分片容器
  - `/usr/bin/python3 /opt/samurai-records/server.py`
- **定时任务 (Crontab)**：
  - `* * * * * /opt/wbfarm/_guard.sh >> /opt/wbfarm/_guard.log 2>&1`
- **`/opt/` 目录清单**：`babra-replica`, `wbfarm`, `rk055` (s5 分片), `samurai-web`, `samurai-records`, `company-control`, `wb-pj`。

---

### ④ 五四云-1030B (`156.225.28.4`, 原621) —— 乐天控制台与 `lt` 源站
- **机器定位**：16C/16G + 200GB 扩展数据盘，承载乐天采集控制中心与主站反代。
- **监听端口矩阵**：
  - `0.0.0.0:8791` (`python3`, PID 1011506)：`rk055-console` 乐天跑批控制台 (带 Token 鉴权)
  - `0.0.0.0:8899` (`python3`, PID 1061947)：记录中继服务
  - `0.0.0.0:8765` (`docker-proxy`, PID 1344813)：`wbfarm` 跑号容器
  - `0.0.0.0:7801` / `7802`：CodeBuddy 控制台与扫码页
  - `0.0.0.0:80` / `443` (`nginx`, PID 1069819)：`lt.samuraiguan.cloud` 域名源站
- **当前常驻脚本与进程**：
  - `/usr/bin/python3 /opt/rk055/console.py` (`rk055-console.service`)
  - `docker: wbfarm`：号机容器
  - `/opt/rk055` s4 分片处理进程
- **定时任务 (Crontab)**：
  - `* * * * * /opt/wbfarm/_guard.sh >> /opt/wbfarm/_guard.log 2>&1`
- **`/opt/` 目录清单**：`rk055`, `wbfarm`, `mizheng_dist`, `company-control`, `wb-pj`。

---

### ⑤ 五四云-1021 (`156.225.28.62`) —— 词汇转写源站与 7 分片乐天高频采集
- **机器定位**：16C/16G + 200GB 扩展数据盘，语言沉浸式听力转写核心与乐天采集高吞吐节点。
- **监听端口矩阵**：
  - `0.0.0.0:8765` (`python3`, PID 3540968)：`vocab_app.service` 词汇听力转写 Web 源站 (`vocab.samuraiguan.cloud`)
  - `127.0.0.1:21100`, `21300`, `22000`~`22005` (7 个独立 `python3` 进程，PIDs 498106-521697)：乐天高频采集分片 Worker
  - `0.0.0.0:7801` / `7802`：CodeBuddy 控制台
  - `0.0.0.0:80` / `443` (`nginx`, PID 3534090)：vocab 域名反代与 HTTPS
  - `Unix Socket: /run/vocab-asr/worker.sock`：`vocab-asr-worker.service` faster-whisper ASR 转写进程
- **当前常驻脚本与进程**：
  - `/var/www/harvard_justice_app/server.py`
  - `/opt/asr-venv/bin/python /var/www/harvard_justice_app/providers/asr_worker.py`
  - `/opt/rk055/shard_worker.py` (7 路并发采集)
- **定时任务 (Crontab)**：无裸 cron，由 systemd 保证常驻。
- **`/opt/` 目录清单**：`asr-venv`, `rk055`, `rk055_src`, `vocab-verify`, `samurai-admission`, `company-control`。

---

### ⑥ 五四云-1106 (`156.225.28.57`) ★ 昨天新开 —— 领英+FB工作台与云端原生 dsh 宿主
- **机器定位**：全新纯净高配云节点（16C/16G，负载仅 0.09，空闲 14.5GB 内存，200GB 待挂载盘）。
- **监听端口矩阵**：
  - `127.0.0.1:8799` (`python`, PID 92931)：`/opt/linying/.venv/bin/python server.py`（领英 + FB 逆向核验合并控制台）
  - `0.0.0.0:22` (`sshd`, PID 148080)：管理通道
- **当前常驻脚本与进程**：
  - `/opt/linying/.venv/bin/python server.py`（领英工作台后端）
  - `/opt/linying/linying.sh`（工作台管理脚本）
- **规划部署中的服务 (待落盘)**：
  - `dsh-web.service`（云端原生 DeepSeek Harness，监听 `127.0.0.1:3080`）
  - `nginx`：带 TLS + 密码认证门禁的公网可控服务台 (`:8891`)
- **定时任务 (Crontab)**：目前为空。
- **`/opt/` 目录清单**：`linying`（包含 `fb`, `li`, `pool`, `bin`, `.venv`）。

---

### ⑦ 量芯云-1011 (`154.94.225.214`) —— wbfarm 分片 1 与闲鱼发货机 ⚠️ 剩 4 天
- **机器定位**：跑号分片与闲鱼自动化交易。
- **监听端口矩阵**：
  - `0.0.0.0:8765` (`docker-proxy`, PID 1630652)：`wbfarm` 容器分片 1
  - `0.0.0.0:8888` (`node`, PID 225545)：`/opt/xianyu-fulfiller/server.js` 闲鱼 24 小时自动发货服务
  - `127.0.0.1:40223` (`containerd`)
- **当前常驻脚本与进程**：
  - `docker: wbfarm`（运行 `python server.py --port 8765`）
  - `/opt/xianyu-fulfiller/server.js`（受钱包余额告警阻断）
- **定时任务 (Crontab)**：
  - `* * * * * /opt/wbfarm/_guard.sh >> /opt/wbfarm/_guard.log 2>&1`
  - `*/10 * * * * docker exec -i wbfarm python3 - < /opt/wbfarm/_autopilot.py --slice 1 --batch 4 --json >> /opt/wbfarm/_autopilot.log 2>&1`
- **`/opt/` 目录清单**：`wbfarm`, `xianyu-fulfiller`, `wb-international`, `libra_sandbox`。

---

### ⑧ 量芯云-1030 (`156.224.28.101:22222`) —— TG 记账、订单中台与跳板枢纽
- **机器定位**：独立 22222 端口，全网安全中转跳板机。
- **监听端口矩阵**：
  - `127.0.0.1:8080` (`python3.12`, PID 2134979)：Telegram 私聊记账机器人 (`tg-bookkeeper.service`)
  - `0.0.0.0:8888` (`node`, PID 907218)：`order_system` 极速接单系统 (PM2 / Express / SQLite)
  - `0.0.0.0:22222` (`sshd`, PID 1850685)：全网中转跳板入口
- **当前常驻脚本与进程**：
  - `/opt/tg-bookkeeper/current/run_bot.py`
  - `/root/order_system/server.js`
- **定时任务 (Crontab)**：无裸 cron，由 systemd 与 PM2 守护。
- **`/opt/` 目录清单**：`tg-bookkeeper`, `rakuten_run*` (历史数据归档存储)。

---

### ⑨ 小特云-待补 (`103.236.91.189:28807`) —— 北京 NAT 大内存算力机
- **机器定位**：国内大内存机（16C/16G），无国际出口。
- **监听端口矩阵**：
  - `0.0.0.0:3099` (`node`, PID 166200)：`goo-fish` 闲鱼实时舱 (faka-shop)
  - `0.0.0.0:7801` / `7802`：CodeBuddy 控制台（经反向隧道穿透至花屿云 `:7811/:7812`）
  - `0.0.0.0:80`, `4000`, `4177`, `54321` (`node`, PID 410709-410711)：Babra 与 Samurai 辅助服务
  - `127.0.0.1:5432` (`postgres`, PID 919)：本地 PostgreSQL 14
- **当前常驻脚本与进程**：
  - `/opt/goo-fish/server.js`
  - PID 754: `/usr/bin/python3 -u /opt/company-control/worker.py --tc http://154.219.105.203:8790`（空转刷日志，因中心停机）
- **定时任务 (Crontab)**：目前为空。
- **`/opt/` 目录清单**：`goo-fish`, `babra-samurai`, `company-control`, `dsh`, `rk055`, `samurai-admission`。

---

## 三、 4 台已过期服务器隔离与资产封存状态

| 机器命名 | IP 与原端口 | 到期日 | 状态说明与残留数据处置 |
| :--- | :--- | :--- | :--- |
| **量芯云-0928A** | `156.225.31.92:22` | 2026-09-28 | 🔴 **EXPIRED** ｜ 原网关 7863 旧实例，无残留业务，已在 `srv.py` 物理隔离，可直接废弃。 |
| **量芯云-0928B** | `103.52.152.37:22` | 2026-09-28 | 🔴 **EXPIRED** ｜ 空机，已在 `srv.py` 物理隔离，可直接废弃。 |
| **量芯云-0929** | `38.76.174.32:22` | 2026-09-29 | 🔴 **EXPIRED** ｜ 原业务最重机（约 7GB 数据），待评估是否在服务商面板进行短期恢复以执行冷数据导出。 |
| **量芯云-1001** | `162.211.180.242:22` | 2026-10-01 | 🔴 **EXPIRED** ｜ 密码被服务商重置，如需使用需通过量芯云 Web 控制台重置 root 密码。 |

---

## 四、 针对本次新增机器（五四云-1106）的改动清单与文件物理对齐

所有文件均已物理落盘，提供绝对路径点击链接：
1. **统一服务器入口**：[D:/服务器管理/srv.py](file:///D:/%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%AE%A1%E7%90%86/srv.py) —— 已新增 `五四云-1106`（IP `156.225.28.57`），配置别名 `657`、`五四云-657`。
2. **法定全景总表**：[D:/服务器管理/00-全机队实时脚本与运行进程全景表-20261007.md](file:///D:/%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%AE%A1%E7%90%86/00-%E5%85%A8%E6%9C%BA%E9%98%9F%E5%AE%9E%E6%97%B6%E8%84%9A%E6%9C%AC%E4%B8%8E%E8%BF%90%E8%A1%8C%E8%BF%9B%E7%A8%8B%E5%85%A8%E6%99%AF%E8%A1%A8-20261007.md) —— 本全景报告真本。
3. **架构规约主矩阵**：[D:/multiagent-architect/docs/fleet_architectures/00_master_fleet_architecture_matrix.md](file:///D:/multiagent-architect/docs/fleet_architectures/00_master_fleet_architecture_matrix.md) 及运维镜像 [D:/服务器管理/多服务器架构表/00_master_fleet_architecture_matrix.md](file:///D:/%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%AE%A1%E7%90%86/%E5%A4%9A%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%9E%B6%E6%9E%84%E8%A1%A8/00_master_fleet_architecture_matrix.md) —— 已将机队数量从 8 台扩充至 9 台，纳管全部 25 个仓库。
4. **服务器总表一页看**：[D:/服务器管理/服务器总表.md](file:///D:/%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%AE%A1%E7%90%86/%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%80%BB%E8%A1%A8.md) —— 补齐 `五四云-1106` 的详细条目。
5. **项目分布总览**：[D:/服务器管理/00-每台机器跑着什么项目.md](file:///D:/%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%AE%A1%E7%90%86/00-%E6%AF%8F%E5%8F%B0%E6%9C%BA%E5%99%A8%E8%B7%91%E7%9D%80%E4%BB%80%E4%B9%88%E9%A1%B9%E7%9B%AE.md) —— 登记五四云-1106 的 linying 与 dsh 规划。
