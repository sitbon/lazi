from lazi.conf import conf

__all__ = "trace",


if conf.DEBUG_TRACING:
    import sys

    def trace(*args, **kwds):
        kwds.setdefault("file", sys.stderr)
        return print(*args, **kwds)

else:
    def trace(*args, **kwds):
        pass
