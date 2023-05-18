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
Python 3.11.2
>>> import lazi.auto
>>> from django import test
[139840712693360] LAZY >>>> [139840715383056] django[.test]
[139840712694640] LAZY <<<< [139840712694240] django.utils[.version] = [139840712695040]
[139840712695040] LAZY >>>> [139840712694880] [django.utils.]django.utils.version[.get_version]
[139840712696720] LAZY >>>> [139840712696000] [django.utils.]django.utils.regex_helper[._lazy_re_compile]
[139840712697680] LAZY >>>> [139840712697280] [django.utils.]django.utils.functional[.SimpleLazyObject]
>>> test.TestCase
# ... A lot of output ...
<class 'django.test.testcases.TestCase'>
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
