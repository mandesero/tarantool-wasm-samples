from typing import TypeVar, Generic, Union, Optional, Protocol, Tuple, List, Any, Self
from types import TracebackType
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from .types import Result, Ok, Err, Some



@dataclass
class VArg_Name:
    value: str


@dataclass
class VArg_Number:
    value: int


VArg = Union[VArg_Name, VArg_Number]



@dataclass
class VResponce_None_:
    pass


@dataclass
class VResponce_Str:
    value: str


@dataclass
class VResponce_Num:
    value: int


VResponce = Union[VResponce_None_, VResponce_Str, VResponce_Num]


@dataclass
class Responce:
    status: str
    value: VResponce
    error: str


class WitWorld(Protocol):

    @abstractmethod
    def call(self, address: str, service: str, method: str, args: VArg) -> Responce:
        raise NotImplementedError

