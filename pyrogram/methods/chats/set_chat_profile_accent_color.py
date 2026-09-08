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


class SetChatProfileAccentColor:
    async def set_chat_profile_accent_color(
        self: pyrogram.Client,
        chat_id: int | str,
        profile_accent_color_id: int | None = None,
        profile_background_custom_emoji_id: str | None = None,
    ) -> bool:
        """Update color

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            profile_accent_color_id (``int``, *optional*):
                Identifier of the accent color to use for profile.

            profile_background_custom_emoji_id (``str``, *optional*):
                Identifier of a custom emoji to be shown on the chat's profile photo background.

        Returns:
            ``bool``: On success, True is returned.
        """
        peer = await self.resolve_peer(chat_id)

        if profile_background_custom_emoji_id is not None:
            profile_background_custom_emoji_id = int(profile_background_custom_emoji_id)

        if isinstance(peer, raw.types.InputPeerSelf):
            r = await self.invoke(
                raw.functions.account.UpdateColor(
                    for_profile=True,
                    color=raw.types.PeerColor(
                        color=profile_accent_color_id,
                        background_emoji_id=profile_background_custom_emoji_id,
                    ),
                )
            )
        elif isinstance(peer, raw.types.InputPeerChannel):
            r = await self.invoke(
                raw.functions.channels.UpdateColor(
                    channel=peer,
                    for_profile=True,
                    color=profile_accent_color_id,
                    background_emoji_id=profile_background_custom_emoji_id,
                )
            )
        else:
            raise ValueError("Invalid peer provided")

        return bool(r)
