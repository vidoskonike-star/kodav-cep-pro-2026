import streamlit as st

def load_css():

    st.markdown("""
    <style>

/* BACKGROUND GLOBAL */
.stApp {
    background: linear-gradient(rgba(0,0,0,0.55), rgba(0,0,0,0.55)),
                url("background.jpg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* TITRES */
h1, h2, h3 {
    color: white;
    font-weight: 700;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: rgba(0,0,0,0.75);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* CARDS */
.card {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 20px;
    backdrop-filter: blur(10px);
    color: white;
    box-shadow: 0px 0px 20px rgba(0,0,0,0.2);
}

/* BOUTONS */
div.stButton > button {
    background: linear-gradient(90deg, #0072ff, #00c6ff);
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: 700;
    transition: 0.3s;
}

div.stButton > button:hover {
    transform: scale(1.03);
    box-shadow: 0px 0px 15px rgba(0,114,255,0.6);
}

    </style>
    """, unsafe_allow_html=True)