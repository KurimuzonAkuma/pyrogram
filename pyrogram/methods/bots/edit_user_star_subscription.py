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


class EditUserStarSubscription:
    async def edit_user_star_subscription(
        self: pyrogram.Client,
        user_id: int | str,
        telegram_payment_charge_id: str,
        is_canceled: bool,
    ) -> bool:
        """Cancels or re-enables Telegram Star subscription for a user.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user.

            telegram_payment_charge_id (``str``):
                Telegram payment identifier of the subscription.

            is_canceled (``bool``):
                Pass *True* to cancel extension of the user subscription, the subscription must be active up to the end of the current subscription period.
                Pass *False* to allow the user to re-enable a subscription that was previously canceled by the bot.

        Returns:
            ``bool``: On success, True is returned.
        """
        # `restore` is the opposite of `is_canceled`: the request cancels the subscription when
        #  the flag is absent and re-enables it when it is set. TDLib sends `!is_canceled` for the
        #  same call, and passing `is_canceled` straight through left the subscription renewing.
        #  https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/telegram/StarManager.cpp#L1100
        return await self.invoke(
            raw.functions.payments.BotCancelStarsSubscription(
                user_id=await self.resolve_peer(user_id),
                charge_id=telegram_payment_charge_id,
                restore=not is_canceled,
            )
        )
