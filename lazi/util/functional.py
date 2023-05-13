from typing import Callable

__all__ = "classproperty", "Singleton", "SingletonMeta", "singlet", "single",


class classproperty(property):
    def __get__(self, instance, cls=None):
        return super().__get__(cls, None)


class Singleton:
    """Non-meta singleton class that supports args and kwds for __init__()."""
    __instances__: dict[type, object] = {}

    @classproperty
    def __instance__(cls: type):
        return cls()

    def __new__(cls, *args, **kwds):
        if (self := cls.__instances__.get(cls, missing := AttributeError())) is missing:
            self = cls.__instances__[cls] = super().__new__(cls, *args, **kwds)
        return self

    @classmethod
    def __delete__(cls):
        del cls.__instances__[cls]

    @classmethod
    def single(cls, clss: type | None = None, /, *args, **kwds) -> object | Callable[[type], object]:
        """Decorator to create a wrapped singleton type."""
        def wrapper(clss_: type):
            class SingletonWrapper(clss_, Singleton):
                __qualname__ = f"SingletonWrapper[{clss_.__qualname__}]"
            return SingletonWrapper(*args, **kwds)
        return wrapper(clss) if clss is not None else wrapper


class SingletonMeta(type, Singleton):
    """Singleton metaclass that does not support args and kwds for __init__()."""

    @property
    def __instance__(cls):
        return cls()

    def __call__(cls):  # Leave out args and kwds to prevent inconsistent calls.
        if (self := cls.__instances__.get(cls, missing := AttributeError())) is missing:
            self = cls.__instances__[cls] = super().__call__()
        return self

    @classmethod
    def single(mcs, cls: type | None = None, /, *args, **kwds) -> object | Callable[[type], object]:
        """Decorator that makes a class a singleton using metaclass."""
        assert not args and not kwds, "SingletonMeta.single() does not support args and kwds."
        return SingletonMeta(cls.__name__, (cls,), dict(cls.__dict__))() if cls is not None else mcs.single


singlet = Singleton.single
single = SingletonMeta.single
