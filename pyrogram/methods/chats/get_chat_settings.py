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


class GetChatSettings:
    async def get_chat_settings(self: pyrogram.Client, chat_id: int | str) -> types.ChatSettings:
        """Get information about a chat settings.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                Unique identifier for the target chat in form of a *t.me/joinchat/* link, identifier (int) or username
                of the target channel/supergroup (in the format @username).

        Returns:
            :obj:`~pyrogram.types.ChatSettings`: On success, a chat settings object is returned.

        Raises:
            ValueError: In case the chat invite link points to a chat you haven't joined yet.

        Example:
            .. code-block:: python

                settings = await app.get_chat_settings("pyrogram")
                print(settings)
        """
        r = await self.invoke(
            raw.functions.messages.GetPeerSettings(peer=await self.resolve_peer(chat_id))
        )

        users = {i.id: i for i in r.users}

        return await types.ChatSettings._parse(self, r.settings, users)
