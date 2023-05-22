import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import base64
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook
import numpy as np

def remove_duplicates(df):
    return df.drop_duplicates()

def recommend_data_types(df):
    """
    Recommends data types for each column in a pandas DataFrame based on its unique values.
    Parameters:
        - df: pandas DataFrame
    Returns:
        - recommendations: dictionary with column names as keys and recommended data types as values
    """
    # Initialize recommendations
    recommendations = {}

    # Iterate over columns
    for col in df.columns:
        # Get unique values in column as strings
        unique_vals = df[col].astype(str).unique()

        # Check if column has any missing values
        if pd.isnull(unique_vals).any():
            recommendations[col] = "object"
            continue

        # Check for boolean columns
        if len(unique_vals) == 2 and set(unique_vals) == {"False", "True"}:
            recommendations[col] = "bool"
            continue

        # Check for datetime columns
        try:
            pd.to_datetime(unique_vals)
            recommendations[col] = "datetime64[ns]"
            continue
        except ValueError:
            pass

        # Check for integer columns
        if all([val.isdigit() or (val.startswith("-") and val[1:].isdigit()) for val in unique_vals]):
            int_min = np.min([int(val) for val in unique_vals])
            int_max = np.max([int(val) for val in unique_vals])
            if -128 <= int_min and int_max <= 127:
                recommendations[col] = "int8"
            elif -32768 <= int_min and int_max <= 32767:
                recommendations[col] = "int16"
            elif -2147483648 <= int_min and int_max <= 2147483647:
                recommendations[col] = "int32"
            else:
                recommendations[col] = "int64"
            continue

        # Check for floating point columns
        if all([val.replace(".", "", 1).isdigit() or (val.startswith("-") and val[1:].replace(".", "", 1).isdigit()) for val in unique_vals]):
            recommendations[col] = "float64"
            continue

        # Default to object column
        recommendations[col] = "object"

    return recommendations
def apply_data_type_recommendations(df, recommendations):
    """
    Applies recommended data types to the columns in a pandas DataFrame.
    Parameters:
        - df: pandas DataFrame
        - recommendations: dictionary with column names as keys and recommended data types as values
    Returns:
        - df: pandas DataFrame with updated data types
    """
    for col, dtype in recommendations.items():
        df[col] = df[col].astype(dtype)
    
    return df

def remove_outdated(df, date_col, time_filter):
    cutoff_date = None
    
    if time_filter:
        cutoff_date = time_filter
    
    if cutoff_date:
        mask = pd.to_datetime(df[date_col]) >= cutoff_date
        df = df.loc[mask]
    
    return df

def replace_text_in_column(df, col_name, old_text, new_text):
    col_dtype = df[col_name].dtype
    
    if col_dtype == 'int64':
        new_text = int(new_text)
    elif col_dtype == 'float64':
        new_text = float(new_text)
    elif col_dtype == 'bool':
        new_text = bool(new_text)
    elif col_dtype == 'datetime64[ns]':
        new_text = pd.to_datetime(new_text)
    
    df[col_name] = df[col_name].astype(str).str.replace(old_text, str(new_text))
    df[col_name] = df[col_name].astype(col_dtype)
    
    return df
def automated_data_cleaning(data):
    # Copy the original data to avoid modifying the original dataset
    cleaned_data = data.copy()

    # Automatic Data Type Recognition
    data_types = cleaned_data.dtypes
    numeric_cols = data_types[data_types.apply(lambda x: pd.api.types.is_numeric_dtype(x))].index
    categorical_cols = data_types[data_types.apply(lambda x: pd.api.types.is_categorical_dtype(x))].index
    datetime_cols = data_types[data_types.apply(lambda x: pd.api.types.is_datetime64_dtype(x))].index

    # Automatic Missing Value Imputation
    for col in cleaned_data.columns:
        if cleaned_data[col].isnull().any():
            if col in numeric_cols:
                # Fill missing values with mean or median of the column
                if pd.api.types.is_integer_dtype(cleaned_data[col]):
                    cleaned_data[col].fillna(cleaned_data[col].mean(), inplace=True)
                else:
                    cleaned_data[col].fillna(cleaned_data[col].median(), inplace=True)
            elif col in categorical_cols:
                # Fill missing values with most frequent value in the column
                cleaned_data[col].fillna(cleaned_data[col].mode()[0], inplace=True)
            elif col in datetime_cols:
                # Fill missing values with forward fill
                cleaned_data[col].fillna(method='ffill', inplace=True)
            else:
                # Fill missing values with next available value in the column
                cleaned_data[col] = cleaned_data[col].fillna(method='bfill')

    return cleaned_data
    
