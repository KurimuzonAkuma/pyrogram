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

import pyrogram
from pyrogram import raw, types, utils

from ..object import Object


class PaidReactor(Object):
    """Contains information about a user that added paid reactions.

    Parameters:
        sender (:obj:`~pyrogram.types.Chat`, *optional*):
            Identifier of the user or chat that added the reactions.
            May be None for anonymous reactors that aren't the current user

        star_count (``int``, *optional*):
            True, if the reactions are tags and Telegram Premium users can filter messages by them.

        is_top (``bool``, *optional*):
            True, if the reactor is one of the most active reactors.
            May be False if the reactor is the current user.

        is_me (``bool``, *optional*):
            True, if the paid reaction was added by the current user.

        is_anonymous (``bool``, *optional*):
            True, if the reactor is anonymous.
    """

    def __init__(
        self,
        *,
        sender: types.Chat | None = None,
        star_count: int | None = None,
        is_top: bool | None = None,
        is_me: bool | None = None,
        is_anonymous: bool | None = None,
    ):
        super().__init__()

        self.sender = sender
        self.star_count = star_count
        self.is_top = is_top
        self.is_me = is_me
        self.is_anonymous = is_anonymous

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        paid_reactor: raw.base.MessageReactor | None,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
    ) -> PaidReactor | None:
        if not paid_reactor:
            return None

        chat = chats.get(utils.get_raw_peer_id(paid_reactor.peer_id)) or users.get(
            utils.get_raw_peer_id(paid_reactor.peer_id)
        )

        return PaidReactor(
            sender=await types.Chat._parse_chat(client, chat),
            star_count=paid_reactor.count,
            is_top=paid_reactor.top,
            is_me=paid_reactor.my,
            is_anonymous=paid_reactor.anonymous,
        )
