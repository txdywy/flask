import time
import threading
import functools

KOJI_LOACL_CACHE_DICT = {}
KOJI_FUNC_LOCK = threading.Lock()
"""
KOJI_LOACL_CACHE_DICT = {key: [ts_expire, value], ... etc.}
"""

def racing(func):
    @functools.wraps(func)
    def foo(*args, **kwargs):
        with KOJI_FUNC_LOCK:
            return func(*args, **kwargs)
    return foo

def keystd(func):
    @functools.wraps(func)
    def foo(*args, **kwargs):
        if len(args) > 0:
            args = list(args)
            args[0] = str(args[0])
            args = tuple(args)
        if 'key' in kwargs:
            kwargs['key'] = str(kwargs['key'])
        return func(*args, **kwargs)
    return foo

@racing
@keystd
def set(key, value, timeout=None):
    if timeout:
        ts_expire = time.time() + timeout
    else:
        ts_expire = None
    KOJI_LOACL_CACHE_DICT[key] = [ts_expire, value]
    return True

@keystd
def get(key):
    v = KOJI_LOACL_CACHE_DICT.get(key)
    if v:
        ts_expire = v[0]
        if not ts_expire or ts_expire > time.time():
            v = v[1]
        else:
            v = None
            del KOJI_LOACL_CACHE_DICT[key]
    return v

@racing
@keystd
def delete(key):
    if key in KOJI_LOACL_CACHE_DICT:
        del KOJI_LOACL_CACHE_DICT[key]
        return True
    else:
        return None

def keys():
    return KOJI_LOACL_CACHE_DICT.keys()

@racing
@keystd
def ttl(key):
    v = KOJI_LOACL_CACHE_DICT.get(key)
    if v:
        ts_expire = v[0]
        if ts_expire:
            r = ts_expire - time.time()
            if r > 0:
                return r
            else:
                del KOJI_LOACL_CACHE_DICT[key]
    return None
    
