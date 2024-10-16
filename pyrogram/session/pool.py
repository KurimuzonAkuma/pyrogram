import asyncio
import logging
from collections import defaultdict
from typing import (
    Dict,
    Optional,
    TYPE_CHECKING,
)

from pyrogram import (
    raw,
)
from pyrogram.errors import AuthBytesInvalid
from pyrogram.session.auth import Auth
from pyrogram.session.session import Session

if TYPE_CHECKING:
    from pyrogram import Client


log = logging.getLogger(__name__)


def get_session_key(
    dc_id: int,
    is_media: bool = False,
    is_cdn: bool = False
) -> int:
    key_prefix = 10_000

    if is_media:
        key_prefix *= 2

    if is_cdn:
        key_prefix *= 2

    return key_prefix + dc_id


class SessionPool:
    def __init__(self, client: "Client"):
        self.client = client

        self.sessions: Dict[int, Session] = {}
        self.locks: Dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)

        self.main_simple_session: Optional[Session] = None
        self.main_simple_session_key = 0

    def set_main_simple_session(self, session: Optional[Session]) -> None:
        self.main_simple_session = session
        if session is None:
            self.main_simple_session_key = 0
        else:
            self.main_simple_session_key = get_session_key(
                dc_id=self.main_simple_session.dc_id,
                is_media=self.main_simple_session.is_media,
                is_cdn=self.main_simple_session.is_cdn
            )

    async def get_simple_session(self, dc_id: int) -> Session:
        return await self.get_session(
            dc_id=dc_id
        )

    async def get_media_session(self, dc_id: int) -> Session:
        return await self.get_session(
            dc_id=dc_id,
            is_media=True
        )

    async def get_cdn_session(self, dc_id: int) -> Session:
        return await self.get_session(
            dc_id=dc_id,
            is_cdn=True,
            is_media=True
        )

    async def authorization_transfer(self, session: Session) -> None:
        if session.dc_id == self.main_simple_session.dc_id:
            return None

        for _ in range(3):
            exported_auth = await self.main_simple_session.invoke(
                query=raw.functions.auth.ExportAuthorization(
                    dc_id=session.dc_id
                ),
                retries=1,
                sleep_threshold=0,
            )

            try:
                await session.invoke(
                    query=raw.functions.auth.ImportAuthorization(
                        id=exported_auth.id,
                        bytes=exported_auth.bytes
                    ),
                    retries=1,
                    sleep_threshold=0,
                )
            except AuthBytesInvalid:
                continue

            break
        else:
            raise AuthBytesInvalid

    async def get_auth_key_by_dc_id(self, dc_id: int) -> bytes:
        if dc_id == self.main_simple_session.dc_id:
            return self.main_simple_session.auth_data.main_auth_key

        auth = Auth(
            client=self.client,  # TODO: use main_simple_session
            dc_id=dc_id,
            test_mode=self.main_simple_session.test_mode
        )

        auth_key = await auth.create()
        return auth_key

    async def get_session(
        self,
        dc_id: int,
        is_media: bool = False,
        is_cdn: bool = False
    ) -> Session:
        if self.main_simple_session is None:
            raise RuntimeError("Main session not initialized")

        key = get_session_key(
            dc_id=dc_id,
            is_media=is_media,
            is_cdn=is_cdn
        )

        if self.main_simple_session_key == key:
            return self.main_simple_session

        async with self.locks[key]:
            session = self.sessions.get(key)
            if session:
                return session

            test_mode = self.main_simple_session.test_mode

            auth_key = await self.get_auth_key_by_dc_id(dc_id)
            session = Session(
                client=self.client, # TODO: use main_simple_session
                dc_id=dc_id,
                auth_key=auth_key,
                test_mode=test_mode,
                is_media=is_media,
                is_cdn=is_cdn,

            )
            await session.start()

            try:
                await self.authorization_transfer(session)
            except Exception as exc:
                log.exception(exc)
                await session.stop()
                raise

            self.sessions[key] = session
            return session

    async def aclose(self) -> None:
        if self.main_simple_session:
            await self.main_simple_session.stop()

        for session in self.sessions.values():
            await session.stop()

        self.set_main_simple_session(None)
