import gspread
import pandas as pd
from google.oauth2.service_account import Credentials



SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def connect():

    creds = Credentials.from_service_account_file(
        "raich-fitness-challenge-4643fe25f371.json",
        scopes=SCOPE
    )

    client = gspread.authorize(creds)

    sheet = client.open(
        "Raich Family Fitness Challenge Data"
    ).sheet1

    return sheet



def load_sheet():

    sheet = connect()

    data = sheet.get_all_records()

    columns = [
        "Date",
        "Person",
        "Type",
        "Amount",
        "Week"
    ]

    if len(data) == 0:
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame(data)

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    return df


def save_sheet(df):

    sheet = connect()

    sheet.clear()

    sheet.update(
        [
            df.columns.tolist()
        ]
        +
        df.astype(str).values.tolist()
    )