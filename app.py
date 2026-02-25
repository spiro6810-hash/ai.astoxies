import streamlit as st
import pandas as pd

st.title("Maintenance AI Dashboard")

uploaded_file = st.file_uploader("Ανέβασε το αρχείο Excel", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    st.success("Το αρχείο φορτώθηκε επιτυχώς ✅")

    # ======================
    # 📊 ΣΤΑΤΙΣΤΙΚΑ
    # ======================

    st.subheader("Στατιστικά")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Σύνολο Αστοχιών", len(df))

    with col2:
        if "SOS" in df.columns:
            sos_count = df["SOS"].astype(str).str.upper().value_counts().get("ΝΑΙ", 0)
            st.metric("Σύνολο SOS", sos_count)

    with col3:
        if "Επισκευάστηκε" in df.columns:
            repaired = df["Επισκευάστηκε"].astype(str).str.upper().value_counts().get("ΝΑΙ", 0)
            st.metric("Επισκευασμένα", repaired)

    st.divider()

    # ======================
    # 📈 ΓΡΑΦΗΜΑΤΑ
    # ======================

    if "Εγκατάσταση" in df.columns:
        st.subheader("Πιο Συχνές Εγκαταστάσεις με Βλάβες")
        top_installations = df["Εγκατάσταση"].value_counts().head(10)
        st.bar_chart(top_installations)

    if "Αστοχία" in df.columns:
        st.subheader("Πιο Συχνές Αστοχίες")
        top_failures = df["Αστοχία"].value_counts().head(10)
        st.bar_chart(top_failures)

    st.divider()

    # ======================
    # 📋 ΠΙΝΑΚΑΣ
    # ======================

    st.subheader("Όλα τα Δεδομένα")
    st.dataframe(df)

else:
    st.info("Ανέβασε αρχείο Excel για να ξεκινήσεις")
