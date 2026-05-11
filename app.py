import streamlit as st
import json
import requests
import base64

# ==========================
# CONFIGURATION
# ==========================
st.set_page_config(page_title="Nova", layout="centered")

# Récupération des secrets (à configurer dans Streamlit Cloud)
API_KEY = st.secrets["MISTRAL_API_KEY"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]
ADMIN_PASSWORD = "babar"

# ==========================
# GESTION DE LA SESSION
# ==========================
if "logged" not in st.session_state:
    st.session_state.logged = False
if "user" not in st.session_state:
    st.session_state.user = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "users" not in st.session_state:
    st.session_state.users = {}

# ==========================
# FONCTIONS IA (MISTRAL API)
# ==========================
def ask_ai(messages):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-small-latest",
        "messages": messages
    }
    try:
        r = requests.post(url, headers=headers, json=payload)
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Erreur API : {e}"

# ==========================
# SAUVEGARDE GITHUB
# ==========================
def save_github():
    path = f"chats/{st.session_state.user}.json"
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    
    # Préparation du contenu
    content = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
    encoded = base64.b64encode(content.encode()).decode()
    
    # Vérifier si le fichier existe déjà pour récupérer son SHA
    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None
    
    data = {
        "message": f"Backup chat for {st.session_state.user}",
        "content": encoded
    }
    if sha:
        data["sha"] = sha
        
    requests.put(url, headers=headers, json=data)

# ==========================
# INTERFACE UTILISATEUR
# ==========================
if not st.session_state.logged:
    st.title("Nova IA - Connexion")
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])
    
    with tab1:
        u = st.text_input("Nom d'utilisateur", key="login_user")
        p = st.text_input("Mot de passe", type="password", key="login_pass")
        if st.button("Se connecter"):
            if u == "admin" and p == ADMIN_PASSWORD:
                st.session_state.logged = True
                st.session_state.user = "admin"
                st.rerun()
            elif u in st.session_state.users and st.session_state.users[u] == p:
                st.session_state.logged = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Identifiants incorrects")
                
    with tab2:
        new_u = st.text_input("Choisir un pseudo", key="reg_user")
        new_p = st.text_input("Choisir un mot de passe", type="password", key="reg_pass")
        if st.button("Créer un compte"):
            if new_u and new_p:
                st.session_state.users[new_u] = new_p
                st.success("Compte créé ! Connectez-vous.")
            else:
                st.warning("Remplissez tous les champs.")

else:
    # Interface Chat une fois connecté
    st.title(f"Nova IA - Session de {st.session_state.user}")
    
    if st.button("Déconnexion"):
        st.session_state.logged = False
        st.rerun()

    # Affichage de l'historique
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Entrée du chat
    if prompt := st.chat_input("Posez votre question à Nova..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            response = ask_ai(st.session_state.messages)
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Sauvegarde automatique
        save_github()
