#!/usr/bin/env python3
"""Web cache and access count tracker"""

import redis
import requests
from functools import wraps
from typing import Callable

# Redis client instance
r = redis.Redis()


def track_access_and_cache(func: Callable) -> Callable:
    """Decorator: Tracks call count and caches HTML content for 10 seconds"""
    @wraps(func)
    def wrapper(url: str) -> str:
        # Increment access count
        r.incr(f"count:{url}")

        # Check if cached response exists
        cached = r.get(f"cached:{url}")
        if cached:
            return cached.decode('utf-8')

        # Fetch, cache for 10 seconds
        html = func(url)
        r.setex(f"cached:{url}", 10, html)
        return html

    return wrapper


@track_access_and_cache
def get_page(url: str) -> str:
    """Fetch HTML content from a URL"""
    response = requests.get(url)
    return response.text
