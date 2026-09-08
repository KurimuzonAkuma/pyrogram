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


class PaidMessagesRefunded(Object):
    """Paid messages were refunded.

    Parameters:
        message_count (``int``):
            The number of refunded messages.

        star_count (``int``):
            The number of refunded Telegram Stars.
    """

    def __init__(self, *, message_count: int, star_count: int):

        super().__init__()

        self.message_count = message_count
        self.star_count = star_count

    @staticmethod
    def _parse(action: raw.types.MessageActionPaidMessagesRefunded) -> PaidMessagesRefunded:
        return PaidMessagesRefunded(message_count=action.count, star_count=action.stars)
