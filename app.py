import streamlit as st
import json
import requests
import base64
from mistralai.client import Mistral
from datetime import datetime

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Nova DB", page_icon="💜")

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]

# ======================
# HELPERS GITHUB
# ======================
def github_save(path, data):

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    content = json.dumps(data, ensure_ascii=False, indent=2)
    encoded = base64.b64encode(content.encode()).decode()

    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None

    payload = {
        "message": f"update {path}",
        "content": encoded
    }

    if sha:
        payload["sha"] = sha

    requests.put(url, headers=headers, json=payload)

def github_load(path):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        return None

    content = r.json()["content"]
    return json.loads(base64.b64decode(content).decode())

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

st.title("💜 Nova DB")

# ======================
# LOGIN / REGISTER
# ======================
if not st.session_state.logged:

    tab1, tab2, tab3 = st.tabs(["Login", "Register", "Admin"])

    # LOGIN
    with tab1:
        u = st.text_input("User")
        p = st.text_input("Pass", type="password")

        if st.button("Login"):
            user_data = github_load(f"users/{u}.json")

            if user_data and user_data["password"] == p:
                st.session_state.logged = True
                st.session_state.user = u

                chat = github_load(f"chats/{u}.json")
                if chat:
                    st.session_state.messages = chat["messages"]

                st.rerun()
            else:
                st.error("Wrong login")

    # REGISTER
    with tab2:
        u2 = st.text_input("New user")
        p2 = st.text_input("New pass", type="password")

        if st.button("Create"):

            github_save(f"users/{u2}.json", {
                "user": u2,
                "password": p2,
                "created": str(datetime.now())
            })

            github_save(f"chats/{u2}.json", {
                "messages": []
            })

            st.success("Account created")

    # ADMIN
    with tab3:
        admin_pass = st.text_input("Admin password", type="password")

        if st.button("Enter admin"):

            if admin_pass == "babar":
                st.session_state.logged = True
                st.session_state.user = "admin"
                st.rerun()
            else:
                st.error("Wrong")

# ======================
# APP
# ======================
else:

    st.success(f"User: {st.session_state.user}")

    # ======================
    # 👑 ADMIN PANEL
    # ======================
    if st.session_state.user == "admin":

        st.warning("ADMIN MODE")

        users_list = github_load("users")
        st.write(users_list)

    # ======================
    # CHAT DISPLAY
    # ======================
    for m in st.session_state.messages:
        if m["role"] == "user":
            st.markdown(f"<div class='user'>🧑 {m['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot'>💜 {m['content']}</div>", unsafe_allow_html=True)

    prompt = st.text_input("Message")

    if st.button("Send") and prompt:

        st.session_state.messages.append({"role": "user", "content": prompt})

        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role": "system", "content": "Tu es Nova, IA féminine douce."},
                *st.session_state.messages
            ]
        )

        reply = response.choices[0].message.content

        st.session_state.messages.append({"role": "assistant", "content": reply})

        # 🔥 SAVE CHAT (DERNIER EN PREMIER = OVERRIDE)
        github_save(f"chats/{st.session_state.user}.json", {
            "messages": st.session_state.messages[::-1]  # dernier en premier
        })

        st.rerun()

    # LOGOUT
    if st.button("Logout"):
        st.session_state.logged = False
        st.session_state.messages = []
        st.rerun()
