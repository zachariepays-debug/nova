import streamlit as st
import json
import os
import requests
from mistralai.client import Mistral

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Nova Pro", page_icon="💜", layout="centered")

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

ADMIN = "admin"

# GitHub (OPTIONNEL mais inclus)
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
GITHUB_REPO = st.secrets.get("GITHUB_REPO", "")

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
# STYLE
# ======================
st.markdown("""
<style>
.stApp { background:#0d0d0d; color:white; }

.user {
    background:#7b2cbf;
    padding:10px;
    border-radius:15px;
    margin:5px;
    text-align:left;
    max-width:80%;
}

.bot {
    background:#1f1f1f;
    padding:10px;
    border-radius:15px;
    margin:5px;
    text-align:left;
    max-width:80%;
}
</style>
""", unsafe_allow_html=True)

st.title("💜 Nova Pro")

# ======================
# GITHUB SAVE
# ======================
def save_github(data):
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/chat_{st.session_state.user}.json"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }

    content = json.dumps(data)

    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None

    payload = {
        "message": "update chat nova",
        "content": content.encode("utf-8").decode("utf-8")
    }

    if sha:
        payload["sha"] = sha

    requests.put(url, headers=headers, json=payload)

# ======================
# LOGIN
# ======================
if not st.session_state.logged:

    mode = st.radio("Choisir", ["Connexion", "Inscription"])

    u = st.text_input("User")
    p = st.text_input("Pass", type="password")

    if mode == "Inscription":
        if st.button("Créer compte"):
            users[u] = p
            with open("users.json", "w") as f:
                json.dump(users, f)
            st.success("OK")

    else:
        if st.button("Login"):
            if u in users and users[u] == p:
                st.session_state.logged = True
                st.session_state.user = u
                st.rerun()

# ======================
# APP
# ======================
else:

    st.sidebar.write(f"👤 {st.session_state.user}")

    # ======================
    # 👑 ADMIN
    # ======================
    if st.session_state.user == ADMIN:
        st.sidebar.title("👑 ADMIN PANEL")
        st.sidebar.write(users)

    # ======================
    # 💾 SAVE GITHUB
    # ======================
    if st.sidebar.button("💾 Sauvegarder GitHub"):
        save_github({
            "user": st.session_state.user,
            "messages": st.session_state.messages
        })
        st.sidebar.success("Sauvegardé")

    # ======================
    # 🎤 VOCAL (DICTÉE INFO)
    # ======================
    st.sidebar.info("🎤 Vocal : utilise micro clavier (mobile / Chrome)")

    # ======================
    # CHAT
    # ======================
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot'>💜 Nova: {msg['content']}</div>", unsafe_allow_html=True)

    prompt = st.text_input("Message")

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

        except Exception as e:
            reply = f"Erreur IA: {e}"

        st.session_state.messages.append({"role": "assistant", "content": reply})

        st.rerun()

    # LOGOUT
    if st.button("Déconnexion"):
        st.session_state.logged = False
        st.session_state.messages = []
        st.rerun()
