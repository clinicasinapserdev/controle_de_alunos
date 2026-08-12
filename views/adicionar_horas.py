import streamlit as st
from datetime import date
from auxiliar.google_sheets import get_sheet_data,append_sheet_data
from auxiliar.download_as_image import df_to_image_bytes
from auxiliar.athentication import caixa_de_autenticacao
import pandas as pd

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

@st.dialog("Visualizar Horas",width = "medium")
def visualizar_horas_aluno(aluno: str,professor: str = None):

    horas_df = get_sheet_data("base_de_horas")
    horas_aluno = horas_df.loc[horas_df["aluno"] == aluno]

    seletor_periodo = st.date_input("Selecione o período:", value=(date.today().replace(day=1),date.today()))
    if len(seletor_periodo) == 2:
        data_inicio, data_fim = seletor_periodo
    else:
        data_inicio = seletor_periodo[0]
        data_fim = seletor_periodo[0]

    filtro_periodo = (horas_aluno["data_da_aula"] >= data_inicio.strftime("%Y-%m-%d")) & (horas_aluno["data_da_aula"] <= data_fim.strftime("%Y-%m-%d"))
    
    horas_aluno = horas_aluno.loc[filtro_periodo]
    horas_aluno["quantidade_de_horas"] = horas_aluno["quantidade_de_horas"].astype(float)
    horas_aluno = horas_aluno.sort_values(by="data_da_aula",ascending=True)
    
    total_horas = horas_aluno["quantidade_de_horas"].sum()
    
    valor_aluno = alunos_df.loc[alunos_df["aluno"] == aluno, "hora_aula"].values[0]

    total_horas = float(total_horas)
    valor_aluno = float(valor_aluno)

    valor_total = total_horas * valor_aluno

    st.subheader(f"Horas do aluno {aluno}:")

    col1,col2,col3= st.columns(3)
    col1.metric("Total de horas no período:", f"{total_horas} horas")
    col2.metric("Valor total no período:", f"R$ {valor_total:.2f}")
    col3.metric("Valor da hora-aula:", f"R$ {valor_aluno:.2f}")

    st.subheader("Detalhamento das horas:")
    
    colunas = ["data_da_aula","quantidade_de_horas","observacoes"]
    relatorio_detalhado_df = horas_aluno[colunas]
    relatorio_detalhado_df = relatorio_detalhado_df.rename(columns={
        "data_da_aula": "Data da Aula",
        "quantidade_de_horas": "Quantidade de Horas",
        "observacoes": "Observações",
    })

    relatorio_detalhado_df["Data da Aula"] = pd.to_datetime(relatorio_detalhado_df["Data da Aula"]).dt.strftime("%d/%m/%Y")
    
    if relatorio_detalhado_df.empty:
        
        st.info("Nenhum registro de horas encontrado para o aluno neste período.")

    else:

        titulo_da_tabela = (
        f"Aluno: {aluno}\n"
        f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}\n"
        f"Total de horas: {total_horas} horas\n"
        f"Valor total: R$ {valor_total:.2f}\n"
        f"Chave Pix: 368.509.398-31 (Patricia Miyuki)"
        )

        st.dataframe(relatorio_detalhado_df,hide_index=True)
        if professor == "Ciro":
            logo_path = "assets/cartão_ciro.png"
        else:
            logo_path = None

        img_bytes = df_to_image_bytes(relatorio_detalhado_df,title=titulo_da_tabela,logo_path=logo_path)

        file_name = f"{aluno} - {data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.png"
        st.download_button(
            label="Baixar tabela",
            data=img_bytes,
            file_name=file_name,
            mime="image/png",
        )

    st.caption("Link para edição no Google Sheets: https://docs.google.com/spreadsheets/d/133kYKvfehQQeJTQ86Z2IM3SmgIBNmd0ZQfhvPFgqFGY/")

professor_parametro = st.query_params.get("professor",None)

if professor_parametro == "ciro":
    index = 1
else:
    index = 0


if autenticado:
    st.title("Adicionar Horas")

    col1,col2 = st.columns(2)

    professor = col1.selectbox("Selecione o professor:", ["Patricia","Ciro"],index=index)

    alunos_filtrados = alunos_df.loc[alunos_df["professor"] == professor]
    alunos = alunos_filtrados["aluno"].tolist()

    aluno = col2.selectbox("Selecione o aluno:", alunos)

    data_aula = col1.date_input("Data da atividade:", value=date.today())
    quantidade_horas = col2.number_input("Quantidade de horas:", step=0.5)
    observacoes = st.text_input("Observações (opcional):")

    botao_adicionar_horas = st.button("Adicionar horas",type="primary")
    visualizar_aluno = st.button("Visualizar horas do aluno",type="secondary")

    if botao_adicionar_horas:
        nova_linha = {
            "data_da_aula": data_aula.strftime("%Y-%m-%d"),
            "quantidade_de_horas": quantidade_horas,
            "aluno": aluno,
            "professor": professor,
            "data_atualizacao": date.today().strftime("%Y-%m-%d"),
            "observacoes": observacoes,
        }
        
        append_sheet_data("base_de_horas", [list(nova_linha.values())])
        st.success(f"Foram adicionadas {quantidade_horas} horas para o aluno {aluno} do professor {professor}.")
        st.balloons()

    if visualizar_aluno:
        visualizar_horas_aluno(aluno,professor)
else:
    st.error("Senha incorreta. Acesso negado.")
    caixa_de_autenticacao()