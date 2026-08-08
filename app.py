import streamlit as st
import pandas as pd
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Vendor Sourcing Agent",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

/* ── Base: dark navy throughout ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #0F1F1A !important;
    font-family: 'DM Sans', sans-serif;
    color: #FFFFFF !important;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: #0A1810 !important; }
#MainMenu, footer { visibility: hidden; }

/* ── All default streamlit text → white ── */
p, span, label, div, li { color: #FFFFFF !important; }
.stMarkdown p, .stMarkdown span { color: #FFFFFF !important; }

/* ── Typography ── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'DM Serif Display', serif;
    color: #FFFFFF !important;
}

/* ── Wordmark ── */
.wordmark {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #FFFFFF !important;
    letter-spacing: -0.5px;
    margin-bottom: 0;
    line-height: 1;
}
.wordmark-sub {
    font-size: 0.82rem;
    color: #B8D8C8 !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 2px;
    font-weight: 500;
}

/* ── Search card: slightly lighter navy ── */
.search-card {
    background: #162E26;
    border-radius: 16px;
    padding: 28px 32px;
    border: 1px solid #1E4035;
    box-shadow: 0 2px 16px rgba(0,0,0,0.2);
    margin-bottom: 24px;
}

/* ── Inputs: dark navy bg, white text ── */
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
    background: #0F1F1A !important;
    border: 1.5px solid #1E4035 !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    color: #FFFFFF !important;
    padding: 10px 14px !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
    color: #6DB89A !important;
}
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
    border-color: #3DAA7A !important;
    box-shadow: 0 0 0 3px rgba(61,170,122,0.2) !important;
}

