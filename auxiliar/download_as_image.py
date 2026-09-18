import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


def df_to_image_bytes(
    df: pd.DataFrame,
    titulo: str = None,
    subtitulo: str = None,
    logo_path: str = None,
) -> BytesIO:
    """Converte um DataFrame em PNG com cabeçalho de cobrança acima da tabela.

    `titulo` é o destaque principal (ex.: professor ou categoria de
    atendimento) e `subtitulo` são as linhas de detalhe (aluno, período,
    horas, valor). A altura da imagem se ajusta à quantidade de linhas
    da tabela, em vez de reservar sempre um espaço em branco fixo.
    """
    n_rows, n_cols = df.shape

    fig_width = max(10, n_cols * 2.5)

    # --- Alturas em polegadas de cada bloco, para a imagem crescer/encolher
    # junto com o conteúdo em vez de deixar espaço em branco sobrando ---
    margem_topo_in = 0.35
    margem_base_in = 0.35

    cabecalho_in = 0.0
    if titulo:
        cabecalho_in += 0.5
    if subtitulo:
        linhas_subtitulo = subtitulo.count("\n") + 1
        cabecalho_in += 0.08 + linhas_subtitulo * 0.28
    if titulo or subtitulo:
        cabecalho_in += 0.25  # respiro + linha divisória antes da tabela

    altura_linha_in = 0.4
    tabela_in = altura_linha_in * (n_rows + 1)  # +1 para a linha de cabeçalho

    logo_in = 2.3 if logo_path else 0.0

    fig_height = margem_topo_in + cabecalho_in + tabela_in + logo_in + margem_base_in

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis("off")

    table_bottom = (margem_base_in + logo_in) / fig_height
    table_height = tabela_in / fig_height
    topo_tabela = table_bottom + table_height

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        bbox=[0.0, table_bottom, 1.0, table_height]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(12)

    # Borda preta ao redor das células
    for cell in table.get_celld().values():
        cell.set_linewidth(0.5)
        cell.set_edgecolor('black')

    # Cores e estilo
    header_color = "#2F5597"
    header_text_color = "white"
    row_colors = ["#f2f2f2", "#ffffff"]

    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor(header_color)
            cell.set_text_props(color=header_text_color, weight="bold")
        else:
            cell.set_facecolor(row_colors[(row - 1) % 2])

    # --- CABEÇALHO DE COBRANÇA acima da tabela ---
    titulo_y = 1 - (margem_topo_in / fig_height)

    if titulo:
        fig.text(
            0.5, titulo_y, titulo,
            ha='center', va='top',
            fontsize=23, fontweight='bold', color=header_color,
        )

    if subtitulo:
        subtitulo_y = titulo_y - (0.55 / fig_height if titulo else 0)
        fig.text(
            0.5, subtitulo_y, subtitulo,
            ha='center', va='top',
            fontsize=13, color='#555555', linespacing=1.7,
        )

    if titulo or subtitulo:
        # Linha divisória fina separando o cabeçalho da tabela
        linha_divisoria = plt.Line2D(
            [0.05, 0.95], [topo_tabela + (0.1 / fig_height)] * 2,
            transform=fig.transFigure, color='#d9d9d9', linewidth=1,
        )
        fig.add_artist(linha_divisoria)

    # --- LOGO SECTION ---
    if logo_path:
        try:
            logo = Image.open(logo_path)
            imagebox = OffsetImage(logo, zoom=0.22)
            logo_y = (margem_base_in + logo_in / 2) / fig_height
            ab = AnnotationBbox(
                imagebox, (0.5, logo_y),
                xycoords='figure fraction',
                frameon=False,
                box_alignment=(0.5, 0.5)
            )
            fig.add_artist(ab)
        except Exception as e:
            print(f"Logo error: {e}")

    plt.subplots_adjust(top=0.99, bottom=0.01, left=0.03, right=0.97)

    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=200, facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf
