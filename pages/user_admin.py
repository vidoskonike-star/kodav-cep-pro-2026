import streamlit as st
from utils.user_manager import list_users, create_user, update_password, update_user, delete_user, get_user


st.set_page_config(page_title="Gestion des utilisateurs", page_icon="🔒", layout="wide")


if "authentication_status" not in st.session_state:
    st.error("Veuillez vous connecter")
    st.stop()

if not st.session_state["authentication_status"]:
    st.error("Accès refusé")
    st.stop()

if st.session_state.get("role") not in {"admin", "circonscription"}:
    st.error("Cette page est réservée aux administrateurs")
    st.stop()


st.title("🔒 Gestion des utilisateurs")

users = list_users()

st.subheader("Liste des utilisateurs")
cols = ["username", "name", "email", "role", "centre"]
table = []
for u, v in users.items():
    table.append({"username": u, "name": v.get("name", ""), "email": v.get("email", ""), "role": v.get("role", ""), "centre": v.get("centre", "")})

st.dataframe(table, use_container_width=True)

st.subheader("Modifier un utilisateur")
with st.form("edit_user"):
    sel = st.selectbox("Choisir utilisateur", [u for u in users.keys()])
    user = get_user(sel)
    new_name = st.text_input("Nom", value=user.get("name", ""))
    new_email = st.text_input("Email", value=user.get("email", ""))
    new_role = st.selectbox("Rôle", ["admin", "circonscription", "teacher"], index=["admin","circonscription","teacher"].index(user.get("role", "teacher")))
    new_centre = st.text_input("Centre", value=user.get("centre", ""))
    if st.form_submit_button("Enregistrer modifications"):
        try:
            update_user(sel, email=new_email, name=new_name, role=new_role, centre=new_centre, performed_by=st.session_state.get("username"))
            st.success("Utilisateur mis à jour")
            st.experimental_rerun()
        except Exception as e:
            st.error(str(e))

st.subheader("Changer mot de passe")
with st.form("change_password"):
    sel2 = st.selectbox("Choisir utilisateur pour mot de passe", [u for u in users.keys()], key="pw_sel")
    pwd = st.text_input("Nouveau mot de passe", type="password")
    if st.form_submit_button("Mettre à jour le mot de passe"):
        if not pwd:
            st.error("Mot de passe vide")
        else:
            try:
                update_password(sel2, pwd, performed_by=st.session_state.get("username"))
                st.success("Mot de passe mis à jour")
                st.experimental_rerun()
            except Exception as e:
                st.error(str(e))

st.subheader("Créer un nouvel utilisateur")
with st.form("create_user"):
    username = st.text_input("Identifiant (username)")
    name = st.text_input("Nom complet")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    role = st.selectbox("Rôle", ["teacher", "circonscription", "admin"])
    centre = st.text_input("Centre", value="CENTRE_PAR_DEFAUT")
    if st.form_submit_button("Créer"):
        if not username or not name or not email or not password:
            st.error("Tous les champs sont requis")
        else:
            try:
                create_user(username, email, name, password, role=role, centre=centre, performed_by=st.session_state.get("username"))
                st.success("Utilisateur créé")
                st.experimental_rerun()
            except Exception as e:
                st.error(str(e))

st.subheader("Supprimer un utilisateur")
with st.form("delete_user"):
    del_sel = st.selectbox("Choisir utilisateur à supprimer", [u for u in users.keys()], key="del_sel")
    confirm = st.checkbox("Je confirme la suppression de cet utilisateur")
    if st.form_submit_button("Supprimer"):
        if not confirm:
            st.error("Confirme la suppression")
        else:
            try:
                delete_user(del_sel, performed_by=st.session_state.get("username"))
                st.success("Utilisateur supprimé")
                st.experimental_rerun()
            except Exception as e:
                st.error(str(e))

if st.button("Retour à l'accueil"):
    st.switch_page("app.py")
