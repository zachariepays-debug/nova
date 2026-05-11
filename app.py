import streamlit as st

st.set_page_config(
    page_title="Nova",
    page_icon="💜",
    layout="wide"
)

st.markdown("""
<style>
.stButton button {
    height: 150px;
    font-size: 35px;
    border-radius: 25px;
}
</style>
""", unsafe_allow_html=True)

st.title("💜 NOVA")
st.subheader("Bienvenue sur Nova IA")

col1, col2 = st.columns(2)

with col1:
    st.button("💬 IA TEXTE", use_container_width=True)

with col2:
    st.button("🎤 IA VOCALE", use_container_width=True)
