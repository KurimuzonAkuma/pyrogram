import secrets
import time
from typing import Optional


class MsgId:
    last_message_id = 0

    def __new__(cls, server_time: Optional[float] = None) -> int:
        if server_time is None:
            server_time = time.time()

        t = int(server_time * (1 << 32))

        rx = secrets.randbits(32)
        to_xor = rx & ((1 << 22) - 1)
        t ^= to_xor
        result = t & (-4)

        if cls.last_message_id >= result:
            to_mul = ((rx >> 22) & 1023) + 1
            result = cls.last_message_id + 8 * to_mul

        cls.last_message_id = result
        return result
