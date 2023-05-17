import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import base64
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook
import numpy as np


def fill_missing_values(df):
    # Make a copy of the DataFrame
    df = df.copy()

    # Check if any missing values exist
    if df.isnull().sum().sum() == 0:
        st.write("No missing values found.")
        return df
    
    # Determine column data types
    numeric_cols = []
    non_numeric_cols = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)
        else:
            non_numeric_cols.append(col)
    
    # Recommend fill method based on column data types
    if len(non_numeric_cols) == 0:
        fill_method = "Fill with Mean"
        st.write("All columns are numeric. Filling missing values using the mean of the column.")
    else:
        if len(numeric_cols) == 0:
            fill_method = "Fill with Mode"
            st.write("All columns are non-numeric. Filling missing values using the mode of the column.")
        else:
            # Let the user choose the fill method
            fill_method = st.selectbox("Fill method for missing values:", ["Fill with Previous Value", "Fill with Next Value", "Fill with Mean", "Fill with Median", "Fill with Mode"])

    # Fill missing values using selected method
    if fill_method == "Fill with Previous Value":
        df.fillna(method='pad', inplace=True)
        st.write("Filled missing values using the previous value.")
    elif fill_method == "Fill with Next Value":
        df.fillna(method='bfill', inplace=True)
        st.write("Filled missing values using the next value.")
    elif fill_method == "Fill with Mean":
        df.fillna(df.mean(), inplace=True)
        st.write("Filled missing values using the mean of the column.")
    elif fill_method == "Fill with Median":
        df.fillna(df.median(), inplace=True)
        st.write("Filled missing values using the median of the column.")
    elif fill_method == "Fill with Mode":
        df.fillna(df.mode().iloc[0], inplace=True)
        st.write("Filled missing values using the mode of the column.")
        
    return df

def main():
    # Set Streamlit app title
    st.set_page_config(page_title="Dirty Data Cleaner", page_icon=":wrench:")
    # Define a variable to store the cleaned data
    cleaned_data = None
    # Upload file and display original data
    st.sidebar.title("Upload & Inspect Data")
    uploaded_file = st.sidebar.file_uploader("Choose a CSV or XLSX file", type=["csv", "xlsx"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Initialize values for showing/hiding sections
        show_original = True
        show_cleaned = True
    # Sidebar options to clean data
    st.sidebar.title("Data Cleaning Options")
    with st.sidebar.expander("Fill missing values"):
            col_to_fill = st.selectbox("Select column to check missing data:", df.columns)
            missing_data = df[col_to_fill].isnull().sum()
            st.write(f"Missing data in {col_to_fill} column:", missing_data)
            # Store the cleaned data in the temporary variable 
            cleaned_data = fill_missing_values(df)
            if show_cleaned:
                st.subheader("Cleaned Data")
                st.dataframe(cleaned_data, height=500)