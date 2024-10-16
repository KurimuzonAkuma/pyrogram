#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
import logging
from typing import (
    Optional,
    Tuple,
    Type,
)

from .transport import (
    TCP,
    TCPAbridged,
)
from .transport.tcp.connector.base import Connector
from .transport.tcp.connector.direct_connector import DirectConnector
from ..session.internals import DataCenter

try:
    from .transport.tcp.connector.python_socks_connector import PythonSocksProxyConnector as python_socks_proxy_connector
except ImportError:
    python_socks_proxy_connector = None

try:
    from .transport.tcp.connector.socks_connector import SocksProxyConnector as socks_proxy_connector
except ImportError:
    socks_proxy_connector = None

log = logging.getLogger(__name__)


async def make_connector(
    destination: Tuple[str, int],
    proxy: Optional[dict],
    timeout: int
):
    if proxy is None:
        return await DirectConnector.new(destination=destination, timeout=timeout)
    elif python_socks_proxy_connector:
        return await python_socks_proxy_connector.new(destination=destination, proxy=proxy, timeout=timeout)
    elif socks_proxy_connector:
        return await socks_proxy_connector.new(destination=destination, proxy=proxy, timeout=timeout)
    else:
        raise ValueError("Unknown connector type")


class Connection:
    MAX_CONNECTION_ATTEMPTS = 3

    def __init__(
        self,
        connector: Connector,
        protocol: TCP
    ) -> None:
        self.connector = connector
        self.protocol = protocol

    @classmethod
    async def new(
        cls,
        dc_id: int,
        test_mode: bool,
        ipv6: bool,
        proxy: dict,
        media: bool = False,
        protocol_factory: Type[TCP] = TCPAbridged
    ) -> "Connection":
        destination = DataCenter(dc_id, test_mode, ipv6, media)

        for i in range(Connection.MAX_CONNECTION_ATTEMPTS):
            try:
                log.info("Connecting connector...")
                connector = await make_connector(
                    destination=destination,
                    proxy=proxy,
                    timeout=protocol_factory.TIMEOUT
                )
            except Exception as exc:
                log.warning("Unable to connect due to network issues: %s", exc)
                await asyncio.sleep(1)
                continue

            protocol = protocol_factory(connector)

            try:
                log.info("Connecting protocol...")
                await protocol.connect()
            except Exception as exc:
                await connector.close(timeout=protocol.TIMEOUT)
                log.warning("Unable to connect due to network issues: %s", exc)
                await asyncio.sleep(1)
                continue

            log.info(
                "Connected! %s DC%s%s - IPv%s",
                "Test" if test_mode else "Production",
                dc_id,
                " (media)" if media else "",
                "6" if ipv6 else "4"
            )

            return cls(
                connector=connector,
                protocol=protocol
            )

    async def close(self) -> None:
        await self.connector.close(timeout=self.protocol.TIMEOUT)
        log.info("Disconnected")

    async def send(self, data: bytes) -> None:
        await self.protocol.send(data)

    async def recv(self) -> Optional[bytes]:
        return await self.protocol.recv()
