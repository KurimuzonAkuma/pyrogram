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
import logging

import pyrogram
from pyrogram.session.session import Session
log = logging.getLogger(__name__)


class Connect:
    async def connect(
        self: "pyrogram.Client",
    ) -> bool:
        """
        Connect the client to Telegram servers.

        Returns:
            ``bool``: On success, in case the passed-in session is authorized, True is returned. Otherwise, in case
            the session needs to be authorized, False is returned.

        Raises:
            ConnectionError: In case you try to connect an already connected client.
        """
        if self.is_connected:
            raise ConnectionError("Client is already connected")

        await self.load_session()

        dc_id = await self.storage.dc_id()
        auth_key = await self.storage.auth_key()
        test_mode = await self.storage.test_mode()

        main_simple_session = Session(
            client=self,
            dc_id=dc_id,
            auth_key=auth_key,
            test_mode=test_mode,
        )

        await main_simple_session.start()

        log.debug("Connected")

        self.session_pool.set_main_simple_session(main_simple_session)
        self.is_connected = True

        return bool(await self.storage.user_id())
