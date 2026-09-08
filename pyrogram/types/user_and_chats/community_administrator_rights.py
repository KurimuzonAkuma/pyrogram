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

from typing import TYPE_CHECKING

from ..object import Object

if TYPE_CHECKING:
    from pyrogram import raw


class CommunityAdministratorRights(Object):
    """Describes rights of the administrator in a community.

    Parameters:
        can_manage_community (``bool``, *optional*):
            True, if the user is an administrator.
            Implied by any other privilege.

        can_change_info (``bool``, *optional*):
            True, if the administrator can change the community name, photo, and other settings.

        can_edit_chat_list (``bool``, *optional*):
            True, if the user can change the chats added to the community.

        can_promote_members (``bool``, *optional*):
            True, if the administrator can add new administrators with a subset of their own privileges or demote administrators that were directly or indirectly promoted by them.

        can_ban_members (``bool``, *optional*):
            True, if the administrator can ban, or unban community members.
    """

    def __init__(
        self,
        *,
        can_manage_community: bool,
        can_change_info: bool,
        can_edit_chat_list: bool,
        can_promote_members: bool,
        can_ban_members: bool,
    ):
        super().__init__()

        self.can_manage_community = can_manage_community
        self.can_change_info = can_change_info
        self.can_edit_chat_list = can_edit_chat_list
        self.can_promote_members = can_promote_members
        self.can_ban_members = can_ban_members

    @staticmethod
    def _parse(admin_rights: raw.base.ChatAdminRights) -> CommunityAdministratorRights:
        if admin_rights is None:
            return None

        return CommunityAdministratorRights(
            can_manage_community=admin_rights.other,
            can_change_info=admin_rights.change_info,
            can_edit_chat_list=admin_rights.manage_linked_peers,
            can_promote_members=admin_rights.add_admins,
            can_ban_members=admin_rights.ban_users,
        )
