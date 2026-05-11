import streamlit as st
import json
import os

st.set_page_config(
    page_title="Nova",
    page_icon="💜",
    layout="wide"
)

# Création fichier users
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

# Charger users
with open("users.json", "r") as f:
    users = json.load(f)

# Session
if "logged" not in st.session_state:
    st.session_state.logged = False

# STYLE
st.markdown("""
<style>
.stButton button {
    height: 60px;
    font-size: 25px;
    border-radius: 20px;
}
</style>
""", unsafe_allow_html=True)

st.title("💜 NOVA")

# PAS CONNECTÉ
if not st.session_state.logged:

    menu = st.selectbox(
        "Choisir",
        ["Connexion", "Inscription"]
    )

    username = st.text_input("Nom utilisateur")
    password = st.text_input("Mot de passe", type="password")

    # INSCRIPTION
    if menu == "Inscription":

        if st.button("Créer compte"):

            if username in users:
                st.error("Nom déjà utilisé")

            else:
                users[username] = password

                with open("users.json", "w") as f:
                    json.dump(users, f)

                st.success("Compte créé")

    # CONNEXION
    else:

        if st.button("Connexion"):

            if username in users and users[username] == password:

                st.session_state.logged = True
                st.session_state.username = username
                st.rerun()

            else:
                st.error("Identifiants incorrects")

# CONNECTÉ
else:

    st.success(f"Bienvenue {st.session_state.username}")

    col1, col2 = st.columns(2)

    with col1:
        st.button("💬 IA TEXTE", use_container_width=True)

    with col2:
        st.button("🎤 IA VOCALE", use_container_width=True)

    if st.button("Déconnexion"):
        st.session_state.logged = False
        st.rerun()
