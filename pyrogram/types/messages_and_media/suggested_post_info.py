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

from datetime import datetime

from pyrogram import raw, types, utils, enums

from ..object import Object


class SuggestedPostInfo(Object):
    """Contains information about a suggested post.

    Parameters:
        price (:obj:`~pyrogram.types.SuggestedPostPrice`, *optional*):
            Proposed price of the post.
            If the field is omitted, then the post is unpaid.

        send_date (:py:obj:`~datetime.datetime`, *optional*):
            Proposed send date of the post.
            If the field is omitted, then the post can be published at any time
            within 30 days at the sole discretion of the user or administrator who approves it.

        state (:obj:`~pyrogram.enums.SuggestedPostState`, *optional*):
            State of the suggested post.
    """

    def __init__(
        self,
        *,
        price: types.SuggestedPostPrice | None = None,
        send_date: datetime | None = None,
        state: enums.SuggestedPostState | None = None,
    ):
        super().__init__()

        self.price = price
        self.send_date = send_date
        self.state = state

    @staticmethod
    def _parse(suggested_post: raw.types.SuggestedPost) -> SuggestedPostInfo | None:
        if not suggested_post:
            return None

        state = None

        if suggested_post.accepted:
            state = enums.SuggestedPostState.APPROVED
        elif suggested_post.rejected:
            state = enums.SuggestedPostState.DECLINED
        else:
            state = enums.SuggestedPostState.PENDING

        return SuggestedPostInfo(
            price=types.SuggestedPostPrice._parse(suggested_post.price),
            send_date=utils.timestamp_to_datetime(suggested_post.schedule_date),
            state=state,
        )
