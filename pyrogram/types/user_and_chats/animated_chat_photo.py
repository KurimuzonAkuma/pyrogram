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


class AnimatedChatPhoto(Object):
    """Animated variant of a chat photo in MPEG4 format.

    Parameters:
        length (``int``):
            Animation width and height.

        animation (:obj:`~pyrogram.types.Animation`):
            Animation.

        main_frame_timestamp (``float``, *optional*):
            Timestamp of the frame, used as a static chat photo.
    """

    def __init__(
        self,
        *,
        client: pyrogram.Client | None = None,
        length: int,
        animation: types.Animation,
        main_frame_timestamp: float | None = None,
    ):
        super().__init__(client)

        self.length = length
        self.animation = animation
        self.main_frame_timestamp = main_frame_timestamp

    @staticmethod
    async def _parse(
        client,
        photo: raw.types.Photo
    ):
        if not isinstance(photo, raw.types.Photo):
            return None

        if not photo.video_sizes:
            return None

        video_size = max(
            [v for v in photo.video_sizes if isinstance(v, raw.types.VideoSize)],
            key=lambda v: v.w * v.h,
        )

        return AnimatedChatPhoto(
            length=video_size.w,
            animation=types.Animation(
                file_id=FileId(
                    file_type=FileType.PHOTO,
                    dc_id=photo.dc_id,
                    media_id=photo.id,
                    access_hash=photo.access_hash,
                    file_reference=photo.file_reference,
                    thumbnail_source=ThumbnailSource.THUMBNAIL,
                    thumbnail_file_type=FileType.PHOTO,
                    thumbnail_size=video_size.type,
                    volume_id=0,
                    local_id=0,
                ).encode(),
                file_unique_id=FileUniqueId(
                    file_unique_type=FileUniqueType.DOCUMENT, media_id=photo.id
                ).encode(),
                width=video_size.w,
                height=video_size.h,
                duration=0,
                file_size=video_size.size,
                date=utils.timestamp_to_datetime(photo.date),
                file_name=f"video_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4",
                mime_type="video/mp4",
                client=client,
            ),
            main_frame_timestamp=video_size.video_start_ts,
        )