def main():
    # Set Streamlit app title
    st.set_page_config(page_title="Dirty Data Cleaner", page_icon=":wrench:")
     # Instructions
    st.title("Dirty Data Cleaner")
    st.write("Welcome to the Dirty Data Cleaner web app!")
    st.write("This app allows you to clean and preprocess your data easily. Please follow the instructions below to get started:")

    # Step 1: Upload & Inspect Data
    st.subheader("Step 1: Upload & Inspect Data")
    st.write("Upload your CSV or XLSX file using the file uploader on the left sidebar.")
    st.write("Once uploaded, you can view the original data and apply various data cleaning operations.")

    # Step 2: Data Type Recommendations
    st.subheader("Step 2: Data Type Recommendations")
    st.write("In this step, the app recommends data types for each column in your dataset based on the unique values present.")
    st.write("You can view the recommended data types and apply them to the columns.")

    # Step 3: Change Data Types
    st.subheader("Step 3: Change Data Types")
    st.write("If you want to manually change the data types of specific columns, you can do so in this step.")
    st.write("Select the columns and their corresponding data types, and apply the changes.")

    # Step 4: Replace Text in Columns
    st.subheader("Step 4: Replace Text in Columns")
    st.write("If you need to replace specific text in a column, you can do that in this step.")
    st.write("Select the column, enter the text to replace, and the replacement text.")

    # Step 5: Remove Duplicates
    st.subheader("Step 5: Remove Duplicates")
    st.write("If your dataset contains duplicate rows, you can remove them in this step.")

    # Step 6: Remove Outdated Data
    st.subheader("Step 6: Remove Outdated Data")
    st.write("If your dataset has a date column and you want to remove rows based on a specific time range, you can do that here.")
    st.write("Select the date column and set the start and end dates/times.")

    # Step 7: Fill Missing Values
    st.subheader("Step 7: Fill Missing Values")
    st.write("If your dataset has missing values, you can fill them using various methods in this step.")
    st.write("Select the column to check missing data and choose the fill method.")

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


        # Sidebar option to hide or unhide sections
        st.sidebar.title("Show/Hide Sections")
        if st.sidebar.checkbox("Original Data", value=True, key="show_original"):
            show_original = True
        else:
            show_original = False
        if st.sidebar.checkbox("Cleaned Data", value=True, key="show_cleaned"):
            show_cleaned = True
        else:
            show_cleaned = False

        # Show original data
        if show_original:
            st.subheader("Original Data")
            st.dataframe(df, height=500)
        # Sidebar options to inspect data and clean it
        with st.sidebar.expander("Recommend data types for columns"):
            recommendations = recommend_data_types(df)
            st.write("Recommended data types:", recommendations)
            # Inside the "Recommend data types for columns" expander
            if st.button("Apply Recommendations"):
                cleaned_data = apply_data_type_recommendations(df, recommendations)
                st.write("Changed data types of recommended columns.")
                if show_cleaned:
                    st.subheader("Cleaned Data")
                    st.dataframe(cleaned_data, height=500)
        with st.sidebar.expander("View column data types"):
            col_to_dtype = {col: st.selectbox(col, ['int', 'float', 'object', 'bool', 'datetime64[ns]'], key=col) for col in df.columns}
            if st.button("Change Data Types"):
                df = df.astype(col_to_dtype)
                cleaned_data = df.astype(col_to_dtype)
                st.write("Changed data types of selected columns.")
                if show_cleaned:
                    st.subheader("Cleaned Data")
                    st.dataframe(cleaned_data, height=500)       

        with st.sidebar.expander("Show unique values in column"):
            col = st.selectbox("Select column:", df.columns)
            unique_values = df[col].astype(str).unique()
            st.write(f"Unique values in {col} column:", unique_values.tolist())
        # Sidebar section
        with st.sidebar.expander("Replace text in column"):
            col_to_replace = st.selectbox("Select column to replace text:", df.columns)
            old_text = st.text_input("Enter text to replace:")
            new_text = st.text_input("Enter replacement text:")


            if st.button("Replace Text"):
                cleaned_data = replace_text_in_column(df, col_to_replace, old_text, new_text)
                st.write("Replaced text in column:", col_to_replace)
                if show_cleaned:
                    st.subheader("Cleaned Data")
                    st.dataframe(cleaned_data, height=500)
        # Sidebar options to clean data
        st.sidebar.title("Data Cleaning Options")
        with st.sidebar.expander("Remove duplicates"):
            if st.button("Remove Duplicates"):
                df = remove_duplicates(df)
                cleaned_data = remove_duplicates(df)
                st.write("Removed duplicate rows.")
                if show_cleaned:
                    st.subheader("Cleaned Data")
                    st.dataframe(cleaned_data, height=500)
        with st.sidebar.expander("Remove outdated data"):
            date_col = st.selectbox("Select date column:", df.columns)
            start_date = st.date_input("Select start date:")
            end_date = st.date_input("Select end date:")
            start_time = st.time_input("Select start time:")
            end_time = st.time_input("Select end time:")
            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(end_date, end_time)
            time_filter = [start_datetime, end_datetime]

            if st.button("Remove Outdated Data"):
                cleaned_data = remove_outdated(df, date_col, time_filter)
                st.write("Removed outdated rows.")

                if show_cleaned:
                    st.subheader("Cleaned Data")
                    st.dataframe(cleaned_data, height=500)
        with st.sidebar.expander("Auto fill missing values"):
            if st.button("Auto fill missing values"):
                df = automated_data_cleaning(df)
                cleaned_data = df
                st.subheader("Cleaned Data")
                st.dataframe(cleaned_data, height=500)

        # Show cleaned data
        if show_cleaned:
            st.subheader("Cleaned Data")
            st.dataframe(cleaned_data, height=500)
            # Download cleaned data as file
            file_format = uploaded_file.name.split(".")[-1]

            if file_format == 'csv':
                data = cleaned_data.to_csv(index=False)
            else:
                wb = Workbook()
                ws = wb.active
                for r in dataframe_to_rows(cleaned_data, index=False, header=True):
                    ws.append(r)
                data = openpyxl.writer.excel.save_virtual_workbook(wb)

            b64 = base64.b64encode(data).decode()
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="cleaned_data.{file_format}"><button>Download {file_format.upper()}</button></a>'
            st.markdown(href, unsafe_allow_html=True)
            # Clear history if user uploads a new file
            if uploaded_file != st.session_state.get('uploaded_file', None):
                st.session_state.uploaded_file = uploaded_file
                st.session_state.cleaned_data = []

if __name__ == "__main__":
    main()
