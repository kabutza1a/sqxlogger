"""
cleaner.py
StrategyQuant ID parser and data cleaning engine.
Asset lookup now reads from SQLite via db_lookup.py
"""
import re
from datetime import datetime

VALID_DIRECTIONS = {"L", "S", "LS"}
VALID_TIMEFRAMES = {"M15", "M30", "H1", "H2", "H4"}
DIRECTION_MAP    = {"L": "Long", "S": "Short", "LS": "LS"}

def _get_asset_map() -> dict:
    """Load asset map from database. Falls back to hardcoded if DB not ready."""
    try:
        import db_lookup
        m = db_lookup.get_lookup_map()
        if m:
            return m
    except Exception:
        pass
    # Fallback hardcoded map
    return {
        "AU":"AUDUSD","DAX":"DAX","DJ":"WS30","EG":"EURGBP","EJ":"EURJPY",
        "EU":"EURUSD","EURGBP":"EURGBP","G":"XAUUSD","GA":"GBPAUD","GDAX":"DAX",
        "GJ":"GBPJPY","GU":"GBPUSD","NDX":"NDX","NI225":"NI225","NU":"NZDUSD",
        "NZDUSD":"NZDUSD","SP":"SP500","UC":"USDCHF","UJ":"USDJPY","USDCHF":"USDCHF",
    }

def normalise_id(raw_id: str) -> str:
    s = raw_id.strip().upper().replace("-", "_")
    s = re.sub(r"[^A-Z0-9_]", "", s)
    return s.strip("_")

def parse_id(raw_id: str) -> dict:
    result = {
        "asset": "UNKNOWN", "direction": "UNKNOWN",
        "timeframe": "UNKNOWN", "parse_warning": False, "warnings": [],
    }
    if not raw_id or not raw_id.strip():
        result["parse_warning"] = True
        result["warnings"].append("ID is empty or null")
        return result

    asset_map = _get_asset_map()
    tokens = [t for t in re.split(r"[-_]", raw_id.strip()) if t]

    if not tokens:
        result["parse_warning"] = True
        result["warnings"].append("ID produced no tokens after splitting")
        return result

    stem = tokens[0].upper()
    if stem in asset_map:
        result["asset"] = asset_map[stem]
    else:
        result["parse_warning"] = True
        result["warnings"].append(f"Asset stem '{stem}' not found in lookup table")

    if len(tokens) < 2:
        result["parse_warning"] = True
        result["warnings"].append("No direction or timeframe tokens found")
        return result

    direction_token = None
    timeframe_token = None
    for tok in tokens[1:]:
        clean = re.sub(r"[^A-Z0-9]", "", tok.upper())
        if not clean:
            continue
        if clean in VALID_DIRECTIONS:
            direction_token = clean
        elif clean in VALID_TIMEFRAMES:
            timeframe_token = clean

    if direction_token:
        result["direction"] = DIRECTION_MAP[direction_token]
    else:
        result["parse_warning"] = True
        result["warnings"].append("No valid direction token found (L, S, or LS)")

    if timeframe_token:
        result["timeframe"] = timeframe_token
    else:
        result["parse_warning"] = True
        result["warnings"].append("No valid timeframe token found (M15,M30,H1,H2,H4)")

    return result

def parse_date(date_str: str):
    if not date_str or not str(date_str).strip():
        return None
    try:
        return datetime.strptime(str(date_str).strip(), "%d/%m/%Y").date()
    except ValueError:
        return None

def parse_duration_minutes(time_str: str):
    if not time_str or not str(time_str).strip():
        return None
    s = str(time_str).strip().upper()
    m = re.match(r"^(\d+)D(?:(\d+)H?)?(?:(\d+)M)?$", s)
    if m:
        return int(m.group(1))*1440 + (int(m.group(2)) if m.group(2) else 0)*60 + (int(m.group(3)) if m.group(3) else 0)
    m = re.match(r"^(\d+)H(?:(\d+)M?)?$", s)
    if m:
        return int(m.group(1))*60 + (int(m.group(2)) if m.group(2) else 0)
    return None

def clean_row(raw: dict) -> dict:
    cleaned = {}
    cleaned["id"] = str(raw.get("ID", "")).strip()
    parsed = parse_id(cleaned["id"])
    cleaned["asset"]         = parsed["asset"]
    cleaned["direction"]     = parsed["direction"]
    cleaned["timeframe"]     = parsed["timeframe"]
    cleaned["parse_warning"] = parsed["parse_warning"]
    cleaned["warnings"]      = parsed["warnings"]
    cleaned["normalised_id"] = normalise_id(cleaned["id"])

    date_val = parse_date(raw.get("date", ""))
    if date_val is None:
        cleaned["error"] = f"Invalid or missing date: '{raw.get('date', '')}'"
        return cleaned
    cleaned["date"] = date_val.isoformat()

    try:
        f = raw.get("finals", None)
        cleaned["finals"] = int(float(f)) if f not in (None, "", "nan") else None
    except (ValueError, TypeError):
        cleaned["finals"] = None
        cleaned["warnings"].append(f"Could not parse finals: '{raw.get('finals')}'")
        cleaned["parse_warning"] = True

    cleaned["time"]             = str(raw.get("time", "")).strip() or None
    cleaned["duration_minutes"] = parse_duration_minutes(cleaned["time"])

    try:
        lo = raw.get("loops", None)
        cleaned["loops"] = int(float(lo)) if lo not in (None, "", "nan") else None
    except (ValueError, TypeError):
        cleaned["loops"] = None

    cleaned["note2"]    = str(raw.get("Note2", "")).strip() or None
    cleaned["note"]     = str(raw.get("note",  "")).strip() or None
    cleaned["template"] = str(raw.get("template", "")).strip() or None
    cleaned["error"]    = None
    return cleaned
