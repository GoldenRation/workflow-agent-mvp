from datetime import date

from agents.inbox_agent import InboxAgent
from agents.planner_agent import PlannerAgent
from agents.task_agent import TaskAgent
from agents.writer_agent import WriterAgent
from utils.text_utils import markdown_table


class WorkflowOrchestrator:
    def __init__(self):
        self.inbox_agent = InboxAgent()
        self.task_agent = TaskAgent()
        self.planner_agent = PlannerAgent()
        self.writer_agent = WriterAgent()

    def run(self, text: str, report_date: date | None = None) -> dict:
        inbox_result = self.inbox_agent.run(text)
        task_result = self.task_agent.run(text, inbox_result.data["sentences"])
        planner_result = self.planner_agent.run(task_result.data["tasks"])
        writer_result = self.writer_agent.run(
            inbox_result.data,
            task_result.data["tasks"],
            planner_result.data,
            report_date=report_date,
        )

        markdown_report = self._build_markdown_report(
            inbox_result,
            task_result,
            planner_result,
            writer_result,
        )

        return {
            "summary": inbox_result.summary,
            "inbox": inbox_result.data,
            "tasks": task_result.data["tasks"],
            "plan": planner_result.data,
            "agent_summaries": [
                inbox_result.summary,
                task_result.summary,
                planner_result.summary,
                writer_result.summary,
            ],
            "meeting_notes": writer_result.data["meeting_notes"],
            "weekly_report": writer_result.data["weekly_report"],
            "markdown_report": markdown_report,
        }

    def _build_markdown_report(self, inbox_result, task_result, planner_result, writer_result) -> str:
        tasks = task_result.data["tasks"]
        plan = planner_result.data
        task_table = markdown_table(
            tasks,
            [
                ("id", "编号"),
                ("title", "事项"),
                ("owner", "负责人"),
                ("deadline", "截止"),
                ("priority", "优先级"),
                ("status", "状态"),
            ],
        )
        schedule_lines = []
        for block in plan.get("schedule", []):
            titles = "；".join(task["title"] for task in block.get("tasks", [])) or "无"
            schedule_lines.append(f"- **{block['time']} {block['focus']}**：{titles}")

        return f"""# 个人工作流 Agent 分析报告

## Agent 运行摘要
- {inbox_result.summary}
- {task_result.summary}
- {planner_result.summary}
- {writer_result.summary}

## 待办列表
{task_table}

## 今日计划
{chr(10).join(schedule_lines) if schedule_lines else '暂无计划。'}

## 风险提醒
{chr(10).join('- ' + item for item in plan.get('risks', [])) if plan.get('risks') else '- 暂无明显风险。'}

---

{writer_result.data['meeting_notes']}

---

{writer_result.data['weekly_report']}
""".strip()
