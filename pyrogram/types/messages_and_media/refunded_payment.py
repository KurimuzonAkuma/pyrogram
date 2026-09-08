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


class RefundedPayment(Object):
    """This object contains basic information about a refunded payment.

    Parameters:
        currency (``str``):
            Three-letter ISO 4217 `currency <https://core.telegram.org/bots/payments#supported-currencies>`_ code, or ``XTR`` for payments in `Telegram Stars <https://t.me/BotNews/90>`_.

        total_amount (``int``):
            Total price in the smallest units of the currency (integer, **not** float/double). For example, for a price of ``US$ 1.45`` pass ``amount = 145``. See the __exp__ parameter in `currencies.json <https://core.telegram.org/bots/payments/currencies.json>`_, it shows the number of digits past the decimal point for each currency (2 for the majority of currencies).

        invoice_payload (``str``):
            Bot specified invoice payload. Only available to the bot that received the payment.

        telegram_payment_charge_id (``str``):
            Telegram payment identifier. Only available to the bot that received the payment.

        provider_payment_charge_id (``str``):
            Provider payment identifier. Only available to the bot that received the payment.
    """

    def __init__(
        self,
        *,
        currency: str,
        total_amount: str,
        invoice_payload: str,
        telegram_payment_charge_id: str,
        provider_payment_charge_id: str
    ):

        super().__init__()

        self.currency = currency
        self.total_amount = total_amount
        self.invoice_payload = invoice_payload
        self.telegram_payment_charge_id = telegram_payment_charge_id
        self.provider_payment_charge_id = provider_payment_charge_id

    @staticmethod
    def _parse(
        payment: raw.types.MessageActionPaymentRefunded
    ) -> RefundedPayment:
        invoice_payload = None

        # Try to decode invoice payload into string. If that fails, fallback to bytes instead of decoding by
        # ignoring/replacing errors, this way, button clicks will still work.
        try:
            invoice_payload = payment.payload.decode()
        except (UnicodeDecodeError, AttributeError):
            invoice_payload = getattr(payment, "payload", None)

        return RefundedPayment(
            currency=payment.currency,
            total_amount=payment.total_amount,
            invoice_payload=invoice_payload,
            telegram_payment_charge_id=payment.charge.id,
            provider_payment_charge_id=payment.charge.provider_charge_id
        )
