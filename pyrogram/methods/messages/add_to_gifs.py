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
from pyrogram.file_id import FileId


class AddToGifs:
    async def add_to_gifs(self: pyrogram.Client, file_id: str, unsave: bool = False) -> bool:
        """Add a GIF to the list of saved GIFs.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            file_id (``str``):
                Unique identifier for the GIF.

            unsave (``bool``, optional):
                Whether to remove the GIF from the list of saved GIFs. Defaults to ``False``.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.add_to_gifs(message.animation.file_id)

        """
        decoded_file_id = FileId.decode(file_id)

        return await self.invoke(
            raw.functions.messages.SaveGif(
                id=raw.types.InputDocument(
                    id=decoded_file_id.media_id,
                    file_reference=decoded_file_id.file_reference,
                    access_hash=decoded_file_id.access_hash,
                ),
                unsave=unsave,
            )
        )
