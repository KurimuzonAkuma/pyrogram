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
import time

log = logging.getLogger(__name__)


class MsgId:
    _last_msg_id = 0

    def __new__(cls) -> int:
        now = time.time()
        base_msg_id = int(now * (2**32)) & ~0b11

        if base_msg_id <= cls._last_msg_id:
           base_msg_id = cls._last_msg_id + 4

        cls._last_msg_id = base_msg_id

        return base_msg_id
