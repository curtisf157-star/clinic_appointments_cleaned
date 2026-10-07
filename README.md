# Messy Clinic Appointments — Data Cleaning with Pandas & SQL

A portfolio project that takes a deliberately messy healthcare appointments dataset and turns it into a clean, analysis-ready dataset using **Python (Pandas)** and **SQL (SQLite)**.

---

## Project Overview

The raw dataset simulates real-world clinic appointment records and is intentionally messy: mixed date formats, inconsistent gender values, multiple currencies, missing fields, and repeated patient IDs. The goal was to clean it end-to-end and then query the cleaned data with SQL.

**Workflow:**

```
messy_clinic_appointments.csv
        │
        ▼
   Raw.py  (Pandas cleaning)
        │
        ▼
cleaned_clinic_appointments.csv
        │
        ▼
 load_to_sqlite.py
        │
        ▼
     clinic.db  (SQLite)
        │
        ▼
  query_sqlite.py  (SQL queries)
```

---

## Dataset

- **Rows:** 1,000
- **Columns:** 13 raw → 27 cleaned
- **Fields:** patient ID, name, age, gender, appointment date, booking date, doctor, department, billing amount, follow-up required

### Types of messiness handled

| Issue | Examples | Fix |
|---|---|---|
| Mixed date formats | `2026/02/26`, `30-Nov-2025`, `August 05, 24`, `12-Jun-2024` | `dateutil.parser` |
| Inconsistent gender values | `M`, `Male`, `1`, `F`, `female`, `0` | Mapped to `Male` / `Female` / `Unknown` |
| Multi-currency billing | `£425.8`, `€344.26`, `$84.44`, `Rs85.76` | Split into `billing_currency` + `billing_amount_clean` |
| Follow-up variants | `1`, `Y`, `Yes`, `0`, `N`, `No` | Mapped to boolean |
| Missing values | empty strings, `NaN` | Flagged, not silently dropped |
| Repeated patient IDs | same ID, different names | Preserved and flagged — ID is not a unique key |
| Doctor titles | `Dr.`, `MD`, `DDS`, `DVM` | Stripped to clean names |

---

## Tech Stack

- **Python 3.13**
- **Pandas** — data loading and cleaning
- **NumPy** — numeric handling
- **python-dateutil** — flexible date parsing
- **SQLite** — lightweight database for SQL queries

---

## Project Structure

```
clinic-appointments-cleaning/
├── messy_clinic_appointments.csv       # raw input
├── Raw.py                              # Pandas cleaning script
├── cleaned_clinic_appointments.csv     # cleaned output
├── load_to_sqlite.py                   # loads cleaned CSV into SQLite
├── clinic.db                           # SQLite database
├── query_sqlite.py                     # SQL queries against cleaned data
└── README.md
```

---

## Cleaning Steps (Raw.py)

1. Load raw CSV with all columns as strings
2. Normalize column names (`lower_snake_case`)
3. Strip whitespace from text columns
4. Cast `patient_id` to nullable integer, add `appointment_id`
5. Clean `patient_name` (title case, collapse spaces)
6. Validate `age` (drop values outside 0–120)
7. Map `gender` to `Male` / `Female` / `Unknown`
8. Parse `appointment_date` and `booking_date` with mixed-format parser
9. Compute `booking_lead_days` and flag negative leads
10. Extract `billing_currency` and `billing_amount_clean`
11. Standardize `follow_up_required` to boolean
12. Clean `department` and `doctor` names
13. Drop exact duplicates, flag composite duplicates
14. Add features: appointment year/month/weekday, age group
15. Save to `cleaned_clinic_appointments.csv`

---

## SQL Layer

The cleaned CSV is loaded into a SQLite table called `appointments`, then queried with SQL.

**Example query — appointments per department:**

```sql
SELECT
  department_clean,
  COUNT(*) AS total_appointments,
  ROUND(AVG(billing_amount_clean), 2) AS avg_billing
FROM appointments
WHERE billing_amount_clean IS NOT NULL
GROUP BY department_clean
ORDER BY total_appointments DESC;
```

**Result:**

| department_clean | total_appointments | avg_billing |
|---|---|---|
| Neurology | 259 | 275.16 |
| Orthopedics | 248 | 279.08 |
| Cardiology | 224 | 259.09 |
| General | 219 | 291.31 |

---

## Key Assumptions

- Slash dates like `05/23/2025` are treated as **US format** (`MM/DD/YYYY`)
- `Rs` is treated as **INR**
- `1` / `0` in gender map to `Male` / `Female`
- `patient_id` is **not unique** — repeated IDs are kept and flagged
- Rows with missing critical dates are **flagged**, not deleted

---

## What This Project Demonstrates

- Handling messy, real-world data with Pandas
- Robust mixed-format date parsing
- Multi-currency extraction with regex
- Category standardization and boolean coercion
- Feature engineering from dates and age
- Data quality validation and flagging (instead of hiding bad rows)
- Loading cleaned data into SQLite and writing SQL queries
- End-to-end workflow: raw → cleaned → queried

---

## How to Run

### 1. Install dependencies

```bash
pip install pandas numpy python-dateutil
```

### 2. Clean the data

```bash
python Raw.py
```

Outputs `cleaned_clinic_appointments.csv`.

### 3. Load into SQLite

```bash
python load_to_sqlite.py
```

Creates `clinic.db` with table `appointments`.

### 4. Run SQL queries

```bash
python query_sqlite.py
```

Prints department-level summary from SQLite.

---

## Possible Next Steps

- Add Power BI / Tableau dashboard on top of the cleaned dataset
- Build an appointment trends analysis (monthly, by department)
- Compare follow-up rates across departments
- Convert billing amounts to a single currency using documented exchange rates
- Add unit tests for the cleaning functions

---

## Author

**Curtis**  
Data cleaning and SQL portfolio project.

Feel free to fork, reuse, or adapt.