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
import inspect

from .parsers import (
    ChatsType,
    parse_update,
    UsersType,
)
from pyrogram.raw.core import TLObject

import asyncio
import logging
from collections import OrderedDict

import pyrogram
from pyrogram import errors
from pyrogram import raw
from pyrogram.handlers import RawUpdateHandler


log = logging.getLogger(__name__)


class Dispatcher:
    def __init__(self, client: "pyrogram.Client"):
        self.client = client

        self.handler_worker_tasks = []  # TODO: maybe make Semaphore?
        self.locks_list = []  # TODO: make global router lock

        self.updates_queue = asyncio.Queue()  # TODO: move queue to client / session
        self.groups = OrderedDict()

        # TODO: make routing like aiogram with back compatibility

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return asyncio.get_running_loop()

    async def start(self):
        if self.client.no_updates:
            return None

        for i in range(self.client.workers):
            self.locks_list.append(asyncio.Lock())

            self.handler_worker_tasks.append(
                asyncio.create_task(
                    self.handler_worker(self.locks_list[-1]),
                    name=f"dispatcher-worker-{i}",
                )
            )

        log.info("Started %s HandlerTasks", self.client.workers)

        if not self.client.skip_updates:
            # TODO: make better recover gaps, save states, impl watchdog, impl state gap detect

            states = await self.client.storage.update_state()

            if not states:
                log.info("No states found, skipping recovery.")
                return

            message_updates_counter = 0
            other_updates_counter = 0

            for state in states:
                id, local_pts, _, local_date, _ = state

                prev_pts = 0

                while True:
                    # TODO: make message box pattern like telethon

                    try:
                        diff = await self.client.invoke(
                            raw.functions.updates.GetChannelDifference(
                                channel=await self.client.resolve_peer(id),
                                filter=raw.types.ChannelMessagesFilterEmpty(),
                                pts=local_pts,
                                limit=10000,
                            )
                            if id < 0
                            else raw.functions.updates.GetDifference(
                                pts=local_pts, date=local_date, qts=0
                            )
                        )
                    except (errors.ChannelPrivate, errors.ChannelInvalid):
                        break

                    if isinstance(diff, raw.types.updates.DifferenceEmpty):
                        break
                    elif isinstance(diff, raw.types.updates.DifferenceTooLong):
                        # TODO: maybe re-fetch updates
                        break
                    elif isinstance(diff, raw.types.updates.Difference):
                        local_pts = diff.state.pts
                    elif isinstance(diff, raw.types.updates.DifferenceSlice):
                        local_pts = diff.intermediate_state.pts
                        local_date = diff.intermediate_state.date

                        if prev_pts == local_pts:
                            break

                        prev_pts = local_pts
                    elif isinstance(diff, raw.types.updates.ChannelDifferenceEmpty):
                        break
                    elif isinstance(diff, raw.types.updates.ChannelDifferenceTooLong):
                        break
                    elif isinstance(diff, raw.types.updates.ChannelDifference):
                        local_pts = diff.pts

                    users = {i.id: i for i in diff.users}
                    chats = {i.id: i for i in diff.chats}

                    # TODO: sort updates

                    for message in diff.new_messages:
                        message_updates_counter += 1
                        self.updates_queue.put_nowait(
                            (
                                raw.types.UpdateNewMessage(
                                    message=message, pts=local_pts, pts_count=-1
                                )
                                if id == self.client.me.id
                                else raw.types.UpdateNewChannelMessage(
                                    message=message, pts=local_pts, pts_count=-1
                                ),
                                users,
                                chats,
                            )
                        )

                    for update in diff.other_updates:
                        other_updates_counter += 1
                        self.updates_queue.put_nowait((update, users, chats))

                    if isinstance(
                        diff,
                        (
                            raw.types.updates.Difference,
                            raw.types.updates.ChannelDifference,
                        ),
                    ):
                        break

                # TODO: make better state save, too many requests to storage... ?
                await self.client.storage.update_state(id)

            log.info(
                "Recovered %s messages and %s updates.",
                message_updates_counter,
                other_updates_counter,
            )

    async def stop(self):
        if self.client.no_updates:
            return None

        for i in range(self.client.workers):
            self.updates_queue.put_nowait(None)

        for i in self.handler_worker_tasks:
            await i

        self.handler_worker_tasks.clear()
        self.groups.clear()

        log.info("Stopped %s HandlerTasks", self.client.workers)

    def add_handler(self, handler, group: int):
        async def fn():
            for lock in self.locks_list:
                await lock.acquire()

            # TODO: replace groups to routers
            # TODO: impl back compatibility by Dispatcher Decorator pattern
            # TODO: impl most common used routers sorting with many strategies like latency/count/latency and count

            try:
                if group not in self.groups:
                    self.groups[group] = []
                    self.groups = OrderedDict(sorted(self.groups.items()))

                self.groups[group].append(handler)
            finally:
                for lock in self.locks_list:
                    lock.release()

        asyncio.create_task(fn(), name="dispatcher-add-handler")

    def remove_handler(self, handler, group: int):
        async def fn():
            for lock in self.locks_list:
                await lock.acquire()

            try:
                if group not in self.groups:
                    raise ValueError(
                        f"Group {group} does not exist. Handler was not removed."
                    )

                self.groups[group].remove(handler)
            finally:
                for lock in self.locks_list:
                    lock.release()

        asyncio.create_task(fn(), name="dispatcher-remove-handler")

    async def handle_packet(self, update: TLObject, users: UsersType, chats: ChatsType):
        parsed_update, handler_type = await parse_update(
            client=self.client,
            update=update,
            users=users,
            chats=chats,
        )

        for group in self.groups.values():
            for handler in group:
                args = None

                if handler_type and isinstance(handler, handler_type):
                    try:
                        if await handler.check(self.client, parsed_update):
                            args = (parsed_update,)
                    except Exception as exc:
                        log.exception(exc)
                        continue
                elif isinstance(handler, RawUpdateHandler):
                    args = (update, users, chats)

                if args is None:
                    continue

                try:
                    if inspect.iscoroutinefunction(handler.callback):
                        await handler.callback(self.client, *args)
                    else:
                        # TODO: remove sync or move on next layer
                        await self.loop.run_in_executor(
                            self.client.executor, handler.callback, self.client, *args
                        )
                except pyrogram.ContinuePropagation:
                    log.debug("Continue propagation detected")
                    continue

                break

    async def handler_worker(self, lock: asyncio.Lock) -> None:
        while True:
            packet = await self.updates_queue.get()

            if packet is None:
                break

            try:
                update, users, chats = packet

                async with lock:
                    await self.handle_packet(update, users, chats)
            except pyrogram.StopPropagation:
                log.debug("Handler was stopped.")
            except Exception as exc:
                log.exception(exc)  # TODO: exception handler?
