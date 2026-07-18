# SQX Runs Logger — Data Cleaning & System Specification
**Project:** SQX Runs Logger — Streamlit Dashboard App  
**Version:** 1.4 | **Date:** 29-Apr-2026  

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 27-Apr-2026 | Initial specification |
| 1.1 | 27-Apr-2026 | Revised duplicate ID rule; Finals aggregation rule; version history added |
| 1.2 | 27-Apr-2026 | CSV analysis findings: LS direction, M15/H timeframes, ID normalisation, time field, template field |
| 1.3 | 27-Apr-2026 | Value-based parser adopted; LS and M15 confirmed valid; Q5 ID normalisation confirmed |
| 1.4 | 27-Apr-2026 | All open questions resolved; data corrections logged; deployment details added |

---

## 1. Overview

SQX Runs Logger is a private Streamlit web application for logging, tracking and analysing StrategyQuant strategy generation runs across Forex pairs and commodities.

**Technology stack:**
- Python 3.8+ / Streamlit
- SQLite database (sqlog.db)
- Deployed on Oracle Cloud Free Tier VPS (Ubuntu 20.04)
- URL: http://141.147.72.114:8501

**Source files:**

| File | Purpose |
|------|---------|
| app.py | Main Streamlit application — all pages and UI |
| db.py | Database operations — CRUD, queries, soft delete |
| db_lookup.py | Asset lookup table — stored in SQLite, manageable via UI |
| cleaner.py | ID parser and data cleaning engine |
| requirements.txt | Python dependencies |
| sqlog.db | SQLite database file |

---

## 2. Asset Lookup Table

Maps ID stems to standardised asset names. Stored in the SQLite `asset_lookup` table and manageable via the Asset Lookup page in the app.

| ID_Stem | Asset | ID_Stem | Asset |
|---------|-------|---------|-------|
| AU | AUDUSD | NDX | NDX |
| DAX | DAX | NI225 | NI225 |
| DJ | WS30 | NU | NZDUSD |
| EG | EURGBP | NZDUSD | NZDUSD |
| EJ | EURJPY | SP | SP500 |
| EU | EURUSD | UC | USDCHF |
| EURGBP | EURGBP | UJ | USDJPY |
| G | XAUUSD | USDCHF | USDCHF |
| GA | GBPAUD | | |
| GDAX | DAX | | |
| GJ | GBPJPY | | |
| GU | GBPUSD | | |

New mappings can be added via the Asset Lookup page without code changes.

---

## 3. ID Field Decoding Rules

### 3.1 Format

```
<Asset_Stem> <delimiter> <Direction> <delimiter> <Timeframe> [optional trailing characters]
```

**IMPORTANT:** Direction and Timeframe tokens may be **transposed**. The parser detects each token **by its value**, not by position.

### 3.2 Delimiters

Hyphen `-` or Underscore `_`. Mixed delimiters in the same ID are supported.

### 3.3 ID Normalisation

For multi-run detection, a normalised form is derived:
- Convert to uppercase
- Replace `-` with `_`
- Strip trailing non-alphanumeric characters

`G-L-H1`, `G_L_H1`, and `G_L_H1_` all normalise to `G_L_H1`.

### 3.4 Component 1 — Asset Stem

Always the **first token**. Looked up in the asset_lookup table (case-insensitive). Not found → `Asset = "UNKNOWN"`, `parse_warning = True`.

### 3.5 Component 2 — Direction *(detected by value)*

| Code | Stored As | Meaning |
|------|-----------|---------|
| L | Long | Long only |
| S | Short | Short only |
| LS | LS | Both Long and Short capability |

### 3.6 Component 3 — Timeframe *(detected by value)*

| Code | Meaning |
|------|---------|
| M15 | 15 Minutes |
| M30 | 30 Minutes |
| H1 | 1 Hour |
| H2 | 2 Hours |
| H4 | 4 Hours |

Bare `H` alone is NOT valid.

---

## 4. Parsing Algorithm

```python
VALID_DIRECTIONS = {"L", "S", "LS"}
VALID_TIMEFRAMES = {"M15", "M30", "H1", "H2", "H4"}
DIRECTION_MAP    = {"L": "Long", "S": "Short", "LS": "LS"}

1. Strip whitespace from ID
2. tokens = re.split(r'[-_]', ID.strip()) — remove empty strings
3. Asset Stem = tokens[0] — look up in asset_lookup (case-insensitive)
4. For each token in tokens[1:]:
     clean = re.sub(r'[^A-Z0-9]', '', token.upper())
     if clean in VALID_DIRECTIONS: direction_token = clean
     elif clean in VALID_TIMEFRAMES: timeframe_token = clean
5. Direction = DIRECTION_MAP[direction_token] or "UNKNOWN"
6. Timeframe = timeframe_token (uppercase) or "UNKNOWN"
7. normalised_id = re.sub(r'[^A-Z0-9_]', '', ID.upper().replace('-','_')).rstrip('_')
8. date: parse DD/MM/YYYY → store as YYYY-MM-DD
```

---

## 5. Error Handling & Flagging

A `parse_warning` boolean column (True/False) flags any row with decode issues.

