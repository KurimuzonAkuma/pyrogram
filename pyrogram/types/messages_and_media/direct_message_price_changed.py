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

from pyrogram import raw

from ..object import Object


class DirectMessagePriceChanged(Object):
    """A price for direct messages was changed in the channel chat.

    Parameters:
        is_enabled (``bool``):
            True, if direct messages group was enabled for the channel, False otherwise

        paid_message_star_count (``int``):
            The new number of Telegram Stars that must be paid by non-administrator users of the channel chat
            for each message sent to the direct messages group.
            0 if the direct messages group was disabled or the messages are free.
    """

    def __init__(
        self,
        *,
        is_enabled: bool,
        paid_message_star_count: int
    ):

        super().__init__()

        self.is_enabled = is_enabled
        self.paid_message_star_count = paid_message_star_count

    @staticmethod
    def _parse(
        action: raw.types.MessageActionPaidMessagesPrice
    ) -> DirectMessagePriceChanged:
        return DirectMessagePriceChanged(
            is_enabled=action.broadcast_messages_allowed,
            paid_message_star_count=action.stars
        )
