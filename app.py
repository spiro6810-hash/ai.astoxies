import streamlit as st
import pandas as pd

st.set_page_config(page_title="Maintenance Dashboard (Offline)", layout="wide")

st.title("Maintenance Dashboard (Offline)")
st.caption("Upload Excel → φίλτρα → στατιστικά → offline agent για παρόμοιες αστοχίες (χωρίς OpenAI).")

uploaded_file = st.file_uploader("Ανέβασε το αρχείο Excel", type=["xlsx"])

if uploaded_file is None:
    st.info("Ανέβασε αρχείο Excel για να ξεκινήσεις.")
    st.stop()

# ======================
# 📥 Load data
# ======================
df = pd.read_excel(uploaded_file)

st.success("Το αρχείο φορτώθηκε ✅")

# ======================
# 🧹 Clean dates (αν υπάρχουν)
# ======================
if "Ημ/νία" in df.columns:
    df["Ημ/νία"] = pd.to_datetime(df["Ημ/νία"], errors="coerce")

if "Ημ/νία Επισκευής" in df.columns:
    df["Ημ/νία Επισκευής"] = pd.to_datetime(df["Ημ/νία Επισκευής"], errors="coerce")

# ======================
# 🎛 Sidebar filters
# ======================
st.sidebar.header("Φίλτρα")

filtered = df.copy()

# Φίλτρο Υπεύθυνος
if "Υπεύθυνος Ομάδας" in filtered.columns:
    people = sorted([x for x in filtered["Υπεύθυνος Ομάδας"].dropna().unique()])
    selected_people = st.sidebar.multiselect("Υπεύθυνος Ομάδας", people)
    if selected_people:
        filtered = filtered[filtered["Υπεύθυνος Ομάδας"].isin(selected_people)]

# Φίλτρο Ημερομηνίας
if "Ημ/νία" in filtered.columns and filtered["Ημ/νία"].notna().any():
    min_date = filtered["Ημ/νία"].min()
    max_date = filtered["Ημ/νία"].max()
    if pd.notnull(min_date) and pd.notnull(max_date):
        date_range = st.sidebar.date_input("Εύρος Ημερομηνίας", [min_date.date(), max_date.date()])
        if len(date_range) == 2:
            start = pd.to_datetime(date_range[0])
            end = pd.to_datetime(date_range[1])
            filtered = filtered[(filtered["Ημ/νία"] >= start) & (filtered["Ημ/νία"] <= end)]

# ======================
# 📊 Metrics
# ======================
st.subheader("Στατιστικά")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Σύνολο Εγγραφών", len(filtered))

with c2:
    if "SOS" in filtered.columns:
        sos_count = filtered["SOS"].astype(str).str.upper().eq("ΝΑΙ").sum()
        st.metric("SOS (ΝΑΙ)", int(sos_count))
    else:
        st.metric("SOS (ΝΑΙ)", "—")

with c3:
    if "Επισκευάστηκε" in filtered.columns:
        repaired = filtered["Επισκευάστηκε"].astype(str).str.upper().eq("ΝΑΙ").sum()
        st.metric("Επισκευασμένα (ΝΑΙ)", int(repaired))
    else:
        st.metric("Επισκευασμένα (ΝΑΙ)", "—")

with c4:
    # Μέσος χρόνος επισκευής σε ημέρες
    if "Ημ/νία" in filtered.columns and "Ημ/νία Επισκευής" in filtered.columns:
        temp = filtered.dropna(subset=["Ημ/νία", "Ημ/νία Επισκευής"]).copy()
        if len(temp) > 0:
            temp["Χρόνος (ημέρες)"] = (temp["Ημ/νία Επισκευής"] - temp["Ημ/νία"]).dt.days
            avg_days = temp["Χρόνος (ημέρες)"].mean()
            st.metric("Μ.Ο. Χρόνου Επισκευής (ημέρες)", round(float(avg_days), 2))
        else:
            st.metric("Μ.Ο. Χρόνου Επισκευής (ημέρες)", "—")
    else:
        st.metric("Μ.Ο. Χρόνου Επισκευής (ημέρες)", "—")

st.divider()

# ======================
# 📈 Charts
# ======================
left, right = st.columns(2)

with left:
    if "Εγκατάσταση" in filtered.columns:
        st.subheader("Top 10 Εγκαταστάσεις με Βλάβες")
        st.bar_chart(filtered["Εγκατάσταση"].value_counts().head(10))
    else:
        st.info("Δεν υπάρχει στήλη 'Εγκατάσταση'.")

with right:
    if "Αστοχία" in filtered.columns:
        st.subheader("Top 10 Αστοχίες")
        st.bar_chart(filtered["Αστοχία"].value_counts().head(10))
    else:
        st.info("Δεν υπάρχει στήλη 'Αστοχία'.")

st.divider()

# ======================
# 🧠 OFFLINE AGENT
# ======================
st.subheader("🧠 Offline Agent: Βρες παρόμοιες αστοχίες & πρόταση")

new_issue = st.text_area("Γράψε νέα αστοχία (περιγραφή)")
run = st.button("Ανάλυση (offline)")

if run:
    if not new_issue.strip():
        st.warning("Γράψε πρώτα μια περιγραφή αστοχίας.")
    elif "Αστοχία" not in df.columns:
        st.error("Δεν υπάρχει στήλη 'Αστοχία' στο αρχείο.")
    else:
        base = df.copy()
        base["Αστοχία"] = base["Αστοχία"].astype(str)

        # Απλή ομοιότητα λέξεων: Jaccard
        def similarity(a: str, b: str) -> float:
            a_set = set(a.lower().split())
            b_set = set(b.lower().split())
            if not a_set or not b_set:
                return 0.0
            return len(a_set & b_set) / len(a_set | b_set)

        base["_score"] = base["Αστοχία"].apply(lambda x: similarity(new_issue, x))
        top = base.sort_values("_score", ascending=False).head(10)

        st.markdown("### 🔎 Top 10 παρόμοιες περιπτώσεις από το ιστορικό")
        cols_show = [c for c in ["Ημ/νία", "Εγκατάσταση", "Εργασία", "Αστοχία", "SOS", "Προτεινόμενη Ενέργεια", "Επισκευάστηκε", "Τροχιά", "ΧΘ", "TrackID"] if c in top.columns]
        st.dataframe(top[cols_show])

        # Πρόταση ενέργειας από τις top περιπτώσεις
        suggestion = "Έλεγχος στο πεδίο και καταγραφή ευρημάτων."
        if "Προτεινόμενη Ενέργεια" in top.columns:
            actions = top["Προτεινόμενη Ενέργεια"].dropna().astype(str)
            if len(actions) > 0:
                suggestion = actions.value_counts().idxmax()

        # Εκτίμηση SOS από ιστορικό
        sos_guess = "ΟΧΙ"
        if "SOS" in top.columns:
            sos_yes = top["SOS"].astype(str).str.upper().eq("ΝΑΙ").sum()
            sos_guess = "ΝΑΙ" if sos_yes >= 3 else "ΟΧΙ"

        st.markdown("### ✅ Offline πρόταση")
        st.write(f"**Προτεινόμενη ενέργεια:** {suggestion}")
        st.write(f"**SOS (εκτίμηση από παρόμοια):** {sos_guess}")
        st.caption("Offline agent = αναζήτηση ομοιότητας + κανόνες. Δεν χρειάζεται OpenAI ούτε API.")

st.divider()

# ======================
# 📋 Data table
# ======================
st.subheader("Δεδομένα (με φίλτρα)")
st.dataframe(filtered)


