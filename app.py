import streamlit as st
import json
import requests
import base64

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Nova", page_icon="💜", layout="centered")

MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
GITHUB_REPO = st.secrets.get("GITHUB_REPO", "")

ADMIN_PASSWORD = "babar"

# ======================
# USERS STORAGE LOCAL + GITHUB
# ======================
if "users" not in st.session_state:
    st.session_state.users = {}

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
# STYLE CHAT
# ======================
st.markdown("""
<style>
.stApp { background:#0d0d0d; color:white; }

.user {
    background:#7b2cbf;
    padding:10px;
    border-radius:15px;
    margin:5px;
    max-width:80%;
}

.bot {
    background:#1f1f1f;
    padding:10px;
    border-radius:15px;
    margin:5px;
    max-width:80%;
}
</style>
""", unsafe_allow_html=True)

st.title("💜 Nova")

# ======================
# MISTRAL API (SAFE)
# ======================
def ask_mistral(messages):

    url = "https://api.mistral.ai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistral-small-latest",
        "messages": messages
    }

    r = requests.post(url, headers=headers, json=payload)

    return r.json()["choices"][0]["message"]["content"]

# ======================
# GITHUB SAVE AUTO
# ======================
def save_github():

    if not GITHUB_TOKEN or not GITHUB_REPO:
        return

    path = f"chats/{st.session_state.user}.json"
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    content = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
    encoded = base64.b64encode(content.encode()).decode()

    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None

    payload = {
        "message": f"auto save {st.session_state.user}",
        "content": encoded
    }

    if sha:
        payload["sha"] = sha

    requests.put(url, headers=headers, json=payload)

# ======================
# LOGIN / REGISTER / ADMIN
# ======================
if not st.session_state.logged:

    tab1, tab2, tab3 = st.tabs(["Connexion", "Inscription", "Admin"])

    # LOGIN
    with tab1:
        u = st.text_input("User")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if u in st.session_state.users and st.session_state.users[u] == p:
                st.session_state.logged = True
                st.session_state.user = u
                st.rerun()

    # REGISTER
    with tab2:
        u2 = st.text_input("New user")
        p2 = st.text_input("New pass", type="password")

        if st.button("Create"):
            st.session_state.users[u2] = p2
            st.success("Compte créé")

    # ADMIN
    with tab3:
        admin = st.text_input("Admin password", type="password")

        if st.button("Enter admin"):
            if admin == ADMIN_PASSWORD:
                st.session_state.logged = True
                st.session_state.user = "admin"
                st.rerun()
            else:
                st.error("Wrong password")

# ======================
# APP PRINCIPALE
# ======================
else:

    st.success(f"Connecté : {st.session_state.user}")

    # 👑 ADMIN PANEL
    if st.session_state.user == "admin":
        st.warning("👑 ADMIN MODE")
        st.write("Users:", st.session_state.users)

    # CHAT DISPLAY
    for m in st.session_state.messages:
        if m["role"] == "user":
            st.markdown(f"<div class='user'>🧑 {m['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot'>💜 Nova: {m['content']}</div>", unsafe_allow_html=True)

    prompt = st.text_input("Message")

    if st.button("Envoyer") and prompt:

        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            reply = ask_mistral(st.session_state.messages)

        except Exception as e:
            reply = f"Erreur IA: {e}"

        st.session_state.messages.append({"role": "assistant", "content": reply})

        # 💾 SAVE AUTO GITHUB
        try:
            save_github()
        except:
            pass

        st.rerun()

    if st.button("Déconnexion"):
        st.session_state.logged = False
        st.session_state.messages = []
        st.rerun()
