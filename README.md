# Dirty Data Cleaner

This is a Streamlit app that allows users to upload CSV or XLSX files containing dirty data, and clean it using various options. The app provides the following functionalities:

- Uploading and inspecting original data
- Viewing column data types
- Showing unique values in columns
- Replacing text in a specific column
- Removing duplicate rows
- Removing outdated data based on date column and time filter
- Filling missing values using various methods
- Showing cleaned data
- Saving cleaned data as a CSV or XLSX file
- Viewing version history of cleaned data and downloading previous versions

# Requirements

To run this app, you will need:

- Python 3.7+
- streamlit
- pandas
- openpyxl

You can install these dependencies by running:
<code> pip install -r requirements.txt </code>

# How to use
Use can use on website: [cleandata.streamlit.app](https://cleandata.streamlit.app) or 
1. Clone this repository or download the files.
2. Install the requirements mentioned above.
3. Open your terminal/command prompt/Anaconda Prompt, navigate to the folder where you have downloaded/cloned the files and run:
<code> streamlit run app.py </code>

An app window will open in your browser where you can perform the desired cleaning operations.
Note: This app has been tested with CSV and XLSX files. If you encounter any issues with other file formats, please let the developer know.

# Required Imports:

- streamlit: The web application framework used to create the user interface.
- pandas: A powerful data manipulation library in Python.
- datetime and timedelta: Libraries for working with dates and times.
- base64: A library for encoding and decoding data in Base64 format.
- openpyxl: A library for reading and writing Excel files.
- numpy: A library for numerical computing.

# Data Cleaning Functions:
- remove_duplicates(df): Removes duplicate rows from a DataFrame.
- recommend_data_types(df): Recommends data types for each column in a DataFrame based on unique values.
- apply_data_type_recommendations(df, recommendations): Applies recommended data types to the columns in a DataFrame.
- remove_outdated(df, date_col, time_filter): Removes rows from a DataFrame based on a specified time range.
- replace_text_in_column(df, col_name, old_text, new_text): Replaces text in a specific column of a DataFrame.
- automated_data_cleaning(data): Performs automated data cleaning, including data type recognition and missing value imputation.
# Main Function:
- The main() function is the entry point of the Streamlit application.
- The application's title and introductory information are displayed.
- The application is divided into multiple steps, each with its own instructions.
- The user can upload a CSV or XLSX file and view the original data.
- Various data cleaning steps are available, including data type recommendations, changing data types, replacing text, removing duplicates, removing outdated data, and filling missing values.
- The cleaned data is displayed, and the user can download it as a CSV or XLSX file.

# Streamlit User Interface:
- The Streamlit sidebar is used to provide options for file uploading, section visibility, and data cleaning operations.
- The uploaded file is read into a DataFrame and displayed as the original data.
- User inputs and selections are used to perform data cleaning operations.
- The cleaned data is displayed, and a download link is provided for the user to download the cleaned data.
# Execution:
- The main() function is called at the end to run the Streamlit application.
