import json
from datetime import date
from pathlib import Path

import streamlit as st

from agents import WorkflowOrchestrator

ROOT = Path(__file__).parent
SAMPLES_PATH = ROOT / "data" / "samples.json"


@st.cache_data
def load_samples() -> dict[str, str]:
    if not SAMPLES_PATH.exists():
        return {}
    return json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))


def render_task_table(tasks: list[dict]) -> None:
    if not tasks:
        st.info("未识别到待办事项。可以尝试加入“请、需要、跟进、提交、今天、明天”等行动描述。")
        return
    st.dataframe(tasks, use_container_width=True, hide_index=True)


def render_plan(plan: dict) -> None:
    schedule = plan.get("schedule", [])
    if not schedule:
        st.info("暂无可规划任务。")
        return
    for block in schedule:
        with st.container(border=True):
            st.markdown(f"**{block['time']}｜{block['focus']}**")
            for task in block.get("tasks", []):
                st.write(f"- {task['id']} {task['title']}（{task['priority']}，截止：{task['deadline']}）")
    risks = plan.get("risks", [])
    if risks:
        st.warning("\n".join(f"- {risk}" for risk in risks))


def main() -> None:
    st.set_page_config(page_title="个人工作流 Agent MVP", page_icon="AI", layout="wide")
    st.title("个人工作流 Agent / 多 Agent 办公助手 MVP")
    st.caption("本地规则引擎演示版：信息整理 Agent → 任务 Agent → 计划 Agent → 写作 Agent")

    samples = load_samples()
    with st.sidebar:
        st.header("输入配置")
        sample_name = st.selectbox("选择内置示例", ["自定义输入", *samples.keys()])
        report_date = st.date_input("报告日期", value=date.today())
        st.markdown("---")
        st.markdown("**运行方式**")
        st.code("streamlit run app.py", language="bash")
        st.markdown("**说明**：当前版本不需要 API Key，适合演示 MVP。")

    default_text = samples.get(sample_name, "")
    text = st.text_area(
        "粘贴你的工作信息、会议记录、聊天消息或邮件内容",
        value=default_text,
        height=260,
        placeholder="例如：今天需要整理客户反馈；明天提交周报；请王强跟进接口评审……",
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        run_button = st.button("运行多 Agent 分析", type="primary", use_container_width=True)
    with col2:
        st.caption("建议输入 5-20 条办公信息，效果更明显。")

    if not run_button:
        st.info("选择示例或粘贴文本后，点击“运行多 Agent 分析”。")
        return

    if not text.strip():
        st.error("请先输入需要分析的工作文本。")
        return

    orchestrator = WorkflowOrchestrator()
    result = orchestrator.run(text, report_date=report_date)

    st.subheader("Agent 协作链路")
    cols = st.columns(4)
    agent_names = ["InboxAgent", "TaskAgent", "PlannerAgent", "WriterAgent"]
    for col, name, summary in zip(cols, agent_names, result["agent_summaries"]):
        with col:
            st.metric(name, "完成")
            st.caption(summary)

    tab_summary, tab_tasks, tab_plan, tab_notes, tab_weekly, tab_download = st.tabs(
        ["信息摘要", "待办列表", "今日计划", "会议纪要", "周报草稿", "导出"]
    )

    with tab_summary:
        st.markdown(f"### 总览\n{result['summary']}")
        for category, items in result["inbox"].get("buckets", {}).items():
            with st.expander(category, expanded=True):
                for item in items:
                    st.write(f"- {item}")

    with tab_tasks:
        render_task_table(result["tasks"])

    with tab_plan:
        render_plan(result["plan"])

    with tab_notes:
        st.markdown(result["meeting_notes"])

    with tab_weekly:
        st.markdown(result["weekly_report"])

    with tab_download:
        st.download_button(
            "下载 Markdown 报告",
            data=result["markdown_report"].encode("utf-8"),
            file_name=f"workflow-agent-report-{report_date}.md",
            mime="text/markdown",
            use_container_width=True,
        )
        st.code(result["markdown_report"], language="markdown")


if __name__ == "__main__":
    main()
