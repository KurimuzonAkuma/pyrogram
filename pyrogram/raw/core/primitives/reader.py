import struct
from io import BytesIO


class BinaryReader:
    def __init__(self, value: bytes):
        self.buffer = BytesIO(value)

    def read_int(self, signed: bool = True) -> int:
        return int.from_bytes(self.buffer.read(4), "little", signed=signed)

    def read_long(self, signed: bool = True) -> int:
        return int.from_bytes(self.buffer.read(8), "little", signed=signed)

    def read_int_128(self, signed: bool = True) -> int:
        return int.from_bytes(self.buffer.read(16), "little", signed=signed)

    def read_int_256(self, signed: bool = True) -> int:
        return int.from_bytes(self.buffer.read(32), "little", signed=signed)

    def read_double(self) -> float:
        value = self.buffer.read(8)
        (double, ) = struct.unpack("d", value)
        return double

    def read_bool(self) -> bool:
        constructor_id = self.read_int(signed=False)

        if constructor_id == 0x997275B5:
            return True
        elif constructor_id == 0xBC799737:
            return False
        else:
            raise ValueError("Unexcepted constructor_id")

    def read_bytes(self) -> bytes:
        length = int.from_bytes(self.buffer.read(1), "little")

        if length <= 253:
            x = self.buffer.read(length)
            self.buffer.read(-(length + 1) % 4)
        else:
            length = int.from_bytes(self.buffer.read(3), "little")
            x = self.buffer.read(length)
            self.buffer.read(-length % 4)

        return x

    def read_string(self) -> str:
        value = self.read_bytes()
        return value.decode("utf-8")

    def __enter__(self) -> "BinaryReader":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.buffer.close()
        return None
