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
from pyrogram import types, enums


class GetChatsForFolderInviteLink:
    async def get_chats_for_folder_invite_link(
        self: pyrogram.Client,
        chat_folder_id: int
    ) -> list[types.Chat]:
        """Returns chats from a chat folder, suitable for adding to a chat folder invite link.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_folder_id (``int``):
                Unique identifier (int) of the target folder.

        Returns:
            List of :obj:`~pyrogram.types.Chat`: On success, list of suitable chats is returned.

        Example:
            .. code-block:: python

                for chat in await app.get_chats_for_folder_invite_link(folder_id):
                    print(chat.title)
        """
        folder = None
        chats = types.List()

        for f in await self.get_folders():
            if f.id == chat_folder_id:
                folder = f
                break

        if not folder:
            raise ValueError("Folder not found")

        if (
            folder.excluded_chats
            or folder.exclude_muted
            or folder.exclude_read
            or folder.exclude_archived
            or folder.include_contacts
            or folder.include_non_contacts
            or folder.include_bots
            or folder.include_groups
            or folder.include_channels
        ):
            return chats

        pinned_chats = folder.pinned_chats or []
        included_chats = folder.included_chats or []
        available_chats = pinned_chats + included_chats

        for chat in available_chats:
            if chat.type in (enums.ChatType.FORUM, enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL):
                chats.append(chat)

        return chats
