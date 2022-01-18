from decorator import decorator
from time import time


from datetime import datetime, timedelta
import functools

def cache(expiry_time=0, _cache=None, num_args=None, cache_empty=False):

    def _memoize_with_expiry(func, *args, **kw):
        # Determine what cache to use - the supplied one, or one we create inside the
        # wrapped function.
        if _cache is None and not hasattr(func, '_cache'):
            func._cache = {}
        cache = _cache or func._cache

        mem_args = args[:num_args]
        # frozenset is used to ensure hashability
        if kw:
            key = mem_args, frozenset(kw.items())
        else:
            key = mem_args
        if key in cache:
            result, timestamp = cache[key]
            # Check the age.
            age = time() - timestamp
            if not expiry_time:
                return result
            if age < expiry_time:
                return result
        result = func(*args, **kw)

        # Check for empty response,
        # allowing it to cache or not
        if not result and not cache_empty:
            return result
        else:
            cache[key] = (result, time())
            return result

    return decorator(_memoize_with_expiry)



def timed_cache(**timedelta_kwargs):
    def _wrapper(f):
        update_delta = timedelta(**timedelta_kwargs)
        next_update = datetime.utcnow() + update_delta
        # Apply @lru_cache to f with no cache size limit
        f = functools.lru_cache(None)(f)

        @functools.wraps(f)
        def _wrapped(*args, **kwargs):
            nonlocal next_update
            now = datetime.utcnow()
            if now >= next_update:
                f.cache_clear()
                next_update = now + update_delta
            return f(*args, **kwargs)

        return _wrapped

    return _wrapper