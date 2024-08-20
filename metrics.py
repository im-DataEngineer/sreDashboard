import streamlit as st
from fpdf import FPDF
from metricsFunc import get_severity_incidents_sidebar, get_total_incidents_sidebar, calculate_average_downtime_sidebar, \
    assess_risk
from io import BytesIO
import base64


def encode_pdf(pdf_output):
    # Get the byte data from the BytesIO object
    pdf_data = pdf_output.getvalue()
    # Encode the byte data in base64
    return base64.b64encode(pdf_data).decode('utf-8')

# Function to generate PDF with metrics in tabular format
def generate_pdf(df, selected_app_id, selected_app_display, selected_metric, baseline_avg_incidents):
    pdf = FPDF()
    pdf.add_page()

    # Title in bold black with appId and display name
    pdf.set_font("Arial", style='B', size=12)  # Set font to bold
    pdf.set_text_color(0, 0, 0)  # Set text color to black
    pdf.cell(200, 10, txt=f"Metrics Report for {selected_app_display}", ln=True, align='C')
    pdf.ln(10)  # Add a line break

    # Metrics Range
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Metrics Range: {selected_metric}", ln=True)
    pdf.ln(8)  # Add a line break

    # Total Incidents
    current_incidents, previous_incidents, percentage_change = get_total_incidents_sidebar(selected_app_id, df, selected_metric)
    delta_incidents = current_incidents - previous_incidents
    pdf.cell(200, 10, txt=f"Total Incidents: {current_incidents} \n({delta_incidents:+.0f} ({percentage_change:+.2f}%))", ln=True)

    # Average Downtime
    average_downtime = calculate_average_downtime_sidebar(df, selected_app_id, selected_metric)
    pdf.cell(200, 10, txt=f"Average Downtime (minutes): {average_downtime:.2f}", ln=True)

    # Risk
    risk_info = assess_risk(df, selected_app_id, baseline_avg_incidents)
    pdf.cell(200, 10, txt=f"Risk Level: {risk_info['level']}", ln=True)

    pdf.ln(10)  # Add a line break before the table

    # Severity Metrics Table
    pdf.set_font("Arial", size=10)
    severity_counts, severity_deltas, severity_percentage_changes = get_severity_incidents_sidebar(selected_app_id, df, selected_metric)
    severity_order = ['P1', 'P2', 'P3', 'P4']

    # Table Header
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(60, 10, 'Severity', 1, 0, 'C', fill=True)
    pdf.cell(40, 10, 'Count', 1, 0, 'C', fill=True)
    pdf.cell(50, 10, 'Delta', 1, 0, 'C', fill=True)
    pdf.cell(40, 10, 'Change (%)', 1, 1, 'C', fill=True)  # 1, 1 moves to next line after cell

    # Table Content
    for severity in severity_order:
        if severity in severity_counts and severity_counts[severity] > 0:
            count = severity_counts[severity]
            delta = severity_deltas[severity]
            percentage_change = severity_percentage_changes[severity]
            pdf.cell(60, 10, severity, 1)
            pdf.cell(40, 10, str(count), 1)
            pdf.cell(50, 10, f"{delta:+.0f}", 1)
            pdf.cell(40, 10, f"{percentage_change:+.2f}%", 1, 1)  # Include + or - sign in percentage

    return pdf


# Function to display the Metrics page content
def metrics(df):
    # Verify content of app_displays
    app_displays = df['app_display'].unique()

    # Find the default display value for "B6OV"
    default_app_display = "B6OV (My Business Portal)"

    # Calculate the baseline average number of incidents using the entire DataFrame
    baseline_avg_incidents = df.groupby('appId').size().mean()

    # Create columns for dropdowns and buttons
    col1, col2, col3, col4 = st.columns([3, 3, 1, 1])

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
        st.markdown(
            f'''
            <div style="margin-top: 5px; margin-left: 15px">
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

    with col4:
        # Generate PDF
        pdf = generate_pdf(df, selected_app_id, selected_app_display, selected_metric, baseline_avg_incidents)

        # Save PDF to a BytesIO object
        pdf_output = BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)

        # Encode PDF
        pdf_base64 = encode_pdf(pdf_output)

        # Button to download PDF, styled like the Open Jira button
        st.markdown(
            f'''
            <div style="margin-top: 5px;">
                <a href="data:application/pdf;base64,{pdf_base64}"
                    download="Metrics_Report_{selected_app_id}.pdf"
                    style="
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
                    ">Export</a>
            </div>
            ''',
            unsafe_allow_html=True
        )

    # Place Total Incidents and Average Downtime in the same row
    col1, col2, col3 = st.columns(3)

    with col1:
        # Total Incidents
        current_incidents, previous_incidents, percentage_change = get_total_incidents_sidebar(selected_app_id, df, selected_metric)
        delta_incidents = current_incidents - previous_incidents
        st.metric("Total Incidents", current_incidents, delta=f"{delta_incidents:+.0f} ({abs(percentage_change):.2f}%)", help="Total number of incidents in the selected period.")

    with col2:
        # Average Downtime
        average_downtime = calculate_average_downtime_sidebar(df, selected_app_id, selected_metric)
        st.metric("Average Downtime (minutes)", f"{average_downtime:.2f}", help="Average downtime of the application in minutes.")

    with col3:
        # Risk
        risk_info = assess_risk(df, selected_app_id, baseline_avg_incidents)
        st.metric("Risk", risk_info['level'], help="Risk level based on incidents and other metrics.")

    # Severity metrics in the sidebar
    st.header("Severity Metrics")

    # Fetch severity metrics
    severity_counts, severity_deltas, severity_percentage_changes = get_severity_incidents_sidebar(selected_app_id, df, selected_metric)

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
                st.metric(f"{severity} Incidents", count, delta=f"{delta:+.0f} ({abs(percentage_change):.2f}%)", help=f"{severity} incidents in the selected period.")
    else:
        st.write("No severity metrics available.")
