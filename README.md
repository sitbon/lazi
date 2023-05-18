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
[139659818784768] LAZY >>>> [139659821474144] django[.VERSION]
[139659818784768] LAZY EXEC [139659821474144] django >>>> 
[139659819833296] FIND INIT django.utils [pyc] [-]  
[139659818783728] CREA LAZY [139659818783808] django.utils .... 
[139659819833296] FIND INIT [django.utils.]django.utils.version [pyc] [-]  
[139659818784448] CREA LAZY [139659818784208] [django.utils.]django.utils.version .... 
[139659818783728] LAZY <<<< [139659818783808] django.utils[.version] = [139659818784448]
[139659818783728] LAZY EXEC [139659818783808] django.utils >>>> 
[139659818783728] EXEC LOAD [139659818783808] django.utils ++++  # This is where the lazy module is fully loaded. 
[139659818784448] LAZY >>>> [139659818784208] [django.utils.]django.utils.version[.get_version]
[139659818784448] LAZY EXEC [139659818784208] [django.utils.]django.utils.version >>>> 
[139659819833296] FIND INIT datetime [pyc] [-] S  # "S" means it's a stdlib module.
[139659818786048] CREA LAZY [139659818786208] datetime .... 
[139659819833296] FIND INIT subprocess [pyc] [-] S 
[139659818786128] CREA LAZY [139659818786448] subprocess .... 
[139659819833296] FIND INIT [django.utils.]django.utils.regex_helper [pyc] [-]  
[139659818786528] CREA LAZY [139659818786368] [django.utils.]django.utils.regex_helper .... 
[139659818786528] LAZY >>>> [139659818786368] [django.utils.]django.utils.regex_helper[._lazy_re_compile]
[139659818786528] LAZY EXEC [139659818786368] [django.utils.]django.utils.regex_helper >>>> 
[139659819833296] FIND INIT [django.utils.]django.utils.functional [pyc] [-]  
[139659818787488] CREA LAZY [139659818787328] [django.utils.]django.utils.functional .... 
[139659818787488] LAZY >>>> [139659818787328] [django.utils.]django.utils.functional[.SimpleLazyObject]
[139659818787488] LAZY EXEC [139659818787328] [django.utils.]django.utils.functional >>>> 
[139659819833296] FIND INIT copy [pyc] [-] S 
[139659818790368] CREA LAZY [139659818791248] copy .... 
[139659818787488] EXEC LOAD [139659818787328] [django.utils.]django.utils.functional ++++ 
[139659818786528] EXEC LOAD [139659818786368] [django.utils.]django.utils.regex_helper ++++ 
[139659818784448] EXEC LOAD [139659818784208] [django.utils.]django.utils.version ++++ 
[139659818784768] EXEC LOAD [139659821474144] django ++++ 
(4, 2, 1, 'final', 0)
>>> exit()
[139659818790368] LAZY DEAD [139659818791248] copy
[139659818787488] LOAD DEAD [139659818787328] [django.utils.]django.utils.functional
[139659818786528] LOAD DEAD [139659818786368] [django.utils.]django.utils.regex_helper
[139659818786128] LAZY DEAD [139659818786448] subprocess
[139659818786048] LAZY DEAD [139659818786208] datetime
[139659818784448] LOAD DEAD [139659818784208] [django.utils.]django.utils.version
[139659818783728] LOAD DEAD [139659818783808] django.utils
[139659818784768] LOAD DEAD [139659821474144] django
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
