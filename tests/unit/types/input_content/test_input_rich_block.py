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

from typing import Final

import pytest

from pyrogram import raw, types
from pyrogram.file_id import FileId, FileType, ThumbnailSource

_PHOTO_FILE_ID: Final[str] = FileId(
    file_type=FileType.PHOTO,
    dc_id=2,
    media_id=333,
    access_hash=444,
    file_reference=b"ref",
    thumbnail_source=ThumbnailSource.THUMBNAIL,
    thumbnail_file_type=FileType.PHOTO,
    thumbnail_size="x",
    volume_id=0,
    local_id=0,
).encode()

_VOICE_FILE_ID: Final[str] = FileId(
    file_type=FileType.VOICE,
    dc_id=2,
    media_id=111,
    access_hash=222,
    file_reference=b"ref",
).encode()

_AUDIO_FILE_ID: Final[str] = FileId(
    file_type=FileType.AUDIO,
    dc_id=2,
    media_id=555,
    access_hash=666,
    file_reference=b"ref",
).encode()

_DOCUMENT_FILE_ID: Final[str] = FileId(
    file_type=FileType.DOCUMENT,
    dc_id=2,
    media_id=777,
    access_hash=888,
    file_reference=b"ref",
).encode()

_EMPTY_CAPTION: Final[raw.types.PageCaption] = raw.types.PageCaption(
    text=raw.types.TextEmpty(),
    credit=raw.types.TextEmpty(),
)

_TITLE_TEXT: Final[raw.types.TextPlain] = raw.types.TextPlain(text="Title")


async def test_a_paragraph_serializes_its_rich_text() -> None:
    block = types.InputRichBlockParagraph(text=types.RichTextBold(text="hi"))

    result = await block.write(
        client=None,
        photos=[],
        documents=[],
    )

    assert result == raw.types.PageBlockParagraph(
        text=raw.types.TextBold(text=raw.types.TextPlain(text="hi")),
    )


@pytest.mark.parametrize(
    ("size", "expected"),
    [
        pytest.param(1, raw.types.PageBlockHeading1(text=_TITLE_TEXT), id="h1"),
        pytest.param(2, raw.types.PageBlockHeading2(text=_TITLE_TEXT), id="h2"),
        pytest.param(3, raw.types.PageBlockHeading3(text=_TITLE_TEXT), id="h3"),
        pytest.param(4, raw.types.PageBlockHeading4(text=_TITLE_TEXT), id="h4"),
        pytest.param(5, raw.types.PageBlockHeading5(text=_TITLE_TEXT), id="h5"),
        pytest.param(6, raw.types.PageBlockHeading6(text=_TITLE_TEXT), id="h6"),
    ],
)
async def test_a_section_heading_picks_the_constructor_of_its_size(
    size: int,
    *,
    expected: raw.core.TLObject,
) -> None:
    block = types.InputRichBlockSectionHeading(
        text="Title",
        size=size,
    )

    result = await block.write(
        client=None,
        photos=[],
        documents=[],
    )

    assert result == expected


async def test_a_section_heading_rejects_an_out_of_range_size() -> None:
    block = types.InputRichBlockSectionHeading(
        text="Title",
        size=7,
    )

    with pytest.raises(ValueError, match="Invalid section heading size: 7"):
        await block.write(
            client=None,
            photos=[],
            documents=[],
        )


async def test_a_preformatted_block_defaults_its_language_to_an_empty_string() -> None:
    block = types.InputRichBlockPreformatted(text="code")

    result = await block.write(
        client=None,
        photos=[],
        documents=[],
    )

    assert result == raw.types.PageBlockPreformatted(
        text=raw.types.TextPlain(text="code"),
        language="",
    )


