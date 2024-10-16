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
import functools
import inspect
import io
import logging
import math
import os
from concurrent.futures import Executor
from contextlib import contextmanager
from hashlib import md5
from pathlib import PurePath
from typing import (
    Awaitable,
    BinaryIO,
    Callable,
    Optional,
    Union,
)
from typing_extensions import ParamSpec
import pyrogram
from pyrogram import (
    raw,
    StopTransmission,
    types,
)
from pyrogram.raw.core import TLObject
from pyrogram.session.session import Session

log = logging.getLogger(__name__)


async def file_upload_worker(
    session: Session,
    queue: "asyncio.Queue[TLObject]"
) -> None:
    while True:
        data = await queue.get()

        if data is None:
            return

        try:
            await session.invoke(data)
        except Exception as e:
            log.exception(e)


P = ParamSpec("P")


async def empty_progress_callback(current: int, total: int, *args, **kwargs) -> None:
    return None


def make_progress_callback(
    callback: Optional[Callable[[int, int, P], Awaitable[None]]],
    executor: Executor,
    file_size: int,
    args: P.args,
    kwargs: P.kwargs
) -> Callable[[int], Awaitable[None]]:
    if callback is None:
        callback = empty_progress_callback

    if args is None:
        args = ()

    if kwargs is None:
        kwargs = {}

    is_awaitable = inspect.iscoroutinefunction(callback)

    async def wrapper(current: int) -> None:
        func = functools.partial(callback, current, file_size, *args, **kwargs)
        if is_awaitable:
            return await func()

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(executor, func)

    return wrapper


@contextmanager
def open_media_file(
    me: Optional[types.User],
    path: Union[str, BinaryIO]
):
    if isinstance(path, (str, PurePath)):
        fp = open(path, "rb")
        fp_close = True
    elif isinstance(path, io.IOBase):
        fp = path
        fp_close = False
    else:
        raise ValueError("Invalid file. Expected a file path as string or a binary (not text) file pointer")

    file_name = getattr(fp, "name", "file.jpg")
    fp.seek(0, os.SEEK_END)
    file_size = fp.tell()
    fp.seek(0)

    if file_size == 0:
        raise ValueError("File size equals to 0 B")

    file_size_limit_mib = 4_000 if me and me.is_premium else 2_000
    if file_size > file_size_limit_mib * 1024 * 1024:
        raise ValueError(f"Can't upload files bigger than {file_size_limit_mib} MiB")

    try:
        yield fp, file_size, file_name
    finally:
        if fp_close:
            fp.close()


class SaveFile:
    async def save_file(
        self: "pyrogram.Client",
        path: Union[str, BinaryIO],
        file_id: int = None,
        file_part: int = 0,
        progress: Callable = None,
        progress_args: tuple = None,
        progress_kwargs: dict = None,
    ):
        """Upload a file onto Telegram servers, without actually sending the message to anyone.
        Useful whenever an InputFile type is required.

        .. note::

            This is a utility method intended to be used **only** when working with raw
            :obj:`functions <pyrogram.api.functions>` (i.e: a Telegram API method you wish to use which is not
            available yet in the Client class as an easy-to-use method).

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            path (``str`` | ``BinaryIO``):
                The path of the file you want to upload that exists on your local machine or a binary file-like object
                with its attribute ".name" set for in-memory uploads.

            file_id (``int``, *optional*):
                In case a file part expired, pass the file_id and the file_part to retry uploading that specific chunk.

            file_part (``int``, *optional*):
                In case a file part expired, pass the file_id and the file_part to retry uploading that specific chunk.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            ``InputFile``: On success, the uploaded file is returned in form of an InputFile object.

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        async with self.save_file_semaphore:
            if path is None:
                return None

            with open_media_file(self.me, path) as (fp, file_size, file_name):
                progress_callback = make_progress_callback(
                    callback=progress,
                    executor=self.executor,
                    file_size=file_size,
                    args=progress_args,
                    kwargs=progress_kwargs,
                )

                part_size = 512 * 1024

                file_total_parts = math.ceil(file_size / part_size)
                is_big = file_size > 10 * 1024 * 1024
                workers_count = 4 if is_big else 1
                is_missing_part = file_id is not None
                file_id = file_id or self.rnd_id()
                md5_sum = md5() if not is_big and not is_missing_part else None
                dc_id = await self.storage.dc_id()

                session = await self.session_pool.get_media_session(dc_id)

                queue = asyncio.Queue(1)
                workers = [asyncio.create_task(file_upload_worker(session, queue), name=f"upload-worker-{i}") for i in range(workers_count)]

                try:
                    fp.seek(part_size * file_part)

                    while True:
                        chunk = fp.read(part_size)

                        if not chunk:
                            if not is_big and not is_missing_part:
                                md5_sum = "".join([hex(i)[2:].zfill(2) for i in md5_sum.digest()])
                            break

                        if is_big:
                            rpc = raw.functions.upload.SaveBigFilePart(
                                file_id=file_id,
                                file_part=file_part,
                                file_total_parts=file_total_parts,
                                bytes=chunk
                            )
                        else:
                            rpc = raw.functions.upload.SaveFilePart(
                                file_id=file_id,
                                file_part=file_part,
                                bytes=chunk
                            )

                        await queue.put(rpc)

                        if is_missing_part:
                            return

                        if not (is_big or is_missing_part):
                            md5_sum.update(chunk)

                        file_part += 1
                        await progress_callback(min(file_part * part_size, file_size))
                except StopTransmission:
                    raise
                except Exception as e:
                    log.exception(e)
                else:
                    if is_big:
                        return raw.types.InputFileBig(
                            id=file_id,
                            parts=file_total_parts,
                            name=file_name,

                        )
                    else:
                        return raw.types.InputFile(
                            id=file_id,
                            parts=file_total_parts,
                            name=file_name,
                            md5_checksum=md5_sum
                        )
                finally:
                    for _ in workers:
                        await queue.put(None)

                    await asyncio.gather(*workers)
