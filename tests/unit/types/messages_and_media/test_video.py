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

from pyrogram import types


def _video() -> "types.Video":
    return types.Video(
        file_id="file-id",
        file_unique_id="file-unique-id",
        width=1,
        height=1,
        codec="h264",
        duration=1,
    )


def test_two_videos_do_not_share_one_alternative_videos_list() -> None:
    first = _video()
    second = _video()

    assert first.alternative_videos is None
    assert second.alternative_videos is None

    first.alternative_videos = [second]

    assert second.alternative_videos is None
