import streamlit as st
import json
import os
from mistralai.client import Mistral

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Nova", page_icon="💜", layout="wide")

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
# STYLE CHATGPT
# ======================
st.markdown("""
<style>

.stApp {
    background-color: #0d0d0d;
    color: white;
}

.chat {
    max-width: 800px;
    margin: auto;
    padding-bottom: 120px;
}

.user {
    background: #7b2cbf;
    padding: 12px;
    border-radius: 18px;
    margin: 8px 0;
    text-align: right;
}

.bot {
    background: #1f1f1f;
    padding: 12px;
    border-radius: 18px;
    margin: 8px 0;
}

input {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 60%;
    height: 50px;
    border-radius: 25px;
    padding: 10px;
}

</style>
""", unsafe_allow_html=True)

st.title("💜 Nova Chat")

# ======================
# LOGIN / INSCRIPTION
# ======================
if not st.session_state.logged:

    mode = st.radio("Choisir", ["Connexion", "Inscription"])

    username = st.text_input("Nom utilisateur")
    password = st.text_input("Mot de passe", type="password")

    # INSCRIPTION
    if mode == "Inscription":

        if st.button("Créer compte"):

            if username in users:
                st.error("Nom déjà utilisé")

            elif username == "" or password == "":
                st.error("Remplis tous les champs")

            else:
                users[username] = password

                with open("users.json", "w") as f:
                    json.dump(users, f)

                st.success("Compte créé ✔️")

    # CONNEXION
    else:

        if st.button("Connexion"):

            if username in users and users[username] == password:
                st.session_state.logged = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Erreur connexion")

# ======================
# CHAT
# ======================
else:

    st.success(f"Bienvenue {st.session_state.username}")

    st.markdown("<div class='chat'>", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot'>💜 Nova : {msg['content']}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    prompt = st.text_input("Message", label_visibility="collapsed")

    if st.button("Envoyer") and prompt:

        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            response = client.chat.complete(
                model="mistral-small-latest",
                messages=[
                    {"role": "system", "content": "Tu es Nova, une IA féminine douce et utile."},
                    *st.session_state.messages
                ]
            )

            reply = response.choices[0].message.content

        except:
            reply = "Erreur IA"

        st.session_state.messages.append({"role": "assistant", "content": reply})

        st.rerun()

    if st.button("Déconnexion"):
        st.session_state.logged = False
        st.session_state.messages = []
        st.rerun()
