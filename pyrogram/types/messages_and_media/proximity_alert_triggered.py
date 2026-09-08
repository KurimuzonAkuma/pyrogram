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
from pyrogram import raw, types, utils

from ..object import Object


class ProximityAlertTriggered(Object):
    """Information about a proximity alert.

    Parameters:
        traveler (:obj:`~pyrogram.types.User`):
            Chat that triggered the proximity alert.

        watcher (:obj:`~pyrogram.types.User`):
            Chat that subscribed for the proximity alert.

        distance (``str``):
            The distance between the users.
    """

    def __init__(
        self, *, traveler: pyrogram.types.User, watcher: pyrogram.types.User, distance: str
    ):
        super().__init__()

        self.traveler = traveler
        self.watcher = watcher
        self.distance = distance

    @staticmethod
    async def _parse(
        client: pyrogram.Client,
        action: raw.types.MessageActionGeoProximityReached,
        users: dict[int, raw.base.User],
        chats: dict[int, raw.base.Chat],
    ) -> ProximityAlertTriggered:
        from_id = utils.get_raw_peer_id(action.from_id)
        to_id = utils.get_raw_peer_id(action.to_id)

        return ProximityAlertTriggered(
            traveler=await types.Chat._parse_chat(client, users.get(from_id) or chats.get(from_id)),
            watcher=await types.Chat._parse_chat(client, users.get(to_id) or chats.get(to_id)),
            distance=action.distance,
        )
