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


class GetDialogsCount:
    async def get_dialogs_count(
        self: pyrogram.Client, pinned_only: bool = False, from_archive: bool | None = None
    ) -> int:
        """Get the total count of your dialogs.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            pinned_only (``bool``, *optional*):
                Pass True if you want to count only pinned dialogs.
                Defaults to False.

            from_archive (``bool``, *optional*):
                Pass True to get dialogs count from archive.

        Returns:
            ``int``: On success, the dialogs count is returned.

        Example:
            .. code-block:: python

                count = await app.get_dialogs_count()
                print(count)
        """

        if pinned_only:
            r = await self.invoke(
                raw.functions.messages.GetPinnedDialogs(folder_id=1 if from_archive else 0)
            )

            return len(r.dialogs)
        else:
            r = await self.invoke(
                raw.functions.messages.GetDialogs(
                    offset_date=0,
                    offset_id=0,
                    offset_peer=raw.types.InputPeerEmpty(),
                    limit=1,
                    hash=0,
                    folder_id=None if from_archive is None else 1 if from_archive else 0,
                )
            )

            if isinstance(r, raw.types.messages.Dialogs):
                return len(r.dialogs)
            else:
                return r.count
