import aiohttp
import asyncio

from src.dtypes import HTTPSession, Endpoints
from typing import Iterable


TOKEN: str = "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTA5ODM0MTUsInR5cGUiOiJleHRlcm5hbCIsInVzZXIiOiJ5b3VuZ2NoZWVrbXVzaWNAZ21haWwuY29tIn0.-HMdi7GRhhpec1FSuJ5A0SV38vjjtKVM_dYi6vuVk6jDsM2QVUh5yOTP7gGC3qeaqOABu3eiZGKdKQf-xsM34Q"


class AsyncRequest:
    """
    Clase local para ser llamada por la clase API
    """

    _session: HTTPSession | None = None

    @classmethod
    async def __aenter__(cls) -> None:
        cls._session = aiohttp.ClientSession()
        return cls

    @classmethod
    async def __aexit__(cls, *err: tuple) -> None:
        await cls._session.close()
        cls._session = None
        cls._errors = err
        return cls

    @classmethod
    async def _get(
        cls, url: str, header: dict | None = None, data: dict | None = None
    ):
        async with cls._session.get(
            url, headers=header, data=data
        ) as response:
            return await response.json()


class API:

    token: str = ""
    header: dict = {}
    data: dict = {"Content-Type": "application/json"}
    site: str = "https://api.estadisticasbcra.com/"
    points: list[Endpoints] | None = None

    def __new__(cls, token: str = TOKEN):
        cls.token = token
        cls.header = {"Authorization": "BEARER " + token}
        return cls

    @classmethod
    async def _request(cls, points: tuple[Endpoints]):
        async with AsyncRequest() as req:
            return await asyncio.gather(
                *[req._get(cls.site + p, cls.header) for p in points]
            )

    @classmethod
    def query(cls, *points: Endpoints) -> Iterable:
        """
        Metodo que interactua con la API

        Parameter
        ---------
        *points: Endpoints
            Recibe estrictamente los nombres de los endpoints
            expuestos en la documentacion de esta:
                https://estadisticasbcra.com/api/documentacion

        Return
        ------
        Retorna una lista con todos los responses: List[JSON]
        en orden declarado en los argumentos

        Example
        -------
        >>> data = API()
        >>> data.query('usd', 'usd_of')
        >>> data
        [...responses...]
        """
        return asyncio.run(cls._request(points))
