import asyncio
import ipaddress
import socket
from concurrent.futures import ThreadPoolExecutor
from typing import (
    Any,
    Dict,
    Tuple,
)

import socks

from .base import Connector
from .errors import (
    ConnectorError,
    ConnectorProxyError,
    ConnectorProxyTimeoutError,
    ConnectorTimeoutError,
)


class SocksProxyConnector(Connector):
    @classmethod
    async def new(cls, destination: Tuple[str, int], proxy: Dict[str, Any], timeout: int) -> "SocksProxyConnector":
        scheme = proxy.get("scheme")
        if scheme is None:
            raise ValueError("No scheme specified")

        proxy_type = socks.PROXY_TYPES.get(scheme.upper())

        if proxy_type is None:
            raise ValueError(f"Unknown proxy type {scheme}")

        hostname = proxy.get("hostname")
        port = proxy.get("port")
        username = proxy.get("username")
        password = proxy.get("password")

        try:
            ip_address = ipaddress.ip_address(hostname)
        except ValueError:
            is_proxy_ipv6 = False
        else:
            is_proxy_ipv6 = isinstance(ip_address, ipaddress.IPv6Address)

        proxy_family = socket.AF_INET6 if is_proxy_ipv6 else socket.AF_INET
        sock = socks.socksocket(proxy_family)

        sock.set_proxy(
            proxy_type=proxy_type,
            addr=hostname,
            port=port,
            username=username,
            password=password
        )
        sock.settimeout(timeout)

        loop = asyncio.get_running_loop()

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                await asyncio.wait_for(loop.run_in_executor(executor, sock.connect, destination), timeout=timeout)
        except asyncio.TimeoutError as exc:
            raise ConnectorProxyTimeoutError("Connection to the proxy server timed out") from exc
        except Exception as exc:
            raise ConnectorProxyError("An error occurred while connecting to the proxy server") from exc

        sock.setblocking(False)

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
