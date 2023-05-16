import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import base64
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook

def remove_duplicates(df):
    return df.drop_duplicates()

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
    # Ask user which method to use to fill missing values
    fill_method = st.radio("Select a method to fill missing values:", 
                           options=["Fill with Previous Value", "Fill with Next Value",
                                    "Fill with Mean", "Fill with Median", "Fill with Mode",
                                    "Interpolate"])
    
    if fill_method == "Fill with Previous Value":
        df.fillna(method='pad', inplace=True)
        st.write("Filled missing values using previous value.")
    elif fill_method == "Fill with Next Value":
        df.fillna(method='bfill', inplace=True)
        st.write("Filled missing values using next value.")
    elif fill_method == "Fill with Mean":
        df.fillna(df.mean(), inplace=True)
        st.write("Filled missing values using mean of column.")
    elif fill_method == "Fill with Median":
        df.fillna(df.median(), inplace=True)
        st.write("Filled missing values using median of column.")
    elif fill_method == "Fill with Mode":
        df.fillna(df.mode().iloc[0], inplace=True)
        st.write("Filled missing values using mode of column.")
    elif fill_method == "Interpolate":
        df.interpolate(inplace=True)
        st.write("Filled missing values using interpolation.")
        
    return df

def add_data_summary_column(df):
    df['data_summary'] = df.apply(lambda x: ', '.join([f"{col}: {x[col]}" for col in df.columns]), axis=1)
    return df
    
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
        st.sidebar.title("Data Inspection Options")
        with st.sidebar.expander("View column data types"):
            st.write(df.dtypes)
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
            df_copy = df.copy()
            df = fill_missing_values(df_copy)
            if show_cleaned:
                st.subheader("Cleaned Data")
                st.dataframe(df, height=500)

        # Show cleaned data
        if show_cleaned:
            st.subheader("Cleaned Data")
            st.dataframe(df, height=500)

        # Save the cleaned dataframe in history
        if 'cleaned_data' not in st.session_state:
            st.session_state.cleaned_data = []
            
        current_time = datetime.now()
        df = add_data_summary_column(df)
        df['datetime'] = current_time
        st.session_state.cleaned_data.append(df.copy())

        if len(st.session_state.cleaned_data) > 1 and show_history:
            # Display version edit history
            st.subheader("Version History")
            for i, version in enumerate(st.session_state.cleaned_data[:-1]):
                version_num = i + 1
                st.write(f"Version {version_num} - {version['datetime'].dt.strftime('%m/%d/%Y %I:%M %p').iloc[0]}")
                st.write(version[['data_summary']])
                # Download button for each version
                file_format = uploaded_file.name.split(".")[-1]
                if file_format == 'csv':
                    data = version.to_csv(index=False)
                else:
                    wb = Workbook()
                    ws = wb.active
                    for r in dataframe_to_rows(version, index=False, header=True):
                        ws.append(r)
                    data = openpyxl.writer.excel.save_virtual_workbook(wb)

                b64 = base64.b64encode(data).decode()
                href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="cleaned_data_v{version_num}.{file_format}"><button>Download Version {version_num}</button></a>'
                st.markdown(href, unsafe_allow_html=True)
                
                st.write("")

            st.write(f"Current Version - {current_time.strftime('%m/%d/%Y %I:%M %p')}")
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
if __name__ == "__main__":
    main()        