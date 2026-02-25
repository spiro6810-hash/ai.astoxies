import streamlit as st
import pandas as pd
import os
from openai import OpenAI
df = pd.read_excel(uploaded_file)
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

import streamlit as st
import pandas as pd

st.title("Maintenance AI Dashboard")

uploaded_file = st.file_uploader("Ανέβασε το αρχείο Excel", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    st.success("Το αρχείο φορτώθηκε επιτυχώς ✅")

    # ======================
    # 🧹 Καθαρισμός Ημερομηνιών
    # ======================

    if "Ημ/νία" in df.columns:
        df["Ημ/νία"] = pd.to_datetime(df["Ημ/νία"], errors="coerce")

    if "Ημ/νία Επισκευής" in df.columns:
        df["Ημ/νία Επισκευής"] = pd.to_datetime(df["Ημ/νία Επισκευής"], errors="coerce")

    # ======================
    # 🎛 ΦΙΛΤΡΑ
    # ======================

    st.sidebar.header("Φίλτρα")

    if "Υπεύθυνος Ομάδας" in df.columns:
        selected_team = st.sidebar.multiselect(
            "Υπεύθυνος Ομάδας",
            df["Υπεύθυνος Ομάδας"].dropna().unique()
        )
        if selected_team:
            df = df[df["Υπεύθυνος Ομάδας"].isin(selected_team)]

    if "Ημ/νία" in df.columns:
        min_date = df["Ημ/νία"].min()
        max_date = df["Ημ/νία"].max()

        if pd.notnull(min_date) and pd.notnull(max_date):
            date_range = st.sidebar.date_input(
                "Εύρος Ημερομηνίας",
                [min_date, max_date]
            )
            if len(date_range) == 2:
                df = df[(df["Ημ/νία"] >= pd.to_datetime(date_range[0])) &
                        (df["Ημ/νία"] <= pd.to_datetime(date_range[1]))]

    # ======================
    # 📊 ΣΤΑΤΙΣΤΙΚΑ
    # ======================

    st.subheader("Στατιστικά")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Σύνολο Αστοχιών", len(df))

    with col2:
        if "SOS" in df.columns:
            sos_count = df["SOS"].astype(str).str.upper().eq("ΝΑΙ").sum()
            st.metric("Σύνολο SOS", sos_count)

    with col3:
        if "Επισκευάστηκε" in df.columns:
            repaired = df["Επισκευάστηκε"].astype(str).str.upper().eq("ΝΑΙ").sum()
            st.metric("Επισκευασμένα", repaired)

    # ======================
    # ⏱ ΧΡΟΝΟΣ ΕΠΙΣΚΕΥΗΣ
    # ======================

    if "Ημ/νία" in df.columns and "Ημ/νία Επισκευής" in df.columns:
        df["Χρόνος Επισκευής (ημέρες)"] = (
            df["Ημ/νία Επισκευής"] - df["Ημ/νία"]
        ).dt.days

        avg_repair_time = df["Χρόνος Επισκευής (ημέρες)"].mean()

        if pd.notnull(avg_repair_time):
            st.metric("Μέσος Χρόνος Επισκευής (ημέρες)", round(avg_repair_time, 2))

    st.divider()

    # ======================
    # 📈 ΓΡΑΦΗΜΑΤΑ
    # ======================

    if "Εγκατάσταση" in df.columns:
        st.subheader("Top 10 Εγκαταστάσεις με Βλάβες")
        st.bar_chart(df["Εγκατάσταση"].value_counts().head(10))

    if "Αστοχία" in df.columns:
        st.subheader("Top 10 Αστοχίες")
        st.bar_chart(df["Αστοχία"].value_counts().head(10))

    st.divider()

    st.subheader("Δεδομένα")
    st.dataframe(df)
    st.divider()
st.subheader("🤖 AI Maintenance Agent")

new_issue = st.text_area("Περιέγραψε νέα αστοχία (π.χ. 'ρωγμή στην κεφαλή από νερά στο ΧΘ 05350')")

if new_issue:
    # Παίρνουμε λίγες σχετικές γραμμές για “γνώση” (context)
    cols = [c for c in ["Ημ/νία", "Εγκατάσταση", "Εργασία", "Αστοχία", "SOS", "Προτεινόμενη Ενέργεια"] if c in df.columns]
    context_data = df[cols].dropna(subset=["Αστοχία"]).head(25).to_string(index=False)

    prompt = f"""
Είσαι έμπειρος μηχανικός συντήρησης (AI Agent).
Με βάση το ιστορικό, αξιολόγησε τη νέα αστοχία και πρότεινε ενέργειες.

Ιστορικό (δείγμα):
{context_data}

Νέα αστοχία:
{new_issue}

Απάντησε στα Ελληνικά με μορφή:
1) Σύνοψη
2) Πιθανή αιτία
3) Προτεινόμενη ενέργεια (συγκεκριμένα βήματα)
4) SOS: ΝΑΙ/ΟΧΙ + γιατί
5) Προτεραιότητα: Χαμηλή/Μεσαία/Υψηλή
"""

    with st.spinner("Το AI αναλύει..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Είσαι βοηθός συντήρησης για ανάλυση αστοχιών."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

    st.success("AI Πρόταση")
    st.write(response.choices[0].message.content)

else:
    st.info("Ανέβασε αρχείο Excel για να ξεκινήσεις")


