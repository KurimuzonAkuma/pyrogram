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

from pyrogram import types

from ..object import Object


class OrderInfo(Object):
    """This object represents information about an order.

    Parameters:
        name (``str``, *optional*):
            User name.

        phone_number (``str``, *optional*):
            User's phone number.

        email (``str``, *optional*):
            User email.

        shipping_address (:obj:`~pyrogram.types.ShippingAddress`, *optional*):
            User shipping address.

    """

    def __init__(
        self,
        *,
        name: str | None = None,
        phone_number: str | None = None,
        email: str | None = None,
        shipping_address: types.ShippingAddress | None = None
    ):
        super().__init__()

        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.shipping_address = shipping_address
