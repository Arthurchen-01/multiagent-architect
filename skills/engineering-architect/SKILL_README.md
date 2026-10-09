# engineering-architect ｜工程架构师

> 一个把「资深工程师/架构师怎么判断」写成流程的 Agent Skill。
> 遵循 **Agent Skills 开放标准**（`SKILL.md` + `references/` + `assets/` + `scripts/`）。

- **版本**：v0.1.0.0
- **日期**：2026-10-09
- **技能目录**：`engineering-architect/`（目录名必须与 frontmatter 里的 `name` 一致）

---

## 一、它是干什么的

把模糊需求变成**可验收的系统**。核心是四件事：

1. **判档** —— 这是小活、中活还是大活？**判据是「做错一次多贵」，不是代码行数。**
   小活直接做，**不写 PRD**；大活才写架构决策。
2. **核实** —— 三条腿：网上权威做法 + 项目自己的尺子 + 常识推演。**缺一条不算核实。**
3. **复核** —— 影响面大的结论要**换一家 AI** 独立重走一遍（同厂换上下文不算）。
4. **留证据** —— 验收跑过、结论落盘、汇报是工程图七段。

它有五个工作模式，按信号自动路由：**Architect / Engineer / Debugger / Reviewer / Coach**。
默认是**自动干活**；只有你明确说「我想练」时才进 Coach 模式。

---

## 二、装到哪（三个环境，一条命令）

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

**一条命令装进本机所有会用到它的 AI 环境**，装完自动逐个校验 + 比对哈希：

| # | 环境 | 装到哪 | 怎么被找到 |
| :-- | :-- | :-- | :-- |
| 1 | **dsh**（DeepSeek Harness） | `%USERPROFILE%\.dsh\skills\` | 自动扫描该目录 |
| 2 | **WorkBuddy** | `%USERPROFILE%\.workbuddy\skills\` | 自动扫描该目录 |
| 3 | **Antigravity 2.0 / IDE** | `%USERPROFILE%\.gemini\config\skills\` | 全局技能目录（所有工作区可见） |
| 4 | **Antigravity IDE**（旧路径） | `%USERPROFILE%\.gemini\antigravity\skills\` | 旧版兼容路径 |
| 5 | **Antigravity CLI** | `%USERPROFILE%\.gemini\antigravity-cli\skills\` | CLI 全局技能目录 |

> **本机的一个关键事实**：第 1 和第 2 个位置**其实是同一个文件夹的两个入口**
> （两个都是 junction，都指向同一个共享技能库）。所以脚本会**自动去重** —— 只写一次，
> 但两个环境都看得到。这也是为什么「装到 dsh」等于「装到 WorkBuddy」。

**别的环境**（ChatGPT、其它客户端）：把整个 `engineering-architect\` 文件夹拷进那个客户端的
skills 目录即可。它是**纯 Markdown**，没有任何外部依赖，不挑环境。

**DryRun（只看不装）**：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -DryRun
```

**卸载**：把上表五个位置里的 `engineering-architect` 文件夹删掉即可。没有写注册表、没有改环境变量。

> **如果觉得它太吵**（每轮对话都占一点上下文）：在 `SKILL.md` 开头加一行
> `disable-model-invocation: true`，它就变成「只有你打名字才启动」。
> WorkBuddy 也可以用它自己的 `skillOverrides` 达到同样效果。

### 装完之后，改了源文件怎么办

**重新跑一次 `install.ps1` 就行**（它会覆盖 + 重新校验 + 比对哈希）。
**不要直接改装好的那几份** —— 那会造出「同一个技能有好几个版本」，
正是本技能模式库 `P-03 双真相源` 警告的情况。

> 为什么用「复制」而不是「链接」：链接更省事，但**有些客户端扫描技能时会跳过链接**，
> 那就等于没装。**这里优先保证「一定找得到」，用复制 + 哈希校验来防走样。**

---

## 三、目录结构

```
engineering-architect/
├── SKILL.md                          # 核心：闸门 / 路由 / 五种模式 / 反模式（90 行正文）
├── references/
│   ├── pattern-library.md            # 八类基础模式 + 11 张从真实事故提炼的模式卡
│   ├── diagnosis-tree.md             # Debugger：把「感觉不对」变成「可复现的一句话」
│   ├── project-memory.md             # 状态放哪、怎么写、多人怎么不打架
│   ├── coach-mode.md                 # Coach：先预测、再反馈的刻意练习闭环
│   └── sources.md                    # 每条规矩的出处（凭什么）
├── assets/
│   ├── pattern-card-template.md      # 新模式卡模板
│   ├── decision-record-template.md   # 决策记录模板（Prediction 必须在 Result 之前）
│   ├── report-template.md            # 工程图七段汇报模板
│   └── trigger-eval.json             # 触发评测集（训练集 8 + 验证集 6）
└── scripts/
    └── validate_skill.py             # 校验技能包合规 + 扫指纹泄漏（只读、不联网）
```

