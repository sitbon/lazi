from . import conf  # noqa: Require relative import to work.

conf.clear()  # noqa: Clear the conf cache.
conf.get()  # noqa: Force the conf cache to reload.

__getattr__ = conf.__getattr__  # noqa: Provide the conf cache as the module's attributes.
