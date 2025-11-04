"""
Este script analiza las cifras de personas desaparecidas
desde una perspectiva demográfica.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go


# Todas las gráficas de este script
# van a compartir el mismo esquema de colores.
PLOT_COLOR = "#171010"
PAPER_COLOR = "#2B2B2B"

# La fecha en la que los datos fueron recopilados.
FECHA_FUENTE = "01/11/2025"


# Estos serán nuestros grupos etarios.
EDADES = [
    (0, 4),
    (5, 9),
    (10, 14),
    (15, 19),
    (20, 24),
    (25, 29),
    (30, 34),
    (35, 39),
    (40, 44),
    (45, 49),
    (50, 54),
    (55, 59),
    (60, 64),
    (65, 69),
    (70, 74),
    (75, 79),
    (80, 84),
    (85, 120),
]


def tasa_edad(año):
    """
    Crea una gráfica de dispersión mostrando las distintas
    tasas de personas desaparecidas, separadas por grupo de edad y sexo.

    Parameters
    ----------
    año : int
        El año que nos interesa graficar.

    """

    # Cargamos el dataset de personas desaparecidas.
    df = pd.read_csv("./data.csv", dtype={"CVE_ENT": str})

    # Seleccionamos un registro por víctima.
    df = df.groupby("ID_VICTIMA").last()

    # Limpiamos valores confidenciales.
    df = df.replace("CONFIDENCIAL", np.nan)

    # Convertimos las fechas a DateTime.
    df["FECHA_DESAPARICION"] = pd.to_datetime(df["FECHA_DESAPARICION"], errors="coerce")
    df["FECHA_REGISTRO"] = pd.to_datetime(df["FECHA_REGISTRO"], errors="coerce")
    df["FECHA_NACIMIENTO"] = pd.to_datetime(df["FECHA_NACIMIENTO"], errors="coerce")

    # Vamos a preferir la fecha de desaparición.
    # Pero cuando no esté disponible usaremos la fecha de registro.
    df["FECHA_DESAPARICION"] = df["FECHA_DESAPARICION"].fillna(df["FECHA_REGISTRO"])

    # Seleccionamos los registros del año de nuestro interés.
    df = df[df["FECHA_DESAPARICION"].dt.year == año]

    # calculamos la edad al momento de la desaparición.
    df["EDAD"] = df["FECHA_DESAPARICION"].dt.year - df["FECHA_NACIMIENTO"].dt.year

    data = list()

    # Iteramos sobre todos nuestros grupos de edad y contamos los registros
    # para cada uno.
    for a, b in EDADES:
        temp_mujeres = df[(df["SEXO"] == "MUJER") & (df["EDAD"].between(a, b))]
        temp_hombres = df[(df["SEXO"] == "HOMBRE") & (df["EDAD"].between(a, b))]

        # Para el último grupo de edad le agregamos el símbolo de 'mayor o igual que'
        # para que coincida con el índice de los datasets de población quinquenal.
        data.append(
            {
                "edad": f"{a}-{b}" if a < 85 else "≥85",
                "mujeres": len(temp_mujeres),
                "hombres": len(temp_hombres),
            }
        )

    # Creamos un DataFrame con los conteos de cada grupo de edad y sexo.
    final = pd.DataFrame.from_records(data, index="edad")

    # Cargamos el dataset de la población de hombres por grupos de edad.
    hombres_pop = pd.read_csv("./assets/poblacion_quinquenal/hombres.csv", index_col=0)

    # Seleccionamos la población del año que nos interesa.
    hombres_pop = hombres_pop[str(año)]

    # Agregamos la columna de población de hombres.
    final["poblacion_hombres"] = hombres_pop

    # Calculamos la tasa por cada 100k hombres para cada grupo de edad.
    final["tasa_hombres"] = final["hombres"] / final["poblacion_hombres"] * 100000

    # Cargamos el dataset de la población de mujeres por grupos de edad.
    mujeres_pop = pd.read_csv("./assets/poblacion_quinquenal/mujeres.csv", index_col=0)

    # Seleccionamos la población del año que nos interesa.
    mujeres_pop = mujeres_pop[str(año)]

    # Agregamos la columna de población de mujeres.
    final["poblacion_mujeres"] = mujeres_pop

    # Calculamos la tasa por cada 100k mujeres para cada grupo de edad.
    final["tasa_mujeres"] = final["mujeres"] / final["poblacion_mujeres"] * 100000

    fig = go.Figure()

    # Agregamos la gráfica de dispersión para hombres.
    fig.add_trace(
        go.Scatter(
            x=final.index,
            y=final["tasa_hombres"],
            mode="markers",
            name=f"<b>Hombres</b><br>{final['hombres'].sum():,.0f} víctimas",
            marker_color="#00e5ff",
            marker_symbol="circle-open",
            marker_size=36,
            marker_line_width=5,
        )
    )

    # Agregamos la gráfica de dispersión para mujeres.
    fig.add_trace(
        go.Scatter(
            x=final.index,
            y=final["tasa_mujeres"],
            mode="markers",
            name=f"<b>Mujeres</b><br>{final['mujeres'].sum():,.0f} víctimas",
            marker_color="#ffea00",
            marker_symbol="diamond-open",
            marker_size=36,
            marker_line_width=5,
        )
    )

    fig.update_xaxes(
        range=[-0.7, len(final) - 0.3],
        ticks="outside",
        ticklen=10,
        zeroline=False,
        tickcolor="#FFFFFF",
        linewidth=2,
        showline=True,
        showgrid=True,
        gridwidth=0.5,
        mirror=True,
        nticks=len(final) + 1,
    )

    fig.update_yaxes(
        title="Tasa por cada 100,000 hombres/mujeres dentro del grupo de edad",
        title_font_size=20,
        ticks="outside",
        separatethousands=True,
        ticklen=10,
        title_standoff=15,
        tickcolor="#FFFFFF",
        linewidth=2,
        gridwidth=0.5,
        showline=True,
        nticks=20,
        zeroline=True,
        mirror=True,
    )

    # Personalizamos la leyenda y agregamos las anotaciones correspondientes.
    fig.update_layout(
        showlegend=True,
        legend_itemsizing="constant",
        legend_borderwidth=1,
        legend_bordercolor="#FFFFFF",
        legend_x=0.99,
        legend_y=0.98,
        legend_xanchor="right",
        legend_yanchor="top",
        width=1920,
        height=1080,
        font_family="Montserrat",
        font_color="#FFFFFF",
        font_size=24,
        title_text=f"Tasas de incidencia de personas desaparecidas en México durante {año} según edad y sexo",
        title_x=0.5,
        title_y=0.965,
        margin_t=80,
        margin_r=40,
        margin_b=120,
        margin_l=130,
        title_font_size=36,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        annotations=[
            dict(
                x=0.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="left",
                yanchor="top",
                text=f"Fuente: RNPDNO ({FECHA_FUENTE})",
            ),
            dict(
                x=0.5,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="center",
                yanchor="top",
                text="Grupo de edad al momento de la desaparición",
            ),
            dict(
                x=1.01,
                y=-0.11,
                xref="paper",
                yref="paper",
                xanchor="right",
                yanchor="top",
                text="🧁 @lapanquecita",
            ),
        ],
    )

    fig.write_image(f"./tasa_edad_{año}.png")


if __name__ == "__main__":
    tasa_edad(2025)
