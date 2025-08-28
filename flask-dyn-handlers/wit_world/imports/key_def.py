from typing import TypeVar, Generic, Union, Optional, Protocol, Tuple, List, Any, Self
from types import TracebackType
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from ..types import Result, Ok, Err, Some
from ..imports import tarantool_tarantool_types


def new(parts: List[tarantool_tarantool_types.KeyPart]) -> tarantool_tarantool_types.KeyDef:
    """
    Raises: `wit_world.types.Err(wit_world.imports.tarantool_tarantool_types.BoxError)`
    """
    raise NotImplementedError

def dup(key_def: tarantool_tarantool_types.KeyDef) -> tarantool_tarantool_types.KeyDef:
    """
    Raises: `wit_world.types.Err(wit_world.imports.tarantool_tarantool_types.BoxError)`
    """
    raise NotImplementedError

def merge(left: tarantool_tarantool_types.KeyDef, right: tarantool_tarantool_types.KeyDef) -> tarantool_tarantool_types.KeyDef:
    """
    Raises: `wit_world.types.Err(wit_world.imports.tarantool_tarantool_types.BoxError)`
    """
    raise NotImplementedError

def delete(key_def: tarantool_tarantool_types.KeyDef) -> None:
    raise NotImplementedError

def dump_parts(key_def: tarantool_tarantool_types.KeyDef) -> List[tarantool_tarantool_types.KeyPart]:
    """
    Raises: `wit_world.types.Err(wit_world.imports.tarantool_tarantool_types.BoxError)`
    """
    raise NotImplementedError

def validate_key(key_def: tarantool_tarantool_types.KeyDef, key: bytes) -> Tuple[bool, int]:
    """
    Raises: `wit_world.types.Err(wit_world.imports.tarantool_tarantool_types.BoxError)`
    """
    raise NotImplementedError

def validate_full_key(key_def: tarantool_tarantool_types.KeyDef, key: bytes) -> Tuple[bool, int]:
    """
    Raises: `wit_world.types.Err(wit_world.imports.tarantool_tarantool_types.BoxError)`
    """
    raise NotImplementedError

def part_count(key_def: tarantool_tarantool_types.KeyDef) -> int:
    """
    Raises: `wit_world.types.Err(wit_world.imports.tarantool_tarantool_types.BoxError)`
    """
    raise NotImplementedError

def extract_key(key_def: tarantool_tarantool_types.KeyDef, tuple: tarantool_tarantool_types.BoxTuple) -> bytes:
    """
    Raises: `wit_world.types.Err(wit_world.imports.tarantool_tarantool_types.BoxError)`
    """
    raise NotImplementedError

def validate_tuple(key_def: tarantool_tarantool_types.KeyDef, tuple: tarantool_tarantool_types.BoxTuple) -> bool:
    raise NotImplementedError

