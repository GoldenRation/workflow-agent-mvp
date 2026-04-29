# 个人工作流 Agent / 多 Agent 办公助手 MVP

这是一个完整可运行的本地 MVP，用于演示个人办公场景里的多 Agent 协作：

1. InboxAgent：整理输入信息并按场景分类。
2. TaskAgent：提取待办事项、负责人、截止时间和优先级。
3. PlannerAgent：生成今日计划和风险提醒。
4. WriterAgent：生成会议纪要和周报草稿。

当前版本使用本地规则引擎，不需要 API Key，适合快速演示和二次开发。

## 目录结构

```text
.
├── app.py
├── requirements.txt
├── agents/
│   ├── base.py
│   ├── inbox_agent.py
│   ├── task_agent.py
│   ├── planner_agent.py
│   ├── writer_agent.py
│   └── orchestrator.py
├── utils/
│   └── text_utils.py
└── data/
    └── samples.json
```

## 运行方式

建议使用 Python 3.10+。

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

启动后浏览器会打开本地页面。你可以选择左侧内置示例，也可以粘贴自己的会议记录、聊天消息、邮件内容或工作流水。

## 功能说明

- 信息归类：自动识别会议沟通、项目推进、风险问题、数据报告等内容。
- 待办提取：根据“请、需要、跟进、确认、提交、完成、修复、整理”等关键词识别行动项。
- 优先级判断：根据“紧急、尽快、今天、阻塞、风险”等关键词判断高优先级。
- 今日计划：按优先级生成时间块。
- 文档生成：自动生成会议纪要、周报草稿和 Markdown 报告。
- 导出：页面内支持下载 Markdown 报告。

## 打包成 zip

在项目目录执行：

```bash
python -m zipfile -c workflow-agent-mvp.zip app.py requirements.txt README.md .gitignore agents utils data
```

把 `workflow-agent-mvp.zip` 发给别人，对方解压后按“运行方式”安装依赖并启动即可。

## 后续可扩展方向

- 接入 Claude API / OpenAI / 本地大模型，将规则 Agent 替换为真实 LLM Agent。
- 接入飞书、企业微信、邮箱或日历。
- 增加 SQLite 数据库存储历史任务。
- 增加任务状态编辑和日程 ICS 导出。
- 增加团队成员维度和多人协作看板。
