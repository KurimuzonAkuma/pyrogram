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

import pytest

from pyrogram import filters
from tests.unit.filters import FakeClient, Message

c = FakeClient()


@pytest.mark.asyncio
async def test_single():
    f = filters.command("start")

    m = Message("/start")
    assert await f(c, m)


@pytest.mark.asyncio
async def test_multiple():
    f = filters.command(["start", "help"])

    m = Message("/start")
    assert await f(c, m)

    m = Message("/help")
    assert await f(c, m)

    m = Message("/settings")
    assert not await f(c, m)


@pytest.mark.asyncio
async def test_prefixes():
    f = filters.command("start", prefixes=list(".!#"))

    m = Message(".start")
    assert await f(c, m)

    m = Message("!start")
    assert await f(c, m)

    m = Message("#start")
    assert await f(c, m)

    m = Message("/start")
    assert not await f(c, m)


@pytest.mark.asyncio
async def test_case_sensitive():
    f = filters.command("start", case_sensitive=True)

    m = Message("/start")
    assert await f(c, m)

    m = Message("/StArT")
    assert not await f(c, m)


@pytest.mark.asyncio
async def test_case_insensitive():
    f = filters.command("start", case_sensitive=False)

    m = Message("/start")
    assert await f(c, m)

    m = Message("/StArT")
    assert await f(c, m)


@pytest.mark.asyncio
async def test_with_mention():
    f = filters.command("start")

    m = Message("/start@username")
    assert await f(c, m)

    m = Message("/start@UserName")
    assert await f(c, m)

    m = Message("/start@another")
    assert not await f(c, m)


@pytest.mark.asyncio
async def test_with_args():
    f = filters.command("start")

    m = Message("/start")
    await f(c, m)
    assert m.command == ["start"]

    m = Message("/StArT")
    await f(c, m)
    assert m.command == ["start"]

    m = Message("/start@username")
    await f(c, m)
    assert m.command == ["start"]

    m = Message("/start a b c")
    await f(c, m)
    assert m.command == ["start"] + list("abc")

    m = Message("/start@username a b c")
    await f(c, m)
    assert m.command == ["start"] + list("abc")

    m = Message("/start 'a b' c")
    await f(c, m)
    assert m.command == ["start", "a b", "c"]

    m = Message('/start     a     b     "c     d"')
    await f(c, m)
    assert m.command == ["start"] + list("ab") + ["c     d"]


@pytest.mark.asyncio
async def test_caption():
    f = filters.command("start")

    m = Message(caption="/start")
    assert await f(c, m)


@pytest.mark.asyncio
async def test_no_text():
    f = filters.command("start")

    m = Message()
    assert not await f(c, m)


@pytest.mark.asyncio
async def test_metacharacter_matches_only_its_own_literal() -> None:
    command_filter = filters.command("buy.now")

    message = Message("/buy.now")
    assert await command_filter(c, message)

    message = Message("/buyXnow")
    assert not await command_filter(c, message)


@pytest.mark.asyncio
async def test_repeated_metacharacter_matches_its_own_command() -> None:
    command_filter = filters.command("c++")

    message = Message("/c++ a b")
    assert await command_filter(c, message)
    assert message.command == ["c++"] + list("ab")

    message = Message("/c++@username a b")
    assert await command_filter(c, message)
    assert message.command == ["c++"] + list("ab")


@pytest.mark.asyncio
async def test_command_that_is_nothing_but_a_metacharacter() -> None:
    command_filter = filters.command("+")

    message = Message("/+ a")
    assert await command_filter(c, message)
    assert message.command == ["+", "a"]

    # The pattern was built for every message carrying the prefix, so an unrelated one
    #  reached the same uncompilable regex and raised out of the dispatcher.
    message = Message("/other")
    assert not await command_filter(c, message)
