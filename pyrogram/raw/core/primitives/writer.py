import struct
from io import BytesIO


class BinaryWriter:
    # TODO: cythonize

    def __init__(self):
        self.buffer = BytesIO()

    def _write_int(self, value: int, size: int, signed: bool) -> None:
        self.buffer.write(int.to_bytes(value, length=size, byteorder="little", signed=signed))
        return None

    def write_int(self, value: int, signed: bool = True) -> None:
        self._write_int(value=value, size=4, signed=signed)
        return None

    def write_long(self, value: int, signed: bool = True) -> None:
        self._write_int(value=value, size=8, signed=signed)
        return None


    def write_int_128(self, value: int, signed: bool = True) -> None:
        self._write_int(value=value, size=16, signed=signed)
        return None

    def write_int_256(self, value: int, signed: bool = True) -> None:
        self._write_int(value=value, size=32, signed=signed)
        return None

    def write_double(self, value: float) -> None:
        self.buffer.write(struct.pack("d", value)) # TODO: pack double without struct
        return None

    def write_bool(self, value: bool) -> None:
        if value is True:
            self.write_int(value=0x997275B5, signed=False)
        elif value is False:
            self.write_int(value=0xBC799737, signed=False)
        else:
            raise ValueError("Boolean value expected")

    def write_bytes(self, value: bytes) -> None:
        length = len(value)

        if length <= 253:
            self._write_int(value=length, size=1, signed=False)
            self.buffer.write(value)
            self.buffer.write(bytes(-(length + 1) % 4))
        else:
            self.buffer.write(b'\xfe')
            self._write_int(value=length, size=3, signed=False)
            self.buffer.write(value)
            self.buffer.write(bytes(-length % 4))

        return None

    def write_string(self, value: str) -> None:
        self.write_bytes(value.encode("utf-8"))
        return None

    def getvalue(self) -> bytes:
        return self.buffer.getvalue()

    def __enter__(self) -> "BinaryWriter":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.buffer.close()
        return None
