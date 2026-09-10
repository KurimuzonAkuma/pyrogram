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

import re
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Protocol
from collections.abc import Callable

import pytest

from pyrogram import raw, types

# `write()` only ever touches `client` through `client.resolve_peer(chat_id)`, and that
#  call is skipped whenever `chat_id` stays at its default `None` (see e.g.
#  `InputMediaPhoto.write`). Every case below raises before reaching any other use of
#  `client`, so passing `None` for it - already how tests/unit/types/input_content/
#  test_input_rich_message.py exercises `write()` - keeps these tests mock-free.
_MEDIA_FACTORIES = [
    pytest.param(types.InputMediaPhoto, id="photo"),
    pytest.param(types.InputMediaAnimation, id="animation"),
    pytest.param(types.InputMediaAudio, id="audio"),
    pytest.param(types.InputMediaDocument, id="document"),
    pytest.param(types.InputMediaSticker, id="sticker"),
    pytest.param(types.InputMediaVoiceNote, id="voice-note"),
    pytest.param(types.InputMediaVideo, id="video"),
    pytest.param(
        lambda media: types.InputMediaLivePhoto(media, photo="file_id_placeholder"),
        id="live-photo",
    ),
]


class _MediaFactory(Protocol):
    def __call__(self, media: Path, /) -> types.InputMedia: ...


class _UploadReached(Exception):
    """Stops `write()` as soon as it hands the media over to be uploaded."""


class _RecordingClient:
    """Records what `write()` passes to `save_file`, then stops the upload.

    `guess_mime_type` answers None so every caller falls back to its own default; these
    tests are about which branch `write()` takes, not about mime detection.
    """

    def __init__(self) -> None:
        self.saved: list[str | Path | BinaryIO] = []

    def guess_mime_type(self, filename: str | Path | BinaryIO) -> str | None:
        return None

    # Python resolves this attribute before it evaluates the query being passed to it,
    #  so it has to exist even though `save_file` raises while that query is still
    #  being built.
    async def invoke(self, query: raw.core.TLObject) -> raw.core.TLObject:
        raise AssertionError("`save_file` was expected to stop the upload first")

    async def save_file(
        self,
        path: str | Path | BinaryIO,
        *,
        progress: Callable | None = None,
        progress_args: tuple = (),
    ) -> raw.base.InputFile:
        self.saved.append(path)

        raise _UploadReached


@pytest.mark.parametrize("factory", _MEDIA_FACTORIES)
async def test_write_raises_for_a_media_path_that_does_not_exist(
    tmp_path: Path,
    factory: _MediaFactory,
) -> None:
    missing = tmp_path / "missing.jpg"

    with pytest.raises(FileNotFoundError, match=re.escape(str(missing))):
        await factory(missing).write(client=None)


async def test_live_photo_write_raises_for_a_photo_path_that_does_not_exist(
    tmp_path: Path,
) -> None:
    # `media` has to survive its own is-a-local-file check to reach the `photo` guard,
    #  so it is a string that is neither an existing path nor a URL - a bare file_id
    #  shape is enough since `write()` never gets far enough to decode it.
    missing = tmp_path / "missing.jpg"
    media = types.InputMediaLivePhoto("not-a-local-path", photo=missing)

    with pytest.raises(FileNotFoundError, match=re.escape(str(missing))):
        await media.write(client=None)


async def test_video_write_raises_for_a_video_cover_path_that_does_not_exist(
    tmp_path: Path,
) -> None:
    # Regression test for the video_cover guard having been placed after the
    #  `re.match("^https?://", ...)` URL check instead of before it: a non-existent
    #  `Path` reached `re.match()` there and raised `TypeError` instead of this.
    missing = tmp_path / "cover.jpg"
    media = types.InputMediaVideo("not-a-local-path", video_cover=missing)

    with pytest.raises(FileNotFoundError, match=re.escape(str(missing))):
        await media.write(client=None)


async def test_write_raises_for_a_path_like_that_is_not_a_pathlib_path(tmp_path: Path) -> None:
    # `save_file` opens anything `os.PathLike`, so the dispatch has to recognise the same
    #  set. Narrowing on `pathlib.Path` alone let a `PurePath` fall through to
    #  `re.match()`, which raised `TypeError: expected string or bytes-like object, got
    #  'PurePosixPath'` instead of naming the missing file.
    missing = PurePosixPath(tmp_path / "missing.jpg")

    with pytest.raises(FileNotFoundError, match=re.escape(str(missing))):
        await types.InputMediaPhoto(missing).write(client=None)


async def test_live_photo_write_rejects_a_local_photo_next_to_a_remote_media(
    tmp_path: Path,
) -> None:
    # The guard used to check only the TYPE of `photo`, so an existing file was reported
    #  as `No such file or directory`. What is actually wrong is the mix: the call this
    #  falls through to addresses both `media` and `photo` by file_id.
    existing = tmp_path / "photo.jpg"
    existing.write_bytes(b"payload")
    media = types.InputMediaLivePhoto("not-a-local-path", photo=existing)

    with pytest.raises(ValueError, match="both be local files or both be file_ids"):
        await media.write(client=None)


@pytest.mark.parametrize("factory", _MEDIA_FACTORIES)
async def test_write_uploads_a_media_path_that_exists(
    tmp_path: Path,
    factory: _MediaFactory,
) -> None:
    existing = tmp_path / "media.bin"
    existing.write_bytes(b"payload")
    client = _RecordingClient()

    with pytest.raises(_UploadReached):
        await factory(existing).write(client=client)

    assert client.saved == [existing]
