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

import asyncio
import inspect
from typing import Callable, Any, Awaitable

import pyrogram
from pyrogram.methods.utilities.idle import idle


class Run:
    def run(
        self: "pyrogram.Client",
        coroutine: Callable[[Any, Any], Awaitable[Any]] = None,
        on_startup: Callable[[Any, Any], Awaitable[Any]] = None,
        on_shutdown: Callable[[Any, Any], Awaitable[Any]] = None
    ):
        """Start the client, idle the main script and finally stop the client.

        When calling this method without any argument it acts as a convenience method that calls
        :meth:`~pyrogram.Client.start`, :meth:`~pyrogram.idle` and :meth:`~pyrogram.Client.stop` in sequence.
        It makes running a single client less verbose.

        In case a coroutine is passed as argument, runs the coroutine until it's completed and doesn't do any client
        operation. This is almost the same as :py:obj:`asyncio.run` except for the fact that Pyrogram's ``run`` uses the
        current event loop instead of a new one.

        If you want to run multiple clients at once, see :meth:`pyrogram.compose`.

        Parameters:
            coroutine (``Coroutine``, *optional*):
                Pass a coroutine to run it until it completes.

            on_startup (``callable``, *optional*):
                Function to execute when client is started.

            on_shutdown (``callable``, *optional*):
                Function to execute on client's shutdown.

            NOTE: 
                You can use client methods in on_startup and on_shutdown
                functions only if you're not specifying a coroutine in run()
                since new functions run only before coroutine (it means before client is authorized)
                and after It's finished (after client is terminated).

        Raises:
            ConnectionError: In case you try to run an already started client.

        Example:
            .. code-block:: python

                from pyrogram import Client

                app = Client("my_account")
                ...  # Set handlers up
                app.run()

            .. code-block:: python

                from pyrogram import Client

                app = Client("my_account")


                async def main():
                    async with app:
                        print(await app.get_me())


                app.run(main())
        """
        loop = asyncio.get_event_loop()
        run = loop.run_until_complete

        if coroutine is not None:
            if on_startup:
                run(on_startup())
            run(coroutine)
            if on_shutdown:
                run(on_shutdown())
        else:
            if inspect.iscoroutinefunction(self.start):
                run(self.start(on_startup=on_startup))
                run(idle())
                run(self.stop(on_shutdown=on_shutdown))
            else:
                self.start(on_startup=on_startup)
                run(idle())
                self.stop(on_shutdown=on_shutdown)
