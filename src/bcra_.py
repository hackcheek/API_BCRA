import datetime as dt
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns

from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from dateutil.relativedelta import relativedelta

from docs import STDOUT, get_data_usage, doble_template, week_var_template
from dtypes import UsdType, JSON, WeekSamples, Endpoints, Frame, MonthSamples
from typing import Optional, Any, Iterable, Coroutine
from api import API


def to_dataframe(
    data: JSON, v: Optional[str] = None, col: Optional[dict] = None
) -> pd.DataFrame:

    columns: dict[str, str] = {"d": "date"}
    if v:
        columns["v"] = v
    if col:
        columns.update(col)

    df: pd.DataFrame = (
        pd.DataFrame(data).rename(columns=columns)
        # .astype({'date': })
    )
    df["date"] = pd.to_datetime(df["date"]).dt.date.astype(np.datetime64)
    return df


class Data(dict):
    def __init__(self, *args, **kwargs):
        super(Data, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def call_api(self, *points: Endpoints):
        """
        Extraer la data proveniente
        de la API estadisticasbcra.com

        Parameter
        ---------
        points : list of strings
            Este debe contener una lista con los endpoints
            correspondientes a el API
            https://estadisticasbcra.com/api/documentacion

        Examples
        --------
        >>> data: list[JSON] = Data().call_api('usd', 'usd_of')
        >>> data
        [{...api content...}]

        Usar este metodo es una mala forma
        de llenar una variable con los datos que requerimos
        >>> usd = data.call_api('usd') # X

        Una buena practica seria
        ejecutar el codigo de la siguiente forma
        >>> data = Data()
        >>> data.call_api('usd', 'usd_of')
        >>> usd: pd.DataFrame = data.usd
        >>> usd_of: pd.DataFrame = data.usd_of
        """
        if not self.__dict__:
            api: API = API()
            resp = api.query(*points)

            content: list[pd.DataFrame] = [to_dataframe(json) for json in resp]

            data = dict(zip(points, content))

            super(Data, self).__init__(data)
            return self


def last_year(data: pd.DataFrame) -> pd.DataFrame:
    day_365 = dt.datetime.today() - dt.timedelta(days=365)
    return (
        data.loc[data["date"] >= day_365].reset_index().drop("index", axis=1)
    )


# consignas
def a(var_usd: pd.DataFrame) -> dt.datetime:
    """
    Consigna:
    Retorna el Día con mayor variación
    en la brecha del ultimo año

    Parameter
    ---------
    var_usd: DataFrame con columna 'v'.
        Variable a medir
        el mayor porcentaje de dicha columna

    Return
    ------
    Datetime:
        Fecha objetivo, "El dia d mayor variacion"

    Example
    -------
    >>> var_usd = pd.DataFrame({
    ...     'date': ['2022-03-04', '2002-03-05',
    ...              '2022-03-06', '2002-03-07'],
    ...     'variation': [5.4726, 6.5327,
    ...                   4.3902, 3.7383]
    ... })
    >>> a(var_usd)
    2022-03-04
    """
    last_var: pd.DataFrame = last_year(var_usd)

    return (
        last_var.loc[last_var["v"] == last_var["v"].max(), "date"]
        .dt.date.values[0]
        .strftime("%Y-%m-%d")
    )


def b(data: pd.DataFrame, col: str) -> Frame:
    """
    Consigna:
    Retorna los 5 días con mayor volatilidad del ultimo año

    Parameter
    ---------
    data: DataFrame con columna 'date'
        Necesario que contenga esta columna
        ya que esta se usara como referencia
        a la hora de calcular la volatilidad
    col: str
        columna a procesar y calcular la volatilidad
        de cada una de sus filas

    Return
    ------
    :: Frame
    date:
        columna comparativa
    volatility:
        columna con el top de volatilidades

    Example
    -------
    >>> data = pd.DataFrame({
    ... 'date': [2022-08-01, 2022-08-29, 2022-07-28, ...]
    ... 'price': [282, 296, 314, ...]
    ... })
    >>> b(data)
            date  volatility
    0 2022-07-04    0.084218
    1 2022-07-21    0.061181
    2 2022-07-08    0.060396
    3 2022-07-29    0.059034
    4 2022-07-20    0.051792
    """
    vol: pd.DataFrame = last_year(data)
    vol["volatility"] = abs(np.log(vol[col] / vol[col].shift()))

    return (
        vol.sort_values(by="volatility", ascending=False)
        .drop([col], axis=1)
        .head(5)
        .reset_index(drop=True)
    )


def c(data_var: pd.DataFrame) -> tuple[str, str, float]:
    """
    Consigna:
    Semana con mayor variación en la brecha del ultimo año

    Parameter
    ---------
    data_var: DataFrame de variacion entre usd y usd_of

    Return
    ------
    :: tupla
    string:
        Dia del comienzo de semana ganadora
    string:
        Dia del final de semana ganadora
    float:
        Porcentaje de variacion ganador

    Example
    -------
    >>> c(data.var_usd_vs_usd_of)
    ('2022-07-18', '2022-07-22', 34.72449999999999)
    """
    weeks: WeekSamples = last_year(data_var).resample("W-FRI", on="date")
    min_var: pd.Series = weeks.v.min()
    max_var: pd.Series = weeks.v.max()

    week_var: pd.Series = (max_var - min_var).sort_values(ascending=False)
    last_week: dt.timedelta = dt.timedelta(days=4)

    start_week = week_var.keys()[0] - last_week

    data_var.tail(11)

    return (
        start_week.date().strftime("%Y-%m-%d"),
        week_var.keys()[0].date().strftime("%Y-%m-%d"),
        week_var[0],
    )


def d(var_data: pd.DataFrame) -> pd.DataFrame:
    """
    Consigna:
    Día de la semana donde hay mayor variación
    en la brecha el ultimo año

    Parameter
    ---------
    var_data: Dataframe con columna 'date' y 'v'
        Necesario para poder agrupar por los llamados weekdays
        y asi sacar un promedio de 'v'

    Return
    ------
    :: Dataframe
    date:
        Indice con los dias de la semana (target feature)
    v:
        Columna de valores promediados y
        agrupados por los dias de la semana

    Example
    -------
    >>> d(data.var_usd_vs_usd_of)
                       v
    date
    Jueves     92.954272
    Miercoles  92.953049
    Viernes    92.570404
    Martes     92.120416
    Lunes      91.474823
    """
    index_: dict[int, str] = {
        0: "Lunes",
        1: "Martes",
        2: "Miercoles",
        3: "Jueves",
        4: "Viernes",
    }

    last_data: pd.DataFrame = last_year(var_data)
    weekday: pd.DataFrame = last_data.groupby(last_data.date.dt.weekday).mean()

    return weekday.rename(index=index_).sort_values(by="v", ascending=False)


def regression(point: str, month: int):
    """
        La regresion lleva consigo mucho error, Esto se debe a que
    la historia del dolar en argentina crece de forma casi exponencial;
    por este motivo realize un logaritmo natural a los precios.
        No considero que recortar el historico sea buena practica.
    """
    df = data[point].copy()

    X = df.date.apply(lambda x: x.toordinal()).values.reshape(-1, 1)
    y = np.log(df.v.values.reshape(-1, 1))

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=50
    )

    model = LinearRegression()
    model.fit(X, y)

    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    pred_date = np.array(
        (dt.datetime.today() + relativedelta(months=month)).toordinal()
    ).reshape(1, -1)

    prediction = np.exp(model.predict(pred_date))

    _, ax1 = plt.subplots()

    ax1.plot(df.date, np.log(df.v), color="grey")

    ax2 = ax1.twiny()
    ax2.plot(
        X_train,
        y_train_pred,
        color="black",
        linestyle="--",
        label="Train",
        alpha=0.5,
    )
    ax2.plot(X_test, y_test_pred, color="black", label="Test", alpha=0.5)

    ax1.set_yticks([])
    ax1.set_xticks([])
    ax2.set_yticks([])
    ax2.set_xticks([])

    plt.legend(loc="upper left")
    plt.show()

    print("Error en Train: %.2f" % mean_squared_error(y_train, y_train_pred))
    print("Error en Test: %.2f" % mean_squared_error(y_test, y_test_pred))
    print("Score test: %.2f" % model.score(X_test, y_test))
    print("Score train: %.2f\n" % model.score(X_train, y_train))
    print("Prediccion a %i meses: %.2f" % (month, prediction))


