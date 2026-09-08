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

import random

from pyrogram import raw, types

from ..object import Object


class GiftedGrams(Object):
    """TON Grams were gifted to a user.

    Parameters:
        gifter (:obj:`~pyrogram.types.User`, *optional*):
            User that gifted Telegram Premium.
            None if the gift was anonymous.

        receiver (:obj:`~pyrogram.types.User`):
            User that received Telegram Premium.

        gram_amount (``int``):
            The received amount of Toncoins, in the smallest units of the cryptocurrency.

        transaction_id (``str``, *optional*):
            Identifier of the transaction for Telegram Stars purchase.
            For receiver only.

        sticker (:obj:`~pyrogram.types.Sticker`):
            A sticker to be shown in the message.
    """

    def __init__(
        self,
        *,
        gifter: types.User | None = None,
        receiver: types.User,
        gram_amount: int | None = None,
        transaction_id: str | None = None,
        sticker: types.Sticker | None = None,
    ):
        super().__init__()

        self.gifter = gifter
        self.receiver = receiver
        self.gram_amount = gram_amount
        self.transaction_id = transaction_id
        self.sticker = sticker

    @staticmethod
    async def _parse(
        client,
        action: raw.types.MessageActionGiftTon,
        gifter: raw.base.User | None = None,
        receiver: raw.base.User | None = None,
    ) -> GiftedGrams:
        raw_stickers = await client.invoke(
            raw.functions.messages.GetStickerSet(
                stickerset=raw.types.InputStickerSetTonGifts(), hash=0
            )
        )

        return GiftedGrams(
            gifter=await types.User._parse(client, gifter),
            receiver=await types.User._parse(client, receiver),
            gram_amount=action.crypto_amount,
            transaction_id=action.transaction_id,
            sticker=random.choice(
                types.List(
                    [
                        await types.Sticker._parse(
                            client, doc, {type(i): i for i in doc.attributes}
                        )
                        for doc in raw_stickers.documents
                    ]
                )
            ),
        )
