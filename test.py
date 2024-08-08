import streamlit as st
import pandas as pd
import os
import glob
from graphs import generate_graph, generate_source_graph, generate_pie_chart, generate_severity_bar_chart
from metrics import assess_risk, get_total_incidents, get_severity_incidents, calculate_average_downtime
from sideBarMetrics import get_severity_incidents_sidebar, get_total_incidents_sidebar, calculate_average_downtime_sidebar

# Load JSON data into a DataFrame
df = pd.concat(map(pd.read_json, glob.glob(os.path.join('', "*.json"))))

# Convert the date column to datetime
df['date'] = pd.to_datetime(df['date'])

# Combine appId and appName for display in the dropdown
df['app_display'] = df['appId'].str.strip() + ' (' + df['appName'].str.strip() + ')'

# Verify content of app_displays
app_displays = df['app_display'].unique()

# Find the default display value for "B6OV"
default_app_display = "B6OV (My Business Portal)"

# Calculate the baseline average number of incidents using the entire DataFrame
baseline_avg_incidents = df.groupby('appId').size().mean()

# Streamlit app
st.set_page_config(page_title="SRE Incident Trends Dashboard", layout="wide")

# Custom CSS to hide Streamlit's default navbar and footer
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .css-1d391kg {  /* Adjust the top padding of the main container */
        padding-top: 0px;
    }
    .css-12oz5g7 {  /* Adjust the top margin of the main container */
        margin-top: -50px;
    }
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Custom header
st.markdown('<div class="header" style="padding: 10px; text-align: center; background-color: #f1f1f1; font-size: 24px; font-weight: bold;">SRE Incident Trends Dashboard</div>', unsafe_allow_html=True)

# Create container for dropdowns
with st.container():
    col1, col2, col3 = st.columns([1, 1, 2])

    # Dropdown menus in the first row
    with col1:
        # Set default appId to "B6OV"
        selected_app_display = st.selectbox("Select App ID", app_displays, index=list(app_displays).index(default_app_display), key="app_id")
        selected_app_id = selected_app_display.split(' ')[0]
        print("selected_app_display:", selected_app_display)  # This will print in the terminal
        print("selected_app_id:", selected_app_id)  # This will print in the terminal

    with col2:
        # Set default time range to '3 Months'
        selected_time_range = st.selectbox("Select Time Range", ['3 Months', '6 Months', '1 Year'], index=0, key="time_range")

    with col3:
        # Date range selection
        date_range = st.date_input("Select Date Range", [])
        if date_range:
            if len(date_range) == 2:
                start_date, end_date = date_range
            else:
                start_date = end_date = None
        else:
            start_date = end_date = None

# Display metrics with st.metric
with st.container():
    columns = st.columns([1, 1, 1, 1, 1, 1, 1])

    # Total Incidents
    current_incidents, previous_incidents, percentage_change = get_total_incidents(selected_app_id, selected_time_range, df)
    delta_incidents = current_incidents - previous_incidents
    columns[0].metric("Total Incidents", current_incidents, delta=f"{delta_incidents:+.0f} ({abs(percentage_change):.2f}%)")

    # Risk
    risk_info = assess_risk(df, selected_app_id, baseline_avg_incidents)
    columns[1].metric("Risk", risk_info['level'], delta=risk_info.get('delta', ''))

    # Average Downtime
    average_downtime = calculate_average_downtime(df, selected_app_id, selected_time_range, start_date, end_date)
    columns[2].metric("Average Downtime (minutes)", f"{average_downtime:.2f}")

    # Severity Metrics
    severity_counts, severity_deltas, severity_percentage_changes = get_severity_incidents(selected_app_id, selected_time_range, df)
    for i, (severity, count) in enumerate(severity_counts.items(), start=3):
        columns[i].metric(
            f"{severity} Incidents",
            count,
            delta=f"{severity_deltas[severity]:+.0f} ({abs(severity_percentage_changes[severity]):.2f}%)"
        )

# Metrics selection in the sidebar
with st.sidebar:
    st.header("Metrics")
    metric_options = ['1 Day', '1 Week', '1 Month']
    selected_metric = st.selectbox("Select Metrics Range", metric_options, index=0, key="metric_sidebar")

    # Total Incidents
    st.header("Total Incidents")
    current_incidents, previous_incidents, percentage_change = get_total_incidents_sidebar(selected_app_id, df,
                                                                                           selected_metric)
    delta_incidents = current_incidents - previous_incidents
    st.metric("Total Incidents", current_incidents, delta=f"{delta_incidents:+.0f} ({abs(percentage_change):.2f}%)")

    # Average Downtime
    average_downtime = calculate_average_downtime_sidebar(df, selected_app_id, selected_metric)
    st.metric("Average Downtime (minutes)", f"{average_downtime:.2f}")

    # Severity metrics in the sidebar
    st.header("Severity Metrics")

    # Fetch severity metrics
    severity_counts, severity_deltas, severity_percentage_changes = get_severity_incidents_sidebar(selected_app_id, df,
                                                                                                   selected_metric)

    # Define the order of severity
    severity_order = ['P1', 'P2', 'P3', 'P4']

    # Collect metrics that have non-zero values
    valid_metrics = [
        (severity, severity_counts[severity], severity_deltas[severity], severity_percentage_changes[severity])
        for severity in severity_order if severity in severity_counts and severity_counts[severity] > 0
    ]

    # If there are valid metrics, display them in pairs
    if valid_metrics:
        for i in range(0, len(valid_metrics), 2):
            col1, col2 = st.columns(2)
            with col1:
                severity, count, delta, percentage_change = valid_metrics[i]
                st.metric(
                    f"{severity} Incidents",
                    count,
                    delta=f"{delta:+.0f} ({abs(percentage_change):.2f}%)"
                )
            if i + 1 < len(valid_metrics):
                with col2:
                    severity, count, delta, percentage_change = valid_metrics[i + 1]
                    st.metric(
                        f"{severity} Incidents",
                        count,
                        delta=f"{delta:+.0f} ({abs(percentage_change):.2f}%)"
                    )
    else:
        st.write("No severity metrics available.")
# Create container for graphs
with st.container():
    col1, col2 = st.columns([1, 1])

    with col1:
        fig = generate_graph(selected_app_id, selected_time_range, df, start_date, end_date)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig_source = generate_source_graph(selected_app_id, selected_time_range, df, start_date, end_date)
        st.plotly_chart(fig_source, use_container_width=True)

# Create container for the pie chart
with st.container():
    col1, col2 = st.columns([1, 1])

    with col1:
        fig_pie = generate_pie_chart(selected_app_id, selected_time_range, df, start_date, end_date)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        fig_severity_bar = generate_severity_bar_chart(selected_app_id, selected_time_range, df, start_date, end_date)
        st.plotly_chart(fig_severity_bar, use_container_width=True)
