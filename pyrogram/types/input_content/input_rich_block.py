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


async def _write_caption(
    client: pyrogram.Client,
    *,
    caption: types.RichBlockCaption | None,
) -> raw.types.PageCaption:
    if caption is None:
        return raw.types.PageCaption(
            text=raw.types.TextEmpty(),
            credit=raw.types.TextEmpty(),
        )

    return await caption.write(client)


async def _get_input_photo(
    client: pyrogram.Client,
    *,
    chat_id: int | str | None,
    input_media: raw.base.InputMedia,
) -> raw.types.InputPhoto:
    if isinstance(input_media, raw.types.InputMediaPhoto):
        return input_media.id

    # An external photo has no id yet: the server assigns one when it fetches the URL.
    if chat_id is None:
        peer = raw.types.InputPeerSelf()
    else:
        peer = await client.resolve_peer(chat_id)

    uploaded_media = await client.invoke(
        raw.functions.messages.UploadMedia(
            peer=peer,
            media=input_media,
        ),
    )

    return raw.types.InputPhoto(
        id=uploaded_media.photo.id,
        access_hash=uploaded_media.photo.access_hash,
        file_reference=uploaded_media.photo.file_reference,
    )


async def _get_input_document(
    client: pyrogram.Client,
    *,
    chat_id: int | str | None,
    input_media: raw.base.InputMedia,
) -> raw.types.InputDocument:
    if isinstance(input_media, raw.types.InputMediaDocument):
        return input_media.id

    # External documents take the same upload round-trip as photos: see `_get_input_photo`.
    if chat_id is None:
        peer = raw.types.InputPeerSelf()
    else:
        peer = await client.resolve_peer(chat_id)

    uploaded_media = await client.invoke(
        raw.functions.messages.UploadMedia(
            peer=peer,
            media=input_media,
        ),
    )

    return raw.types.InputDocument(
        id=uploaded_media.document.id,
        access_hash=uploaded_media.document.access_hash,
        file_reference=uploaded_media.document.file_reference,
    )


class InputRichBlock(Object):
    """This object represents a block of a rich formatted message to be sent.

    It can be one of:

    - :obj:`~pyrogram.types.InputRichBlockListItem`
    - :obj:`~pyrogram.types.InputRichBlockParagraph`
    - :obj:`~pyrogram.types.InputRichBlockSectionHeading`
    - :obj:`~pyrogram.types.InputRichBlockPreformatted`
    - :obj:`~pyrogram.types.InputRichBlockFooter`
    - :obj:`~pyrogram.types.InputRichBlockDivider`
    - :obj:`~pyrogram.types.InputRichBlockMathematicalExpression`
    - :obj:`~pyrogram.types.InputRichBlockAnchor`
    - :obj:`~pyrogram.types.InputRichBlockList`
    - :obj:`~pyrogram.types.InputRichBlockBlockQuotation`
    - :obj:`~pyrogram.types.InputRichBlockPullQuotation`
    - :obj:`~pyrogram.types.InputRichBlockCollage`
    - :obj:`~pyrogram.types.InputRichBlockSlideshow`
    - :obj:`~pyrogram.types.InputRichBlockTable`
    - :obj:`~pyrogram.types.InputRichBlockDetails`
    - :obj:`~pyrogram.types.InputRichBlockMap`
    - :obj:`~pyrogram.types.InputRichBlockAnimation`
    - :obj:`~pyrogram.types.InputRichBlockAudio`
    - :obj:`~pyrogram.types.InputRichBlockPhoto`
    - :obj:`~pyrogram.types.InputRichBlockVideo`
    - :obj:`~pyrogram.types.InputRichBlockVoiceNote`
    - :obj:`~pyrogram.types.InputRichBlockThinking`
    """

    def __init__(self) -> None:
        super().__init__()

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        raise NotImplementedError


