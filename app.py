import streamlit as st
import json
import os
from mistralai import Mistral

# ======================
# CONFIG
# ======================
st.set_page_config(
    page_title="Nova",
    page_icon="💜",
    layout="centered"
)

# ⚠️ MET TA CLE MISTRAL ICI
client = Mistral(api_key="TA_CLE_API_ICI")

# ======================
# USERS SYSTEM
# ======================
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

with open("users.json", "r") as f:
    users = json.load(f)

# ======================
# SESSION STATE
# ======================
if "logged" not in st.session_state:
    st.session_state.logged = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "mode" not in st.session_state:
    st.session_state.mode = None

# ======================
# STYLE MOBILE
# ======================
st.markdown("""
<style>
.stApp {
    background-color: #0d0d0d;
    color: white;
}

h1 {
    text-align: center;
    font-size: 50px !important;
    color: #c77dff;
}

.stButton button {
    height: 140px;
    font-size: 28px !important;
    border-radius: 25px;
    background: linear-gradient(45deg,#7b2cbf,#c77dff);
    color: white;
    border: none;
}

input {
    height: 50px !important;
    font-size: 18px !important;
}
</style>
""", unsafe_allow_html=True)

# ======================
# TITLE
# ======================
st.title("💜 NOVA")

# ======================
# LOGIN / REGISTER
# ======================
if not st.session_state.logged:

    menu = st.selectbox("Choisir", ["Connexion", "Inscription"])

    username = st.text_input("Nom utilisateur")
    password = st.text_input("Mot de passe", type="password")

    # INSCRIPTION
    if menu == "Inscription":

        if st.button("Créer compte", use_container_width=True):

            if username in users:
                st.error("Nom déjà utilisé")

            elif username == "" or password == "":
                st.error("Remplis tous les champs")

            else:
                users[username] = password

                with open("users.json", "w") as f:
                    json.dump(users, f)

                st.success("Compte créé")

    # CONNEXION
    else:

        if st.button("Connexion", use_container_width=True):

            if username in users and users[username] == password:
                st.session_state.logged = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Identifiants incorrects")

# ======================
# APP PRINCIPALE
# ======================
else:

    st.success(f"Bienvenue {st.session_state.username}")

    # MENU
    if st.button("💬 IA TEXTE", use_container_width=True):
        st.session_state.mode = "chat"

    if st.button("🎤 IA VOCALE", use_container_width=True):
        st.info("Bientôt disponible 🔥")

    # ======================
    # CHAT IA
    # ======================
    if st.session_state.mode == "chat":

        st.subheader("💬 Nova IA")

        user_input = st.text_input("Parle à Nova")

        if st.button("Envoyer") and user_input:

            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })

            response = client.chat.complete(
                model="mistral-large-latest",
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es Nova, une IA féminine douce, naturelle et utile."
                    },
                    *st.session_state.messages
                ]
            )

            reply = response.choices[0].message.content

            st.session_state.messages.append({
                "role": "assistant",
                "content": reply
            })

        # AFFICHAGE
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"🧑‍💬 **Toi :** {msg['content']}")
            else:
                st.markdown(f"💜 **Nova :** {msg['content']}")

    # ======================
    # LOGOUT
    # ======================
    if st.button("Déconnexion"):
        st.session_state.logged = False
        st.session_state.messages = []
        st.session_state.mode = None
        st.rerun()
