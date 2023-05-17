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
        if all([val.isdigit() or val.startswith("-") and val[1:].isdigit() for val in unique_vals]):
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
    Applies recommended data types to columns in a pandas DataFrame.
    Parameters:
        - df: pandas DataFrame
        - recommendations: dictionary with column names as keys and recommended data types as values
    Returns:
        - df: pandas DataFrame with updated data types
    """
    # Iterate over recommended data types
    for col, dtype in recommendations.items():
        # Update data type of column
        df[col] = df[col].astype(dtype)

    return df

def remove_outdated(df, date_col, time_filter):
    if time_filter:
        start_datetime = time_filter[0]
        end_datetime = time_filter[1]
        mask = (df[date_col] >= start_datetime) & (df[date_col] <= end_datetime)
        df = df.loc[mask]
    else:
        if time_filter == "Last 24 Hours":
            cutoff_date = datetime.now() - timedelta(days=1)
        elif time_filter == "Last 7 Days":
            cutoff_date = datetime.now() - timedelta(weeks=1)
        elif time_filter == "Last 30 Days":
            cutoff_date = datetime.now() - timedelta(weeks=4)
        else:
            cutoff_date = None

        if cutoff_date is not None:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df = df[df[date_col] > cutoff_date]

    return df

def replace_text_in_column(df, col_name, old_text, new_text):
    col_dtype = df[col_name].dtype
    
    if col_dtype == 'int64':
        new_text = int(new_text)
    elif col_dtype == 'float64':
        new_text = float(new_text)
    elif col_dtype == 'bool':
        new_text = bool(new_text)
    
    df[col_name] = df[col_name].astype('str').str.replace(old_text, str(new_text))
    df[col_name] = df[col_name].astype(col_dtype)
    
    return df

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


# Function to remove outliers using z-score
def remove_outliers_zscore(data, column, threshold):
    z_scores = (data[column] - data[column].mean()) / data[column].std()
    filtered_data = data[abs(z_scores) < threshold]
    return filtered_data

# Function to remove outliers using IQR method
def remove_outliers_iqr(data, column, whisker_width):
    q1 = data[column].quantile(0.25)
    q3 = data[column].quantile(0.75)
    iqr = q3 - q1
    lower_whisker = q1 - whisker_width * iqr
    upper_whisker = q3 + whisker_width * iqr
    filtered_data = data[(data[column] >= lower_whisker) & (data[column] <= upper_whisker)]
    return filtered_data

def main():
    # Set Streamlit app title
    st.set_page_config(page_title="Dirty Data Cleaner", page_icon=":wrench:")

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
        show_history = False

        # Sidebar option to hide or unhide sections
        st.sidebar.title("Show/Hide Sections")
        if st.sidebar.checkbox("Original Data", value=True):
            show_original = True
        else:
            show_original = False
        if st.sidebar.checkbox("Cleaned Data", value=True):
            show_cleaned = True
        else:
            show_cleaned = False
        if st.sidebar.checkbox("Version History", value=False):
            show_history = True
        else:
            show_history = False

        # Show original data
        if show_original:
            st.subheader("Original Data")
            st.dataframe(df, height=500)

        # Sidebar options to inspect data and clean it
        with st.sidebar.expander("Recommend data types for columns"):
            recommendations = recommend_data_types(df)
            st.write("Recommended data types:", recommendations)
            if st.button("Apply Recommendations"):
                df = apply_data_type_recommendations(df, recommendations)
                st.write("Changed data types of recommended columns.")
                if show_cleaned:
                    st.subheader("Cleaned Data")
                    st.dataframe(df, height=500)
        with st.sidebar.expander("View column data types"):
            col_to_dtype = {col: st.selectbox(col, ['int', 'float', 'object', 'bool', 'datetime64[ns]'], key=col) for col in df.columns}
            if st.button("Change Data Types"):
                df = df.astype(col_to_dtype)
                st.write("Changed data types of selected columns.")
                if show_cleaned:
                    st.subheader("Cleaned Data")
                    st.dataframe(df, height=500)       
        with st.sidebar.expander("Show unique values in column"):
            col = st.selectbox("Select column:", df.columns)
            unique_values = df[col].astype(str).unique()
            st.write(f"Unique values in {col} column:", unique_values.tolist())
        with st.sidebar.expander("Replace text in column"):
            col_to_replace = st.selectbox("Select column to replace text:", df.columns)
            old_text = st.text_input("Enter text to replace:")
            new_text = st.text_input("Enter replacement text:")
            if st.button("Replace Text"):
                df = replace_text_in_column(df, col_to_replace, old_text, new_text)
                st.write("Replaced text in column:", col_to_replace)
                if show_cleaned:
                    st.subheader("Cleaned Data")
                    st.dataframe(df, height=500)
        # Sidebar options to clean data
        st.sidebar.title("Data Cleaning Options")
        with st.sidebar.expander("Remove duplicates"):
            if st.button("Remove Duplicates"):
                df = remove_duplicates(df)
                st.write("Removed duplicate rows.")
                if show_cleaned:
                    st.subheader("Cleaned Data")
                    st.dataframe(df, height=500)
        with st.sidebar.expander("Remove outdated data"):
            date_col = st.selectbox("Select date column:", df.columns)
            filter_type = st.radio("Filter type:", options=["All", "Time period"])
            if filter_type == "Time period":
                start_date = st.date_input("Select start date:")
                end_date = st.date_input("Select end date:")
                start_time = st.time_input("Select start time:")
                end_time = st.time_input("Select end time:")
                start_datetime = datetime.combine(start_date, start_time)
                end_datetime = datetime.combine(end_date, end_time)
                time_filter = [start_datetime, end_datetime]
            else:
                time_filter_options = ["Last 24 Hours", "Last 7 Days", "Last 30 Days"]
                time_filter = st.selectbox("Select time filter:", options=time_filter_options)
            if st.button("Remove Outdated Data"):
                df = remove_outdated(df, date_col, time_filter)
                st.write("Removed outdated rows.")
                if show_cleaned:
                    st.subheader("Cleaned Data")
                    st.dataframe(df, height=500)

        with st.sidebar.expander("Fill missing values"):
                col_to_fill = st.selectbox("Select column to check missing data:", df.columns)
                missing_data = df[col_to_fill].isnull().sum()
                st.write(f"Missing data in {col_to_fill} column:", missing_data)
                fill_method = st.selectbox("Select fill method:", ["Fill with Previous Value", "Fill with Next Value", "Fill with Mean", "Fill with Median", "Fill with Mode"])
                if fill_method == "Fill with Previous Value":
                    df[col_to_fill].fillna(method='pad', inplace=True)
                    st.write("Filled missing values using the previous value.")
                elif fill_method == "Fill with Next Value":
                    df[col_to_fill].fillna(method='bfill', inplace=True)
                    st.write("Filled missing values using the next value.")
                elif fill_method == "Fill with Mean":
                    df[col_to_fill].fillna(df[col_to_fill].mean(), inplace=True)
                    st.write("Filled missing values using the mean of the column.")
                elif fill_method == "Fill with Median":
                    df[col_to_fill].fillna(df[col_to_fill].median(), inplace=True)
                    st.write("Filled missing values using the median of the column.")
                elif fill_method == "Fill with Mode":
                    df[col_to_fill].fillna(df[col_to_fill].mode().iloc[0], inplace=True)
                    st.write("Filled missing values using the mode of the column.")

                if show_cleaned:
                    st.subheader("Cleaned Data")
                    st.dataframe(df, height=500)
                # Remove outliers using z-score
        with st.sidebar.expander("Remove Outliers using Z-score"):
            outlier_columns = st.multiselect("Select columns:", df.columns)
            outlier_threshold = st.number_input("Select Z-score threshold:", min_value=0.0, value=3.0)
            if st.button("Remove Outliers"):
                df = remove_outliers_zscore(df, outlier_columns, outlier_threshold)
                st.write("Removed outliers using Z-score")
                if show_cleaned:
                    st.subheader("Cleaned Data")
                    st.dataframe(df, height=500)  
        # Show cleaned data
        if show_cleaned:
            st.subheader("Cleaned Data")
            st.dataframe(df, height=500)
            # Download cleaned data as file
            file_format = uploaded_file.name.split(".")[-1]

            if file_format == 'csv':
                data = df.to_csv(index=False)
            else:
                wb = Workbook()
                ws = wb.active
                for r in dataframe_to_rows(df, index=False, header=True):
                    ws.append(r)
                data = openpyxl.writer.excel.save_virtual_workbook(wb)

            b64 = base64.b64encode(data).decode()
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="cleaned_data.{file_format}"><button>Download {file_format.upper()}</button></a>'
            st.markdown(href, unsafe_allow_html=True)
            # Clear history if user uploads a new file
            if uploaded_file != st.session_state.get('uploaded_file', None):
                st.session_state.uploaded_file = uploaded_file
                st.session_state.cleaned_data = []

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("Built by Vanh")
if __name__ == "__main__":
    main()