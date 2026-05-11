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

/* fond */
.stApp {
    background-color: #0d0d0d;
    color: white;
}

/* zone chat */
.chat-container {
    max-width: 800px;
    margin: auto;
    padding-bottom: 120px;
}

/* bulles user */
.user {
    background: #7b2cbf;
    padding: 12px 16px;
    border-radius: 18px;
    margin: 10px 0;
    text-align: right;
}

/* bulles IA */
.bot {
    background: #1f1f1f;
    padding: 12px 16px;
    border-radius: 18px;
    margin: 10px 0;
    text-align: left;
}

/* input en bas */
input {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 60%;
    height: 50px;
    border-radius: 25px;
    padding: 10px;
    border: none;
    font-size: 16px;
}

/* bouton envoyer */
.stButton {
    position: fixed;
    bottom: 20px;
    right: 18%;
}

</style>
""", unsafe_allow_html=True)

st.title("💜 Nova Chat")

# ======================
# LOGIN SIMPLE
# ======================
if not st.session_state.logged:

    u = st.text_input("Nom")
    p = st.text_input("Mot de passe", type="password")

    if st.button("Connexion"):

        if u in users and users[u] == p:
            st.session_state.logged = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("Erreur")

# ======================
# CHAT STYLE GPT
# ======================
else:

    st.markdown("## 💬 Discussion avec Nova")

    # DISPLAY CHAT
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot'>💜 Nova : {msg['content']}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # INPUT
    prompt = st.text_input("Message", label_visibility="collapsed")

    if st.button("Envoyer") and prompt:

        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            response = client.chat.complete(
                model="mistral-small-latest",
                messages=[
                    {"role": "system", "content": "Tu es Nova, une IA féminine douce."},
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
