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
from pyrogram import enums, raw, types, utils


class EditFolder:
    async def edit_folder(
        self: pyrogram.Client,
        folder_id: int,
        name: str | None = None,
        parse_mode: enums.ParseMode | None = None,
        entities: list[types.MessageEntity] | None = None,
        animate_custom_emoji: bool | None = None,
        icon: str | None = None,
        color: enums.FolderColor | None = None,
        pinned_chats: list[int | str] | None = None,
        included_chats: list[int | str] | None = None,
        excluded_chats: list[int | str] | None = None,
        exclude_muted: bool | None = None,
        exclude_read: bool | None = None,
        exclude_archived: bool | None = None,
        include_contacts: bool | None = None,
        include_non_contacts: bool | None = None,
        include_bots: bool | None = None,
        include_groups: bool | None = None,
        include_channels: bool | None = None,
    ) -> bool:
        """Update chat folder.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            folder_id (``int``):
                Unique chat folder identifier, 2-255.

            name (``str``, *optional*):
                The text of the chat folder name, 1-12 characters without line feeds.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                Special entities like bold, italic, etc. that appear in the folder name.

            animate_custom_emoji (``bool``, *optional*):
                True, if custom emoji in the name must be animated.

            icon (``str``, *optional*):
                The chosen icon for the chat folder.
                Pass None to leave the folder icon as default.

            color (:obj:`~pyrogram.enums.FolderColor`, *optional*)
                Pass :obj:`~pyrogram.enums.FolderColor` to set folder color.
                Can't be changed if folder tags are disabled or the current user doesn't have Telegram Premium subscription.

            is_shareable (``bool``, *optional*):
                True, if at least one link has been created for the folder.

            pinned_chats (List of :obj:`~pyrogram.types.Chat`, *optional*):
                The pinned chats in the folder.
                You can pass an ID (int), username (str) or phone number (str).
                There can be up to getOption("chat_folder_chosen_chat_count_max") pinned and always included non-secret chats and the same number of secret chats, but the limit can be increased with Telegram Premium.

            included_chats (List of :obj:`~pyrogram.types.Chat`, *optional*):
                The always included chats in the folder.
                You can pass an ID (int), username (str) or phone number (str).
                There can be up to getOption("chat_folder_chosen_chat_count_max") pinned and always included non-secret chats and the same number of secret chats, but the limit can be increased with Telegram Premium.

            excluded_chats (List of :obj:`~pyrogram.types.Chat`, *optional*):
                The always excluded chats in the folder.
                You can pass an ID (int), username (str) or phone number (str).
                There can be up to getOption("chat_folder_chosen_chat_count_max") always excluded non-secret chats and the same number of secret chats, but the limit can be increased with Telegram Premium.

            exclude_muted (``bool``, *optional*):
                True, if muted chats need to be excluded.

            exclude_read (``bool``, *optional*):
                True, if read chats need to be excluded.

            exclude_archived (``bool``, *optional*):
                True, if archived chats need to be excluded.

            include_contacts (``bool``, *optional*):
                True, if contacts need to be included.

            include_non_contacts (``bool``, *optional*):
                True, if non-contact users need to be included.

            include_bots (``bool``, *optional*):
                True, if bots need to be included.

            include_groups (``bool``, *optional*):
                True, if basic groups and supergroups need to be included.

            include_channels (``bool``, *optional*):
                True, if channels need to be included.

        Returns:
            ``bool``: True, on success.

        Example:
            .. code-block:: python

                # Update folder
                await app.edit_folder(folder_id, name="New folder title", included_chats=["me"])
        """
        dialog_filters = await self.invoke(raw.functions.messages.GetDialogFilters())

        raw_folders = [
            folder
            for folder in dialog_filters.filters
            if isinstance(folder, (raw.types.DialogFilter, raw.types.DialogFilterChatlist))
        ]

        is_folder_exists = False

        for folder in raw_folders:
            if folder.id == folder_id:
                is_folder_exists = True

        if not is_folder_exists:
            raise ValueError(f"Folder with id {folder_id} not found")

        name, title_entities = (
            await utils.parse_text_entities(self, name, parse_mode, entities)
        ).values()
        title_entities = title_entities or []

        pinned_chats = pinned_chats or []
        included_chats = included_chats or []
        excluded_chats = excluded_chats or []

        r = await self.invoke(
            raw.functions.messages.UpdateDialogFilter(
                id=folder_id,
                filter=raw.types.DialogFilter(
                    id=folder_id,
                    title=raw.types.TextWithEntities(
                        text=name,
                        entities=title_entities,
                    ),
                    pinned_peers=[await self.resolve_peer(peer) for peer in pinned_chats],
                    include_peers=[await self.resolve_peer(peer) for peer in included_chats],
                    exclude_peers=[await self.resolve_peer(peer) for peer in excluded_chats],
                    contacts=include_contacts,
                    non_contacts=include_non_contacts,
                    groups=include_groups,
                    broadcasts=include_channels,
                    bots=include_bots,
                    exclude_muted=exclude_muted,
                    exclude_read=exclude_read,
                    exclude_archived=exclude_archived,
                    title_noanimate=not animate_custom_emoji,
                    emoticon=icon,
                    color=color.value if color else None,
                ),
            )
        )

        return r
