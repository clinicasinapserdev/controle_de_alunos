import streamlit as st
from datetime import date
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
import re
import pandas as pd

from auxiliar.google_sheets import get_sheet_data
from auxiliar.download_as_image import df_to_image_bytes


def limpar_nome_arquivo(texto: str) -> str:
    texto = str(texto).strip()
    texto = re.sub(r'[\\/*?:"<>|]', "", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto


def normalizar_periodo(seletor_periodo):
    if isinstance(seletor_periodo, (tuple, list)):
        if len(seletor_periodo) == 2:
            return seletor_periodo[0], seletor_periodo[1]
        if len(seletor_periodo) == 1:
            return seletor_periodo[0], seletor_periodo[0]

    return seletor_periodo, seletor_periodo


def gerar_zip_tabelas_alunos(
    df_professor: pd.DataFrame,
    professor: str,
    data_inicio: date,
    data_fim: date,
) -> bytes:
    zip_buffer = BytesIO()

    alunos = sorted(df_professor["aluno"].dropna().unique())

    logo_path = "assets/cartão_ciro.png" if professor == "Ciro" else None

    with ZipFile(zip_buffer, "w", ZIP_DEFLATED) as zip_file:
        for aluno in alunos:
            df_aluno = df_professor.loc[df_professor["aluno"] == aluno].copy()

            if df_aluno.empty:
                continue

            df_aluno["quantidade_de_horas"] = pd.to_numeric(
                df_aluno["quantidade_de_horas"],
                errors="coerce",
            ).fillna(0)

            df_aluno["hora_aula"] = pd.to_numeric(
                df_aluno["hora_aula"],
                errors="coerce",
            ).fillna(0)

            df_aluno["valor_total"] = (
                df_aluno["quantidade_de_horas"] * df_aluno["hora_aula"]
            )

            total_horas = float(df_aluno["quantidade_de_horas"].sum())
            valor_total = float(df_aluno["valor_total"].sum())

            valores_hora = df_aluno["hora_aula"].dropna()
            valor_aluno = float(valores_hora.iloc[0]) if not valores_hora.empty else 0

            colunas = ["data_da_aula", "quantidade_de_horas", "observacoes"]

            relatorio_detalhado_df = df_aluno[colunas].copy()

            relatorio_detalhado_df = relatorio_detalhado_df.rename(
                columns={
                    "data_da_aula": "Data da Aula",
                    "quantidade_de_horas": "Quantidade de Horas",
                    "observacoes": "Observações",
                }
            )

            relatorio_detalhado_df["Data da Aula"] = pd.to_datetime(
                relatorio_detalhado_df["Data da Aula"],
                errors="coerce",
            ).dt.strftime("%d/%m/%Y")

            titulo_da_tabela = (
                f"Aluno: {aluno}\n"
                f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}\n"
                f"Total de horas: {total_horas} horas\n"
                f"Valor total: R$ {valor_total:.2f}\n"
                f"Chave Pix: 368.509.398-31 (Patricia Miyuki)"
            )

            img_bytes = df_to_image_bytes(
                relatorio_detalhado_df,
                title=titulo_da_tabela,
                logo_path=logo_path,
            )

            if hasattr(img_bytes, "getvalue"):
                img_bytes = img_bytes.getvalue()

            nome_aluno = limpar_nome_arquivo(aluno)

            file_name = (
                f"{nome_aluno} - "
                f"{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.png"
            )

            zip_file.writestr(file_name, img_bytes)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


if "base_alunos" not in st.session_state:
    st.session_state["base_alunos"] = get_sheet_data("base_alunos")

if "base_de_horas" not in st.session_state:
    st.session_state["base_de_horas"] = get_sheet_data("base_de_horas")

alunos_df = st.session_state["base_alunos"].copy()
horas_df = st.session_state["base_de_horas"].copy()

alunos_df["aluno"] = alunos_df["aluno"].astype(str).str.strip()
alunos_df["professor"] = alunos_df["professor"].astype(str).str.strip()

# Remove linhas duplicadas de aluno/professor (ex.: cadastro repetido
# por engano na planilha), mantendo a mais recente.
alunos_df = alunos_df.drop_duplicates(
    subset=["aluno", "professor"],
    keep="last",
)

horas_df["aluno"] = horas_df["aluno"].astype(str).str.strip()
horas_df["professor"] = horas_df["professor"].astype(str).str.strip()

st.title("Visualizar total")

seletor_periodo = st.date_input(
    "Selecione o período:",
    value=(date.today().replace(day=1), date.today()),
)

