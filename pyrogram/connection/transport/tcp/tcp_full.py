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

from __future__ import annotations as _annotations

import asyncio
import logging
from binascii import crc32
from struct import pack, unpack

from pyrogram.connection.proxy import Proxy
from pyrogram.connection.transport.tcp.tcp import TCP

log = logging.getLogger(__name__)


class TCPFull(TCP):
    def __init__(
        self,
        ipv6: bool,
        proxy: Proxy | None = None,
        crypto_executor_workers: int = 1,
        loop: asyncio.AbstractEventLoop | None = None,
        dc_id: int | None = None,
    ) -> None:
        super().__init__(ipv6, proxy, crypto_executor_workers, loop, dc_id=dc_id)

        self.seq_no: int = 0

    async def connect(self, address: tuple[str, int]) -> None:
        self.marker_event.clear()
        await super().connect(address)
        self.seq_no = 0
        self.marker_event.set()

    async def send(self, data: bytes, *args) -> None:
        data = pack("<II", len(data) + 12, self.seq_no) + data
        data += pack("<I", crc32(data))
        self.seq_no += 1

        await super().send(data, wait_for_marker=False)

    async def recv(self, length: int = 0) -> bytes | None:
        length_bytes = await super().recv(4)

        if length_bytes is None:
            return None

        packet = await super().recv(unpack("<I", length_bytes)[0] - 4)

        if packet is None:
            return None

        packet = length_bytes + packet
        checksum = packet[-4:]
        packet = packet[:-4]

        if crc32(packet) != unpack("<I", checksum)[0]:
            return None

        return packet[8:]
