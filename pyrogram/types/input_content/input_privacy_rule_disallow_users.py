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
from collections.abc import Iterable

import pyrogram
from pyrogram import raw
from .input_privacy_rule import InputPrivacyRule


class InputPrivacyRuleDisallowUsers(InputPrivacyRule):
    """Disallow only participants of certain users.

    Parameters:
        chat_ids (``int`` | ``str`` | Iterable of ``int`` or ``str``, *optional*):
            Unique identifier (int) or username (str) of the target chat.
    """

    def __init__(
        self,
        chat_ids: int | str | Iterable[int | str],
    ):
        super().__init__()

        self.chat_ids = chat_ids

    async def write(self, client: pyrogram.Client):
        users = (
            list(self.chat_ids) if not isinstance(self.chat_ids, (int, str)) else [self.chat_ids]
        )
        users = await asyncio.gather(*[client.resolve_peer(i) for i in users])

        return raw.types.InputPrivacyValueDisallowUsers(users=users)
