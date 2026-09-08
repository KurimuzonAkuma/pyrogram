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


class HideChatStories:
    async def hide_chat_stories(
        self: pyrogram.Client,
        chat_id: int | str,
    ) -> bool:
        """Hide the active stories of a user, preventing them from being displayed on the action bar on the homescreen.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

        Returns:
            ``bool``: On success, a bool is returned.

        Example:
            .. code-block:: python

                # Hide stories from specific chat
                await app.hide_chat_stories(chat_id)
        """
        r = await self.invoke(
            raw.functions.stories.TogglePeerStoriesHidden(
                peer=await self.resolve_peer(chat_id), hidden=True
            )
        )

        return r
