import streamlit as st
import pandas as pd
from charts import generate_graph, generate_source_graph, generate_pie_chart, generate_severity_bar_chart
from metrics_old import assess_risk, get_total_incidents, get_severity_incidents, calculate_average_downtime

def graphs(df):
    # Verify content of app_displays
    app_displays = df['app_display'].unique()

    # Find the default display value for "B6OV"
    default_app_display = "B6OV (My Business Portal)"

    # Calculate the baseline average number of incidents using the entire DataFrame
    baseline_avg_incidents = df.groupby('appId').size().mean()

    # Create container for dropdowns
    with st.container():
        col1, col2, col3 = st.columns([1, 1, 2])

        # Dropdown menus in the first row
        with col1:
            # Set default appId to "B6OV"
            selected_app_display = st.selectbox("Select App ID", app_displays,
                                                index=list(app_displays).index(default_app_display), key="appId")
            selected_app_id = selected_app_display.split(' ')[0]

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

    # Display metrics with st.metric
    with st.container():
        columns = st.columns([1, 1])

        # Total Incidents
        current_incidents, previous_incidents, percentage_change = get_total_incidents(selected_app_id,
                                                                                       selected_time_range, df)
        delta_incidents = current_incidents - previous_incidents
        columns[0].metric("Total Incidents", current_incidents)

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
            fig_severity_bar = generate_severity_bar_chart(selected_app_id, selected_time_range, df, start_date,
                                                           end_date)
            st.plotly_chart(fig_severity_bar, use_container_width=True)


