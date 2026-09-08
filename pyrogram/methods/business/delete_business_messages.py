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

from collections.abc import Iterable

import pyrogram
from pyrogram import raw


class DeleteBusinessMessages:
    async def delete_business_messages(
        self: pyrogram.Client, business_connection_id: str, message_ids: int | Iterable[int]
    ) -> int:
        """Delete messages on behalf of a business account.

        .. note::

            Requires the `can_delete_sent_messages` business bot right to delete messages sent by the bot itself,
            or the `can_delete_all_messages` business bot right to delete any message.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            business_connection_id (``str``):
                Unique identifier of business connection on behalf of which to send the request.

            message_ids (``int`` | Iterable of ``int``):
                An iterable of message identifiers to delete (integers) or a single message id.
                All messages must be from the same chat.

        Returns:
            ``int``: Amount of affected messages

        Example:
            .. code-block:: python

                # Delete one message
                await app.delete_business_messages(connection_id, message_id)

                # Delete multiple messages at once
                await app.delete_business_messages(connection_id, list_of_message_ids)
        """
        message_ids = list(message_ids) if not isinstance(message_ids, int) else [message_ids]

        r = await self.invoke(
            raw.functions.messages.DeleteMessages(id=message_ids, revoke=True),
            business_connection_id=business_connection_id,
        )

        return r.pts_count
