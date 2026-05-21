---
name: interview-evaluation-skill
description: 根据面试记录结构化整理候选人信息，并输出有证据支撑的面试评价。适用于 Codex 需要从飞书妙记、粘贴的面试记录、PDF、Word、DOCX 或其他面试材料中提取信息；与用户确认专业能力和软素质维度；沉淀可复用评分标准；并使用 NH、H-、H、H+、MH 进行评价的场景。
---

# 面试评价整理 Skill

## 核心流程

1. 识别面试材料来源：
   - 飞书妙记 URL 或 token：使用飞书妙记相关工具获取逐字稿、摘要、章节和待办。
   - 用户粘贴的面试记录：直接使用用户提供的文本。
   - PDF、Word、DOCX：先用可用的文档或 PDF 工具提取文本，再进入评价流程。
2. 读取评分标准记忆：优先加载环境变量 `INTERVIEW_EVALUATION_RUBRICS_PATH` 指定的 JSON 文件；未设置时加载 Skill 内置的 `memory/rubrics.json`。如果文件不存在，按 `references/rubric-memory.md` 的 schema 创建默认结构；如果文件格式异常，脚本会先备份坏文件再回到默认结构。
3. 评分前先确认考察维度：
   - 维度统一归入 `professional_ability`（专业能力）和 `soft_quality`（软素质）。
   - 如果用户已经给出维度，先标准化命名，只对歧义项追问。
   - 如果用户没有给维度，根据岗位和上下文提出一组精简默认维度，请用户确认或调整。
   - 用户确认后的维度用 `scripts/rubric_memory.py` 写入记忆。
4. 生成评价时，以 `references/system-prompt.md` 作为核心提示词，以 `references/output-schema.md` 作为输出结构约束。
5. 当用户质疑某个评分，或补充更具体的评分标准时，更新对应维度的标准记忆，然后重新评估受影响维度和总体建议。

## 评分尺度

只能使用以下评分，从低到高：

- `NH`：明显低于录用标准。
- `H-`：接近标准，但存在实质风险。
- `H`：达到录用标准。
- `H+`：明显高于录用标准。
- `MH`：非常突出，形成强录用信号。

不要虚高评分。高于 `H` 的评分必须有面试记录中的具体、重复、与岗位强相关的证据支撑。

## 记忆规则

只在评分标准记忆 JSON 中保存可复用的评分标准信息。发布或多人使用时，建议用 `INTERVIEW_EVALUATION_RUBRICS_PATH` 指向用户自己的记忆文件，例如项目内的 `.interview-evaluation/rubrics.json` 或用户目录下的 `$HOME/.interview-evaluation/rubrics.json`。

- 类别、维度名称、别名、定义。
- `NH`、`H-`、`H`、`H+`、`MH` 的等级锚点。
- 来自用户反馈的评分校准记录。

不要保存完整面试原文、候选人隐私数据、手机号、邮箱、证件号、薪酬信息或原始简历，除非用户明确要求并指定存放位置。

常用命令：

```bash
python3 scripts/rubric_memory.py show
python3 scripts/rubric_memory.py upsert-dimension --category professional_ability --name "AI coding" --definition "使用 AI 工具提升编码效率和质量的能力" --levels-json '{"H":"能用 AI 加速常规编码任务，并能做基本审查","H+":"能用 AI 拆解任务、验证输出，并改善设计质量"}'
python3 scripts/rubric_memory.py add-calibration --category professional_ability --name "AI coding" --from-rating H+ --to-rating H --note "用户认为 H+ 偏高，因为缺少独立验证 AI 输出的证据" --standard "H+ 需要证明候选人能独立验证 AI 输出，并发现非显而易见的问题。"
```

以上命令需要在 Skill 目录下运行。

## 输出纪律

结论先行，再给证据。每个维度评分都必须引用面试证据；没有证据时明确写“证据不足”。区分事实提取和评价判断。面试记录不完整时标注不确定性，不要补全不存在的信息。

如果用户只要求调整评分标准，只更新记忆并总结变更，不输出候选人评价。
