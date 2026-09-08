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
from pyrogram import raw, utils
from pyrogram import types
from ..object import Object


class Giveaway(Object):
    """An giveaway.

    Parameters:
        chats (List of :obj:`~pyrogram.types.Chat`):
            Get the list of channels you need to subscribe to.

        quantity (``int``):
            Number of subscriptions.

        months (``int``):
            Number of months for which a subscription is given.

        until_date (:py:obj:`~datetime.datetime`):
            Date when the giveaway will end.

        description (``str``, *optional*):
            Prize description.

        only_new_subscribers (``bool``, *optional*):
            True, if this giveaway is for new subscribers only.

        only_for_countries (List of ``str`` , *optional*):
            A list of two-letter ISO 3166-1 alpha-2 country codes indicating the countries
            from which eligible users for the giveaway must come.
            If None, then all users can participate in the giveaway.
            Users with a phone number that was bought on Fragment can always participate in giveaways.

        winners_are_visible (``bool``, *optional*):
            True, if this giveaway winners is visible.

        stars (``int``, *optional*):
            Stars amount.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        chats: list[types.Chat] | None = None,
        quantity: int | None = None,
        months: int | None = None,
        until_date: datetime | None = None,
        description: str | None = None,
        only_new_subscribers: bool | None = None,
        only_for_countries: list[str] | None = None,
        winners_are_visible: bool | None = None,
        stars: int | None = None
    ):
        super().__init__(client)

        self.chats = chats
        self.quantity = quantity
        self.months = months
        self.until_date = until_date
        self.description = description
        self.only_new_subscribers = only_new_subscribers
        self.only_for_countries = only_for_countries
        self.winners_are_visible = winners_are_visible
        self.stars = stars

    @staticmethod
    async def _parse(
        client,
        giveaway: raw.types.MessageMediaGiveaway,
        chats: dict
    ) -> Giveaway:
        return Giveaway(
            chats=types.List([await types.Chat._parse_channel_chat(client, chats.get(i)) for i in giveaway.channels]),
            quantity=giveaway.quantity,
            months=giveaway.months,
            until_date=utils.timestamp_to_datetime(giveaway.until_date),
            description=getattr(giveaway, "prize_description", None) or None,
            only_new_subscribers=getattr(giveaway, "only_new_subscribers", None),
            only_for_countries=types.List(getattr(giveaway, "countries_iso2", [])) or None,
            winners_are_visible=getattr(giveaway, "winners_are_visible", None),
            stars=getattr(giveaway, "stars", None),
            client=client
        )