class InputRichBlockListItem(InputRichBlock):
    """An item of a list to be sent.

    Parameters:
        blocks (List of :obj:`~pyrogram.types.InputRichBlock`):
            The content of the item.

        has_checkbox (``bool``, *optional*):
            Pass True if the item has a checkbox.

        is_checked (``bool``, *optional*):
            Pass True if the item has a checked checkbox.

        value (``int``, *optional*):
            For ordered lists, the numeric value of the item label.

        type (``str``, *optional*):
            For ordered lists, the type of the item label.
            Must be one of "a" for lowercase letters, "A" for uppercase letters,
            "i" for lowercase Roman numerals, "I" for uppercase Roman numerals,
            or "1" for decimal numbers.
    """

    def __init__(
        self,
        blocks: list[types.InputRichBlock],
        has_checkbox: bool | None = None,
        is_checked: bool | None = None,
        value: int | None = None,
        type: str | None = None,
    ) -> None:
        super().__init__()

        self.blocks = blocks
        self.has_checkbox = has_checkbox
        self.is_checked = is_checked
        self.value = value
        self.type = type

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
        ordered: bool,
    ) -> raw.base.PageListItem | raw.base.PageListOrderedItem:
        blocks = [
            await block.write(
                client=client,
                chat_id=chat_id,
                photos=photos,
                documents=documents,
            )
            for block in self.blocks
        ]

        if ordered:
            return raw.types.PageListOrderedItemBlocks(
                checkbox=self.has_checkbox,
                checked=self.is_checked,
                blocks=blocks,
                value=self.value,
                type=self.type,
            )

        return raw.types.PageListItemBlocks(
            checkbox=self.has_checkbox,
            checked=self.is_checked,
            blocks=blocks,
        )


class InputRichBlockParagraph(InputRichBlock):
    """A text paragraph, corresponding to the HTML tag ``<p>``.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Text of the block.
    """

    def __init__(
        self,
        text: types.RichText,
    ) -> None:
        super().__init__()

        self.text = text

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        return raw.types.PageBlockParagraph(text=await types.RichText._write(client, self.text))


class InputRichBlockSectionHeading(InputRichBlock):
    """A section heading, corresponding to the HTML tags ``<h1>``, ``<h2>``, ``<h3>``, ``<h4>``, ``<h5>``, or ``<h6>``.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Text of the block.

        size (``int``):
            Relative size of the text font, 1-6.
            1 is the largest, 6 is the smallest.
    """

    def __init__(
        self,
        text: types.RichText,
        size: int,
    ) -> None:
        super().__init__()

        self.text = text
        self.size = size

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        text = await types.RichText._write(client, self.text)

        if self.size == 1:
            return raw.types.PageBlockHeading1(text=text)

        if self.size == 2:
            return raw.types.PageBlockHeading2(text=text)

        if self.size == 3:
            return raw.types.PageBlockHeading3(text=text)

        if self.size == 4:
            return raw.types.PageBlockHeading4(text=text)

        if self.size == 5:
            return raw.types.PageBlockHeading5(text=text)

        if self.size == 6:
            return raw.types.PageBlockHeading6(text=text)

        raise ValueError(f"Invalid section heading size: {self.size}")


class InputRichBlockPreformatted(InputRichBlock):
    """A preformatted text block, corresponding to the nested HTML tags ``<pre>`` and ``<code>``.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Text of the block.

        language (``str``, *optional*):
            The programming language of the text.
    """

    def __init__(
        self,
        text: types.RichText,
        language: str | None = None,
    ) -> None:
        super().__init__()

        self.text = text
        self.language = language

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        return raw.types.PageBlockPreformatted(
            text=await types.RichText._write(client, self.text),
            language=self.language or "",
        )


class InputRichBlockFooter(InputRichBlock):
    """A footer, corresponding to the HTML tag ``<footer>``.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Text of the block.
    """

    def __init__(self, text: types.RichText) -> None:
        super().__init__()

        self.text = text

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        return raw.types.PageBlockFooter(text=await types.RichText._write(client, self.text))


class InputRichBlockDivider(InputRichBlock):
    """A divider, corresponding to the HTML tag ``<hr/>``."""

    def __init__(self) -> None:
        super().__init__()

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        return raw.types.PageBlockDivider()


class InputRichBlockMathematicalExpression(InputRichBlock):
    """A block with a mathematical expression in LaTeX format, corresponding to the custom HTML tag ``<tg-math-block>``.

    Parameters:
        expression (``str``):
            The mathematical expression in LaTeX format.
    """

    def __init__(self, expression: str) -> None:
        super().__init__()

        self.expression = expression

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        return raw.types.PageBlockMath(source=self.expression)


class InputRichBlockAnchor(InputRichBlock):
    """A block with an anchor, corresponding to the HTML tag ``<a>`` with the attribute ``name``.

    Parameters:
        name (``str``):
            The name of the anchor.
    """

    def __init__(self, name: str) -> None:
        super().__init__()

        self.name = name

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        return raw.types.PageBlockAnchor(name=self.name)


