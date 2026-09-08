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


class PaymentOption(Object):
    """Describes an additional payment option.

    Parameters:
        title (``str``):
            Title for the payment option.

        url (``str``):
            Payment form URL to be opened in a web view.
    """

    def __init__(self, *, title: str, url: str):
        super().__init__()

        self.title = title
        self.url = url

    @staticmethod
    def _parse(option: raw.base.PaymentFormMethod) -> PaymentOption:
        return PaymentOption(title=option.title, url=option.url)
