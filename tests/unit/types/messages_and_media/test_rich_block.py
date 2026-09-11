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

import json
from typing import Final

import pytest

import pyrogram
from pyrogram import raw, types


_EMPTY_CAPTION: Final[raw.types.PageCaption] = raw.types.PageCaption(
    text=raw.types.TextEmpty(),
    credit=raw.types.TextEmpty(),
)


async def _parse(block: raw.base.PageBlock) -> types.RichBlock:
    return await types.RichBlock._parse(None, block, {}, {}, None, {}, {})


@pytest.mark.parametrize(
    ("compact", "expected"),
    [
        pytest.param(True, True, id="compact"),
        pytest.param(None, None, id="not-compact"),
    ],
)
async def test_a_table_keeps_the_compact_flag_the_schema_carries(
    compact: bool | None,
    *,
    expected: bool | None,
) -> None:
    parsed = await _parse(
        raw.types.PageBlockTable(
            title=raw.types.TextEmpty(),
            rows=[],
            compact=compact,
        )
    )

    assert parsed.is_compact is expected


async def test_a_table_parses_all_attributes_and_flags() -> None:
    parsed = await _parse(
        raw.types.PageBlockTable(
            title=raw.types.TextPlain(text="Table Title"),
            rows=[
                raw.types.PageTableRow(
                    cells=[
                        raw.types.PageTableCell(
                            text=raw.types.TextPlain(text="Cell 1"),
                        )
                    ]
                )
            ],
            bordered=True,
            striped=True,
            compact=True,
        )
    )

    assert parsed.is_bordered is True
    assert parsed.is_striped is True
    assert parsed.is_compact is True
    assert len(parsed.cells) == 1
    assert len(parsed.cells[0]) == 1


def test_rich_block_table_direct_instantiation() -> None:
    table = types.RichBlockTable(
        cells=[],
        is_bordered=True,
        is_striped=False,
        is_compact=True,
    )
    assert table.cells == []
    assert table.is_bordered is True
    assert table.is_striped is False
    assert table.is_compact is True


def test_rich_block_table_defaults() -> None:
    table = types.RichBlockTable(cells=[])
    assert table.cells == []
    assert table.is_bordered is None
    assert table.is_striped is None
    assert table.is_compact is None
    assert table.caption is None


@pytest.mark.parametrize(
    ("bordered", "striped", "compact"),
    [
        (True, False, True),
        (False, True, False),
        (True, True, False),
        (False, False, True),
        (None, None, None),
    ],
)
async def test_a_table_preserves_flag_combinations(
    bordered: bool | None,
    striped: bool | None,
    compact: bool | None,
) -> None:
    parsed = await _parse(
        raw.types.PageBlockTable(
            title=raw.types.TextEmpty(),
            rows=[],
            bordered=bordered,
            striped=striped,
            compact=compact,
        )
    )

    assert parsed.is_bordered is bordered
    assert parsed.is_striped is striped
    assert parsed.is_compact is compact


async def test_a_table_handles_none_rows_and_none_cells() -> None:
    parsed_none_rows = await _parse(
        raw.types.PageBlockTable(
            title=raw.types.TextEmpty(),
            rows=None,
            compact=True,
        )
    )
    assert parsed_none_rows.cells == []
    assert parsed_none_rows.is_compact is True

    parsed_none_cells = await _parse(
        raw.types.PageBlockTable(
            title=raw.types.TextEmpty(),
            rows=[raw.types.PageTableRow(cells=None)],
            compact=True,
        )
    )
    assert parsed_none_cells.cells == []
    assert parsed_none_cells.is_compact is True


async def test_a_table_serializes_with_is_compact() -> None:
    table = types.RichBlockTable(
        cells=[],
        is_bordered=True,
        is_striped=False,
        is_compact=True,
    )

    data = json.loads(str(table))
    assert data["_"] == "RichBlockTable"
    assert data["is_compact"] is True
    assert data["is_bordered"] is True
    assert data["is_striped"] is False
    assert "is_compact=True" in repr(table)


