"""Streamlit dashboard for Liverpool City Region housing pipeline."""

from __future__ import annotations

import io

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from utils.analytics import BASELINE_BUILT, TARGET_UNITS, categorical_breakdown, completion_breakdown, summarize_kpis
from utils.data_loader import clean_data, load_raw_data

load_dotenv()

st.set_page_config(
    page_title="LCR Housing Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏡 Liverpool City Region Housing Delivery Dashboard")
st.caption(
    "Data-rich, presentation-ready overview for the Mayor and stakeholders. "
    "Explore pipeline progress, investment, and AI-powered data entry concepts."
)


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    raw = load_raw_data()
    return clean_data(raw)


def kpi_card(label: str, value: float, delta: str | None = None, help_text: str | None = None):
    st.metric(label, f"{value:,.0f}" if isinstance(value, (int, float)) else value, delta=delta, help=help_text)


def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()

    st.sidebar.header("Interactive Filters")
    areas = st.sidebar.multiselect("Area", sorted(working["Area"].dropna().unique())) if "Area" in working else []
    developers = (
        st.sidebar.multiselect("Developer", sorted(working["Developer"].dropna().unique()))
        if "Developer" in working
        else []
    )
    timelines = (
        st.sidebar.multiselect("Timeline", sorted(working["Timeline"].dropna().unique())) if "Timeline" in working else []
    )
    statuses = (
        st.sidebar.multiselect("Planning Status", sorted(working["Planning Status"].dropna().unique()))
        if "Planning Status" in working
        else []
    )
    land_types = (
        st.sidebar.multiselect("Land Type", sorted(working["Land Type"].dropna().unique())) if "Land Type" in working else []
    )

    search_term = st.sidebar.text_input("Search project name, postcode, or keywords")

    # Numeric filters
    if "Units" in working:
        min_units, max_units = int(working["Units"].min()), int(working["Units"].max())
        unit_range = st.sidebar.slider("Units", min_units, max_units, (min_units, max_units))
    else:
        unit_range = None

    if "Cost (£)" in working and working["Cost (£)"].notna().any():
        min_cost, max_cost = int(working["Cost (£)"].min(skipna=True)), int(working["Cost (£)"].max(skipna=True))
        cost_range = st.sidebar.slider("Cost (£)", min_cost, max_cost, (min_cost, max_cost))
    else:
        cost_range = None

    # Apply filters
    if areas:
        working = working[working["Area"].isin(areas)]
    if developers:
        working = working[working["Developer"].isin(developers)]
    if timelines:
        working = working[working["Timeline"].isin(timelines)]
    if statuses:
        working = working[working["Planning Status"].isin(statuses)]
    if land_types:
        working = working[working["Land Type"].isin(land_types)]
    if unit_range:
        working = working[(working["Units"] >= unit_range[0]) & (working["Units"] <= unit_range[1])]
    if cost_range and "Cost (£)" in working:
        working = working[(working["Cost (£)"].fillna(0) >= cost_range[0]) & (working["Cost (£)"].fillna(0) <= cost_range[1])]

    if search_term:
        search_lower = search_term.lower()
        mask = pd.Series([False] * len(working))
        for col in ["Project Name", "Postcode", "Sponsor", "Developer", "Mix", "Timeline", "Planning Status"]:
            if col in working:
                mask = mask | working[col].astype(str).str.lower().str.contains(search_lower)
        working = working[mask]

    return working


def render_kpis(filtered: pd.DataFrame):
    kpis = summarize_kpis(filtered)
    progress = (kpis["units_built"] / kpis["target_units"]) * 100 if kpis["target_units"] else 0
    delta = f"{progress:.1f}% of {kpis['target_units']:,} target"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("Total Homes Planned", kpis["units_total"], help_text="Sum of Units across filtered projects")
    with col2:
        kpi_card("Homes Built", kpis["units_built"], delta=delta, help_text="Completed units or baseline estimate")
    with col3:
        kpi_card("Total Investment (£)", kpis["cost_total"], help_text="Aggregated development ask")
    with col4:
        kpi_card("Capacity (people)", kpis["capacity"], help_text="Units × 1.8 occupancy assumption")



