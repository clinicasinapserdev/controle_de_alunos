import streamlit as st
import pandas as pd

from auxiliar.google_sheets import get_sheet_data, set_sheet_data
from auxiliar.athentication import caixa_de_autenticacao


password = st.secrets["PASSWORD"]
password_parametro = st.query_params.get("password", None)


# ============================================================
# AUTENTICAÇÃO
# ============================================================

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if password == password_parametro:
    st.session_state["autenticado"] = True

autenticado = st.session_state["autenticado"]


# ============================================================
# CARREGAMENTO DA BASE
# ============================================================

if "base_professores_df" not in st.session_state:
    st.session_state["base_professores_df"] = get_sheet_data("base_professores")


# ============================================================
# PÁGINA
# ============================================================

if autenticado:
    st.title("Adicionar Professores")

    professores_df = st.session_state["base_professores_df"]

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

        # Atualiza a cópia armazenada na sessão.
        st.session_state["base_professores_df"] = base_professores_editada.copy()

        # Força recarregar a lista de professores nas demais páginas.
        if hasattr(get_sheet_data, "clear"):
            get_sheet_data.clear()

        if "base_professores" in st.session_state:
            del st.session_state["base_professores"]

        st.success("Base de professores atualizada com sucesso!")
        st.balloons()

else:
    st.error("Senha incorreta. Acesso negado.")
    caixa_de_autenticacao()