def main() -> None:
    """
    Main function of the program.
    It prints answers and controls program flow.
    """

    points: list[Endpoints] = [
        "usd",
        "usd_of",
        "var_usd_vs_usd_of",
        "inflacion_mensual_oficial",
        "var_usd_anual",
        "var_usd_of_anual",
        "milestones",
    ]

    # Init data vars
    data = Data()
    data.call_api(*points)

    out_a: str = a(data.var_usd_vs_usd_of)
    out_b: str = doble_template.format(
        *[
            f"{i}          {j}"
            for i, j in zip(
                b(data.usd, "v").to_string().split("\n"),
                b(data.usd_of, "v").to_string().split("\n"),
            )
        ]
    )
    out_c: str = week_var_template % c(data.var_usd_vs_usd_of)
    out_d: str = d(data.var_usd_vs_usd_of).to_string()

    # Junto los dolares y agrupo por meses
    def dolars_month_gen() -> pd.DataFrame:
        dolars: pd.DataFrame = pd.merge(
            data.usd, data.usd_of, on="date"
        ).rename(columns={"v_x": "blue", "v_y": "oficial"})

        dmonth: pd.DataFrame = (
            dolars.resample("MS", on="date").mean().reset_index()
        )
        # dmonth.date = dmonth.date.dt.to_period('M')
        return dmonth

    # Asigno meses a date de los politicos
    def politic_gen() -> pd.DataFrame:
        return (
            data.milestones.copy()
            .rename({"t": "entidad", "e": "nombre"}, axis=1)
            .astype({"entidad": "string", "nombre": "string"})
        )

    # Left join entre dolars_month y politicts
    def pol_dol_gen() -> pd.DataFrame:
        pol_dol: pd.DataFrame = (
            pd.merge(
                dolars_month_gen(), data.milestones, on="date", how="left"
            )
            .fillna(method="ffill")
            .dropna()
        ).rename(columns={"e": "nombre", "t": "entidad"})

        return pol_dol.astype({"nombre": "string", "entidad": "string"})

    dolar_month: pd.DataFrame = dolars_month_gen()
    politic: pd.DataFrame = politic_gen()
    politic_dolar: pd.DataFrame = pol_dol_gen()

    # para el ejercicio
    # grafico 1, precios nombres y entidades

    politic_month: pd.DataFrame = politic_gen()
    politic_month.date = (
        politic_gen().date.dt.strftime("%Y%m").astype({"date": np.int32})
    )
    # borro registros de antes del 2002 07 -- Danger
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

    # Ejercicio e
    def dolar_events_plot() -> None:
        fig, ax1 = plt.subplots()
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
        ax1.set_xticklabels(
            ["Nestor", "Cristina", "Cristina", "Macri", "Alberto"]
        )
        ax2.set_yscale("log")
        ax2.set_yticks([5, 10, 20, 40, 80, 160, 300])
        ax2.get_yaxis().set_major_formatter(
            matplotlib.ticker.ScalarFormatter()
        )

        plt.xlabel("Dolar vs Eventos politicos")
        plt.savefig("./plots/dolar_events.png")
        plt.show()

    dolar_events_plot()

    regression("usd", 12)

    # politic_dolar.date = (
    # politic_gen().date.dt.strftime('%Y%m')
    # .astype({'date': np.int32})
    # )

    # para la correlacion

    le = LabelEncoder()

    politic_dolar["nombre_le"] = le.fit_transform(politic_dolar.nombre)
    politic_dolar["entidad_le"] = le.fit_transform(politic_dolar.entidad)

    pol_dol_corr: pd.DataFrame = politic_dolar

    pol_dol_corr["blue_vol"] = abs(
        np.log(pol_dol_corr.blue / pol_dol_corr.blue.shift())
    )
    pol_dol_corr["oficial_vol"] = abs(
        np.log(pol_dol_corr.oficial / pol_dol_corr.oficial.shift())
    )

    volatility_corr: pd.DataFrame = (
        pol_dol_corr.dropna()
        .drop(["date", "blue", "oficial", "nombre", "entidad"], axis=1)
        .groupby(["nombre_le", "entidad_le"])
        .sum()
        .reset_index()
    )
    volatility_corr

    sns.heatmap(volatility_corr.corr().abs(), cmap="binary", annot=True)
    plt.savefig("./plots/volatility_corr.png")
    plt.show()

    print(STDOUT.format(out_a, out_b, out_c, out_d, "hola"))


if __name__ == "__main__":
    main()
