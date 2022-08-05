BANNER: str = """

██╗░░██╗███████╗███╗░░██╗██████╗░██╗░░░██╗  ██████╗░██╗  ░░███╗░░
██║░░██║██╔════╝████╗░██║██╔══██╗╚██╗░██╔╝  ██╔══██╗██║  ░████║░░
███████║█████╗░░██╔██╗██║██████╔╝░╚████╔╝░  ██████╔╝██║  ██╔██║░░
██╔══██║██╔══╝░░██║╚████║██╔══██╗░░╚██╔╝░░  ██╔═══╝░██║  ╚═╝██║░░
██║░░██║███████╗██║░╚███║██║░░██║░░░██║░░░  ██║░░░░░██║  ███████╗
╚═╝░░╚═╝╚══════╝╚═╝░░╚══╝╚═╝░░╚═╝░░░╚═╝░░░  ╚═╝░░░░░╚═╝  ╚══════╝
"""

STDOUT: str = (
    """
%s


[ * ] Respuestas a las consignas propuestas [ * ]


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


[>] Día de la semana donde hay mayor variación
    en la brecha el ultimo año
{}


Regresion Lineal
----------------

[>] Dolar blue

{}


[>] Dolar oficial

{}

"""
    % BANNER
)


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


def test_docs():
    """
    Documentacion.
    Esto es una prueba, intenta con otras funciones

    >>> func().__doc__
    """
