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

from pyrogram import raw
from pyrogram.methods.bots.edit_user_star_subscription import EditUserStarSubscription


class _InvokeCalled(Exception):
    """Raised by the fake `invoke` once reached, carrying the built query for inspection."""

    def __init__(self, query: raw.functions.payments.BotCancelStarsSubscription) -> None:
        self.query = query


class FakeClient(EditUserStarSubscription):
    async def resolve_peer(self, peer_id: int | str) -> raw.types.InputUser:
        return raw.types.InputUser(
            user_id=peer_id,
            access_hash=0,
        )

    async def invoke(self, query: raw.functions.payments.BotCancelStarsSubscription) -> None:
        raise _InvokeCalled(query)


async def _restore_flag_for(*, is_canceled: bool) -> bool:
    client = FakeClient()

    with pytest.raises(_InvokeCalled) as exc_info:
        await client.edit_user_star_subscription(7, "charge", is_canceled=is_canceled)

    return exc_info.value.query.restore


@pytest.mark.asyncio
async def test_canceling_clears_the_restore_flag() -> None:
    # `restore=is_canceled` sent `restore=True` for a cancellation, which the server reads as
    #  "keep it renewing", so the subscription was never canceled and the call still returned True.
    assert await _restore_flag_for(is_canceled=True) is False


@pytest.mark.asyncio
async def test_re_enabling_sets_the_restore_flag() -> None:
    assert await _restore_flag_for(is_canceled=False) is True
