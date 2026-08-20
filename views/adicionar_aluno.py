import streamlit as st
import pandas as pd

from auxiliar.google_sheets import get_sheet_data, set_sheet_data, get_professores_list


# ============================================================
# PÁGINA
# ============================================================

st.title("Adicionar Alunos")

alunos_df = get_sheet_data("base_alunos")
professores = get_professores_list()

base_alunos_editada = st.data_editor(
    alunos_df,
    num_rows="dynamic",
    column_config={
        "aluno": st.column_config.TextColumn(
            "Nome do Aluno"
        ),
        "hora_aula": st.column_config.NumberColumn(
            "Hora Aula",
            help="Valor da hora-aula",
            format="R$ %.2f",
        ),
        "professor": st.column_config.SelectboxColumn(
            "Professor",
            options=professores,
            required=True,
        ),
    },
    key="editor_base_alunos",
)

atualizar_botao = st.button(
    "Atualizar base de alunos",
    type="primary",
)

if atualizar_botao:
    set_sheet_data(
        "base_alunos",
        base_alunos_editada,
    )

    st.success("Base de alunos atualizada com sucesso!")
    st.balloons()