| Condition | Action |
|-----------|--------|
| Asset stem not in lookup table | Asset = "UNKNOWN", parse_warning = True |
| No direction token found | Direction = "UNKNOWN", parse_warning = True |
| No timeframe token found | Timeframe = "UNKNOWN", parse_warning = True |
| Fewer than 2 tokens after stem | Affected fields = "UNKNOWN", parse_warning = True |
| ID empty or null | All fields = "UNKNOWN", parse_warning = True |
| Invalid date format | Row rejected, error shown to user |

Flagged rows are **retained** in the database and visible in the Data Quality page.

---

## 6. Duplicate & Multi-Run Rules

### 6.1 True Duplicate
Same **raw ID** AND same **Date** → rejected on import, error shown to user.

### 6.2 Multi-Run
Same **normalised ID** but different **Date** → retained as a separate record.

### 6.3 Composite Primary Key
Database primary key = `(id, date)`. `normalised_id` stored separately for grouping.

### 6.4 Finals Aggregation in Reports

| Report View | Finals Treatment |
|-------------|-----------------|
| Individual run detail | Finals per run |
| Summary by normalised ID | SUM of Finals |
| Summary by Asset | SUM of Finals |
| Summary by Timeframe | SUM of Finals |
| Summary by Direction | SUM of Finals |
| Total KPI card | SUM of all Finals |

---

## 7. Database Schema

### Table: runs

| Column | Type | Notes |
|--------|------|-------|
| id | TEXT NOT NULL | Raw ID, preserved unchanged |
| normalised_id | TEXT NOT NULL | Generated for grouping |
| asset | TEXT | From lookup table |
| direction | TEXT | Long / Short / LS |
| timeframe | TEXT | M15 / M30 / H1 / H2 / H4 |
| date | TEXT NOT NULL | Stored as YYYY-MM-DD |
| finals | INTEGER | Nullable |
| time | TEXT | Raw duration string |
| duration_minutes | INTEGER | Parsed from time, nullable |
| loops | INTEGER | Nullable |
| note2 | TEXT | Nullable |
| note | TEXT | Nullable |
| template | TEXT | e.g. v3.2, v4. Nullable |
| parse_warning | INTEGER | 0 or 1 |
| deleted | INTEGER | 0 = active, 1 = soft-deleted |

**Primary Key:** (id, date)

### Table: asset_lookup

| Column | Type | Notes |
|--------|------|-------|
| stem | TEXT PRIMARY KEY | Uppercase ID stem |
| asset | TEXT NOT NULL | Standardised asset name |

---

## 8. Soft Delete

Records are never permanently deleted. The `deleted` column controls visibility:

- `deleted = 0` — active record, visible in all views and reports
- `deleted = 1` — soft-deleted, hidden from all views and reports

Soft-deleted records can be restored at any time via the Edit / Delete page.

---

## 9. Time Field Parsing

The `time` field is stored raw. `duration_minutes` is derived for sorting.

| Pattern | Example | Minutes |
|---------|---------|---------|
| XH | 24H | 1440 |
| XhYm | 9h51 | 591 |
| XD | 1D | 1440 |
| XDY | 1D9 | 1980 |
| XdYh | 8d3h | 11700 |

Rules (case-insensitive): D = days, H = hours, M = minutes. Unparseable → duration_minutes = NULL.

---

## 10. Coverage Matrix Logic

The Coverage Matrix shows finals by asset × timeframe × direction.

- LS direction is **excluded** — only Long and Short are shown
- Rows = all distinct assets in the database, sorted alphabetically
- Columns = M15-Long, M15-Short, M30-Long, M30-Short, H1-Long, H1-Short, H2-Long, H2-Short, H4-Long, H4-Short
- Cell value = SUM of finals for that combination across all runs
- Cell colour:
  - Dark green (#1D9E75) = 50+ finals
  - Medium green (#5DCAA5) = 20–49 finals
  - Light green (#9FE1CB) = 1–19 finals
  - Pink (#FFE4E4) = 0 or no data (gap)

---

## 11. Data Corrections Log

Errors identified in source CSV, corrected by user on 27-Apr-2026.

| Original ID | Corrected ID | Date | Finals (orig) | Finals (corrected) | Issue |
|-------------|-------------|------|---------------|--------------------|-------|
| EU_S_H | EU_S_H1 | 15/03/2026 | 135 | 35 | Timeframe H corrected to H1; finals 135 corrected to 35 |
| EU-L | EU-L_H1 | 20/02/2026 | 2 | 2 | Missing timeframe added as H1; finals unchanged |

---

## 12. Deployment

| Item | Detail |
|------|--------|
| Server | Oracle Cloud Free Tier VPS |
| OS | Ubuntu 20.04 LTS |
| IP | 141.147.72.114 |
| Port | 8501 |
| URL | http://141.147.72.114:8501 |
| Username | ubuntu |
| App path | /home/ubuntu/sqxlogger/ |
| Service | systemd service: sqxlogger |
| Python | 3.8 (venv at ~/sqxlogger/venv) |

**Service commands:**
```bash
sudo systemctl start sqxlogger
sudo systemctl stop sqxlogger
sudo systemctl restart sqxlogger
sudo systemctl status sqxlogger
```

**Update app files from Mac:**
```bash
scp -i ~/path/to/key.pem app.py ubuntu@141.147.72.114:~/sqxlogger/
sudo systemctl restart sqxlogger
```

---

*Specification frozen at v1.4. All open questions resolved.*
