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


class PaidMessagesPriceChanged(Object):
    """A price for paid messages was changed in the supergroup chat.

    Parameters:
        paid_message_star_count (``int``):
            The new number of Telegram Stars that must be paid by non-administrator users of the supergroup chat for each sent message.
    """

    def __init__(self, *, paid_message_star_count: int):

        super().__init__()

        self.paid_message_star_count = paid_message_star_count

    @staticmethod
    def _parse(action: raw.types.MessageActionPaidMessagesPrice) -> PaidMessagesPriceChanged:
        return PaidMessagesPriceChanged(paid_message_star_count=action.stars)
