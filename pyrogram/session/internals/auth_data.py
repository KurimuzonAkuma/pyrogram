import os
import time
from bisect import bisect_left
from hashlib import sha1
from typing import (
    List,
    TypeVar,
)

from pyrogram.errors import SecurityCheckMismatch
from pyrogram.raw.core import (
    FutureSalt,
    Message,
    TLObject,
)
from .msg_id import MsgId


class MessageIdDuplicateChecker:
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.saved_message_ids: List[int] = []

    def check(self, message_id: int) -> None:
        if len(self.saved_message_ids) == self.max_size * 2:
            self.saved_message_ids = self.saved_message_ids[self.max_size:]

        if not self.saved_message_ids or message_id > self.saved_message_ids[-1]:
            self.saved_message_ids.append(message_id)
            return None

        if len(self.saved_message_ids) >= self.max_size and message_id < self.saved_message_ids[0]:
            raise SecurityCheckMismatch("The msg_id is lower than all the stored values", fatal=True)

        pos = bisect_left(self.saved_message_ids, message_id)
        if pos < len(self.saved_message_ids) and self.saved_message_ids[pos] == message_id:
            raise SecurityCheckMismatch("The msg_id is equal to any of the stored values")

        self.saved_message_ids.insert(pos, message_id)
        return None


BodyT = TypeVar("BodyT", bound=TLObject)


def get_auth_key_id(auth_key: bytes) -> bytes:
    auth_key_sha1 = sha1(auth_key).digest()
    return auth_key_sha1[-8:]


class AuthData:
    def __init__(
        self,
        main_auth_key: bytes,
    ):
        self.server_salt = FutureSalt(
            valid_since=0,
            valid_until=0,
            salt=0
        )
        self.future_salts: List[FutureSalt] = []

        self.server_time_difference = 0.0
        self.server_time_difference_updated = False

        self.seq_no = 0

        self.main_auth_key = main_auth_key
        self.main_auth_key_id = get_auth_key_id(self.main_auth_key)

        self.session_id = os.urandom(8)

        self.duplicate_checker = MessageIdDuplicateChecker(1_000)
        self.updates_duplicate_checker = MessageIdDuplicateChecker(1_000)
        self.updates_duplicate_rechecker = MessageIdDuplicateChecker(100)

    def check_packet(self, message_id: int, now: float) -> None:
        self.duplicate_checker.check(message_id)

        self.update_server_time_difference(
            diff=(message_id >> 32) - now
        )

        if not self.server_time_difference_updated:
            return None

        if not self.is_valid_inbound_msg_id(
            message_id=message_id, now=now
        ):
            raise SecurityCheckMismatch("The msg_id is equal to any of the stored values")

        return None

    def check_update(self, message_id: int) -> None:
        self.updates_duplicate_checker.check(message_id)

    def recheck_update(self, message_id: int) -> None:
        self.updates_duplicate_rechecker.check(message_id)

    def update_server_time_difference(self, diff: float) -> bool:
        if not self.server_time_difference_updated:
            self.server_time_difference = diff
            self.server_time_difference_updated = True
        elif self.server_time_difference + 1e-4 < diff:
            self.server_time_difference = diff
        else:
            return False

    def reset_server_time_difference(self, diff: float) -> None:
        self.server_time_difference = diff
        self.server_time_difference_updated = False

    def set_future_salts(self, future_salts: List[FutureSalt], now: float) -> None:
        if len(future_salts) < 1:
            return None

        self.future_salts = future_salts
        self.future_salts.sort(key=lambda future_salt: future_salt.valid_since)
        self.update_salt(now)

    def next_message_id(self, now: float) -> int:
        server_time = self.get_server_time(now)
        return MsgId(server_time)

    def is_valid_inbound_msg_id(self, message_id: int, now: float) -> bool:
        server_time = self.get_server_time(now)
        id_time = message_id / (1 << 32)
        return server_time - 300 < id_time < server_time + 30

    def update_salt(self, now: float) -> None:
        server_time = self.get_server_time(now)

        while self.future_salts and self.future_salts[-1].valid_since < server_time:
            self.server_salt = self.future_salts.pop()

        return None

    def get_client_time(self) -> float:
        return time.time()

    def get_server_time(self, now: float) -> float:
        return now + self.server_time_difference

    def set_server_salt(self, salt: int, now: float) -> None:
        self.server_salt.salt = salt

        server_time = self.get_server_time(now)
        self.server_salt.valid_since = server_time
        self.server_salt.valid_until = server_time + 60 * 10

        self.future_salts.clear()
        return None

    def is_server_salt_valid(self, now: float) -> bool:
        return self.server_salt.valid_since > self.get_server_time(now) + 60

    def has_salt(self, now: float) -> bool:
        self.update_salt(now)
        return self.is_server_salt_valid(now)

    def need_future_salts(self, now: float) -> bool:
        self.update_salt(now)

        if len(self.future_salts) < 1:
            return True

        return not self.is_server_salt_valid(now)

    def next_seq_no(self, is_content_related: bool) -> int:
        result = self.seq_no
        if is_content_related:
            result |= 1
            self.seq_no += 2

        return result

    def msg_factory(self, body: BodyT, is_content_related: bool, now: float) -> Message[BodyT]:
        message_id = self.next_message_id(now)
        seq_no = self.next_seq_no(is_content_related)
        return Message(
            body,
            message_id,
            seq_no,
            len(body)
        )

    def get_server_salt(self, now: float) -> int:
        self.update_salt(now)
        return self.server_salt.salt
