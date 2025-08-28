from typing import TypeVar, Generic, Union, Optional, Protocol, Tuple, List, Any, Self
from types import TracebackType
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from ..types import Result, Ok, Err, Some
from ..imports import tarantool_tarantool_types

class TupleIterator:
    
    @classmethod
    def new_tuple_iterator(cls, tuple: tarantool_tarantool_types.BoxTuple) -> Self:
        """
        Raises: `wit_world.types.Err(wit_world.imports.tarantool_tarantool_types.BoxError)`
        """
        raise NotImplementedError
    def position(self) -> int:
        raise NotImplementedError
    def rewind(self) -> None:
        raise NotImplementedError
    def seek(self, pos: int) -> tarantool_tarantool_types.TupleField:
        """
        Raises: `wit_world.types.Err(wit_world.imports.tarantool_tarantool_types.BoxError)`
        """
        raise NotImplementedError
    def next(self) -> tarantool_tarantool_types.TupleField:
        """
        Raises: `wit_world.types.Err(wit_world.imports.tarantool_tarantool_types.BoxError)`
        """
        raise NotImplementedError
    def __enter__(self) -> Self:
        """Returns self"""
        return self
                                
    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None) -> bool | None:
        """
        Release this resource.
        """
        raise NotImplementedError



def new(data: bytes) -> tarantool_tarantool_types.BoxTuple:
    """
    Raises: `wit_world.types.Err(wit_world.imports.tarantool_tarantool_types.BoxError)`
    """
    raise NotImplementedError

def ref(t: tarantool_tarantool_types.BoxTuple) -> int:
    raise NotImplementedError

def unref(t: tarantool_tarantool_types.BoxTuple) -> None:
    raise NotImplementedError

def field_count(t: tarantool_tarantool_types.BoxTuple) -> int:
    raise NotImplementedError

def bsize(t: tarantool_tarantool_types.BoxTuple) -> int:
    raise NotImplementedError

def to_buf(t: tarantool_tarantool_types.BoxTuple) -> bytes:
    """
    Raises: `wit_world.types.Err(wit_world.imports.tarantool_tarantool_types.BoxError)`
    """
    raise NotImplementedError

def format(t: tarantool_tarantool_types.BoxTuple) -> tarantool_tarantool_types.TupleFormat:
    raise NotImplementedError

def field(t: tarantool_tarantool_types.BoxTuple, idx: int) -> tarantool_tarantool_types.TupleField:
    """
    Raises: `wit_world.types.Err(wit_world.imports.tarantool_tarantool_types.BoxError)`
    """
    raise NotImplementedError

def field_by_path(t: tarantool_tarantool_types.BoxTuple, path: str, index_base: int) -> tarantool_tarantool_types.TupleField:
    """
    Raises: `wit_world.types.Err(wit_world.imports.tarantool_tarantool_types.BoxError)`
    """
    raise NotImplementedError

def update(t: tarantool_tarantool_types.BoxTuple, expr: bytes) -> tarantool_tarantool_types.BoxTuple:
    """
    Raises: `wit_world.types.Err(wit_world.imports.tarantool_tarantool_types.BoxError)`
    """
    raise NotImplementedError

def upsert(t: tarantool_tarantool_types.BoxTuple, expr: bytes) -> tarantool_tarantool_types.BoxTuple:
    """
    Raises: `wit_world.types.Err(wit_world.imports.tarantool_tarantool_types.BoxError)`
    """
    raise NotImplementedError

def validate(t: tarantool_tarantool_types.BoxTuple, format: tarantool_tarantool_types.TupleFormat) -> bool:
    raise NotImplementedError

def compare(key_def: tarantool_tarantool_types.KeyDef, left: tarantool_tarantool_types.BoxTuple, right: tarantool_tarantool_types.BoxTuple) -> int:
    raise NotImplementedError

def compare_with_key(tuple: tarantool_tarantool_types.BoxTuple, key: bytes, key_def: tarantool_tarantool_types.KeyDef) -> int:
    raise NotImplementedError