async def test_rich_message_parses_compact_table() -> None:
    raw_rich = raw.types.RichMessage(
        blocks=[
            raw.types.PageBlockTable(
                title=raw.types.TextPlain(text="Compact Stats"),
                rows=[],
                bordered=True,
                compact=True,
            )
        ],
        photos=[],
        documents=[],
    )

    rich_msg = await types.RichMessage._parse(None, raw_rich)
    assert isinstance(rich_msg.blocks, types.List)
    assert len(rich_msg.blocks) == 1
    table = rich_msg.blocks[0]
    assert isinstance(table, types.RichBlockTable)
    assert table.is_compact is True
    assert table.is_bordered is True

    # Test integration with types.List.__repr__ (PR #401)
    list_repr = repr(rich_msg.blocks)
    assert "pyrogram.types.List" in list_repr
    assert "is_compact=True" in list_repr


async def test_message_parses_rich_message_with_compact_table() -> None:
    channel_id = 123456789
    raw_chat = raw.types.Channel(
        id=channel_id,
        title="Test Channel",
        photo=raw.types.ChatPhotoEmpty(),
        date=1755100000,
        usernames=[],
        restriction_reason=[],
    )
    raw_msg = raw.types.Message(
        id=1,
        peer_id=raw.types.PeerChannel(channel_id=channel_id),
        date=1755100000,
        message="",
        entities=[],
        restriction_reason=[],
        rich_message=raw.types.RichMessage(
            blocks=[
                raw.types.PageBlockTable(
                    title=raw.types.TextEmpty(),
                    rows=[],
                    compact=True,
                )
            ],
            photos=[],
            documents=[],
        ),
    )

    cli = pyrogram.Client("test", api_id=1, api_hash="0" * 32, in_memory=True)
    parsed_msg = await types.Message._parse(cli, raw_msg, users={}, chats={channel_id: raw_chat})
    assert parsed_msg.rich_message is not None
    assert isinstance(parsed_msg.rich_message.blocks[0], types.RichBlockTable)
    assert parsed_msg.rich_message.blocks[0].is_compact is True


@pytest.mark.parametrize(
    ("collapsed", "expected"),
    [
        pytest.param(True, types.RichBlockExpandableBlockQuotation, id="collapsed"),
        pytest.param(None, types.RichBlockBlockQuotation, id="not-collapsed"),
    ],
)
async def test_a_blockquote_picks_its_class_from_the_collapsed_flag(
    collapsed: bool | None,
    *,
    expected: type[types.RichBlock],
) -> None:
    parsed = await _parse(
        raw.types.PageBlockBlockquote(
            text=raw.types.TextPlain(text="quote"),
            caption=raw.types.TextPlain(text="credit"),
            collapsed=collapsed,
        )
    )

    assert type(parsed) is expected
    assert parsed.credit == "credit"


async def test_an_expandable_quotation_keeps_its_text_flat() -> None:
    parsed = await _parse(
        raw.types.PageBlockBlockquote(
            text=raw.types.TextPlain(text="quote"),
            caption=raw.types.TextEmpty(),
            collapsed=True,
        )
    )

    assert parsed.text == "quote"


@pytest.mark.parametrize(
    ("flag", "expected"),
    [
        pytest.param("align_left", "left", id="left"),
        pytest.param("align_center", "center", id="center"),
        pytest.param("align_right", "right", id="right"),
        pytest.param(None, None, id="unaligned"),
    ],
)
async def test_a_button_row_reads_its_alignment_off_the_flag_that_is_set(
    flag: str | None,
    *,
    expected: str | None,
) -> None:
    alignment = {flag: True} if flag is not None else {}

    parsed = await _parse(raw.types.PageBlockButtonRow(buttons=[], **alignment))

    assert parsed.align == expected


