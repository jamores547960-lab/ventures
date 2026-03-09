import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="VenturePulse Pro", layout="wide", page_icon="💎")

# --- CUSTOM CSS FOR HORIZONTAL NAVBAR ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }

    /* Hide the default Streamlit header, toolbar, and footer */
    header[data-testid="stHeader"] { display: none !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stToolbar"] { display: none !important; }
    .block-container { padding-top: 1rem !important; }
    
    /* Hide the default Streamlit Sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }

    /* Plain Header Styling */
    .nav-container {
        background-color: #0e1117;
        padding: 10px;
        border-bottom: none;
        margin-bottom: 20px;
    }

    /* Style the horizontal navigation */
    div[data-testid="stHorizontalBlock"] div[data-testid="stVerticalBlock"] > div:nth-child(2) div[role="radiogroup"] {
        justify-content: center;
        gap: 30px;
    }
    
    /* Metric Styling */
    div[data-testid="stMetricValue"] { font-size: 24px; color: #00d4ff; }
    
    /* Button Styling */
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3em; 
        background-color: #238636; 
        color: white; 
        border: none;
        transition: 0.2s ease-in-out;
    }
    .stButton>button:hover { 
        background-color: #2ea043; 
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE LOGIC ---
DB_NAME = "startup_hub.db" 

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS venture_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venture_name TEXT,
            rd_spend REAL,
            administration REAL,
            marketing_spend REAL,
            state TEXT,
            profit REAL
        )
    ''')
    conn.commit()
    conn.close()

def get_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM venture_records", conn)
    conn.close()
    return df

init_db()
df = get_data() 

# --- HORIZONTAL HEADER NAVIGATION ---
st.markdown('<div class="nav-container">', unsafe_allow_html=True)
col_logo, col_nav, col_status = st.columns([1, 2, 1])

with col_logo:
    st.markdown('<p style="font-size: 22px; font-weight: 800; color: #f0f6fc; margin: 0;">💎 VENTURE PULSE</p>', unsafe_allow_html=True)
    st.caption("Enterprise Analytics v3.0")
    
with col_nav:
    # Tab-style navigation bar
    menu = st.radio(
        "Navigation",
        ["📊 Dashboard", "🗂️ Explorer", "➕ Add Entry"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
with col_status:
    if not df.empty:
        st.markdown(f'<p style="text-align: right; color: #238636; font-weight: bold; margin-top: 10px;">● Online: {len(df)} Ventures</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="text-align: right; color: #8b949e; font-weight: bold; margin-top: 10px;">○ System Offline</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# --- DASHBOARD PAGE ---
if menu == "📊 Dashboard":
    st.title("Portfolio Overview")
    if not df.empty:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Profit", f"${df['profit'].sum():,.2f}")
        m2.metric("Total R&D", f"${df['rd_spend'].sum():,.2f}")
        m3.metric("Avg Profit", f"${df['profit'].mean():,.2f}")
        m4.metric("Total Records", len(df))

        st.markdown("---")
        c1, c2 = st.columns([2, 1])
        with c1:
            fig = px.bar(df, x="venture_name", y="profit", color="state", 
                         title="Profit Performance by Venture", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = px.pie(df, values='profit', names='state', title="Regional Profit Share", hole=0.4, template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.subheader("📈 Venture Success Probability Analysis")
        avg_p = df['profit'].mean()
        df['is_success'] = (df['profit'] > avg_p).astype(int)
        fig3 = px.scatter(df, x="rd_spend", y="is_success", labels={"is_success": "Success Prob", "rd_spend": "R&D Spend ($)"}, template="plotly_dark")
        
        if len(df) > 1:
            x_range = np.linspace(df['rd_spend'].min() * 0.8, df['rd_spend'].max() * 1.2, 100)
            midpoint = df['rd_spend'].median()
            scale = df['rd_spend'].std() if df['rd_spend'].std() != 0 else 1
            y_curve = 1 / (1 + np.exp(-(x_range - midpoint) / (scale/2)))
            fig3.add_trace(go.Scatter(x=x_range, y=y_curve, name='Probability Curve', line=dict(color='#ffffff', width=2)))
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("The database is empty. Add a venture to begin.")

# --- DATA EXPLORER PAGE ---
elif menu == "🗂️ Explorer":
    st.title("Venture Database")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("📥 Download Report (CSV)", df.to_csv(index=False), "venture_report.csv")
    else:
        st.warning("No data found.")

# --- ADD ENTRY PAGE ---
elif menu == "➕ Add Entry":
    st.title("Onboard New Venture")
    
    # --- REGISTER NEW NAME SECTION (RE-INSERTED) ---
    with st.expander("✨ Register New Company Name to Dropdown List"):
        st.write("If the company isn't in the list yet, add it here first.")
        new_company_name = st.text_input("New Company Name", placeholder="e.g. Wayne Enterprises")
        if st.button("Add to Dropdown List"):
            if new_company_name:
                csv_path = '1000_Companies.csv'
                if os.path.exists(csv_path):
                    temp_df = pd.read_csv(csv_path)
                    if 'Company' not in temp_df.columns: temp_df['Company'] = "Unknown"
                    
                    if new_company_name not in temp_df['Company'].values:
                        new_row = {'R&D Spend': 0, 'Administration': 0, 'Marketing Spend': 0,
                                   'State': 'New York', 'Profit': 0, 'Company': new_company_name}
                        temp_df = pd.concat([temp_df, pd.DataFrame([new_row])], ignore_index=True)
                        temp_df.to_csv(csv_path, index=False)
                        st.success(f"'{new_company_name}' registered! Reloading...")
                        st.rerun()
                    else:
                        st.warning("This company already exists.")
                else:
                    st.error("CSV file not found.")

    st.markdown("---")

    # Dropdown Logic
    csv_file = "1000_Companies.csv"
    if os.path.exists(csv_file):
        source_df = pd.read_csv(csv_file)
        if 'Company' not in source_df.columns: source_df['Company'] = "Unknown"
        venture_list = sorted(source_df['Company'].dropna().unique().tolist())
    else:
        venture_list = []

    selected_option = st.selectbox("Search & Select Venture Name", options=["-- Manual Entry --"] + venture_list)

    if selected_option != "-- Manual Entry --":
        row = source_df[source_df['Company'] == selected_option].iloc[0]
        d_rd, d_adm, d_mkt, d_profit, d_state = float(row.get('R&D Spend', 0)), float(row.get('Administration', 0)), float(row.get('Marketing Spend', 0)), float(row.get('Profit', 0)), row.get('State', 'New York')
    else:
        d_rd, d_adm, d_mkt, d_profit, d_state = 0.0, 0.0, 0.0, 0.0, "New York"

    with st.form("entry_form", clear_on_submit=True):
        name = st.text_input("Venture Name Confirmation", value="" if selected_option == "-- Manual Entry --" else selected_option)
        col1, col2 = st.columns(2)
        rd = col1.number_input("R&D Investment ($)", value=d_rd)
        adm = col1.number_input("Administrative Cost ($)", value=d_adm)
        mkt = col2.number_input("Marketing Spend ($)", value=d_mkt)
        profit = col2.number_input("Target Profit ($)", value=d_profit)
        state = st.selectbox("Operating State", ["New York", "California", "Florida"])
        
        if st.form_submit_button("SUBMIT TO DATABASE"):
            if name:
                conn = sqlite3.connect(DB_NAME); cursor = conn.cursor()
                cursor.execute('INSERT INTO venture_records (venture_name, rd_spend, administration, marketing_spend, state, profit) VALUES (?, ?, ?, ?, ?, ?)', (name, rd, adm, mkt, state, profit))
                conn.commit(); conn.close()
                st.markdown(
                    f"""
                    <div style="
                        background-color: #0d3320;
                        border: 1px solid #238636;
                        border-radius: 8px;
                        padding: 16px 20px;
                        margin-top: 10px;
                        display: flex;
                        align-items: center;
                        gap: 10px;
                    ">
                        <span style="font-size: 22px;">✅</span>
                        <div>
                            <p style="margin: 0; color: #3fb950; font-weight: 700; font-size: 16px;">
                                Submitted to database successfully!
                            </p>
                            <p style="margin: 0; color: #8b949e; font-size: 13px;">
                                '{name}' has been added to the portfolio.
                            </p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.balloons()
            else: st.error("Name required")

# --- ADMIN CONSOLE ---
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("🛠️ ADMIN CONSOLE"):
    c1, c2 = st.columns(2)
    if c1.button(" Wipe All Records"):
        conn = sqlite3.connect(DB_NAME); conn.execute("DELETE FROM venture_records"); conn.commit(); conn.close()
        st.rerun()
    if c2.button(" Reset Database"):
        if os.path.exists(DB_NAME): os.remove(DB_NAME); st.rerun()