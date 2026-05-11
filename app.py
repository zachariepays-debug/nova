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

# ⚠️ TA CLE API ICI
client = Mistral(api_key="TA_CLE_API_ICI")

# ======================
# USERS
# ======================
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

with open("users.json", "r") as f:
    users = json.load(f)

# ======================
# SESSION
# ======================
if "logged" not in st.session_state:
    st.session_state.logged = False

if "messages" not in st.session_state:
    st.session_state.messages = []

# ======================
# STYLE
# ======================
st.markdown("""
<style>
.stApp {
    background-color: #0d0d0d;
    color: white;
}

h1 {
    text-align: center;
    color: #c77dff;
}
</style>
""", unsafe_allow_html=True)

st.title("💜 NOVA")

# ======================
# LOGIN
# ======================
if not st.session_state.logged:

    mode = st.selectbox("Choisir", ["Connexion", "Inscription"])

    username = st.text_input("Nom utilisateur")
    password = st.text_input("Mot de passe", type="password")

    if mode == "Inscription":

        if st.button("Créer compte"):

            if username in users:
                st.error("Nom déjà utilisé")

            else:
                users[username] = password

                with open("users.json", "w") as f:
                    json.dump(users, f)

                st.success("Compte créé")

    else:

        if st.button("Connexion"):

            if username in users and users[username] == password:
                st.session_state.logged = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Erreur connexion")

# ======================
# APP
# ======================
else:

    st.success(f"Bienvenue {st.session_state.username}")

    user_input = st.text_input("Parle à Nova")

    if st.button("Envoyer") and user_input:

        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {"role": "system", "content": "Tu es Nova, une IA féminine douce et utile."},
                *st.session_state.messages
            ]
        )

        reply = response.choices[0].message.content

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply
        })

    # CHAT
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"🧑‍💬 {msg['content']}")
        else:
            st.markdown(f"💜 Nova : {msg['content']}")

    if st.button("Déconnexion"):
        st.session_state.logged = False
        st.session_state.messages = []
        st.rerun()
