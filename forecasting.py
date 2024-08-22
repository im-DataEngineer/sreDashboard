import streamlit as st
import pandas as pd
from forecastingModel import prediction

def forecasting():

    with st.container():
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            # Date range selection
            date_range = st.date_input("Select Date Range", [], key="forecasting_date_range_key")
            if date_range:
                if len(date_range) == 2:
                    start_date, end_date = date_range
                else:
                    start_date = end_date = None
            else:
                start_date = end_date = None

        with col2:
            st.markdown("""
                <h3 style='font-size: 20px; display: inline; margin-left: 10px;'>Source:</h3>
                <span style='font-size: 18px; display: inline; margin-left: 10px;'>Auto Bridge</span>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
                <h3 style='font-size: 20px; display: inline; margin: 0;'>Category:</h3>
                <span style='font-size: 18px; display: inline; margin-left: 2px;'>Operational Issues</span>
            """, unsafe_allow_html=True)

    if start_date and end_date:
        with st.container():
            # Generate the list of dates using the prediction function
            list_of_dates = prediction(start_date, end_date)

            if list_of_dates:
                # Create a DataFrame for tabular display
                df = pd.DataFrame(list_of_dates, columns=["Predicted Dates"])

                # Add a serial number column
                df.insert(0, 'S.No', range(1, len(df) + 1))

                # Reset the index to remove the default index column
                df.reset_index(drop=True, inplace=True)

                # Display the DataFrame as a table
                st.write("Predicted Dates:")
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.write("No predictions available for the selected date range.")  # Handle case when no predictions are returned
