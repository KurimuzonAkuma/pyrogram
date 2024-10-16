import asyncio
from typing import (
    Any,
    Dict,
    Tuple,
)

from python_socks import (
    ProxyTimeoutError,
    ProxyType,
)
from python_socks.async_.asyncio import Proxy as AsyncProxy

from .base import Connector
from .errors import (
    ConnectorError,
    ConnectorProxyError,
    ConnectorProxyTimeoutError,
    ConnectorTimeoutError,
)

proxy_type_by_scheme: Dict[str, ProxyType] = {
    "SOCKS4": ProxyType.SOCKS4,
    "SOCKS5": ProxyType.SOCKS5,
    "HTTP": ProxyType.HTTP,
}


class PythonSocksProxyConnector(Connector):
    @classmethod
    async def new(cls, destination: Tuple[str, int], proxy: Dict[str, Any], timeout: int) -> "PythonSocksProxyConnector":
        scheme = proxy.get("scheme")
        if scheme is None:
            raise ValueError("No scheme specified")

        proxy_type = proxy_type_by_scheme.get(scheme.upper())

        if proxy_type is None:
            raise ValueError(f"Unknown proxy type {scheme}")

        hostname = proxy.get("hostname")
        port = proxy.get("port")
        username = proxy.get("username")
        password = proxy.get("password")

        proxy = AsyncProxy.create(
            proxy_type=proxy_type,
            host=hostname,
            port=port,
            username=username,
            password=password,
        )
        try:
            sock = await proxy.connect(
                dest_host=destination[0],
                dest_port=destination[1],
                timeout=timeout,
            )
        except (asyncio.TimeoutError, ProxyTimeoutError) as exc:
            raise ConnectorProxyTimeoutError("Connection to the proxy server timed out") from exc
        except Exception as exc:
            raise ConnectorProxyError("An error occurred while connecting to the proxy server") from exc

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(
                    sock=sock,
                ), timeout=timeout
            )
        except asyncio.TimeoutError as exc:
            raise ConnectorTimeoutError("Connection to the destination server timed out") from exc
        except Exception as exc:
            raise ConnectorError("An error occurred while connecting to the destination server") from exc

        return cls(reader=reader, writer=writer)
