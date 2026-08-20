import streamlit as st
import pandas as pd
from auxiliar.google_sheets import get_sheet_data,set_sheet_data

if "base_de_horas" not in st.session_state:
    st.session_state["base_de_horas"] = get_sheet_data("base_de_horas")

horas_df = st.session_state["base_de_horas"]

st.title("⚠️⚠️Modificar horas registradas⚠️⚠️")

base_horas = st.data_editor(
    horas_df,
    num_rows="dynamic",
    column_config={
        "data_da_aula": st.column_config.TextColumn("Data da Aula"),
        "quantidade_de_horas": st.column_config.TextColumn(
            "Quantidade de Horas"
        ),
        "aluno": st.column_config.TextColumn("Aluno"),
        "professor": st.column_config.TextColumn("Professor"),
        "data_atualizacao": st.column_config.TextColumn(
            "Data de Atualização"
        ),
        "observacoes": st.column_config.TextColumn("Observações"),
    },
)

atualizar_botao = st.button("⚠️Atualizar base⚠️")
st.caption("Link para edição no Google Sheets: https://docs.google.com/spreadsheets/d/1qSUrm2deYcni2DdA1hHjsiNvyf0KCM7Hitmb1AcCyoM/")
st.caption("Para editar a planilha diretamente, é necessário estar logado no e-mail: clinicasinapserdev@gmail.com")
if atualizar_botao:
    set_sheet_data("base_de_horas",base_horas)
    st.success("Base atualizada com sucesso!")
    st.balloons()