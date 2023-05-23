# Lazi: Lazy Imports Everywhere

An easy way to implement and track lazy imports globally.

No external dependencies.

**Requires Python >= 3.10, and 3.11 is HIGHLY Recommended.**

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
[7FD30C5BD2B0] LAZY >>>> [7FD30C84E0C0] django VERSION  # Lazy loaded django due to VERSION attr access.
[7FD30C5BD080] LAZY <<<< [7FD30C5BD030] django.utils version = [7FD30C5BD6C0]  # Ditto for django.utils setattr.
[7FD30C5BD6C0] LAZY >>>> [7FD30C5BD170] django.utils|version get_version # Accessing get_version in django.utils.version.
[7FD30C5BE200] LAZY >>>> [7FD30C5BE110] django.utils|regex_helper _lazy_re_compile
[7FD30C5BE5C0] LAZY >>>> [7FD30C5BE4D0] django.utils|functional SimpleLazyObject
(4, 2, 1, 'final', 0)
>>> _
```

And with `TRACE=3`:

```pycon
>>> import lazi.auto
[7F4C28B37350] HOOK Finder refs:0 inst:0 sys:5 
>>> import django
[7F4C28B37350] FIND pyc  django *
[7F4C289BD5D0] CREA LAZY [7F4C28C4A160] django ....  # This is where the a module is set up.
>>> django.VERSION
[7F4C289BD5D0] LAZY >>>> [7F4C28C4A160] django VERSION
[7F4C289BD5D0] LAZY EXEC [7F4C28C4A160] django >>>> 
[7F4C28B37350] FIND pyc  django.utils 
[7F4C289BD080] CREA LAZY [7F4C289BD0D0] django.utils .... 
[7F4C28B37350] FIND pyc  django.utils|version 
[7F4C289BD800] CREA LAZY [7F4C289BD490] django.utils|version .... 
[7F4C289BD080] LAZY >>>> [7F4C289BD0D0] django.utils version = [7F4C289BD800]
[7F4C289BD080] LAZY EXEC [7F4C289BD0D0] django.utils >>>> 
[7F4C289BD080] EXEC LOAD [7F4C289BD0D0] django.utils ++++ 
[7F4C289BD800] LAZY >>>> [7F4C289BD490] django.utils|version get_version
[7F4C289BD800] LAZY EXEC [7F4C289BD490] django.utils|version >>>> 
[7F4C28B37350] FIND pycS datetime *  # "S" means it's a stdlib module. "B" means it's a builtin module.
[7F4C289BDF30] CREA LAZY [7F4C289BDF80] datetime .... 
[7F4C28B37350] FIND pycS subprocess *
[7F4C289BE020] CREA LAZY [7F4C289BE070] subprocess .... 
[7F4C28B37350] FIND pyc  django.utils|regex_helper 
[7F4C289BE0C0] CREA LAZY [7F4C289BDFD0] django.utils|regex_helper .... 
[7F4C289BE0C0] LAZY >>>> [7F4C289BDFD0] django.utils|regex_helper _lazy_re_compile
[7F4C289BE0C0] LAZY EXEC [7F4C289BDFD0] django.utils|regex_helper >>>> 
[7F4C28B37350] FIND pyc  django.utils|functional 
[7F4C289BE4D0] CREA LAZY [7F4C289BE3E0] django.utils|functional .... 
[7F4C289BE4D0] LAZY >>>> [7F4C289BE3E0] django.utils|functional SimpleLazyObject
[7F4C289BE4D0] LAZY EXEC [7F4C289BE3E0] django.utils|functional >>>> 
[7F4C28B37350] FIND pycS copy *
[7F4C289BF830] CREA LAZY [7F4C289BF380] copy .... 
[7F4C289BE4D0] EXEC LOAD [7F4C289BE3E0] django.utils|functional ++++ 
[7F4C289BE0C0] EXEC LOAD [7F4C289BDFD0] django.utils|regex_helper ++++ 
[7F4C289BD800] EXEC LOAD [7F4C289BD490] django.utils|version ++++ 
[7F4C289BD5D0] EXEC LOAD [7F4C28C4A160] django ++++  # This is where a lazy module is fully loaded. 
(4, 2, 1, 'final', 0)
>>> exit()
[7F4C289BF830] LAZY DEAD [7F4C289BF380] copy
[7F4C289BE4D0] LOAD DEAD [7F4C289BE3E0] django.utils|functional
[7F4C289BE0C0] LOAD DEAD [7F4C289BDFD0] django.utils|regex_helper
[7F4C289BE020] LAZY DEAD [7F4C289BE070] subprocess
[7F4C289BDF30] LAZY DEAD [7F4C289BDF80] datetime
[7F4C289BD800] LOAD DEAD [7F4C289BD490] django.utils|version
[7F4C289BD080] LOAD DEAD [7F4C289BD0D0] django.utils
[7F4C289BD5D0] LOAD DEAD [7F4C28C4A160] django
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

