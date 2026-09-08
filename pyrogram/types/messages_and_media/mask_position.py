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

from pyrogram import enums, raw

from ..object import Object


class MaskPosition(Object):
    """This object describes the position on faces where a mask should be placed by default.

    Parameters:
        point (:obj:`~pyrogram.enums.MaskPointType`):
            The part of the face relative to which the mask should be placed.

        x_shift (``float``):
            Shift by X-axis measured in widths of the mask scaled to the face size, from left to right.
            For example, choosing -1.0 will place mask just to the left of the default mask position.

        y_shift (``float``):
            Shift by Y-axis measured in heights of the mask scaled to the face size, from top to bottom.
            For example, 1.0 will place the mask just below the default mask position.

        scale (``float``):
            Mask scaling coefficient. For example, 2.0 means double size.
    """
    def __init__(
        self,
        *,
        point: enums.MaskPointType,
        x_shift: float,
        y_shift: float,
        scale: float
    ):
        super().__init__()

        self.point = point
        self.x_shift = x_shift
        self.y_shift = y_shift
        self.scale = scale

    @staticmethod
    def _parse(
        coords: raw.types.MaskCoords
    ) -> MaskPosition:
        if not coords:
            return None

        return MaskPosition(
            point=enums.MaskPointType(coords.n),
            x_shift=coords.x,
            y_shift=coords.y,
            scale=coords.zoom
        )
