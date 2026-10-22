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

# PAGE CONFIGURATION
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
        color: #173b2c;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.2rem;
    }

    /* Sidebar text visibility */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #173b2c !important;
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

    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] p {
        color: #577061 !important;
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

    /* FIX: readable active and inactive tab labels */
    div[data-testid="stTabs"] button {
        border-radius: 10px 10px 0 0;
        font-weight: 700;
        color: #355746 !important;
        opacity: 1 !important;
    }

    div[data-testid="stTabs"] button p,
    div[data-testid="stTabs"] button span,
    div[data-testid="stTabs"] button div {
        color: #355746 !important;
        opacity: 1 !important;
    }

    div[data-testid="stTabs"] button[aria-selected="true"],
    div[data-testid="stTabs"] button[aria-selected="true"] p,
    div[data-testid="stTabs"] button[aria-selected="true"] span,
    div[data-testid="stTabs"] button[aria-selected="true"] div {
        color: #0f6b45 !important;
        opacity: 1 !important;
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
        .hero {
            padding: 1.2rem;
        }

        .hero-title {
            font-size: 1.9rem;
        }
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
year_lookup = {
    str(column).strip().lower(): column
    for column in df.columns
}

year_candidates = [
    "year",
    "record_year",
    "data_year",
    "harvest_year",
    "season_year",
]

year_column = next(
    (
        year_lookup[name]
        for name in year_candidates
        if name in year_lookup
    ),
    None,
)

if year_column is None:
    year_column = next(
        (
            column
            for column in df.columns
            if "year" in str(column).strip().lower()
        ),
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
    countries = sorted(
        df["country"].dropna().astype(str).unique().tolist()
    )
    selected_country = st.sidebar.selectbox(
        "🌍 Country",
        ["All"] + countries,
    )
else:
    selected_country = "All"


if "crop" in df.columns:
    crops = sorted(
        df["crop"].dropna().astype(str).unique().tolist()
    )
    selected_crop = st.sidebar.selectbox(
        "🌾 Crop",
        ["All"] + crops,
    )
else:
    selected_crop = "All"


selected_year = "All"

if year_column is not None:
    year_values = pd.to_numeric(
        df[year_column],
        errors="coerce",
    ).dropna()

    years = sorted(
        year_values.astype(int).unique().tolist(),
        reverse=True,
    )

    selected_year = st.sidebar.selectbox(
        "📅 Year",
        options=["All"] + years,
        index=0,
        help="Filter the dashboard by the selected year.",
    )
else:
    st.sidebar.info(
        "No year column was detected in the supplied dataset."
    )


st.sidebar.divider()

# Dataset snapshot
st.sidebar.markdown("### 📌 Dataset Snapshot")
st.sidebar.metric("Total records", f"{len(df):,}")

st.sidebar.caption(
    "Use the dropdowns above to filter the dashboard."
)

st.sidebar.markdown(
    """
    <div class="insight-box">
        <div class="insight-title">🌿 Data note</div>
        <span class="small-note">
            This dashboard summarizes the supplied dataset.
            It does not provide live farm monitoring or
            independently validated forecasts.
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)
# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------
filtered_df = filter_records(
    df,
    country=selected_country,
    crop=selected_crop,
)

if selected_year != "All" and year_column is not None:
    numeric_years = pd.to_numeric(
        filtered_df[year_column],
        errors="coerce",
    )
    filtered_df = filtered_df[
        numeric_years == int(selected_year)
    ]

if filtered_df.empty:
    st.warning(
        "No records match the selected filters. "
        "Please change one or more filters."
    )
    st.stop()


# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
        <div class="hero-kicker">
            Agricultural risk intelligence platform
        </div>
        <div class="hero-title">AgriRisk AI</div>
        <div class="hero-copy">
            Understand agricultural risk patterns, explore dataset insights,
            and retrieve supporting advisory information to inform smarter decisions.
        </div>
        <div class="hero-pill">
            🌱 Data-driven insights &nbsp; • &nbsp;
            🌾 Smarter farming decisions
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    f"Current selection · Country: **{selected_country}** · "
    f"Crop: **{selected_crop}** · Year: **{selected_year}**"
)


# --------------------------------------------------
# DASHBOARD TABS
# --------------------------------------------------
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
    st.markdown(
        '<div class="section-heading">📊 Agricultural Risk Overview</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-copy">'
        'Explore key indicators and patterns in the filtered agricultural dataset.'
        '</div>',
        unsafe_allow_html=True,
    )

    # Identify numeric columns for metrics and charts
    numeric_columns = filtered_df.select_dtypes(
        include="number"
    ).columns.tolist()

    # Summary metrics
    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:
        st.metric(
            "Filtered Records",
            f"{len(filtered_df):,}",
        )

    with metric2:
        if "country" in filtered_df.columns:
            country_count = filtered_df["country"].nunique()
        else:
            country_count = 0

        st.metric(
            "Countries",
            f"{country_count:,}",
        )

    with metric3:
        if "crop" in filtered_df.columns:
            crop_count = filtered_df["crop"].nunique()
        else:
            crop_count = 0

        st.metric(
            "Crop Types",
            f"{crop_count:,}",
        )

    with metric4:
        st.metric(
            "Numeric Indicators",
            f"{len(numeric_columns):,}",
        )

    st.divider()

    # Country distribution
    left_chart, right_chart = st.columns(2)

    with left_chart:
        st.markdown("#### 🌍 Records by Country")

        if "country" in filtered_df.columns:
            country_data = (
                filtered_df["country"]
                .fillna("Unknown")
                .astype(str)
                .value_counts()
                .head(12)
                .reset_index()
            )
            country_data.columns = ["Country", "Records"]

            fig_country = px.bar(
                country_data,
                x="Country",
                y="Records",
                color="Records",
                color_continuous_scale="Greens",
                title="Top Countries in Selected Data",
            )

            fig_country.update_layout(
                template="plotly_white",
                showlegend=False,
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=55, b=10),
                xaxis_title="Country",
                yaxis_title="Number of Records",
            )

            st.plotly_chart(
                fig_country,
                use_container_width=True,
            )
        else:
            st.info(
                "A country column is not available in this dataset."
            )

    # Crop distribution
    with right_chart:
        st.markdown("#### 🌾 Records by Crop")

        if "crop" in filtered_df.columns:
            crop_data = (
                filtered_df["crop"]
                .fillna("Unknown")
                .astype(str)
                .value_counts()
                .head(12)
                .reset_index()
            )
            crop_data.columns = ["Crop", "Records"]

            fig_crop = px.bar(
                crop_data,
                x="Crop",
                y="Records",
                color="Records",
                color_continuous_scale="Teal",
                title="Top Crops in Selected Data",
            )

            fig_crop.update_layout(
                template="plotly_white",
                showlegend=False,
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=55, b=10),
                xaxis_title="Crop",
                yaxis_title="Number of Records",
            )

            st.plotly_chart(
                fig_crop,
                use_container_width=True,
            )
        else:
            st.info(
                "A crop column is not available in this dataset."
            )

    st.divider()

    # Numeric indicator distribution
    st.markdown("#### 📈 Numeric Indicator Analysis")

    if numeric_columns:
        selected_indicator = st.selectbox(
            "Choose a numeric indicator",
            options=numeric_columns,
            key="overview_numeric_indicator",
        )

        indicator_data = pd.to_numeric(
            filtered_df[selected_indicator],
            errors="coerce",
        ).dropna()

        if not indicator_data.empty:
            chart_left, chart_right = st.columns(2)

            with chart_left:
                fig_hist = px.histogram(
                    x=indicator_data,
                    nbins=25,
                    title=f"Distribution of {selected_indicator}",
                    labels={"x": selected_indicator, "count": "Records"},
                    color_discrete_sequence=["#15803d"],
                )

                fig_hist.update_layout(
                    template="plotly_white",
                    margin=dict(l=10, r=10, t=55, b=10),
                )

                st.plotly_chart(
                    fig_hist,
                    use_container_width=True,
                )

            with chart_right:
                summary_stats = indicator_data.describe()

                stats_df = pd.DataFrame(
                    {
                        "Statistic": [
                            "Count",
                            "Mean",
                            "Standard Deviation",
                            "Minimum",
                            "25th Percentile",
                            "Median",
                            "75th Percentile",
                            "Maximum",
                        ],
                        "Value": [
                            summary_stats.get("count", 0),
                            summary_stats.get("mean", 0),
                            summary_stats.get("std", 0),
                            summary_stats.get("min", 0),
                            summary_stats.get("25%", 0),
                            summary_stats.get("50%", 0),
                            summary_stats.get("75%", 0),
                            summary_stats.get("max", 0),
                        ],
                    }
                )

                stats_df["Value"] = stats_df["Value"].round(3)

                st.markdown("##### Descriptive Statistics")
                st.dataframe(
                    stats_df,
                    hide_index=True,
                    use_container_width=True,
                )
        else:
            st.info(
                "No valid numeric values are available for this indicator."
            )
    else:
        st.info(
            "No numeric columns are available for charting."
        )

    st.markdown(
        """
        <div class="insight-box">
            <div class="insight-title">💡 How to interpret this page</div>
            <span class="small-note">
                These charts describe the records in the selected dataset.
                They show distributions and descriptive statistics, not
                independently validated agricultural risk predictions.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # --------------------------------------------------
# TAB 2: RISK SCORECARD
# --------------------------------------------------
with tab2:
    st.markdown(
        '<div class="section-heading">🎯 Agricultural Risk Scorecard</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-copy">'
        'Review the available indicators and their distributions '
        'for your selected dataset.'
        '</div>',
        unsafe_allow_html=True,
    )

    # Identify potential risk-related columns
    risk_keywords = [
        "risk",
        "score",
        "severity",
        "vulnerability",
        "impact",
        "probability",
        "likelihood",
        "loss",
        "damage",
        "yield",
        "drought",
        "flood",
        "temperature",
        "rainfall",
        "precipitation",
    ]

    risk_columns = [
        column
        for column in filtered_df.columns
        if any(
            keyword in str(column).lower()
            for keyword in risk_keywords
        )
    ]

    numeric_risk_columns = [
        column
        for column in risk_columns
        if pd.api.types.is_numeric_dtype(filtered_df[column])
    ]

    # Scorecard summary
    score_col1, score_col2, score_col3, score_col4 = st.columns(4)

    with score_col1:
        st.metric(
            "Filtered Records",
            f"{len(filtered_df):,}",
        )

    with score_col2:
        st.metric(
            "Risk-Related Fields",
            f"{len(risk_columns):,}",
        )

    with score_col3:
        st.metric(
            "Numeric Risk Indicators",
            f"{len(numeric_risk_columns):,}",
        )

    with score_col4:
        completeness = (
            filtered_df.notna().sum().sum()
            / max(filtered_df.size, 1)
        ) * 100

        st.metric(
            "Data Completeness",
            f"{completeness:.1f}%",
        )

    st.divider()

    if numeric_risk_columns:
        st.markdown("#### 📋 Indicator Scorecard")

        scorecard_rows = []

        for column in numeric_risk_columns:
            values = pd.to_numeric(
                filtered_df[column],
                errors="coerce",
            ).dropna()

            if values.empty:
                continue

            scorecard_rows.append(
                {
                    "Indicator": str(column),
                    "Mean": round(values.mean(), 3),
                    "Median": round(values.median(), 3),
                    "Minimum": round(values.min(), 3),
                    "Maximum": round(values.max(), 3),
                    "Std. Deviation": round(values.std(), 3),
                    "Valid Records": int(values.count()),
                }
            )

        if scorecard_rows:
            scorecard_df = pd.DataFrame(scorecard_rows)

            st.dataframe(
                scorecard_df,
                hide_index=True,
                use_container_width=True,
            )

            st.markdown("#### 📊 Compare Indicators")

            selected_score_columns = st.multiselect(
                "Choose indicators to compare",
                options=numeric_risk_columns,
                default=numeric_risk_columns[:min(3, len(numeric_risk_columns))],
                key="scorecard_compare_columns",
            )

            if selected_score_columns:
                comparison_rows = []

                for column in selected_score_columns:
                    values = pd.to_numeric(
                        filtered_df[column],
                        errors="coerce",
                    ).dropna()

                    if not values.empty:
                        comparison_rows.append(
                            {
                                "Indicator": str(column),
                                "Mean": values.mean(),
                            }
                        )

                if comparison_rows:
                    comparison_df = pd.DataFrame(comparison_rows)

                    fig_scorecard = px.bar(
                        comparison_df,
                        x="Indicator",
                        y="Mean",
                        color="Mean",
                        color_continuous_scale="Greens",
                        title="Mean Values of Selected Indicators",
                    )

                    fig_scorecard.update_layout(
                        template="plotly_white",
                        showlegend=False,
                        coloraxis_showscale=False,
                        margin=dict(l=10, r=10, t=55, b=10),
                        xaxis_title="Indicator",
                        yaxis_title="Mean Value",
                    )

                    st.plotly_chart(
                        fig_scorecard,
                        use_container_width=True,
                    )
        else:
            st.info(
                "No valid numeric values were found in the "
                "identified risk-related fields."
            )

    else:
        st.info(
            "No numeric risk-related fields were detected. "
            "The scorecard below shows the available dataset fields "
            "so you can inspect the data."
        )

        st.write("**Available columns**")

        st.dataframe(
            pd.DataFrame(
                {
                    "Column": [str(column) for column in filtered_df.columns],
                    "Data Type": [
                        str(filtered_df[column].dtype)
                        for column in filtered_df.columns
                    ],
                    "Non-null Values": [
                        int(filtered_df[column].notna().sum())
                        for column in filtered_df.columns
                    ],
                }
            ),
            hide_index=True,
            use_container_width=True,
        )

    st.markdown(
        """
        <div class="insight-box">
            <div class="insight-title">⚠️ Interpretation note</div>
            <span class="small-note">
                The statistics above summarize observed dataset values.
                A high or low value is not automatically a risk level.
                Validated risk thresholds and a documented scoring method
                are required before indicators can be interpreted as
                actual agricultural risk scores.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # --------------------------------------------------
# TAB 3: AI ADVISORY
# --------------------------------------------------
with tab3:
    st.markdown(
        '<div class="section-heading">🤖 AI Agricultural Advisory</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-copy">'
        'Ask questions about agricultural risks and explore '
        'insights relevant to your selected dataset.'
        '</div>',
        unsafe_allow_html=True,
    )

    # Current dataset context
    st.markdown(
        f"""
        <div class="insight-box">
            <div class="insight-title">🌱 Current Analysis Context</div>
            <span class="small-note">
                Country: {selected_country} &nbsp; | &nbsp;
                Crop: {selected_crop} &nbsp; | &nbsp;
                Year: {selected_year} &nbsp; | &nbsp;
                Records: {len(filtered_df):,}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### 💬 Ask an Agricultural Question")

    # Suggested questions
    suggested_questions = [
        "What agricultural risks should farmers monitor?",
        "How can farmers reduce the impact of drought?",
        "What measures can help protect crops from heavy rainfall?",
        "How can data analysis support agricultural risk management?",
    ]

    selected_question = st.selectbox(
        "Choose a suggested question or type your own below",
        options=["Choose a question..."] + suggested_questions,
        key="advisory_suggested_question",
    )

    with st.form("agri_advisory_form"):
        user_question = st.text_area(
            "Your question",
            value=(
                selected_question
                if selected_question != "Choose a question..."
                else ""
            ),
            placeholder=(
                "Example: What steps can farmers take to reduce "
                "crop losses during drought?"
            ),
            height=120,
        )

        submit_question = st.form_submit_button(
            "✨ Generate Advisory",
            type="primary",
            use_container_width=True,
        )

    if submit_question:
        if not user_question.strip():
            st.warning("Please enter a question first.")
        else:
            # Build context for the advisory backend
            advisory_context = (
                f"Selected country: {selected_country}\n"
                f"Selected crop: {selected_crop}\n"
                f"Selected year: {selected_year}\n"
                f"Number of filtered records: {len(filtered_df)}\n"
                f"Available dataset columns: "
                f"{', '.join(map(str, filtered_df.columns))}\n"
            )

            try:
                with st.spinner("Generating agricultural advisory..."):
                    # The existing backend may accept different arguments.
                    # This call assumes generate_answer accepts a question.
                    answer = generate_answer(user_question.strip())

                st.markdown("#### 📝 Advisory Response")

                st.markdown(
                    """
                    <div class="insight-box">
                        <div class="insight-title">AI-Generated Insight</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if answer is None:
                    st.warning(
                        "The advisory backend returned no response."
                    )
                else:
                    st.markdown(str(answer))

                st.caption(
                    "Advisory responses are informational. Verify "
                    "recommendations against local agricultural guidance "
                    "and current conditions before acting on them."
                )

            except Exception as exc:
                st.error(
                    "The advisory could not be generated. "
                    "Check the generate_answer function in "
                    "src/generator.py and review the error below."
                )
                st.exception(exc)

    st.divider()

    st.markdown("#### 📌 Advisory Guidelines")

    guideline1, guideline2 = st.columns(2)

    with guideline1:
        st.markdown(
            """
            <div class="insight-box">
                <div class="insight-title">🌦️ Weather and Crop Risks</div>
                <span class="small-note">
                    Consider rainfall, temperature, water availability,
                    crop sensitivity, and local forecasts when evaluating
                    agricultural risks.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with guideline2:
        st.markdown(
            """
            <div class="insight-box">
                <div class="insight-title">📊 Data-Driven Decisions</div>
                <span class="small-note">
                    Use reliable observations and local expertise to
                    interpret agricultural data. Historical records alone
                    may not represent current field conditions.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # --------------------------------------------------
# TAB 4: EXPLORE DATASET
# --------------------------------------------------
with tab4:
    st.markdown(
        '<div class="section-heading">🔎 Explore Agricultural Dataset</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-copy">'
        'Inspect records, explore data quality, and export the data '
        'selected using the sidebar filters.'
        '</div>',
        unsafe_allow_html=True,
    )

    # Dataset overview
    data_col1, data_col2, data_col3, data_col4 = st.columns(4)

    with data_col1:
        st.metric("Records", f"{len(filtered_df):,}")

    with data_col2:
        st.metric("Columns", f"{len(filtered_df.columns):,}")

    with data_col3:
        missing_count = int(filtered_df.isna().sum().sum())
        st.metric("Missing Values", f"{missing_count:,}")

    with data_col4:
        duplicate_count = int(filtered_df.duplicated().sum())
        st.metric("Duplicate Rows", f"{duplicate_count:,}")

    st.divider()

    # Select columns to display
    st.markdown("#### 🗂️ Select Columns")

    all_columns = filtered_df.columns.tolist()

    selected_columns = st.multiselect(
        "Choose the columns to display",
        options=all_columns,
        default=all_columns[:min(8, len(all_columns))],
        key="explore_selected_columns",
    )

    if selected_columns:
        display_df = filtered_df[selected_columns].copy()

        # Optional text search
        search_text = st.text_input(
            "🔍 Search displayed records",
            placeholder="Enter a word, country, crop, or value...",
            key="explore_search_text",
        )

        if search_text.strip():
            search_mask = display_df.astype(str).apply(
                lambda column: column.str.contains(
                    search_text.strip(),
                    case=False,
                    na=False,
                    regex=False,
                )
            ).any(axis=1)

            display_df = display_df.loc[search_mask]

        st.caption(
            f"Showing {len(display_df):,} matching records."
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=420,
        )

        # Download the currently selected columns and matching records
        csv_data = display_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download Displayed Data (CSV)",
            data=csv_data,
            file_name="agririsk_filtered_dataset.csv",
            mime="text/csv",
            use_container_width=True,
        )

    else:
        st.info(
            "Select at least one column to preview and download data."
        )

    st.divider()

    # Data quality report
    st.markdown("#### 🧹 Data Quality Report")

    quality_df = pd.DataFrame(
        {
            "Column": [str(column) for column in filtered_df.columns],
            "Data Type": [
                str(filtered_df[column].dtype)
                for column in filtered_df.columns
            ],
            "Non-null Values": [
                int(filtered_df[column].notna().sum())
                for column in filtered_df.columns
            ],
            "Missing Values": [
                int(filtered_df[column].isna().sum())
                for column in filtered_df.columns
            ],
            "Missing (%)": [
                round(
                    filtered_df[column].isna().mean() * 100,
                    2,
                )
                for column in filtered_df.columns
            ],
            "Unique Values": [
                int(filtered_df[column].nunique(dropna=True))
                for column in filtered_df.columns
            ],
        }
    )

    st.dataframe(
        quality_df,
        use_container_width=True,
        hide_index=True,
    )

    # Missing-value visualization
    missing_df = quality_df[
        quality_df["Missing Values"] > 0
    ].sort_values(
        "Missing (%)",
        ascending=False,
    )

    if not missing_df.empty:
        st.markdown("#### 📉 Missing Values by Column")

        fig_missing = px.bar(
            missing_df,
            x="Column",
            y="Missing (%)",
            color="Missing (%)",
            color_continuous_scale="Greens",
            title="Percentage of Missing Values",
        )

        fig_missing.update_layout(
            template="plotly_white",
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=55, b=10),
            xaxis_title="Column",
            yaxis_title="Missing Values (%)",
        )

        st.plotly_chart(
            fig_missing,
            use_container_width=True,
        )
    else:
        st.success(
            "No missing values were found in the filtered dataset."
        )

    st.markdown(
        """
        <div class="insight-box">
            <div class="insight-title">📌 Dataset transparency</div>
            <span class="small-note">
                The explorer displays the records supplied by the dataset
                and applies the selected filters. Downloading the data
                does not add predictions or modify the original source.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()

st.markdown(
    """
    <div style="text-align:center; padding: 0.8rem 0 1.2rem 0;">
        <div style="font-weight:800; color:#14532d;">
            🌱 AgriRisk AI
        </div>
        <div style="font-size:0.78rem; color:#718278; margin-top:0.3rem;">
            Agricultural Risk Intelligence Dashboard
        </div>
        <div style="font-size:0.72rem; color:#718278; margin-top:0.25rem;">
            Data-driven insights for agricultural risk exploration
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
