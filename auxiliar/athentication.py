import streamlit as st

def autenticar_usuario(password_correto: str) -> bool:
    password_saved = st.secrets["PASSWORD"]

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if password_correto == password_saved:
        st.session_state["autenticado"] = True

    return st.session_state["autenticado"]

def caixa_de_autenticacao():
    st.warning("Acesso restrito. Por favor, forneça a senha correta na URL para continuar.")
    password = st.text_input("Password",type="password")
    if st.button("login"):
        password_check = autenticar_usuario(password)
        if password_check:
            st.rerun()