class InputRichBlockList(InputRichBlock):
    """A list of blocks, corresponding to the HTML tag ``<ul>`` or ``<ol>`` with multiple nested tags ``<li>``.

    The list is sent as ordered when any of its items carries *value* or *type*.

    Parameters:
        items (List of :obj:`~pyrogram.types.InputRichBlockListItem`):
            Items of the list.
    """

    def __init__(self, items: list[types.InputRichBlockListItem]) -> None:
        super().__init__()

        self.items = items

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        ordered: bool = any(item.value is not None or item.type is not None for item in self.items)

        items = [
            await item.write(
                client=client,
                chat_id=chat_id,
                photos=photos,
                documents=documents,
                ordered=ordered,
            )
            for item in self.items
        ]

        if ordered:
            return raw.types.PageBlockOrderedList(items=items)

        return raw.types.PageBlockList(items=items)


class InputRichBlockBlockQuotation(InputRichBlock):
    """A block quotation, corresponding to the HTML tag ``<blockquote>``.

    Parameters:
        blocks (List of :obj:`~pyrogram.types.InputRichBlock`):
            Content of the block.

        credit (:obj:`~pyrogram.types.RichText`, *optional*):
            Credit of the block.
    """

    def __init__(
        self,
        blocks: list[types.InputRichBlock],
        credit: types.RichText | None = None,
    ) -> None:
        super().__init__()

        self.blocks = blocks
        self.credit = credit

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        blocks = [
            await block.write(
                client=client,
                chat_id=chat_id,
                photos=photos,
                documents=documents,
            )
            for block in self.blocks
        ]

        return raw.types.PageBlockBlockquoteBlocks(
            blocks=blocks,
            caption=await types.RichText._write(client, self.credit),
        )


class InputRichBlockPullQuotation(InputRichBlock):
    """A quotation with centered text, loosely corresponding to the HTML tag ``<aside>``.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Text of the block.

        credit (:obj:`~pyrogram.types.RichText`, *optional*):
            Credit of the block.
    """

    def __init__(
        self,
        text: types.RichText,
        credit: types.RichText | None = None,
    ) -> None:
        super().__init__()

        self.text = text
        self.credit = credit

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        return raw.types.PageBlockPullquote(
            text=await types.RichText._write(client, self.text),
            caption=await types.RichText._write(client, self.credit),
        )


class InputRichBlockCollage(InputRichBlock):
    """A collage, corresponding to the custom HTML tag ``<tg-collage>``.

    Parameters:
        blocks (List of :obj:`~pyrogram.types.InputRichBlock`):
            Elements of the collage.

        caption (:obj:`~pyrogram.types.RichBlockCaption`, *optional*):
            Caption of the block.
    """

    def __init__(
        self,
        blocks: list[types.InputRichBlock],
        caption: types.RichBlockCaption | None = None,
    ) -> None:
        super().__init__()

        self.blocks = blocks
        self.caption = caption

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        items = [
            await block.write(
                client=client,
                chat_id=chat_id,
                photos=photos,
                documents=documents,
            )
            for block in self.blocks
        ]

        return raw.types.PageBlockCollage(
            items=items,
            caption=await _write_caption(client, caption=self.caption),
        )


class InputRichBlockSlideshow(InputRichBlock):
    """A slideshow, corresponding to the custom HTML tag ``<tg-slideshow>``.

    Parameters:
        blocks (List of :obj:`~pyrogram.types.InputRichBlock`):
            Elements of the slideshow.

        caption (:obj:`~pyrogram.types.RichBlockCaption`, *optional*):
            Caption of the block.
    """

    def __init__(
        self,
        blocks: list[types.InputRichBlock],
        caption: types.RichBlockCaption | None = None,
    ) -> None:
        super().__init__()

        self.blocks = blocks
        self.caption = caption

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        items = [
            await block.write(
                client=client,
                chat_id=chat_id,
                photos=photos,
                documents=documents,
            )
            for block in self.blocks
        ]

        return raw.types.PageBlockSlideshow(
            items=items,
            caption=await _write_caption(client, caption=self.caption),
        )


