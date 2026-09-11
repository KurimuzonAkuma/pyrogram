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

"""`InlineKeyboardButton.write()` reads every field off the object the caller set."""

from __future__ import annotations as _annotations

from pyrogram import raw, types


class PeerResolver:
    """A client that resolves any peer, which is all `write()` asks of one."""

    async def resolve_peer(self, peer_id: int | str) -> raw.types.InputUserSelf:
        return raw.types.InputUserSelf()


async def test_a_chosen_chat_button_carries_its_own_query() -> None:
    button = types.InlineKeyboardButton(
        "text",
        switch_inline_query_chosen_chat=types.SwitchInlineQueryChosenChat(
            query="pick",
            allow_user_chats=True,
        ),
    )

    written = await button.write(PeerResolver())

    assert written.type == raw.types.InlineButtonTypeSwitchInline(
        query="pick",
        peer_types=[raw.types.InlineQueryPeerTypePM()],
    )


async def test_a_login_url_button_carries_the_url_of_its_login_url() -> None:
    button = types.InlineKeyboardButton(
        "text",
        login_url=types.LoginUrl(
            url="https://example.com",
            forward_text="Sign in",
            request_write_access=True,
        ),
    )

    written = await button.write(PeerResolver())

    assert written.type == raw.types.InputInlineButtonTypeUrlAuth(
        url="https://example.com",
        request_write_access=True,
        fwd_text="Sign in",
        bot=raw.types.InputUserSelf(),
    )
