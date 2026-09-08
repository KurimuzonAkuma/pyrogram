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
from pyrogram import raw, types


class ReadChatStories:
    async def read_chat_stories(
        self: pyrogram.Client,
        chat_id: int | str,
        max_id: int = 0,
    ) -> list[int]:
        """Mark all stories up to a certain identifier as read, for a given chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For a contact that exists in your Telegram address book you can use his phone number (str).

            max_id (``int``, *optional*):
                The id of the last story you want to mark as read.
                All the stories before this one will be marked as read as well.
                Defaults to 0 (mark every unread message as read).

        Returns:
            List of ``int``: On success, a list of read stories is returned.

        Example:
            .. code-block:: python

                # Read all stories
                await app.read_chat_stories(chat_id)

                # Mark stories as read only up to the given story id
                await app.read_chat_stories(chat_id, 123)
        """
        r = await self.invoke(
            raw.functions.stories.ReadStories(
                peer=await self.resolve_peer(chat_id),
                max_id=max_id or (1 << 31) - 1
            )
        )

        return types.List(r)
