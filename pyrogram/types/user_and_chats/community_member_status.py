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

from pyrogram import raw, types

from ..object import Object


class CommunityMemberStatus(Object):
    """Provides information about the status of a member in a community.

    It can be one of:

    - :obj:`~pyrogram.types.CommunityMemberStatusCreator`
    - :obj:`~pyrogram.types.CommunityMemberStatusAdministrator`
    - :obj:`~pyrogram.types.CommunityMemberStatusMember`
    - :obj:`~pyrogram.types.CommunityMemberStatusLeft`
    - :obj:`~pyrogram.types.CommunityMemberStatusBanned`
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def _parse(
        community: raw.types.Community | raw.types.CommunityForbidden,
    ) -> CommunityMemberStatus:
        if isinstance(community, raw.types.CommunityForbidden):
            return CommunityMemberStatusBanned()

        if community.creator:
            return CommunityMemberStatusCreator()

        if community.admin_rights:
            return CommunityMemberStatusAdministrator(
                can_be_edited=True,  # TODO: fix
                rights=types.CommunityAdministratorRights._parse(community.admin_rights),
            )

        if community.left:
            return CommunityMemberStatusLeft()

        return CommunityMemberStatusMember()


class CommunityMemberStatusCreator(CommunityMemberStatus):
    """The user is the owner of the community and has all the administrator privileges."""

    def __init__(self):
        super().__init__()


class CommunityMemberStatusAdministrator(CommunityMemberStatus):
    """The user is a member of the community and has some additional privileges.

    Parameters:
        can_be_edited (``bool``):
            True, if the current user can edit the administrator privileges for the called user.

        rights (:obj:`~pyrogram.types.CommunityAdministratorRights`):
            Rights of the administrator.
    """

    def __init__(self, can_be_edited: bool, rights: types.CommunityAdministratorRights):
        super().__init__()

        self.can_be_edited = can_be_edited
        self.rights = rights


class CommunityMemberStatusMember(CommunityMemberStatus):
    """The user is a member of the community, without any additional privileges or restrictions."""

    def __init__(self):
        super().__init__()


class CommunityMemberStatusLeft(CommunityMemberStatus):
    """The user or the chat is not a community member."""

    def __init__(self):
        super().__init__()


class CommunityMemberStatusBanned(CommunityMemberStatus):
    """The user or the chat was banned in the community; implies ban in all chats in the community."""

    def __init__(self):
        super().__init__()
