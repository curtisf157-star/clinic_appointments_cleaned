import re
import numpy as np
import pandas as pd
from dateutil import parser

RAW_PATH = r"C:\Users\curtis\Downloads\Clinic Appointments DataSet\messy_clinic_appointments.csv"
CLEAN_PATH = r"C:\Users\curtis\Downloads\Clinic Appointments DataSet\cleaned_clinic_appointments.csv"
def parse_mixed_date(x):
    if pd.isna(x):
        return pd.NaT
    s = str(x).strip()
    if s == "":
        return pd.NaT
    try:
        return parser.parse(s, dayfirst=False)
    except Exception:
        return pd.NaT


def extract_billing(x):
    if pd.isna(x):
        return pd.Series([np.nan, np.nan])

    s = str(x).strip()
    if s == "":
        return pd.Series([np.nan, np.nan])

    m = re.search(r"([£€$]|Rs)\s*([0-9,]+(?:\.[0-9]+)?)", s, flags=re.I)

    if not m:
        m2 = re.search(r"([0-9,]+(?:\.[0-9]+)?)", s)
        if m2:
            return pd.Series([np.nan, float(m2.group(1).replace(",", ""))])
        return pd.Series([np.nan, np.nan])

    symbol, amount = m.group(1), m.group(2)
    currency_map = {"£": "GBP", "€": "EUR", "$": "USD", "Rs": "INR"}

    return pd.Series([
        currency_map.get(symbol, symbol),
        float(amount.replace(",", ""))
    ])


def clean_follow_up(x):
    if pd.isna(x):
        return pd.NA

    s = str(x).strip().lower()

    if s in ["1", "y", "yes", "true"]:
        return True
    if s in ["0", "n", "no", "false"]:
        return False

    return pd.NA


def main():
    # 1. Load raw data
    df = pd.read_csv(RAW_PATH, dtype=str)

    # 2. Clean column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # 3. Strip text columns
    for col in df.select_dtypes(include=["object", "str"]):
        df[col] = df[col].str.strip()

    # 4. IDs
    df["patient_id"] = pd.to_numeric(df["patient_id"], errors="coerce").astype("Int64")
    df["appointment_id"] = range(1, len(df) + 1)

    # 5. Names
    df["patient_name_clean"] = (
        df["patient_name"]
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )

    # 6. Age
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df.loc[(df["age"] < 0) | (df["age"] > 120), "age"] = np.nan

    # 7. Gender
    gender_map = {
        "m": "Male", "male": "Male", "1": "Male",
        "f": "Female", "female": "Female", "0": "Female"
    }
    df["gender_clean"] = (
        df["gender"]
        .str.lower()
        .str.strip()
        .map(gender_map)
        .fillna("Unknown")
    )

    # 8. Dates
    df["appointment_date_clean"] = df["appointment_date"].apply(parse_mixed_date)
    df["booking_date_clean"] = df["booking_date"].apply(parse_mixed_date)

    df["booking_lead_days"] = (
        df["appointment_date_clean"] - df["booking_date_clean"]
    ).dt.days
    df["negative_lead"] = df["booking_lead_days"] < 0

    # 9. Billing
    df[["billing_currency", "billing_amount_clean"]] = (
        df["billing_amount"].apply(extract_billing)
    )

    # 10. Follow-up
    df["follow_up_required_clean"] = (
        df["follow_up_required"]
        .apply(clean_follow_up)
        .astype("boolean")
    )

    # 11. Department and doctor
    df["department_clean"] = df["department"].str.title()

    df["doctor_clean"] = (
        df["doctor"]
        .str.replace(r"\b(Dr\.|MD|DDS|DVM|Mr\.|Mrs\.|Miss|Ms\.)\b", "", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # 12. Duplicates
    df = df.drop_duplicates()

    key = [
        "patient_id",
        "patient_name_clean",
        "appointment_date_clean",
        "doctor_clean"
    ]
    df["is_duplicate_appointment"] = df.duplicated(key, keep=False)

    # 13. Extra columns
    df["appointment_year"] = df["appointment_date_clean"].dt.year
    df["appointment_month"] = df["appointment_date_clean"].dt.month
    df["appointment_weekday"] = df["appointment_date_clean"].dt.day_name()

    df["age_group"] = pd.cut(
        df["age"],
        bins=[0, 17, 30, 45, 60, 75, 120],
        labels=["0-17", "18-30", "31-45", "46-60", "61-75", "76+"]
    )

    # 14. Save
    df.to_csv(CLEAN_PATH, index=False)
    print(f"Saved cleaned data to {CLEAN_PATH}")
    print(df.head())


if __name__ == "__main__":
    main()