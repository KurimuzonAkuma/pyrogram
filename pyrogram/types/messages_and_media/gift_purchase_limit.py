#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present <https://github.com/TelegramPlayGround>
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

from ..object import Object


class GiftPurchaseLimit(Object):
    """Describes the maximum number of times that a specific gift can be purchased.

    Parameters:
        total_count (``int``, *optional*):
            The maximum number of times the gifts can be purchased.

        remaining_count (``int``, *optional*):
            Number of remaining times the gift can be purchased.
    """

    def __init__(self, *, total_count: int | None = None, remaining_count: int | None = None):
        super().__init__()

        self.total_count = total_count
        self.remaining_count = remaining_count

    @staticmethod
    def _parse(total: int, remains: int) -> GiftPurchaseLimit | None:
        if total is None or total <= 0:
            return None

        return GiftPurchaseLimit(total_count=total, remaining_count=remains)
