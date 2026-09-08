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


class ResetSessions:
    async def reset_sessions(
        self: pyrogram.Client,
    ) -> bool:
        """Terminates all user's authorized sessions except for the current one.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            ``bool``: On success, in case the sessions is destroyed, True is returned. Otherwise, False is returned.

        """
        r = await self.invoke(raw.functions.auth.ResetAuthorizations())

        return r
