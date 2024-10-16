import asyncio
import ipaddress
import logging
import socket
from typing import (
    Optional,
    Tuple,
)

from .base import Connector
from .errors import (
    ConnectorError,
    ConnectorTimeoutError,
)
log = logging.getLogger(__name__)


class DirectConnector(Connector):
    @classmethod
    async def new(cls, destination: Tuple[str, int], timeout: Optional[float] = None) -> "DirectConnector":
        host, port = destination

        try:
            ip_address = ipaddress.ip_address(host)
        except ValueError:
            is_ipv6 = False
        else:
            is_ipv6 = isinstance(ip_address, ipaddress.IPv6Address)

        family = socket.AF_INET6 if is_ipv6 else socket.AF_INET

        log.debug("DirectConnector is_ipv6=%s, family=%s, host=%s, port=%s",is_ipv6,  family, host, port)

        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(
                    host=host,
                    port=port,
                    family=family
                ), timeout=timeout
            )
        except asyncio.TimeoutError as exc:
            raise ConnectorTimeoutError("Connection to the destination server timed out") from exc
        except Exception as exc:
            raise ConnectorError("An error occurred while connecting to the destination server") from exc

        return cls(
            reader=reader,
            writer=writer
        )
