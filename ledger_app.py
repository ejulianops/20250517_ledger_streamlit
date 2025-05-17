import streamlit as st
from supabase import create_client, Client
from datetime import datetime

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
            data = {"date": str(date), "amount": amount, "note": note}
            supabase.table("ledger").insert(data).execute()
            st.success("Entry added to shared ledger!")

# Display entries
st.header("Shared Ledger")
entries = supabase.table("ledger").select("*").execute().data
if entries:
    st.dataframe(entries)
    st.metric("Total Entries", len(entries))
    st.metric("Total Amount", sum(e["amount"] for e in entries))
else:
    st.info("No entries yet.")