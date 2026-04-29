"""
app.py
StrategyQuant Run Log — Streamlit Dashboard
Run with: streamlit run app.py
I added view data 28.4.26
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

import db
import cleaner

import db_lookup

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StrategyQuant Log",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Purple theme CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #2D0050;
    }
    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    /* Header banner */
    .sq-header {
        background: linear-gradient(135deg, #4D0080, #782DA7);
        padding: 18px 24px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .sq-header h1 {
        color: #FFFFFF;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .sq-header p {
        color: #DDB8FF;
        margin: 4px 0 0 0;
        font-size: 0.9rem;
    }
    /* KPI cards */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #D4A8F0;
        border-top: 4px solid #782DA7;
        border-radius: 8px;
        padding: 16px 20px;
        text-align: center;
    }
    .kpi-label {
        color: #782DA7;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .kpi-value {
        color: #2D0050;
        font-size: 2rem;
        font-weight: 700;
        line-height: 1;
    }
    .kpi-warn {
        border-top-color: #FF6B6B;
    }
    .kpi-warn .kpi-value { color: #CC0000; }
    /* Section titles */
    .section-title {
        background: #782DA7;
        color: #FFFFFF;
        padding: 8px 14px;
        border-radius: 6px;
        font-size: 0.95rem;
        font-weight: 600;
        margin: 20px 0 10px 0;
    }
    /* Table styling */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.88rem;
    }
    .styled-table th {
        background: #4D0080;
        color: white;
        padding: 8px 12px;
        text-align: left;
    }
    .styled-table tr:nth-child(even) td {
        background: #F3E8FF;
    }
    .styled-table tr:nth-child(odd) td {
        background: #FFFFFF;
    }
    .styled-table td {
        padding: 7px 12px;
        border-bottom: 1px solid #E0C8FF;
    }
    /* Nav buttons */
    div.stButton > button {
        background: #782DA7;
        color: white;
        border: none;
        border-radius: 6px;
        width: 100%;
        font-weight: 600;
    }
    div.stButton > button:hover {
        background: #4D0080;
    }
    /* Warning badge */
    .warn-badge {
        background: #FFE0E0;
        color: #CC0000;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    /* Success badge */
    .ok-badge {
        background: #E0FFE8;
        color: #007722;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .block-container {
        padding-top: 1rem !important;
    }
    header[data-testid="stHeader"] {
        display: none !important;
    }
    /* Sidebar separator labels */
    div[data-testid="stSidebar"] .stRadio label:nth-child(1),
    div[data-testid="stSidebar"] .stRadio label:nth-child(5) {
        color: #DDB8FF !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        pointer-events: none !important;
        opacity: 0.7 !important;
    }
    /* Hide the radio circle for separator items */
    div[data-testid="stSidebar"] .stRadio label:nth-child(1) span:first-child,
    div[data-testid="stSidebar"] .stRadio label:nth-child(5) span:first-child {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Init DB ───────────────────────────────────────────────────────────────────
db.init_db()

db_lookup.init_lookup()

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 SQX Runs Logger")
    st.markdown("---")

    page = st.radio(
        label="Navigate",
        options=["⬡  VIEWS", "Dashboard", "Coverage Matrix", "View Data","     ",
                 "⬡  ADMIN",
                 "Add New Run", "Edit / Delete", "Asset Lookup",
                 "Import CSV", "Data Quality"],
        label_visibility="collapsed",
        index=1,
        key="main_nav"
    )

    # Prevent the separator line from being a selectable page
    if page in ("⬡  VIEWS", "⬡  ADMIN"):
        page = "Dashboard"

    st.markdown("---")
    st.markdown(
        f"**Total runs:** {db.get_run_count()}  \n"
        f"**Total finals:** {db.get_total_finals():,}  \n"
        f"**Unique assets:** {db.get_unique_assets()}"
    )

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":

    st.markdown("""
    <div class="sq-header">
        <h1>📊 StrategyQuant Run Log — Dashboard</h1>
        <p>Summary of strategy generation runs across all assets</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI cards ─────────────────────────────────────────────────────────────
    total_runs    = db.get_run_count()
    total_finals  = db.get_total_finals()
    unique_assets = db.get_unique_assets()
    warn_count    = db.get_parse_warning_count()

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Total Runs</div>
            <div class="kpi-value">{total_runs:,}</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Total Finals</div>
            <div class="kpi-value">{total_finals:,}</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Unique Assets</div>
            <div class="kpi-value">{unique_assets}</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        warn_class = "kpi-card kpi-warn" if warn_count > 0 else "kpi-card"
        st.markdown(f"""<div class="{warn_class}">
            <div class="kpi-label">Parse Warnings</div>
            <div class="kpi-value">{warn_count}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if total_runs == 0:
        st.info("No data yet. Use **Import CSV** or **Add New Run** to get started.")
        st.stop()

    # ── Report 1: Finals by Asset ──────────────────────────────────────────────
    st.markdown('<div class="section-title">Finals by Asset</div>', unsafe_allow_html=True)

    df_asset = db.get_finals_by_asset()

    col_tbl, col_chart = st.columns([1, 1.4])

    with col_tbl:
        if not df_asset.empty:
            html = '<table class="styled-table"><thead><tr>'
            html += '<th>Asset</th><th style="text-align:right">Runs</th><th style="text-align:right">Total Finals</th>'
            html += '</tr></thead><tbody>'
            for _, row in df_asset.iterrows():
                finals_val = int(row["total_finals"]) if row["total_finals"] else 0
                html += f'<tr><td><b>{row["asset"]}</b></td>'
                html += f'<td style="text-align:right">{int(row["total_runs"])}</td>'
                html += f'<td style="text-align:right">{finals_val:,}</td></tr>'
            html += '</tbody></table>'
            st.markdown(html, unsafe_allow_html=True)

    with col_chart:
        if not df_asset.empty:
            fig = px.bar(
                df_asset,
                x="total_finals",
                y="asset",
                orientation="h",
                text="total_finals",
                color_discrete_sequence=["#782DA7"],
                labels={"total_finals": "Total Finals", "asset": "Asset"},
            )
            fig.update_traces(textposition="outside", texttemplate="%{text:,}")
            fig.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                font_family="Calibri",
                margin=dict(l=10, r=40, t=10, b=10),
                height=max(280, len(df_asset) * 36),
                xaxis=dict(showgrid=True, gridcolor="#F0E0FF"),
                yaxis=dict(categoryorder="total ascending"),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── Report 2: Finals by Asset × Direction ──────────────────────────────────
    st.markdown('<div class="section-title">Finals by Asset — Direction Breakdown</div>',
                unsafe_allow_html=True)

    df_dir = db.get_finals_by_asset_direction()

    if not df_dir.empty:
        # Pivot for table display
        pivot = df_dir.pivot_table(
            index="asset",
            columns="direction",
            values="finals",
            aggfunc="sum",
            fill_value=0,
        ).reset_index()
        pivot["Total"] = pivot.select_dtypes("number").sum(axis=1)
        pivot = pivot.sort_values("Total", ascending=False)

        col_tbl2, col_chart2 = st.columns([1, 1.4])

        with col_tbl2:
            dir_cols = [c for c in pivot.columns if c != "asset"]
            html = '<table class="styled-table"><thead><tr><th>Asset</th>'
            for c in dir_cols:
                html += f'<th style="text-align:right">{c}</th>'
            html += '</tr></thead><tbody>'
            for _, row in pivot.iterrows():
                html += f'<tr><td><b>{row["asset"]}</b></td>'
                for c in dir_cols:
                    val = int(row[c]) if pd.notna(row[c]) else 0
                    bold = " font-weight:600;" if c == "Total" else ""
                    html += f'<td style="text-align:right;{bold}">{val:,}</td>'
                html += '</tr>'
            html += '</tbody></table>'
            st.markdown(html, unsafe_allow_html=True)

        with col_chart2:
            COLOURS = {
                "Long":  "#782DA7",
                "Short": "#FF9900",
                "LS":    "#00AACC",
            }
            fig2 = go.Figure()
            for direction in df_dir["direction"].unique():
                subset = df_dir[df_dir["direction"] == direction]
                fig2.add_trace(go.Bar(
                    name=direction,
                    x=subset["asset"],
                    y=subset["finals"],
                    marker_color=COLOURS.get(direction, "#AAAAAA"),
                    text=subset["finals"],
                    textposition="outside",
                ))
            fig2.update_layout(
                barmode="group",
                plot_bgcolor="white",
                paper_bgcolor="white",
                font_family="Calibri",
                margin=dict(l=10, r=10, t=10, b=60),
                height=360,
                xaxis=dict(showgrid=False, tickangle=-35),
                yaxis=dict(showgrid=True, gridcolor="#F0E0FF", title="Finals"),
                legend=dict(
                    orientation="h",
                    yanchor="bottom", y=1.02,
                    xanchor="right",  x=1,
                ),
            )
            st.plotly_chart(fig2, use_container_width=True)

    else:
        st.info("No asset/direction data to display.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ADD NEW RUN
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Add New Run":

    st.markdown("""
    <div class="sq-header">
        <h1>➕ Add New Run</h1>
        <p>Enter details for a new StrategyQuant strategy generation run</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("add_run_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            raw_id   = st.text_input("ID *", placeholder="e.g. EU_L_H1, GU-S-M30")
            date_str = st.text_input("Date * (DD/MM/YYYY)", 
                          value=datetime.today().strftime("%d/%m/%Y"))
            finals   = st.number_input("Finals", min_value=0, step=1, value=0)
            template = st.text_input("Template", value="v4")
        with c2:
            run_time = st.text_input("Run Time", placeholder="e.g. 14h30, 2D6")
            loops    = st.number_input("Loops", min_value=0, step=1, value=0)
            note     = st.text_area("Note", height=80)
            note2    = st.text_input("Note 2")

        submitted = st.form_submit_button("💾 Save Run", use_container_width=True)

    if submitted:
        errors = []

        # Validate ID
        if not raw_id.strip():
            errors.append("ID is required.")

        # Validate date
        parsed_date = cleaner.parse_date(date_str)
        if parsed_date is None:
            errors.append(f"Date '{date_str}' is not valid. Use DD/MM/YYYY format.")

        # Check for true duplicate
        if raw_id.strip() and parsed_date:
            if db.id_date_exists(raw_id.strip(), parsed_date.isoformat()):
                errors.append(
                    f"A run with ID '{raw_id.strip()}' on {parsed_date.isoformat()} already exists."
                )

        if errors:
            for e in errors:
                st.error(e)
        else:
            # Clean and parse
            raw_row = {
                "ID":       raw_id.strip(),
                "date":     date_str.strip(),
                "finals":   finals if finals > 0 else None,
                "template": template.strip() or None,
                "time":     run_time.strip() or None,
                "loops":    loops if loops > 0 else None,
                "note":     note.strip() or None,
                "Note2":    note2.strip() or None,
            }
            cleaned = cleaner.clean_row(raw_row)

            # Show parse preview
            with st.expander("Parsed values — please confirm", expanded=True):
                pc1, pc2, pc3 = st.columns(3)
                pc1.metric("Asset",     cleaned["asset"])
                pc2.metric("Direction", cleaned["direction"])
                pc3.metric("Timeframe", cleaned["timeframe"])
                if cleaned["parse_warning"]:
                    for w in cleaned["warnings"]:
                        st.warning(f"⚠️ {w}")

            ok, msg = db.insert_run(cleaned)
            if ok:
                st.success(f"✅ Run saved successfully! Multi-run ID: {cleaned['normalised_id']}")
            else:
                st.error(f"❌ {msg}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: IMPORT CSV
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Import CSV":

    st.markdown("""
    <div class="sq-header">
        <h1>📁 Import CSV</h1>
        <p>Upload a StrategyQuant CSV export to bulk import runs</p>
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "**Expected columns:** ID, date, finals, time, loops, Note2, note, template  \n"
        "**Date format:** DD/MM/YYYY  \n"
        "**Duplicate runs** (same ID + same date) will be skipped automatically."
    )

    uploaded = st.file_uploader("Choose CSV file", type=["csv"])

    if uploaded:
        try:
            # Try skipping blank first row (as in source data)
            try:
                df_raw = pd.read_csv(uploaded, skiprows=1)
                if "ID" not in df_raw.columns:
                    uploaded.seek(0)
                    df_raw = pd.read_csv(uploaded)
            except Exception:
                uploaded.seek(0)
                df_raw = pd.read_csv(uploaded)

            st.write(f"**{len(df_raw)} rows found.** Preview:")
            st.dataframe(df_raw.head(5), use_container_width=True)

            if st.button("▶ Import All Rows", use_container_width=True):
                imported = skipped = rejected = warned = 0
                log = []

                for _, raw in df_raw.iterrows():
                    cleaned = cleaner.clean_row(raw.to_dict())

                    if cleaned.get("error"):
                        rejected += 1
                        log.append(f"❌ REJECTED [{raw.get('ID','')}] — {cleaned['error']}")
                        continue

                    ok, msg = db.insert_run(cleaned)
                    if ok:
                        imported += 1
                        if cleaned["parse_warning"]:
                            warned += 1
                            for w in cleaned["warnings"]:
                                log.append(f"⚠️ [{cleaned['id']}] {w}")
                    else:
                        skipped += 1
                        log.append(f"⏭ SKIPPED [{cleaned['id']}] — {msg}")

                # Summary
                st.success(f"✅ Import complete: **{imported}** imported, "
                           f"**{skipped}** skipped (duplicates), "
                           f"**{rejected}** rejected (bad dates), "
                           f"**{warned}** with parse warnings.")

                if log:
                    with st.expander("Import log", expanded=warned > 0):
                        for line in log:
                            st.markdown(line)

                st.rerun()

        except Exception as e:
            st.error(f"Could not read CSV: {e}")



# ══════════════════════════════════════════════════════════════════════════════
# PAGE: VIEW DATA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "View Data":

    st.markdown("""
    <div class="sq-header">
        <h1>🗂️ View Data</h1>
        <p>All imported runs from the database</p>
    </div>
    """, unsafe_allow_html=True)

    df_all = db.get_all_runs()

    if df_all.empty:
        st.info("No data yet. Use Import CSV or Add New Run to get started.")
    else:
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            assets = ["All"] + sorted(df_all["asset"].unique().tolist())
            asset_filter = st.selectbox("Filter by Asset", assets)
        with col2:
            dirs = ["All"] + sorted(df_all["direction"].unique().tolist())
            dir_filter = st.selectbox("Filter by Direction", dirs)
        with col3:
            tfs = ["All"] + sorted(df_all["timeframe"].unique().tolist())
            tf_filter = st.selectbox("Filter by Timeframe", tfs)

        # Apply filters
        df_view = df_all.copy()
        if asset_filter != "All":
            df_view = df_view[df_view["asset"] == asset_filter]
        if dir_filter != "All":
            df_view = df_view[df_view["direction"] == dir_filter]
        if tf_filter != "All":
            df_view = df_view[df_view["timeframe"] == tf_filter]

      
 

        # Clean up display
        display_cols = ["asset", "direction", "timeframe", "finals", "template", "date",
                "time", "loops", "note", "note2", "id", "parse_warning"]
        df_display = df_view[[c for c in display_cols if c in df_view.columns]].copy()

        # Replace nan/None with blank
        df_display = df_display.fillna("")
        df_display["note"]  = df_display["note"].replace("nan", "")
        df_display["note2"] = df_display["note2"].replace("nan", "")
        df_display["time"]  = df_display["time"].replace("nan", "")

        df_display["finals"] = df_display["finals"].apply(
            lambda v: int(v) if v != "" and v == v else ""
        )

        #        Human-friendly parse_warning
        df_display["parse_warning"] = df_display["parse_warning"].apply(
           lambda v: "⚠️ Yes" if v in (1, "1", True, "True") else ""
)


        total_finals_displayed = df_display["finals"].apply(
            lambda v: int(v) if v != "" else 0
        ).sum()

        st.markdown(
            f"<p style='font-size:1.2rem; font-weight:700; color:#4D0080;'>"
            f"➡️ Total Finals: {total_finals_displayed:,} ⬅️"
            f"&nbsp;&nbsp;<span style='font-size:0.9rem; font-weight:400; color:#666;'>"
            f"| Showing {len(df_display)} of {len(df_all)} rows</span></p>",
            unsafe_allow_html=True
        )
        st.dataframe(df_display, use_container_width=True, height=500)


        # ══════════════════════════════════════════════════════════════════════════════
# PAGE: EDIT / DELETE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Edit / Delete":

    st.markdown("""
    <div class="sq-header">
        <h1>✏️ Edit / Delete</h1>
        <p>Search for a record, edit its fields, or soft-delete it</p>
    </div>
    """, unsafe_allow_html=True)

    df_all = db.get_all_runs(include_deleted=False)

    if df_all.empty:
        st.info("No records in the database yet.")
        st.stop()

    # ── Search / filter to find the record ───────────────────────────────────
    st.markdown('<div class="section-title">Find a Record</div>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    with f1:
        assets = ["All"] + sorted(df_all["asset"].unique().tolist())
        sel_asset = st.selectbox("Asset", assets, key="ed_asset")
    with f2:
        dirs = ["All"] + sorted(df_all["direction"].unique().tolist())
        sel_dir = st.selectbox("Direction", dirs, key="ed_dir")
    with f3:
        tfs = ["All"] + sorted(df_all["timeframe"].unique().tolist())
        sel_tf = st.selectbox("Timeframe", tfs, key="ed_tf")

    df_search = df_all.copy()
    if sel_asset != "All":
        df_search = df_search[df_search["asset"] == sel_asset]
    if sel_dir != "All":
        df_search = df_search[df_search["direction"] == sel_dir]
    if sel_tf != "All":
        df_search = df_search[df_search["timeframe"] == sel_tf]

    if df_search.empty:
        st.warning("No records match the filter.")
    else:
        # Build a readable label for each record
        df_search["_label"] = (
            df_search["asset"] + " | " +
            df_search["direction"] + " | " +
            df_search["timeframe"] + " | " +
            df_search["date"] + " | Finals: " +
            df_search["finals"].fillna(0).astype(int).astype(str)
        )
        selected_label = st.selectbox(
            "Select record to edit", df_search["_label"].tolist(), key="ed_select"
        )
        selected_row = df_search[df_search["_label"] == selected_label].iloc[0]
        orig_id   = selected_row["id"]
        orig_date = selected_row["date"]

        st.markdown('<div class="section-title">Edit Record</div>', unsafe_allow_html=True)

        with st.form("edit_form"):
            e1, e2 = st.columns(2)
            with e1:
                new_id   = st.text_input("ID", value=str(orig_id))
                new_date = st.text_input("Date (DD/MM/YYYY)",
                                          value=pd.to_datetime(orig_date).strftime("%d/%m/%Y"))
                new_finals = st.number_input("Finals", min_value=0, step=1,
                                            value=int(selected_row["finals"]) if pd.notna(selected_row["finals"]) else 0)
                new_template = st.text_input("Template",
                                              value=str(selected_row["template"] or ""))
            with e2:
                new_time  = st.text_input("Run Time", value=str(selected_row["time"]) if pd.notna(selected_row["time"]) else "")
                new_loops = st.number_input("Loops", min_value=0, step=1,
                                            value=int(selected_row["loops"]) if pd.notna(selected_row["loops"]) else 0)
                new_note = st.text_area("Note", value=str(selected_row["note"]) if pd.notna(selected_row["note"]) else "", height=80)
                new_note2 = st.text_input("Note 2", value=str(selected_row["note2"]) if pd.notna(selected_row["note2"]) else "")

                s1, s2 = st.columns([3, 1])
                with s1:
                 save_btn = st.form_submit_button("💾 Save Changes", use_container_width=True)
                with s2:
                    del_btn  = st.form_submit_button("🗑️ Delete", use_container_width=True)

        if save_btn:
            parsed_date = cleaner.parse_date(new_date)
            if parsed_date is None:
                st.error(f"Date '{new_date}' is not valid. Use DD/MM/YYYY.")
            else:
                ok, msg = db.update_run(orig_id, orig_date, {
                    "id":       new_id,
                    "date":     parsed_date.isoformat(),
                    "finals":   new_finals if new_finals > 0 else None,
                    "template": new_template or None,
                    "time":     new_time or None,
                    "loops":    new_loops if new_loops > 0 else None,
                    "note":     new_note or None,
                    "note2":    new_note2 or None,
                })
                if ok:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

        if del_btn:
            st.session_state["pending_delete"] = (orig_id, orig_date)

    # ── Delete confirmation ───────────────────────────────────────────────────
    if "pending_delete" in st.session_state:
        del_id, del_date = st.session_state["pending_delete"]
        st.warning(
            f"⚠️ Are you sure you want to delete **{del_id}** on **{del_date}**?  \n"
            f"The record will be hidden but not permanently removed."
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Yes, delete it", use_container_width=True):
                ok, msg = db.soft_delete_run(del_id, del_date)
                if ok:
                    st.success(f"Record deleted. You can restore it from Data Quality.")
                    del st.session_state["pending_delete"]
                    st.rerun()
                else:
                    st.error(msg)
        with c2:
            if st.button("❌ Cancel", use_container_width=True):
                del st.session_state["pending_delete"]
                st.rerun()

    # ── Deleted records / restore ─────────────────────────────────────────────
    st.markdown('<div class="section-title">Deleted Records</div>', unsafe_allow_html=True)
    df_deleted = db.get_deleted_runs()

    if df_deleted.empty:
        st.caption("No deleted records.")
    else:
        st.caption(f"{len(df_deleted)} deleted record(s) — click Restore to reinstate.")
        for _, row in df_deleted.iterrows():
            rc1, rc2 = st.columns([4, 1])
            with rc1:
                st.markdown(
                    f"**{row['asset']}** | {row['direction']} | {row['timeframe']} | "
                    f"{row['date']} | Finals: {int(row['finals']) if pd.notna(row['finals']) else 0}"      
                )
            with rc2:
                if st.button("↩️ Restore", key=f"restore_{row['id']}_{row['date']}"):
                    ok, msg = db.restore_run(row["id"], row["date"])
                    if ok:
                        st.success("Restored.")
                        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ASSET LOOKUP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Asset Lookup":

    st.markdown("""
    <div class="sq-header">
        <h1>🔑 Asset Lookup Table</h1>
        <p>Manage ID stem to asset name mappings</p>
    </div>
    """, unsafe_allow_html=True)

    df_lookup = db_lookup.get_lookup_df()

    st.markdown('<div class="section-title">Current Mappings</div>', unsafe_allow_html=True)
    st.dataframe(df_lookup, use_container_width=True, height=400)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Add New Mapping</div>', unsafe_allow_html=True)
    with st.form("add_mapping_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            new_stem  = st.text_input("ID Stem", placeholder="e.g. GC")
        with c2:
            new_asset = st.text_input("Asset Name", placeholder="e.g. XAUUSD")
        submitted = st.form_submit_button("➕ Add Mapping", use_container_width=True)
    if submitted:
        ok, msg = db_lookup.add_mapping(new_stem, new_asset)
        if ok:
            st.success(f"✅ {msg}")
            st.rerun()
        else:
            st.error(f"❌ {msg}")

    st.markdown('<div class="section-title">Update Existing Mapping</div>', unsafe_allow_html=True)
    with st.form("update_mapping_form", clear_on_submit=True):
        stems     = df_lookup["stem"].tolist()
        upd_stem  = st.selectbox("Select Stem to Update", stems)
        upd_asset = st.text_input("New Asset Name")
        upd_submitted = st.form_submit_button("💾 Update Mapping", use_container_width=True)
    if upd_submitted:
        ok, msg = db_lookup.update_mapping(upd_stem, upd_asset)
        if ok:
            st.success(f"✅ {msg}")
            st.rerun()
        else:
            st.error(f"❌ {msg}")

    st.markdown('<div class="section-title">Re-parse Unknown Records</div>', unsafe_allow_html=True)
    st.caption("After adding new mappings, click below to fix any UNKNOWN records automatically.")
    if st.button("🔄 Re-parse UNKNOWN Records", use_container_width=True):
        fixed, still_unknown = db_lookup.reparse_unknowns()
        if fixed > 0:
            st.success(f"✅ Fixed {fixed} record(s).")
        if still_unknown > 0:
            st.warning(f"⚠️ {still_unknown} record(s) still UNKNOWN.")
        if fixed == 0 and still_unknown == 0:
            st.info("No UNKNOWN records found — everything is clean!")
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: COVERAGE MATRIX
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Coverage Matrix":

    st.markdown("""
    <div class="sq-header">
        <h1>🗺️ Coverage Matrix</h1>
        <p>Finals by asset × timeframe × direction — green = covered, red = gap to target</p>
    </div>
    """, unsafe_allow_html=True)

    df_cov = db.get_coverage_matrix()

    if df_cov.empty:
        st.info("No data yet. Import or add runs to see the coverage matrix.")
        st.stop()

    TIMEFRAMES = ["M15", "M30", "H1", "H2", "H4"]
    DIRECTIONS = ["Long", "Short"]

    # Get all assets present in data, sorted
    all_assets = sorted(df_cov["asset"].unique().tolist())

    # Build lookup dict: (asset, timeframe, direction) -> total_finals
    lookup = {}
    for _, row in df_cov.iterrows():
        key = (row["asset"], row["timeframe"], row["direction"])
        lookup[key] = int(row["total_finals"]) if pd.notna(row["total_finals"]) else 0

    # ── Summary KPIs ──────────────────────────────────────────────────────────
    total_cells  = len(all_assets) * len(TIMEFRAMES) * len(DIRECTIONS)
    covered      = sum(1 for a in all_assets for tf in TIMEFRAMES
                       for d in DIRECTIONS if lookup.get((a, tf, d), 0) > 0)
    gaps         = total_cells - covered
    coverage_pct = round((covered / total_cells * 100) if total_cells > 0 else 0, 1)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Assets Tracked</div>
            <div class="kpi-value">{len(all_assets)}</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Cells Covered</div>
            <div class="kpi-value">{covered}</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card kpi-warn">
            <div class="kpi-label">Gaps (targets)</div>
            <div class="kpi-value">{gaps}</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Coverage %</div>
            <div class="kpi-value">{coverage_pct}%</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Legend ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex; gap:20px; margin-bottom:12px; font-size:12px; flex-wrap:wrap;">
        <span style="display:flex;align-items:center;gap:6px;">
            <span style="width:16px;height:16px;border-radius:3px;background:#1D9E75;display:inline-block;"></span>
            <span>Strong (50+)</span>
        </span>
        <span style="display:flex;align-items:center;gap:6px;">
            <span style="width:16px;height:16px;border-radius:3px;background:#5DCAA5;display:inline-block;"></span>
            <span>Good (20-49)</span>
        </span>
        <span style="display:flex;align-items:center;gap:6px;">
            <span style="width:16px;height:16px;border-radius:3px;background:#9FE1CB;display:inline-block;"></span>
            <span>Partial (1-19)</span>
        </span>
        <span style="display:flex;align-items:center;gap:6px;">
            <span style="width:16px;height:16px;border-radius:3px;background:#FFE4E4;border:1px solid #ffaaaa;display:inline-block;"></span>
            <span>Gap — target this next</span>
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Build HTML matrix table ───────────────────────────────────────────────
    def cell_bg(val):
        if val is None or val == 0:
            return "#FFE4E4"
        if val >= 50: return "#1D9E75"
        if val >= 20: return "#5DCAA5"
        return "#9FE1CB"

    def cell_fg(val):
        if val is None or val == 0:
            return "#cc6666"
        if val >= 20: return "#085041"
        return "#0F6E56"

    html = """
    <style>
    .matrix-wrap { overflow-x: auto; }
    .matrix { border-collapse: collapse; font-size: 12px; width: 100%; }
    .matrix th {
        padding: 5px 8px;
        text-align: center;
        font-weight: 500;
        border-bottom: 2px solid #782DA7;
        color: #4D0080;
        white-space: nowrap;
    }
    .matrix th.asset-col {
        text-align: left;
        min-width: 90px;
        border-right: 2px solid #782DA7;
        position: sticky;
        left: 0;
        background: white;
        z-index: 2;
    }
    .matrix th.tf-header {
        border-left: 2px solid #D4A8F0;
        color: #4D0080;
        font-size: 13px;
    }
    .matrix th.dir-header-l {
        border-left: 2px solid #D4A8F0;
        color: #782DA7;
        font-size: 11px;
        border-bottom: 2px solid #782DA7;
    }
    .matrix th.dir-header-s {
        color: #FF9900;
        font-size: 11px;
        border-bottom: 2px solid #782DA7;
    }
    .matrix td {
        padding: 5px 6px;
        text-align: center;
        border-bottom: 0.5px solid #E8D5F5;
        min-width: 44px;
        font-weight: 500;
    }
    .matrix td.asset-name {
        text-align: left;
        font-weight: 600;
        color: #2D0050;
        border-right: 2px solid #782DA7;
        position: sticky;
        left: 0;
        background: white;
        z-index: 1;
        padding-left: 10px;
    }
    .matrix td.long-cell {
        border-left: 2px solid #D4A8F0;
    }
    .matrix tr:hover td {
        filter: brightness(0.95);
    }
    </style>
    <div class="matrix-wrap">
    <table class="matrix">
    <thead>
        <tr>
            <th class="asset-col" rowspan="2">Asset</th>
    """

    for tf in TIMEFRAMES:
        html += f'<th class="tf-header" colspan="2">{tf}</th>'

    html += "</tr><tr>"

    for tf in TIMEFRAMES:
        html += f'<th class="dir-header-l">Long</th>'
        html += f'<th class="dir-header-s">Short</th>'

    html += "</tr></thead><tbody>"

    for asset in all_assets:
        html += f'<tr><td class="asset-name">{asset}</td>'
        for tf in TIMEFRAMES:
            for direction in DIRECTIONS:
                val = lookup.get((asset, tf, direction), None)
                bg  = cell_bg(val)
                fg  = cell_fg(val)
                cls = "long-cell" if direction == "Long" else ""
                display = str(val) if (val is not None and val > 0) else "—"
                html += (f'<td class="{cls}" '
                         f'style="background:{bg}; color:{fg};">'
                         f'{display}</td>')
        html += "</tr>"

    html += "</tbody></table></div>"

    st.markdown(html, unsafe_allow_html=True)

    # ── Gap list ──────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Gap List — Suggested Mining Targets</div>',
                unsafe_allow_html=True)

    gap_rows = []
    for asset in all_assets:
        for tf in TIMEFRAMES:
            for direction in DIRECTIONS:
                val = lookup.get((asset, tf, direction), None)
                if not val:
                    gap_rows.append({
                        "Asset":     asset,
                        "Timeframe": tf,
                        "Direction": direction,
                        "ID to run": f"{next((k for k,v in {'AUDUSD':'AU','DAX':'DAX','WS30':'DJ','EURGBP':'EG','EURJPY':'EJ','EURUSD':'EU','XAUUSD':'G','GBPAUD':'GA','GBPJPY':'GJ','GBPUSD':'GU','NDX':'NDX','NI225':'NI225','NZDUSD':'NU','SP500':'SP','USDCHF':'UC','USDJPY':'UJ'}.items() if v == asset), asset)}_{direction[0]}_{tf}",
                    })

    df_gaps = pd.DataFrame(gap_rows)
    if not df_gaps.empty:
        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            gap_asset = st.selectbox("Filter gaps by asset",
                                      ["All"] + sorted(df_gaps["Asset"].unique().tolist()),
                                      key="gap_asset")
        with col_filter2:
            gap_tf = st.selectbox("Filter gaps by timeframe",
                                   ["All"] + TIMEFRAMES, key="gap_tf")

        df_gaps_view = df_gaps.copy()
        if gap_asset != "All":
            df_gaps_view = df_gaps_view[df_gaps_view["Asset"] == gap_asset]
        if gap_tf != "All":
            df_gaps_view = df_gaps_view[df_gaps_view["Timeframe"] == gap_tf]

        st.caption(f"{len(df_gaps_view)} gaps shown")
        st.dataframe(df_gaps_view, use_container_width=True, height=300, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DATA QUALITY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Data Quality":

    st.markdown("""
    <div class="sq-header">
        <h1>⚠️ Data Quality</h1>
        <p>Rows flagged during ID parsing — retained in database but need review</p>
    </div>
    """, unsafe_allow_html=True)

    df_warn = db.get_warnings()

    if df_warn.empty:
        st.success("✅ No data quality issues found. All rows parsed cleanly.")
    else:
        st.warning(f"**{len(df_warn)} rows** have parse warnings.")
        st.dataframe(
            df_warn.astype(str),
            use_container_width=True,
            height=400,
        )
        st.caption(
            "Cells highlighted in red contain UNKNOWN values due to "
            "unrecognised ID tokens. Use Add New Run to re-enter corrected data."
        )
