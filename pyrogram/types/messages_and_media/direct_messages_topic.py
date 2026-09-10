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

from ..object import Object


class DirectMessagesTopic(Object):
    """Contains information about a topic in a channel direct messages chat administered by the current user.

    Parameters:
        id (``int``):
            Unique topic identifier inside this chat.

        user (:obj:`~pyrogram.types.User`, *optional*):
            Information about the user that created the topic.

        can_send_unpaid_messages (``bool``, *optional*):
            True, if the other party can send unpaid messages even if the chat has paid messages enabled.

        is_marked_as_unread (``bool``, *optional*):
            True, if the forum topic is marked as unread.

        unread_count (``int``, *optional*):
            Number of unread messages in the chat.

        last_read_inbox_message_id (``int``, *optional*):
            Identifier of the last read incoming message.

        last_read_outbox_message_id (``int``, *optional*):
            Identifier of the last read outgoing message.

        unread_reactions_count (``int``, *optional*):
            Number of messages with unread reactions in the chat.

        last_message (:obj:`~pyrogram.types.Message`, *optional*):
            Last message in the topic.
    """

    def __init__(
        self,
        *,
        id: int,
        user: types.User | None = None,
        can_send_unpaid_messages: bool | None = None,
        is_marked_as_unread: bool | None = None,
        unread_count: int | None = None,
        last_read_inbox_message_id: int | None = None,
        last_read_outbox_message_id: int | None = None,
        unread_reactions_count: int | None = None,
        last_message: types.Message | None = None,
    ):
        super().__init__()

        self.id = id
        self.user = user
        self.can_send_unpaid_messages = can_send_unpaid_messages
        self.is_marked_as_unread = is_marked_as_unread
        self.unread_count = unread_count
        self.last_read_inbox_message_id = last_read_inbox_message_id
        self.last_read_outbox_message_id = last_read_outbox_message_id
        self.unread_reactions_count = unread_reactions_count
        self.last_message = last_message

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        topic: raw.types.MonoForumDialog,
        messages: dict | None = None,
        users: dict[int, raw.base.User] | None = None,
        chats: dict[int, raw.base.Chat] | None = None,
    ) -> DirectMessagesTopic:
        messages = messages or {}
        users = users or {}
        chats = chats or {}

        if not topic:
            return None

        return DirectMessagesTopic(
            id=topic.peer.user_id,
            user=await types.User._parse(client, users.get(topic.peer.user_id)),
            can_send_unpaid_messages=topic.nopaid_messages_exception,
            is_marked_as_unread=topic.unread_mark,
            unread_count=topic.unread_count,
            last_read_inbox_message_id=topic.read_inbox_max_id,
            last_read_outbox_message_id=topic.read_outbox_max_id,
            unread_reactions_count=topic.unread_reactions_count,
            last_message=messages.get(topic.top_message),
        )