/* ── Input labels ── */
[data-testid="stTextInput"] label, [data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label {
    color: #D8F0E4 !important;
    font-weight: 500 !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: #0F1F1A !important;
    border: 1.5px solid #1E4035 !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
}

/* ── Radio buttons ── */
[data-testid="stRadio"] label { color: #FFFFFF !important; }
[data-testid="stRadio"] span { color: #FFFFFF !important; }

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: #3DAA7A !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 10px 28px !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
.stButton > button[kind="primary"]:hover {
    background: #2E8A60 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(61,170,122,0.4) !important;
}

/* ── Secondary / history buttons ── */
.stButton > button[kind="secondary"],
.stButton > button {
    background: #162E26 !important;
    border: 1.5px solid #1E4035 !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #FFFFFF !important;
}
.stButton > button:hover {
    border-color: #3DAA7A !important;
}

/* ── Status badge ── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #162E26;
    color: #B8D8C8;
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 16px;
    border: 1px solid #1E4035;
}
.status-badge.running {
    background: #3A2E1A;
    color: #F0B060;
    border-color: #C8873A;
}
.status-badge.done {
    background: #0A2A18;
    color: #60C080;
    border-color: #1E6A3A;
}

/* ── Field pills ── */
.field-pill {
    display: inline-block;
    background: #1E4035;
    color: #D8F0E4 !important;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-weight: 500;
    margin: 3px;
}
.field-pill.stores {
    background: #5A3A1A;
    color: #F5C880 !important;
}

/* ── Tip box ── */
.tip-box {
    background: #162E26;
    border-left: 3px solid #3DAA7A;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    font-size: 0.85rem;
    color: #B8D8C8 !important;
    margin-top: 12px;
}
.tip-box.stores {
    background: #3A2A14;
    border-left-color: #C8873A;
    color: #F0C070 !important;
}

/* ── Divider ── */
.section-divider {
    height: 1px;
    background: #1E4035;
    margin: 24px 0;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden;
    border: 1px solid #1E4035 !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background: #162E26 !important;
    border: 1.5px solid #3DAA7A !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
}

/* ── Caption text ── */
.stCaptionContainer, [data-testid="stCaptionContainer"] {
    color: #B8D8C8 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state init ──────────────────────────────────────────────────────────
if "mode" not in st.session_state:
    st.session_state.mode = "events"
if "results_df" not in st.session_state:
    st.session_state.results_df = None
if "run_history" not in st.session_state:
    st.session_state.run_history = []
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "status_msg" not in st.session_state:
    st.session_state.status_msg = ""
if "last_query" not in st.session_state:
    st.session_state.last_query = {}

# ── Helper: call Layer 2 (stub — replace with real agent call) ──────────────────
def run_agent(mode, goal, location, date_range=None, radius=None):
    import anthropic

    import os
    from anthropic import Anthropic

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    if mode == "events":
        date_hint = f" between {date_range[0]} and {date_range[1]}" if date_range and date_range[0] else ""
        user_msg = (
            f"Search the web and find vendor/exhibitor booth opportunities for: {goal}. "
            f"Location: {location}{date_hint}. "
            f"Run no more than 3 searches. Find 5-8 real events."
        )
        fields = "Event name, Date, Type, Booth cost ($), Deadline, Location, Contact Email, Phone, Website, Notes"
    else:
        user_msg = (
            f"Search the web and find retail stores matching: {goal}. "
            f"Location: {location}. "
            f"Run no more than 3 searches. Find 5-8 real stores."
        )
        fields = "Store name, Address, Type, Sub-type, Phone, Website, Notes"

    # Step 1: let Claude search the web
    search_response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system="You are a research assistant. Search the web and summarise what you find in plain text. Do not output JSON yet.",
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": user_msg}]
    )

    search_text = " ".join(
        block.text for block in search_response.content
        if hasattr(block, "text")
    )

    if not search_text.strip():
        st.error("No results found. Try a different search.")
        return []

    # Step 2: ask Claude to format the findings as JSON
    format_response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system="You are a data formatter. Convert the provided text into a JSON array. Return a raw JSON array only — no markdown, no explanation, no code fences.",
        messages=[{
            "role": "user",
            "content": (
                f"Convert this into a JSON array. Each item must have these exact keys: {fields}. "
                f"Use — for missing values. Here is the data:\n\n{search_text}"
            )
        }]
    )

    raw = " ".join(
        block.text for block in format_response.content
        if hasattr(block, "text")
    )

    clean = raw.strip().strip("```json").strip("```").strip()

    if not clean:
        st.error("Couldn't format results. Please try again.")
        return []

    return json.loads(clean)

# ── Google Sheets sync (Layer 5) ───────────────────────────────────────────────
def sync_to_sheets(df, is_events):
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        st.error("Missing packages. Run: pip install gspread google-auth")
        return

    KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendorfind-50ab34f8fa28.json")
    SHEET_NAME = "VendorFind Results"
    TAB_NAME = "Events" if is_events else "Stores"

    try:
        creds = Credentials.from_service_account_file(
            KEY_FILE,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
        )
        client = gspread.authorize(creds)
        spreadsheet = client.open(SHEET_NAME)

        # Get or create the right tab
        try:
            worksheet = spreadsheet.worksheet(TAB_NAME)
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=TAB_NAME, rows=500, cols=20)

        # Write header + rows
        data = [df.columns.tolist()] + df.astype(str).values.tolist()
        worksheet.update(data, "A1")

        # Bold the header row
        spreadsheet.batch_update({"requests": [{
            "repeatCell": {
                "range": {"sheetId": worksheet.id, "startRowIndex": 0, "endRowIndex": 1},
                "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                "fields": "userEnteredFormat.textFormat.bold"
            }
        }]})

        st.success(f"Synced {len(df)} rows to the \'{TAB_NAME}\' tab in Google Sheets.")

    except FileNotFoundError:
        st.error("Key file not found. Make sure vendorfind-50ab34f8fa28.json is in the same folder as app.py.")
    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"Sheet \'{SHEET_NAME}\' not found. Make sure you created it and shared it with the service account email.")
    except Exception as e:
        st.error(f"Sync failed: {e}")

# ── Status update helper ────────────────────────────────────────────────────────
def update_status(placeholder, msg, badge_class="running"):
    icon = "⟳" if badge_class == "running" else "✓"
    placeholder.markdown(
        f'<div class="status-badge {badge_class}">{icon} {msg}</div>',
        unsafe_allow_html=True
    )

