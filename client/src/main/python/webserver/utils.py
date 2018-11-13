import asyncio
from twisted.internet.defer import ensureDeferred, Deferred

def as_future(d):
    return d.asFuture(asyncio.get_event_loop())

def as_deferred(f):
    return Deferred.fromFuture(asyncio.ensure_future(f))