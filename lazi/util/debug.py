from contextlib import contextmanager
import logging

from lazi.conf import conf

__all__ = "trace", "traced", "info", "track"


info = logging.info
exception = logging.exception

TRACE = conf.TRACE

if __debug__ and TRACE:

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(message)s",
    )

    traced = lambda at, /, *args, **kwds: logging.debug(*args, **kwds) if TRACE > at else None  # noqa
    trace = lambda *args, **kwds: traced(0, *args, **kwds)

else:
    traced = lambda at, /, *args, **kwds: None
    trace = lambda *args, **kwds: None


@contextmanager
def track(msg: str, log=info, exc=info):
    log(f"... {msg} ...")
    try:
        yield
    except Exception as e:
        exc(_log := f"!!! {msg} !!! {type(e).__name__}: {e}")
        raise
    else:
        log(f"^^^ {msg} ^^^")
