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

from ..object import Object
from .input_rich_block import _get_input_document, _get_input_photo


class InputRichMessageMedia(Object):
    """Describes a media element embedded in an outgoing rich message.

    Parameters:
        id (``str``):
            Unique identifier of the media used in a ``tg://photo?id=``, ``tg://video?id=``,
            ``tg://document?id=``, or ``tg://audio?id=`` link.
            1-64 characters, only A-Z, a-z, 0-9, _ and - are allowed.

        media (:obj:`~pyrogram.types.InputMediaAnimation` | :obj:`~pyrogram.types.InputMediaAudio` | :obj:`~pyrogram.types.InputMediaDocument` | :obj:`~pyrogram.types.InputMediaPhoto` | :obj:`~pyrogram.types.InputMediaVideo` | :obj:`~pyrogram.types.InputMediaVoiceNote`):
            The media to be sent.
            Everything except the media itself and its properties is ignored.
    """

    def __init__(
        self,
        id: str,
        media: types.InputMediaAnimation
        | types.InputMediaAudio
        | types.InputMediaDocument
        | types.InputMediaPhoto
        | types.InputMediaVideo
        | types.InputMediaVoiceNote,
    ) -> None:
        super().__init__()

        self.id = id
        self.media = media

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
    ) -> raw.base.InputRichFile:
        input_media = await self.media.write(
            client=client,
            chat_id=chat_id,
        )

        if isinstance(self.media, types.InputMediaPhoto):
            input_photo = await _get_input_photo(
                client,
                chat_id=chat_id,
                input_media=input_media,
            )

            return raw.types.InputRichFilePhoto(
                id=self.id,
                photo=input_photo,
            )

        input_document = await _get_input_document(
            client,
            chat_id=chat_id,
            input_media=input_media,
        )

        return raw.types.InputRichFileDocument(
            id=self.id,
            document=input_document,
        )
