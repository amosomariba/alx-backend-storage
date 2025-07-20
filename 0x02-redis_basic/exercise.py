#!/usr/bin/env python3
"""This module provides a Cache class to interface with Redis."""

import redis
import uuid
from typing import Union


class Cache:
    """Cache class for storing data in Redis with a random key."""

    def __init__(self):
        """Initialize the Redis client and flush the database."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a randomly generated key.

        Args:
            data: The data to store, can be str, bytes, int or float.

        Returns:
            The key under which the data is stored.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
