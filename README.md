# Lazi: Lazy Imports Everywhere

An easy way to implement and track lazy imports globally.

No external dependencies.

**Requres Python 3.11.**

## Usage:

```shell
poetry add lazi
```
```shell
TRACE=1 python3
```
```pycon
>>> import lazi.auto
>>> import django
>>> django.VERSION
[140071460506656] LAZY >>>> [140071460989312] django[.VERSION]  # Lazy loaded `django` due to `VERSION` attr access.
[140071459492368] LAZY <<<< [140071459492448] django.utils[.version] = [140071459492928]
[140071459492928] LAZY >>>> [140071459492848] [django.utils.]django.utils.version[.get_version]
[140071459495168] LAZY >>>> [140071459495008] [django.utils.]django.utils.regex_helper[._lazy_re_compile]
[140071459496048] LAZY >>>> [140071459495888] [django.utils.]django.utils.functional[.SimpleLazyObject]
(4, 2, 1, 'final', 0)
>>> _
```


### Use for specific modules:

```pycon
>>> from lazi.core import lazi
>>> with lazi:
...   import django
...   print(django.VERSION)
... 
(4, 2, 1, 'final', 0)
>>> _
```

Or:

```pycon
>>> from lazi.core import lazy
>>> django = lazy("django")
>>> django.VERSION
(4, 2, 1, 'final', 0)
>>> _
```

## Configuration

The `lazi.conf` namespace package contains configuration modules
that get autoloaded (in import order) by `lazi.conf.conf`.
It is fully decoupled from the rest of the codebase.

As a result, it's possible configure Lazi by creating `lazi.conf`
modules in your project (within the `lazi.conf` namespace package),
and use conf modules provided by other packages.

Configuration is not yet controllable via environment variables,
but this is planned for the future. Update: Supported for DEBUG_TRACING.

It's also possible to manually change the configuration at runtime,
with the caveat that some variables may have already been used by
`lazi.core`. To avoid this, configure Lazi before importing it:

```python
from lazi.conf import conf

conf.TRACE = 1
import lazi.auto
# ...
```
