from agents.base import AgentResult, BaseAgent
from utils.text_utils import contains_any


class PlannerAgent(BaseAgent):
    name = "PlannerAgent"

    def run(self, tasks: list[dict]) -> AgentResult:
        active_tasks = [task for task in tasks if task.get("status") != "已完成"]
        high = [task for task in active_tasks if task.get("priority") == "高"]
        medium = [task for task in active_tasks if task.get("priority") == "中"]
        low = [task for task in active_tasks if task.get("priority") == "低"]

        schedule = []
        if high:
            schedule.append({"time": "09:30-11:00", "focus": "处理高优先级/风险任务", "tasks": high[:3]})
        if medium:
            schedule.append({"time": "14:00-15:30", "focus": "推进协作与近期截止任务", "tasks": medium[:4]})
        if low:
            schedule.append({"time": "16:30-17:30", "focus": "批量处理低优先级事项", "tasks": low[:5]})
        if active_tasks:
            schedule.append({"time": "17:30-18:00", "focus": "同步进展并更新明日计划", "tasks": active_tasks[:5]})

        risks = []
        for task in active_tasks:
            source = task.get("source_line", "") + task.get("title", "")
            if task.get("deadline") in {"今天", "未指定"} and task.get("priority") == "高":
                risks.append(f"{task['id']}：高优先级任务需要尽快明确完成路径。")
            elif contains_any(source, ["风险", "阻塞", "延期", "依赖", "卡住"]):
                risks.append(f"{task['id']}：存在风险或依赖，请提前同步相关人。")

        summary = f"生成今日计划：{len(schedule)} 个时间块，覆盖 {len(active_tasks)} 个未完成任务。"
        if risks:
            summary += f" 发现 {len(risks)} 条风险提醒。"

        return AgentResult(self.name, summary, {"schedule": schedule, "risks": risks})
