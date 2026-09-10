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
from pyrogram import raw

from .auto_name import AutoName


class PaidReactionPrivacy(AutoName):
    """Reaction privacy type enumeration used in :meth:`~pyrogram.Client.send_paid_reaction`."""

    DEFAULT = raw.types.PaidReactionPrivacyDefault
    "Send default reaction"

    ANONYMOUS = raw.types.PaidReactionPrivacyAnonymous
    "Send anonymous reaction"

    CHAT = raw.types.PaidReactionPrivacyPeer
    "Send reaction as specific chat. You can get all available chats in :meth:`~pyrogram.Client.get_send_as_chats`"
