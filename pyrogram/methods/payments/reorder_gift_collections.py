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


class ReorderGiftCollections:
    async def reorder_gift_collections(
        self: pyrogram.Client,
        owner_id: int | str,
        collection_ids: list[int]
    ) -> types.GiftCollection:
        """Changes order of gift collections.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            owner_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".

            gift_ids (List of ``int``):
                New order of gift collections.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                await app.reorder_gift_collections("me", [123, 456])
        """
        r = await self.invoke(
            raw.functions.payments.ReorderStarGiftCollections(
                peer=await self.resolve_peer(owner_id),
                order=collection_ids
            )
        )

        return r
