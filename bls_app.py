import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

st.set_page_config(
    page_title="BLS Data Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Load and Prepare Data
# -------------------------------
@st.cache_data
def load_data(filename="bls_data.csv"):
    df = pd.read_csv(filename, parse_dates=["date"])
    return df

df = load_data()

# The given series_ids mapping (adjusted to reflect the final set provided by you):
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

# Pivot the data so that each series_name is a column
pivot_df = df.pivot(index="date", columns="series_name", values="value").sort_index()

#Create Sidebar
st.sidebar.title("BLS Dashboard Controls")

st.sidebar.write("Select the unemployment-related metrics you want to visualize:")
unemployment_metrics = [
    "National Unemployment Rate",
    "Men Unemployment Rate (20+)",
    "Women Unemployment Rate (20+)",
    "Black or African American Unemployment Rate",
    "Hispanic or Latino Unemployment Rate",
    "Long-Term Unemployment (27 weeks or more)",
    "Underemployment Rate (U-6)",
    "Youth Unemployment Rate (16-24)",
    "Labor Force Participation Rate",
    "Discouraged Workers"
]

selected_metrics = st.sidebar.multiselect(
    "Choose metrics:", unemployment_metrics,
    default=["National Unemployment Rate"]
)

st.sidebar.write("---")
st.sidebar.write("Select additional economic series to view:")
additional_metrics = [
    "Total Non-Farm Workers",
    "Average Hourly Earnings"
]

selected_additional = st.sidebar.multiselect(
    "Additional series:", additional_metrics, default=[]
)

st.sidebar.markdown(
    """
    **Instructions**:
    - Use the checkboxes/multiselects to add or remove series from the main chart.
    - All data is sourced from the BLS API.
    """
)

# -------------------------------
# Main Page Content
# -------------------------------
st.title("U.S. Labor Market Dashboard")

st.markdown(
    """
    This dashboard provides an interactive view of key U.S. labor market statistics 
    sourced from the Bureau of Labor Statistics (BLS). You can explore unemployment 
    rates by various demographic groups, long-term unemployment, underemployment (U-6), 
    labor force participation, and more. Additionally, you can view total non-farm 
    employment and average hourly earnings to get a broader view of economic health.
    """
)

#create time series

if selected_metrics or selected_additional:
    # Combine selected metrics
    all_selected = selected_metrics + selected_additional
    # Filter the pivot_df for the selected columns
    filtered_df = pivot_df[all_selected].copy()

    # Create a long form DataFrame suitable for Altair
    long_df = filtered_df.reset_index().melt("date", var_name="Metric", value_name="Value")

    base = alt.Chart(long_df).mark_line(point=True).encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("Value:Q", title="Value"),
        color="Metric:N",
        tooltip=["date:T", "Metric:N", "Value:Q"]
    ).properties(
        width=800,
        height=400
    ).interactive()

    st.altair_chart(base, use_container_width=True)

    st.markdown("**Note:** Hover over the chart to see exact values for each metric at a given time.")
else:
    st.warning("Please select at least one metric to view the time series visualization.")

st.write("---")
st.header("Additional Insights")

st.markdown(
    """
    **Potential Analyses:**
    - Compare unemployment rates between demographic groups over time.
    - Examine how changes in Total Non-Farm Workers correlate with unemployment rates.
    - Explore trends in Average Hourly Earnings alongside shifts in employment.
    """
)

# Show basic stats for selected series (if any chosen)
if all_selected:
    st.subheader("Summary Statistics of Selected Series")
    stats = filtered_df.describe()
    st.dataframe(stats)
else:
    st.write("No metrics selected, select series to populate summary statistics.")
