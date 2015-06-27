from redis import Redis
import cPickle as pickle
try:
    from config import REDIS_CACHE, REDIS_PORT
except:
    print '==============redis config not found============'
    REDIS_CACHE = REDIS_PORT = None
if REDIS_CACHE:
    rcache = Redis(host=REDIS_CACHE, port=REDIS_PORT)
else:
    print '==============cache using local koji instead of redis============'
    import koji
    rcache = koji

def dp(value):
    return pickle.dumps(value)

def ld(value):
    if value is None:
        return None
    else:
        return pickle.loads(value)

def set(key, value, timeout=None):
    v = dp(value)
    if timeout:
        rcache.set(key, v, timeout)
    else:
        rcache.set(key, v)
    return True

def get(key):
    r = rcache.get(key)
    return ld(r)

def delete(key):
    return rcache.delete(key)

