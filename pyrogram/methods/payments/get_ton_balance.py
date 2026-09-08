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


class GetTonBalance:
    async def get_ton_balance(
        self: pyrogram.Client
    ) -> float:
        """Get the current TON balance of the current account.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            ``float``: On success, the current stars balance is returned.

        Example:
            .. code-block:: python

                # Get stars balance of current account
                await app.get_stars_balance()

                # Get stars balance of a bot
                await app.get_stars_balance(chat_id="pyrogrambot")
        """
        r = await self.invoke(
            raw.functions.payments.GetStarsTransactions(
                peer=raw.types.InputPeerSelf(),
                offset="",
                limit=0,
                ton=True
            )
        )

        return r.balance.amount
