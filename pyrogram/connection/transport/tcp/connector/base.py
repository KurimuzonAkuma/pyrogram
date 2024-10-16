import asyncio
import logging
from typing import Optional

log = logging.getLogger(__name__)


class Connector:
    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        self.reader = reader
        self.writer = writer

    def write(self, data: bytes) -> None:
        self.writer.write(data)

    async def drain(self) -> None:
        await self.writer.drain()

    async def read(self, n: int = -1) -> bytes:
        return await self.reader.read(n)

    async def close(self, timeout: Optional[int] = None) -> None:
        try:
            self.writer.close()
            await asyncio.wait_for(self.writer.wait_closed(), timeout)
        except asyncio.TimeoutError:
            log.warning("Close connector timed out")
        except Exception as exc:
            log.warning("Close exception: %s %s", type(exc).__name__, exc)
