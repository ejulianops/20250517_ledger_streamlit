import streamlit as st
import pandas as pd
from datetime import datetime
import os

# App title
st.title("Personal Ledger App")

# Initialize session state for our ledger data
if 'ledger_data' not in st.session_state:
    st.session_state.ledger_data = pd.DataFrame(columns=['Date', 'Amount', 'Note'])
    
    # Try to load existing data if available
    if os.path.exists('ledger_data.csv'):
        st.session_state.ledger_data = pd.read_csv('ledger_data.csv', parse_dates=['Date'])

# Input form in sidebar
with st.sidebar:
    st.header("Add New Entry")
    with st.form("entry_form"):
        date = st.date_input("Date", datetime.today())
        amount = st.number_input("Amount", step=0.01, format="%.2f")
        note = st.text_input("Note")
        submitted = st.form_submit_button("Add Entry")
        
        if submitted:
            new_entry = pd.DataFrame([[date, amount, note]], 
                                   columns=['Date', 'Amount', 'Note'])
            st.session_state.ledger_data = pd.concat(
                [st.session_state.ledger_data, new_entry], 
                ignore_index=True
            )
            # Save to CSV
            st.session_state.ledger_data.to_csv('ledger_data.csv', index=False)
            st.success("Entry added successfully!")

# Main display area
st.header("Your Ledger")

# Show the data table
if not st.session_state.ledger_data.empty:
    st.dataframe(st.session_state.ledger_data.sort_values('Date', ascending=False))
    
    # Show summary statistics
    st.subheader("Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Entries", len(st.session_state.ledger_data))
    with col2:
        total_amount = st.session_state.ledger_data['Amount'].sum()
        st.metric("Total Amount", f"{total_amount:.2f}")
        
    # Simple visualization
    st.subheader("Amount Over Time")
    st.line_chart(st.session_state.ledger_data.set_index('Date')['Amount'].cumsum())
else:
    st.info("No entries yet. Add your first entry using the form in the sidebar.")