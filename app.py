import streamlit as st
import json
import requests
import base64
from mistralai.client import Mistral

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Nova", page_icon="💜")

client = Mistral(api_key=st.secrets["MISTRAL_API_KEY"])

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
# SAVE GITHUB FUNCTION
# ======================
def save_to_github():

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
# UI
# ======================
st.title("💜 Nova Auto Save")

prompt = st.text_input("Message")

# ======================
# SEND MESSAGE
# ======================
if st.button("Envoyer") and prompt:

    # user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # IA response
    try:
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role": "system", "content": "Tu es Nova, une IA douce et utile."},
                *st.session_state.messages
            ]
        )

        reply = response.choices[0].message.content

    except Exception as e:
        reply = f"Erreur IA: {e}"

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    # 🔥 AUTO SAVE (IMPORTANT)
    try:
        save_to_github()
        st.success("💾 Sauvegardé automatiquement")
    except Exception as e:
        st.error(f"GitHub error: {e}")

    st.rerun()

# ======================
# DISPLAY CHAT
# ======================
for m in st.session_state.messages:
    st.write(f"**{m['role']} :** {m['content']}")
