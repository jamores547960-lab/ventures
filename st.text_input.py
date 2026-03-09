import streamlit as st
import pandas as pd # Assuming you use pandas to handle data

# 1. Load your existing data from your database or CSV
# Replace this with your actual database fetching logic
existing_data = pd.read_csv('VenturePulse Pro.csv') 
company_list = existing_data['Venture Name'].unique().tolist()

# 2. Add an option to add a "New Venture" if it's not in the list
options = ["Select a Venture..."] + company_list + ["Add New Venture"]

# 3. Create the Dropdown
selected_venture = st.selectbox("Venture Name", options=options)

# 4. Logic to auto-fill features if a company is selected
if selected_venture != "Select a Venture..." and selected_venture != "Add New Venture":
    # Filter data for the selected company
    company_info = existing_data[existing_data['Venture Name'] == selected_venture].iloc[0]
    
    # Use these values as "value" or "placeholder" in your other inputs
    rd_val = company_info['R&D Investment']
    mkt_val = company_info['Marketing Spend']
else:
    rd_val = 0.0
    mkt_val = 0.0

# 5. Your existing input fields now use the variables from above
rd_investment = st.number_input("R&D Investment ($)", value=rd_val)
marketing_spend = st.number_input("Marketing Spend ($)", value=mkt_val)