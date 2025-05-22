
import os
import pandas as pd

EXCEL_PATH = "data/uploaded_excels/latest.xlsx"

def save_uploaded_file(uploaded_file):
    os.makedirs(os.path.dirname(EXCEL_PATH), exist_ok=True)
    with open(EXCEL_PATH, "wb") as f:
        f.write(uploaded_file.getbuffer())

def load_excel_sheets():
    return pd.ExcelFile(EXCEL_PATH)

def get_df_from_sheet(sheet_name):
    return pd.read_excel(EXCEL_PATH, sheet_name=sheet_name)
