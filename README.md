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
[140071460506656] LAZY >>>> [140071460989312] django[.VERSION]  # Lazy loaded django due to VERSION attr access.
[140071459492368] LAZY <<<< [140071459492448] django.utils[.version] = [140071459492928] # Ditto for django.utils setattr.
[140071459492928] LAZY >>>> [140071459492848] [django.utils.]django.utils.version[.get_version]
[140071459495168] LAZY >>>> [140071459495008] [django.utils.]django.utils.regex_helper[._lazy_re_compile]
[140071459496048] LAZY >>>> [140071459495888] [django.utils.]django.utils.functional[.SimpleLazyObject]
(4, 2, 1, 'final', 0)
>>> _
```

And with `TRACE=2`:

```pycon
>>> import lazi.auto
>>> import django
[139659819833296] FIND INIT django [pyc] [-]  
[139659818784768] CREA LAZY [139659821474144] django ....  # This is where the lazy module is set up.
>>> django.VERSION
[140379497174160] LAZY >>>> [140379499847872] django VERSION
[140379497174160] LAZY EXEC [140379499847872] django >>>> 
[140379498707216] FIND pyc  django.utils
[140379497174640] CREA LAZY [140379497174720] django.utils .... 
[140379498707216] FIND pyc  django.utils!version
[140379497175200] CREA LAZY [140379497175600] django.utils|version .... 
[140379497174640] LAZY <<<< [140379497174720] django.utils version = [140379497175200]
[140379497174640] LAZY EXEC [140379497174720] django.utils >>>> 
[140379497174640] EXEC LOAD [140379497174720] django.utils ++++  # This is where the lazy module is fully loaded. 
[140379497175200] LAZY >>>> [140379497175600] django.utils|version get_version
[140379497175200] LAZY EXEC [140379497175600] django.utils|version >>>> 
[140379498707216] FIND pycS datetime  # "S" means it's a stdlib module.
[140379497177040] CREA LAZY [140379497177120] datetime .... 
[140379498707216] FIND pycS subprocess
[140379497177280] CREA LAZY [140379497177360] subprocess .... 
[140379498707216] FIND pyc  django.utils|regex_helper
[140379497177200] CREA LAZY [140379497177440] django.utils|regex_helper .... 
[140379497177200] LAZY >>>> [140379497177440] django.utils|regex_helper _lazy_re_compile
[140379497177200] LAZY EXEC [140379497177440] django.utils|regex_helper >>>> 
[140379498707216] FIND pyc  django.utils|functional
[140379497178240] CREA LAZY [140379497178480] django.utils|functional .... 
[140379497178240] LAZY >>>> [140379497178480] django.utils|functional SimpleLazyObject
[140379497178240] LAZY EXEC [140379497178480] django.utils|functional >>>> 
[140379498707216] FIND pycS copy
[140379497182240] CREA LAZY [140379497183440] copy .... 
[140379497178240] EXEC LOAD [140379497178480] django.utils|functional ++++ 
[140379497177200] EXEC LOAD [140379497177440] django.utils|regex_helper ++++ 
[140379497175200] EXEC LOAD [140379497175600] django.utils|version ++++ 
[140379497174160] EXEC LOAD [140379499847872] django ++++ 
(4, 2, 1, 'final', 0)
>>> exit()
[140379497182240] LAZY DEAD [140379497183440] copy
[140379497178240] LOAD DEAD [140379497178480] django.utils|functional
[140379497177200] LOAD DEAD [140379497177440] django.utils|regex_helper
[140379497177280] LAZY DEAD [140379497177360] subprocess
[140379497177040] LAZY DEAD [140379497177120] datetime
[140379497175200] LOAD DEAD [140379497175600] django.utils|version
[140379497174640] LOAD DEAD [140379497174720] django.utils
[140379497174160] LOAD DEAD [140379499847872] django
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
