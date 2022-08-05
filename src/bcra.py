import pandas as pd
import numpy as np

from typing import Optional

from src.docs import STDOUT, doble_template, week_var_template
from src.dtypes import JSON, Endpoints
from src.api import API
from src.consignas import a, b, c, d

from src.event_dolar import dolar_events_plot

from src.regression import regression


def to_dataframe(
    data: JSON, v: Optional[str] = None, col: Optional[dict] = None
) -> pd.DataFrame:
    """
    Esta funcion convierte en dataframe los response del API

    Parameter
    ---------
    data: JSON
        Este debe ser el dato que el api nos devuelve
    v: Optional - string
        Nuevo nombre de la columna caracteristica
        de esta API "v"
    col: Optional - dict
        Diccionario con los nombres de la columna
        del dataframe como key y el nuevo nombre como value

    Return
    ------
    DataFrame con los datos ingresados

    Examples
    --------
    >>> response_usd
    '{"date":{"0":959126400000,"1":959212800000,"2":959299200000,
    "3":959558400000,"4":959644800000},"v":{"0":1.0005,"1":1.0005,
    "2":1.0004,"3":1.0007,"4":1.0009}}'

    >>> to_dataframe(response_usd)
            date       v
    0 2000-05-24  1.0005
    1 2000-05-25  1.0005
    2 2000-05-26  1.0004
    3 2000-05-29  1.0007
    4 2000-05-30  1.0009

    >>> to_dataframe(response_usd, v='precio')
            date  precio
    0 2000-05-24  1.0005
    1 2000-05-25  1.0005
    .        ...     ...

    >>> response_milestones.columns
    Index(['date', 'e', 't'], dtype='object')

    >>> response_milestones
    '{"date":{"0":665712000000},
    "e":{"0":"Roque Fern\\u00e1ndez"},"t":{"0":"bcra"}}'

    >>> to_dataframe(
    ...     response_milestones,
    ...     {"e": "name", "t": "entity"}
    ... )
            date             name  entity
    0 1991-02-05  Roque Fernández  bcra
    """

    columns: dict[str, str] = {"d": "date"}
    if v:
        columns["v"] = v
    if col:
        columns.update(col)

    df: pd.DataFrame = pd.DataFrame(data).rename(columns=columns)
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


def main() -> None:
    """
    Funcion que muestra por pantalla las consignas,
    ejecutan las funciones del proyecto y guarda los plots
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

    # Formating Console output
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

    # Regresion sobre el dolar blue
    out_reg_blue: str = regression(data.usd, 3, verbose=True, save_plot='blue_regresion')
    out_reg_blue += "\n" + regression(data.usd, 6)
    out_reg_blue += "\n" + regression(data.usd, 12)

    # Regresion sobre el dolar oficial
    out_reg_of: str = regression(data.usd_of, 3, verbose=True, save_plot='oficial_regresion')
    out_reg_of += "\n" + regression(data.usd_of, 6)
    out_reg_of += "\n" + regression(data.usd_of, 12)

    print(STDOUT.format(out_a, out_b, out_c, out_d, out_reg_blue, out_reg_of))

    # Plot comparativo entre los eventos y el dolar
    dolar_events_plot(data)


if __name__ == "__main__":
    main()
