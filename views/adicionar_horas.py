import streamlit as st
import pandas as pd

from datetime import date

from auxiliar.google_sheets import (
    get_sheet_data,
    append_sheet_data,
    get_professores_list,
)
from auxiliar.download_as_image import df_to_image_bytes


# ============================================================
# CARREGAMENTO DA BASE DE ALUNOS
# ============================================================

if "base_alunos" not in st.session_state:
    st.session_state["base_alunos"] = get_sheet_data("base_alunos")

if "base_professores" not in st.session_state:
    st.session_state["base_professores"] = get_professores_list()


# ============================================================
# DIALOG PARA VISUALIZAR AS HORAS
# ============================================================

@st.dialog("Visualizar Horas", width="medium")
def visualizar_horas_aluno(aluno: str, professor: str | None = None):
    horas_df = get_sheet_data("base_de_horas")

    if horas_df.empty:
        st.info("Nenhum registro de horas encontrado.")
        return

    filtro_aluno = horas_df["aluno"].astype(str).str.strip() == str(aluno).strip()

    if professor is not None:
        filtro_aluno &= (
            horas_df["professor"].astype(str).str.strip()
            == str(professor).strip()
        )

    horas_aluno = horas_df.loc[filtro_aluno].copy()

    seletor_periodo = st.date_input(
        "Selecione o período:",
        value=(
            date.today().replace(day=1),
            date.today(),
        ),
    )

    if isinstance(seletor_periodo, (tuple, list)):
        if len(seletor_periodo) == 2:
            data_inicio, data_fim = seletor_periodo
        elif len(seletor_periodo) == 1:
            data_inicio = seletor_periodo[0]
            data_fim = seletor_periodo[0]
        else:
            data_inicio = date.today().replace(day=1)
            data_fim = date.today()
    else:
        data_inicio = seletor_periodo
        data_fim = seletor_periodo

    horas_aluno["data_da_aula"] = pd.to_datetime(
        horas_aluno["data_da_aula"],
        errors="coerce",
    )

    filtro_periodo = (
        horas_aluno["data_da_aula"].dt.date >= data_inicio
    ) & (
        horas_aluno["data_da_aula"].dt.date <= data_fim
    )

    horas_aluno = horas_aluno.loc[filtro_periodo].copy()

    horas_aluno["quantidade_de_horas"] = pd.to_numeric(
        horas_aluno["quantidade_de_horas"],
        errors="coerce",
    ).fillna(0)

    horas_aluno = horas_aluno.sort_values(
        by="data_da_aula",
        ascending=True,
    )

    total_horas = float(
        horas_aluno["quantidade_de_horas"].sum()
    )

    alunos_df = st.session_state["base_alunos"]

    filtro_valor = alunos_df["aluno"].astype(str).str.strip() == str(aluno).strip()

    if professor is not None:
        filtro_valor &= (
            alunos_df["professor"].astype(str).str.strip()
            == str(professor).strip()
        )

    valor_encontrado = alunos_df.loc[filtro_valor, "hora_aula"]

    if valor_encontrado.empty:
        st.error(
            f"Não foi possível encontrar o valor da hora-aula de {aluno}."
        )
        return

    valor_aluno = pd.to_numeric(
        valor_encontrado.iloc[-1],
        errors="coerce",
    )

    if pd.isna(valor_aluno):
        st.error(
            f"O valor da hora-aula de {aluno} é inválido."
        )
        return

    valor_aluno = float(valor_aluno)
    valor_total = total_horas * valor_aluno

    st.subheader(f"Horas do aluno {aluno}:")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total de horas no período:",
        f"{total_horas:g} horas",
    )

    col2.metric(
        "Valor total no período:",
        f"R$ {valor_total:.2f}",
    )

    col3.metric(
        "Valor da hora-aula:",
        f"R$ {valor_aluno:.2f}",
    )

    st.subheader("Detalhamento das horas:")

    colunas = [
        "data_da_aula",
        "quantidade_de_horas",
        "observacoes",
    ]

    # Garante que todas as colunas existam
    for coluna in colunas:
        if coluna not in horas_aluno.columns:
            horas_aluno[coluna] = ""

    relatorio_detalhado_df = horas_aluno[colunas].copy()

    relatorio_detalhado_df = relatorio_detalhado_df.rename(
        columns={
            "data_da_aula": "Data da Aula",
            "quantidade_de_horas": "Quantidade de Horas",
            "observacoes": "Observações",
        }
    )

    relatorio_detalhado_df["Data da Aula"] = (
        pd.to_datetime(
            relatorio_detalhado_df["Data da Aula"],
            errors="coerce",
        ).dt.strftime("%d/%m/%Y")
    )

    if relatorio_detalhado_df.empty:
        st.info(
            "Nenhum registro de horas encontrado para o aluno "
            "neste período."
        )

    else:
        titulo_da_tabela = (
            f"Aluno: {aluno}\n"
            f"Período: {data_inicio.strftime('%d/%m/%Y')} "
            f"a {data_fim.strftime('%d/%m/%Y')}\n"
            f"Total de horas: {total_horas:g} horas\n"
            f"Valor total: R$ {valor_total:.2f}\n"
        )

        st.dataframe(
            relatorio_detalhado_df,
            hide_index=True,
            use_container_width=True,
        )

        img_bytes = df_to_image_bytes(
            relatorio_detalhado_df,
            title=titulo_da_tabela,
            logo_path=None,
        )

        file_name = (
            f"{aluno} - "
            f"{data_inicio.strftime('%Y%m%d')}_"
            f"{data_fim.strftime('%Y%m%d')}.png"
        )

        st.download_button(
            label="Baixar tabela",
            data=img_bytes,
            file_name=file_name,
            mime="image/png",
        )

    st.caption(
        "Link para edição no Google Sheets: "
        "https://docs.google.com/spreadsheets/d/1qSUrm2deYcni2DdA1hHjsiNvyf0KCM7Hitmb1AcCyoM/"
    )


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

