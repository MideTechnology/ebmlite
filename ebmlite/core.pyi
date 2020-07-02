from typing import (Any,
                    BinaryIO,
                    ClassVar,
                    Dict,
                    List,
                    Optional,
                    Text,
                    Type,
                    Union)

SCHEMA_PATH: List[str] = ...
SCHEMATA: Dict[Union[str, bytes, bytearray], Any] = ...


class Element:

    id: Any
    name: Optional[Text]

    schema: ClassVar[Optional[Schema]]
    dtype: ClassVar[Optional[Type]]

    def parse(self, stream: BinaryIO, size: int) -> Any: ...

    def __init__(self,
                 stream: Optional[BinaryIO] = ...,
                 offset: int = ...,
                 size: int = ...,
                 payloadOffset: int = ...): ...

    def getRaw(self) -> Union[bytes, bytearray]: ...


class Schema(object): ...


def loadSchema(filename: Union[str, bytes, bytearray],
               reload: bool = ...,
               **kwargs) -> Schema: ...
