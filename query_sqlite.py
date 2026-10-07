import sqlite3
import pandas as pd

DB_PATH = r"C:\Users\curtis\Downloads\Clinic Appointments DataSet\clinic.db"

conn = sqlite3.connect(DB_PATH)

query = """
SELECT
  department_clean,
  COUNT(*) AS total_appointments,
  ROUND(AVG(billing_amount_clean), 2) AS avg_billing
FROM appointments
WHERE billing_amount_clean IS NOT NULL
GROUP BY department_clean
ORDER BY total_appointments DESC;
"""

result = pd.read_sql(query, conn)
print(result)

conn.close()