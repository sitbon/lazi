from typing import Callable

__all__ = "classproperty",


class classproperty(property):
    def __get__(self, instance, cls=None):
        return super().__get__(cls, None)
