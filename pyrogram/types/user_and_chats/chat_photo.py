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

from datetime import datetime

import pyrogram
from pyrogram import raw, types, utils
from pyrogram.file_id import FileId, FileType, FileUniqueId, FileUniqueType, ThumbnailSource

from ..object import Object


class ChatPhoto(Object):
    """A chat photo.

    Parameters:
        small_file_id (``str``):
            File identifier of small (160x160) chat photo.
            This file_id can be used only for photo download and only for as long as the photo is not changed.

        small_photo_unique_id (``str``):
            Unique file identifier of small (160x160) chat photo, which is supposed to be the same over time and for
            different accounts. Can't be used to download or reuse the file.

        big_file_id (``str``):
            File identifier of big (640x640) chat photo.
            This file_id can be used only for photo download and only for as long as the photo is not changed.

        big_photo_unique_id (``str``):
            Unique file identifier of big (640x640) chat photo, which is supposed to be the same over time and for
            different accounts. Can't be used to download or reuse the file.

        added_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the photo has been added.

        animation (:obj:`~pyrogram.types.AnimatedChatPhoto`, *optional*):
            A big (up to 1280x1280) animated variant of the photo in MPEG4 format.

        sticker (:obj:`~pyrogram.types.ChatPhotoSticker`, *optional*):
            A big (up to 1280x1280) static variant of the photo as a sticker.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        small_file_id: str,
        small_photo_unique_id: str,
        big_file_id: str,
        big_photo_unique_id: str,
        added_date: datetime | None = None,
        animation: types.AnimatedChatPhoto | None = None,
        sticker: types.ChatPhotoSticker | None = None,
    ):
        super().__init__(client)

        self.small_file_id = small_file_id
        self.small_photo_unique_id = small_photo_unique_id
        self.big_file_id = big_file_id
        self.big_photo_unique_id = big_photo_unique_id
        self.added_date = added_date
        self.animation = animation
        self.sticker = sticker

    @staticmethod
    async def _parse(
        client,
        chat_photo: raw.types.UserProfilePhoto | raw.types.ChatPhoto | raw.types.Photo,
        peer_id: int,
        peer_access_hash: int,
    ):
        if not isinstance(
            chat_photo, (raw.types.UserProfilePhoto, raw.types.ChatPhoto, raw.types.Photo)
        ):
            return None

        photo_id = (
            chat_photo.photo_id
            if isinstance(chat_photo, (raw.types.UserProfilePhoto, raw.types.ChatPhoto))
            else chat_photo.id
        )

        small_file_id = FileId(
            file_type=FileType.CHAT_PHOTO,
            dc_id=chat_photo.dc_id,
            media_id=photo_id,
            access_hash=0,
            volume_id=0,
            thumbnail_source=ThumbnailSource.CHAT_PHOTO_SMALL,
            local_id=0,
            chat_id=peer_id,
            chat_access_hash=peer_access_hash,
        )

        big_file_id = FileId(
            file_type=FileType.CHAT_PHOTO,
            dc_id=chat_photo.dc_id,
            media_id=photo_id,
            access_hash=0,
            volume_id=0,
            thumbnail_source=ThumbnailSource.CHAT_PHOTO_BIG,
            local_id=0,
            chat_id=peer_id,
            chat_access_hash=peer_access_hash,
        )

        file_unique_id = FileUniqueId(
            file_unique_type=FileUniqueType.DOCUMENT, media_id=photo_id
        ).encode()

        if isinstance(chat_photo, raw.types.Photo):
            sizes: list[raw.types.PhotoSize] = sorted(
                [size for size in chat_photo.sizes if isinstance(size, raw.types.PhotoSize)],
                key=lambda size: size.w * size.h,
            )

            small_file_id = FileId(
                file_type=FileType.PHOTO,
                dc_id=chat_photo.dc_id,
                media_id=chat_photo.id,
                access_hash=chat_photo.access_hash,
                file_reference=chat_photo.file_reference,
                thumbnail_source=ThumbnailSource.THUMBNAIL,
                thumbnail_file_type=FileType.PHOTO,
                thumbnail_size=sizes[0].type,
                volume_id=0,
                local_id=0,
                chat_id=peer_id,
                chat_access_hash=peer_access_hash,
            )

            big_file_id = FileId(
                file_type=FileType.PHOTO,
                dc_id=chat_photo.dc_id,
                media_id=chat_photo.id,
                access_hash=chat_photo.access_hash,
                file_reference=chat_photo.file_reference,
                thumbnail_source=ThumbnailSource.THUMBNAIL,
                thumbnail_file_type=FileType.PHOTO,
                thumbnail_size=sizes[-1].type,
                volume_id=0,
                local_id=0,
                chat_id=peer_id,
                chat_access_hash=peer_access_hash,
            )

        return ChatPhoto(
            small_file_id=small_file_id.encode(),
            small_photo_unique_id=file_unique_id,
            big_file_id=big_file_id.encode(),
            big_photo_unique_id=file_unique_id,
            added_date=utils.timestamp_to_datetime(getattr(chat_photo, "date", None)),
            animation=await types.AnimatedChatPhoto._parse(client, chat_photo),
            sticker=await types.ChatPhotoSticker._parse(
                client, getattr(chat_photo, "video_sizes", None)
            ),
            client=client,
        )
