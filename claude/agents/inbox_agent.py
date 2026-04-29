from collections import Counter

from agents.base import AgentResult, BaseAgent
from utils.text_utils import RISK_KEYWORDS, contains_any, split_sentences


class InboxAgent(BaseAgent):
    name = "InboxAgent"

    def run(self, text: str) -> AgentResult:
        sentences = split_sentences(text)
        buckets = {
            "会议/沟通": [],
            "项目推进": [],
            "风险问题": [],
            "数据/报告": [],
            "其他信息": [],
        }

        for sentence in sentences:
            if contains_any(sentence, ["会议", "纪要", "对齐", "沟通", "同步", "讨论"]):
                buckets["会议/沟通"].append(sentence)
            elif contains_any(sentence, RISK_KEYWORDS):
                buckets["风险问题"].append(sentence)
            elif contains_any(sentence, ["数据", "报表", "日报", "周报", "指标", "转化率", "GMV"]):
                buckets["数据/报告"].append(sentence)
            elif contains_any(sentence, ["项目", "需求", "上线", "开发", "测试", "评审", "版本"]):
                buckets["项目推进"].append(sentence)
            else:
                buckets["其他信息"].append(sentence)

        non_empty = {key: value for key, value in buckets.items() if value}
        keyword_counter = Counter()
        for sentence in sentences:
            for word in ["会议", "需求", "测试", "上线", "风险", "数据", "客户", "周报", "评审"]:
                if word in sentence:
                    keyword_counter[word] += 1

        top_keywords = "、".join(word for word, _ in keyword_counter.most_common(5)) or "暂无明显主题"
        summary = f"共解析 {len(sentences)} 条信息，主要主题：{top_keywords}。"
        if non_empty:
            summary += " 信息已按办公场景归类，便于后续 Agent 提取待办和生成计划。"

        return AgentResult(self.name, summary, {"sentences": sentences, "buckets": non_empty})
