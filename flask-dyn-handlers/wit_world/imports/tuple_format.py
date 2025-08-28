from typing import TypeVar, Generic, Union, Optional, Protocol, Tuple, List, Any, Self
from types import TracebackType
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from ..types import Result, Ok, Err, Some
from ..imports import tarantool_tarantool_types


def default() -> tarantool_tarantool_types.TupleFormat:
    raise NotImplementedError

def new(key_defs: List[tarantool_tarantool_types.KeyDef]) -> tarantool_tarantool_types.TupleFormat:
    """
    Raises: `wit_world.types.Err(wit_world.imports.tarantool_tarantool_types.BoxError)`
    """
    raise NotImplementedError

def ref(tf: tarantool_tarantool_types.TupleFormat) -> None:
    raise NotImplementedError

def unref(tf: tarantool_tarantool_types.TupleFormat) -> None:
    raise NotImplementedError

