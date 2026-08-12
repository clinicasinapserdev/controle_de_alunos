import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


def df_to_image_bytes(df: pd.DataFrame, title: str = None, logo_path: str = None) -> BytesIO:
    """Converte um DataFrame em PNG com linhas curtas,
    título acima da tabela, sem timestamp e com borda.
    """
    n_rows, n_cols = df.shape

    fig_width = max(10, n_cols * 2.5)
    fig_height = max(7.5, (n_rows * 0.2) + 10.0)

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.axis("off")

    # --- TABELA (posicionada na parte superior da figura) ---
    # Logo: 1200px tall * zoom 0.22 = 264px rendered.
    # At 200dpi, fig_height=7.5" → 1500px. Logo occupies ~264/1500 = 0.176 of fig height.
    # We give the bottom 30% to the logo with some padding, table sits above that.
    table_bottom = 0.55
    table_height = 0.26

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="center",
        bbox=[0.0, table_bottom, 1.0, table_height]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(12)

    # Altura das linhas muito reduzida
    table.scale(1.2, 0.07)

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

    # --- TÍTULO acima da tabela ---
    if title:
        # Posicionamos o título logo acima do topo da tabela
        title_y = table_bottom + table_height + 0.02
        fig.text(0.5, title_y, title, ha='center', va='bottom',
                 fontsize=22, fontweight='bold', color='#333333')

    # --- LOGO SECTION ---
    if logo_path:
        try:
            logo = Image.open(logo_path)
            imagebox = OffsetImage(logo, zoom=0.22)
            # Logo centered in space below table, with a small gap (table_bottom - 0.05) / 2
            logo_y = (table_bottom - 0.06) / 2
            ab = AnnotationBbox(
                imagebox, (0.5, logo_y),
                xycoords='figure fraction',
                frameon=False,
                box_alignment=(0.5, 0.5)
            )
            fig.add_artist(ab)
        except Exception as e:
            print(f"Logo error: {e}")

    plt.subplots_adjust(top=0.97, bottom=0.02, left=0.03, right=0.97)

    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=200, facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf

