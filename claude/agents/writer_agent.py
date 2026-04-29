from agents.base import AgentResult, BaseAgent
from utils.text_utils import markdown_table, today_label


class WriterAgent(BaseAgent):
    name = "WriterAgent"

    def run(self, inbox: dict, tasks: list[dict], plan: dict, report_date=None) -> AgentResult:
        report_date_text = today_label(report_date)
        buckets = inbox.get("buckets", {})
        risks = plan.get("risks", [])

        discussion_lines = []
        for category, items in buckets.items():
            if not items:
                continue
            discussion_lines.append(f"- **{category}**：" + "；".join(items[:3]))

        task_headers = [
            ("id", "编号"),
            ("title", "事项"),
            ("owner", "负责人"),
            ("deadline", "截止"),
            ("priority", "优先级"),
            ("status", "状态"),
        ]
        task_table = markdown_table(tasks, task_headers)

        meeting_notes = f"""# 会议纪要 / 信息整理

日期：{report_date_text}

## 背景
本纪要由个人工作流多 Agent 根据输入文本自动整理生成，用于快速沉淀沟通内容和行动项。

## 讨论要点
{chr(10).join(discussion_lines) if discussion_lines else '- 暂无明确讨论要点。'}

## 行动项
{task_table}

## 风险与提醒
{chr(10).join('- ' + item for item in risks) if risks else '- 暂无明显风险。'}
"""

        done_tasks = [task for task in tasks if task.get("status") == "已完成"]
        todo_tasks = [task for task in tasks if task.get("status") != "已完成"]
        weekly_report = f"""# 工作周报草稿

日期：{report_date_text}

## 本周完成
{chr(10).join('- ' + task['title'] for task in done_tasks) if done_tasks else '- 本次输入中未识别到已完成事项，可补充实际完成内容。'}

## 正在推进
{chr(10).join('- ' + task['title'] + f"（{task['priority']}优先级，截止：{task['deadline']}）" for task in todo_tasks[:8]) if todo_tasks else '- 暂无待推进事项。'}

## 风险与依赖
{chr(10).join('- ' + item for item in risks) if risks else '- 暂无明显风险与依赖。'}

## 下周计划
{chr(10).join('- ' + task['title'] for task in todo_tasks[:5]) if todo_tasks else '- 继续跟进常规工作。'}
"""

        summary = "已生成会议纪要和周报草稿，可直接复制或下载为 Markdown。"
        return AgentResult(
            self.name,
            summary,
            {"meeting_notes": meeting_notes.strip(), "weekly_report": weekly_report.strip()},
        )
