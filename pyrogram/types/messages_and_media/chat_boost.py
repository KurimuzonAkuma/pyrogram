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

from datetime import datetime

import pyrogram
from pyrogram import raw, types, utils
from ..object import Object


class ChatBoost(Object):
    """Contains information about one or more boosts applied by a specific user.

    Parameters:
        id (``str``):
            Unique identifier for this set of boosts.

        date (:py:obj:`~datetime.datetime`):
            Date the boost was applied.

        expire_date (:py:obj:`~datetime.datetime`):
            Point in time when the boost will expire.

        multiplier (``int``):
            If set, this boost counts as multiplier boosts, otherwise it counts as a single boost.

        from_user (:obj:`~pyrogram.types.User`, *optional*):
            The user that that applied the boost.

        is_gift (``bool``, *optional*):
            Whether this boost was applied because the channel/supergroup directly gifted a subscription to the user.

        is_giveaway (``bool``, *optional*):
            Whether this boost was applied because the user was chosen in a giveaway started by the channel/supergroup.

        is_unclaimed (``bool``, *optional*):
            If set, the user hasn't yet invoked :meth:`~pyrogram.Client.apply_gift_code` to claim a subscription gifted directly or in a giveaway by the channel.

        giveaway_message_id (``int``, *optional*):
            The message identifier of the giveaway.

        used_gift_slug (``str``, *optional*):
            The created Telegram Premium gift code, only set if either gift or giveaway are set AND it is either a gift code for the currently logged in user or if it was already claimed.

        stars (``int``, *optional*):
            Stars amount.
    """

    def __init__(
        self,
        *,
        id: str,
        date: datetime,
        expire_date: datetime,
        multiplier: int,
        from_user: types.User | None = None,
        is_gift: bool | None = None,
        is_giveaway: bool | None = None,
        is_unclaimed: bool | None = None,
        giveaway_message_id: int | None = None,
        used_gift_slug: str | None = None,
        stars: int | None = None
    ):
        super().__init__()

        self.id = id
        self.date = date
        self.expire_date = expire_date
        self.multiplier = multiplier
        self.from_user = from_user
        self.is_gift = is_gift
        self.is_giveaway = is_giveaway
        self.is_unclaimed = is_unclaimed
        self.giveaway_message_id = giveaway_message_id
        self.used_gift_slug = used_gift_slug
        self.stars = stars

    @staticmethod
    async def _parse(client: pyrogram.Client, boost: raw.types.Boost, users) -> ChatBoost:
        return ChatBoost(
            id=boost.id,
            date=utils.timestamp_to_datetime(boost.date),
            expire_date=utils.timestamp_to_datetime(boost.expires),
            multiplier=getattr(boost, "multiplier", 1),
            from_user=await types.User._parse(client, users.get(boost.user_id)),
            is_gift=getattr(boost, "gift", None),
            is_giveaway=getattr(boost, "giveaway", None),
            is_unclaimed=getattr(boost, "unclaimed", None),
            giveaway_message_id=getattr(boost, "giveaway_msg_id", None),
            used_gift_slug=getattr(boost, "used_gift_slug", None),
            stars=getattr(boost, "stars", None)
        )
