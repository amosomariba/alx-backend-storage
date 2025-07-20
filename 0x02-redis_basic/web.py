#!/usr/bin/env python3
"""Web cache and tracker using requests and redis"""

import redis
import requests
from functools import wraps
from typing import Callable

# Redis connection
r = redis.Redis()


def track_access(func: Callable) -> Callable:
    """Decorator to track URL access count and cache results with expiration"""
    @wraps(func)
    def wrapper(url: str) -> str:
        # Increment the access counter
        r.incr(f"count:{url}")

        # Check if cached version exists
        cached_page = r.get(f"cached:{url}")
        if cached_page:
            return cached_page.decode('utf-8')

        # If not cached, fetch the content
        content = func(url)

        # Store in cache with 10s expiration
        r.setex(f"cached:{url}", 10, content)

        return content
    return wrapper


@track_access
def get_page(url: str) -> str:
    """Returns the HTML content of the given URL"""
    response = requests.get(url)
    return response.text
