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
