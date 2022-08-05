import pandas as pd
import numpy as np
import datetime as dt

import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

from dateutil.relativedelta import relativedelta
from typing import Optional


def regression(
    data: pd.DataFrame,
    month: int,
    verbose: bool = False,
    plot: bool = False,
    save_plot: Optional[str] = None,
) -> str:
    """
    La regresion lleva consigo mucho error, Esto se debe a que
    el dolar en argentina crece de forma casi exponencial;
    por este motivo realize un logaritmo natural a los precios.

    Parameters
    ----------
    data: DataFrame
        Data del tipo de dolar al cual
        se le va a hacer la regresion
    month: integer
        Mes a predecir
    verbose: bool (Default False)
        Llamar True si se quiere ver
        los errores y scores del modelo
    plot: bool (Default False)
        Llamar True si se quiere ver
        el plot, equivalente a hacer plt.show()
    save_plot: string Opcional
        Este string sera el nombre con el
        que se va a guardar la imagen del plot
        en el directorio API_BCRA/plots

    return
    ------
    Retorna un string con la informacion del modelo
    """
    df = data.copy()

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

    if plot or save_plot:
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

        if save_plot:
            plt.savefig(f"../plots/{save_plot}.png")
        elif plot:
            plt.show()
        plt.cla()

    if verbose:
        return (
            "Error en Train: %.2f \n"
            % mean_squared_error(y_train, y_train_pred)
            + "Error en Test: %.2f \n"
            % mean_squared_error(y_test, y_test_pred)
            + "Score test: %.2f \n" % model.score(X_test, y_test)
            + "Score train: %.2f \n\n" % model.score(X_train, y_train)
            + "Prediccion a %i meses: %.2f" % (month, prediction)
        )
    else:
        return "Prediccion a %i meses: %.2f" % (month, prediction)
