from typing import Any, Optional

def toXml(el: Any, parent: Optional[Any] = ..., offsets: bool = ..., sizes: bool = ..., types: bool = ..., ids: bool = ...): ...
def xml2ebml(xmlFile: Any, ebmlFile: Any, schema: Any, sizeLength: Optional[Any] = ..., headers: bool = ..., unknown: bool = ...): ...
def loadXml(xmlFile: Any, schema: Any, ebmlFile: Optional[Any] = ...): ...
def pprint(el: Any, values: bool = ..., out: Any = ..., indent: str = ..., _depth: int = ...) -> None: ...
