# SQX Runs Logger

A private Streamlit dashboard for logging, tracking, and analysing [StrategyQuant](https://strategyquant.com/) strategy generation runs — replacing manual spreadsheet tracking with a proper searchable database.

I advise you converse with Claude AI (my default) or your preferred AI (ChatGPT, Grok, etc.) to guide you through installing this app — it's a simple process, and an AI assistant can walk you through it step by step. See below for example installation steps.

![Dashboard](Images/SQXRunsLogger%20dashboard.png)

## Features

- **Dashboard** — KPI cards and finals-by-asset reports, with a direction breakdown (Long / Short / LS)
- **Coverage Matrix** — a heatmap of every asset × timeframe × direction combination, so you can see at a glance where you have data and where the gaps are
- **Gap List** — a filterable list of suggested run IDs to target next, generated straight from the coverage gaps
- **View Data** — a sortable, filterable table of every run in the database
- **Add New Run / Edit / Delete** — manual entry with soft-delete (nothing is ever permanently lost)
- **Import CSV** — bulk import from a StrategyQuant CSV export, with automatic duplicate detection
- **Asset Lookup Table** — manage the ID-stem-to-asset mappings used to decode run IDs
- **Data Quality** — a review page for any rows the ID parser couldn't fully decode

## Screenshots

| | |
|---|---|
| ![Coverage Matrix](Images/SQXRunsLogger%20Coverage%20Matrix.png) Coverage Matrix | ![Asset Analysis](Images/SQXRunsLogger%20asset%20analysis.png) Finals by Asset — Direction Breakdown |
| ![View Data](Images/SQXRunsLogger%20View%20Data.png) View Data | ![Add New Run](Images/SQXRunsLogger.%20add%20run.png) Add New Run |
| ![Asset Lookup](Images/SQXRunsLogger%20asset%20lookup.png) Asset Lookup Table | ![Import CSV](Images/SQXRunsLogger%20import%20csv.png) Import CSV |
| ![Gap List / Targets](Images/SQXRunsLogger%20Targets.png) Gap List — Suggested Targets | ![Data Quality](Images/SQXRunsLogger%20Data%20Check.png) Data Quality |

## Requirements

- Python 3.8+
- Dependencies listed in [`requirements.txt`](requirements.txt) (Streamlit, pandas, Plotly)

## Installation

Anyone can clone the repo and run it locally or on a server:

```bash
git clone https://github.com/kabutza1a/sqxlogger
cd sqxlogger
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./start.sh
```

Ask your AI assistant to walk you through any of these steps if you're not familiar with the terminal.

## Where It Runs

SQX Runs Logger can run locally on a PC or Mac, or on the web via a VPS so you can access it from any browser. It requires very little in the way of resources — a free-tier cloud VPS (e.g. Oracle Cloud's Free Tier) is more than enough, or you can run it alongside other tools on a VPS you already have.

If you're deploying to a headless Linux VPS, you'll connect to it via SSH from a terminal — again, an AI assistant can talk you through setting that up.

## Documentation

- [Installation Notes](INSTALL-NOTES.md) — a plain-English guide to getting set up, written for non-programmers
- [User Guide](SQXRunsLogger_UserGuide_v1.0-public.docx) — a walkthrough of every page in the app
- [System Specification](SQXRunsLogger_Spec_v1.4-public.md) — ID parsing rules, database schema, and deployment notes

## Source Files

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit application — all pages and UI |
| `db.py` | Database operations — CRUD, queries, soft delete |
| `db_lookup.py` | Asset lookup table — stored in SQLite, manageable via the UI |
| `cleaner.py` | ID parser and data cleaning engine |
| `requirements.txt` | Python dependencies |
| `start.sh` | Convenience script to activate the venv and launch the app |

---

*If you want to modify SQX Runs Logger, fork the repo (or clone your own local copy) so you have your own version to work from.*
