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
from pyrogram import raw, types
from pyrogram.raw.core import TLObject

from ..object import Object


def _collect_mentioned_user_ids(blocks: list[raw.base.PageBlock]) -> list[int]:
    user_ids: list[int] = []
    stack: list[TLObject] = list(blocks)

    while stack:
        current = stack.pop()

        if isinstance(current, raw.types.TextMentionName):
            user_ids.append(current.user_id)

        for slot in current.__slots__:
            value = getattr(current, slot)

            if isinstance(value, TLObject):
                stack.append(value)
            elif isinstance(value, list):
                stack.extend(item for item in value if isinstance(item, TLObject))

    return list(dict.fromkeys(user_ids))


class InputRichMessage(Object):
    """Describes a rich message to be sent.

    Exactly one of the fields *html*, *markdown*, or *blocks* must be used.

    Parameters:
        blocks (List of :obj:`~pyrogram.types.InputRichBlock`, *optional*):
            Content of the rich message to send described as a list of blocks.

        html (``str``, *optional*):
            Content of the rich message to send described using HTML formatting.
            See `rich message formatting options <https://core.telegram.org/bots/api#rich-message-formatting-options>`__ for more details.
            Use *media* field to specify the media used in the message.

        markdown (``str``, *optional*):
            Content of the rich message to send described using Markdown formatting.
            See `rich message formatting options <https://core.telegram.org/bots/api#rich-message-formatting-options>`__ for more details.
            Use *media* field to specify the media used in the message.

        media (List of :obj:`~pyrogram.types.InputRichMessageMedia`, *optional*):
            List of media that are specified in the *markdown* or *html* fields using
            ``tg://photo?id=``, ``tg://video?id=``, ``tg://document?id=``, and ``tg://audio?id=`` links.

        is_rtl (``bool``, *optional*):
            Pass *True* if the rich message must be shown right-to-left.

        skip_entity_detection (``bool``, *optional*):
            Pass *True* to skip automatic detection of entities
            (e.g., URLs, email addresses, username mentions, hashtags, cashtags, bot commands, or phone numbers) in the text.
    """

    def __init__(
        self,
        blocks: list[types.InputRichBlock] | None = None,
        html: str | None = None,
        markdown: str | None = None,
        media: list[types.InputRichMessageMedia] | None = None,
        is_rtl: bool | None = None,
        skip_entity_detection: bool | None = None,
    ) -> None:
        super().__init__()

        self.blocks = blocks
        self.html = html
        self.markdown = markdown
        self.media = media
        self.is_rtl = is_rtl
        self.skip_entity_detection = skip_entity_detection

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
    ) -> raw.base.InputRichMessage:
        if self.blocks:
            return await self._write_blocks(
                blocks=self.blocks,
                client=client,
                chat_id=chat_id,
            )

        files: list[raw.base.InputRichFile] | None = None
        if self.media:
            files = [
                await item.write(
                    client=client,
                    chat_id=chat_id,
                )
                for item in self.media
            ]

        if self.html:
            return raw.types.InputRichMessageHTML(
                html=self.html,
                rtl=self.is_rtl,
                noautolink=self.skip_entity_detection,
                files=files,
            )

        if self.markdown:
            return raw.types.InputRichMessageMarkdown(
                markdown=self.markdown,
                rtl=self.is_rtl,
                noautolink=self.skip_entity_detection,
                files=files,
            )

        raise ValueError("You must provide either blocks, markdown or html in the rich message")

    async def _write_blocks(
        self,
        *,
        blocks: list[types.InputRichBlock],
        client: pyrogram.Client,
        chat_id: int | str | None,
    ) -> raw.types.InputRichMessage:
        photos: list[raw.base.InputPhoto] = []
        documents: list[raw.base.InputDocument] = []

        raw_blocks = [
            await block.write(
                client=client,
                chat_id=chat_id,
                photos=photos,
                documents=documents,
            )
            for block in blocks
        ]

        users: list[raw.base.InputUser] = []
        for user_id in _collect_mentioned_user_ids(raw_blocks):
            peer = await client.resolve_peer(user_id)
            users.append(
                raw.types.InputUser(
                    user_id=peer.user_id,
                    access_hash=peer.access_hash,
                ),
            )

        return raw.types.InputRichMessage(
            rtl=self.is_rtl,
            noautolink=self.skip_entity_detection,
            blocks=raw_blocks,
            photos=photos or None,
            documents=documents or None,
            users=users or None,
        )
