import streamlit as st
import pandas as pd

# Φόρτωση του Excel
file_path = "αστοχιες.xlsx.xlsx"  # βάλτο στην ίδια φάκελο με το script
df = pd.read_excel(file_path)

st.title("AI Agent για Αστοχίες Συντήρησης")

# Φιλτράρισμα με επιλογές
υπευθυνος = st.selectbox("Επιλέξτε Υπεύθυνο Ομάδας:", ["Όλοι"] + df['Υπεύθυνος Ομάδας'].dropna().unique().tolist())
sos_filter = st.checkbox("Μόνο SOS = Yes")

filtered_df = df.copy()

if υπευθυνος != "Όλοι":
    filtered_df = filtered_df[filtered_df['Υπεύθυνος Ομάδας'] == υπευθυνος]

if sos_filter:
    filtered_df = filtered_df[filtered_df['SOS'] == "Yes"]

# Εμφάνιση αποτελεσμάτων
st.write(f"Βρέθηκαν {len(filtered_df)} εγγραφές.")
st.dataframe(filtered_df[['Ημ/νία','Υπεύθυνος Ομάδας','Εγκατάσταση','Εργασία','Αστοχία','SOS','Προτεινόμενη Ενέργεια']])

# Αν υπάρχουν φωτογραφίες
if 'Φωτογραφία' in filtered_df.columns:
    st.subheader("Φωτογραφίες")
    for index, row in filtered_df.iterrows():
        if pd.notna(row['Φωτογραφία']):
            st.write(f"{row['Εγκατάσταση']} - {row['Αστοχία']}")
            st.image(row['Φωτογραφία'], use_column_width=True)

    st.divider()

    # ======================
    # 📋 ΠΙΝΑΚΑΣ
    # ======================

    st.subheader("Όλα τα Δεδομένα")
    st.dataframe(df)

else:
    st.info("Ανέβασε αρχείο Excel για να ξεκινήσεις")