---

## 四、怎么验收（每次改完都跑一遍）

```powershell
python engineering-architect\scripts\validate_skill.py engineering-architect
```

退出码 `0` = 通过。它检查：

- frontmatter 必填项、`name` 命名规则、**name 与目录同名**、`description` ≤1024 字符；
- `SKILL.md` 正文 ≤500 行；
- `SKILL.md` 引用的文件**全部存在**，且技能内文件都能从 `SKILL.md` **一层直达**；
- **指纹扫描**：交付物里不许出现 IP、Windows 绝对路径、MAC、凭据。

**当前状态**（2026-10-09 实测，装到 dsh 之后又验了一遍）：**`OK=7  WARN=8  FAIL=0`，退出码 0**。

那 8 条 WARN 全是同一类：**references 之间互相指了一下**（例如 `pattern-library.md` 里说
「先照 `diagnosis-tree.md` 定位根因」）。规范要求「一层深」的本意是**别让 agent 跳两次才找到东西** ——
这里每个文件都能从 `SKILL.md` 直接指到（`OK` 里那条「技能内文件全部能从 SKILL.md 一层直达」就是查这个），
所以这 8 条是**可接受的**，不是缺陷。

---

## 五、触发测试（改过 description 之后必须做）

1. 打开 `engineering-architect/assets/trigger-eval.json`，里面有 14 条查询：
   **前 8 条应该触发，后 6 条不应该**（后 6 条是「近邻」负例，专门测边界）。
2. 每条跑 **3 次**，记触发率。**>0.5 视为触发**。
3. **只用前 8 条（训练集）来改 description**；后 6 条（验证集）只用来检查有没有过拟合，
   **不许拿它指导修改**。
4. 每轮改完记下验证集的通过率，**取验证集最好的那一版**（不一定是你最后改的那版）。

> 这是开放标准推荐的做法。**不做这一步，description 的可靠性只能靠猜。**

---

## 六、版本规矩

- 一个版本一个文件夹：`skills/vX.Y.Z.W/`，里面的技能目录名**固定不变**（`engineering-architect`）。
- **改内容 = 升版本**，并在 `CHANGELOG.md` 写清：改了什么、为什么、怎么验的。
- 旧版本**不要删**（留着做对照），除非确定没人用。
- 升版本的判据：
  - `W`（第四位）：改错字、改措辞、加案例 —— 行为不变。
  - `Z`（第三位）：改判据、加模式卡、改流程 —— 行为变了但接口没变。
  - `Y`（第二位）：加/删 reference 文件、改加载地图 —— 结构变了。
  - `X`（第一位）：换定位（比如拆成多个 skill）。
- **发布前的修订并进同一版**（在 `CHANGELOG.md` 里记「发布前修订」），**发布后**再改才按四位升版本。
  判据：这一版**有没有被真实任务用过**。没用过就还是草稿，不值得为一行改动开新文件夹。

---

## 七、已知取舍（给你留的叫停口）

| 取舍 | 现在的选择 | 想改的话 |
| :-- | :-- | :-- |
| 自动触发 vs 安静 | 选了**自动触发**（description 常驻，约 530 字符） | 加 `disable-model-invocation: true` 变手动 |
| 一个 skill 装五种模式 vs 拆五个 | 选了**一个**（初版不拆，靠 references 渐进加载） | 拆成五个时，每个要自己的 description，常驻成本变高 |
| 八类模式是「初始分类、非最终定论」 | 照原样保留，**没有假装它是定论** | 用出经验后按 `pattern-library.md` §三 改 |
| 「宏大终局」那条写成了**待验证假设** | 明确标注「不是统计事实」 | 想验证就去数：从开工到第一个端到端闭环隔了多久 |

---

## 八、下一步（建议，不是命令）

1. **拿两个差异大的真实任务试它**：一个简单自动化活、一个多模块复杂活。
   看它能不能**正确判档**（该不写 PRD 的时候真的没写）、**维护状态**、**提出有效的验收**。
2. **按真实失败改**，别一次设计完。
   最直接的改法：**你每次纠正它一次，就往 `SKILL.md` §6 反模式或 `pattern-library.md` 加一条。**
3. 用 `assets/trigger-eval.json` 跑一轮触发测试，把不触发/误触发的记下来再改 description。

---

_本文件属于 `skills/v0.1.0.0/` 版本目录，改版本时一并更新。_
