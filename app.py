import streamlit as st
import pandas as pd

# Τίτλος
st.title("Αστοχίες Σιδηροδρομικής Υποδομής")

# Φόρτωσε το Excel
df = pd.read_excel("αστοχιες.xlsx")

# Φίλτρα
st.sidebar.header("Φίλτρα")
date_filter = st.sidebar.date_input("Ημερομηνία")
responsible_filter = st.sidebar.selectbox("Υπεύθυνος Ομάδας", ["Όλοι"] + sorted(df['Υπεύθυνος Ομάδας'].dropna().unique()))
installation_filter = st.sidebar.selectbox("Εγκατάσταση", ["Όλες"] + sorted(df['Εγκατάσταση'].dropna().unique()))

# Εφαρμογή φίλτρων
filtered_df = df.copy()

if responsible_filter != "Όλοι":
    filtered_df = filtered_df[filtered_df['Υπεύθυνος Ομάδας'] == responsible_filter]

if installation_filter != "Όλες":
    filtered_df = filtered_df[filtered_df['Εγκατάσταση'] == installation_filter]

# Εμφάνιση πίνακα
st.dataframe(filtered_df)

# Προβολή φωτογραφιών (αν υπάρχει)
if 'Φωτογραφία' in filtered_df.columns:
    for idx, row in filtered_df.iterrows():
        if pd.notna(row['Φωτογραφία']):
            st.write(f"**{row['Εγκατάσταση']}** - {row['Ημ/νία']}")
            st.image(row['Φωτογραφία'], width=400)