class InputRichBlockTable(InputRichBlock):
    """A table, corresponding to the HTML tag ``<table>``.

    Parameters:
        cells (List of List of :obj:`~pyrogram.types.RichBlockTableCell`):
            Cells of the table.

        is_bordered (``bool``, *optional*):
            Pass True if the table has borders.

        is_striped (``bool``, *optional*):
            Pass True if the table is striped.

        caption (:obj:`~pyrogram.types.RichText`, *optional*):
            Caption of the table.
    """

    def __init__(
        self,
        cells: list[list[types.RichBlockTableCell]],
        is_bordered: bool | None = None,
        is_striped: bool | None = None,
        caption: types.RichText | None = None,
    ) -> None:
        super().__init__()

        self.cells = cells
        self.is_bordered = is_bordered
        self.is_striped = is_striped
        self.caption = caption

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        rows: list[raw.types.PageTableRow] = []

        for row in self.cells:
            row_cells = [await cell.write(client) for cell in row]
            rows.append(raw.types.PageTableRow(cells=row_cells))

        return raw.types.PageBlockTable(
            bordered=self.is_bordered,
            striped=self.is_striped,
            title=await types.RichText._write(client, self.caption),
            rows=rows,
        )


class InputRichBlockDetails(InputRichBlock):
    """An expandable block for details disclosure, corresponding to the HTML tag ``<details>``.

    Parameters:
        summary (:obj:`~pyrogram.types.RichText`):
            Always shown summary of the block.

        blocks (List of :obj:`~pyrogram.types.InputRichBlock`):
            Content of the block.

        is_open (``bool``, *optional*):
            Pass True if the content of the block is visible by default.
    """

    def __init__(
        self,
        summary: types.RichText,
        blocks: list[types.InputRichBlock],
        is_open: bool | None = None,
    ) -> None:
        super().__init__()

        self.summary = summary
        self.blocks = blocks
        self.is_open = is_open

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        blocks = [
            await block.write(
                client=client,
                chat_id=chat_id,
                photos=photos,
                documents=documents,
            )
            for block in self.blocks
        ]

        return raw.types.PageBlockDetails(
            open=self.is_open,
            blocks=blocks,
            title=await types.RichText._write(client, self.summary),
        )


class InputRichBlockMap(InputRichBlock):
    """A block with a map, corresponding to the custom HTML tag ``<tg-map>``.

    The map's width and height must not exceed 10000 in total.
    The width and height ratio must be at most 20.

    Parameters:
        location (:obj:`~pyrogram.types.Location`):
            Location of the center of the map.

        zoom (``int``, *optional*):
            Map zoom level, 0-24.

        width (``int``, *optional*):
            Map width, 0-10000.

        height (``int``, *optional*):
            Map height, 0-10000.

        caption (:obj:`~pyrogram.types.RichBlockCaption`, *optional*):
            Caption of the block.
    """

    def __init__(
        self,
        location: types.Location,
        zoom: int | None = None,
        width: int | None = None,
        height: int | None = None,
        caption: types.RichBlockCaption | None = None,
    ) -> None:
        super().__init__()

        self.location = location
        self.zoom = zoom
        self.width = width
        self.height = height
        self.caption = caption

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        return raw.types.InputPageBlockMap(
            geo=raw.types.InputGeoPoint(
                lat=self.location.latitude,
                long=self.location.longitude,
                accuracy_radius=self.location.accuracy_radius,
            ),
            zoom=self.zoom or 0,
            w=self.width or 0,
            h=self.height or 0,
            caption=await _write_caption(client, caption=self.caption),
        )


class InputRichBlockAnimation(InputRichBlock):
    """A block with an animation, corresponding to the HTML tag ``<video>``.

    Parameters:
        animation (:obj:`~pyrogram.types.InputMediaAnimation`):
            The animation. Caption is ignored.

        caption (:obj:`~pyrogram.types.RichBlockCaption`, *optional*):
            Caption of the block.
    """

    def __init__(
        self,
        animation: types.InputMediaAnimation,
        caption: types.RichBlockCaption | None = None,
    ) -> None:
        super().__init__()

        self.animation = animation
        self.caption = caption

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        input_media = await self.animation.write(
            client=client,
            chat_id=chat_id,
        )

        input_document = await _get_input_document(
            client,
            chat_id=chat_id,
            input_media=input_media,
        )
        documents.append(input_document)

        return raw.types.PageBlockVideo(
            video_id=input_document.id,
            caption=await _write_caption(client, caption=self.caption),
        )


class InputRichBlockAudio(InputRichBlock):
    """A block with a music file, corresponding to the HTML tag ``<audio>``.

    Parameters:
        audio (:obj:`~pyrogram.types.InputMediaAudio`):
            The audio. Caption is ignored.

        caption (:obj:`~pyrogram.types.RichBlockCaption`, *optional*):
            Caption of the block.
    """

    def __init__(
        self,
        audio: types.InputMediaAudio,
        caption: types.RichBlockCaption | None = None,
    ) -> None:
        super().__init__()

        self.audio = audio
        self.caption = caption

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        input_media = await self.audio.write(
            client=client,
            chat_id=chat_id,
        )

        input_document = await _get_input_document(
            client,
            chat_id=chat_id,
            input_media=input_media,
        )
        documents.append(input_document)

        return raw.types.PageBlockAudio(
            audio_id=input_document.id,
            caption=await _write_caption(client, caption=self.caption),
        )