def render_visuals(filtered: pd.DataFrame):
    st.subheader("Visual Analytics")

    # Built vs target
    kpis = summarize_kpis(filtered)
    progress_df = pd.DataFrame(
        {
            "Category": ["Built", "Remaining to Target"],
            "Units": [kpis["units_built"], max(kpis["target_units"] - kpis["units_built"], 0)],
        }
    )
    fig_progress = px.bar(
        progress_df,
        x="Category",
        y="Units",
        color="Category",
        color_discrete_sequence=["#4CAF50", "#FFC107"],
        title="Homes built vs 6,600 target",
        text="Units",
    )
    fig_progress.update_traces(texttemplate="%{y:,.0f}", textposition="outside")

    # Area distribution
    area_df = categorical_breakdown(filtered, "Area")
    fig_area = px.bar(
        area_df.head(15),
        x="Area",
        y="Units",
        color="Units",
        title="Units by Area",
        color_continuous_scale="Blues",
    )

    # Developer breakdown
    dev_df = categorical_breakdown(filtered, "Developer")
    fig_dev = px.pie(dev_df.head(12), names="Developer", values="Units", title="Share of Units by Developer")

    # Completion timelines
    completion_df = completion_breakdown(filtered)
    fig_completion = px.line(
        completion_df,
        x="Year",
        y="Units",
        markers=True,
        title="Expected Completions by Year",
    )

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_progress, use_container_width=True)
    with col2:
        st.plotly_chart(fig_dev, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(fig_area, use_container_width=True)
    with col4:
        st.plotly_chart(fig_completion, use_container_width=True)

    # Distribution of site sizes if available
    if "Site Size (hectares)" in filtered:
        fig_site = px.histogram(
            filtered,
            x="Site Size (hectares)",
            nbins=20,
            title="Distribution of Site Size (hectares)",
            color_discrete_sequence=["#9C27B0"],
        )
        st.plotly_chart(fig_site, use_container_width=True)



def render_data_explorer(filtered: pd.DataFrame):
    st.subheader("Raw Data Explorer")
    st.write("Sort columns, page through the dataset, and export the current view.")

    # Pagination helpers
    page_size = st.selectbox("Rows per page", [10, 25, 50, 100], index=1)
    total_rows = len(filtered)
    total_pages = max((total_rows - 1) // page_size + 1, 1)

    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
    start = (page - 1) * page_size
    end = start + page_size

    st.dataframe(filtered.iloc[int(start): int(end)], use_container_width=True, height=420)

    # Export filtered results
    csv_buffer = io.StringIO()
    filtered.to_csv(csv_buffer, index=False)
    st.download_button(
        label="⬇️ Export filtered CSV",
        data=csv_buffer.getvalue(),
        file_name="filtered_housing_pipeline.csv",
        mime="text/csv",
    )



def render_ai_mock():
    st.subheader("AI-powered data entry (concept demo)")
    st.write(
        "Prototype of an intelligent data entry assistant that transforms raw text into structured metadata. "
        "In production, this would call an LLM for automated summarisation and entity extraction."
    )

    with st.form("ai_form"):
        raw_text = st.text_area(
            "Paste project details",
            placeholder="e.g. 55 affordable homes near L30 6UR led by Your Housing Group, early enabling works required...",
            height=140,
        )
        submitted = st.form_submit_button("Summarise with AI ✨")

    if submitted:
        st.success("AI-powered summarisation complete (mocked)")
        st.write(
            "The intelligent data entry assistant would auto-classify key fields for reviewer approval."
        )

        # Mock outputs
        st.info("Plot Description: Compact infill scheme delivering mixed affordable tenure across L30 corridor.")
        st.warning("Status: Pre-planning due diligence — procurement route still being defined.")
        st.success("Key Details: AI-powered summarisation, automated metadata extraction, readiness score 0.64.")
        st.map(
            pd.DataFrame(
                {"lat": [53.4486], "lon": [-2.9885]}, index=[0]
            ),
            zoom=10,
        )



def main():
    data = load_data()
    filtered = filter_data(data)

    st.markdown("---")
    render_kpis(filtered)
    st.markdown("---")
    render_visuals(filtered)
    st.markdown("---")
    render_data_explorer(filtered)
    st.markdown("---")
    render_ai_mock()


if __name__ == "__main__":
    main()
