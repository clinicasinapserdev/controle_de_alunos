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

if "base_alunos" not in st.session_state:
    st.session_state["base_alunos"] = get_sheet_data("base_alunos")

alunos_df = st.session_state["base_alunos"]

if autenticado:
    st.title("Adicionar Alunos")

    base_alunos = st.data_editor(
        alunos_df,
        num_rows="dynamic",
        column_config={
            "aluno": st.column_config.TextColumn("Nome do Aluno"),
            "hora_aula": st.column_config.NumberColumn(
                "Hora Aula",
                help="Valor da hora-aula",
                format="R$ %.2f",
            ),
            "professor": st.column_config.SelectboxColumn(
                "Professor", 
                options=["Patricia","Ciro"],
                required=True),    
        },
    )

    atualizar_botao = st.button("Atualizar base de alunos")

    if atualizar_botao:
        set_sheet_data("base_alunos",base_alunos)
        st.success("Base de alunos atualizada com sucesso!")
        st.balloons()
else:
    st.error("Senha incorreta. Acesso negado.")
    caixa_de_autenticacao()