st.title("Adicionar Horas")

# Permite forçar a atualização caso a planilha tenha sido
# alterada diretamente no Google Sheets.
if st.button(
    "Atualizar listas de alunos e professores",
    type="secondary",
):
    # Se get_sheet_data usa @st.cache_data, limpa o resultado
    # armazenado antes de consultar novamente.
    if hasattr(get_sheet_data, "clear"):
        get_sheet_data.clear()

    st.session_state["base_alunos"] = get_sheet_data(
        "base_alunos"
    )

    st.session_state["base_professores"] = get_professores_list()

    st.success("Listas de alunos e professores atualizadas!")
    st.rerun()

alunos_df = st.session_state["base_alunos"]

if alunos_df.empty:
    st.warning(
        "A base de alunos está vazia. Cadastre pelo menos um aluno."
    )
    st.stop()

colunas_obrigatorias = {
    "aluno",
    "professor",
    "hora_aula",
}

colunas_ausentes = colunas_obrigatorias.difference(
    alunos_df.columns
)

if colunas_ausentes:
    st.error(
        "A base de alunos não possui as seguintes colunas: "
        + ", ".join(sorted(colunas_ausentes))
    )
    st.stop()

col1, col2 = st.columns(2)

professores = st.session_state["base_professores"]

if not professores:
    st.warning(
        "A base de professores está vazia. Cadastre pelo menos "
        "um professor na página 'Adicionar Professores'."
    )
    st.stop()

professor = col1.selectbox(
    "Selecione o professor:",
    professores,
)

alunos_filtrados = alunos_df.loc[
    alunos_df["professor"].astype(str).str.strip() == professor
].copy()

alunos = (
    alunos_filtrados["aluno"]
    .dropna()
    .astype(str)
    .str.strip()
)

alunos = sorted(
    aluno
    for aluno in alunos.unique().tolist()
    if aluno
)

if not alunos:
    st.warning(
        f"Não há alunos cadastrados para o professor {professor}."
    )
    st.stop()

aluno = col2.selectbox(
    "Selecione o aluno:",
    alunos,
)

data_aula = col1.date_input(
    "Data da atividade:",
    value=date.today(),
)

quantidade_horas = col2.number_input(
    "Quantidade de horas:",
    min_value=0.0,
    step=0.5,
)

observacoes = st.text_input(
    "Observações (opcional):"
)

botao_adicionar_horas = st.button(
    "Adicionar horas",
    type="primary",
)

visualizar_aluno = st.button(
    "Visualizar horas do aluno",
    type="secondary",
)

if botao_adicionar_horas:
    if quantidade_horas <= 0:
        st.error(
            "A quantidade de horas deve ser maior do que zero."
        )

    else:
        nova_linha = {
            "data_da_aula": data_aula.strftime("%Y-%m-%d"),
            "quantidade_de_horas": quantidade_horas,
            "aluno": aluno,
            "professor": professor,
            "data_atualizacao": date.today().strftime("%Y-%m-%d"),
            "observacoes": observacoes,
        }

        append_sheet_data(
            "base_de_horas",
            [list(nova_linha.values())],
        )

        # Evita que a janela de visualização continue mostrando
        # uma versão em cache anterior ao novo registro.
        if hasattr(get_sheet_data, "clear"):
            get_sheet_data.clear()

        st.success(
            f"Foram adicionadas {quantidade_horas:g} horas "
            f"para o aluno {aluno}, do professor {professor}."
        )

        st.balloons()

if visualizar_aluno:
    visualizar_horas_aluno(
        aluno,
        professor,
    )