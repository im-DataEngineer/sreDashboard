import streamlit as st
from metricsFunc import get_severity_incidents_sidebar, get_total_incidents_sidebar, calculate_average_downtime_sidebar, \
    assess_risk


# Function to display the Metrics page content
def metrics(df):
    # Verify content of app_displays
    app_displays = df['app_display'].unique()

    # Find the default display value for "B6OV"
    default_app_display = "B6OV (My Business Portal)"

    # Calculate the baseline average number of incidents using the entire DataFrame
    baseline_avg_incidents = df.groupby('appId').size().mean()

    # Create columns for dropdowns and button
    col1, col2, col3 = st.columns([3, 3, 1])

    with col1:
        # Set default appId to "B6OV"
        selected_app_display = st.selectbox("Select App ID", app_displays,
                                            index=list(app_displays).index(default_app_display), key="app_id")
        selected_app_id = selected_app_display.split(' ')[0]

    with col2:
        # Dropdown for selecting metrics range
        metric_options = ['1 Day', '1 Week', '1 Month', '3 Months', '6 Months', '1 Year']
        selected_metric = st.selectbox("Select Metrics Range", metric_options, index=0, key="metric_sidebar")

    with col3:
        # Button to open Jira
        jira_url = "https://your-jira-instance.atlassian.net/browse/TEST-123"  # Dummy Jira URL
        # Display the URL as a clickable button with modern styling
        st.markdown(
            f'''
            <div style="margin-top: 28px;">
                <a href="{jira_url}" target="_blank" style="
                    display: inline-block;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 600;
                    color: #ffffff;
                    background-color: #000000;
                    border: none;
                    border-radius: 4px;
                    text-align: center;
                    text-decoration: none;
                    cursor: pointer;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                    transition: background-color 0.3s, transform 0.2s;
                ">Open Jira</a>
            </div>
            ''',
            unsafe_allow_html=True
        )

    # Place Total Incidents and Average Downtime in the same row
    col1, col2, col3 = st.columns(3)

    with col1:
        # Total Incidents
        current_incidents, previous_incidents, percentage_change = get_total_incidents_sidebar(selected_app_id, df,
                                                                                               selected_metric)
        delta_incidents = current_incidents - previous_incidents
        st.metric("Total Incidents", current_incidents, delta=f"{delta_incidents:+.0f} ({abs(percentage_change):.2f}%)")

    with col2:
        # Average Downtime
        average_downtime = calculate_average_downtime_sidebar(df, selected_app_id, selected_metric)
        st.metric("Average Downtime (minutes)", f"{average_downtime:.2f}")

    with col3:
        # Risk
        risk_info = assess_risk(df, selected_app_id, baseline_avg_incidents)
        st.metric("Risk", risk_info['level'], delta=risk_info.get('delta', ''))

    # Severity metrics in the sidebar
    st.header("Severity Metrics")

    # Fetch severity metrics
    severity_counts, severity_deltas, severity_percentage_changes = get_severity_incidents_sidebar(selected_app_id, df,
                                                                                                   selected_metric)

    # Define the order of severity
    severity_order = ['P1', 'P2', 'P3', 'P4']

    # Initialize list for columns if metrics are available
    valid_metrics = []

    # Collect valid severity metrics
    for severity in severity_order:
        if severity in severity_counts and severity_counts[severity] > 0:
            valid_metrics.append(severity)

    # Only display if there are valid metrics
    if valid_metrics:
        # Create columns for the valid severity metrics
        columns = st.columns(len(valid_metrics))

        for i, severity in enumerate(valid_metrics):
            with columns[i]:
                count = severity_counts[severity]
                delta = severity_deltas[severity]
                percentage_change = severity_percentage_changes[severity]
                st.metric(
                    f"{severity} Incidents",
                    count,
                    delta=f"{delta:+.0f} ({abs(percentage_change):.2f}%)"
                )

    else:
        st.write("No severity metrics available.")
