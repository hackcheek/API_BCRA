import typing as T
import numpy as np
import pandas as pd


import aiohttp
import asyncio

from dataclasses import dataclass
from pandas.core import resample

JSON: T.TypeAlias = None | int | str | bool | list[T.Any] | dict[T.Any, T.Any]
JSONList: T.TypeAlias = list[JSON]
Coroutine: T.TypeAlias = T.Coroutine
HTTPSession: T.TypeAlias = aiohttp.ClientSession
WeekSamples: T.TypeAlias = resample.Resampler
JSONapi: T.TypeAlias = list[T.Coroutine[T.Any, T.Any, list[JSON]]]
Frame: T.TypeAlias = pd.DataFrame | pd.Series



@dataclass(slots=True, frozen=True)
class UsdType:
    date: np.datetime64
    price: np.float16


Endpoints: T.TypeAlias = T.Literal[
    'milestones',
    'base',
    'base_usd',
    'base_usd_of',
    'reservas',
    'base_div_res',
    'usd',
    'usd_of',
    'usd_of_minorista',
    'var_usd_vs_usd_of',
    'circulacion_monetaria',
    'billetes_y_monedas',
    'efectivo_en_ent_fin',
    'depositos_cuenta_ent_fin',
    'depositos',
    'cuentas_corrientes',
    'cajas_ahorro',
    'plazo_fijo',
    'tasa_depositos_30_dias',
    'prestamos',
    'tasa_prestamos_personales',
    'tasa_adelantos_cuenta_corriente',
    'porc_prestamos_vs_depositos',
    'lebac',
    'leliq',
    'lebac_usd',
    'leliq_usd',
    'leliq_usd_of',
    'tasa_leliq',
    'm2_privado_variacion_mensual',
    'cer',
    'uva',
    'uvi',
    'tasa_badlar',
    'tasa_baibar',
    'tasa_tm20',
    'tasa_pase_activas_1_dia',
    'tasa_pase_pasivas_1_dia',
    'inflacion_mensual_oficial',
    'inflacion_interanual_oficial',
    'inflacion_esperada_oficial',
    'dif_inflacion_esperada_vs_interanual',
    'var_base_monetaria_interanual',
    'var_usd_interanual',
    'var_usd_oficial_interanual',
    'var_merval_interanual',
    'var_usd_anual',
    'var_usd_of_anual',
    'var_merval_anual',
    'merval',
    'merval_usd',
]
