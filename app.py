import streamlit as st  # type: ignore
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    pd = None
    PANDAS_AVAILABLE = False

try:
    import plotly.express as px # type: ignore
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from src.workflows.basic_workflow import run_research_workflow
from src.agents.head_agent import HeadAgent
from src.agents.worker_agents import DataAnalysisAgent
from src.agents.security_agents import InputSecurityAgent, OutputSecurityAgent

st.set_page_config(
    page_title="Multi-Agent Security System",
    page_icon="🤖",
    layout="centered",
)

if "history" not in st.session_state:
    st.session_state.history = []

# --- Professional agent names ---
AGENT_LABELS = {
    "research": "🔬 Senior Research Analyst",
    "code": "💻 Principal Software Engineer",
    "data_analysis": "📊 Senior Data Scientist",
    "sql_software": "🗄️ Database & Systems Engineer",
}

EXAMPLE_QUERIES = {
    "🔬 Research example": "What are the main differences between supervised and unsupervised machine learning?",
    "💻 Code example": "Write a Python function to check if a number is prime",
    "📊 Data analysis example": "Analyze this data: sales were 100, 150, 200, 175, 220 over 5 months. What's the average and trend?",
    "🗄️ SQL & Systems example": "I'm getting a SQL deadlock error on my orders table, how do I fix it and optimize the query?",
}

# --- Sidebar ---
with st.sidebar:
    st.header("Example Queries")
    st.caption("Click an example to load it into the input box.")
    for label, example in EXAMPLE_QUERIES.items():
        if st.button(label, use_container_width=True):
            st.session_state["query_input"] = example

    st.divider()

    st.header("History")
    if st.session_state.history:
        for item in reversed(st.session_state.history):
            with st.expander(f"{item['agent']} — {item['query'][:40]}..."):
                st.markdown(f"**Query:** {item['query']}")
                st.markdown(f"**Result:**\n\n{item['result']}")
        if st.button("Clear history", use_container_width=True):
            st.session_state.history = []
            st.rerun()
    else:
        st.caption("No queries yet.")

# --- Main UI ---
st.title("🤖 Multi-Agent Security System")
st.caption(
    "A multi-agent AI system with input/output security checks, "
    "dynamic task routing, and specialized worker agents."
)

with st.expander("ℹ️ How it works", expanded=False):
    st.markdown(
        """
This system processes your query through several stages:

1. **Input Security Check** — Your input is screened for prompt
   injection attempts or unsafe requests.
2. **Task Routing** — The Head Agent analyzes your query and routes
   it to the most appropriate specialist agent.
3. **Worker Execution** — One of the following agents handles the task:
   - 🔬 **Senior Research Analyst** — general knowledge and research queries
   - 💻 **Principal Software Engineer** — code generation, explanation, and debugging
   - 📊 **Senior Data Scientist** — statistics, insights, and business reports
   - 🗄️ **Database & Systems Engineer** — SQL queries, database issues, and software/environment troubleshooting
4. **Output Security Check** — The response is screened before being
   shown to you.
        """
    )

tab1, tab2 = st.tabs(["💬 Ask the Agents", "📊 Data Dashboard"])

