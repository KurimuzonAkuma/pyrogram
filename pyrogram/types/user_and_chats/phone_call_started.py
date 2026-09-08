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


class PhoneCallStarted(Object):
    """A service message about a phone_call started in the chat.

    Parameters:
        id (``int``):
            Unique call identifier.

        is_video (``bool``):
            True, if call was a video call.
    """

    def __init__(
        self, *,
        id: int,
        is_video: bool
    ):
        super().__init__()

        self.id = id
        self.is_video = is_video

    @staticmethod
    def _parse(action: raw.types.MessageActionPhoneCall) -> PhoneCallStarted:
        return PhoneCallStarted(
            id=action.call_id,
            is_video=action.video
        )
