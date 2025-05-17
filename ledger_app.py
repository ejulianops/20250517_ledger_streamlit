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
        
        # In your form submission:
        if submitted and "user" in st.session_state:
            try:
                data = {
                    "date": str(date),
                    "amount": float(amount),
                    "note": str(note),
                    "user_id": st.session_state.user.user.id  # This is already UUID
                }
                response = supabase.table("ledger").insert(data).execute()
                st.success("Entry added!")
            except Exception as e:
                st.error(f"Error: {e}")

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

# Auth function
def login():
    with st.sidebar:
        st.header("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            try:
                user = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = user
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {e}")