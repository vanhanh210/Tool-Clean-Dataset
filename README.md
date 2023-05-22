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
# How can i auto fill missing values? 

The code snippet you provided defines a function called automated_data_cleaning that performs automated data cleaning operations on a given dataset. Here's an explanation of each step in the code:
1. cleaned_data = data.copy(): This line creates a copy of the original dataset (data) to avoid modifying the original data. The cleaning operations will be performed on this copied dataset.
2. data_types = cleaned_data.dtypes: This line retrieves the data types of each column in the cleaned_data dataset. It uses the dtypes attribute of a DataFrame to obtain the data types.
3. numeric_cols = data_types[data_types.apply(lambda x: pd.api.types.is_numeric_dtype(x))].index: This line identifies the columns with numeric data types by applying a lambda function to each data type in the data_types series. The lambda function checks if a data type is numeric using pd.api.types.is_numeric_dtype(). The resulting boolean series is used to filter the column indices, and the .index attribute returns the column names.
4. categorical_cols = data_types[data_types.apply(lambda x: pd.api.types.is_categorical_dtype(x))].index: This line identifies the columns with categorical data types by applying a similar lambda function. It checks if a data type is categorical using pd.api.types.is_categorical_dtype(). The resulting boolean series is used to filter the column indices, and the .index attribute returns the column names.
5. datetime_cols = data_types[data_types.apply(lambda x: pd.api.types.is_datetime64_dtype(x))].index: This line identifies the columns with datetime data types using a lambda function. It checks if a data type is datetime using pd.api.types.is_datetime64_dtype(). The resulting boolean series is used to filter the column indices, and the .index attribute returns the column names.
6. The code then proceeds to perform missing value imputation based on the identified column types:
For each column (col) in the cleaned_data dataset:
- It checks if the column has any missing values using cleaned_data[col].isnull().any().
- If the column is numeric (col in numeric_cols), it fills the missing values with the mean value of the column if it is an integer data type, or with the median value if it is not (cleaned_data[col].fillna(cleaned_data[col].mean(), inplace=True) or cleaned_data[col].fillna(cleaned_data[col].median(), inplace=True)).
- If the column is categorical (col in categorical_cols), it fills the missing values with the most frequent value in the column (cleaned_data[col].fillna(cleaned_data[col].mode()[0], inplace=True)).
- If the column is a datetime column (col in datetime_cols), it fills the missing values using forward fill (cleaned_data[col].fillna(method='ffill', inplace=True)).
- If the column does not fall into any of the above categories, it fills the missing values with the next available value in the column (cleaned_data[col] = cleaned_data[col].fillna(method='bfill')).
7. Finally, the function returns the cleaned_data dataset, which now contains the original dataset with missing values imputed and no modifications to the original data.

This function provides a simple automated approach to clean data by handling missing values based on their data types.
