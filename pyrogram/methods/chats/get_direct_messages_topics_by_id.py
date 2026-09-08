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

import logging
from typing import overload
from collections.abc import Iterable

import pyrogram
from pyrogram import raw, types

log = logging.getLogger(__name__)


class GetDirectMessagesTopicsByID:
    @overload
    async def get_direct_messages_topics_by_id(
        self: pyrogram.Client, chat_id: int | str, topic_ids: int
    ) -> types.DirectMessagesTopic | None: ...

    @overload
    async def get_direct_messages_topics_by_id(
        self: pyrogram.Client, chat_id: int | str, topic_ids: Iterable[int]
    ) -> list[types.DirectMessagesTopic]: ...

    async def get_direct_messages_topics_by_id(
        self: pyrogram.Client, chat_id: int | str, topic_ids: int | Iterable[int]
    ) -> types.DirectMessagesTopic | list[types.DirectMessagesTopic] | None:
        """Get one or more direct message topic from a chat by using topic identifiers.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            topic_ids (``int`` | Iterable of ``int``, *optional*):
                Pass a single topic identifier or an iterable of topic ids (as integers) to get the information of the
                topic themselves.

        Returns:
            :obj:`~pyrogram.types.DirectMessagesTopic` | List of :obj:`~pyrogram.types.DirectMessagesTopic` | ``None``:
            In case *topic_ids* was not a list, a single topic is returned, otherwise a list of topics is returned. In
            case *topic_ids* was not a list and the chat has no topic with that identifier, None is returned.

        Example:
            .. code-block:: python

                # Get one topic
                await app.get_direct_messages_topics_by_id(chat_id, 12345)

                # Get more than one topic (list of topics)
                await app.get_direct_messages_topics_by_id(chat_id, [12345, 12346])
        """
        is_iterable = not isinstance(topic_ids, int)
        ids = list(topic_ids) if is_iterable else [topic_ids]

        r = await self.invoke(
            raw.functions.messages.GetSavedDialogsByID(
                ids=[await self.resolve_peer(i) for i in ids],
                parent_peer=await self.resolve_peer(chat_id),
            )
        )

        users = {i.id: i for i in r.users}
        chats = {i.id: i for i in r.chats}

        topics = types.List()

        for i in r.dialogs:
            topics.append(
                await types.DirectMessagesTopic._parse(
                    client=self, topic=i, users=users, chats=chats
                )
            )

        # A topic exists only once its peer has written to the chat, and asking for a peer
        #  without one answers with an empty `dialogs` vector rather than an error:
        #
        #  await app.get_direct_messages_topics_by_id(chat_id, user_id)  # -> None
        return topics if is_iterable else topics[0] if topics else None
