import streamlit as st
import pandas as pd

# Τίτλος
st.title("Αστοχίες Σιδηροδρομικής Υποδομής")

# Φόρτωσε το Excel
df = pd.read_excel("Full_Anafres_Epitheorisis_Correct.xlsx")
import streamlit as st
import pandas as pd

st.title("Maintenance AI - Ανάλυση Αστοχιών")

df = pd.read_excel("Full_Anafres_Epitheorisis_Correct.xlsx")

st.subheader("Στατιστικά")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Σύνολο Αστοχιών", len(df))

with col2:
    if "SOS" in df.columns:
        st.metric("Σύνολο SOS", df["SOS"].sum())

with col3:
    if "Επισκευάστηκε" in df.columns:
        completed = df[df["Επισκευάστηκε"] == "ΝΑΙ"]
        st.metric("Επισκευασμένα", len(completed))

st.divider()

st.subheader("Πιο Συχνές Εγκαταστάσεις με Βλάβες")
top_installations = df["Εγκατάσταση"].value_counts().head(10)
st.bar_chart(top_installations)

st.subheader("Πιο Συχνές Αστοχίες")
top_failures = df["Αστοχία"].value_counts().head(10)
st.bar_chart(top_failures)

st.divider()

st.subheader("Όλα τα Δεδομένα")
st.dataframe(df)
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

