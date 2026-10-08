# 10-沉浸式语言学习与内容引擎架构规范 (vocab / zh-editor / AP-Learning-Web / ap-tracker / study-pod)

> **纳管仓库**：
> - `Arthurchen-01/vocab` (哈佛公正课与《进击的巨人》沉浸式听力词汇转写站)
> - `Arthurchen-01/zh-editor` (多语言富文本排版、句法语法标注与内容编辑器)
> - `Arthurchen-01/AP-Learning-Web` & `Arthurchen-01/AP-Learning-Web-01` (AP 国际课程沉浸式学习门户系统)
> - `Arthurchen-01/ap-tracker` (学习进度、任务里程碑与多维量化打卡追踪器)
> - `Arthurchen-01/study-pod` (分布式协作学习舱与知识库同步运行时)
> 
> **部署节点**：
> - **五四云-1021** (`156.225.28.62`)：词汇转写源站主控 (`:8765` -> `vocab.samuraiguan.cloud`) + 本地 faster-whisper ASR Worker (Unix Socket: `/run/vocab-asr/worker.sock`)
> - **五四云-1023** (`156.225.28.106`)：AI 大模型辅助词汇释义与语法解析服务 (`:7864`)
> - **花屿云-1024** (`154.219.105.203`)：音频原文件与 DOCX 成果包分布式冷备存储
> - **本机 Windows 控制端** (`D:\vocab`, `D:\SAMURAI_留学系统_项目总控`)：本地语音分析测试、教材导入与界面调试

---

## 一、 系统定位与用户学习画像

### 1.1 业务背景与用户学习目标
用户是**日语初学者**，当前的核心学习方式是通过**《进击的巨人》第一季（進撃の巨人 S1）**进行动漫沉浸式日语词汇与听力句子的学习，同时结合经典公开课（如哈佛公正课 Justice）进行双语深度理解。本系统是一套端到端的**多模态音频转写、时间戳对齐、生词提取、句法分析与多端渲染平台**。

### 1.2 历史多服务器协作 4 大死穴与根因分析
1. **ASR 长音频阻塞主线程与 Web 服务超时**：
   - *病根*：早期直接在 Web 请求线程中调用 Whisper 模型，7 分钟音频导致 HTTP 请求挂死 200+ 秒，Nginx 报 504 Gateway Timeout；
   - *整改*：架构重构为**独立 Unix Socket 异步工作进程（`vocab-asr-worker.service`）**，Web 端秒级返回 Job ID，前端通过轮询或 SSE 监听转写进度，实测 1.95x 离线转写加速比。
2. **导出的 DOCX 格式损坏（假 OOXML 包）**：
   - *病根*：早期导出脚本直接把 HTML 文本保存为 `.docx` 扩展名，导致 Word 打开报“文件已损坏”；
   - *整改*：引入基于 `python-docx` 的严格 OOXML 打包规范，必须通过 `zipfile.testzip()` 完整性校验，包含带时间戳的段落与表格排版。
3. **多语言编码乱码（Windows GBK 与 Linux UTF-8 冲突）**：
   - *病根*：日文假名（如「駆逐してやる」）与特殊音标在跨服务器传输中发生二次转码乱码；
   - *整改*：全局强制落实 UTF-8 编码约束，数据库连接与文件读写强制指定 `encoding="utf-8"`。
4. **多端学习进度脱节与静态资源割裂**：
   - *病根*：`AP-Learning-Web` 前端与 `ap-tracker` 后端状态不同步，学习进度卡片无法实时更新；
   - *整改*：标准化 RESTful / GraphQL API 接口契约，通过 SQLite / PostgreSQL 统一持久化打卡流水。

---

## 二、 核心架构设计与处理流水线

### 2.1 音频转写与词汇提取流水线 (ASR & Vocab Pipeline)

```
[用户上传 MP3 / 动漫原声音轨 (進撃の巨人 S1)]
       │
       ▼ (1) POST /api/asr/job (上传音频文件)
[vocab_app (五四云-1021:8765)]
       │
       ├─► (2) 写入作业元数据并下发任务至 Unix Socket (/run/vocab-asr/worker.sock)
       │
       ▼ (3) 异步执行
[vocab-asr-worker (faster-whisper small 模型)]
       │
       ├─► (a) VAD 语音活动检测 (切分静音片段)
       ├─► (b) 逐字逐句生成带精确毫秒时间戳的字幕片段
       ├─► (c) 调用五四云-1023:7864 提取日语生词与语法解析 (假名注音/词性/例句)
       │
       ▼ (4) 导出格式生成器 (Format Exporters)
       ├── DOCX 导出 (带时间戳、段落分词、专业排版，通过 zip 结构校验)
       ├── TXT 导出 (UTF-8 纯文本对白)
       └── MD 导出 (支持 Markdown 语法高亮与词汇注释)
```

