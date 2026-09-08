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

import logging
from collections.abc import Iterable

import pyrogram
from pyrogram import raw
from pyrogram.errors import (
    ChannelInvalid,
    ChannelPrivate,
    PersistentTimestampInvalid,
    PersistentTimestampOutdated,
)
from pyrogram.storage import UpdateState
from pyrogram.utils import ZERO_CHANNEL_ID

log = logging.getLogger(__name__)


class RecoverGaps:
    async def recover_gaps(
        self: pyrogram.Client, ids: int | Iterable[int] | None = None
    ) -> tuple[int, int]:
        """Restores updates for the time while the client was offline.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            ids (``int`` | List of ``int``, *optional*):
                Identifiers of the chats to recover, 0 for personal messages and updates.
                If omitted, all known chats will be recovered.

        Returns:
            ``tuple``: The number of recovered messages and other updates is returned.
        """
        message_updates_counter = 0
        other_updates_counter = 0

        states = await self.storage.get_update_states(ids)

        if not states:
            log.info("No states found, skipping recovery")
            return (message_updates_counter, other_updates_counter)

        log.info("Started gaps recovering...")

        for local_state in states:
            id = local_state.id
            local_pts = local_state.pts
            local_qts = local_state.qts
            local_date = local_state.date
            local_seq = local_state.seq

            state_deleted = False

            while True:
                request_pts = local_pts

                try:
                    diff = await self.invoke(
                        raw.functions.updates.GetChannelDifference(
                            channel=await self.resolve_peer(id),
                            filter=raw.types.ChannelMessagesFilterEmpty(),
                            pts=request_pts,
                            limit=10000,
                            force=False,
                        )
                        if id < ZERO_CHANNEL_ID
                        else raw.functions.updates.GetDifference(
                            pts=request_pts, date=local_date, qts=0
                        )
                    )
                except (ChannelPrivate, ChannelInvalid):
                    await self.storage.delete_update_state(id)
                    state_deleted = True
                    break
                except (PersistentTimestampOutdated, PersistentTimestampInvalid):
                    continue

                if isinstance(diff, raw.types.updates.DifferenceEmpty):
                    await self.storage.set_update_state(
                        UpdateState(id, local_pts, local_qts, diff.date, diff.seq)
                    )
                    break

                if isinstance(diff, raw.types.updates.DifferenceTooLong):
                    local_pts = diff.pts
                    await self.storage.set_update_state(
                        UpdateState(id, local_pts, local_qts, local_date, local_seq)
                    )
                    continue

                if isinstance(diff, raw.types.updates.Difference):
                    local_pts = diff.state.pts
                    local_date = diff.state.date
                    local_seq = diff.state.seq
                elif isinstance(diff, raw.types.updates.DifferenceSlice):
                    new_pts = diff.intermediate_state.pts
                    no_progress = new_pts == request_pts
                    local_pts = new_pts
                    local_date = diff.intermediate_state.date
                    local_seq = diff.intermediate_state.seq
                elif isinstance(diff, raw.types.updates.ChannelDifferenceEmpty):
                    await self.storage.set_update_state(
                        UpdateState(id, diff.pts, local_qts, local_date, local_seq)
                    )
                    break
                elif isinstance(diff, raw.types.updates.ChannelDifferenceTooLong):
                    local_pts = diff.dialog.pts
                    await self.storage.set_update_state(
                        UpdateState(id, local_pts, local_qts, local_date, local_seq)
                    )
                    continue
                elif isinstance(diff, raw.types.updates.ChannelDifference):
                    local_pts = diff.pts

                users = {i.id: i for i in diff.users}
                chats = {i.id: i for i in diff.chats}

                for message in diff.new_messages:
                    self.dispatcher.updates_queue.put_nowait(
                        (
                            raw.types.UpdateNewMessage(
                                message=message, pts=local_pts, pts_count=-1
                            ),
                            users,
                            chats,
                        )
                    )
                    message_updates_counter += 1

                for update in diff.other_updates:
                    self.dispatcher.updates_queue.put_nowait((update, users, chats))
                    other_updates_counter += 1

                if isinstance(diff, raw.types.updates.Difference):
                    break

                if isinstance(diff, raw.types.updates.ChannelDifference) and diff.final:
                    break

                if isinstance(diff, raw.types.updates.DifferenceSlice) and no_progress:
                    break

            if state_deleted:
                continue

            await self.storage.set_update_state(
                UpdateState(id, local_pts, local_qts, local_date, local_seq)
            )

        await self.storage.save()

        log.info(
            "Recovered %s messages and %s updates", message_updates_counter, other_updates_counter
        )
        return (message_updates_counter, other_updates_counter)
