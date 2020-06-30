from typing import Any, Optional, Union
from xml.etree import ElementTree as ET

from .core import Element, Schema

def toXml(el: Element,
          parent: Optional[ET.Element] = ...,
          offset: bool = ...,
          sizes: bool = ...,
          types: bool = ...,
          ids: bool = ...) -> ET.Element: ...

def xmlElement2ebml(xmlEl: ET.Element,
                    ebmlFile,
                    schema: Schema,
                    sizeLength: Optional[int] = ...,
                    unknown: bool = ...): ...