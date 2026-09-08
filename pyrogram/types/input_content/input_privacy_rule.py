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

from ..object import Object


class InputPrivacyRule(Object):
    """Content of a privacy rule.

    It should be one of:

    - :obj:`~pyrogram.types.InputPrivacyRuleAllowAll`
    - :obj:`~pyrogram.types.InputPrivacyRuleAllowContacts`
    - :obj:`~pyrogram.types.InputPrivacyRuleAllowPremium`
    - :obj:`~pyrogram.types.InputPrivacyRuleAllowUsers`
    - :obj:`~pyrogram.types.InputPrivacyRuleAllowChats`
    - :obj:`~pyrogram.types.InputPrivacyRuleDisallowAll`
    - :obj:`~pyrogram.types.InputPrivacyRuleDisallowContacts`
    - :obj:`~pyrogram.types.InputPrivacyRuleDisallowUsers`
    - :obj:`~pyrogram.types.InputPrivacyRuleDisallowChats`
    """

    def __init__(self):
        super().__init__()

    async def write(self, client: pyrogram.Client):
        raise NotImplementedError
