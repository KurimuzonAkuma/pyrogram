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
from pyrogram import raw, types


class EditFolderInviteLink:
    async def edit_folder_invite_link(
        self: pyrogram.Client,
        chat_folder_id: int,
        invite_link: str,
        chat_ids: list[int | str] | None = None,
        name: str | None = None,
    ) -> types.FolderInviteLink:
        """Edits an invite link for a chat folder.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_folder_id (``int``):
                Unique identifier (int) of the target folder.

            invite_link (``str``):
                Invite link to be edited.

            chat_ids (List of ``int`` | ``str``, *optional*):
                Identifiers of chats to be accessible by the invite link.
                Use :meth:`~pyrogram.Client.get_chats_for_folder_invite_link` to get suitable chats.
                Basic groups will be automatically converted to supergroups before link creation.

            name (``str``, *optional*):
                Name of the link, 0-32 characters.

        Returns:
            :obj:`~pyrogram.types.FolderInviteLink`: On success, information about the invite link is returned.

        Example:
            .. code-block:: python

                # Edit folder link
                await app.edit_folder_invite_link(
                    chat_folder_id=folder_id,
                    invite_link="https://t.me/addlist/abcde",
                    chat_ids=[123456789, 987654321],
                    name="News"
                )
        """
        match = re.match(
            r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/(?:addlist/|\+))([\w-]+)$",
            invite_link,
        )

        if match:
            slug = match.group(1)
        elif isinstance(invite_link, str):
            slug = invite_link
        else:
            raise ValueError("Invalid folder invite link")

        r = await self.invoke(
            raw.functions.chatlists.EditExportedInvite(
                chatlist=raw.types.InputChatlistDialogFilter(filter_id=chat_folder_id),
                slug=slug,
                title=name,
                peers=[await self.resolve_peer(i) for i in chat_ids]
                if chat_ids is not None
                else None,
            )
        )

        return types.FolderInviteLink._parse(r)
