import streamlit as st
import json
import requests
import base64
from mistralai.client import Mistral

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Nova", page_icon="💜", layout="centered")

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

ADMIN_PASSWORD = "babar"

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
GITHUB_REPO = st.secrets.get("GITHUB_REPO", "")

# ======================
# USERS
# ======================
if "users" not in st.session_state:
    if "users.json" in st.secrets:
        st.session_state.users = json.loads(st.secrets["users.json"])
    else:
        st.session_state.users = {}

# fallback simple local
try:
    with open("users.json", "r") as f:
        users = json.load(f)
except:
    users = {}

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
# SAVE TO GITHUB (AUTO)
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
# STYLE
# ======================
st.markdown("""
<style>
.stApp {
    background-color: #0d0d0d;
    color: white;
    font-family: Arial;
}

.user {
    background: #7b2cbf;
    padding: 10px;
    border-radius: 15px;
    margin: 5px;
    text-align: left;
    max-width: 80%;
}

.bot {
    background: #1f1f1f;
    padding: 10px;
    border-radius: 15px;
    margin: 5px;
    text-align: left;
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

    tab1, tab2, tab3 = st.tabs(["Connexion", "Inscription", "Admin"])

    with tab1:
        u = st.text_input("User")
        p = st.text_input("Password", type="password")

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
            st.success("Compte créé")

    with tab3:
        admin_pass = st.text_input("Admin password", type="password")

        if st.button("Enter admin"):
            if admin_pass == ADMIN_PASSWORD:
                st.session_state.logged = True
                st.session_state.user = "admin"
                st.rerun()
            else:
                st.error("Wrong password")

# ======================
# APP
# ======================
else:

    st.success(f"Connecté : {st.session_state.user}")

    # ADMIN PANEL
    if st.session_state.user == "admin":
        st.warning("👑 ADMIN MODE")
        st.write(users)

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
            response = client.chat.complete(
                model="mistral-small-latest",
                messages=[
                    {"role": "system", "content": "Tu es Nova, IA féminine douce et utile."},
                    *st.session_state.messages
                ]
            )

            reply = response.choices[0].message.content

        except Exception as e:
            reply = f"Erreur IA: {e}"

        st.session_state.messages.append({"role": "assistant", "content": reply})

        # 🔥 AUTO SAVE GITHUB
        try:
            save_github()
        except:
            pass

        st.rerun()

    # LOGOUT
    if st.button("Déconnexion"):
        st.session_state.logged = False
        st.session_state.messages = []
        st.rerun()
