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

import pyrogram
from pyrogram import raw

from .input_message_content import InputMessageContent

log = logging.getLogger(__name__)


class InputLocationMessageContent(InputMessageContent):
    """Content of a location message to be sent as the result of an inline query.

    Parameters:
        latitude (``float``):
            Latitude of the location.

        longitude (``float``):
            Longitude of the location.

        horizontal_accuracy (``float``, *optional*):
            The radius of uncertainty for the location, measured in meters, 0-1500.

        live_period (``int``, *optional*):
            Period in seconds during which the location can be updated,
            should be between 60 and 86400, or 0x7FFFFFFF for live locations that can be edited indefinitely.

        heading (``int``, *optional*):
            For live locations, a direction in which the user is moving, in degrees.
            Must be between 1 and 360 if specified.

        proximity_alert_radius (``int``, *optional*):
            For live locations, a maximum distance for proximity alerts about approaching another chat member, in meters.
            Must be between 1 and 100000 if specified.
    """

    def __init__(
        self,
        latitude: float,
        longitude: float,
        horizontal_accuracy: float | None = None,
        live_period: int | None = None,
        heading: int | None = None,
        proximity_alert_radius: int | None = None,
    ):
        super().__init__()

        self.latitude = latitude
        self.longitude = longitude
        self.horizontal_accuracy = horizontal_accuracy
        self.live_period = live_period
        self.heading = heading
        self.proximity_alert_radius = proximity_alert_radius

    async def write(self, client: pyrogram.Client, reply_markup):
        return raw.types.InputBotInlineMessageMediaGeo(
            geo_point=raw.types.InputGeoPoint(
                lat=self.latitude, long=self.longitude, accuracy_radius=self.horizontal_accuracy
            ),
            heading=self.heading,
            period=self.live_period,
            proximity_notification_radius=self.proximity_alert_radius,
            reply_markup=await reply_markup.write(client) if reply_markup else None,
        )
