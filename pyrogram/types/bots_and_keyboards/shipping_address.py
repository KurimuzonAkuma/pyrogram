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


class ShippingAddress(Object):
    """Contains information about a shipping address.

    Parameters:
        country_code (``str``):
            Two-letter `ISO 3166-1 alpha-2 <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2>`_ country code.

        state (``str``):
            State, if applicable.

        city (``str``):
            City.

        street_line1 (``str``):
            First line for the address.

        street_line2 (``str``):
            Second line for the address.

        post_code (``str``):
            Address post code.

    """

    def __init__(
        self,
        *,
        country_code: str,
        state: str,
        city: str,
        street_line1: str,
        street_line2: str,
        post_code: str
    ):
        super().__init__()

        self.country_code = country_code
        self.state = state
        self.city = city
        self.street_line1 = street_line1
        self.street_line2 = street_line2
        self.post_code = post_code

    @staticmethod
    def _parse(
        shipping_address: raw.types.PostAddress,
    ) -> ShippingAddress | None:
        if not shipping_address:
            return None

        return ShippingAddress(
            country_code=shipping_address.country_iso2,
            state=shipping_address.state,
            city=shipping_address.city,
            street_line1=shipping_address.street_line1,
            street_line2=shipping_address.street_line2,
            post_code=shipping_address.post_code
        )
