import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from src.dataclass import Data


def dolars_month_gen(data: Data) -> pd.DataFrame:
    """
    Funcion que genera un dataframe con los valores
    de los diferentes dolares y los agrupa por mes
    """
    dolars: pd.DataFrame = pd.merge(data.usd, data.usd_of, on="date").rename(
        columns={"v_x": "blue", "v_y": "oficial"}
    )

    dmonth: pd.DataFrame = (
        dolars.resample("MS", on="date").mean().reset_index()
    )
    return dmonth


def politic_gen(data: Data) -> pd.DataFrame:
    """
    Funcion que genera un dataframe con los eventos
    politicos
    """
    return (
        data.milestones.copy()
        .rename({"t": "entidad", "e": "nombre"}, axis=1)
        .astype({"entidad": "string", "nombre": "string"})
    )


def dolar_events_plot(data: Data, plot: bool = False) -> None:
    """
    Consigna: Con la info histórica del valor del dólar y del blue,
    realizar un análisis exploratorio. Cruzar la data con sucesos importantes
    a nivel político-económico y graficar mes a mes.

    Parameter
    ---------
    data: Data
        AttribDict que contiene
        todos los dataframes que consultamos a la API
    """
    dolar_month: pd.DataFrame = dolars_month_gen(data)
    politic: pd.DataFrame = politic_gen(data)
    politic_month: pd.DataFrame = politic_gen(data)

    politic_month.date = (
        politic_gen(data).date.dt.strftime("%Y%m").astype({"date": np.int32})
    )

    politic_dolar: pd.DataFrame = (
        pd.merge(dolar_month, politic, on="date", how="left")
        .fillna(method="ffill")
        .dropna()
    ).rename(columns={"e": "nombre", "t": "entidad"})

    # borro registros de antes del 2002 07 -- Cuidado! recursivo
    politic_month = politic_month.drop(index=np.arange(0, 20)).reset_index(
        drop=True
    )

    colors = {
        "econ": "royalblue",
        "bcra": "cornflowerblue",
        "misc": "lightsteelblue",
        "fina": "slategrey",
        "trea": "silver",
    }

    _, ax1 = plt.subplots()
    i = -1
    x_ticks = list()

    for be, ne in zip(politic_month.date.shift(), politic_month.date):
        i += 1
        if politic_month.entidad.iloc[i] == "pres":
            x_ticks.append(politic_month.date.iloc[i])
            ax1.axvline(be, color="teal", linestyle="--")
        else:
            color: str = colors[politic_month.entidad.iloc[i]]
            ax1.axvspan(be, ne, facecolor=color, alpha=0.5)

    ax2 = ax1.twiny()

    ax2.plot(politic_dolar.date, politic_dolar.blue, color="black")
    ax2.plot(politic_dolar.date, politic_dolar.oficial, color="grey")

    # Config
    ax1.set_xticks(x_ticks)
    ax1.set_xticklabels(["Nestor", "Cristina", "Cristina", "Macri", "Alberto"])
    ax2.set_yscale("log")
    ax2.set_yticks([5, 10, 20, 40, 80, 160, 300])
    ax2.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

    ax2.legend(
        ["Dolar Blue", "Dolar Oficial"], loc="lower right", frameon=True
    )

    plt.xlabel("Dolar vs Eventos politicos")
    plt.savefig("../plots/dolar_events.png")

    if plot:
        plt.show()
    plt.cla()
    plt.clf()
