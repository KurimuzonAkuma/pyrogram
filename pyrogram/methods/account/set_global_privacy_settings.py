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


class SetGlobalPrivacySettings:
    async def set_global_privacy_settings(
        self: pyrogram.Client,
        archive_and_mute_new_chats: bool | None = None,
        keep_unmuted_chats_archived: bool | None = None,
        keep_chats_from_folders_archived: bool | None = None,
        show_read_date: bool | None = None,
        allow_new_chats_from_unknown_users: bool | None = None,
        incoming_paid_message_star_count: int | None = None,
        show_gift_button: bool | None = None,
        accepted_gift_types: types.AcceptedGiftTypes | None = None,
    ) -> types.GlobalPrivacySettings:
        """Set account global privacy settings.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            archive_and_mute_new_chats (``bool``, *optional*):
                Whether to archive and mute new chats from non-contacts,

            keep_unmuted_chats_archived (``bool``, *optional*):
                Whether unmuted chats will be kept in
                the Archive chat list when they get a new message.

            keep_chats_from_folders_archived (``bool``, *optional*):
                Whether unmuted chats, that are always included or pinned
                in a folder, will be kept in the Archive chat list when they get
                a new message. Ignored if keep_unmuted_chats_archived is set.

            show_read_date (``bool``, *optional*):
                True, if message read date is shown to other users in private chats.
                If false and the current user isn't a Telegram Premium user,
                then they will not be able to see other's message read date.

            allow_new_chats_from_unknown_users (``bool``, *optional*):
                True, if non-contacts users are able to write first to the current user.
                Telegram Premium subscribers are able to write first regardless of this setting.

            incoming_paid_message_star_count (``int``, *optional*):
                Number of Telegram Stars that must be paid for every incoming private message
                by non-contacts.
                Must be between 0-``paid_message_star_count_max``.
                If positive, then allow_new_chats_from_unknown_users must be true.
                The current user will receive ``paid_message_earnings_per_mille`` Telegram Stars
                for each 1000 Telegram Stars paid for message sending.

            show_gift_button (``bool``, *optional*):
                True, if a button for sending a gift to the user or by the user must be always shown in the input field.

            accepted_gift_types (:obj:`~pyrogram.types.AcceptedGiftTypes`, *optional*):
                Information about gifts that can be received by the user.

        Returns:
            :obj:`~pyrogram.types.GlobalPrivacySettings`: On success, the new global privacy settings is returned.

        Example:
            .. code-block:: python

                # Archive new chats
                await app.set_global_privacy_settings(
                    archive_and_mute_new_chats=True
                )

                # Set price for incoming messages
                await app.set_global_privacy_settings(
                    incoming_paid_message_star_count=10
                )
        """
        settings = await self.invoke(raw.functions.account.GetGlobalPrivacySettings())

        if archive_and_mute_new_chats is not None:
            settings.archive_and_mute_new_noncontact_peers = archive_and_mute_new_chats

        if keep_unmuted_chats_archived is not None:
            settings.keep_archived_unmuted = keep_unmuted_chats_archived

        if keep_chats_from_folders_archived is not None:
            settings.keep_archived_folders = keep_chats_from_folders_archived

        if show_read_date is not None:
            settings.hide_read_marks = show_read_date

        if allow_new_chats_from_unknown_users is not None:
            settings.new_noncontact_peers_require_premium = allow_new_chats_from_unknown_users

        if incoming_paid_message_star_count is not None:
            settings.noncontact_peers_paid_stars = incoming_paid_message_star_count

        if show_gift_button is not None:
            settings.show_gift_button = show_gift_button

        if accepted_gift_types is not None:
            settings.disallowed_gifts = accepted_gift_types.write()

        r = await self.invoke(raw.functions.account.SetGlobalPrivacySettings(settings=settings))

        return types.GlobalPrivacySettings._parse(r)
