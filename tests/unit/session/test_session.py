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
from concurrent.futures import Executor
from hashlib import sha1, sha256
from os import urandom
from typing import Final

import pytest

import pyrogram
from pyrogram import raw
from pyrogram.crypto import aes, mtproto
from pyrogram.raw.core import Long, Message
from pyrogram.session.session import Result, Session, SessionState

_DC_ID: Final[int] = 2
_PORT: Final[int] = 443
_AUTH_KEY: Final[bytes] = bytes(256)
_PACKET: Final[bytes] = b"one packet"

# The salt the session holds before the server offers a new one, and the one it offers.
_STALE_SALT: Final[int] = 111
_NEW_SALT: Final[int] = 999

# `bad_server_salt` error code: "incorrect server salt".
#  https://core.telegram.org/mtproto/service_messages_about_messages#notice-of-ignored-error-message
_INCORRECT_SERVER_SALT: Final[int] = 48

# Long enough that a `stop()` which does not wait would have returned several times
#  over, short enough to keep the suite quick.
_NOT_DONE_TIMEOUT: Final[float] = 0.1

# What `Session.STOP_TIMEOUT` is replaced with, so a test of the cancelling path does
#  not sit through the real grace period.
_SHORT_STOP_TIMEOUT: Final[float] = 0.05


class StubProtocol:
    def __init__(self) -> None:
        # `handle_packet` unpacks in this executor; `None` means the loop default one.
        self.crypto_executor: Executor | None = None


class StubConnection:
    def __init__(self) -> None:
        self.closed = asyncio.Event()
        self.packets = [_PACKET]
        self.protocol = StubProtocol()

    async def recv(self) -> bytes | None:
        if self.packets:
            return self.packets.pop()

        await self.closed.wait()
        return None

    async def close(self) -> None:
        self.closed.set()


def _started_session() -> Session:
    client = pyrogram.Client("test", api_id=1, api_hash="0" * 32, in_memory=True)
    session = Session(client, _DC_ID, "127.0.0.1", _PORT, _AUTH_KEY, test_mode=True)

    session.connection = StubConnection()
    session._state = SessionState.STARTED
    session.is_started.set()

    return session


def _pack_as_server(message: Message, *, session_id: bytes, auth_key: bytes) -> bytes:
    """`pyrogram.crypto.mtproto.pack`, in the direction the server writes.

    The outer salt is the sender's own and `unpack` skips it, so it is left at zero.
    """
    data: bytes = Long(0) + session_id + message.write()
    padding = urandom(-(len(data) + 12) % 16 + 12)

    # 96 = 88 + 8, the offset an incoming message keys on.
    msg_key = sha256(auth_key[96 : 96 + 32] + data + padding).digest()[8:24]
    aes_key, aes_iv = mtproto.kdf(auth_key, msg_key, False)

    return (
        sha1(auth_key).digest()[-8:] + msg_key + aes.ige256_encrypt(data + padding, aes_key, aes_iv)
    )


async def _bad_server_salt_packet(*, session: Session, bad_msg_id: int) -> bytes:
    body = raw.types.BadServerSalt(
        bad_msg_id=bad_msg_id,
        bad_msg_seqno=0,
        error_code=_INCORRECT_SERVER_SALT,
        new_server_salt=_NEW_SALT,
    )

    # A server message identity is odd, and the factory allocates client ones.
    message = Message(
        body,
        await session.msg_factory.allocate_message_identity() + 1,
        1,
        len(body),
    )

    return _pack_as_server(
        message,
        session_id=session.session_id,
        auth_key=session.auth_key,
    )


async def test_stop_waits_for_the_packet_it_is_still_handling() -> None:
    session = _started_session()

    release = asyncio.Event()
    handled: bool = False

    async def handle_packet(packet: bytes) -> None:
        nonlocal handled

        await release.wait()
        handled = True

    session.handle_packet = handle_packet
    session.recv_task = session.client.loop.create_task(session.recv_worker())

    await asyncio.sleep(0)

    stopping = asyncio.ensure_future(session.stop())

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(asyncio.shield(stopping), _NOT_DONE_TIMEOUT)

    assert not handled

    release.set()
    await stopping

    assert handled
    assert session.pending_tasks == set()


async def test_stop_cancels_a_packet_that_will_not_finish(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(Session, "STOP_TIMEOUT", _SHORT_STOP_TIMEOUT)

    session = _started_session()

    async def handle_packet(packet: bytes) -> None:
        await asyncio.Event().wait()

    session.handle_packet = handle_packet
    session.recv_task = session.client.loop.create_task(session.recv_worker())

    await asyncio.sleep(0)

    handling = next(iter(session.pending_tasks))

    await session.stop()

    assert handling.cancelled()
    assert session.pending_tasks == set()


async def test_a_finished_task_leaves_the_pending_set() -> None:
    session = _started_session()

    task = session._create_tracked_task(asyncio.sleep(0))

    assert session.pending_tasks == {task}

    await task
    await asyncio.sleep(0)

    assert session.pending_tasks == set()


async def test_a_restart_queued_before_stop_does_not_reconnect() -> None:
    session = _started_session()

    started: bool = False

    async def start() -> None:
        nonlocal started

        started = True

    session.start = start

    # The task is only scheduled here: it runs once the loop is yielded to, which is
    #  after the stop below, and that is the order the client shuts down in.
    restarting = session.client.loop.create_task(session.restart())

    await session.stop()
    await restarting

    assert not started
    assert session.state is SessionState.STOPPED


async def test_a_restart_already_starting_is_stopped_again() -> None:
    session = _started_session()

    starting = asyncio.Event()
    release = asyncio.Event()

    async def start() -> None:
        starting.set()
        await release.wait()

        session._state = SessionState.STARTED
        session.is_started.set()

    session.start = start
    restarting = session.client.loop.create_task(session.restart())

    await starting.wait()
    await session.stop()

    release.set()
    await restarting

    assert session.state is SessionState.STOPPED
    assert not session.is_started.is_set()


async def test_a_bad_server_salt_nobody_awaits_still_updates_the_salt() -> None:
    session = _started_session()
    session.salt = _STALE_SALT

    # `ping_worker` sends with `wait_response=False`, so nothing registers a `Result`.
    ping_msg_id = await session.msg_factory.allocate_message_identity()

    await session.handle_packet(
        await _bad_server_salt_packet(
            session=session,
            bad_msg_id=ping_msg_id,
        ),
    )

    assert ping_msg_id not in session.results
    assert session.salt == _NEW_SALT


async def test_a_bad_server_salt_still_resolves_the_call_that_waits_for_it() -> None:
    session = _started_session()
    session.salt = _STALE_SALT

    awaited_msg_id = await session.msg_factory.allocate_message_identity()
    session.results[awaited_msg_id] = Result()

    await session.handle_packet(
        await _bad_server_salt_packet(
            session=session,
            bad_msg_id=awaited_msg_id,
        ),
    )

    assert session.results[awaited_msg_id].event.is_set()
    assert session.salt == _NEW_SALT
