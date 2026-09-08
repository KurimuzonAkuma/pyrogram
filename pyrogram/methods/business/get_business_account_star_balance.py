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


class GetBusinessAccountStarBalance:
    async def get_business_account_star_balance(
        self: pyrogram.Client,
        business_connection_id: str,
    ) -> int:
        """Return the amount of Telegram Stars owned by a managed business account.

        .. note::

            Requires the `can_view_gifts_and_stars` business bot right.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            business_connection_id (``str``):
                Unique identifier of business connection on behalf of which to send the request.

        Returns:
            ``int``: On success, the current stars balance is returned.

        Example:
            .. code-block:: python

                # Get stars balance
                await app.get_business_account_star_balance("connection_id")
        """
        connection_info = await self.get_business_connection(business_connection_id)

        r = await self.invoke(
            raw.functions.payments.GetStarsStatus(
                peer=await self.resolve_peer(connection_info.user.id),
            ),
            business_connection_id=business_connection_id,
        )

        return r.balance.amount
