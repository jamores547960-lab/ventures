import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os


st.set_page_config(page_title="Venture Analytics Pro", layout="wide")
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")


st.sidebar.title("💎 Enterprise EVPD")
page = st.sidebar.selectbox("Navigate System", ["Executive Overview", "Venture Explorer", "Resource Entry"])

def get_data(path):
    try:
        r = requests.get(f"{API_URL}/{path}", timeout=5)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        return None


if page == "Executive Overview":
    st.title(" Executive Performance Summary")
    
    metrics = get_data("metrics")
    
    
    if metrics:
        m1, m2, m3, m4 = st.columns(4)
        total_p = metrics.get('total_profit', 0)
        avg_p = metrics.get('avg_profit', 0)
        eff = metrics.get('efficiency_ratio', 0)
        state = metrics.get('top_state', "N/A")
        
        m1.metric("Total Portfolio Profit", f"${total_p / 1e6:.1f}M")
        m2.metric("Avg. Venture Profit", f"${avg_p:,.0f}")
        m3.metric("Capital Efficiency", f"{eff}%")
        m4.metric("Leading Region", state)
    else:
        st.warning("⚠️ Metrics data unavailable. Please ensure the Backend is running and CSV is loaded.")

    st.markdown("---")
    
    data = get_data("ventures")
    if data:
        df = pd.DataFrame(data)
        if not df.empty:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Profitability vs. Investment Density")
                fig = px.scatter(df, x="rd_spend", y="profit", size="marketing_spend", color="state",
                                 template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.subheader("Regional Distribution")
                state_avg = df.groupby('state')['profit'].mean().reset_index()
                fig2 = px.pie(state_avg, values='profit', names='state', hole=0.5, template="plotly_dark")
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No records found in database.")

elif page == "Venture Explorer":
    st.title(" Data Explorer")
    data = get_data("ventures")
    if data:
        df = pd.DataFrame(data)
        if not df.empty:
            state_filter = st.sidebar.multiselect("Select States", df['state'].unique(), default=df['state'].unique())
            filtered_df = df[df['state'].isin(state_filter)]
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info("Database is currently empty.")


elif page == "Resource Entry":
    st.title("➕ Venture Capital Onboarding")
    with st.form("venture_form"):
        rd = st.number_input("R&D Budget", 0.0)
        adm = st.number_input("Administrative Overhead", 0.0)
        mkt = st.number_input("Marketing & Growth Spend", 0.0)
        profit = st.number_input("Reported Net Profit", 0.0)
        state = st.selectbox("Operating State", ["New York", "California", "Florida"])
        if st.form_submit_button("Submit"):
            payload = {"rd_spend": rd, "administration": adm, "marketing_spend": mkt, "state": state, "profit": profit}
            requests.post(f"{API_URL}/ventures", json=payload)
            st.success("Record Saved!")
            st.rerun()