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

class SuggestedPostPriceStar(Object):
    """Describes price of a suggested post in Telegram Stars.

    Parameters:
        star_count (``int``):
            The amount of Telegram Stars agreed to pay for the post, 5-100000.
    """
    def __init__(
        self, *,
        star_count: int
    ):
        super().__init__()

        self.star_count = star_count

    @staticmethod
    def _parse(post_price: raw.types.StarsAmount) -> SuggestedPostPriceStar | None:
        if isinstance(post_price, raw.types.StarsAmount):
            return SuggestedPostPriceStar(
                star_count=post_price.amount
            )

    def write(self) -> raw.types.StarsAmount:
        return raw.types.StarsAmount(
            amount=self.star_count,
            nanos=0
        )


class SuggestedPostPriceTon(Object):
    """Describes price of a suggested post in Toncoins.

    Parameters:
        toncoin_nano_count (``int``):
            The amount of Toncoin in nanotons agreed to pay for the post, 10000000-10000000000000.
    """
    def __init__(
        self, *,
        toncoin_nano_count: int
    ):
        super().__init__()

        self.toncoin_nano_count = toncoin_nano_count

    @staticmethod
    def _parse(post_price: raw.types.StarsTonAmount) -> SuggestedPostPriceTon | None:
        if isinstance(post_price, raw.types.StarsTonAmount):
            return SuggestedPostPriceTon(
                toncoin_nano_count=post_price.amount
            )

    def write(self) -> raw.types.StarsTonAmount:
        return raw.types.StarsTonAmount(
            amount=self.toncoin_nano_count
        )


class SuggestedPostPrice(Object):
    """Describes price of a suggested post.

    It can be one of:

    - :obj:`~pyrogram.types.SuggestedPostPriceStar`
    - :obj:`~pyrogram.types.SuggestedPostPriceTon`
    """

    def __init__(
        self,
    ):
        super().__init__()

    @staticmethod
    def _parse(
        suggested_post_price: raw.base.StarsAmount
    ) -> SuggestedPostPriceStar | SuggestedPostPriceTon | None:
        if isinstance(suggested_post_price, raw.types.StarsAmount):
            return SuggestedPostPriceStar._parse(suggested_post_price)
        elif isinstance(suggested_post_price, raw.types.StarsTonAmount):
            return SuggestedPostPriceTon._parse(suggested_post_price)

    def write(self) -> raw.base.StarsAmount:
        raise NotImplementedError
