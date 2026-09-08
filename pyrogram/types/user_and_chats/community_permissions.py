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


class CommunityPermissions(Object):
    """Describes actions that a user is allowed to take in a community.

    Parameters:
        can_edit_chat_list (``bool``, *optional*):
            True, if the user can change the chats added to the community.
    """

    def __init__(
        self,
        *,
        can_edit_chat_list: bool,
    ):
        super().__init__()

        self.can_edit_chat_list = can_edit_chat_list

    @staticmethod
    def _parse(denied_permissions: raw.base.ChatBannedRights) -> CommunityPermissions:
        if isinstance(denied_permissions, raw.types.ChatBannedRights):
            return CommunityPermissions(
                can_edit_chat_list=not denied_permissions.manage_linked_peers,
            )
