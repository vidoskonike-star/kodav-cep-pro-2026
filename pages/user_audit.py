import streamlit as st
from utils.audit import read_logs
import pandas as pd


st.set_page_config(page_title="Journal des actions utilisateurs", page_icon="📋", layout="wide")

if "authentication_status" not in st.session_state:
    st.error("Veuillez vous connecter")
    st.stop()

if not st.session_state["authentication_status"]:
    st.error("Accès refusé")
    st.stop()

if st.session_state.get("role") not in {"admin", "circonscription"}:
    st.error("Cette page est réservée aux administrateurs")
    st.stop()

st.title("📋 Journal des actions des utilisateurs")

logs = read_logs()
if not logs:
    st.info("Aucun événement enregistré.")
else:
    df = pd.DataFrame(logs)
    df = df.sort_values("timestamp", ascending=False)
    st.dataframe(df, use_container_width=True, height=600)

if st.button("Retour à l'accueil"):
    st.switch_page("app.py")
