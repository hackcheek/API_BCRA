from src.docs import STDOUT, doble_template, week_var_template
from src.dtypes import Endpoints
from src.consignas import a, b, c, d
from src.event_dolar import dolar_events_plot
from src.regression import regression
from src.dataclass import Data


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
    out_reg_blue: str = regression(
        data.usd, 3, verbose=True, save_plot="blue_regresion"
    )
    out_reg_blue += "\n" + regression(data.usd, 6)
    out_reg_blue += "\n" + regression(data.usd, 12)

    # Regresion sobre el dolar oficial
    out_reg_of: str = regression(
        data.usd_of, 3, verbose=True, save_plot="oficial_regresion"
    )
    out_reg_of += "\n" + regression(data.usd_of, 6)
    out_reg_of += "\n" + regression(data.usd_of, 12)

    print(STDOUT.format(out_a, out_b, out_c, out_d, out_reg_blue, out_reg_of))

    # Plot comparativo entre los eventos y el dolar
    dolar_events_plot(data)


if __name__ == "__main__":
    main()
