import streamlit as st
import json
import os
from mistralai.client import Mistral

# ======================
# CONFIG
# ======================
st.set_page_config(
    page_title="Nova",
    page_icon="💜",
    layout="centered"
)

# ⚠️ TA CLE API MISTRAL
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
# MEMOIRE CHAT
# ======================
def load_chat(user):
    file = f"chats_{user}.json"
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save_chat(user, messages):
    file = f"chats_{user}.json"
    with open(file, "w") as f:
        json.dump(messages, f)

# ======================
# SESSION
# ======================
if "logged" not in st.session_state:
    st.session_state.logged = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "mode" not in st.session_state:
    st.session_state.mode = None

# ======================
# STYLE
# ======================
st.markdown("""
<style>

.stApp {
    background-color: #0d0d0d;
    color: white;
    font-family: Arial;
}

h1 {
    text-align: center;
    font-size: 48px !important;
    color: #c77dff;
}

/* BOUTONS BULLES */
.stButton > button {
    background: linear-gradient(135deg, #7b2cbf, #c77dff);
    color: white;
    border: none;
    border-radius: 50px;
    padding: 16px;
    font-size: 20px !important;
    width: 100%;
    margin-top: 10px;
}

/* INPUT */
input {
    height: 50px !important;
    font-size: 18px !important;
    border-radius: 15px;
}

/* CHAT BULLES */
.user-bubble {
    background: #7b2cbf;
    color: white;
    padding: 12px;
    border-radius: 20px;
    margin: 8px 0;
    text-align: right;
    max-width: 80%;
    margin-left: auto;
}

.ai-bubble {
    background: #222;
    color: white;
    padding: 12px;
    border-radius: 20px;
    margin: 8px 0;
    text-align: left;
    max-width: 80%;
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

                # 🔥 CHARGER MEMOIRE CHAT
                st.session_state.messages = load_chat(username)

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

        user_input = st.text_input("Écris à Nova")

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

            # 💾 SAUVEGARDE MEMOIRE
            save_chat(st.session_state.username, st.session_state.messages)

        # ======================
        # AFFICHAGE BULLES
        # ======================
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f"<div class='user-bubble'>🧑 {msg['content']}</div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"<div class='ai-bubble'>💜 Nova : {msg['content']}</div>",
                    unsafe_allow_html=True
                )

    # ======================
    # LOGOUT
    # ======================
    if st.button("Déconnexion"):
        st.session_state.logged = False
        st.session_state.messages = []
        st.session_state.mode = None
        st.rerun()