class InputRichBlockPhoto(InputRichBlock):
    """A block with a photo, corresponding to the HTML tag ``<img>``.

    Parameters:
        photo (:obj:`~pyrogram.types.InputMediaPhoto`):
            The photo. Caption is ignored.

        caption (:obj:`~pyrogram.types.RichBlockCaption`, *optional*):
            Caption of the block.
    """

    def __init__(
        self,
        photo: types.InputMediaPhoto,
        caption: types.RichBlockCaption | None = None,
    ) -> None:
        super().__init__()

        self.photo = photo
        self.caption = caption

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        input_media = await self.photo.write(
            client=client,
            chat_id=chat_id,
        )

        input_photo = await _get_input_photo(
            client,
            chat_id=chat_id,
            input_media=input_media,
        )
        photos.append(input_photo)

        return raw.types.PageBlockPhoto(
            photo_id=input_photo.id,
            caption=await _write_caption(client, caption=self.caption),
        )


class InputRichBlockVideo(InputRichBlock):
    """A block with a video, corresponding to the HTML tag ``<video>``.

    Parameters:
        video (:obj:`~pyrogram.types.InputMediaVideo`):
            The video. Caption is ignored.

        caption (:obj:`~pyrogram.types.RichBlockCaption`, *optional*):
            Caption of the block.
    """

    def __init__(
        self,
        video: types.InputMediaVideo,
        caption: types.RichBlockCaption | None = None,
    ) -> None:
        super().__init__()

        self.video = video
        self.caption = caption

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        input_media = await self.video.write(
            client=client,
            chat_id=chat_id,
        )

        input_document = await _get_input_document(
            client,
            chat_id=chat_id,
            input_media=input_media,
        )
        documents.append(input_document)

        return raw.types.PageBlockVideo(
            video_id=input_document.id,
            caption=await _write_caption(client, caption=self.caption),
        )


class InputRichBlockVoiceNote(InputRichBlock):
    """A block with a voice note, corresponding to the HTML tag ``<audio>``.

    Parameters:
        voice_note (:obj:`~pyrogram.types.InputMediaVoiceNote`):
            The voice note. Caption is ignored.

        caption (:obj:`~pyrogram.types.RichBlockCaption`, *optional*):
            Caption of the block.
    """

    def __init__(
        self,
        voice_note: types.InputMediaVoiceNote,
        caption: types.RichBlockCaption | None = None,
    ) -> None:
        super().__init__()

        self.voice_note = voice_note
        self.caption = caption

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        input_media = await self.voice_note.write(
            client=client,
            chat_id=chat_id,
        )

        input_document = await _get_input_document(
            client,
            chat_id=chat_id,
            input_media=input_media,
        )
        documents.append(input_document)

        # A voice note travels as `pageBlockVideo`: that is the constructor the server uses
        #  for voice documents in rich messages, and the one `RichBlock._parse` reads them from.
        return raw.types.PageBlockVideo(
            video_id=input_document.id,
            caption=await _write_caption(client, caption=self.caption),
        )


class InputRichBlockThinking(InputRichBlock):
    """A block with a "Thinking..." placeholder, corresponding to the custom HTML tag ``<tg-thinking>``.
    The block may be used only in :meth:`~pyrogram.Client.send_rich_message_draft`, therefore it can't be received in messages.
    See https://t.me/addemoji/AIActions for examples of custom emoji, which are recommended for usage in the block.

    Parameters:
        text (:obj:`~pyrogram.types.RichText`):
            Text of the block.
            See https://t.me/addemoji/AIActions for examples of custom emoji, which are recommended for usage in the block.
    """

    def __init__(
        self,
        text: types.RichText,
    ) -> None:
        super().__init__()

        self.text = text

    async def write(
        self,
        *,
        client: pyrogram.Client,
        chat_id: int | str | None = None,
        photos: list[raw.base.InputPhoto],
        documents: list[raw.base.InputDocument],
    ) -> raw.base.PageBlock:
        return raw.types.PageBlockThinking(text=await types.RichText._write(client, self.text))
