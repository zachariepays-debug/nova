import streamlit as st
import json
import os
import requests
from mistralai.client import Mistral

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Nova PRO MAX", page_icon="💜", layout="centered")

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]  # ex: "user/nova-db"
GITHUB_FILE = "data.json"

ADMIN = "admin"

# ======================
# LOAD USERS
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
# GITHUB SAVE FUNCTION
# ======================
def save_to_github(data):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    # get old file sha
    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None

    payload = {
        "message": "update nova data",
        "content": json.dumps(data).encode("utf-8").decode("utf-8").encode("base64").decode("utf-8") if False else json.dumps(data),
    }

    if sha:
        payload["sha"] = sha

    requests.put(url, headers=headers, json=payload)

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

st.title("💜 Nova PRO MAX")

# ======================
# LOGIN
# ======================
if not st.session_state.logged:

    tab1, tab2 = st.tabs(["Connexion", "Inscription"])

    with tab1:
        u = st.text_input("User")
        p = st.text_input("Pass", type="password")

        if st.button("Login"):
            if u in users and users[u] == p:
                st.session_state.logged = True
                st.session_state.user = u
                st.rerun()

    with tab2:
        u2 = st.text_input("New user")
        p2 = st.text_input("New pass", type="password")

        if st.button("Register"):
            users[u2] = p2
            with open("users.json", "w") as f:
                json.dump(users, f)
            st.success("OK")

# ======================
# APP
# ======================
else:

    st.sidebar.write(f"👤 {st.session_state.user}")

    # ADMIN PANEL
    if st.session_state.user == ADMIN:
        st.sidebar.title("👑 ADMIN")
        st.sidebar.write(users)

    # EXPORT CHAT
    if st.sidebar.button("💾 Save GitHub"):
        save_to_github({
            "user": st.session_state.user,
            "messages": st.session_state.messages
        })
        st.sidebar.success("Saved!")

    # LOGOUT
    if st.sidebar.button("Logout"):
        st.session_state.logged = False
        st.session_state.messages = []
        st.rerun()

    # CHAT
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='user'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot'>💜 Nova: {msg['content']}</div>", unsafe_allow_html=True)

    # VOICE (DICTÉE)
    st.info("🎤 Vocal : utilise micro clavier (Chrome / mobile)")

    prompt = st.text_input("Message")

    if st.button("Send") and prompt:

        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            response = client.chat.complete(
                model="mistral-small-latest",
                messages=[
                    {"role": "system", "content": "Tu es Nova, IA féminine douce."},
                    *st.session_state.messages
                ]
            )

            reply = response.choices[0].message.content

        except Exception as e:
            reply = f"Erreur: {e}"

        st.session_state.messages.append({"role": "assistant", "content": reply})

        st.rerun()
