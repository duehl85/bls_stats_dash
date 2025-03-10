import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

st.set_page_config(
    page_title="BLS Data Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Load and Prepare Data

@st.cache_data
def load_data(filename="bls_data.csv"):
    df = pd.read_csv(filename, parse_dates=["date"])
    return df

df = load_data()

# Series_ids mapping (adjusted to reflect the final selected series)
series_ids = {
    "Total Non-Farm Workers": "CEU0000000001",
    "Average Hourly Earnings": "CES0500000003",
    "National Unemployment Rate": "LNS14000000",
    "Men Unemployment Rate (20+)": "LNS14000006",
    "Women Unemployment Rate (20+)": "LNS14000007",
    "Black or African American Unemployment Rate": "LNS14000003",
    "Hispanic or Latino Unemployment Rate": "LNS14000009",
    "Long-Term Unemployment (27 weeks or more)": "LNS13008756",
    "Underemployment Rate (U-6)": "LNS13327709",
    "Youth Unemployment Rate (16-24)": "LNU04000012",
    "Labor Force Participation Rate": "LNS11300000",
    "Discouraged Workers": "LNS15026645"
}

# Categorize metrics:
percentage_metrics = [
    "National Unemployment Rate",
    "Men Unemployment Rate (20+)",
    "Women Unemployment Rate (20+)",
    "Black or African American Unemployment Rate",
    "Hispanic or Latino Unemployment Rate",
    "Long-Term Unemployment (27 weeks or more)",
    "Underemployment Rate (U-6)",
    "Youth Unemployment Rate (16-24)",
    "Labor Force Participation Rate"
]

# Count-based and earnings metrics
count_metrics = ["Total Non-Farm Workers"]
earnings_metric = "Average Hourly Earnings"
discouraged_metric = "Discouraged Workers"

# Pivot Data
pivot_df = df.pivot(index="date", columns="series_name", values="value").sort_index()


# Sidebar Controls

st.sidebar.title("BLS Dashboard Controls")

st.sidebar.markdown("**Percentage-based metrics (Rates, Participation)**")
selected_percentages = st.sidebar.multiselect(
    "Select metrics to display on the main chart:",
    percentage_metrics,
    default=["National Unemployment Rate"]
)

st.sidebar.write("---")

display_non_farm = st.sidebar.checkbox("Show Total Non-Farm Workers (Count)", value=True)
display_earnings = st.sidebar.checkbox("Show Average Hourly Earnings (Dollars)", value=True)
display_discouraged = st.sidebar.checkbox("Show Discouraged Workers (Count)", value=False)

st.sidebar.markdown(
    """
    **Note:**  
    - The main chart displays percentage-based metrics only.
    - Total Non-Farm Workers, Average Hourly Earnings, and Discouraged Workers are displayed separately.
    """
)


# Main Page Content

st.title("U.S. Labor Market Dashboard")

st.markdown(
    """
    This dashboard provides an interactive view of key U.S. labor market statistics from the BLS.
    
    **Features:**
    - **Main Chart:** Percentage-based metrics (unemployment rates, participation rates, etc.).
    - **Additional Charts:** Total Non-Farm Workers, Average Hourly Earnings, and Discouraged Workers displayed separately.
    - **Date Range Slider:** Filter all charts and summaries based on a selected date range.
    - **Statistical Summaries:** View average, maximum, minimum, and other statistics for selected metrics within the chosen date range.
    """
)


# Date Range Selection

min_date = pivot_df.index.min()
max_date = pivot_df.index.max()

st.subheader("Select Date Range")
date_range = st.slider(
    "Date range:",
    min_value=min_date.to_pydatetime(),
    max_value=max_date.to_pydatetime(),
    value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
    format="YYYY-MM"
)

start_date, end_date = date_range

# Filter pivot_df based on the selected date range
filtered_pivot_df = pivot_df.loc[(pivot_df.index >= start_date) & (pivot_df.index <= end_date)]


# Main Chart: Percentage Metrics

st.header("Percentage-Based Metrics")
if selected_percentages:
    # Check that these columns exist in filtered_pivot_df
    available_cols = set(filtered_pivot_df.columns)
    chosen_perc = [col for col in selected_percentages if col in available_cols]

    if chosen_perc:
        filtered_df = filtered_pivot_df[chosen_perc].dropna(how='all', axis=0)
        if not filtered_df.empty:
            long_df = filtered_df.reset_index().melt("date", var_name="Metric", value_name="Value")

            base = alt.Chart(long_df).mark_line(point=True).encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y("Value:Q", title="Percentage", scale=alt.Scale(zero=False)),
                color="Metric:N",
                tooltip=["date:T", "Metric:N", alt.Tooltip("Value:Q", format=".2f")]
            ).properties(
                width=800,
                height=400
            ).interactive()

            st.altair_chart(base, use_container_width=True)
            st.markdown("_Note: Hover over the chart for detailed values._")
        else:
            st.warning("No data available for the selected date range and metrics.")
    else:
        st.warning("None of the selected percentage metrics are available in the dataset.")
