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

from pyrogram import raw, types

from ..object import Object


class ShippingOption(Object):
    """This object represents one shipping option.

    Parameters:
        id (``str``):
            Shipping option identifier.

        title (``str``):
            Option title.

        prices (List of :obj:`~pyrogram.types.LabeledPrice`):
            List of price portions.

    """

    def __init__(
        self,
        id: str,
        title: str,
        prices: list[types.LabeledPrice]
    ):
        super().__init__()

        self.id = id
        self.title = title
        self.prices = prices

    @staticmethod
    def _parse(shipping_option: raw.types.ShippingOption) -> ShippingOption:
        if isinstance(shipping_option, raw.types.ShippingOption):
            return ShippingOption(
                id=shipping_option.id,
                title=shipping_option.title,
                prices=[
                    types.LabeledPrice._parse(price)
                    for price in shipping_option.prices
                ]
            )

    def write(self):
        return raw.types.ShippingOption(
            id=self.id,
            title=self.title,
            prices=[
                price.write()
                for price in self.prices
            ]
        )
