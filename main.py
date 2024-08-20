import streamlit as st
import pandas as pd
import os
import glob
from metrics import metrics
from graphs import graphs

# Set page configuration to use a wide layout
st.set_page_config(layout="wide")

# Load JSON data into a DataFrame
df = pd.concat(map(pd.read_json, glob.glob(os.path.join('', "*.json"))))

# Convert the date column to datetime
df['date'] = pd.to_datetime(df['date'])

# Combine appId and appName for display in the dropdown
df['app_display'] = df['appId'].str.strip() + ' (' + df['appName'].str.strip() + ')'


# Main function with tabs for navigation
def main():
    # Custom CSS to ensure tabs span the entire width of the screen
    st.markdown("""
        <style>
        /* Styling for the tab container to ensure full width */
        .css-1v3fvcr {
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        /* Styling for each tab to ensure they are full width */
        .css-14xtw13 {
            display: flex;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        .css-14xtw13 > div {
            flex: 1;
            text-align: center;
            padding: 10px;
            box-sizing: border-box;
            border: none; /* Remove borders if present */
        }
        </style>
        """, unsafe_allow_html=True)

    # Creating tabs for Metrics and Graphs
    tab1, tab2 = st.tabs(["Metrics", "📈 Chart"])

    with tab1:
        metrics(df)

    with tab2:
        graphs(df)

if __name__ == "__main__":
    main()