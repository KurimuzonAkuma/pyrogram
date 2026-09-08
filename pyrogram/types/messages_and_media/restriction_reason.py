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

from ..object import Object


class RestrictionReason(Object):
    """Restriction reason.

    Parameters:
        platform (``str``):
            Platform identifier (ios, android, wp, all, etc.), can be concatenated with a dash as separator (android-ios, ios-wp, etc).

        reason (``str``):
            Restriction reason (porno, terms, etc.). Ignore this restriction reason if it is contained in the ignore_restriction_reasons » client configuration parameter.

        text (``str``):
            Error message to be shown to the user.
    """
    def __init__(
        self, *,
        platform: str,
        reason: str,
        text: str
    ):
        super().__init__()

        self.platform = platform
        self.reason = reason
        self.text = text

    @staticmethod
    def _parse(
        restriction_reason: raw.types.RestrictionReason
    ) -> RestrictionReason | None:
        if not restriction_reason:
            return None

        return RestrictionReason(
            platform=restriction_reason.platform,
            reason=restriction_reason.reason,
            text=restriction_reason.text
        )