async def test_a_list_with_a_typed_item_serializes_as_ordered() -> None:
    block = types.InputRichBlockList(
        items=[
            types.InputRichBlockListItem(
                blocks=[types.InputRichBlockParagraph(text="first")],
                value=3,
                type="i",
            ),
            types.InputRichBlockListItem(
                blocks=[types.InputRichBlockParagraph(text="second")],
            ),
        ],
    )

    result = await block.write(
        client=None,
        photos=[],
        documents=[],
    )

    assert result == raw.types.PageBlockOrderedList(
        items=[
            raw.types.PageListOrderedItemBlocks(
                checkbox=None,
                checked=None,
                blocks=[
                    raw.types.PageBlockParagraph(text=raw.types.TextPlain(text="first")),
                ],
                value=3,
                type="i",
            ),
            raw.types.PageListOrderedItemBlocks(
                checkbox=None,
                checked=None,
                blocks=[
                    raw.types.PageBlockParagraph(text=raw.types.TextPlain(text="second")),
                ],
                value=None,
                type=None,
            ),
        ],
    )


async def test_a_list_without_labels_serializes_as_unordered_with_checkboxes() -> None:
    block = types.InputRichBlockList(
        items=[
            types.InputRichBlockListItem(
                blocks=[types.InputRichBlockParagraph(text="task")],
                has_checkbox=True,
                is_checked=True,
            ),
        ],
    )

    result = await block.write(
        client=None,
        photos=[],
        documents=[],
    )

    assert result == raw.types.PageBlockList(
        items=[
            raw.types.PageListItemBlocks(
                checkbox=True,
                checked=True,
                blocks=[
                    raw.types.PageBlockParagraph(text=raw.types.TextPlain(text="task")),
                ],
            ),
        ],
    )


@pytest.mark.parametrize(
    ("is_compact", "compact"),
    [
        pytest.param(None, None, id="default"),
        pytest.param(True, True, id="compact"),
    ],
)
async def test_a_table_serializes_its_cells_and_flags(
    is_compact: bool | None, compact: bool | None
) -> None:
    block = types.InputRichBlockTable(
        cells=[
            [
                types.RichBlockTableCell(
                    text="header",
                    is_header=True,
                    align="center",
                ),
                types.RichBlockTableCell(),
            ],
        ],
        is_bordered=True,
        is_compact=is_compact,
        caption="totals",
    )

    result = await block.write(
        client=None,
        photos=[],
        documents=[],
    )

    assert result == raw.types.PageBlockTable(
        bordered=True,
        striped=None,
        compact=compact,
        title=raw.types.TextPlain(text="totals"),
        rows=[
            raw.types.PageTableRow(
                cells=[
                    raw.types.PageTableCell(
                        header=True,
                        align_center=True,
                        align_right=False,
                        valign_middle=False,
                        valign_bottom=False,
                        text=raw.types.TextPlain(text="header"),
                        colspan=None,
                        rowspan=None,
                    ),
                    raw.types.PageTableCell(
                        header=None,
                        align_center=False,
                        align_right=False,
                        valign_middle=False,
                        valign_bottom=False,
                        text=None,
                        colspan=None,
                        rowspan=None,
                    ),
                ],
            ),
        ],
    )


async def test_a_map_serializes_its_location_and_defaults() -> None:
    block = types.InputRichBlockMap(
        location=types.Location(
            latitude=50.45,
            longitude=30.52,
        ),
        zoom=12,
    )

    result = await block.write(
        client=None,
        photos=[],
        documents=[],
    )

    assert result == raw.types.InputPageBlockMap(
        geo=raw.types.InputGeoPoint(
            lat=50.45,
            long=30.52,
            accuracy_radius=None,
        ),
        zoom=12,
        w=0,
        h=0,
        caption=_EMPTY_CAPTION,
    )


async def test_a_block_quotation_without_credit_serializes_an_empty_caption() -> None:
    block = types.InputRichBlockBlockQuotation(
        blocks=[types.InputRichBlockParagraph(text="quote")],
    )

    result = await block.write(
        client=None,
        photos=[],
        documents=[],
    )

    assert result == raw.types.PageBlockBlockquoteBlocks(
        blocks=[
            raw.types.PageBlockParagraph(text=raw.types.TextPlain(text="quote")),
        ],
        caption=raw.types.TextEmpty(),
    )


