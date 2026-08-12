from dotenv import load_dotenv
load_dotenv()   # works for local development

import os
import json
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st


def get_config(name: str) -> str:
    """
    Try to read a value from Streamlit secrets (Cloud),
    fall back to environment variables (.env / system).
    """
    try:
        return st.secrets[name]
    except Exception:
        return os.environ[name]


def get_credentials():
    # On Streamlit Cloud this will read from st.secrets,
    # locally it can read from .env
    cred_input = get_config("GOOGLE_CREDENTIALS_JSON")
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    # If the value is a path to a file, load file; otherwise treat as JSON string
    if os.path.isfile(cred_input):
        with open(cred_input) as f:
            info = json.load(f)
    else:
        info = json.loads(cred_input)

    return Credentials.from_service_account_info(info, scopes=scopes)


def create_client():
    creds = get_credentials()
    return gspread.authorize(creds)


gc = create_client()
SPREADSHEET_ID = get_config("SPREADSHEET_ID")
sh = gc.open_by_key(SPREADSHEET_ID)


def get_sheet_data(sheet_name: str):
    sheet = sh.worksheet(sheet_name)
    values = sheet.get_all_values()
    header, rows = values[0], values[1:]
    return pd.DataFrame(rows, columns=header)


def set_sheet_data(sheet_name: str, df: pd.DataFrame):
    worksheet = sh.worksheet(sheet_name)
    worksheet.clear()
    set_with_dataframe(worksheet, df, include_index=False, include_column_header=True)


def append_sheet_data(sheet_name: str, data: list):
    worksheet = sh.worksheet(sheet_name)
    worksheet.append_rows(data, value_input_option='USER_ENTERED')
