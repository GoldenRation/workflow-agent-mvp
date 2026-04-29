from agents.base import AgentResult, BaseAgent
from utils.text_utils import (
    TASK_KEYWORDS,
    compact_title,
    contains_any,
    extract_deadline,
    guess_owner,
    priority_of,
    split_sentences,
    task_status,
)


class TaskAgent(BaseAgent):
    name = "TaskAgent"

    def run(self, text: str, sentences: list[str] | None = None) -> AgentResult:
        sentences = sentences or split_sentences(text)
        tasks = []

        for index, sentence in enumerate(sentences, start=1):
            if not contains_any(sentence, TASK_KEYWORDS):
                continue
            priority, reason = priority_of(sentence)
            tasks.append(
                {
                    "id": f"T{len(tasks) + 1:02d}",
                    "title": compact_title(sentence),
                    "owner": guess_owner(sentence),
                    "deadline": extract_deadline(sentence),
                    "priority": priority,
                    "status": task_status(sentence),
                    "reason": reason,
                    "source_line": f"第 {index} 条：{sentence}",
                }
            )

        tasks.sort(key=lambda item: {"高": 0, "中": 1, "低": 2}.get(item["priority"], 3))
        summary = f"识别出 {len(tasks)} 个待办事项。"
        if tasks:
            high_count = sum(1 for task in tasks if task["priority"] == "高")
            summary += f" 其中高优先级 {high_count} 个，建议优先处理有明确截止时间或风险信号的任务。"
        else:
            summary += " 当前文本更像信息记录，未发现明显行动项。"

        return AgentResult(self.name, summary, {"tasks": tasks})
