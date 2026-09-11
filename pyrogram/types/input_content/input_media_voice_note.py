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

import io
import os
import re
from pathlib import Path
from typing import BinaryIO
from collections.abc import Callable

import pyrogram
from pyrogram import raw, utils
from pyrogram._typing import PathType
from pyrogram.file_id import FileType

from ... import enums
from ..messages_and_media import MessageEntity
from .input_media import InputMedia


class InputMediaVoiceNote(InputMedia):
    """A voice note to be sent inside a rich message.

    It is intended to be used with :obj:`~pyrogram.types.InputRichBlockVoiceNote`.

    Parameters:
        media (``str`` | ``os.PathLike`` | ``BinaryIO``):
            Voice note to send.
            Pass a file_id as string to send a voice note that exists on the Telegram servers or
            pass a file path as string to upload a new voice note that exists on your local machine or
            pass a binary file-like object with its attribute “.name” set for in-memory uploads or
            pass an HTTP URL as a string for Telegram to get a voice note from the Internet.

        caption (``str``, *optional*):
            Caption of the voice note to be sent, 0-1024 characters.
            If not specified, the original caption is kept. Pass "" (empty string) to remove the caption.

        parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
            By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
            List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

        duration (``int``, *optional*):
            Duration of the voice note in seconds

    Raises:
        FileNotFoundError: In case a local ``os.PathLike`` doesn't point to an existing file.
    """

    def __init__(
        self,
        media: PathType | BinaryIO,
        caption: str = "",
        parse_mode: enums.ParseMode | None = None,
        caption_entities: list[MessageEntity] | None = None,
        duration: int = 0,
    ) -> None:
        super().__init__(media, caption, parse_mode, caption_entities)

        self.duration = duration

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        progress: Callable | None = None,
        progress_args: tuple = (),
        ttl_seconds: int | None = None,
        **kwargs,
    ) -> raw.base.InputMedia:
        if chat_id is None:
            peer = raw.types.InputPeerSelf()
        else:
            peer = await client.resolve_peer(chat_id)

        if isinstance(self.media, io.BytesIO) or Path(self.media).is_file():
            mime_type: str = client.guess_mime_type(self.media) or "audio/ogg"

            if mime_type == "audio/mpeg":
                mime_type = "audio/ogg"

            uploaded_media = await client.invoke(
                raw.functions.messages.UploadMedia(
                    peer=peer,
                    media=raw.types.InputMediaUploadedDocument(
                        mime_type=mime_type,
                        file=await client.save_file(
                            self.media,
                            progress=progress,
                            progress_args=progress_args,
                        ),
                        attributes=[
                            raw.types.DocumentAttributeAudio(
                                voice=True,
                                duration=self.duration,
                            ),
                        ],
                        ttl_seconds=ttl_seconds,
                    ),
                ),
            )

            return raw.types.InputMediaDocument(
                id=raw.types.InputDocument(
                    id=uploaded_media.document.id,
                    access_hash=uploaded_media.document.access_hash,
                    file_reference=uploaded_media.document.file_reference,
                ),
            )

        if isinstance(self.media, os.PathLike):
            raise FileNotFoundError(f"No such file or directory: {self.media}")

        if re.match("^https?://", self.media):
            return raw.types.InputMediaDocumentExternal(
                url=self.media,
                ttl_seconds=ttl_seconds,
            )

        return utils.get_input_media_from_file_id(
            self.media,
            FileType.VOICE,
            ttl_seconds=ttl_seconds,
        )