async def test_a_photo_block_from_a_file_id_collects_its_input_photo() -> None:
    photos: list[raw.base.InputPhoto] = []
    block = types.InputRichBlockPhoto(photo=types.InputMediaPhoto(_PHOTO_FILE_ID))

    result = await block.write(
        client=None,
        photos=photos,
        documents=[],
    )

    assert result == raw.types.PageBlockPhoto(
        spoiler=None,
        photo_id=333,
        caption=_EMPTY_CAPTION,
        url=None,
        webpage_id=None,
    )
    assert photos == [
        raw.types.InputPhoto(
            id=333,
            access_hash=444,
            file_reference=b"ref",
        ),
    ]


async def test_a_voice_note_block_from_a_file_id_serializes_as_a_video_block() -> None:
    documents: list[raw.base.InputDocument] = []
    block = types.InputRichBlockVoiceNote(voice_note=types.InputMediaVoiceNote(_VOICE_FILE_ID))

    result = await block.write(
        client=None,
        photos=[],
        documents=documents,
    )

    assert result == raw.types.PageBlockVideo(
        autoplay=None,
        loop=None,
        spoiler=None,
        video_id=111,
        caption=_EMPTY_CAPTION,
    )
    assert documents == [
        raw.types.InputDocument(
            id=111,
            access_hash=222,
            file_reference=b"ref",
        ),
    ]


async def test_an_audio_block_from_a_file_id_collects_its_input_document() -> None:
    documents: list[raw.base.InputDocument] = []
    block = types.InputRichBlockAudio(audio=types.InputMediaAudio(_AUDIO_FILE_ID))

    result = await block.write(
        client=None,
        photos=[],
        documents=documents,
    )

    assert result == raw.types.PageBlockAudio(
        audio_id=555,
        caption=_EMPTY_CAPTION,
    )
    assert documents == [
        raw.types.InputDocument(
            id=555,
            access_hash=666,
            file_reference=b"ref",
        ),
    ]


async def test_an_expandable_quotation_serializes_as_a_collapsed_blockquote() -> None:
    block = types.InputRichBlockExpandableBlockQuotation(
        text=types.RichTextBold(text="quote"),
        credit=types.RichTextItalic(text="credit"),
    )

    result = await block.write(
        client=None,
        photos=[],
        documents=[],
    )

    assert result == raw.types.PageBlockBlockquote(
        text=raw.types.TextBold(text=raw.types.TextPlain(text="quote")),
        caption=raw.types.TextItalic(text=raw.types.TextPlain(text="credit")),
        collapsed=True,
    )


@pytest.mark.parametrize(
    ("align", "expected"),
    [
        pytest.param("left", (True, False, False), id="left"),
        pytest.param("center", (False, True, False), id="center"),
        pytest.param("right", (False, False, True), id="right"),
        pytest.param(None, (False, False, False), id="unaligned"),
    ],
)
async def test_a_buttons_block_sets_the_alignment_flag_its_name_picks(
    align: str | None,
    *,
    expected: tuple[bool, bool, bool],
) -> None:
    block = types.InputRichBlockButtons(
        buttons=[],
        align=align,
    )

    result = await block.write(
        client=None,
        photos=[],
        documents=[],
    )

    assert (result.align_left, result.align_center, result.align_right) == expected


async def test_a_buttons_block_serializes_its_buttons_as_page_buttons() -> None:
    block = types.InputRichBlockButtons(
        buttons=[
            types.RichMessageButton(
                text="open",
                url="https://example.com",
            ),
        ],
    )

    result = await block.write(
        client=None,
        photos=[],
        documents=[],
    )

    assert result.buttons == [
        raw.types.PageButton(
            text=raw.types.TextPlain(text="open"),
            type=raw.types.InlineButtonTypeUrl(url="https://example.com"),
            style=None,
        ),
    ]


async def test_a_document_block_from_a_file_id_collects_its_input_document() -> None:
    documents: list[raw.base.InputDocument] = []
    block = types.InputRichBlockDocument(document=types.InputMediaDocument(_DOCUMENT_FILE_ID))

    result = await block.write(
        client=None,
        photos=[],
        documents=documents,
    )

    assert result == raw.types.PageBlockDocument(
        document_id=777,
        caption=_EMPTY_CAPTION,
    )
    assert documents == [
        raw.types.InputDocument(
            id=777,
            access_hash=888,
            file_reference=b"ref",
        ),
    ]
