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
import logging
from contextlib import suppress
from io import BytesIO
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Union,
)
import pyrogram
from pyrogram import raw
from pyrogram.connection import Connection
from pyrogram.crypto import mtproto
from pyrogram.errors import (
    AuthKeyDuplicated,
    FloodPremiumWait,
    FloodWait,
    InternalServerError,
    RPCError,
    SecurityCheckMismatch,
    ServiceUnavailable,
    Unauthorized,
)
from pyrogram.raw.all import layer
from .internals import AuthData

log = logging.getLogger(__name__)


class RequestState:
    def __init__(
        self,
        request: raw.core.TLObject,
    ):
        self.request = request
        self.future = asyncio.Future()

    def __str__(self):
        return str(self.request)

    def done(self) -> bool:
        return self.future.done()

    def set_result(self, value: Any) -> None:
        if self.future.done():
            return None
        self.future.set_result(value)

    def set_exception(self, value: Exception) -> None:
        if self.future.done():
            return None
        self.future.set_exception(value)

    @property
    def request_raw(self) -> raw.core.TLObject:
        request = self.request
        while isinstance(
            request, (
                raw.functions.InvokeAfterMsg,
                raw.functions.InvokeAfterMsgs,
                raw.functions.InitConnection,
                raw.functions.InvokeWithLayer,
                raw.functions.InvokeWithoutUpdates,
                raw.functions.InvokeWithMessagesRange,
                raw.functions.InvokeWithTakeout,
                raw.functions.InvokeWithBusinessConnection,
            )
        ):
            request = request.query

        return request

    @property
    def is_content_related(self) -> bool:
        return not isinstance(
            self.request_raw, (raw.functions.Ping, raw.types.HttpWait, raw.types.MsgsAck, raw.core.MsgContainer)
        )


async def task_cancel(*tasks: "Optional[asyncio.Task[Any]]") -> None:
    for task in tasks:
        if task is None:
            continue

        if task.done():
            continue

        task.cancel()

        try:
            await task
        except (asyncio.CancelledError, RuntimeError):
            pass