async def test_a_button_row_parses_every_button_it_carries() -> None:
    parsed = await _parse(
        raw.types.PageBlockButtonRow(
            buttons=[
                raw.types.PageButton(
                    text=raw.types.TextPlain(text="open"),
                    type=raw.types.InlineButtonTypeUrl(url="https://example.com"),
                ),
            ],
        )
    )

    assert isinstance(parsed.buttons, types.List)
    assert [button.text for button in parsed.buttons] == ["open"]
    assert parsed.buttons[0].url == "https://example.com"


async def test_a_button_of_a_type_a_rich_button_cannot_express_keeps_its_text() -> None:
    # `InlineButtonType` holds constructors with no `RichMessageButton` field, and the server
    #  may add more. Parsing one used to fall through and give a `None` back.
    parsed = await _parse(
        raw.types.PageBlockButtonRow(
            buttons=[
                raw.types.PageButton(
                    text=raw.types.TextPlain(text="buy"),
                    type=raw.types.InlineButtonTypeBuy(),
                ),
            ],
        )
    )

    assert parsed.buttons[0].text == "buy"


async def test_a_document_block_parses_the_document_it_points_at() -> None:
    document = raw.types.Document(
        id=555,
        access_hash=666,
        file_reference=b"ref",
        date=0,
        mime_type="application/pdf",
        size=10,
        dc_id=2,
        attributes=[raw.types.DocumentAttributeFilename(file_name="a.pdf")],
    )

    parsed = await types.RichBlock._parse(
        None,
        raw.types.PageBlockDocument(
            document_id=555,
            caption=raw.types.PageCaption(
                text=raw.types.TextPlain(text="caption"),
                credit=raw.types.TextEmpty(),
            ),
        ),
        {},
        {555: document},
        None,
        {},
        {},
    )

    assert parsed.document.file_name == "a.pdf"
    assert parsed.caption.text == "caption"


@pytest.mark.parametrize(
    "block",
    [
        pytest.param(
            raw.types.PageBlockVideo(
                video_id=1,
                caption=_EMPTY_CAPTION,
            ),
            id="video",
        ),
        pytest.param(
            raw.types.PageBlockDocument(
                document_id=1,
                caption=_EMPTY_CAPTION,
            ),
            id="document",
        ),
        pytest.param(
            raw.types.PageBlockAudio(
                audio_id=1,
                caption=_EMPTY_CAPTION,
            ),
            id="audio",
        ),
    ],
)
@pytest.mark.parametrize(
    "documents",
    [
        pytest.param({}, id="absent"),
        pytest.param({1: raw.types.DocumentEmpty(id=1)}, id="empty"),
    ],
)
async def test_a_media_block_without_a_usable_document_is_unsupported(
    block: raw.base.PageBlock,
    *,
    documents: dict[int, raw.base.Document],
) -> None:
    parsed = await types.RichBlock._parse(None, block, {}, documents, None, {}, {})

    # `type()` rather than `==`: `Object.__eq__` iterates `self.__dict__`, so an attribute-less
    #  object compares equal to everything, `None` included.
    assert type(parsed) is types.RichBlockUnsupported


async def test_a_media_block_inside_a_list_item_still_finds_its_document() -> None:
    document = raw.types.Document(
        id=555,
        access_hash=666,
        file_reference=b"ref",
        date=0,
        mime_type="application/pdf",
        size=10,
        dc_id=2,
        attributes=[raw.types.DocumentAttributeFilename(file_name="a.pdf")],
    )

    parsed = await types.RichBlock._parse(
        None,
        raw.types.PageBlockList(
            items=[
                raw.types.PageListItemBlocks(
                    blocks=[
                        raw.types.PageBlockDocument(
                            document_id=555,
                            caption=_EMPTY_CAPTION,
                        )
                    ]
                )
            ]
        ),
        {},
        {555: document},
        None,
        {},
        {},
    )

    assert parsed.items[0].blocks[0].document.file_name == "a.pdf"
