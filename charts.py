import pandas as pd
import plotly.express as px
import streamlit as st


def generate_graph(app_id, time_range, df, start_date=None, end_date=None):
    # Ensure 'date' column is in datetime format
    df['date'] = pd.to_datetime(df['date'])

    current_date = df['date'].max()

    if start_date and end_date:
        # Filter data based on selected date range
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        df_time_filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        date_label_format = '%d %b %Y'
        title_time_range = f"{start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}"
        hover_date_format = '%d %b %Y'
    else:
        # Filter data based on predefined time range
        if time_range == '6 Months':
            start_of_range = (current_date - pd.DateOffset(months=5)).replace(day=1)
        elif time_range == '3 Months':
            start_of_range = (current_date - pd.DateOffset(months=2)).replace(day=1)
        elif time_range == '1 Year':
            start_of_range = (current_date - pd.DateOffset(years=1)).replace(day=1)
        else:
            start_of_range = current_date.replace(day=1)  # Default to current month

        df_time_filtered = df[(df['date'] >= start_of_range) & (df['date'] <= current_date)]
        date_label_format = '%b %Y'
        title_time_range = f"{start_of_range.strftime('%d %b %Y')} to {current_date.strftime('%d %b %Y')}"
        hover_date_format = '%b %Y'

    # Aggregate counts by date
    df_time_filtered['date'] = df_time_filtered['date'].dt.to_period('D') if start_date and end_date else \
    df_time_filtered['date'].dt.to_period('M')
    incident_trends = df_time_filtered[df_time_filtered['appId'] == app_id].groupby('date').size().reset_index(
        name='incident_count')
    incident_trends['date_end'] = incident_trends['date'].dt.to_timestamp()  # Get the last day of each period
    incident_trends['date_label'] = incident_trends['date_end'].dt.strftime('%d %b %Y') if start_date and end_date else \
    incident_trends['date_end'].dt.strftime('%b %Y')  # Label for the x-axis

    # Create an interactive line chart
    fig = px.line(incident_trends, x='date_label', y='incident_count',
                  title=f'Trends of SRE Incidents for App ID: {app_id} from {title_time_range}',
                  labels={'date_label': 'Date' if start_date and end_date else 'Month',
                          'incident_count': 'Number of Incidents'},
                  markers=True)

    fig.update_traces(mode='markers+lines', line=dict(color='red'),
                      hovertemplate='Date: %{customdata}<br>Incidents: %{y}',
                      customdata=incident_trends['date_end'].dt.strftime(hover_date_format))

    fig.update_layout(
        xaxis_title='Date' if start_date and end_date else 'Month',
        yaxis_title='Number of Incidents',
        hovermode='x',
        yaxis=dict(tickmode='linear', tick0=0, dtick=2),  # Ensure y-axis has intervals of 2
        title={
            'text': f'Trends of SRE Incidents for App ID: {app_id} from {title_time_range}',
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis=dict(tickformat=date_label_format)  # Format x-axis to show date or month/year
    )

    return fig


def generate_source_graph(app_id, time_range, df, start_date=None, end_date=None):
    # Ensure 'date' column is in datetime format
    df['date'] = pd.to_datetime(df['date'])
    current_date = df['date'].max()

    if start_date and end_date:
        # Ensure both dates are provided
        try:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            df_time_filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            title_time_range = f"{start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}"
        except Exception as e:
            st.error(f"Error in date range filtering: {e}")
            return
    else:
        # Handle predefined time ranges
        if time_range == '6 Months':
            start_of_range = (current_date - pd.DateOffset(months=5)).replace(day=1)
        elif time_range == '3 Months':
            start_of_range = (current_date - pd.DateOffset(months=2)).replace(day=1)
        elif time_range == '1 Year':
            start_of_range = (current_date - pd.DateOffset(years=1)).replace(day=1)
        else:
            start_of_range = current_date.replace(day=1)  # Default to current month

        df_time_filtered = df[(df['date'] >= start_of_range) & (df['date'] <= current_date)]
        title_time_range = f"{start_of_range.strftime('%d %b %Y')} to {current_date.strftime('%d %b %Y')}"

    if df_time_filtered.empty:
        st.warning("No data available for the selected range.")
        return

    # Aggregate counts by source
    incident_sources = df_time_filtered[df_time_filtered['appId'] == app_id]['source'].value_counts().reset_index()
    incident_sources.columns = ['source', 'incident_count']

    # Create an interactive bar chart
    fig = px.bar(incident_sources, x='source', y='incident_count',
                 title=f'Sources of SRE Incidents for App ID: {app_id} from {title_time_range}',
                 labels={'source': 'Source', 'incident_count': 'Number of Incidents'})

    fig.update_traces(marker_color='black')

    fig.update_layout(
        xaxis_title='Source',
        yaxis_title='Number of Incidents',
        hovermode='x',
        yaxis=dict(tickmode='linear', tick0=0, dtick=2),  # Ensure y-axis has intervals of 2
        title={
            'text': f'Sources of SRE Incidents for App ID: {app_id} from {title_time_range}',
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    return fig


def generate_pie_chart(app_id, time_range, df, start_date=None, end_date=None):
    # Ensure 'date' column is in datetime format
    df['date'] = pd.to_datetime(df['date'])
    current_date = df['date'].max()

    if start_date and end_date:
        # Ensure both dates are provided
        try:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            df_time_filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            title_time_range = f"{start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}"
        except Exception as e:
            st.error(f"Error in date range filtering: {e}")
            return
    else:
        # Handle predefined time ranges
        if time_range == '6 Months':
            start_of_range = (current_date - pd.DateOffset(months=5)).replace(day=1)
        elif time_range == '3 Months':
            start_of_range = (current_date - pd.DateOffset(months=2)).replace(day=1)
        elif time_range == '1 Year':
            start_of_range = (current_date - pd.DateOffset(years=1)).replace(day=1)
        else:
            start_of_range = current_date.replace(day=1)  # Default to current month

        df_time_filtered = df[(df['date'] >= start_of_range) & (df['date'] <= current_date)]
        title_time_range = f"{start_of_range.strftime('%d %b %Y')} to {current_date.strftime('%d %b %Y')}"

    if df_time_filtered.empty:
        st.warning("No data available for the selected range.")
        return

    # Filter the data for the specific appId
    df_specific_app = df_time_filtered[df_time_filtered['appId'] == app_id]

    # Group by severity, and count the number of incidents
    incident_severity = df_specific_app.groupby(['severity']).size().reset_index(name='incident_count')

    # Define custom colors for the red-black theme
    colors = ["#E1D8D6", "#050100", "#8C8786", "#FC2F03", "#B42A0D", "#936960", "#F95330"]

    # Create an interactive pie chart
    fig = px.pie(incident_severity, names='severity', values='incident_count',
                 title=f'Severity Distribution for App ID: {app_id} from {title_time_range}',
                 labels={'severity': 'Severity', 'incident_count': 'Number of Incidents'},
                 hole=0.3,  # Add a hole in the middle for a donut chart
                 color_discrete_sequence=colors)  # Apply custom color sequence

    # Update layout for better readability
    fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#000000', width=2)))  # Black border for better contrast
    fig.update_layout(
        title={
            'text': f'Severity Distribution for App ID: {app_id} from {title_time_range}',
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        font=dict(color='black')  # Default text color
    )

    return fig


def generate_severity_bar_chart(app_id, time_range, df, start_date=None, end_date=None):
    # Ensure 'date' column is in datetime format
    df['date'] = pd.to_datetime(df['date'])
    current_date = df['date'].max()

    if start_date and end_date:
        # Ensure both dates are provided
        try:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            df_time_filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            title_time_range = f"{start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}"
        except Exception as e:
            st.error(f"Error in date range filtering: {e}")
            return
    else:
        # Handle predefined time ranges
        if time_range == '6 Months':
            start_of_range = (current_date - pd.DateOffset(months=5)).replace(day=1)
        elif time_range == '3 Months':
            start_of_range = (current_date - pd.DateOffset(months=2)).replace(day=1)
        elif time_range == '1 Year':
            start_of_range = (current_date - pd.DateOffset(years=1)).replace(day=1)
        else:
            start_of_range = current_date.replace(day=1)  # Default to current month

        df_time_filtered = df[(df['date'] >= start_of_range) & (df['date'] <= current_date)]
        title_time_range = f"{start_of_range.strftime('%d %b %Y')} to {current_date.strftime('%d %b %Y')}"

    if df_time_filtered.empty:
        st.warning("No data available for the selected range.")
        return

    # Filter the data for the specific appId
    df_specific_app = df_time_filtered[df_time_filtered['appId'] == app_id]

    # Aggregate counts by month and severity
    df_specific_app['month'] = df_specific_app['date'].dt.to_period('M')
    incident_severity_monthly = df_specific_app.groupby(['month', 'severity']).size().reset_index(name='incident_count')
    incident_severity_monthly['month_end'] = incident_severity_monthly['month'].dt.to_timestamp('M')  # Get the last day of each month
    incident_severity_monthly['month_label'] = incident_severity_monthly['month_end'].dt.strftime('%b %Y')  # Label for the x-axis

    # Define custom colors for the red-black theme
    colors = ["#E1D8D6", "#050100", "#8C8786", "#FC2F03", "#B42A0D", "#936960", "#F95330"]

    # Create an interactive bar chart
    fig = px.bar(incident_severity_monthly, x='month_label', y='incident_count', color='severity',
                 title=f'Total Number of Incidents by Severity for App ID: {app_id} from {title_time_range}',
                 labels={'month_label': 'Month', 'incident_count': 'Number of Incidents', 'severity': 'Severity'},
                 color_discrete_sequence=colors)  # Apply custom colors

    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Number of Incidents',
        hovermode='x',
        barmode='group',  # Group bars by severity
        yaxis=dict(tickmode='linear', tick0=0, dtick=2),  # Ensure y-axis has intervals of 2
        title={
            'text': f'Total Number of Incidents by Severity for App ID: {app_id} from {title_time_range}',
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    return fig

