#!/usr/bin/env python3
"""
This module defines a Cache class to interface with Redis.
It allows storing and retrieving data with type conversion.
"""

from typing import Union, Callable, Optional
import redis
import uuid


class Cache:
    """
    Cache class using Redis as a backend.
    Provides store and typed retrieval methods.
    """

    def __init__(self):
        """
        Initialize the Cache instance and flush the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis under a randomly generated key.
        Returns the key as a string.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis by key and optionally apply a conversion function.
        If the key doesn't exist, returns None.
        """
        value = self._redis.get(key)
        if value is None:
            return None
        return fn(value) if fn is not None else value

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve string data from Redis using UTF-8 decoding.
        Returns None if the key doesn't exist.
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve integer data from Redis by converting bytes to int.
        Returns None if the key doesn't exist.
        """
        return self.get(key, fn=int)
