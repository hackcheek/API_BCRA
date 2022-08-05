import pandas as pd
import numpy as np
import datetime as dt

from .dtypes import Frame, WeekSamples

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


def last_year(data: pd.DataFrame) -> pd.DataFrame:
    """
    Filtro para dataframes, que toma los datos del ultimo año

    Parameter
    ---------
    data: DataFrame
        Este dataframe debe contener una columna llamada date
        y estar en formato datetime

    Return
    ------
    DataFrame con registros del ultimo año

    Example
    -------
    >>> data.usd
               date         v
    0    2000-05-24    1.0005
    1    2000-05-25    1.0005
    4    2000-05-30    1.0009
    ...         ...       ...
    5561 2022-07-28  314.0000
    5564 2022-08-02  291.0000
    5565 2022-08-03  298.0000

    >>> last_year(data.usd)
              date      v
    0   2021-08-05  180.5
    1   2021-08-06  178.5
    2   2021-08-09  179.0
    ..         ...    ...
    241 2022-08-01  282.0
    242 2022-08-02  291.0
    243 2022-08-03  298.0
    """
    day_365 = dt.datetime.today() - dt.timedelta(days=365)
    return (
        data.loc[data["date"] >= day_365].reset_index().drop("index", axis=1)
    )
