# Lazi: Lazy Imports Everywhere

An easy way to implement and track lazy imports globally.

No external dependencies.

**Requres Python 3.11.**

## Usage:

```shell
poetry add lazi
```
```shell
DEBUG_TRACING=1 python3
```
```pycon
Python 3.11.2
>>> import lazi.auto
[140402520740240] +Finder refs:0 inst:0 sys:5
>>> from django import test
[140402520858096] <get> LAZY django[.test]
[140402518572896] <set> LAZY django.utils[.version] [140402518571056]
[140402518571056] <get> LAZY django.utils.version[.get_version]
[140402518606128] <get> LAZY django.utils.regex_helper[._lazy_re_compile]
[140402518607408] <get> LAZY django.utils.functional[.SimpleLazyObject]
>>> test.TestCase
[140402519121472] <get> LAZY django.test[.TestCase]
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
conf.DEBUG_TRACING = 1
import lazi.auto
# ...
```
