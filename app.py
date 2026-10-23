import pandas as pd
import plotly.express as px
import streamlit as st

from src.risk_engine import (
    load_data,
    filter_records,
    get_summary,
    get_risk_scorecard,
)
from src.generator import generate_answer


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="AgriRisk AI | Agricultural Risk Intelligence",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --forest: #14532d;
        --deep: #064e3b;
        --green: #15803d;
        --mint: #dcfce7;
        --page: #f4f8f3;
        --ink: #173b2c;
        --muted: #64786b;
        --line: #dce8df;
    }

    .stApp {
        background:
            radial-gradient(circle at 92% 2%, rgba(187, 247, 208, 0.25), transparent 25%),
            var(--page);
        color: var(--ink);
        font-family: 'DM Sans', sans-serif;
    }

    [data-testid="stHeader"] {
        background: rgba(244, 248, 243, 0.88);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #e9f5eb 0%, #f5faf5 72%, #e0f0e4 100%);
        border-right: 1px solid #d6e6d9;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.2rem;
    }

    .brand-lockup {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0.35rem 0 0.2rem 0;
    }

    .brand-icon {
        font-size: 2.15rem;
        line-height: 1;
    }

    .brand-name {
        font-family: 'Manrope', sans-serif;
        font-weight: 800;
        font-size: 1.42rem;
        color: #075b40;
        letter-spacing: -0.7px;
    }

    .brand-caption {
        font-size: 0.78rem;
        color: #5b7564;
        margin: 0.1rem 0 0.8rem 0;
    }

    .hero {
        position: relative;
        overflow: hidden;
        border-radius: 22px;
        padding: 1.65rem 1.8rem;
        margin: 0.1rem 0 1.2rem 0;
        color: white;
        background:
            linear-gradient(105deg, rgba(5, 66, 48, 0.97) 0%, rgba(9, 94, 66, 0.92) 48%, rgba(20, 115, 70, 0.76) 100%);
        border: 1px solid rgba(255,255,255,0.38);
        box-shadow: 0 12px 30px rgba(20, 83, 45, 0.13);
    }

    .hero:after {
        content: "🌾";
        position: absolute;
        right: 4%;
        top: 2%;
        font-size: 5.5rem;
        opacity: 0.16;
        transform: rotate(-12deg);
    }

    .hero-kicker {
        color: #bbf7d0;
        font-weight: 700;
        font-size: 0.76rem;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }

    .hero-title {
        font-family: 'Manrope', sans-serif;
        font-size: clamp(2rem, 3vw, 2.7rem);
        line-height: 1.08;
        letter-spacing: -1.2px;
        font-weight: 800;
        margin: 0;
    }

    .hero-copy {
        margin-top: 0.65rem;
        color: #e0f2e5;
        font-size: 1rem;
        max-width: 720px;
        line-height: 1.55;
    }

    .hero-pill {
        display: inline-block;
        margin-top: 0.9rem;
        border: 1px solid rgba(220,252,231,0.42);
        background: rgba(255,255,255,0.1);
        padding: 0.4rem 0.7rem;
        border-radius: 999px;
        font-size: 0.78rem;
        color: #f0fdf4;
    }

    .section-heading {
        font-family: 'Manrope', sans-serif;
        color: #124b35;
        font-size: 1.25rem;
        font-weight: 800;
        letter-spacing: -0.35px;
        margin: 0.25rem 0 0.1rem 0;
    }

    .section-copy {
        color: var(--muted);
        font-size: 0.9rem;
        margin-bottom: 0.9rem;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff, #f8fcf8);
        border: 1px solid var(--line);
        padding: 1.05rem 1.15rem;
        border-radius: 17px;
        box-shadow: 0 5px 16px rgba(21, 72, 42, 0.045);
        min-height: 125px;
    }

    div[data-testid="stMetricLabel"] {
        color: #577061;
        font-weight: 600;
        font-size: 0.86rem;
    }

    div[data-testid="stMetricValue"] {
        color: #14532d;
        font-family: 'Manrope', sans-serif;
        font-weight: 800;
        letter-spacing: -0.8px;
    }

    div[data-testid="stMetricDelta"] {
        font-size: 0.76rem;
    }

    div[data-testid="stTabs"] button {
        border-radius: 10px 10px 0 0;
        font-weight: 700;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #0f6b45;
    }

    div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        background-color: #16835b;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #dce8df;
        border-radius: 16px;
    }

    .insight-box {
        border: 1px solid #cce8d5;
        background: linear-gradient(135deg, #e8f7ec, #f8fcf8);
        padding: 1rem 1.1rem;
        border-radius: 16px;
        margin: 0.3rem 0 0.8rem 0;
    }

    .insight-title {
        color: #14532d;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }

    .small-note {
        color: #718278;
        font-size: 0.78rem;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(100deg, #15803d, #0f6b4a);
        border: 0;
        border-radius: 10px;
        font-weight: 700;
        min-height: 2.75rem;
        box-shadow: 0 4px 12px rgba(21, 128, 61, 0.16);
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(100deg, #166534, #064e3b);
        border: 0;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #dce8df;
        border-radius: 12px;
        overflow: hidden;
    }

    .stDownloadButton > button {
        border-radius: 10px;
        font-weight: 700;
        border-color: #a7d7b5;
        color: #14532d;
    }

    hr {
        border-color: #d8e7dc;
    }

    @media (max-width: 768px) {
        .hero { padding: 1.2rem; }
        .hero-title { font-size: 1.9rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def get_data():
    return load_data()


try:
    df = get_data()
except Exception as exc:
    st.error(f"Could not load the agricultural dataset: {exc}")
    st.stop()

if df.empty:
    st.error("The dataset is empty.")
    st.stop()


# Automatically identify a year column (case-insensitive).
year_lookup = {str(column).strip().lower(): column for column in df.columns}
year_candidates = ["year", "record_year", "data_year", "harvest_year", "season_year"]
year_column = next((year_lookup[name] for name in year_candidates if name in year_lookup), None)

if year_column is None:
    year_column = next(
        (column for column in df.columns if "year" in str(column).strip().lower()),
        None,
    )


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.markdown(
    """
    <div class="brand-lockup">
        <div class="brand-icon">🌱</div>
        <div class="brand-name">AgriRisk AI</div>
    </div>
    <div class="brand-caption">Agricultural Risk Intelligence</div>
    """,
    unsafe_allow_html=True,
)
st.sidebar.divider()
st.sidebar.markdown("### ⚙️ Dashboard Filters")
st.sidebar.caption("Choose the records you want to analyze.")

if "country" in df.columns:
    countries = sorted(df["country"].dropna().astype(str).unique().tolist())
    selected_country = st.sidebar.selectbox("🌍 Country", ["All"] + countries)
else:
    selected_country = "All"

if "crop" in df.columns:
    crops = sorted(df["crop"].dropna().astype(str).unique().tolist())
    selected_crop = st.sidebar.selectbox("🌾 Crop", ["All"] + crops)
else:
    selected_crop = "All"

selected_year = "All"
if year_column is not None:
    year_values = pd.to_numeric(df[year_column], errors="coerce").dropna()
    years = sorted(year_values.astype(int).unique().tolist(), reverse=True)
    selected_year = st.sidebar.selectbox(
        "📅 Year",
        options=["All"] + years,
        index=0,
        help="Filter the dashboard by the selected year.",
    )
else:
    st.sidebar.info("No year column was detected in the supplied dataset.")

st.sidebar.divider()

# Show a small dataset summary in the sidebar.
st.sidebar.markdown("### 📌 Dataset Snapshot")
st.sidebar.metric("Total records", f"{len(df):,}")
st.sidebar.caption("Use the dropdowns above to filter the dashboard.")
st.sidebar.markdown(
    """
    <div class="insight-box">
        <div class="insight-title">🌿 Data note</div>
        <span class="small-note">This dashboard summarizes the supplied dataset. It does not provide live farm monitoring or independently validated forecasts.</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------
filtered_df = filter_records(df, country=selected_country, crop=selected_crop)

if selected_year != "All" and year_column is not None:
    numeric_years = pd.to_numeric(filtered_df[year_column], errors="coerce")
    filtered_df = filtered_df[numeric_years == int(selected_year)]

if filtered_df.empty:
    st.warning("No records match the selected filters. Please change one or more filters.")
    st.stop()


# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
        <div class="hero-kicker">Agricultural risk intelligence platform</div>
        <div class="hero-title">AgriRisk AI</div>
        <div class="hero-copy">
            Understand agricultural risk patterns, explore dataset insights,
            and retrieve supporting advisory information to inform smarter decisions.
        </div>
        <div class="hero-pill">🌱 Data-driven insights &nbsp; • &nbsp; 🌾 Smarter farming decisions</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    f"Current selection  ·  Country: **{selected_country}**  ·  "
    f"Crop: **{selected_crop}**  ·  Year: **{selected_year}**"
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Risk Overview", "🎯 Risk Scorecard", "🤖 AI Advisory", "🔎 Explore Dataset"]
)


# --------------------------------------------------
# TAB 1: RISK OVERVIEW
# --------------------------------------------------
with tab1:
    st.markdown('<div class="section-heading">Agricultural Risk Overview</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">A quick view of the selected records, risk distribution, and recorded indicators.</div>',
        unsafe_allow_html=True,
    )

    total_records = len(filtered_df)
    if "risk_category" in filtered_df.columns:
        risk_counts = filtered_df["risk_category"].value_counts()
        high_critical = (
            filtered_df["risk_category"].astype(str).str.strip().str.lower()
            .isin(["high", "critical"]).sum()
        )
        high_critical_pct = high_critical / total_records * 100 if total_records else 0
    else:
        risk_counts = pd.Series(dtype=int)
        high_critical_pct = 0

    def average_of(column):
        if column in filtered_df.columns:
            return pd.to_numeric(filtered_df[column], errors="coerce").mean()
        return float("nan")

    climate_avg = average_of("climate_stress_index")
    disease_avg = average_of("disease_risk_score")
    pest_avg = average_of("pest_risk_score")

    metric_columns = st.columns(4)
    metric_columns[0].metric("📚 Records Analyzed", f"{total_records:,}", help="Records after applying the sidebar filters.")
    metric_columns[1].metric("🚨 High / Critical Risk", f"{high_critical_pct:.2f}%", help="Share of selected records labelled High or Critical.")
    metric_columns[2].metric("🌡️ Avg. Climate Stress", f"{climate_avg:.2f}" if pd.notna(climate_avg) else "N/A")
    metric_columns[3].metric("🦠 Avg. Disease Risk", f"{disease_avg:.2f}" if pd.notna(disease_avg) else "N/A")

    st.write("")
    left, right = st.columns([1, 1.15], gap="large")

    with left:
        with st.container(border=True):
            st.markdown("#### 🧭 Risk Category Distribution")
            if not risk_counts.empty:
                risk_chart = risk_counts.rename_axis("Risk Category").reset_index(name="Records")
                fig = px.pie(
                    risk_chart,
                    names="Risk Category",
                    values="Records",
                    hole=0.62,
                    color="Risk Category",
                    color_discrete_map={
                        "Low": "#36a66a",
                        "Moderate": "#f4c542",
                        "High": "#f28c45",
                        "Critical": "#e45454",
                    },
                )
                fig.update_traces(
                    textposition="outside",
                    textinfo="percent",
                    hovertemplate="<b>%{label}</b><br>Records: %{value:,}<br>Share: %{percent}<extra></extra>",
                    marker=dict(line=dict(color="#ffffff", width=3)),
                )
                fig.update_layout(
                    margin=dict(t=10, b=10, l=10, r=10),
                    legend_title_text="Risk level",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="DM Sans, sans-serif", color="#294c39"),
                    showlegend=True,
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Risk category data is unavailable.")

    with right:
        with st.container(border=True):
            st.markdown("#### 📈 Average Risk Indicators")
            indicator_columns = [
                column for column in
                ["climate_stress_index", "disease_risk_score", "pest_risk_score"]
                if column in filtered_df.columns
            ]
            if indicator_columns:
                indicator_data = pd.DataFrame({
                    "Indicator": [column.replace("_", " ").title() for column in indicator_columns],
                    "Average": [
                        pd.to_numeric(filtered_df[column], errors="coerce").mean()
                        for column in indicator_columns
                    ],
                }).dropna(subset=["Average"])
                fig = px.bar(
                    indicator_data,
                    x="Indicator",
                    y="Average",
                    text_auto=".2f",
                    color="Indicator",
                    color_discrete_sequence=["#48a868", "#f3bd3d", "#4298db"],
                )
                fig.update_traces(
                    textposition="outside",
                    marker_line_width=0,
                    hovertemplate="%{x}<br>Average: %{y:.2f}<extra></extra>",
                )
                fig.update_layout(
                    margin=dict(t=20, b=15, l=10, r=10),
                    xaxis_title="",
                    yaxis_title="Average score",
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="DM Sans, sans-serif", color="#294c39"),
                    yaxis=dict(gridcolor="#e5eee7", zeroline=False),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Risk indicator columns are unavailable.")

    action_col, insight_col = st.columns([1.15, 1], gap="large")

    with action_col:
        with st.container(border=True):
            st.markdown("#### 🛠️ Most Frequently Recorded Actions")
            if "recommended_action" in filtered_df.columns:
                actions = (
                    filtered_df["recommended_action"].dropna().astype(str).value_counts()
                    .head(5).rename_axis("Recommended Action").reset_index(name="Records")
                )
                if not actions.empty:
                    action_fig = px.bar(
                        actions.sort_values("Records", ascending=True),
                        x="Records",
                        y="Recommended Action",
                        orientation="h",
                        text="Records",
                    )
                    action_fig.update_traces(
                        marker_color="#269b75",
                        texttemplate="%{text:,}",
                        textposition="outside",
                        cliponaxis=False,
                        hovertemplate="%{y}<br>Records: %{x:,}<extra></extra>",
                    )
                    action_fig.update_layout(
                        margin=dict(t=10, b=10, l=5, r=35),
                        xaxis_title="Number of records",
                        yaxis_title="",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="DM Sans, sans-serif", color="#294c39"),
                        xaxis=dict(gridcolor="#e5eee7", zeroline=False),
                    )
                    st.plotly_chart(action_fig, use_container_width=True)
                else:
                    st.info("No recommended actions are available.")
            else:
                st.info("The recommended_action column is unavailable.")

    with insight_col:
        with st.container(border=True):
            st.markdown("#### 💡 Key Insights")
            if not risk_counts.empty:
                dominant_risk = risk_counts.idxmax()
                dominant_count = int(risk_counts.max())
                dominant_pct = dominant_count / total_records * 100 if total_records else 0
                st.markdown(
                    f"""
                    <div class="insight-box">
                        <div class="insight-title">Most common risk category</div>
                        <div><b>{dominant_risk}</b> represents {dominant_pct:.2f}% of the selected records ({dominant_count:,} rows).</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            indicators = {
                "Climate stress": climate_avg,
                "Disease risk": disease_avg,
                "Pest risk": pest_avg,
            }
            valid_indicators = {k: v for k, v in indicators.items() if pd.notna(v)}
            if valid_indicators:
                highest_indicator = max(valid_indicators, key=valid_indicators.get)
                st.write(f"• **Highest average indicator:** {highest_indicator} ({valid_indicators[highest_indicator]:.2f}).")

            if "recommended_action" in filtered_df.columns:
                top_action = filtered_df["recommended_action"].dropna().astype(str).value_counts()
                if not top_action.empty:
                    st.write(f"• **Most recorded action:** {top_action.index[0]} ({int(top_action.iloc[0]):,} records).")

            st.caption("These are descriptive statistics from the supplied dataset, not calibrated predictions of future crop failure.")


# --------------------------------------------------
# TAB 2: RISK SCORECARD
# --------------------------------------------------
with tab2:
    st.markdown('<div class="section-heading">Risk Scorecard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">A compact summary of the risk metrics calculated for the current selection.</div>',
        unsafe_allow_html=True,
    )

    scorecard = get_risk_scorecard(filtered_df)
    if isinstance(scorecard, dict):
        score_columns = st.columns(min(max(len(scorecard), 1), 4))
        for index, (label, value) in enumerate(scorecard.items()):
            with score_columns[index % len(score_columns)]:
                if isinstance(value, float):
                    display_value = f"{value:.2f}"
                else:
                    display_value = f"{value:,}" if isinstance(value, int) else str(value)
                st.metric(label.replace("_", " ").title(), display_value)

        with st.expander("View scorecard values as structured data"):
            st.json(scorecard)
    else:
        st.write(scorecard)

    with st.container(border=True):
        st.markdown("#### 📋 Filtered Dataset Summary")
        st.write(f"Records in the current selection: **{len(filtered_df):,}**")
        if "risk_category" in filtered_df.columns:
            summary = (
                filtered_df["risk_category"].value_counts()
                .rename_axis("Risk Category").reset_index(name="Records")
            )
            summary["Share (%)"] = (summary["Records"] / len(filtered_df) * 100).round(2)
            st.dataframe(summary, use_container_width=True, hide_index=True)



# --------------------------------------------------
# TAB 3: AI ADVISORY
# --------------------------------------------------
with tab3:
    st.markdown(
        '<div class="section-heading">Agricultural Risk Advisory</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-copy">Ask a question about agricultural risks and inspect the supporting advisory references.</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("#### 💬 What would you like to understand?")

        suggested_questions = [
            "Choose a suggested question...",
            "What actions can help manage high pest risk?",
            "How can farmers reduce disease risk?",
            "What factors contribute to high climate stress?",
            "What actions are recommended for high-risk crops?",
            "How can farmers prepare for agricultural climate risks?",
            "Summarize the main risks for the selected country and crop.",
        ]

        selected_question = st.selectbox(
            "Suggested questions",
            options=suggested_questions,
            key="suggested_question",
        )

        question = st.text_area(
            "Enter your question",
            placeholder="Select a suggested question above or type your own...",
            height=110,
            key="agri_question",
            label_visibility="collapsed",
        )

        final_question = question.strip()

        if (
            not final_question
            and selected_question != "Choose a suggested question..."
        ):
            final_question = selected_question

        st.caption(
            f"Current context: {selected_country} · "
            f"{selected_crop} · {selected_year}"
        )

        if st.button(
            "✨ Generate Advisory",
            type="primary",
            use_container_width=True,
        ):
            if not final_question:
                st.warning(
                    "Please enter a question or select a suggestion first."
                )
            else:
                with st.spinner(
                    "Analyzing dataset insights and retrieving advisory information..."
                ):
                    try:
                        result = generate_answer(
                            final_question,
                            country=selected_country,
                            crop=selected_crop,
                        )

                        st.session_state["advisory_result"] = result
                        st.session_state["advisory_question"] = final_question

                    except Exception as exc:
                        st.error(f"Unable to generate advisory: {exc}")

    result = st.session_state.get("advisory_result")

    if result:
        with st.container(border=True):
            st.markdown("#### 🌿 Advisory Response")

            if isinstance(result, dict):
                answer = result.get("answer", "No answer was returned.")
                citations = result.get("citations", [])

                st.markdown(answer)

                if citations:
                    st.markdown("#### 📚 Supporting References")

                    for citation in citations:
                        ref_id = citation.get("id", "Reference")
                        topic = citation.get("topic", "Agricultural advisory")

                        with st.expander(f"📄 {ref_id} — {topic}"):
                            st.write(citation.get("text", ""))

                            source = citation.get("source")
                            if source:
                                st.caption(f"Source: {source}")

                            url = citation.get("url")
                            if isinstance(url, str) and url.startswith(
                                ("https://", "http://")
                            ):
                                st.markdown(f"[Open source ↗]({url})")

                            similarity = citation.get("similarity")
                            if isinstance(similarity, (float, int)):
                                st.caption(
                                    f"Retrieval similarity: {similarity:.3f}"
                                )

                st.info(
                    "Advisory content is informational. Verify recommendations "
                    "with authoritative agricultural sources before making "
                    "farming decisions."
                )
            else:
                st.write(result)



# --------------------------------------------------
# TAB 4: EXPLORE DATASET
# --------------------------------------------------
with tab4:
    st.markdown('<div class="section-heading">Explore Agricultural Dataset</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Search, inspect, and export the records that match your sidebar filters.</div>',
        unsafe_allow_html=True,
    )

    st.metric("Records in current selection", f"{len(filtered_df):,}")
    search_text = st.text_input(
        "🔎 Search within the filtered dataset",
        placeholder="Search for a country, crop, risk category, or action...",
    )

    display_df = filtered_df.copy()
    if search_text.strip():
        text_columns = display_df.select_dtypes(include=["object", "string"]).columns
        if len(text_columns) > 0:
            matches = display_df[text_columns].apply(
                lambda column: column.astype(str).str.contains(
                    search_text, case=False, na=False, regex=False
                )
            ).any(axis=1)
            display_df = display_df[matches]

    st.caption(f"Showing {len(display_df):,} matching records.")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    csv_data = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Dataset as CSV",
        data=csv_data,
        file_name="agririsk_filtered_dataset.csv",
        mime="text/csv",
    )

    st.caption(
        "Dataset-derived results describe the supplied records; they are not independently validated real-time forecasts."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()
st.markdown(
    """
    <div style="text-align:center; color:#718278; font-size:0.8rem; padding:0.3rem 0 0.8rem 0;">
        🌱 <b>AgriRisk AI</b> · Agricultural Risk Intelligence · Built for data-driven exploration
    </div>
    """,
    unsafe_allow_html=True,
)