# ── LAYOUT ─────────────────────────────────────────────────────────────────────
# Header
col_logo, col_spacer = st.columns([2, 3])
with col_logo:
    st.markdown('<div class="wordmark">🌿 VendorFind</div>', unsafe_allow_html=True)
    st.markdown('<div class="wordmark-sub">Wellness vendor sourcing agent</div>', unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# Mode toggle (using radio styled as toggle)
mode_col, _ = st.columns([2, 3])
with mode_col:
    mode_choice = st.radio(
        "Search mode",
        options=["🗓 Find Events", "🏪 Find Stores"],
        horizontal=True,
        label_visibility="collapsed",
        key="mode_radio"
    )
    st.session_state.mode = "events" if "Events" in mode_choice else "stores"

is_events = st.session_state.mode == "events"
accent = "#2E5339" if is_events else "#C8873A"
pill_class = "" if is_events else "stores"
tip_class = "" if is_events else "stores"

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Main two-column layout ──────────────────────────────────────────────────────
left_col, right_col = st.columns([3, 1], gap="large")

with left_col:
    st.markdown('<div class="search-card">', unsafe_allow_html=True)

    if is_events:
        st.markdown("##### Find vendor events")
        goal = st.text_area(
            "What are you looking for?",
            placeholder="e.g. vegan festivals, wellness expos, cultural fairs, holistic health events",
            height=90,
            key="goal_events"
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            location = st.text_input("Location", placeholder="e.g. New England", key="loc_events")
        with c2:
            date_from = st.text_input("From", placeholder="e.g. June 2026", key="date_from")
        with c3:
            date_to = st.text_input("To", placeholder="e.g. December 2026", key="date_to")

        tip_text = "💡 Be specific about event types and your geography to get the most relevant results."
        fields_label = "Fields extracted per event:"
        fields = ["Event name", "Date", "Type", "Booth cost", "Deadline", "Location", "Contact Email", "Phone", "Website"]
    else:
        st.markdown("##### Find stores and retailers")
        goal = st.text_area(
            "What types of stores?",
            placeholder="e.g. ethnic grocery stores, new age shops, ayurvedic stores, metaphysical shops",
            height=90,
            key="goal_stores"
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            location = st.text_input("Location", placeholder="e.g. Greater Boston", key="loc_stores")
        with c2:
            radius = st.selectbox("Radius", ["25 miles", "50 miles", "100 miles", "Statewide"], key="radius")
        with c3:
            store_focus = st.selectbox(
                "Focus",
                ["All types", "Ethnic grocery", "New age / metaphysical", "Ayurvedic / herbal", "Health food"],
                key="store_focus"
            )
        date_from = date_to = None

        tip_text = "💡 Run separate searches for each store type to get better coverage across your region."
        fields_label = "Fields extracted per store:"
        fields = ["Store name", "Address", "Type", "Sub-type", "Phone", "Website", "Notes"]

    # Field pills
    st.markdown(f"<div style='margin-top:12px;font-size:0.8rem;color:#B8D8C8;font-weight:500;margin-bottom:4px'>{fields_label}</div>", unsafe_allow_html=True)
    pills_html = "".join([f'<span class="field-pill {pill_class}">{f}</span>' for f in fields])
    st.markdown(pills_html, unsafe_allow_html=True)

    st.markdown(f'<div class="tip-box {tip_class}">{tip_text}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    run_btn = st.button(
        f"{'🔍 Search for events' if is_events else '🔍 Search for stores'}",
        type="primary",
        key="run_btn"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Status + Results ────────────────────────────────────────────────────────
    status_placeholder = st.empty()

    if run_btn:
        if not goal.strip() or not location.strip():
            st.warning("Please fill in what you're looking for and a location.")
        else:
            st.session_state.is_running = True
            st.session_state.results_df = None

            steps_events = [
                "Building search queries…",
                "Searching the web for events…",
                "Reading event pages…",
                "Extracting booth details…",
                "Formatting results…",
            ]
            steps_stores = [
                "Building search queries…",
                "Searching for stores in your area…",
                "Reading store listings…",
                "Classifying store types…",
                "Formatting results…",
            ]
            steps = steps_events if is_events else steps_stores

            for step in steps:
                update_status(status_placeholder, step, "running")
                time.sleep(0.6)

            # Call Layer 2
            results = run_agent(
                mode=st.session_state.mode,
                goal=goal,
                location=location,
                date_range=(date_from, date_to) if is_events else None,
            )

            df = pd.DataFrame(results)
            st.session_state.results_df = df
            st.session_state.is_running = False

            # Save to run history
            st.session_state.run_history.insert(0, {
                "mode": st.session_state.mode,
                "goal": goal,
                "location": location,
                "count": len(results),
                "timestamp": datetime.now().strftime("%b %d, %Y – %H:%M"),
                "df": df.copy()
            })

            update_status(
                status_placeholder,
                f"Done — {len(results)} {'events' if is_events else 'stores'} found",
                "done"
            )

    # ── Results table ───────────────────────────────────────────────────────────
    if st.session_state.results_df is not None:
        df = st.session_state.results_df
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        res_label = "events found" if is_events else "stores found"
        st.markdown(f"<span style='font-size:0.85rem;color:#B8D8C8;font-weight:500'>✦ {len(df)} {res_label} — click any cell to edit</span>", unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True,
            key="results_editor"
        )
        st.session_state.results_df = edited_df

        # Export row
        ex1, ex2, ex3 = st.columns([2, 2, 3])
        with ex1:
            csv = edited_df.to_csv(index=False).encode("utf-8")
            fname = f"{'events' if is_events else 'stores'}_{datetime.now().strftime('%Y%m%d')}.csv"
            st.download_button("⬇ Download CSV", csv, fname, "text/csv", key="dl_csv")
        with ex2:
            json_str = edited_df.to_json(orient="records", indent=2).encode("utf-8")
            st.download_button("⬇ Download JSON", json_str, fname.replace(".csv", ".json"), "application/json", key="dl_json")
        with ex3:
            if st.button("↑ Sync to Google Sheets", key="sync_sheets"):
                sync_to_sheets(edited_df, is_events)

# ── Right column: run history ───────────────────────────────────────────────────
with right_col:
    st.markdown("<div style='font-size:0.8rem;font-weight:600;color:#B8D8C8;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:12px'>Past searches</div>", unsafe_allow_html=True)

    if not st.session_state.run_history:
        st.markdown("<div style='font-size:0.85rem;color:#6DB89A;padding:12px 0'>No searches yet. Run your first search to see history here.</div>", unsafe_allow_html=True)
    else:
        for i, run in enumerate(st.session_state.run_history[:8]):
            mode_icon = "🗓" if run["mode"] == "events" else "🏪"
            label = f"{run['goal'][:28]}…" if len(run["goal"]) > 28 else run["goal"]
            if st.button(
                f"{mode_icon} {label}\n{run['count']} results · {run['location']}",
                key=f"hist_{i}",
                use_container_width=True,
            ):
                st.session_state.results_df = run["df"]
                st.rerun()

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.8rem;font-weight:600;color:#B8D8C8;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:12px'>Quick tips</div>", unsafe_allow_html=True)

    tips = [
        ("🗓", "Events", "Include the year in your search for accurate upcoming dates."),
        ("🏪", "Stores", "Run one search per store type for the best coverage."),
        ("✏️", "Editing", "Click any cell in the results table to correct a value before exporting."),
        ("⬇", "Export", "Download CSV to open in Excel, or JSON to feed into your CRM."),
    ]
    for icon, label, tip in tips:
        st.markdown(f"""
        <div style='margin-bottom:12px'>
          <div style='font-size:0.8rem;font-weight:600;color:#D8F0E4'>{icon} {label}</div>
          <div style='font-size:0.78rem;color:#B8D8C8;margin-top:2px;line-height:1.4'>{tip}</div>
        </div>
        """, unsafe_allow_html=True)