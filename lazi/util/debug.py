from lazi.conf import conf

__all__ = "trace", "traced"


if __debug__ and conf.DEBUG_TRACING:
    import sys

    def trace(*args, **kwds):
        kwds.setdefault("file", sys.stderr)
        return print(*args, **kwds)

    def traced(at: int, /, *args, **kwds):
        if conf.DEBUG_TRACING > at:
            return trace(*args, **kwds)

else:
    def trace(*args, **kwds):
        pass

    def traced(at: int, /, *args, **kwds):
        pass
