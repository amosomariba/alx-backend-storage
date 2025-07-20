#!/usr/bin/env python3
"""Exercise module with Redis decorators"""
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Decorator to count how many times a method is called"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator to store the history of inputs and outputs"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        self._redis.rpush(input_key, str(args))

        output = method(self, *args, **kwargs)

        self._redis.rpush(output_key, str(output))

        return output
    return wrapper


class Cache:
    """Main Cache class using Redis"""

    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Stores data in Redis with a random key"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """Gets data from Redis and optionally applies a conversion function"""
        value = self._redis.get(key)
        if value is None:
            return None
        return fn(value) if fn else value

    def get_str(self, key: str) -> str:
        """Returns string representation of Redis value"""
        return self.get(key, fn=lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """Returns integer representation of Redis value"""
        return self.get(key, fn=int)
