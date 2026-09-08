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


class UserRating(Object):
    """Contains information about rating of a user.

    Parameters:
        level (``int``):
            The level of the user.
            May be negative.

        is_maximum_level_reached (``bool``):
            True, if the maximum level is reached.

        rating (``int``):
            Numerical value of the rating.

        current_level_rating (``int``):
            The rating required for the current level.

        next_level_rating (``int``, *optional*):
            The rating required for the next level.
    """

    def __init__(
        self, *,
        level: int,
        is_maximum_level_reached: bool,
        rating: int,
        current_level_rating: int,
        next_level_rating: int | None = None
    ):
        super().__init__(None)

        self.level = level
        self.is_maximum_level_reached = is_maximum_level_reached
        self.rating = rating
        self.current_level_rating = current_level_rating
        self.next_level_rating = next_level_rating

    @staticmethod
    def _parse(rating: raw.types.StarsRating) -> UserRating | None:
        if not rating:
            return None

        return UserRating(
            level=rating.level,
            is_maximum_level_reached=rating.next_level_stars == 0 and rating.level > 0,
            rating=rating.stars,
            current_level_rating=rating.current_level_stars,
            next_level_rating=rating.next_level_stars
        )
