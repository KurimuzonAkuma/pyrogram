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

import pyrogram
from pyrogram import raw

from .input_invoice import InputInvoice


class InputInvoiceMessage(InputInvoice):
    """An invoice from a message or paid media purchase from paid media message.

    Parameters:
        chat_id (``int`` | ``str``):
            Unique identifier (int) or username (str) of the target chat.

        message_id (``int``):
            Unique message identifier.
    """

    def __init__(
        self,
        chat_id: int | str,
        message_id: int,
    ):
        super().__init__()

        self.chat_id = chat_id
        self.message_id = message_id

    async def write(self, client: pyrogram.Client):
        return raw.types.InputInvoiceMessage(
            peer=await client.resolve_peer(self.chat_id), msg_id=self.message_id
        )
