from . import conf  # noqa: Require relative import to work.

__all__ = conf.__all__

conf.clear()  # noqa: Clear the conf cache.
conf.get()  # noqa: Force the conf cache to reload.

__getattr__ = lambda attr: getattr(conf, attr)  # Provide the conf cache as the module's attributes.
