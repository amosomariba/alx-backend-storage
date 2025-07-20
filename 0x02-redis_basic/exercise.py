#!/usr/bin/env python3
"""Exercise module with replay feature"""
import redis
import uuid
from typing import Callable, Union, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Decorator that counts how many times a method is called"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator to store the history of inputs and outputs for a function"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        self._redis.rpush(f"{key}:inputs", str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(f"{key}:outputs", str(result))
        return result
    return wrapper


def replay(method: Callable):
    """Displays the call history of a Cache method"""
    redis_instance = method.__self__._redis
    key = method.__qualname__

    inputs = redis_instance.lrange(f"{key}:inputs", 0, -1)
    outputs = redis_instance.lrange(f"{key}:outputs", 0, -1)

    print(f"{key} was called {len(inputs)} times:")
    for input_args, output in zip(inputs, outputs):
        args_str = input_args.decode()
        result_str = output.decode()
        print(f"{key}(*{args_str}) -> {result_str}")



class Cache:
    """Cache class that uses Redis"""
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store the data in Redis and return the key"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """Retrieve data from Redis, optionally transforming it"""
        data = self._redis.get(key)
        if data is None:
            return None
        return fn(data) if fn else data

    def get_str(self, key: str) -> str:
        """Get a string from Redis"""
        return self.get(key, lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """Get an int from Redis"""
        return self.get(key, int)
