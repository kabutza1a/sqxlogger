"""
db_lookup.py
Asset lookup table stored in SQLite.
Replaces hardcoded ASSET_MAP in cleaner.py.
"""
import sqlite3, os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "sqlog.db")

SEED_DATA = [
    ("AU",     "AUDUSD"),
    ("DAX",    "DAX"),
    ("DJ",     "WS30"),
    ("EG",     "EURGBP"),
    ("EJ",     "EURJPY"),
    ("EU",     "EURUSD"),
    ("EURGBP", "EURGBP"),
    ("G",      "XAUUSD"),
    ("GA",     "GBPAUD"),
    ("GDAX",   "DAX"),
    ("GJ",     "GBPJPY"),
    ("GU",     "GBPUSD"),
    ("NDX",    "NDX"),
    ("NI225",  "NI225"),
    ("NU",     "NZDUSD"),
    ("NZDUSD", "NZDUSD"),
    ("SP",     "SP500"),
    ("UC",     "USDCHF"),
    ("UJ",     "USDJPY"),
    ("USDCHF", "USDCHF"),
]

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_lookup():
    """Create asset_lookup table and seed with default mappings."""
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS asset_lookup (
            stem  TEXT PRIMARY KEY,
            asset TEXT NOT NULL
        )
    """)
    # Seed only if empty
    count = conn.execute("SELECT COUNT(*) FROM asset_lookup").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT OR IGNORE INTO asset_lookup (stem, asset) VALUES (?, ?)",
            SEED_DATA
        )
    conn.commit()
    conn.close()

def get_lookup_map() -> dict:
    """Return full lookup as uppercase-keyed dict."""
    conn = get_conn()
    rows = conn.execute("SELECT stem, asset FROM asset_lookup").fetchall()
    conn.close()
    return {r["stem"].upper(): r["asset"] for r in rows}

def get_lookup_df() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql(
        "SELECT stem, asset FROM asset_lookup ORDER BY stem", conn
    )
    conn.close()
    return df

def add_mapping(stem: str, asset: str) -> tuple[bool, str]:
    stem  = stem.strip().upper()
    asset = asset.strip().upper()
    if not stem or not asset:
        return False, "Stem and asset cannot be empty."
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO asset_lookup (stem, asset) VALUES (?, ?)",
            (stem, asset)
        )
        conn.commit()
        return True, f"Added: {stem} → {asset}"
    except sqlite3.IntegrityError:
        return False, f"Stem '{stem}' already exists. Use Update to change it."
    finally:
        conn.close()

def update_mapping(stem: str, new_asset: str) -> tuple[bool, str]:
    stem      = stem.strip().upper()
    new_asset = new_asset.strip().upper()
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE asset_lookup SET asset=? WHERE stem=?",
            (new_asset, stem)
        )
        conn.commit()
        return True, f"Updated: {stem} → {new_asset}"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def delete_mapping(stem: str) -> tuple[bool, str]:
    stem = stem.strip().upper()
    conn = get_conn()
    try:
        conn.execute("DELETE FROM asset_lookup WHERE stem=?", (stem,))
        conn.commit()
        return True, f"Deleted mapping for stem '{stem}'."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def reparse_unknowns() -> tuple[int, int]:
    """
    Re-parse all runs where asset='UNKNOWN' using the current lookup table.
    Returns (fixed_count, still_unknown_count).
    """
    import cleaner
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, date FROM runs WHERE asset='UNKNOWN'"
    ).fetchall()
    fixed = 0
    still_unknown = 0
    for row in rows:
        parsed = cleaner.parse_id(row["id"])
        if parsed["asset"] != "UNKNOWN":
            conn.execute("""
                UPDATE runs SET
                    asset=?, direction=?, timeframe=?,
                    normalised_id=?, parse_warning=?
                WHERE id=? AND date=?
            """, (
                parsed["asset"], parsed["direction"], parsed["timeframe"],
                cleaner.normalise_id(row["id"]),
                int(parsed["parse_warning"]),
                row["id"], row["date"]
            ))
            fixed += 1
        else:
            still_unknown += 1
    conn.commit()
    conn.close()
    return fixed, still_unknown
