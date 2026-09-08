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
from pyrogram import raw, utils

from .input_credentials import InputCredentials


class InputCredentialsSaved(InputCredentials):
    """Applies if a user chooses some previously saved payment credentials.

    Parameters:
        saved_credentials_id (``str``):
            Identifier of the saved credentials.

        password (``str``):
            Your Two-Step Verification password.
    """

    def __init__(self, saved_credentials_id: str, password: str):
        super().__init__()

        self.saved_credentials_id = saved_credentials_id
        self.password = password

    async def write(self, client: pyrogram.Client):
        r = await client.invoke(
            raw.functions.account.GetTmpPassword(
                password=utils.compute_password_check(
                    await client.invoke(raw.functions.account.GetPassword()), self.password
                ),
                period=60,
            )
        )

        return raw.types.InputPaymentCredentialsSaved(
            id=self.saved_credentials_id, tmp_password=r.tmp_password
        )
