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

from pyrogram import raw

from ..object import Object


class SwitchInlineQueryChosenChat(Object):
    """This object represents an inline button that switches the current user to inline mode in a chosen chat, with an optional default inline query.

    Parameters:
        query (``str``, *optional*):
            The default inline query to be inserted in the input field. If left empty, only the bot's username will be inserted.

        allow_user_chats (``bool``, *optional*):
            *True*, if private chats with users can be chosen.

        allow_bot_chats (``bool``, *optional*):
            *True*, if private chats with bots can be chosen.

        allow_group_chats (``bool``, *optional*):
            *True*, if group and supergroup chats can be chosen.

        allow_channel_chats (``bool``, *optional*):
            *True*, if channel chats can be chosen.
    """

    def __init__(
        self,
        *,
        query: str | None = None,
        allow_user_chats: bool | None = None,
        allow_bot_chats: bool | None = None,
        allow_group_chats: bool | None = None,
        allow_channel_chats: bool | None = None,
    ):
        super().__init__()

        self.query = query
        self.allow_user_chats = allow_user_chats
        self.allow_bot_chats = allow_bot_chats
        self.allow_group_chats = allow_group_chats
        self.allow_channel_chats = allow_channel_chats

    @staticmethod
    def _parse(
        button_type: raw.types.InlineButtonTypeSwitchInline,
    ) -> SwitchInlineQueryChosenChat | None:
        if not isinstance(button_type, raw.types.InlineButtonTypeSwitchInline):
            return None

        if not button_type.peer_types:
            return None

        allow_user_chats = None
        allow_bot_chats = None
        allow_group_chats = None
        allow_channel_chats = None

        for peer_type in button_type.peer_types:
            if isinstance(
                peer_type,
                (raw.types.InlineQueryPeerTypeBotPM, raw.types.InlineQueryPeerTypeSameBotPM),
            ):
                allow_bot_chats = True

            elif isinstance(peer_type, raw.types.InlineQueryPeerTypeBroadcast):
                allow_channel_chats = True

            elif isinstance(
                peer_type,
                (raw.types.InlineQueryPeerTypeChat, raw.types.InlineQueryPeerTypeMegagroup),
            ):
                allow_group_chats = True

            elif isinstance(peer_type, raw.types.InlineQueryPeerTypePM):
                allow_user_chats = True

        return SwitchInlineQueryChosenChat(
            query=button_type.query,
            allow_user_chats=allow_user_chats,
            allow_bot_chats=allow_bot_chats,
            allow_group_chats=allow_group_chats,
            allow_channel_chats=allow_channel_chats,
        )

