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
[140016542011360] LAZY >>>> [140016544686432] django VERSION  # Lazy loaded django due to VERSION attr access.
[140016542012960] LAZY <<<< [140016542013120] django.utils version = [140016542013520]  # Ditto for django.utils setattr.
[140016542013520] LAZY >>>> [140016542013920] django.utils|version get_version
[140016542015600] LAZY >>>> [140016542015840] django.utils|regex_helper _lazy_re_compile
[140016542016640] LAZY >>>> [140016542016880] django.utils|functional SimpleLazyObject
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

## Tricky Situations

### Expected global state is not there.

This is the most common issue when using `lazi.auto`, and can be difficult to debug.

Fortunately, Lazi will show some useful tracebacks including the original exception before
it was transformed into an `ImportError` (by CPython, thowing away the original traceback).

Example:
```pycon
>>> import lazi.auto
>>> import pandas.core.nanops
[140343991111888] EXEC DEAD [140343991111968] dateutil.tz|win !!!! six.moves
[140343977781872] EXEC DEAD [140343977777872] pandas.core|nanops !!!! 
                  !!!! OptionError: No such keys(s): 'compute.use_bottleneck'
Traceback (most recent call last):
  File "/home/jq/pr/lazi/lazi/core/loader.py", line 107, in exec_module
    self.loader.exec_module(target if target is not None else module)
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/.../pandas/core/nanops.py", line 74, in <module>
    set_use_bottleneck(get_option("compute.use_bottleneck"))
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/.../pandas/_config/config.py", line 261, in __call__
    return self.__func__(*args, **kwds)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/.../pandas/_config/config.py", line 135, in _get_option
    key = _get_single_key(pat, silent)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/.../pandas/_config/config.py", line 121, in _get_single_key
    raise OptionError(f"No such keys(s): {repr(pat)}")
pandas._config.config.OptionError: No such keys(s): 'compute.use_bottleneck'
[140343976684704] EXEC DEAD [140343976684864] pandas.core.arrays.sparse|array !!!! pandas.core.nanops
[140343976682224] EXEC DEAD [140343976682464] pandas.core.arrays.sparse|accessor !!!! pandas.core.nanops
[140343976681984] EXEC DEAD [140343976681744] pandas.core.arrays.sparse !!!! pandas.core.nanops
[140343980659536] EXEC DEAD [140343980659456] pandas.core.arrays !!!! pandas.core.nanops
[140343980335376] EXEC DEAD [140343980335456] pandas.core|api !!!! pandas.core.nanops
[140345351918096] EXEC DEAD [140345351918496] pandas !!!! pandas.core.nanops
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/jq/pr/lazi/lazi/core/module.py", line 102, in __setattr__
    spec.loader.exec_module(self, True)
  File "/home/jq/pr/lazi/lazi/core/loader.py", line 107, in exec_module
    self.loader.exec_module(target if target is not None else module)
  File "/<site-packages>/pandas/__init__.py", line 48, in <module>
    from pandas.core.api import (
  File "/home/jq/pr/lazi/lazi/core/module.py", line 75, in __getattribute__
    spec.loader.exec_module(self, True)
  File "/home/jq/pr/lazi/lazi/core/loader.py", line 107, in exec_module
    self.loader.exec_module(target if target is not None else module)
  File "/<site-packages>/pandas/core/api.py", line 27, in <module>
    from pandas.core.arrays import Categorical
  File "/home/jq/pr/lazi/lazi/core/module.py", line 75, in __getattribute__
    spec.loader.exec_module(self, True)
  File "/home/jq/pr/lazi/lazi/core/loader.py", line 107, in exec_module
    self.loader.exec_module(target if target is not None else module)
  File "/<site-packages>/pandas/core/arrays/__init__.py", line 19, in <module>
    from pandas.core.arrays.sparse import SparseArray
  File "/home/jq/pr/lazi/lazi/core/module.py", line 75, in __getattribute__
    spec.loader.exec_module(self, True)
  File "/home/jq/pr/lazi/lazi/core/loader.py", line 107, in exec_module
    self.loader.exec_module(target if target is not None else module)
  File "/<site-packages>/pandas/core/arrays/sparse/__init__.py", line 1, in <module>
    from pandas.core.arrays.sparse.accessor import (
  File "/home/jq/pr/lazi/lazi/core/module.py", line 75, in __getattribute__
    spec.loader.exec_module(self, True)
  File "/home/jq/pr/lazi/lazi/core/loader.py", line 107, in exec_module
    self.loader.exec_module(target if target is not None else module)
  File "/<site-packages>/pandas/core/arrays/sparse/accessor.py", line 16, in <module>
    from pandas.core.arrays.sparse.array import SparseArray
  File "/home/jq/pr/lazi/lazi/core/module.py", line 75, in __getattribute__
    spec.loader.exec_module(self, True)
  File "/home/jq/pr/lazi/lazi/core/loader.py", line 107, in exec_module
    self.loader.exec_module(target if target is not None else module)
  File "/<site-packages>/pandas/core/arrays/sparse/array.py", line 101, in <module>
    from pandas.core.nanops import check_below_min_count
ImportError: cannot import name 'check_below_min_count' from 'pandas.core.nanops' (unknown location)

>>> _
```

_Unforunately_... This isn't something that can be worked around without outer dependency tracking, which
generally results in entire packages getting loaded anyway.

If you're more interested in just tracking imports with Lazi, use the `NO_HOOK` config variable (see below).

## Configuration

The `lazi.conf` namespace package contains configuration modules
that get autoloaded (in import order) by `lazi.conf.conf`.
It is fully decoupled from the rest of the codebase.

As a result, it's possible configure Lazi by creating `lazi.conf`
modules in your project (within the `lazi.conf` namespace package),
and use conf modules provided by other packages.

Configuration variables can also be set from the environment.

It's also possible to manually change the configuration at runtime,
with the caveat that some variables may have already been used by
`lazi.core`. To avoid this, configure Lazi before importing it:

```python
from lazi.conf import conf

conf.TRACE = 1
import lazi.auto
# ...
```
