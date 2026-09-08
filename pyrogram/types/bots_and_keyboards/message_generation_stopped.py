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
from ..update import Update


class MessageGenerationStopped(Object, Update):
    """This object describes an update about a user stopping message generation.

    Parameters:
        chat (:obj:`~pyrogram.types.Chat`):
            Chat in which the message is generated.

        message_thread_id (``int``, *optional*):
            Unique identifier of the message thread in which the message is generated.

        draft_id (``int``):
            Unique identifier of the message draft which was stopped.
    """

    def __init__(self, *, chat: types.Chat, message_thread_id: int | None = None, draft_id: int):
        super().__init__()

        self.chat = chat
        self.message_thread_id = message_thread_id
        self.draft_id = draft_id

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        update: raw.types.UpdateUserTyping | raw.types.UpdateChannelUserTyping,
        users: list[raw.base.User],
        chats: list[raw.base.Chat],
    ) -> MessageGenerationStopped:
        action: raw.types.SendMessageStopDraftAction = update.action

        return MessageGenerationStopped(
            chat=await types.Chat._parse_chat(
                client=client,
                chat=users.get(getattr(update, "user_id", None))
                or chats.get(getattr(update, "channel_id", None)),
            ),
            message_thread_id=update.top_msg_id,
            draft_id=action.random_id,
        )
