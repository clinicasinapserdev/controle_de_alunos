import streamlit as st

st.set_page_config(layout="wide")

# --- PAGE SETUP ---
horas_page = st.Page(
    "views/adicionar_horas.py",
    title="Adicionar Horas",
    icon=":material/punch_clock:",
    default=True,
)

aluno_page = st.Page(
    "views/adicionar_aluno.py",
    title="Adicionar Alunos",
    icon=":material/child_care:",
)

professor_page = st.Page(
    "views/adicionar_professor.py",
    title="Adicionar Professores",
    icon=":material/person:",
)

total_page = st.Page(
    "views/total_de_dinheiro.py",
    title="Total de Dinheiro",
    icon=":material/money:",
)

editar_horas_page = st.Page(
    "views/editar_planilha.py",
    title="Editar Planilha de Horas",
    icon=":material/warning:",
)

# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
# pg = st.navigation(pages=[about_page, project_1_page, project_2_page])

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Controle de horas": [horas_page,total_page],
        "Configurações": [aluno_page,professor_page,editar_horas_page],
    }
)

# --- SHARED ON ALL PAGES ---
st.sidebar.caption("Version 1.1.4")


# --- RUN NAVIGATION ---
pg.run()