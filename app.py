import streamlit as st
import json
import requests
import base64

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Nova", page_icon="💜")

MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
GITHUB_REPO = st.secrets.get("GITHUB_REPO", "")

# ======================
# SESSION
# ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "user" not in st.session_state:
    st.session_state.user = "default"

# ======================
# MISTRAL API (NO SDK)
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
        "message": "auto save nova",
        "content": encoded
    }

    if sha:
        payload["sha"] = sha

    requests.put(url, headers=headers, json=payload)

# ======================
# UI
# ======================
st.title("💜 Nova")

prompt = st.text_input("Message")

if st.button("Envoyer") and prompt:

    # user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # IA response
    try:
        reply = ask_mistral(st.session_state.messages)

    except Exception as e:
        reply = f"Erreur IA: {e}"

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    # 🔥 AUTO SAVE GITHUB
    try:
        save_github()
    except:
        pass

    st.rerun()

# ======================
# DISPLAY CHAT
# ======================
for m in st.session_state.messages:
    if m["role"] == "user":
        st.markdown(f"🧑 **Toi:** {m['content']}")
    else:
        st.markdown(f"💜 **Nova:** {m['content']}")
