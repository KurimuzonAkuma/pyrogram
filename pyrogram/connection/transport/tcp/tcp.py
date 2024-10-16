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
from typing import Optional

from .connector.base import Connector

log = logging.getLogger(__name__)


class TCP:
    TIMEOUT = 10

    def __init__(self, connector: Connector) -> None:
        self.connector = connector
        self.lock = asyncio.Lock()
        self.loop = asyncio.get_event_loop()

    async def connect(self) -> None:
        return None

    async def send(self, data: bytes) -> None:
        async with self.lock:
            try:
                self.connector.write(data)
                await self.connector.drain()
            except Exception as e:
                log.info("Send exception: %s %s", type(e).__name__, e)
                raise OSError(e)

    async def recv(self, length: int = 0) -> Optional[bytes]:
        data = b""

        while len(data) < length:
            log.debug("Recv length: %d / %d bytes", len(data), length)

            try:
                chunk = await asyncio.wait_for(
                    self.connector.read(length - len(data)),
                    TCP.TIMEOUT
                )
            except (OSError, asyncio.TimeoutError):
                return None
            else:
                if chunk:
                    data += chunk
                else:
                    return None

        return data
