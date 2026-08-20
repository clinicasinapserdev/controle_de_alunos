import streamlit as st
import pandas as pd

from auxiliar.google_sheets import get_sheet_data, set_sheet_data


# ============================================================
# PÁGINA
# ============================================================

st.title("Adicionar Professores")

professores_df = get_sheet_data("base_professores")

# Garante que a base tenha sempre a coluna "professor", mesmo
# quando a planilha está vazia (sem cabeçalho) ou com outro nome.
if professores_df.empty and professores_df.columns.empty:
    professores_df = pd.DataFrame(columns=["professor"])
elif "professor" not in professores_df.columns:
    professores_df = professores_df.rename(
        columns={professores_df.columns[0]: "professor"}
    )

base_professores_editada = st.data_editor(
    professores_df,
    num_rows="dynamic",
    column_config={
        "professor": st.column_config.TextColumn(
            "Nome do Professor"
        ),
    },
    key="editor_base_professores",
)

atualizar_botao = st.button(
    "Atualizar base de professores",
    type="primary",
)

if atualizar_botao:
    set_sheet_data(
        "base_professores",
        base_professores_editada,
    )

    st.success("Base de professores atualizada com sucesso!")
    st.balloons()
