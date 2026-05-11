import streamlit as st
import json
import os
from mistralai.client import Mistral

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Nova", page_icon="💜", layout="centered")

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

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

if "user" not in st.session_state:
    st.session_state.user = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

# ======================
# STYLE FIX CHAT
# ======================
st.markdown("""
<style>

.stApp {
    background-color: #0d0d0d;
    color: white;
}

/* zone chat */
.chat {
    max-width: 800px;
    margin: auto;
    padding-bottom: 120px;
}

/* USER */
.user {
    background: #7b2cbf;
    padding: 12px;
    border-radius: 18px;
    margin: 8px 0;
    text-align: left;
    width: fit-content;
    max-width: 80%;
}

/* BOT */
.bot {
    background: #1f1f1f;
    padding: 12px;
    border-radius: 18px;
    margin: 8px 0;
    text-align: left;
    width: fit-content;
    max-width: 80%;
}

h1 {
    text-align: center;
    color: #c77dff;
}

</style>
""", unsafe_allow_html=True)

st.title("💜 Nova")

# ======================
# LOGIN / REGISTER
# ======================
if not st.session_state.logged:

    mode = st.radio("Choisir", ["Connexion", "Inscription"])

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
                st.success("Compte créé ✔️")

    else:

        if st.button("Connexion"):

            if username in users and users[username] == password:
                st.session_state.logged = True
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Erreur connexion")

# ======================
# CHAT
# ======================
else:

    st.success(f"Bienvenue {st.session_state.user}")

    # CHAT DISPLAY
    st.markdown("<div class='chat'>", unsafe_allow_html=True)

    for msg in st.session_state.messages:

        if msg["role"] == "user":
            st.markdown(f"<div class='user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)

        else:
            st.markdown(f"<div class='bot'>💜 Nova : {msg['content']}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # INPUT
    prompt = st.text_input("Écris à Nova")

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

        except Exception as e:
            reply = f"⚠️ Erreur IA : {e}"

        st.session_state.messages.append({"role": "assistant", "content": reply})

        st.rerun()

    # LOGOUT
    if st.button("Déconnexion"):
        st.session_state.logged = False
        st.session_state.messages = []
        st.rerun()
