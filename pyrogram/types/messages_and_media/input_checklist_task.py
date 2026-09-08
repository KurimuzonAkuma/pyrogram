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
from pyrogram import enums, raw, types, utils

from ..object import Object


class InputChecklistTask(Object):
    """Describes a task in a checklist to be sent.

    Parameters:
        id (``int``):
            Unique identifier of the task.

        text (``str``):
            Text of the task.

        parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
            The parse mode to use for the checklist.

        entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            List of special entities that appear in the checklist title.
    """

    def __init__(
        self,
        *,
        id: int,
        text: str,
        parse_mode: enums.ParseMode | None = None,
        entities: list[types.MessageEntity] | None = None,
    ):
        super().__init__()

        self.id = id
        self.text = text
        self.parse_mode = parse_mode
        self.entities = entities

    async def write(self, client: pyrogram.Client) -> raw.types.TodoItem:
        task_title, task_entities = (
            await utils.parse_text_entities(client, self.text, self.parse_mode, self.entities)
        ).values()

        return raw.types.TodoItem(
            id=self.id,
            title=raw.types.TextWithEntities(text=task_title, entities=task_entities or []),
        )
