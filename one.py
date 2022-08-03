import datetime as dt
import pandas as pd
import numpy as np

from docs import STDOUT, get_data_usage, doble_template, week_var_template
from dtypes import UsdType, JSON, WeekSamples, Endpoints, Frame
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
        pd.DataFrame(data)
        .rename(columns=columns)
        # .astype({'date': })
    )
    df["date"] = (
        pd.to_datetime(df["date"]).dt.date.astype(np.datetime64)
    )
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

            content: list[pd.DataFrame] = [
                to_dataframe(json) for json in resp
            ]

            data = dict(zip(points, content))

            super(Data, self).__init__(data)
            return self


def last_year(data: pd.DataFrame) -> pd.DataFrame:
    day_365 = dt.datetime.today() - dt.timedelta(days=365)
    return (
        data.loc[data["date"] >= day_365]
        .reset_index()
        .drop('index', axis=1)
    )


def name_var(var: Any) -> str:
    return [name for name in globals() if globals()[name] is var][0]


def save_record(data: pd.DataFrame) -> None:
    data.to_csv(f'./{name_var(data)}')


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
        last_var
        .loc[last_var["v"] == last_var["v"].max(), "date"]
        .dt.date.values[0].strftime("%Y-%m-%d")
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
        .drop(['v'], axis=1)
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
        week_var[0]
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

    """
    index_: dict[int, str] = {
        0: 'Lunes',
        1: 'Martes',
        2: 'Miercoles',
        3: 'Jueves',
        4: 'Viernes',
    }

    last_data = last_year(var_data)
    weekday = last_data.groupby(last_data.date.dt.weekday).mean()

    return (
        weekday.rename(index=index_)
        .sort_values(by='v', ascending=False)
     )



def main():
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
            f'{i}          {j}'
            for i, j in zip(
                b(data.usd, 'v').to_string().split('\n'),
                b(data.usd_of, 'v').to_string().split('\n')
            )
        ]
    )
    out_c: str = week_var_template % c(data.var_usd_vs_usd_of)


    print(
        STDOUT.format(
            out_a,
            out_b,
            out_c
        )
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

        """
        index_: dict[int, str] = {
            0: 'Lunes',
            1: 'Martes',
            2: 'Miercoles',
            3: 'Jueves',
            4: 'Viernes',
        }

        last_data = last_year(var_data)
        weekday = last_data.groupby(last_data.date.dt.weekday).mean()

        return (
            weekday.rename(index=index_)
            .sort_values(by='v', ascending=False)
         )




if __name__ == "__main__":
    main()
