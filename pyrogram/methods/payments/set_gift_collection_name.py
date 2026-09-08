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


class SetGiftCollectionName:
    async def set_gift_collection_name(
        self: pyrogram.Client,
        owner_id: int | str,
        collection_id: int,
        name: str
    ) -> types.GiftCollection:
        """Changes name of a gift collection.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            owner_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".

            collection_id (``int``):
                Identifier of the gift collection.

            name (``str``):
                New name of the collection, 1-12 characters.

        Returns:
            :obj:`~pyrogram.types.GiftCollection`: On success, a updated collection is returned.

        Example:
            .. code-block:: python

                await set_gift_collection_name("me", 123, "My best gifts!")
        """
        r = await self.invoke(
            raw.functions.payments.UpdateStarGiftCollection(
                peer=await self.resolve_peer(owner_id),
                collection_id=collection_id,
                title=name
            )
        )

        return await types.GiftCollection._parse(self, r)
