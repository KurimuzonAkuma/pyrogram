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

import re

import pyrogram
from pyrogram import raw

from .input_invoice import InputInvoice


class InputInvoiceName(InputInvoice):
    """An invoice from a link.

    Parameters:
        name (``str``):
            The name of the invoice or link itself.
    """
    def __init__(
        self,
        name: str,
    ):
        super().__init__()

        self.name = name

    async def write(self, client: pyrogram.Client):
        match = re.match(r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/\$)([\w-]+)$", self.name)

        if match:
            slug = match.group(1)
        else:
            slug = self.name

        return raw.types.InputInvoiceSlug(
            slug=slug
        )
