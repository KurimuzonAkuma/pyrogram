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


class DeleteFolderInviteLink:
    async def delete_folder_invite_link(
        self: pyrogram.Client, chat_folder_id: int, invite_link: str
    ) -> bool:
        """Deletes an invite link for a chat folder.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_folder_id (``int``):
                Unique identifier (int) of the target folder.

            invite_link (``str``):
                Invite link to be edited.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Delete folder link
                await app.delete_folder_invite_link(
                    chat_folder_id=folder_id,
                    invite_link="https://t.me/addlist/abcde"
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
            raw.functions.chatlists.DeleteExportedInvite(
                chatlist=raw.types.InputChatlistDialogFilter(filter_id=chat_folder_id), slug=slug
            )
        )

        return r
