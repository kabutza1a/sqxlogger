"""
db.py - SQLite database operations. Supports soft delete via deleted column.
"""

import os
import sqlite3

import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "sqlog.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id TEXT NOT NULL, normalised_id TEXT NOT NULL,
            asset TEXT, direction TEXT, timeframe TEXT,
            date TEXT NOT NULL, finals INTEGER, time TEXT,
            duration_minutes INTEGER, loops INTEGER,
            note2 TEXT, note TEXT, template TEXT,
            parse_warning INTEGER DEFAULT 0,
            deleted INTEGER DEFAULT 0,
            PRIMARY KEY (id, date)
        )
    """)
    # Migrate existing DB - add deleted column if missing
    cols = [r[1] for r in conn.execute("PRAGMA table_info(runs)").fetchall()]
    if "deleted" not in cols:
        conn.execute("ALTER TABLE runs ADD COLUMN deleted INTEGER DEFAULT 0")
    conn.commit()
    conn.close()


def insert_run(row: dict) -> tuple[bool, str]:
    conn = get_conn()
    try:
        conn.execute(
            """
            INSERT INTO runs (id,normalised_id,asset,direction,timeframe,date,
                finals,time,duration_minutes,loops,note2,note,template,parse_warning,deleted)
            VALUES (:id,:normalised_id,:asset,:direction,:timeframe,:date,
                :finals,:time,:duration_minutes,:loops,:note2,:note,:template,:parse_warning,0)
        """,
            {**row, "parse_warning": int(row.get("parse_warning", False))},
        )
        conn.commit()
        return True, "OK"
    except sqlite3.IntegrityError:
        return (
            False,
            f"Duplicate: ID '{row['id']}' already exists for date {row['date']}",
        )
    finally:
        conn.close()


def get_all_runs(include_deleted: bool = False) -> pd.DataFrame:
    conn = get_conn()
    where = "" if include_deleted else "WHERE deleted = 0"
    df = pd.read_sql(
        f"SELECT * FROM runs {where} ORDER BY asset, direction, timeframe, date", conn
    )
    conn.close()
    return df


def get_run_by_id_date(raw_id: str, date_str: str):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM runs WHERE id = ? AND date = ?", (raw_id, date_str)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_run(raw_id: str, date_str: str, fields: dict) -> tuple[bool, str]:
    import cleaner

    conn = get_conn()
    try:
        new_id = fields.get("id", raw_id).strip()
        new_date = fields.get("date", date_str)
        parsed = cleaner.parse_id(new_id)
        norm_id = cleaner.normalise_id(new_id)
        duration = cleaner.parse_duration_minutes(fields.get("time", "") or "")
        conn.execute(
            """
            UPDATE runs SET
                id=?,normalised_id=?,asset=?,direction=?,timeframe=?,date=?,
                finals=?,time=?,duration_minutes=?,loops=?,
                note=?,note2=?,template=?,parse_warning=?
            WHERE id=? AND date=?
        """,
            (
                new_id,
                norm_id,
                parsed["asset"],
                parsed["direction"],
                parsed["timeframe"],
                new_date,
                fields.get("finals"),
                fields.get("time") or None,
                duration,
                fields.get("loops") or None,
                fields.get("note") or None,
                fields.get("note2") or None,
                fields.get("template") or None,
                int(parsed["parse_warning"]),
                raw_id,
                date_str,
            ),
        )
        conn.commit()
        return True, "Record updated successfully."
    except sqlite3.IntegrityError:
        return False, f"ID + date combination already exists."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def soft_delete_run(raw_id: str, date_str: str) -> tuple[bool, str]:
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE runs SET deleted=1 WHERE id=? AND date=?", (raw_id, date_str)
        )
        conn.commit()
        return True, "Record deleted."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def restore_run(raw_id: str, date_str: str) -> tuple[bool, str]:
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE runs SET deleted=0 WHERE id=? AND date=?", (raw_id, date_str)
        )
        conn.commit()
        return True, "Record restored."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def get_run_count() -> int:
    conn = get_conn()
    n = conn.execute("SELECT COUNT(*) FROM runs WHERE deleted=0").fetchone()[0]
    conn.close()
    return n


def get_total_finals() -> int:
    conn = get_conn()
    n = conn.execute(
        "SELECT COALESCE(SUM(finals),0) FROM runs WHERE deleted=0"
    ).fetchone()[0]
    conn.close()
    return n


def get_unique_assets() -> int:
    conn = get_conn()
    n = conn.execute(
        "SELECT COUNT(DISTINCT asset) FROM runs WHERE asset!='UNKNOWN' AND deleted=0"
    ).fetchone()[0]
    conn.close()
    return n


def get_parse_warning_count() -> int:
    conn = get_conn()
    n = conn.execute(
        "SELECT COUNT(*) FROM runs WHERE parse_warning=1 AND deleted=0"
    ).fetchone()[0]
    conn.close()
    return n


def get_finals_by_asset() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql(
        """
        SELECT asset, COUNT(*) AS total_runs, SUM(finals) AS total_finals
        FROM runs WHERE asset!='UNKNOWN' AND deleted=0
        GROUP BY asset ORDER BY total_finals DESC
    """,
        conn,
    )
    conn.close()
    return df


def get_finals_by_asset_direction() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql(
        """
        SELECT asset, direction, COUNT(*) AS runs, SUM(finals) AS finals
        FROM runs WHERE asset!='UNKNOWN' AND deleted=0
        GROUP BY asset, direction ORDER BY asset, direction
    """,
        conn,
    )
    conn.close()
    return df


def get_warnings() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql(
        """
        SELECT id, asset, direction, timeframe, date, finals, template
        FROM runs WHERE parse_warning=1 AND deleted=0 ORDER BY date DESC
    """,
        conn,
    )
    conn.close()
    return df


def get_deleted_runs() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql(
        """
        SELECT id, asset, direction, timeframe, date, finals, template
        FROM runs WHERE deleted=1 ORDER BY asset, date DESC
    """,
        conn,
    )
    conn.close()
    return df


def id_date_exists(raw_id: str, date_str: str) -> bool:
    conn = get_conn()
    n = conn.execute(
        "SELECT COUNT(*) FROM runs WHERE id=? AND date=?", (raw_id, date_str)
    ).fetchone()[0]
    conn.close()
    return n > 0


def get_coverage_matrix() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql(
        """
       SELECT asset, direction, timeframe, SUM(finals) AS total_finals, COUNT(*) AS runs
       FROM runs
       WHERE deleted = 0
          AND asset != 'UNKNOWN'
          AND direction IN ('Long', 'Short')
          AND timeframe != 'UNKNOWN'
       GROUP BY asset, direction, timeframe
    """,
        conn,
    )
    conn.close()
    return df
