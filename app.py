import streamlit as st
import json
import requests
from mistralai.client import Mistral
import base64

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Nova", page_icon="💜")

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]  # ex: "user/nova-db"

# ======================
# SESSION
# ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ======================
# GITHUB FUNCTIONS
# ======================
def save_chat_github(username, messages):

    path = f"chats/{username}.json"
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    content = json.dumps(messages, ensure_ascii=False, indent=2)
    encoded = base64.b64encode(content.encode()).decode()

    # check file exists
    r = requests.get(url, headers=headers)

    sha = None
    if r.status_code == 200:
        sha = r.json()["sha"]

    payload = {
        "message": f"update chat {username}",
        "content": encoded
    }

    if sha:
        payload["sha"] = sha

    requests.put(url, headers=headers, json=payload)

# ======================
# UI
# ======================
st.title("💜 Nova Auto Save GitHub")

username = st.text_input("Pseudo")

prompt = st.text_input("Message")

if st.button("Envoyer") and prompt and username:

    # add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # IA call
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

    # 🔥 AUTO SAVE GITHUB
    try:
        save_chat_github(username, st.session_state.messages)
        st.success("💾 Sauvegardé sur GitHub")
    except Exception as e:
        st.error(f"GitHub error: {e}")

    st.rerun()

# DISPLAY CHAT
for m in st.session_state.messages:
    st.write(f"**{m['role']} :** {m['content']}")
