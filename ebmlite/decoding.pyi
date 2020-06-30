from datetime import datetime
from typing import Any, BinaryIO, Optional, Tuple, Union

def decodeIntLength(byte: int) -> Tuple[int, int]: ...
def decodeIDLength(byte: int) -> Tuple[int, int]: ...
def readElementID(stream: BinaryIO) -> Tuple[int, int]: ...
def readElementSize(stream: BinaryIO) -> Tuple[Optional[int], int]: ...
def readUInt(stream: BinaryIO, size: int) -> int: ...
def readInt(stream: BinaryIO, size) -> int: ...
def readFloat(stream: BinaryIO, size: int) -> float: ...
def readString(stream: BinaryIO, size: int) -> bytes: ...
def readUnicode(stream: BinaryIO, size: int) -> str: ...
def readDate(stream: BinaryIO, size: int) -> datetime: ...
