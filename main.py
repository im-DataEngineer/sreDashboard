import streamlit as st
import pandas as pd
import os
import glob
from metrics import metrics
from graphs import graphs
from forecasting import forecasting

# Set page configuration to use a wide layout
st.set_page_config(layout="wide")

# Load JSON data into a DataFrame
df = pd.concat(map(pd.read_json, glob.glob(os.path.join('', "*.json"))))

# Convert the date column to datetime
df['date'] = pd.to_datetime(df['date'])

# Combine appId and appName for display in the dropdown
df['app_display'] = df['appId'].str.strip() + ' (' + df['appName'].str.strip() + ')'

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
        .st-emotion-cache-1whx7iy p{
        font-size : 18px !important;
        }
        </style>
        """, unsafe_allow_html=True)

    # Creating tabs for Metrics and Graphs
    tab1, tab2, tab3 = st.tabs(["Metrics", "Forecasting", "📈 Chart"])

    with tab1:
        metrics(df)

    with tab2:
        forecasting()

    with tab3:
        graphs(df)

if __name__ == "__main__":
    main()