Fortunately, Lazi wraps the original exception before it poetentially gets transformed into an `ImportError`.

Example (with `TRACE=0`):
```pycon
>>> import lazi.auto
>>> import pandas.core.nanops
Traceback (most recent call last):
  File "/home/jq/pr/lazi/lazi/core/loader.py", line 115, in exec_module
    self.loader.exec_module(target if target is not None else module)
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "<site-packages>/pandas/core/nanops.py", line 74, in <module>
    set_use_bottleneck(get_option("compute.use_bottleneck"))
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<site-packages>/pandas/_config/config.py", line 261, in __call__
    return self.__func__(*args, **kwds)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<site-packages>/pandas/_config/config.py", line 135, in _get_option
    key = _get_single_key(pat, silent)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<site-packages>/pandas/_config/config.py", line 121, in _get_single_key
    raise OptionError(f"No such keys(s): {repr(pat)}")
pandas._config.config.OptionError: No such keys(s): 'compute.use_bottleneck'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/jq/pr/lazi/lazi/core/module.py", line 102, in __setattr__
    spec.loader.exec_module(self, True)
  File "/home/jq/pr/lazi/lazi/core/loader.py", line 115, in exec_module
    self.loader.exec_module(target if target is not None else module)
  File "<site-packages>/pandas/__init__.py", line 48, in <module>
    from pandas.core.api import (
  File "/home/jq/pr/lazi/lazi/core/module.py", line 75, in __getattribute__
    spec.loader.exec_module(self, True)
  File "/home/jq/pr/lazi/lazi/core/loader.py", line 115, in exec_module
    self.loader.exec_module(target if target is not None else module)
  File "<site-packages>/pandas/core/api.py", line 27, in <module>
    from pandas.core.arrays import Categorical
  File "/home/jq/pr/lazi/lazi/core/module.py", line 75, in __getattribute__
    spec.loader.exec_module(self, True)
  File "/home/jq/pr/lazi/lazi/core/loader.py", line 115, in exec_module
    self.loader.exec_module(target if target is not None else module)
  File "<site-packages>/pandas/core/arrays/__init__.py", line 19, in <module>
    from pandas.core.arrays.sparse import SparseArray
  File "/home/jq/pr/lazi/lazi/core/module.py", line 75, in __getattribute__
    spec.loader.exec_module(self, True)
  File "/home/jq/pr/lazi/lazi/core/loader.py", line 115, in exec_module
    self.loader.exec_module(target if target is not None else module)
  File "<site-packages>/pandas/core/arrays/sparse/__init__.py", line 1, in <module>
    from pandas.core.arrays.sparse.accessor import (
  File "/home/jq/pr/lazi/lazi/core/module.py", line 75, in __getattribute__
    spec.loader.exec_module(self, True)
  File "/home/jq/pr/lazi/lazi/core/loader.py", line 115, in exec_module
    self.loader.exec_module(target if target is not None else module)
  File "<site-packages>/pandas/core/arrays/sparse/accessor.py", line 16, in <module>
    from pandas.core.arrays.sparse.array import SparseArray
  File "/home/jq/pr/lazi/lazi/core/module.py", line 75, in __getattribute__
    spec.loader.exec_module(self, True)
  File "/home/jq/pr/lazi/lazi/core/loader.py", line 115, in exec_module
    self.loader.exec_module(target if target is not None else module)
  File "<site-packages>/pandas/core/arrays/sparse/array.py", line 101, in <module>
    from pandas.core.nanops import check_below_min_count
  File "/home/jq/pr/lazi/lazi/core/module.py", line 75, in __getattribute__
    spec.loader.exec_module(self, True)
  File "/home/jq/pr/lazi/lazi/core/loader.py", line 136, in exec_module
    raise Loader.Error(f"Error loading {name_}" if not __debug__ else msg) from e
lazi.core.loader.Loader.Error: [7F899C139260] EXEC DEAD [7F899C1382C0] pandas.core|nanops !!!! OptionError
>>> _
```

_Unforunately_... This isn't something that can be worked around without outer dependency tracking, which
generally results in entire packages getting loaded anyway.

If you're more interested in just tracking imports with Lazi, use the `NO_HOOK`
or `NO_LAZY` config variables (see below and [lazi/conf/base.py](lazi/conf/base.py)).

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
