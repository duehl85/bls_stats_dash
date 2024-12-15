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

# The given series_ids mapping (adjusted to reflect the final selected series
series_ids = {
    "National Unemployment Rate": "LNS14000000",
    "Men Unemployment Rate (20+)": "LNS14000006",
    "Women Unemployment Rate (20+)": "LNS14000007",
    "Black or African American Unemployment Rate": "LNS14000003",
    "Hispanic or Latino Unemployment Rate": "LNS14000009",
    "Long-Term Unemployment (27 weeks or more)": "LNS13008756",
    "Underemployment Rate (U-6)": "LNS13327709",
    "Youth Unemployment Rate (16-24)": "LNU04000012",
    "Labor Force Participation Rate": "LNS11300000",
    "Discouraged Workers": "LNS15026645",
    "Total Non-Farm Workers": "CEU0000000001",
    "Average Hourly Earnings": "CES0500000003"
}

# Categorize % based statistics
percentage_metrics = [
    "National Unemployment Rate",
    "Men Unemployment Rate (20+)",
    "Women Unemployment Rate (20+)",
    "Black or African American Unemployment Rate",
    "Hispanic or Latino Unemployment Rate",
    "Underemployment Rate (U-6)",
    "Youth Unemployment Rate (16-24)",
    "Labor Force Participation Rate"
]

# Categorize count based statistics
count_metrics = ["Discouraged Workers", "Total Non-Farm Workers"]

# Categorize dollar based metrics
earnings_metric = "Average Hourly Earnings"

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

# Options to display non-percentage data
display_non_farm = st.sidebar.checkbox("Show Total Non-Farm Workers (Count)", value=True)
display_earnings = st.sidebar.checkbox("Show Average Hourly Earnings (Dollars)", value=True)

st.sidebar.markdown(
    """
    **Note:**  
    - The main chart displays percentage-based metrics only.
    - Total Non-Farm Workers and Average Hourly Earnings are displayed in separate charts below to avoid mixing scales.
    """
)

# Main Page

st.title("U.S. Labor Market Dashboard")

st.markdown(
    """
    This dashboard provides an interactive view of key U.S. labor market statistics from the BLS.

    **Charts:**
    - **Main Chart:** Display one or more percentage-based metrics (e.g. unemployment rates, participation rates).
    - **Additional Charts:** 
        - Total Non-Farm Workers (in thousands of persons)
        - Average Hourly Earnings (in dollars per hour)
    """
)


# Main Chart: Percentage Metrics
st.header("Percentage-Based Metrics")

if selected_percentages:
    # Filter data
    filtered_df = pivot_df[selected_percentages].dropna(how='all', axis=0)

    # Convert to long form for Altair
    long_df = filtered_df.reset_index().melt("date", var_name="Metric", value_name="Value")

    # Create Altair chart for percentages
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
    st.warning("Select at least one percentage-based metric to display.")

# Additional Charts

# Total Non-Farm Workers
if display_non_farm and "Total Non-Farm Workers" in pivot_df.columns:
    st.header("Total Non-Farm Workers")
    # Display line chart
    nonfarm_df = pivot_df[["Total Non-Farm Workers"]].dropna()
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

# Average Hourly Earnings
if display_earnings and earnings_metric in pivot_df.columns:
    st.header("Average Hourly Earnings")
    earnings_df = pivot_df[[earnings_metric]].dropna()
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

# Discouraged Workers 
if "Discouraged Workers" in pivot_df.columns:
    st.header("Discouraged Workers")
    dw_df = pivot_df[["Discouraged Workers"]].dropna()
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
    st.markdown(
        "Discouraged workers are those not currently seeking employment due to the belief no jobs are available.")
