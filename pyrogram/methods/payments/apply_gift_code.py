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

import re

import pyrogram
from pyrogram import raw


class ApplyGiftCode:
    async def apply_gift_code(
        self: pyrogram.Client,
        link: str,
    ) -> bool:
        """Apply a gift code.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            link (``str``):
                The gift code link.

        Returns:
            ``bool``: On success, True is returned.

        Raises:
            ValueError: In case the gift code link is invalid.

        Example:
            .. code-block:: python

                # apply a gift code
                await app.apply_gift_code("t.me/giftcode/abc1234567def")
        """
        match = re.match(r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/(?:giftcode/|\+))([\w-]+)$", link)

        if match:
            slug = match.group(1)
        elif isinstance(link, str):
            slug = link
        else:
            raise ValueError("Invalid gift code link")

        await self.invoke(
            raw.functions.payments.ApplyGiftCode(
                slug=slug
            )
        )

        return True
