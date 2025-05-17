import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# App title
st.title("Joint Ledger App (Supabase)")

# Input form
with st.sidebar:
    st.header("Add New Entry")
    with st.form("entry_form"):
        date = st.date_input("Date", datetime.today())
        amount = st.number_input("Amount", step=0.01, format="%.2f")
        note = st.text_input("Note")
        submitted = st.form_submit_button("Add Entry")
        
        if submitted:
            try:
                data = {"date": str(date), "amount": float(amount), "note": str(note)}
                response = supabase.table("ledger").insert(data).execute()
                if response.data:
                    st.success("Entry added to shared ledger!")
                else:
                    st.error("Failed to add entry")
            except Exception as e:
                st.error(f"Error adding entry: {str(e)}")

# Display entries
st.header("Shared Ledger")
try:
    response = supabase.table("ledger").select("*").execute()
    entries = pd.DataFrame(response.data) if response.data else pd.DataFrame()
    
    if not entries.empty:
        # Convert date string to datetime for proper sorting
        entries['date'] = pd.to_datetime(entries['date'])
        # Sort by date (newest first)
        entries = entries.sort_values('date', ascending=False)
        # Convert back to date-only format for display
        entries['date'] = entries['date'].dt.date
        
        st.dataframe(entries)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Entries", len(entries))
        with col2:
            total = entries['amount'].sum()
            st.metric("Total Amount", f"${total:,.2f}")
    else:
        st.info("No entries yet. Add your first entry above.")
        
except Exception as e:
    st.error(f"Error loading entries: {str(e)}")