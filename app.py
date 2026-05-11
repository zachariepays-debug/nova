import streamlit as st
import json
import os

st.set_page_config(
    page_title="Nova",
    page_icon="💜",
    layout="centered"
)

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

# ======================
# STYLE
# ======================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: sans-serif;
}

.stApp {
    background-color: #0d0d0d;
    color: white;
}

h1 {
    text-align: center;
    font-size: 55px !important;
    color: #c77dff;
}

.big-button button {
    height: 180px;
    font-size: 35px !important;
    border-radius: 30px;
    margin-top: 20px;
    background: linear-gradient(45deg,#7b2cbf,#c77dff);
    color: white;
    border: none;
}

.stTextInput input {
    height: 55px;
    font-size: 20px;
    border-radius: 15px;
}

.stSelectbox div {
    font-size: 20px;
}

.small-text {
    text-align:center;
    color:gray;
    font-size:18px;
}

</style>
""", unsafe_allow_html=True)

# ======================
# LOGO
# ======================

st.markdown("# 💜 NOVA")

# ======================
# LOGIN / REGISTER
# ======================

if not st.session_state.logged:

    st.markdown(
        "<p class='small-text'>Assistant IA vocal intelligent</p>",
        unsafe_allow_html=True
    )

    menu = st.selectbox(
        "Choisir",
        ["Connexion", "Inscription"]
    )

    username = st.text_input("Nom utilisateur")

    password = st.text_input(
        "Mot de passe",
        type="password"
    )

    # ======================
    # REGISTER
    # ======================

    if menu == "Inscription":

        if st.button("Créer mon compte", use_container_width=True):

            if username in users:
                st.error("Nom déjà utilisé")

            elif username == "" or password == "":
                st.error("Remplis tous les champs")

            else:

                users[username] = password

                with open("users.json", "w") as f:
                    json.dump(users, f)

                st.success("Compte créé avec succès")

    # ======================
    # LOGIN
    # ======================

    else:

        if st.button("Connexion", use_container_width=True):

            if username in users and users[username] == password:

                st.session_state.logged = True
                st.session_state.username = username
                st.rerun()

            else:
                st.error("Identifiants incorrects")

# ======================
# HOME
# ======================

else:

    st.success(
        f"Bienvenue {st.session_state.username}"
    )

    st.markdown("## Choisissez un mode")

    st.markdown(
        '<div class="big-button">',
        unsafe_allow_html=True
    )

    st.button(
        "💬 IA TEXTE",
        use_container_width=True
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="big-button">',
        unsafe_allow_html=True
    )

    st.button(
        "🎤 IA VOCALE",
        use_container_width=True
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    if st.button(
        "Déconnexion",
        use_container_width=True
    ):

        st.session_state.logged = False
        st.rerun()
