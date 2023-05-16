from contextlib import contextmanager
import logging

from lazi.conf import conf

__all__ = "trace", "traced", "log", "track"

PRETTY = None


if __debug__ and conf.DEBUG_TRACING:

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(message)s",
    )

    traced = lambda at, /, *args, **kwds: logging.debug(*args, **kwds) if conf.DEBUG_TRACING > at else None  # noqa
    trace = lambda *args, **kwds: traced(0, *args, **kwds)

else:
    traced = lambda at, /, *args, **kwds: None
    trace = lambda *args, **kwds: None
    init_pretty = lambda: None

log = logging.debug


@contextmanager
def track(msg: str):
    log(f">>> {msg} ...")
    try:
        yield
    except Exception as e:
        log(_log := f"!!! {msg} >>> {type(e).__name__}: {e}")
        raise
    else:
        log(f"^^^ {msg} ^^^")
