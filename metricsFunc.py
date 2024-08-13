import pandas as pd

def get_total_incidents_sidebar(app_id, df, metric_range=None):
    current_date = df['date'].max()

    # Determine the start of the current period based on the selected metric range
    if metric_range:
        if metric_range == '1 Day':
            start_of_range = current_date - pd.DateOffset(days=1)
        elif metric_range == '1 Week':
            start_of_range = current_date - pd.DateOffset(weeks=1)
        elif metric_range == '1 Month':
            start_of_range = (current_date - pd.DateOffset(months=1)).replace(day=1)
        elif metric_range == '3 Months':
            start_of_range = (current_date - pd.DateOffset(months=2)).replace(day=1)
        elif metric_range == '6 Months':
            start_of_range = (current_date - pd.DateOffset(months=5)).replace(day=1)
        elif metric_range == '1 Year':
            start_of_range = (current_date - pd.DateOffset(years=1)).replace(day=1)
    else:
        start_of_range = current_date

    # Filter data from the start of the current period to the end of the current period
    df_time_filtered = df[(df['date'] >= start_of_range) & (df['date'] <= current_date)]
    current_incidents = df_time_filtered[df_time_filtered['appId'] == app_id].shape[0]

    # Determine the start of the previous period based on the selected metric range
    if metric_range:
        if metric_range == '1 Day':
            start_of_previous_range = start_of_range - pd.DateOffset(days=1)
        elif metric_range == '1 Week':
            start_of_previous_range = start_of_range - pd.DateOffset(weeks=1)
        elif metric_range == '1 Month':
            start_of_previous_range = (start_of_range - pd.DateOffset(months=1)).replace(day=1)
        elif metric_range == '3 Months':
            start_of_previous_range = (start_of_range - pd.DateOffset(months=3)).replace(day=1)
        elif metric_range == '6 Months':
            start_of_previous_range = (start_of_range - pd.DateOffset(months=6)).replace(day=1)
        elif metric_range == '1 Year':
            start_of_previous_range = (start_of_range - pd.DateOffset(years=1)).replace(day=1)

    # Filter data from the start of the previous period to the end of the previous period
    df_previous_filtered = df[(df['date'] >= start_of_previous_range) & (df['date'] < start_of_range)]
    previous_incidents = df_previous_filtered[df_previous_filtered['appId'] == app_id].shape[0]

    # Calculate percentage change
    if previous_incidents == 0:
        percentage_change = 0  # Infinite increase if there were no previous incidents
    else:
        percentage_change = ((current_incidents - previous_incidents) / previous_incidents) * 100

    return current_incidents, previous_incidents, percentage_change

def get_severity_incidents_sidebar(app_id, df, metric_range=None):
    current_date = df['date'].max()

    # Define metric range mapping
    metric_range_map = {
        '1 Day': pd.DateOffset(days=1),
        '1 Week': pd.DateOffset(weeks=1),
        '1 Month': pd.DateOffset(months=1),
        '3 Months': pd.DateOffset(months=2),
        '6 Months': pd.DateOffset(months=5),
        '1 Year': pd.DateOffset(years=1)
    }

    # Determine the start and end dates based on the metric range
    if metric_range and metric_range in metric_range_map:
        if metric_range in ['3 Months', '6 Months', '1 Year']:
            start_of_range = (current_date - metric_range_map[metric_range]).replace(day=1)
        else:
            start_of_range = current_date - metric_range_map[metric_range]
        end_of_range = current_date

        # Define previous period for metrics
        prev_end_of_range = start_of_range - pd.DateOffset(days=1)
        if metric_range in ['3 Months', '6 Months', '1 Year']:
            prev_start_of_range = (start_of_range - metric_range_map[metric_range]).replace(day=1)
        else:
            prev_start_of_range = start_of_range - metric_range_map[metric_range]
    else:
        start_of_range = current_date.replace(day=1)  # Default to current month
        prev_start_of_range = (current_date - pd.DateOffset(months=1)).replace(day=1)
        prev_end_of_range = start_of_range - pd.DateOffset(days=1)

    # Filter data from the start of the range to the end of the current period
    df_time_filtered = df[(df['date'] >= start_of_range) & (df['date'] <= end_of_range)]
    df_prev_time_filtered = df[(df['date'] >= prev_start_of_range) & (df['date'] <= prev_end_of_range)]

    # Filter the data for the specific appId
    df_specific_app = df_time_filtered[df_time_filtered['appId'] == app_id]
    df_prev_specific_app = df_prev_time_filtered[df_prev_time_filtered['appId'] == app_id]

    # Group by severity and count the number of incidents
    severity_counts = df_specific_app['severity'].value_counts().to_dict()
    prev_severity_counts = df_prev_specific_app['severity'].value_counts().to_dict()

    # Calculate deltas and percentage changes
    severity_deltas = {}
    severity_percentage_changes = {}
    for severity in set(severity_counts.keys()).union(prev_severity_counts.keys()):
        current_count = severity_counts.get(severity, 0)
        previous_count = prev_severity_counts.get(severity, 0)
        delta = current_count - previous_count
        if previous_count == 0:
            percentage_change = 100  # When previous count is 0, use 100% as a special case
        else:
            percentage_change = (delta / previous_count * 100) if previous_count != 0 else 0
        severity_deltas[severity] = delta
        severity_percentage_changes[severity] = percentage_change

    return severity_counts, severity_deltas, severity_percentage_changes


def calculate_average_downtime_sidebar(df: pd.DataFrame, app_id: str, metric_range=None) -> float:
    """
    Calculate the average downtime for a specific appId within a given time range.
    """

    # Determine the start of the current period based on the selected metric range
    current_date = df['date'].max()

    if metric_range:
        if metric_range == '1 Day':
            start_of_range = current_date - pd.DateOffset(days=1)
        elif metric_range == '1 Week':
            start_of_range = current_date - pd.DateOffset(weeks=1)
        elif metric_range == '1 Month':
            start_of_range = (current_date - pd.DateOffset(months=1)).replace(day=1)
        elif metric_range == '3 Months':
            start_of_range = (current_date - pd.DateOffset(months=2)).replace(day=1)
        elif metric_range == '6 Months':
            start_of_range = (current_date - pd.DateOffset(months=5)).replace(day=1)
        elif metric_range == '1 Year':
            start_of_range = (current_date - pd.DateOffset(years=1)).replace(day=1)
    else:
        start_of_range = current_date

    # Filter data based on the calculated start and end dates
    filtered_df = df[(df['appId'] == app_id) & (df['date'] >= start_of_range) & (df['date'] <= current_date)]

    # Calculate average downtime
    average_downtime = filtered_df['duration'].mean() if not filtered_df.empty else 0.0

    return average_downtime

def assess_risk(df: pd.DataFrame, app_id: str, baseline_avg_incidents: float) -> dict:
    # Filter data for the specific appId
    df_specific_app = df[df['appId'] == app_id]

    # Calculate current number of incidents for the specific appId
    current_incident_count = df_specific_app.shape[0]

    # Calculate percentage difference
    percentage_diff = ((current_incident_count - baseline_avg_incidents) / baseline_avg_incidents) * 100

    # Assess Risk
    if percentage_diff > 70:
        return {'level': 'High', 'color': 'red'}
    elif percentage_diff > 40:
        return {'level': 'Medium', 'color': 'orange'}
    else:
        return {'level': 'Low', 'color': 'green'}
