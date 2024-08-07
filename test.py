import streamlit as st
import pandas as pd
import os
import glob
from graphs import generate_graph, generate_source_graph, generate_pie_chart, generate_severity_bar_chart
from metrics import  assess_risk, get_total_incidents, get_severity_incidents, calculate_average_downtime

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

# Custom CSS for sidebar width
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        width: 200px;
    }
    </style>
    """, unsafe_allow_html=True)

# Header with title
st.markdown("""
    <style>
    .header {
        padding: 10px;
        text-align: center;
        background-color: #f1f1f1;
        font-size: 24px;
        font-weight: bold;
    }
    </style>
    <div class="header">SRE Incident Trends Dashboard</div>
    """, unsafe_allow_html=True)

# Create container for dropdowns
with st.container():
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])

    # Dropdown menus in the first row
    with col1:
        # Set default appId to "B6OV"
        selected_app_display = st.selectbox("Select App ID", app_displays, index=list(app_displays).index(default_app_display), key="app_id")
        selected_app_id = selected_app_display.split(' ')[0]
        print("selected_app_display:", selected_app_display)  # This will print in the terminal
        print("selected_app_id:", selected_app_id)  # This will print in the terminal

    with col2:
        # Set default time range to '3 Months'
        selected_time_range = st.selectbox("Select Time Range", ['3 Months', '6 Months', '1 Year'], index=0,
                                           key="time_range")

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

    with col4:
        # Metrics selection with default "Select Range"
        metric_options = ['1 Day', '1 Week', '1 Month']
        selected_metric = st.selectbox("Select Metrics Range", [''] + metric_options, index=0, format_func=lambda x: 'Select Range' if x == '' else x, key="metric")



# Display metrics with st.metric
with st.container():
    col1, col2, col3 = st.columns(3)

    # Total Incidents
    current_incidents, previous_incidents, percentage_change = get_total_incidents(selected_app_id, selected_time_range, df, selected_metric)
    delta_incidents = current_incidents - previous_incidents
    col1.metric("Total Incidents", current_incidents, delta=f"{delta_incidents:+.0f} ({abs(percentage_change):.2f}%)")

    # Risk
    risk_info = assess_risk(df, selected_app_id, baseline_avg_incidents)
    col2.metric("Risk", risk_info['level'], delta=risk_info.get('delta', ''))

    # Average Downtime
    average_downtime = calculate_average_downtime(df, selected_app_id, selected_time_range, start_date, end_date, selected_metric)
    col3.metric("Average Downtime (minutes)", f"{average_downtime:.2f}")

# Severity metrics in the sidebar
with st.sidebar:
    st.header("Severity Metrics")
    severity_counts, severity_deltas, severity_percentage_changes = get_severity_incidents(selected_app_id, selected_time_range, df, selected_metric)
    for severity, count in severity_counts.items():
        st.metric(
            f"{severity} Incidents",
            count,
            delta=f"{severity_deltas[severity]:+.0f} ({abs(severity_percentage_changes[severity]):.2f}%)"
        )

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
