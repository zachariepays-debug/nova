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
# CHAT SAVE
# ======================
def load_chat(user):
    file = f"chat_{user}.json"
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save_chat(user, messages):
    file = f"chat_{user}.json"
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
# STYLE SIMPLE & STABLE
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

    user = st.text_input("Nom utilisateur")
    pwd = st.text_input("Mot de passe", type="password")

    if mode == "Inscription":

        if st.button("Créer compte"):
            users[user] = pwd
            with open("users.json", "w") as f:
                json.dump(users, f)
            st.success("Compte créé")

    else:

        if st.button("Connexion"):

            if user in users and users[user] == pwd:
                st.session_state.logged = True
                st.session_state.user = user
                st.session_state.messages = load_chat(user)
                st.rerun()
            else:
                st.error("Erreur connexion")

# ======================
# APP
# ======================
else:

    st.success(f"Bienvenue {st.session_state.user}")

    if st.button("💬 Ouvrir Nova"):
        st.session_state.mode = "chat"

    # ======================
    # CHAT SIMPLE + STABLE
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
                    {"role": "system", "content": "Tu es Nova, une IA féminine douce, naturelle et utile."},
                    *st.session_state.messages
                ]
            )

            reply = response.choices[0].message.content

            st.session_state.messages.append({
                "role": "assistant",
                "content": reply
            })

            save_chat(st.session_state.user, st.session_state.messages)

        # AFFICHAGE CHAT
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"🧑‍💬 **Toi :** {msg['content']}")
            else:
                st.markdown(f"💜 **Nova :** {msg['content']}")

    # ======================
    # VOIX SIMPLE (SAFE)
    # ======================
    st.markdown("---")
    st.info("🎤 Voix : utilise le micro du téléphone (dictée clavier)")

    # LOGOUT
    if st.button("Déconnexion"):
        st.session_state.logged = False
        st.session_state.messages = []
        st.session_state.mode = None
        st.rerun()
