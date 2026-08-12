import streamlit as st
import pandas as pd
from auxiliar.google_sheets import get_sheet_data,set_sheet_data
from auxiliar.athentication import caixa_de_autenticacao

password = st.secrets["PASSWORD"]
password_parametro = st.query_params.get("password",None)

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if password == password_parametro:
    st.session_state["autenticado"] = True

autenticado = st.session_state["autenticado"]

if "base_de_horas" not in st.session_state:
    st.session_state["base_de_horas"] = get_sheet_data("base_de_horas")

horas_df = st.session_state["base_de_horas"]

if autenticado:
    st.title("⚠️⚠️Modificar horas registradas⚠️⚠️")

    base_horas = st.data_editor(
        horas_df,
        num_rows="dynamic"
    )

    atualizar_botao = st.button("⚠️Atualizar base⚠️")
    st.caption("Link para edição no Google Sheets: https://docs.google.com/spreadsheets/d/1qSUrm2deYcni2DdA1hHjsiNvyf0KCM7Hitmb1AcCyoM/")
    st.caption("Para editar a planilha diretamente, é necessário estar logado no e-mail: clinicasinapserdev@gmail.com")
    if atualizar_botao:
        set_sheet_data("base_de_horas",base_horas)
        st.success("Base atualizada com sucesso!")
        st.balloons()

else:

    st.error("Senha incorreta. Acesso negado.")
    caixa_de_autenticacao()