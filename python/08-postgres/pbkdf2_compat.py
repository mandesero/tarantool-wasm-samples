"""Fallback for componentize Python builds without hashlib.pbkdf2_hmac."""

import hashlib
import hmac


def pbkdf2_hmac(
    hash_name: str,
    password: bytes,
    salt: bytes,
    iterations: int,
    dklen: int | None = None,
) -> bytes:
    if iterations < 1:
        raise ValueError("iterations must be positive")
    digest_size = hashlib.new(hash_name).digest_size
    if dklen is None:
        dklen = digest_size
    if dklen < 0:
        raise ValueError("key length must not be negative")
    block_count = (dklen + digest_size - 1) // digest_size
    if block_count > 0xFFFFFFFF:
        raise OverflowError("derived key is too long")

    derived = bytearray()
    for block_index in range(1, block_count + 1):
        value = hmac.new(
            password,
            salt + block_index.to_bytes(4, "big"),
            hash_name,
        ).digest()
        accumulator = bytearray(value)
        for _ in range(iterations - 1):
            value = hmac.new(password, value, hash_name).digest()
            for index, byte in enumerate(value):
                accumulator[index] ^= byte
        derived.extend(accumulator)
    return bytes(derived[:dklen])


def install() -> None:
    if not hasattr(hashlib, "pbkdf2_hmac"):
        hashlib.pbkdf2_hmac = pbkdf2_hmac
