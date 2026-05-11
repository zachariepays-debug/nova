import streamlit as st
import json
import os
from mistralai import Mistral

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Nova Ultra Pro", page_icon="💜", layout="wide")

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

ADMIN = "admin"

# ======================
# DATA USERS
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

if "user" not in st.session_state:
    st.session_state.user = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

# ======================
# STYLE CHATGPT PRO
# ======================
st.markdown("""
<style>
body {
    background-color: #0d0d0d;
}

.stApp {
    background-color: #0d0d0d;
    color: white;
}

.chat-box {
    max-width: 850px;
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

.title {
    text-align: center;
    color: #c77dff;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='title'>💜 Nova Ultra Pro</h1>", unsafe_allow_html=True)

# ======================
# LOGIN / REGISTER
# ======================
if not st.session_state.logged:

    tab1, tab2 = st.tabs(["Connexion", "Inscription"])

    with tab1:
        u = st.text_input("Utilisateur")
        p = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            if u in users and users[u] == p:
                st.session_state.logged = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Erreur login")

    with tab2:
        u2 = st.text_input("Nouveau user")
        p2 = st.text_input("Nouveau pass", type="password")

        if st.button("Créer compte"):
            if u2 in users:
                st.error("Existe déjà")
            else:
                users[u2] = p2
                with open("users.json", "w") as f:
                    json.dump(users, f)
                st.success("Compte créé")

# ======================
# APP
# ======================
else:

    st.sidebar.title("⚙️ Panel")

    st.sidebar.write(f"Connecté: {st.session_state.user}")

    # ADMIN
    if st.session_state.user == ADMIN:
        st.sidebar.warning("ADMIN MODE")
        st.sidebar.write(users)

    # EXPORT CHAT
    if st.sidebar.button("📁 Export chat"):
        txt = ""
        for m in st.session_state.messages:
            txt += f"{m['role']}: {m['content']}\n"

        st.sidebar.download_button("Télécharger", txt, "nova_chat.txt")

    # LOGOUT
    if st.sidebar.button("Déconnexion"):
        st.session_state.logged = False
        st.session_state.messages = []
        st.rerun()

    # ======================
    # CHAT UI
    # ======================
    st.markdown("<div class='chat-box'>", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot'>💜 Nova : {msg['content']}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ======================
    # VOIX INFO
    # ======================
    st.info("🎤 Vocal : utilise dictée vocale du téléphone / Chrome (clic micro clavier)")

    # INPUT
    prompt = st.text_input("Écris à Nova")

    if st.button("Envoyer") and prompt:

        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            response = client.chat.complete(
                model="mistral-small-latest",
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es Nova, une IA féminine douce, intelligente et naturelle."
                    },
                    *st.session_state.messages
                ]
            )

            reply = response.choices[0].message.content

        except Exception as e:
            reply = f"⚠️ Erreur IA: {e}"

        st.session_state.messages.append({"role": "assistant", "content": reply})

        st.rerun()