data_inicio, data_fim = normalizar_periodo(seletor_periodo)

horas_df["data_da_aula"] = pd.to_datetime(
    horas_df["data_da_aula"],
    errors="coerce",
)

if "data_atualizacao" in horas_df.columns:
    horas_df["data_atualizacao"] = pd.to_datetime(
        horas_df["data_atualizacao"],
        errors="coerce",
    )

merged_df = horas_df.merge(
    alunos_df,
    on=["aluno", "professor"],
    how="left",
)

filtro_periodo = (
    (merged_df["data_da_aula"].dt.date >= data_inicio)
    & (merged_df["data_da_aula"].dt.date <= data_fim)
)

merged_df = merged_df.loc[filtro_periodo].copy()

merged_df["quantidade_de_horas"] = pd.to_numeric(
    merged_df["quantidade_de_horas"],
    errors="coerce",
).fillna(0)

merged_df["hora_aula"] = pd.to_numeric(
    merged_df["hora_aula"],
    errors="coerce",
).fillna(0)

merged_df["valor_total"] = (
    merged_df["quantidade_de_horas"] * merged_df["hora_aula"]
)

resumo_professor = (
    merged_df.groupby("professor")[["quantidade_de_horas", "valor_total"]]
    .sum()
    .reset_index()
)

total_geral_horas = resumo_professor["quantidade_de_horas"].sum()
total_geral_valor = resumo_professor["valor_total"].sum()

resumo_professor.loc[len(resumo_professor)] = [
    "Total Geral",
    total_geral_horas,
    total_geral_valor,
]

st.subheader("Resumo por Professor")

st.dataframe(
    resumo_professor,
    hide_index=True,
    column_config={
        "professor": st.column_config.TextColumn("Professor"),
        "quantidade_de_horas": st.column_config.NumberColumn(
            "Quantidade de horas",
            format="%.2f",
        ),
        "valor_total": st.column_config.NumberColumn(
            "Valor total",
            format="R$ %.2f",
        ),
    },
)

professores_disponiveis = sorted(
    merged_df["professor"].dropna().unique()
)

if professores_disponiveis:
    professor_selecionado_download = st.selectbox(
        "Selecione o professor para baixar as tabelas dos alunos:",
        professores_disponiveis,
        key="professor_download_tabelas",
    )

    df_professor_download = merged_df.loc[
        merged_df["professor"] == professor_selecionado_download
    ].copy()

    zip_bytes = gerar_zip_tabelas_alunos(
        df_professor=df_professor_download,
        professor=professor_selecionado_download,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )

    nome_professor = limpar_nome_arquivo(professor_selecionado_download)

    st.download_button(
        label="Baixar todas as tabelas",
        data=zip_bytes,
        file_name=(
            f"tabelas_{nome_professor}_"
            f"{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.zip"
        ),
        mime="application/zip",
    )
else:
    st.info("Nenhum professor encontrado neste período.")

resumo_aluno = (
    merged_df.groupby(["aluno", "professor"])[["quantidade_de_horas", "valor_total"]]
    .sum()
    .reset_index()
)

resumo_aluno.sort_values(by="professor", inplace=True)

st.subheader("Resumo por Aluno")

st.dataframe(
    resumo_aluno,
    hide_index=True,
    column_config={
        "aluno": st.column_config.TextColumn("Aluno"),
        "professor": st.column_config.TextColumn("Professor"),
        "quantidade_de_horas": st.column_config.NumberColumn(
            "Quantidade de horas",
            format="%.2f",
        ),
        "valor_total": st.column_config.NumberColumn(
            "Valor total",
            format="R$ %.2f",
        ),
    },
)

st.subheader("Detalhe do Aluno")

alunos_disponiveis = sorted(merged_df["aluno"].dropna().unique())

if alunos_disponiveis:
    aluno_selecionado = st.selectbox(
        "Selecione um aluno:",
        alunos_disponiveis,
    )

    detalhe_aluno = merged_df.loc[
        merged_df["aluno"] == aluno_selecionado
    ].copy()

    st.dataframe(
        detalhe_aluno,
        hide_index=True,
        column_config={
            "data_da_aula": st.column_config.DatetimeColumn(
                "Data da aula",
                format="DD/MM/YYYY",
            ),
            "data_atualizacao": st.column_config.DatetimeColumn(
                "Data de atualização",
                format="DD/MM/YYYY",
            ),
            "valor_total": st.column_config.NumberColumn(
                "Valor total",
                format="R$ %.2f",
            ),
        },
    )
else:
    st.info("Nenhum aluno encontrado neste período.")