# ============================================================
# TAB 1: Existing agent chat flow
# ============================================================
with tab1:
    st.divider()

    user_input = st.text_area(
        "Enter your query",
        placeholder="e.g. 'Write a Python function to check if a number is prime' "
        "or 'Analyze this data: sales were 100, 150, 200, 175, 220 over 5 months'",
        height=120,
        key="query_input",
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        submit = st.button("Run", type="primary", use_container_width=True)

    if submit:
        if not user_input.strip():
            st.warning("Please enter a query before running.")
        else:
            head = HeadAgent(name="HeadAgent")
            route_info = head.route_task(user_input)
            worker_type = route_info.get("worker_type", "research")
            agent_label = AGENT_LABELS.get(worker_type, worker_type)

            with st.spinner(f"Routing to {agent_label}..."):
                result = run_research_workflow(user_input)

            st.divider()

            if result.startswith("REQUEST BLOCKED") or result.startswith("OUTPUT BLOCKED"):
                st.error(result)
            else:
                st.success(f"Handled by: {agent_label}")
                st.markdown("### Result")
                st.markdown(result)

                st.session_state.history.append({
                    "query": user_input,
                    "agent": agent_label,
                    "result": result,
                })

                download_content = (
                    f"Query: {user_input}\n"
                    f"Agent: {agent_label}\n\n"
                    f"Result:\n{result}\n"
                )
                st.download_button(
                    label="⬇️ Download result as text",
                    data=download_content,
                    file_name="agent_result.txt",
                    mime="text/plain",
                )

# ============================================================
# TAB 2: Data Dashboard (CSV upload + charts + advanced stats + AI analysis)
# ============================================================
with tab2:
    st.divider()
    st.subheader("Upload a CSV file")
    st.caption(
        "Upload sales data, HR data, or any tabular dataset. "
        "You'll get summary stats, customizable charts, advanced statistical "
        "analysis, and an optional AI report."
    )

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Could not read CSV file: {e}")
            df = None

        if df is not None:
            st.markdown("#### Data Preview")
            st.dataframe(df.head(20), use_container_width=True)

            st.markdown(f"**Rows:** {len(df)} &nbsp;&nbsp; **Columns:** {len(df.columns)}")

            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

            if numeric_cols:
                st.markdown("#### Summary Statistics")
                st.dataframe(df[numeric_cols].describe(), use_container_width=True)

            # --------------------------------------------------
            # Advanced Statistics (PhD-level)
            # --------------------------------------------------
            if numeric_cols:
                st.divider()
                st.markdown("#### 🎓 Advanced Statistical Analysis")
                st.caption(
                    "Distributional shape, dispersion, and outlier diagnostics "
                    "for each numeric column."
                )

                adv_rows = []
                for col in numeric_cols:
                    series = df[col].dropna()
                    if series.empty:
                        continue
                    q1 = series.quantile(0.25)
                    q3 = series.quantile(0.75)
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    outliers = series[(series < lower_bound) | (series > upper_bound)]

                    adv_rows.append({
                        "Column": col,
                        "Mean": round(series.mean(), 2),
                        "Median": round(series.median(), 2),
                        "Std Dev": round(series.std(), 2),
                        "Variance": round(series.var(), 2),
                        "Skewness": round(series.skew(), 2),
                        "Kurtosis": round(series.kurt(), 2),
                        "IQR": round(iqr, 2),
                        "Outliers (IQR method)": int(len(outliers)),
                        "Missing Values": int(df[col].isna().sum()),
                    })

                adv_df = pd.DataFrame(adv_rows)
                st.dataframe(adv_df, use_container_width=True)

                with st.expander("📖 How to read these metrics"):
                    st.markdown(
                        """
- **Skewness**: 0 = symmetric distribution. Positive = right-skewed (long tail of high values). Negative = left-skewed.
- **Kurtosis**: 0 = normal-like tails. Higher = more extreme outliers than normal distribution.
- **IQR (Interquartile Range)**: Spread of the middle 50% of the data. Used to detect outliers.
- **Outliers (IQR method)**: Values beyond 1.5×IQR from Q1/Q3 — a standard statistical outlier rule.
                        """
                    )

                if len(numeric_cols) >= 2 and PLOTLY_AVAILABLE:
                    st.markdown("##### Correlation Heatmap")
                    corr_matrix = df[numeric_cols].corr().round(2)
                    fig_corr = px.imshow(
                        corr_matrix,
                        text_auto=True,
                        color_continuous_scale="RdBu_r",
                        zmin=-1, zmax=1,
                        aspect="auto",
                        title="Correlation Between Numeric Variables",
                    )
                    st.plotly_chart(fig_corr, use_container_width=True)

            st.divider()
            st.markdown("#### Build a Chart")

            chart_type = st.selectbox(
                "Chart type",
                ["Bar", "Line", "Pie", "Scatter", "Histogram", "Box Plot"],
            )

            col_a, col_b = st.columns(2)

            if chart_type in ["Bar", "Line", "Scatter"]:
                with col_a:
                    x_col = st.selectbox("X-axis (category or numeric)", df.columns.tolist())
                with col_b:
                    y_options = numeric_cols if numeric_cols else df.columns.tolist()
                    y_col = st.selectbox("Y-axis (numeric)", y_options)

                if st.button("Generate Chart", type="primary"):
                    try:
                        if chart_type == "Bar":
                            chart_data = df.groupby(x_col)[y_col].sum().sort_values(ascending=False)
                            st.bar_chart(chart_data)
                        elif chart_type == "Line":
                            chart_data = df.groupby(x_col)[y_col].sum()
                            st.line_chart(chart_data)
                        elif chart_type == "Scatter":
                            st.scatter_chart(df, x=x_col, y=y_col)
                    except Exception as e:
                        st.error(f"Could not generate chart: {e}")

            elif chart_type == "Pie":
                if categorical_cols:
                    pie_col = st.selectbox("Category column", categorical_cols)
                    if st.button("Generate Chart", type="primary"):
                        if not PLOTLY_AVAILABLE:
                            st.error("Plotly is not installed. Run: pip install plotly")
                        else:
                            try:
                                counts = df[pie_col].value_counts().reset_index()
                                counts.columns = [pie_col, "count"]
                                fig = px.pie(counts, names=pie_col, values="count",
                                              title=f"Distribution of {pie_col}")
                                st.plotly_chart(fig, use_container_width=True)
                            except Exception as e:
                                st.error(f"Could not generate pie chart: {e}")
                else:
                    st.info("No categorical columns found for a pie chart.")

            elif chart_type == "Histogram":
                if numeric_cols:
                    hist_col = st.selectbox("Numeric column", numeric_cols)
                    if st.button("Generate Chart", type="primary"):
                        if not PLOTLY_AVAILABLE:
                            st.error("Plotly is not installed. Run: pip install plotly")
                        else:
                            try:
                                fig = px.histogram(
                                    df, x=hist_col, marginal="box", nbins=30,
                                    title=f"Distribution of {hist_col}",
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            except Exception as e:
                                st.error(f"Could not generate histogram: {e}")
                else:
                    st.info("No numeric columns found for a histogram.")

            elif chart_type == "Box Plot":
                if numeric_cols:
                    with col_a:
                        box_y = st.selectbox("Numeric column", numeric_cols)
                    with col_b:
                        group_options = ["(none)"] + categorical_cols
                        box_x = st.selectbox("Group by (optional)", group_options)
                    if st.button("Generate Chart", type="primary"):
                        if not PLOTLY_AVAILABLE:
                            st.error("Plotly is not installed. Run: pip install plotly")
                        else:
                            try:
                                if box_x != "(none)":
                                    fig = px.box(df, x=box_x, y=box_y,
                                                  title=f"{box_y} distribution by {box_x}")
                                else:
                                    fig = px.box(df, y=box_y, title=f"Distribution of {box_y}")
                                st.plotly_chart(fig, use_container_width=True)
                            except Exception as e:
                                st.error(f"Could not generate box plot: {e}")
                else:
                    st.info("No numeric columns found for a box plot.")

            st.divider()
            st.markdown("#### AI Business Report")
            st.caption(
                "Generate a written analysis (key metrics, insights, business "
                "implications, recommendations) based on a summary of this data."
            )

            if st.button("Generate AI Report"):
                summary_parts = [
                    f"Dataset with {len(df)} rows and {len(df.columns)} columns.",
                    f"Columns: {', '.join(df.columns.tolist())}.",
                ]
                if numeric_cols:
                    summary_parts.append("Numeric summary statistics:")
                    summary_parts.append(df[numeric_cols].describe().to_string())
                if categorical_cols:
                    for cat in categorical_cols[:3]:
                        top_vals = df[cat].value_counts().head(5).to_string()
                        summary_parts.append(f"Top values for '{cat}':\n{top_vals}")

                data_summary = "\n".join(summary_parts)

                input_guard = InputSecurityAgent()
                is_safe, msg = input_guard.check(data_summary)

                if not is_safe:
                    st.error(f"REQUEST BLOCKED BY INPUT SECURITY: {msg}")
                else:
                    with st.spinner("Generating AI report..."):
                        agent = DataAnalysisAgent()
                        report = agent.run(data_summary)

                        output_guard = OutputSecurityAgent()
                        is_safe_out, msg_out = output_guard.check(report)

                    if not is_safe_out:
                        st.error(f"OUTPUT BLOCKED BY SECURITY: {msg_out}")
                    else:
                        st.markdown(report)
                        report_content = (
                            f"Dataset summary:\n{data_summary}\n\n"
                            f"AI Business Report:\n{report}"
                        )
                        st.download_button(
                            label="⬇️ Download report as text",
                            data=report_content,
                            file_name="ai_business_report.txt",
                            mime="text/plain",
                        )
