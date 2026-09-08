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


class ViewMessages:
    async def view_messages(
        self: pyrogram.Client,
        chat_id: int | str,
        message_id: int | list[int],
    ) -> bool:
        """Increment message views counter.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int`` | List of ``int``):
                Identifier or list of message identifiers of the target message.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Increment message views
                await app.view_messages(chat_id, 1)
        """
        ids = [message_id] if not isinstance(message_id, list) else message_id

        r = await self.invoke(
            raw.functions.messages.GetMessagesViews(
                peer=await self.resolve_peer(chat_id), id=ids, increment=True
            )
        )

        return bool(r)