else:
    st.warning("Select at least one percentage-based metric to display.")


# Additional Charts
# Initialize a list to keep track of all selected metrics for statistical summaries
all_selected_metrics = selected_percentages.copy()

# Total Non-Farm Workers
if display_non_farm and "Total Non-Farm Workers" in filtered_pivot_df.columns:
    st.header("Total Non-Farm Workers")
    nonfarm_df = filtered_pivot_df[["Total Non-Farm Workers"]].dropna()
    if not nonfarm_df.empty:
        nf_long = nonfarm_df.reset_index().melt("date", var_name="Metric", value_name="Workers (in thousands)")
        nonfarm_chart = alt.Chart(nf_long).mark_line(point=True).encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("Workers (in thousands):Q", title="Workers (in thousands)"),
            tooltip=["date:T", alt.Tooltip("Workers (in thousands):Q", format=",.0f")]
        ).properties(
            width=800,
            height=300,
            title="Total Non-Farm Workers Over Time"
        ).interactive()

        st.altair_chart(nonfarm_chart, use_container_width=True)
        st.markdown("This metric represents the total number of non-farm payroll jobs (in thousands).")
        all_selected_metrics.append("Total Non-Farm Workers")
    else:
        st.info("No data available for Total Non-Farm Workers in the selected date range.")

# Average Hourly Earnings
if display_earnings and earnings_metric in filtered_pivot_df.columns:
    st.header("Average Hourly Earnings")
    earnings_df = filtered_pivot_df[[earnings_metric]].dropna()
    if not earnings_df.empty:
        earnings_long = earnings_df.reset_index().melt("date", var_name="Metric", value_name="Dollars per Hour")
        earnings_chart = alt.Chart(earnings_long).mark_line(point=True).encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("Dollars per Hour:Q", title="Dollars per Hour", scale=alt.Scale(zero=False)),
            tooltip=["date:T", alt.Tooltip("Dollars per Hour:Q", format=".2f")]
        ).properties(
            width=800,
            height=300,
            title="Average Hourly Earnings Over Time"
        ).interactive()

        st.altair_chart(earnings_chart, use_container_width=True)
        st.markdown("Average hourly earnings provides insight into wage trends over time.")
        all_selected_metrics.append(earnings_metric)
    else:
        st.info("No data available for Average Hourly Earnings in the selected date range.")

# Discouraged Workers
if display_discouraged and discouraged_metric in filtered_pivot_df.columns:
    st.header("Discouraged Workers")
    dw_df = filtered_pivot_df[[discouraged_metric]].dropna()
    if not dw_df.empty:
        dw_long = dw_df.reset_index().melt("date", var_name="Metric", value_name="Persons (in thousands)")
        dw_chart = alt.Chart(dw_long).mark_line(point=True).encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("Persons (in thousands):Q", title="Persons (in thousands)"),
            tooltip=["date:T", alt.Tooltip("Persons (in thousands):Q", format=",.0f")]
        ).properties(
            width=800,
            height=300,
            title="Discouraged Workers Over Time"
        ).interactive()

        st.altair_chart(dw_chart, use_container_width=True)
        st.markdown("Discouraged workers are those not currently seeking employment due to the belief no jobs are available.")
        all_selected_metrics.append(discouraged_metric)
    else:
        st.info("No data available for Discouraged Workers in the selected date range.")


# Statistical Summaries

if all_selected_metrics:
    st.write("---")
    st.header("Statistical Summaries of Selected Metrics")

    selected_data = filtered_pivot_df[all_selected_metrics].dropna(how='all', axis=0)

    if not selected_data.empty:
        stats = selected_data.describe().T
        st.dataframe(stats, use_container_width=True)
    else:
        st.info("No data available for statistical summaries in the selected date range.")
else:
    st.write("---")
    st.info("No metrics selected. Please select metrics to view statistical summaries.")
