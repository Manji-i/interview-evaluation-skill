# 评分标准记忆

评分标准记忆默认存放在 Skill 目录下的 `memory/rubrics.json`。

发布给他人或被其他 Agent 调用时，推荐通过环境变量 `INTERVIEW_EVALUATION_RUBRICS_PATH` 指定独立记忆文件，避免把个人评分标准写进 Skill 安装目录，或让多个项目共用同一份记忆。

示例：

```bash
export INTERVIEW_EVALUATION_RUBRICS_PATH="./.interview-evaluation/rubrics.json"
export INTERVIEW_EVALUATION_RUBRICS_PATH="$HOME/.interview-evaluation/rubrics.json"
```

这里只保存可复用的评价标准，不保存候选人记录、面试原文或隐私信息。

## Schema

```json
{
  "version": 1,
  "updated_at": "ISO-8601 timestamp",
  "rating_scale": {
    "NH": "clearly below hiring bar",
    "H-": "near bar but materially risky",
    "H": "meets hiring bar",
    "H+": "clearly above bar",
    "MH": "exceptional strong hire signal"
  },
  "categories": {
    "professional_ability": {
      "display_name": "专业能力",
      "dimensions": {}
    },
    "soft_quality": {
      "display_name": "软素质",
      "dimensions": {}
    }
  },
  "templates": {}
}
```

## 维度对象

```json
{
  "name": "AI coding",
  "aliases": ["AI 编程", "AI coding 能力"],
  "definition": "使用 AI 工具提升编码效率和质量的能力。",
  "level_anchors": {
    "NH": "",
    "H-": "",
    "H": "",
    "H+": "",
    "MH": ""
  },
  "calibrations": [
    {
      "timestamp": "ISO-8601 timestamp",
      "from_rating": "H+",
      "to_rating": "H",
      "note": "用户反馈摘要。",
      "standard": "更新后的评分标准。"
    }
  ]
}
```

## 模版对象

`templates` 用于保存“本次面试要考察哪些维度”的组合。维度对象解决“某个维度怎么打分”，模版对象解决“这场面试用哪些维度”。

```json
{
  "name": "产品经理一面",
  "aliases": ["PM 一面"],
  "description": "产品经理一面常用维度",
  "role": "产品经理",
  "dimensions": [
    {
      "category": "professional_ability",
      "name": "业务理解"
    },
    {
      "category": "professional_ability",
      "name": "产品拆解"
    },
    {
      "category": "soft_quality",
      "name": "学习能力"
    }
  ],
  "created_at": "ISO-8601 timestamp",
  "updated_at": "ISO-8601 timestamp"
}
```

## 更新规则

- 维度 key 必须稳定，并支持中文维度名。
- 除非用户明确要求修改，否则保留已有等级锚点。
- 用户反馈评分偏高或偏低时，追加 calibration 记录，不直接覆盖历史记录。
- 当用户补充新的评分标准时，把标准更新到相关等级锚点，并记录反馈原因。
- 每次评价前都要让用户确认本次维度组合；历史模版只能作为候选项，不应自动套用。
- 用户确认一组维度会复用时，将其保存为 `templates`；用户只临时增删维度时，不要强行更新原模版。
- 不要把面试原文、候选人隐私信息、手机号、邮箱、证件号、薪酬信息或原始简历写入记忆。
- 如果记忆 JSON 损坏，脚本应先把坏文件备份为 `rubrics.json.broken.<timestamp>`，再回到默认结构，避免整个 Skill 失效。
