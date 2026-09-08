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
from pyrogram import raw, types, utils

from ..object import Object


class FactCheck(Object):
    """Represents a fact-check created by an independent fact-checker.

    Parameters:
        need_check (``bool``, *optional*):
            If set, the country/text fields will not be set, and the fact check must be fetched manually by the client (if it isn't already cached with the key specified in hash) using bundled messages.getFactCheck requests, when the message with the factcheck scrolls into view.

        country (``str``, *optional*):
            A two-letter ISO 3166-1 alpha-2 country code of the country for which the fact-check should be shown.

        text (``str``, *optional*):
            The fact-check.

        entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            For text messages, special entities like usernames, URLs, bot commands, etc. that appear in the text.
    """

    def __init__(
        self,
        *,
        need_check: bool | None = None,
        country: str | None = None,
        text: str | None = None,
        entities: list[types.MessageEntity] | None = None,
    ):
        super().__init__()

        self.need_check = need_check
        self.country = country
        self.text = text
        self.entities = entities

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        fact_check: raw.types.FactCheck,
        users: dict[int, list[raw.base.User]],
    ) -> FactCheck | None:
        if not fact_check:
            return None

        message, entities = (
            await utils.parse_text_with_entities(client, getattr(fact_check, "text", None), users)
        ).values()

        return FactCheck(
            need_check=getattr(fact_check, "need_check", None),
            country=getattr(fact_check, "country", None),
            text=message,
            entities=entities,
        )
