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
from pyrogram import enums, raw, types, utils

from ..object import Object


class ChatShared(Object):
    """Contains information about a chat shared with a bot.

    Parameters:
        button_id (``int``):
            Identifier of button.

        chat (:obj:`~pyrogram.types.Chat`):
            Requested chats.
    """

    def __init__(
        self,
        *,
        button_id: int,
        chat: types.Chat,
    ):
        super().__init__()

        self.button_id = button_id
        self.chat = chat

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        action: raw.types.MessageActionRequestedPeer | raw.types.MessageActionRequestedPeerSentMe,
        chats: dict[int, raw.base.Chat] | None = None,
    ) -> ChatShared | None:
        chats = chats or {}

        peer = action.peers[0]

        if isinstance(peer, (raw.types.PeerUser, raw.types.RequestedPeerUser)):
            return None

        peer_id = utils.get_peer_id(peer)
        peer_type = utils.get_peer_type(peer_id)

        if peer_type == "chat":
            chat_type = enums.ChatType.GROUP
        else:
            chat_type = enums.ChatType.CHANNEL

        chat_shared = None

        if isinstance(action, raw.types.MessageActionRequestedPeer):
            raw_chat = chats.get(utils.get_raw_peer_id(peer))

            if raw_chat:
                chat_shared = await types.Chat._parse_chat(client, raw_chat)
            else:
                chat_shared = types.Chat(id=peer_id, type=chat_type, client=client)
        elif isinstance(action, raw.types.MessageActionRequestedPeerSentMe):
            chat_shared = types.Chat(
                id=peer_id,
                type=chat_type,
                first_name=getattr(peer, "first_name", None),
                last_name=getattr(peer, "last_name", None),
                title=getattr(peer, "title", None),
                username=getattr(peer, "username", None),
                photo=types.Photo._parse(client, getattr(peer, "photo", None)),
                client=client,
            )

        return ChatShared(button_id=action.button_id, chat=chat_shared)
