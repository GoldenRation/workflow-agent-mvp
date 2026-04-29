import re
from datetime import date

TASK_KEYWORDS = [
    "需要", "请", "麻烦", "安排", "跟进", "确认", "提交", "完成", "修复", "整理", "同步",
    "评审", "对齐", "输出", "发送", "更新", "准备", "排查", "处理", "推进", "上线",
]
HIGH_PRIORITY_KEYWORDS = ["紧急", "尽快", "马上", "今天", "阻塞", "风险", "故障", "严重", "必须"]
MEDIUM_PRIORITY_KEYWORDS = ["明天", "本周", "周五", "评审", "确认", "同步", "提交"]
RISK_KEYWORDS = ["风险", "阻塞", "延期", "故障", "问题", "不确定", "缺少", "依赖", "卡住"]
DONE_KEYWORDS = ["已完成", "完成了", "已经", "已提交", "已同步", "done", "finished"]


def split_sentences(text: str) -> list[str]:
    normalized = re.sub(r"[\r\t]+", " ", text.strip())
    chunks = re.split(r"[\n。！？!?；;]+", normalized)
    return [re.sub(r"\s+", " ", chunk).strip(" -•、") for chunk in chunks if chunk.strip()]


def contains_any(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def extract_deadline(text: str) -> str:
    patterns = [
        r"(今天|明天|后天|本周|下周|月底|月末|上午|下午|今晚|本月底)",
        r"(周一|周二|周三|周四|周五|周六|周日|周天)",
        r"(\d{1,2}月\d{1,2}[日号]?)",
        r"(\d{1,2}[日号]\s*(前|之前|之前完成)?)",
        r"(\d{1,2}:\d{2})",
    ]
    matches: list[str] = []
    for pattern in patterns:
        matches.extend(re.findall(pattern, text))
    cleaned = []
    for match in matches:
        if isinstance(match, tuple):
            cleaned.append("".join(item for item in match if item))
        else:
            cleaned.append(match)
    return "、".join(dict.fromkeys(cleaned)) or "未指定"


def guess_owner(text: str) -> str:
    patterns = [
        r"@([\w\u4e00-\u9fa5]{1,8})",
        r"([\u4e00-\u9fa5]{2,4})(?:负责|来处理|跟进|确认|整理|提交)",
        r"请([\u4e00-\u9fa5]{2,4})(?:负责|跟进|确认|整理|提交|处理)?",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            owner = match.group(1).strip()
            if owner not in {"大家", "我们", "团队", "同学", "今天", "明天"}:
                return owner
    return "我/待确认"


def priority_of(text: str) -> tuple[str, str]:
    if contains_any(text, HIGH_PRIORITY_KEYWORDS):
        return "高", "命中紧急/风险/今天等关键词"
    if contains_any(text, MEDIUM_PRIORITY_KEYWORDS):
        return "中", "命中近期截止或协作关键词"
    return "低", "未发现紧急信号，可排入常规计划"


def task_status(text: str) -> str:
    return "已完成" if contains_any(text, DONE_KEYWORDS) else "待处理"


def compact_title(text: str, max_len: int = 42) -> str:
    title = re.sub(r"^(请|麻烦|需要|安排|帮忙|我们要|大家要)", "", text.strip())
    return title if len(title) <= max_len else title[:max_len] + "..."


def markdown_table(rows: list[dict], headers: list[tuple[str, str]]) -> str:
    if not rows:
        return "暂无。"
    head = "| " + " | ".join(label for _, label in headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(str(row.get(key, "")).replace("|", "\\|") for key, _ in headers) + " |")
    return "\n".join([head, sep, *body])


def today_label(value: date | None = None) -> str:
    value = value or date.today()
    return value.strftime("%Y-%m-%d")
