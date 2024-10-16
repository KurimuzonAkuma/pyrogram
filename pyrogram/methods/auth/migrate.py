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

import pyrogram
from pyrogram.session.auth import Auth
from pyrogram.session.session import Session


class MigrateDC:
    async def migrate_dc(
        self: "pyrogram.Client", dc_id: int
    ) -> bool:
        await self.session_pool.aclose()
        await self.storage.dc_id(dc_id)

        dc_id = await self.storage.dc_id()
        test_mode = await self.storage.test_mode()

        auth_key = await Auth(
            client=self,
            dc_id=dc_id,
            test_mode=self.test_mode,
        ).create()
        await self.storage.auth_key(auth_key)
        main_simple_session = Session(
            client=self,
            dc_id=dc_id,
            auth_key=auth_key,
            test_mode=test_mode,
        )
        await main_simple_session.start()
        self.session_pool.set_main_simple_session(main_simple_session)
