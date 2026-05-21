## 项目规则

这个工作区用于存放面试评价相关的本地 Codex Skill 源文件。

## 目录结构

- `AGENTS.md`：工作区规则和维护约定。
- `<skill-name>/`：每个 Skill 一个独立目录。目录名使用小写英文、数字和连字符。
- `<skill-name>/SKILL.md`：Skill 必需入口文件，包含 YAML frontmatter 和精简执行说明。
- `<skill-name>/agents/openai.yaml`：Skill 的界面展示元数据。
- `<skill-name>/references/`：提示词、结构 schema、评分标准和示例，按需读取。
- `<skill-name>/scripts/`：Skill 使用的确定性辅助脚本。
- `<skill-name>/memory/`：本地用户级 Skill 记忆，例如考察维度、评分标准和校准记录。

## 命名规则

- Skill 目录使用英文 hyphen-case，例如 `interview-evaluation-skill`。
- 引用文件使用描述性小写英文名，例如 `system-prompt.md`。
- 记忆文件使用稳定、机器可读的名称，例如 `rubrics.json`。

## 工作流程

1. 项目结构或约定发生变化时，先更新本文件。
2. 结构约定明确后，再创建或修改 Skill 文件。
3. `SKILL.md` 保持精简；详细提示词、schema 和示例放到 `references/`。
4. 每次修改 Skill 后，使用 `skill-creator` 的校验脚本验证。
5. 不在本工作区保存面试原文、候选人隐私数据、密钥、token 或生产凭证；除非用户明确要求，并且先约定存放位置。

## 验证方式

- 对修改过的 Skill 目录运行 `skill-creator` 的 `quick_validate.py`。
- 新增或修改脚本后，至少运行一条代表性命令验证脚本可用。
