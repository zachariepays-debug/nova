import streamlit as st
import json
import requests
import base64

# ==========================
# CONFIGURATION & SECRETS
# ==========================
st.set_page_config(page_title="Nova", layout="centered")

# Ces clés doivent être dans tes Secrets Streamlit Cloud [cite: 10, 23, 24]
API_KEY = st.secrets["MISTRAL_API_KEY"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]
ADMIN_PASSWORD = "babar" # [cite: 5, 25]

# ==========================
# INITIALISATION SESSION
# ==========================
if "logged" not in st.session_state:
    st.session_state.logged = False # [cite: 30]
if "user" not in st.session_state:
    st.session_state.user = "" # [cite: 31]
if "messages" not in st.session_state:
    st.session_state.messages = [] # [cite: 33]
if "users" not in st.session_state:
    st.session_state.users = {} # [cite: 35]

# ==========================
# FONCTIONS TECHNIQUES
# ==========================
def ask_ai(messages): # [cite: 40]
    url = "https://api.mistral.ai/v1/chat/completions" # [cite: 41]
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-small-latest", # [cite: 47]
        "messages": messages
    }
    r = requests.post(url, headers=headers, json=payload) # [cite: 50]
    return r.json()["choices"][0]["message"]["content"] # [cite: 51]

def save_github(): # [cite: 55]
    path = f"chats/{st.session_state.user}.json" # [cite: 57]
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}" # [cite: 58]
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    
    # Encodage du contenu [cite: 63, 65]
    content = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
    encoded = base64.b64encode(content.encode()).decode()
    
    # Récupération du SHA pour la mise à jour [cite: 66, 67]
    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None
    
    data = {"message": "auto save nova", "content": encoded} # [cite: 71, 72]
    if sha: data["sha"] = sha # [cite: 74]
    
    requests.put(url, headers=headers, json=data) # [cite: 75]

# ==========================
# INTERFACE LOGIN / ADMIN
# ==========================
if not st.session_state.logged: # [cite: 91]
    st.title("💜 NOVA IA") # [cite: 1, 86]
    tab1, tab2, tab3 = st.tabs(["Login", "Register", "Admin"]) # [cite: 93]
    
    with tab1:
        u = st.text_input("User") # [cite: 95]
        p = st.text_input("Password", type="password") # [cite: 96]
        if st.button("Login"): # [cite: 97]
            if u in st.session_state.users and st.session_state.users[u] == p: # [cite: 98]
                st.session_state.logged = True # [cite: 100]
                st.session_state.user = u # [cite: 101]
                st.rerun() # [cite: 102]
            else:
                st.error("Échec de la connexion")

    with tab2:
        u2 = st.text_input("New user") # [cite: 103]
        p2 = st.text_input("New password", type="password") # [cite: 104]
        if st.button("Create"): # [cite: 105]
            st.session_state.users[u2] = p2 # [cite: 106]
            st.success("Compte créé") # [cite: 107]

    with tab3: # SECTION ADMIN [cite: 108]
        a = st.text_input("Admin password", type="password") # [cite: 111]
        if st.button("Enter"): # [cite: 112]
            if a == ADMIN_PASSWORD: # [cite: 113]
                st.session_state.logged = True # [cite: 114]
                st.session_state.user = "admin" # [cite: 115]
                st.rerun() # [cite: 116]
            else:
                st.error("Wrong password") # [cite: 118]

# ==========================
# APP PRINCIPALE
# ==========================
else:
    st.success(f"Connecté : {st.session_state.user}") # [cite: 123]
    
    if st.session_state.user == "admin": # [cite: 124]
        st.warning("⚠️ ADMIN MODE") # [cite: 125]
        st.write("Base de données utilisateurs :", st.session_state.users) # [cite: 126]

    # Affichage des messages [cite: 127]
    for m in st.session_state.messages:
        role = "👤" if m["role"] == "user" else "🤖 Nova:"
        st.markdown(f"{role} {m['content']}") # [cite: 128, 130]

    # Envoi de message [cite: 131]
    prompt = st.chat_input("Message") 
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt}) # [cite: 133]
        reply = ask_ai(st.session_state.messages) # [cite: 134]
        st.session_state.messages.append({"role": "assistant", "content": reply}) # [cite: 135]
        
        try:
            save_github() # [cite: 138]
        except:
            pass # [cite: 140]
        st.rerun() # [cite: 141]

    if st.button("Déconnexion"): # [cite: 142]
        st.session_state.logged = False # [cite: 143]
        st.session_state.messages = []
        st.rerun()
