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


class InputVenueMessageContent(InputMessageContent):
    """Content of a venue message to be sent as the result of an inline query.

    Parameters:
        latitude (``float``):
            Latitude of the location.

        longitude (``float``):
            Longitude of the location.

        title (``str``):
            Name of the venue.

        address (``str``):
            Address of the venue.

        foursquare_id (``str``, *optional*):
            Foursquare identifier of the venue, if known.

        foursquare_type (``str``, *optional*):
            Foursquare type of the venue, if known.
            (For example, “arts_entertainment/default”, “arts_entertainment/aquarium” or “food/icecream”.)
    """

    def __init__(
        self,
        latitude: float,
        longitude: float,
        title: str,
        address: str,
        foursquare_id: str | None = None,
        foursquare_type: str | None = None,
        google_place_id: str | None = None,
        google_place_type: str | None = None,
    ):
        super().__init__()

        self.latitude = latitude
        self.longitude = longitude
        self.title = title
        self.address = address
        self.foursquare_id = foursquare_id
        self.foursquare_type = foursquare_type
        self.google_place_id = google_place_id
        self.google_place_type = google_place_type

    async def write(self, client: pyrogram.Client, reply_markup):
        return raw.types.InputBotInlineMessageMediaVenue(
            geo_point=raw.types.InputGeoPoint(lat=self.latitude, long=self.longitude),
            title=self.title,
            address=self.address,
            provider="",
            venue_id=self.foursquare_id,
            venue_type=self.foursquare_type,
            reply_markup=await reply_markup.write(client) if reply_markup else None,
        )
