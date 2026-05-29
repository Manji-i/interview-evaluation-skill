# Interview Evaluation Skill

面试评价整理 Skill，用于根据面试记录和用户指定考察维度，生成可直接上传招聘系统、供其他面试官阅读的结构化面试评价。

当前版本：`v1.1`

## 能力

- 支持飞书妙记、粘贴面试记录、PDF、Word、DOCX 等材料来源。
- 支持自定义考察维度，维度分为专业能力和软素质。
- 支持保存和复用维度模版；每次面试前先确认使用历史模版、调整模版或新建模版。
- 使用 `NH / H- / H / H+ / MH` 评分。
- 基于面试证据输出维度匹配度分析、主要风险和总体建议。
- 支持沉淀维度评分标准，并根据用户反馈持续校准 rubric。

## 亮点功能

- 自定义考核维度
- 对评分进行纠偏之后可以保存到 rubric.md，根据用户反馈持续校准评估标准


## 目录结构

```text
interview-evaluation-skill/
├── SKILL.md
├── agents/openai.yaml
├── memory/rubrics.json
├── references/
│   ├── output-schema.md
│   ├── rubric-memory.md
│   ├── system-prompt.md
│   └── version-history.md
└── scripts/rubric_memory.py
```

## 使用方式

将 `interview-evaluation-skill/` 放入支持 Codex Skill 的 skills 目录，或在 Agent 中显式引用该 Skill。

典型请求：

```text
使用 interview-evaluation-skill，基于这份面试记录，按业务理解、学习能力、Owner 意识三个维度输出面试评价。
```

## 评分标准记忆

默认评分标准文件：

```text
interview-evaluation-skill/memory/rubrics.json
```

多人使用或在其他 Agent 中调用时，建议通过环境变量指定独立记忆文件，避免把个人评分标准写入 Skill 安装目录：

```bash
export INTERVIEW_EVALUATION_RUBRICS_PATH="./.interview-evaluation/rubrics.json"
```

常用命令：

```bash
python3 interview-evaluation-skill/scripts/rubric_memory.py show
python3 interview-evaluation-skill/scripts/rubric_memory.py list-templates
python3 interview-evaluation-skill/scripts/rubric_memory.py upsert-dimension --category professional_ability --name "业务理解" --definition "理解业务逻辑、关键指标和岗位问题本质的能力"
python3 interview-evaluation-skill/scripts/rubric_memory.py upsert-template --name "产品经理一面" --role "产品经理" --description "产品经理一面常用维度" --dimensions-json '[{"category":"professional_ability","name":"业务理解"},{"category":"soft_quality","name":"学习能力"}]'
python3 interview-evaluation-skill/scripts/rubric_memory.py add-calibration --category professional_ability --name "业务理解" --from-rating H+ --to-rating H --note "用户认为 H+ 偏高" --standard "H+ 需要有明确业务抽象、主动方案设计和可复核结果。"
```

## 隐私边界

不要把面试原文、候选人隐私信息、手机号、邮箱、证件号、薪酬信息或原始简历写入 `memory/rubrics.json`。该文件只用于保存可复用的评分维度和评分标准。

## 打包文件

仓库内提供：

```text
interview-evaluation-skill.zip
```

可直接分享给需要安装 Skill 的用户。

## 版本记录

完整版本记录见：

```text
interview-evaluation-skill/references/version-history.md
```
