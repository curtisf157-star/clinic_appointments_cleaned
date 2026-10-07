import pandas as pd
import sqlite3

CSV_PATH = r"C:\Users\curtis\Downloads\Clinic Appointments DataSet\cleaned_clinic_appointments.csv"
DB_PATH = r"C:\Users\curtis\Downloads\Clinic Appointments DataSet\clinic.db"

print("Reading cleaned CSV...")
df = pd.read_csv(CSV_PATH)
print(f"Rows: {len(df)}  Columns: {len(df.columns)}")

print("Writing to SQLite...")
conn = sqlite3.connect(DB_PATH)
df.to_sql("appointments", conn, if_exists="replace", index=False)
conn.close()

print(f"Done. Database saved to {DB_PATH}")
print("Table name: appointments")