
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
    page_title="AgriRisk AI",
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
    :root {
        --forest: #205c3b;
        --leaf: #2f8554;
        --line: #dce9dc;
    }
    .stApp {
        background: linear-gradient(135deg, #f7faf5 0%, #eef5eb 100%);
        color: #24352a;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #e5f0e1 0%, #f0f6ed 100%);
        border-right: 1px solid #d7e5d3;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
        color: var(--forest);
    }
    .main-title {
        color: var(--forest);
        font-size: 2.55rem;
        font-weight: 850;
        letter-spacing: -1px;
        margin-bottom: 0;
        line-height: 1.15;
    }
    .subtitle {
        color: #607565;
        font-size: 1rem;
        margin: .35rem 0 1rem 0;
    }
    h1, h2, h3, h4 { color: #244b32; }
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff 0%, #f8fcf7 100%);
        border: 1px solid var(--line);
        border-left: 4px solid #4a9560;
        padding: 17px 18px;
        border-radius: 14px;
        box-shadow: 0 4px 14px rgba(36, 84, 48, .055);
        transition: transform .18s ease, box-shadow .18s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(36, 84, 48, .10);
    }
    div[data-testid="stMetricLabel"] { color: #617565; font-weight: 600; }
    div[data-testid="stMetricValue"] { color: #205c3b; font-weight: 800; }
    div[data-testid="stTabs"] button {
        border-radius: 10px 10px 0 0;
        font-weight: 650;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #205c3b;
        border-bottom-color: #2f8554;
    }
    div[data-testid="stPlotlyChart"] {
        background: rgba(255,255,255,.88);
        border: 1px solid #e1ebe0;
        border-radius: 14px;
        padding: 8px;
        box-shadow: 0 3px 12px rgba(36,84,48,.035);
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #dce9dc;
        border-radius: 12px;
        overflow: hidden;
    }
    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(90deg, #246b43, #398957);
        color: white;
        border: 0;
        border-radius: 10px;
        font-weight: 650;
        padding: .55rem 1rem;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: #1e5736;
        color: white;
        border: 0;
    }
    [data-testid="stAlert"] { border-radius: 12px; }
    hr { border-color: #dce9dc; }
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
# A year dropdown can only filter data if the dataset actually contains a year field.
year_lookup = {str(column).strip().lower(): column for column in df.columns}
year_candidates = [
    "year",
    "record_year",
    "data_year",
    "harvest_year",
    "season_year",
]

year_column = next(
    (year_lookup[name] for name in year_candidates if name in year_lookup),
    None,
)

# Also support other column names containing "year", e.g. "planting_year".
if year_column is None:
    year_column = next(
        (
            column for column in df.columns
            if "year" in str(column).strip().lower()
        ),
        None,
    )


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.title("🌱 AgriRisk AI")
st.sidebar.caption("Agricultural Risk Intelligence")
st.sidebar.divider()

st.sidebar.subheader("Filter Data")

# Country dropdown
if "country" in df.columns:
    countries = sorted(
        df["country"].dropna().astype(str).unique().tolist()
    )
    selected_country = st.sidebar.selectbox(
        "Select Country",
        ["All"] + countries,
    )
else:
    selected_country = "All"

# Crop dropdown
if "crop" in df.columns:
    crops = sorted(
        df["crop"].dropna().astype(str).unique().tolist()
    )
    selected_crop = st.sidebar.selectbox(
        "Select Crop",
        ["All"] + crops,
    )
else:
    selected_crop = "All"

# Year dropdown
selected_year = "All"

if year_column is not None:
    available_years = pd.to_numeric(
        df[year_column], errors="coerce"
    ).dropna()

    years = sorted(
        available_years.astype(int).unique().tolist(),
        reverse=True,
    )

    selected_year = st.sidebar.selectbox(
        "Select Year",
        options=["All"] + years,
        index=0,
        help="Choose a year to filter the dashboard.",
    )
else:
    st.sidebar.info(
        "A year dropdown is unavailable because no year column "
        "was detected in the dataset."
    )

st.sidebar.divider()
st.sidebar.caption("Data-driven insights and advisory support")


# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------
filtered_df = filter_records(
    df,
    country=selected_country,
    crop=selected_crop,
)

if selected_year != "All" and year_column is not None:
    year_values = pd.to_numeric(
        filtered_df[year_column], errors="coerce"
    )
    filtered_df = filtered_df[year_values == selected_year]

if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()


# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown(
    '<div class="main-title">🌱 AgriRisk AI</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">'
    'Agricultural Risk Intelligence <span style="color:#9bb7a0;">|</span> '
    'Data-driven insights for smarter farming'
    '</div>',
    unsafe_allow_html=True,
)

filter_description = (
    f"Country: {selected_country}  |  "
    f"Crop: {selected_crop}  |  "
    f"Year: {selected_year}"
)
st.caption(filter_description)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Risk Overview",
        "🎯 Risk Scorecard",
        "🤖 AI Advisory",
        "🔎 Explore Dataset",
    ]
)


# --------------------------------------------------
# TAB 1: RISK OVERVIEW
# --------------------------------------------------
with tab1:
    st.subheader("Agricultural Risk Overview")

    total_records = len(filtered_df)

    if "risk_category" in filtered_df.columns:
        risk_counts = filtered_df["risk_category"].value_counts()
        high_critical = (
            filtered_df["risk_category"]
            .astype(str)
            .str.strip()
            .str.lower()
            .isin(["high", "critical"])
            .sum()
        )
        high_critical_pct = (
            high_critical / total_records * 100
            if total_records else 0
        )
    else:
        risk_counts = pd.Series(dtype=int)
        high_critical_pct = 0

    metric_columns = st.columns(4)

    metric_columns[0].metric(
        "Records Analyzed",
        f"{total_records:,}",
    )
    metric_columns[1].metric(
        "High/Critical Risk",
        f"{high_critical_pct:.2f}%",
    )

    if "climate_stress_index" in filtered_df.columns:
        climate_avg = pd.to_numeric(
            filtered_df["climate_stress_index"],
            errors="coerce",
        ).mean()
    else:
        climate_avg = float("nan")

    if "disease_risk_score" in filtered_df.columns:
        disease_avg = pd.to_numeric(
            filtered_df["disease_risk_score"],
            errors="coerce",
        ).mean()
    else:
        disease_avg = float("nan")

    metric_columns[2].metric(
        "Avg. Climate Stress",
        f"{climate_avg:.2f}" if pd.notna(climate_avg) else "N/A",
    )
    metric_columns[3].metric(
        "Avg. Disease Risk",
        f"{disease_avg:.2f}" if pd.notna(disease_avg) else "N/A",
    )

    left, right = st.columns(2)

    with left:
        st.markdown("#### Risk Category Distribution")

        if not risk_counts.empty:
            risk_chart = risk_counts.rename_axis(
                "Risk Category"
            ).reset_index(name="Records")

            fig = px.pie(
                risk_chart,
                names="Risk Category",
                values="Records",
                hole=0.48,
            )
            fig.update_layout(
                margin=dict(t=20, b=20, l=10, r=10)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Risk category data is unavailable.")

    with right:
        st.markdown("#### Average Risk Indicators")

        indicator_columns = [
            column
            for column in [
                "climate_stress_index",
                "disease_risk_score",
                "pest_risk_score",
            ]
            if column in filtered_df.columns
        ]

        if indicator_columns:
            indicator_data = pd.DataFrame({
                "Indicator": [
                    column.replace("_", " ").title()
                    for column in indicator_columns
                ],
                "Average": [
                    pd.to_numeric(
                        filtered_df[column], errors="coerce"
                    ).mean()
                    for column in indicator_columns
                ],
            })

            fig = px.bar(
                indicator_data,
                x="Indicator",
                y="Average",
                text_auto=".2f",
            )
            fig.update_layout(
                margin=dict(t=20, b=20, l=10, r=10),
                xaxis_title="",
                yaxis_title="Average Score",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Risk indicator columns are unavailable.")

    st.markdown("#### Recommended Actions")

    if "recommended_action" in filtered_df.columns:
        actions = (
            filtered_df["recommended_action"]
            .dropna()
            .astype(str)
            .value_counts()
            .head(5)
            .rename_axis("Recommended Action")
            .reset_index(name="Records")
        )

        if not actions.empty:
            st.dataframe(
                actions,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No recommended actions are available.")


# --------------------------------------------------
# TAB 2: RISK SCORECARD
# --------------------------------------------------
with tab2:
    st.subheader("Risk Scorecard")

    scorecard = get_risk_scorecard(filtered_df)

    if isinstance(scorecard, dict):
        # Clean summary cards — avoid showing the raw nested JSON.
        risk_distribution = scorecard.get("risk_distribution", {})
        indicator_averages = scorecard.get("indicator_averages", {})
        top_actions = scorecard.get("top_actions", {})

        total_scorecard_records = int(
            scorecard.get("records", len(filtered_df))
        )
        high_critical_pct = float(
            scorecard.get("high_critical_percent", 0)
        )
        most_common_risk = (
            max(risk_distribution, key=risk_distribution.get)
            if isinstance(risk_distribution, dict) and risk_distribution
            else "N/A"
        )
        leading_action = (
            max(top_actions, key=top_actions.get)
            if isinstance(top_actions, dict) and top_actions
            else "N/A"
        )

        metric_cols = st.columns(4)
        metric_cols[0].metric("Records Analyzed", f"{total_scorecard_records:,}")
        metric_cols[1].metric("High / Critical Risk", f"{high_critical_pct:.2f}%")
        metric_cols[2].metric("Most Common Risk", most_common_risk)
        metric_cols[3].metric("Risk Categories", len(risk_distribution))

        st.caption(
            f"Leading recommendation: **{leading_action}**"
            if leading_action != "N/A"
            else "Risk summary for the current filters."
        )

        left, right = st.columns(2)

        with left:
            st.markdown("#### Risk Distribution")
            if isinstance(risk_distribution, dict) and risk_distribution:
                risk_df = pd.DataFrame({
                    "Risk Category": list(risk_distribution.keys()),
                    "Records": list(risk_distribution.values()),
                })
                risk_order = ["Low", "Moderate", "High", "Critical"]
                risk_df["_order"] = risk_df["Risk Category"].map(
                    {name: i for i, name in enumerate(risk_order)}
                ).fillna(len(risk_order))
                risk_df = risk_df.sort_values("_order").drop(columns="_order")
                fig = px.bar(
                    risk_df,
                    x="Risk Category",
                    y="Records",
                    color="Risk Category",
                    color_discrete_map={
                        "Low": "#6aa56b",
                        "Moderate": "#b5cc72",
                        "High": "#e6a23c",
                        "Critical": "#c94c4c",
                    },
                    text_auto=True,
                )
                fig.update_layout(
                    showlegend=False,
                    margin=dict(t=15, b=15, l=10, r=10),
                    xaxis_title="",
                    yaxis_title="Number of Records",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Risk distribution is unavailable.")

        with right:
            st.markdown("#### Indicator Averages")
            if isinstance(indicator_averages, dict) and indicator_averages:
                indicator_df = pd.DataFrame({
                    "Indicator": list(indicator_averages.keys()),
                    "Average Score": list(indicator_averages.values()),
                })
                fig = px.bar(
                    indicator_df,
                    x="Indicator",
                    y="Average Score",
                    color_discrete_sequence=["#438653"],
                    text_auto=".2f",
                )
                fig.update_layout(
                    showlegend=False,
                    margin=dict(t=15, b=15, l=10, r=10),
                    xaxis_title="",
                    yaxis_title="Average Score",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Indicator averages are unavailable.")

        st.markdown("#### Top Recommended Actions")
        if isinstance(top_actions, dict) and top_actions:
            actions_df = pd.DataFrame({
                "Recommended Action": list(top_actions.keys()),
                "Records": list(top_actions.values()),
            })
            st.dataframe(
                actions_df,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Recommended action data is unavailable.")
    else:
        st.write(scorecard)

    st.markdown("#### Filtered Dataset Summary")
    st.write(f"Records in the current selection: **{len(filtered_df):,}**")

    if "risk_category" in filtered_df.columns:
        st.dataframe(
            filtered_df["risk_category"]
            .value_counts()
            .rename_axis("Risk Category")
            .reset_index(name="Records"),
            use_container_width=True,
            hide_index=True,
        )


# --------------------------------------------------
# TAB 3: AI ADVISORY
# --------------------------------------------------
with tab3:
    st.subheader("Agricultural Risk Advisory")

    st.caption(
        "Ask a question about agricultural risks, climate stress, "
        "disease, pests, or recommended actions."
    )

    # Suggested questions dropdown — keeps the existing dashboard theme.
    suggested_questions = [
        "What actions can help manage high pest risk?",
        "What does the dataset show about climate stress?",
        "How can farmers respond to high disease risk?",
        "What are the most frequently recorded recommended actions?",
        "Compare the recorded risk categories for my selected filters.",
        "What irrigation-related actions are recommended in the dataset?",
        "Summarize the main agricultural risks in the selected records.",
        "Which risk category appears most often in the selected records?",
        "What is the average disease risk for the selected crop and country?",
        "Which risk indicator has the highest average value in the selected records?",
    ]

    selected_suggestion = st.selectbox(
        "Suggested questions",
        options=["Choose a suggested question..."] + suggested_questions,
        index=0,
        key="suggested_question",
    )

    if st.button("Use Suggested Question", key="use_suggested_question"):
        if selected_suggestion != "Choose a suggested question...":
            # Set this before the text area is created on this rerun.
            st.session_state["agri_question"] = selected_suggestion

    question = st.text_area(
        "Enter your question",
        placeholder=(
            "Example: What actions can help manage high pest risk?"
        ),
        height=100,
        key="agri_question",
    )

    if st.button("Generate Advisory", type="primary"):
        if not question.strip():
            st.warning("Please enter a question first.")
        else:
            with st.spinner("Analyzing advisory information..."):
                try:
                    result = generate_answer(
                        question,
                        country=selected_country,
                        crop=selected_crop,
                    )

                    st.session_state["advisory_result"] = result

                except Exception as exc:
                    st.error(f"Unable to generate advisory: {exc}")

    result = st.session_state.get("advisory_result")

    if result:
        st.markdown("#### Advisory Response")

        if isinstance(result, dict):
            answer = result.get("answer", "No answer was returned.")
            citations = result.get("citations", [])
            st.markdown(answer)

            if citations:
                st.markdown("#### Supporting References")

                for citation in citations:
                    with st.expander(
                        f"{citation.get('id', 'Reference')} — "
                        f"{citation.get('topic', 'Agricultural advisory')}"
                    ):
                        st.write(citation.get("text", ""))

                        source = citation.get("source")
                        if source:
                            st.caption(f"Source: {source}")

                        url = citation.get("url")
                        if isinstance(url, str) and url.startswith(
                            ("https://", "http://")
                        ):
                            st.markdown(f"[Open source]({url})")

            st.caption(
                "Advisory content is informational. Verify "
                "recommendations with authoritative agricultural "
                "sources before making farming decisions."
            )
        else:
            st.write(result)


# --------------------------------------------------
# TAB 4: EXPLORE DATASET
# --------------------------------------------------
with tab4:
    st.subheader("Explore Agricultural Dataset")

    st.write(
        f"Showing **{len(filtered_df):,}** records "
        "after applying the sidebar filters."
    )

    search_text = st.text_input(
        "Search within the filtered dataset",
        placeholder="Search for a country, crop, risk category, or action...",
    )

    display_df = filtered_df.copy()

    if search_text.strip():
        text_columns = display_df.select_dtypes(
            include=["object", "string"]
        ).columns

        if len(text_columns) > 0:
            matches = display_df[text_columns].apply(
                lambda column: column.astype(str).str.contains(
                    search_text,
                    case=False,
                    na=False,
                    regex=False,
                )
            ).any(axis=1)

            display_df = display_df[matches]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    csv_data = display_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Filtered Dataset as CSV",
        data=csv_data,
        file_name="agririsk_filtered_dataset.csv",
        mime="text/csv",
    )

    st.caption(
        "Dataset-derived results describe the supplied records; "
        "they are not independently validated real-time forecasts."
    )