### 2.2 核心模块拓扑表

| 模块名称 | 纳管仓库 / 路径 | 核心组件与依赖 | 部署位置 |
| :--- | :--- | :--- | :--- |
| **Vocab Web App** | `Arthurchen-01/vocab` | Flask / FastAPI, Jinja2, Nginx 反代 | `五四云-1021:/var/www/harvard_justice_app` |
| **Whisper ASR Worker** | `providers/asr_worker.py` | `faster-whisper small`, CTranslate2, FFmpeg | `五四云-1021:/opt/asr-venv` |
| **Chinese/Japanese Editor** | `Arthurchen-01/zh-editor` | Vue 3 / TipTap 富文本, 假名注音插件 (Furigana) | 静态分发 / 本地运行 |
| **AP Learning Portal** | `Arthurchen-01/AP-Learning-Web` | Next.js / TailwindCSS, 课程音视频同步渲染 | 前端集群托管 |
| **Progress Tracker** | `Arthurchen-01/ap-tracker` | 打卡日历, 艾宾浩斯遗忘曲线复习算法 | SQLite / Node.js |
| **Study Pod** | `Arthurchen-01/study-pod` | WebRTC / WebSocket 协作学习白板 | 本地与云端节点 |

---

## 三、 多服务器部署与运维操作手册 (Fleet Operations)

### 3.1 跨节点部署与服务治理

```bash
# 1. 检查五四云-1021 上词汇转写站与 ASR Worker 状态
ssh root@156.225.28.62 "systemctl status vocab_app.service vocab-asr-worker.service"

# 2. 检查 Unix Socket 管道通信
ssh root@156.225.28.62 "ls -la /run/vocab-asr/worker.sock"

# 3. 验证公网访问连通性
curl -I https://vocab.samuraiguan.cloud/transcribe.html

# 4. 执行音频转写回归测试 (针对 7 分钟音频用例)
ssh root@156.225.28.62 "python3 /var/www/harvard_justice_app/tests/test_e2e_asr.py"
```

### 3.2 实测性能基准 (2026-10-06 压测真实数据)

| 测试音频 | 音频时长 | 处理耗时 | 加速比 | 产物格式 | 校验结论 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 短录音 E2E | 00:02 | 0.8s | 2.5x | docx, txt, md | ✅ zipfile 校验通过 |
| 巨人第一季音轨片段 | 07:12 | 219s | 1.95x | docx (含假名注音) | ✅ 正确识别并对齐 |

---

## 四、 防死锁与断网自愈策略 (Anti-Bug Runbook)

### 4.1 故障场景 A：ASR 进程 OOM 或挂死
- **触发表现**：转写任务一直卡在 `status=running`，Unix Socket 无响应。
- **自愈机制**：
  1. `vocab_app` 设置每个作业的最大超时时间（15 分钟），超时后标记为 `TIMEOUT_FAILED`；
  2. Systemd 单元 `vocab-asr-worker.service` 配置 `Restart=always` 及内存上限 `MemoryMax=4G`；
  3. 异常退出时系统自动清理残留在 `/tmp/vocab_asr_*` 的音频切片文件，防止占满系统盘。

### 4.2 故障场景 B：DOCX 导出时非 UTF-8 字符导致打包失败
- **触发表现**：用户下载 DOCX 返回 500 内部服务器错误。
- **排查与修复**：
  1. 在字符进入 `python-docx` 之前，强制通过 `re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)` 过滤非法 XML 控制字符；
  2. 导出完成后自动调用 `zipfile.ZipFile(docx_path).testzip()` 进行结构断言；
  3. 断言失败自动降级为 `.md` 格式文本，确保用户学习成果绝不丢失。

---

## 五、 验收标准与交付清单 (Acceptance Criteria)

1. [x] **架构物理落盘**：完整编制语言沉浸式转写、排版与学习门户架构至 `10_learning_and_content_engine_architecture.md`；
2. [x] **学习偏好对齐**：完整支持日语初学者沉浸式听力句型分析（进击的巨人 S1）与公开课转写；
3. [x] **端到端实测印证**：严谨记录 2026-10-06 实测的 1.95x 加速比与三种导出格式（DOCX/TXT/MD）；
4. [x] **解耦防死锁**：确认 Web 服务与 ASR 运算通过 Unix Socket 严格异步解耦。