class Session:
    START_TIMEOUT = 2
    WAIT_TIMEOUT = 15
    SLEEP_THRESHOLD = 10
    MAX_RETRIES = 10
    ACKS_THRESHOLD = 10
    PING_INTERVAL = 5

    TRANSPORT_ERRORS = {
        403: "forbidden",
        404: "auth key not found",
        429: "transport flood",
        444: "invalid DC"
    }

    def __init__(
        self,
        client: "pyrogram.Client",
        dc_id: int,
        auth_key: bytes,
        test_mode: bool,
        is_media: bool = False,
        is_cdn: bool = False,
        reconnect: bool = True
    ):
        self.client = client
        self.dc_id = dc_id
        self.test_mode = test_mode
        self.is_media = is_media
        self.is_cdn = is_cdn
        self.reconnect = reconnect
        self.auth_data: AuthData = AuthData(
            main_auth_key=auth_key
        )

        self.connection: Optional[Connection] = None

        self.pending_acks: Set[int] = set()
        self.pending_requests: "asyncio.Queue[RequestState]" = asyncio.Queue()

        self.results: Dict[int, RequestState] = {}

        self.ping_task: "Optional[asyncio.Task[None]]" = None
        self.ping_event = asyncio.Event()
        self.pong_event = asyncio.Event()

        self.recv_task: "Optional[asyncio.Task[None]]" = None
        self.send_task: "Optional[asyncio.Task[None]]" = None

        self.is_started = asyncio.Event()

        self.handler_by_constructor_id: Dict[int, Callable[[raw.core.Message], Awaitable[None]]] = {
            raw.types.RpcResult.ID: self.handle_rpc_result,
            raw.core.MsgContainer.ID: self.handle_msg_container,
            raw.core.GzipPacked.ID: self.handle_gzip_packed,
            raw.types.Pong.ID: self.handle_pong,
            raw.types.BadServerSalt.ID: self.handle_bad_server_salt,
            raw.types.BadMsgNotification.ID: self.handle_bad_msg_notification,
            raw.types.MsgDetailedInfo.ID: self.handle_msg_detailed_info,
            raw.types.MsgNewDetailedInfo.ID: self.handle_msg_new_detailed_info,
            raw.types.NewSessionCreated.ID: self.handle_new_session_created,
            raw.types.MsgsAck.ID: self.handle_msgs_ack,
            raw.core.FutureSalts.ID: self.handle_future_salts,
            raw.types.MsgsStateReq.ID: self.handle_state_forgotten,
            raw.types.MsgResendReq.ID: self.handle_state_forgotten,
            raw.types.MsgsAllInfo.ID: self.handle_msg_all,
            raw.types.DestroySessionOk.ID: self.handle_destroy_session,
            raw.types.DestroySessionNone.ID: self.handle_destroy_session,
            raw.types.DestroyAuthKeyOk.ID: self.handle_destroy_auth_key,
            raw.types.DestroyAuthKeyNone.ID: self.handle_destroy_auth_key,
            raw.types.DestroyAuthKeyFail.ID: self.handle_destroy_auth_key,

            raw.types.Updates.ID: self.handle_update,
            raw.types.UpdatesCombined.ID: self.handle_update,
            raw.types.UpdateShortMessage.ID: self.handle_update,
            raw.types.UpdateShortChatMessage.ID: self.handle_update,
            raw.types.UpdateShort.ID: self.handle_update,
            raw.types.UpdatesTooLong.ID: self.handle_update
        }

        self._loop: Optional[asyncio.AbstractEventLoop] = None

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        return self._loop

    async def start(self):
        while True:
            try:
                self.connection = await self.client.connection_factory.new(
                    dc_id=self.dc_id,
                    test_mode=self.test_mode,
                    ipv6=self.client.ipv6,
                    proxy=self.client.proxy,
                    media=self.is_media,
                    protocol_factory=self.client.protocol_factory
                )

                self.recv_task = asyncio.create_task(self.recv_worker(), name="recv-worker")
                self.send_task = asyncio.create_task(self.send_worker(), name="send-worker")

                await self.send(raw.functions.Ping(ping_id=0), timeout=self.START_TIMEOUT)

                if not self.is_cdn:
                    await self.send(
                        raw.functions.InvokeWithLayer(
                            layer=layer,
                            query=raw.functions.InitConnection(
                                api_id=await self.client.storage.api_id(),
                                app_version=self.client.app_version,
                                device_model=self.client.device_model,
                                system_version=self.client.system_version,
                                system_lang_code=self.client.system_lang_code,
                                lang_pack=self.client.lang_pack,
                                lang_code=self.client.lang_code,
                                query=raw.functions.help.GetConfig(),
                                params=self.client.init_connection_params,
                            )
                        ),
                        timeout=self.START_TIMEOUT
                    )

                self.ping_task = asyncio.create_task(self.ping_worker(), name="ping-worker")

                log.info("Session initialized: Layer %s", layer)
                log.info("Device: %s - %s", self.client.device_model, self.client.app_version)
                log.info("System: %s (%s)", self.client.system_version, self.client.lang_code)
            except (AuthKeyDuplicated, Unauthorized) as e:
                await self.stop()
                raise e
            except (OSError, RPCError):
                await self.stop()
            except Exception as e:
                await self.stop()
                raise e
            else:
                break

        self.is_started.set()

        log.info("Session started")

    async def stop(self):
        self.is_started.clear()
        self.ping_event.clear()
        self.pong_event.clear()

        await task_cancel(
            self.ping_task,
            self.recv_task,
            self.send_task
        )

        if self.connection:
            await self.connection.close()

        if not self.is_media and callable(self.client.disconnect_handler):
            try:
                await self.client.disconnect_handler(self.client)
            except Exception as e:
                log.exception(e)

        log.info("Session stopped")

    async def restart(self):
        await self.stop()

        if self.reconnect:
            await self.start()

    async def ping_worker(self):
        log.info("PingTask started")

        while True:
            log.debug("wait ping task begin")

            with suppress(asyncio.TimeoutError):
                await asyncio.wait_for(self.ping_event.wait(), self.WAIT_TIMEOUT + 15)

            log.debug("wait ping task end")

            if not self.pong_event.is_set():
                log.debug("pong not found")
                asyncio.create_task(self.restart(), name="session-restart")  # TODO: graceful restart
                break

            self.pong_event.clear()
            self.pending_requests.put_nowait(
                RequestState(
                    raw.functions.PingDelayDisconnect(
                        ping_id=0, disconnect_delay=self.WAIT_TIMEOUT + 10
                    )
                )
            )

        log.info("PingTask stopped")

    async def send_worker(self):
        # TODO: ping
        # TODO: future salts
        # TODO: resend_answer
        # TODO: cancel_answer
        # TODO: get_state_info
        # TODO: ack
        # TODO: gzip
        # TODO: group batch to containers
        log.info("SendTask started")

        while True:
            log.debug("wait pending request")
            request_state = await self.pending_requests.get()
            log.debug("pending request: %s", request_state)

            try:
                if request_state.done():
                    log.debug("drop request: %s", request_state)
                    continue

                now = self.auth_data.get_client_time()
                message = self.auth_data.msg_factory(
                    body=request_state.request,
                    is_content_related=request_state.is_content_related,
                    now=now
                )

                log.debug("pack message begin")
                payload = await self.loop.run_in_executor(
                    pyrogram.crypto_executor,
                    mtproto.pack,
                    message,
                    self.auth_data.get_server_salt(
                        now=now
                    ),
                    self.auth_data.session_id,
                    self.auth_data.main_auth_key,
                    self.auth_data.main_auth_key_id
                )
                log.debug("pack message end")

                self.results[message.msg_id] = request_state

                try:
                    log.debug("connection.send begin")
                    await self.connection.send(payload)
                    log.debug("connection.send end")
                except OSError as exc:
                    log.warning("Connection error: %s", exc)  # TODO: graceful restart
                    asyncio.create_task(self.restart(), name="session-restart")
                    break
                else:
                    log.debug("Sent: %s", request_state)
            finally:
                self.pending_requests.task_done()
                log.debug("pending request done")

    async def recv_worker(self):
        log.info("NetworkTask started")

        while True:
            log.debug("connection.recv begin")
            packet = await self.connection.recv()
            log.debug("connection.recv end")

            log.debug("packet: %s", packet)

            if packet is None or len(packet) == 4:
                if packet:
                    error_code = -int.from_bytes(packet, byteorder="little", signed=True)

                    log.info("error_code: %s", error_code)

                    if error_code == 404:
                        raise Unauthorized(
                            "Auth key not found in the system. You must delete your session file "
                            "and log in again with your phone number or bot token."
                        )

                    log.warning(
                        "Server sent transport error: %s (%s)",
                        error_code, Session.TRANSPORT_ERRORS.get(error_code, "unknown error")
                    )

                if self.is_started.is_set():
                    asyncio.create_task(self.restart(), name="session-restart")  # TODO: graceful restart

                break

            log.debug("unpack message begin")
            message = await self.loop.run_in_executor(
                pyrogram.crypto_executor,
                mtproto.unpack,
                BytesIO(packet),
                self.auth_data.session_id,
                self.auth_data.main_auth_key,
                self.auth_data.main_auth_key_id
            )
            log.debug("unpack message end")

            try:
                await self.handle_message(message)
            except SecurityCheckMismatch as exc:
                log.info("Discarding packet: %s", exc)
                if exc.fatal:
                    await self.connection.close()
                    return
            except Exception as exc:
                log.warning("Unhandled exception: %s", exc)

            log.debug("send acks")
            await self.send_pending_acks()

        log.info("NetworkTask stopped")

    def reset_server_time_difference(self, message_id: int) -> None:
        log.debug("reset server time difference: %s", message_id)

        diff = (message_id >> 32) - self.auth_data.get_client_time()
        self.auth_data.reset_server_time_difference(diff)

    async def handle_message(self, message: raw.core.Message) -> None:
        log.debug("handle message: %s", message)

        self.auth_data.check_packet(
            message_id=message.msg_id,
            now=self.auth_data.get_client_time()
        )

        if message.seq_no % 2:
            self.pending_acks.add(message.msg_id)

        handler = self.handler_by_constructor_id.get(message.body.ID)
        if handler is None:
            return await self.handle_unknown(message)
        return await handler(message)

    def set_request_state_result(self, msg_id: int, value: Any) -> None:
        log.debug("set request state (%s) result: %s", msg_id, value)

        request_state = self.results.pop(msg_id, None)
        if request_state is None:
            return None

        request_state.set_result(value)
        return None

    def set_request_state_exception(self, msg_id: int, value: Exception) -> None:
        log.debug("set request state (%s) exception: %s", msg_id, value)

        request_state = self.results.pop(msg_id, None)
        if request_state is None:
            return None

        request_state.set_exception(value)
        return None

    async def handle_msg_container(
        self,
        message: raw.core.Message[raw.core.MsgContainer],
    ) -> None:
        log.debug("raw.core.MsgContainer received: %s", message)
        for msg in message.body.messages:
            try:
                await self.handle_message(msg)
            except SecurityCheckMismatch as exc:
                log.info("Discarding packet: %s", exc)
            except Exception as exc:
                log.warning("Unhandled exception: %s", exc)

        self.set_request_state_result(message.msg_id, message.body)

    async def handle_rpc_result(self, message: raw.core.Message[raw.types.RpcResult]) -> None:
        log.debug("raw.types.RpcResult received: %s", message)

        if message.msg_id < (message.body.req_msg_id - (15 << 32)):
            self.reset_server_time_difference(
                message_id=message.msg_id
            )

        request_state = self.results.pop(message.body.req_msg_id, None)
        if request_state is None:
            return None

        if isinstance(message.body.result, raw.types.RpcError):
            try:
                RPCError.raise_it(message.body.result, type(request_state.request_raw))
            except Exception as exc:
                request_state.set_exception(exc)
            else:
                request_state.set_result(None)
        else:
            request_state.set_result(message.body.result)

    async def handle_gzip_packed(self, message: raw.core.Message[raw.core.GzipPacked]) -> None:
        log.debug("raw.core.GzipPacked received: %s", message)
        # unreachable
        return None

    async def handle_pong(self, message: raw.core.Message[raw.types.Pong]) -> None:
        log.debug("raw.types.Pong received: %s", message)

        if message.msg_id < (message.body.msg_id - (15 << 32)):
            self.reset_server_time_difference(
                message_id=message.msg_id
            )

        self.pong_event.set()
        self.set_request_state_result(
            msg_id=message.body.msg_id,
            value=message.body
        )

    async def handle_bad_server_salt(self, message: raw.core.Message[raw.types.BadServerSalt]) -> None:
        log.debug("raw.types.BadServerSalt received: %s", message)

        self.auth_data.set_server_salt(
            salt=message.body.new_server_salt,
            now=self.auth_data.get_client_time()
        )
        request_state = self.results.pop(message.body.bad_msg_id, None)
        if request_state is None:
            return None

        self.pending_requests.put_nowait(request_state)

    async def handle_bad_msg_notification(self, message: raw.core.Message[raw.types.BadMsgNotification]) -> None:
        log.debug("raw.types.BadMsgNotification received: %s", message)

        request_state = self.results.pop(message.body.bad_msg_id, None)
        if request_state is None:
            return None

        if message.body.error_code in (16, 17, 18):
            # MsgIdTooLow, MsgIdTooHigh, MsgIdMod4
            self.reset_server_time_difference(message.msg_id)
            self.pending_requests.put_nowait(request_state)
            return None

        if message.body.error_code == 32:
            # SeqNoTooLow
            self.auth_data.seq_no += 64
            self.pending_requests.put_nowait(request_state)
            return None

        if message.body.error_code == 33:
            # SeqNoTooHigh
            self.auth_data.seq_no -= 16
            self.pending_requests.put_nowait(request_state)
            return None

        if message.body.error_code in (19, 20, 48):
            # MsgIdCollision, MsgIdTooOld, BadServerSalt
            # BadServerSalt unreachable
            self.pending_requests.put_nowait(request_state)
            return None

        rpc_name = ".".join(request_state.request_raw.QUALNAME.split(".")[1:])
        rpc_error_code = f"BAD_MSG_NOTIFICATION_{message.body.error_code}"

        request_state.set_exception(
            value=RPCError(
                value=rpc_error_code,
                rpc_name=rpc_name,
            )
        )

    async def handle_msg_detailed_info(self, message: raw.core.Message[raw.types.MsgDetailedInfo]) -> None:
        log.debug("raw.types.MsgDetailedInfo received: %s", message)
        self.pending_acks.add(message.body.answer_msg_id)

    async def handle_msg_new_detailed_info(self, message: raw.core.Message[raw.types.MsgNewDetailedInfo]) -> None:
        log.debug("raw.types.MsgNewDetailedInfo received: %s", message)
        self.pending_acks.add(message.body.answer_msg_id)

    async def handle_new_session_created(self, message: raw.core.Message[raw.types.NewSessionCreated]) -> None:
        log.debug("raw.types.NewSessionCreated received: %s", message)

        # TODO: Create new auth key + session, re-send requests
        self.auth_data.set_server_salt(
            salt=message.body.server_salt,
            now=self.auth_data.get_client_time()
        )

        return None

    async def handle_msgs_ack(self, message: raw.core.Message[raw.types.MsgsAck]) -> None:
        log.debug("raw.types.MsgsAck received: %s", message)

        for msg_id in message.body.msg_ids:
            request_state = self.results.get(msg_id)
            if request_state is None:
                continue

            if isinstance(request_state.request_raw, raw.functions.auth.LogOut):
                del self.results[msg_id]
                request_state.set_result(True)

        return None

    async def handle_future_salts(self, message: raw.core.Message[raw.core.FutureSalts]) -> None:
        log.debug("raw.core.FutureSalts received: %s", message)

        self.auth_data.set_future_salts(
            future_salts=message.body.salts,
            now=self.auth_data.get_client_time()
        )
        self.set_request_state_result(
            msg_id=message.body.req_msg_id,
            value=message.body
        )

    async def handle_state_forgotten(
        self, message: raw.core.Message[Union[raw.types.MsgsStateReq, raw.types.MsgResendReq]]
    ) -> None:
        log.debug("raw.types.MsgsStateReq/raw.types.MsgResendReq received: %s", message)
        return None

    async def handle_msg_all(self, message: raw.core.Message[raw.types.MsgsAllInfo]) -> None:
        log.debug("raw.types.MsgsAllInfo received: %s", message)
        return None

    async def handle_destroy_session(
        self, message: raw.core.Message[Union[raw.types.DestroySessionOk, raw.types.DestroySessionNone]]
    ) -> None:
        log.debug("raw.types.DestroySessionOk/raw.types.DestroySessionNone received: %s", message)

        msg_ids: List[int] = []

        for msg_id, request_state in self.results.items():
            request_raw = request_state.request_raw

            if not isinstance(request_raw, raw.functions.DestroySession):
                continue

            if request_raw.session_id == message.body.session_id:
                msg_ids.append(msg_id)

        for msg_id in msg_ids:
            self.set_request_state_result(msg_id=msg_id, value=message.body)

        return None

    async def handle_destroy_auth_key(
        self,
        message: raw.core.Message[
            Union[raw.types.DestroyAuthKeyOk, raw.types.DestroyAuthKeyNone, raw.types.DestroyAuthKeyFail]]
    ) -> None:
        log.debug(
            "raw.types.DestroyAuthKeyOk/raw.types.DestroyAuthKeyNone/raw.types.DestroyAuthKeyFail received: %s", message
        )

        # TODO: close connection

        msg_ids: List[int] = []

        for msg_id, request_state in self.results.items():
            if isinstance(request_state.request_raw, raw.functions.DestroyAuthKey):
                msg_ids.append(msg_id)

        for msg_id in msg_ids:
            self.set_request_state_result(msg_id=msg_id, value=message.body)

        return None

    async def handle_update(self, message: raw.core.Message[raw.base.Updates]) -> None:
        log.debug("raw.base.Updates received: %s", message)

        self.auth_data.check_update(message.msg_id)
        self.auth_data.recheck_update(message.msg_id)

        await self.client.handle_updates(message.body)

    async def handle_unknown(self, message: raw.core.Message[raw.core.TLObject]) -> None:
        log.debug("Unknown received: %s", message)
        return None

    async def send_pending_acks(self) -> None:
        if len(self.pending_acks) < self.ACKS_THRESHOLD:
            return None

        log.debug("Sending %s acks", len(self.pending_acks))

        pending_acks = self.pending_acks.copy()
        self.pending_acks.clear()

        self.pending_requests.put_nowait(
            RequestState(
                raw.types.MsgsAck(msg_ids=list(pending_acks))
            )
        )

    async def send(self, data: raw.core.TLObject, wait_response: bool = True, timeout: float = WAIT_TIMEOUT):
        request_state = RequestState(request=data)
        self.pending_requests.put_nowait(request_state)
        log.debug("send request_state: %s", request_state)

        if not wait_response:
            log.debug("no wait response")
            return None

        try:
            log.debug("wait response")
            result = await asyncio.wait_for(request_state.future, timeout)
        except asyncio.TimeoutError as exc:
            raise TimeoutError("Request timed out") from exc

        return result

    async def invoke(
        self,
        query: raw.core.TLObject,
        retries: int = MAX_RETRIES,
        timeout: float = WAIT_TIMEOUT,
        sleep_threshold: float = SLEEP_THRESHOLD
    ):
        if isinstance(query, (raw.functions.InvokeWithoutUpdates, raw.functions.InvokeWithTakeout)):
            inner_query = query.query
        else:
            inner_query = query

        query_name = ".".join(inner_query.QUALNAME.split(".")[1:])

        while True:
            try:
                return await self.send(query, timeout=timeout)
            except (FloodWait, FloodPremiumWait) as e:
                amount = e.value

                if amount > sleep_threshold >= 0:
                    raise

                log.warning(
                    '[%s] Waiting for %s seconds before continuing (required by "%s")',
                    self.client.name, amount, query_name
                )

                await asyncio.sleep(amount)
            except (OSError, InternalServerError, ServiceUnavailable) as e:
                if retries == 0:
                    raise e from None

                (log.warning if retries < 2 else log.info)(
                    '[%s] Retrying "%s" due to: %s',
                    Session.MAX_RETRIES - retries + 1,
                    query_name, str(e) or repr(e)
                )

                await asyncio.sleep(0.5)

                return await self.invoke(query, retries - 1, timeout)
