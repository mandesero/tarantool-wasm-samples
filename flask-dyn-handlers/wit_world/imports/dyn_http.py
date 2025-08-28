from typing import TypeVar, Generic, Union, Optional, Protocol, Tuple, List, Any, Self
from types import TracebackType
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from ..types import Result, Ok, Err, Some


@dataclass
class Header:
    name: str
    value: str

@dataclass
class Param:
    name: str
    value: str

@dataclass
class UriComponents:
    scheme: str
    host: str
    port: int
    path: str
    query: str
    query_args: List[Param]
    fragment: str

@dataclass
class Request:
    method: str
    target: str
    http_version: str
    uri: UriComponents
    headers: List[Header]
    body: Optional[bytes]
    body_done: bool
    done: bool

@dataclass
class Response:
    status: int
    reason: str
    headers: List[Header]
    trailers: List[Header]
    body: Optional[bytes]


def handler(name: str, req: Request) -> Response:
    raise NotImplementedError

