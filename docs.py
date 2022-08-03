# Order of variables in format (a, b, c, d, e, f1, f2, f3, g, h)
STDOUT: str = """
________________________________________________

Realizacion del proyecto 1 de henry.
Interesado en consultas a APIs y manejo de datos
________________________________________________



DATA últimos 365 días:
---------------------

[>] Dia con mayor variacion
    entre dolar blue y dolar official

{}


[>] Top 5 dias con mayor volatilidad
    comparando el dolar blue con el oficial

Dolar blue                        Dolar Oficial
----------                        -------------
{}


[>] Semana con mayor variación en la brecha
{}
"""


doble_template: str = """\
{}
{}
{}
{}
{}
{}
"""

week_var_template: str = """\
Desde %s hasta %s
Con una variacion de %.2f%%
"""


get_data_usage: str = """
Usage:
>>> data = Data.get_data([Endpoints])
"""
