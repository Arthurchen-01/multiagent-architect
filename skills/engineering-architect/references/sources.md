# 权威出处（谁说的、凭什么）

> 什么时候读：有人问「凭什么这样规定」「这规矩哪来的」，或者要把本 skill 移植到别的环境时。
>
> **一条元规则**：本 skill 里的**模式**是从真实案例里提炼的**模型**，不是自然定律。
> 它内部自洽，但不等于客观正确。说给别人听时，永远说「按这套模型会读成 X」，不说「X 是错的」。

---

## 一、格式标准（本 skill 的文件长什么样，为什么这样长）

| 规矩 | 出处 |
| :-- | :-- |
| `SKILL.md` + YAML frontmatter（`name` / `description` 必填） | Agent Skills 开放标准 · Specification |
| `name` 只能小写字母数字连字符、≤64 字符、**必须与目录同名** | 同上 |
| `description` ≤1024 字符，要写「做什么 + 什么时候用」 | 同上 |
| 目录约定 `scripts/` `references/` `assets/` | 同上 |
| **渐进式披露**：元数据（~100 token，常驻）→ 正文（<5000 token）→ 资源（按需） | 同上 |
| `SKILL.md` 保持 **500 行以内**，超了拆到 `references/` | 同上 |
| 引用**只允许一层深**（都从 `SKILL.md` 直接指过去，不许链式跳转） | 同上 |
| 超过 100 行的参考文件要在顶部放目录 | Claude 官方 · Skill authoring best practices |
| `description` 用**祈使句、第三人称**，写用户意图而不是实现细节，**宁可写得主动些** | agentskills.io · Optimizing skill descriptions |
| **控制自由度**：脆弱的步骤写死命令；判断类任务给方向 + 说明为什么 | Claude 官方 · Skill authoring best practices |
| **给默认值，不给菜单** | 同上 |
| **教方法，不教答案**（procedure 优于 declaration） | 同上 |
| **gotchas 是最值钱的内容**（反直觉的环境事实，不是通用建议） | 同上 |
| **从真实材料提炼**，不要凭空生成（用内部事故报告/运行手册提炼，胜过通用「最佳实践」文章） | 同上 |
| 用**执行后修订**迭代：跑真实任务 → 把结果（不只失败）喂回去改 | 同上 |

来源：

- Agent Skills 开放标准（Anthropic 发起，多家客户端采纳）
  `https://agentskills.io/specification`、`/skill-creation/best-practices`、
  `/skill-creation/optimizing-descriptions`、`/skill-creation/evaluating-skills`
- Anthropic 工程博客《Equipping agents for the real world with Agent Skills》
  `https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills`
- Claude 平台文档《Skill authoring best practices》
  `https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices`

---

## 二、本 skill 的内容从哪来

| 内容 | 来源 |
| :-- | :-- |
| 八类基础模式、五项基本功、五层诊断树 | 《AI 工程架构师·聊天上下文总结》（本项目材料），**标注为初始分类、非最终定论** |
| P-01 ~ P-11 模式卡 | **本项目真实事故**（逐条见每张卡的「案例」） |
| 三条腿核实 / 换厂复核 / 落盘 / 只有两类事回到用户 | 用户定死的常驻协作规矩（AI 协作闭环） |
| 开工过闸门 / 外发不裸奔 / 交付物不带指纹 | 用户定死的常驻出口不变量 |
| 工程图七段汇报 / 人话 / 必带大图 | 用户定死的常驻汇报口径 |
| 「讲模型不讲真理」「交底我的局限」「战略层归当事人」 | 用户定死的《对当事人交付的规矩》 |
| 每个单元该有哪些文件、决策记录与经验教训格式 | 本机已装的 `project-skeleton-architecture` skill（**不在本 skill 里复制**） |

**边界声明**：在这台机器上，上面那些「用户定死的规矩」的**权威版本**是工作区里的
`AGENTS.md` 系列文件。本 skill 是它们的**可携带载体**（换到没装那套文件的机器上也能用），
**不是替代品**。两边冲突时，以 `AGENTS.md` 为准，并回来修本 skill。

---

## 三、本 skill 明确不做的事（避免和别的 skill 打架）

- **不代替专用 skill 执行**：代码审查走 `code-review`，疑难 bug 走 `diagnosing-bugs`，
  出规格走 `to-spec`，查资料走 `research`。本 skill 负责**判断这是哪类活、该走哪条路**。
- **不替代项目骨架规范**：文件该怎么摆，看 `project-skeleton-architecture`。
- **不替代出口不变量**：能不能外发、挂不挂代理，看出口闸门和 `egress-invariant`。

---

## 四、怎么改这个 skill（改之前先读这一节）

1. **只改一处**：同一个意思只允许存在一个地方。发现两处说法不一致 → 删掉一处，不要「都留着」。
2. **加规则前先问**：「不说这句，模型会不会默认做错？」不会 → 这句是废话，删掉。
3. **加内容前先问**：「这是项目特定事实吗？」是 → 写进项目文件，不要写进 skill。
4. **改完必须过校验**：`python scripts/validate_skill.py <skill 目录>`，退出码 0 才算改完。
5. **改完升版本**：见版本目录里的 `CHANGELOG.md`。
