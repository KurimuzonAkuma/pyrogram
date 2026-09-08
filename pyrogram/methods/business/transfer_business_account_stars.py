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


class TransferBusinessAccountStars:
    async def transfer_business_account_stars(
        self: pyrogram.Client,
        business_connection_id: str,
        star_count: int,
    ) -> bool:
        """Transfers Telegram Stars from the business account balance to the bot’s balance.

        .. note::

            Requires the `can_transfer_stars` business bot right.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            business_connection_id (``str``):
                Unique identifier of the business connection.

            star_count (``int`` | ``str``):
                Number of Telegram Stars to transfer, 1-10000.

        Returns:
            ``bool``: On success, True is returned.
        """
        # Why telegram won't let us just use InputPeerSelf :(
        if self.me:
            bot_id = self.me.id
        else:
            bot_id = (
                await self.invoke(raw.functions.users.GetUsers(id=[raw.types.InputPeerSelf()]))
            )[0].id

        invoice = raw.types.InputInvoiceBusinessBotTransferStars(
            bot=await self.resolve_peer(bot_id), stars=star_count
        )

        payment_form = await self.invoke(
            raw.functions.payments.GetPaymentForm(invoice=invoice),
            business_connection_id=business_connection_id,
        )

        await self.invoke(
            raw.functions.payments.SendStarsForm(
                form_id=payment_form.form_id,
                invoice=invoice,
            ),
            business_connection_id=business_connection_id,
        )

        return True
