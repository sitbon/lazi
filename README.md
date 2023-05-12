# Lazi: Lazy Imports Everywhere

A lightweight and extensible way to implement lazy imports globally.

## Usage:

```shell
poetry add lazi
```

```python
"""Automatic lazy loading example.

Install django to run, or change the imports.
"""
import lazi.auto                 # Install import tracking.
import django.test               # Import stuff.
print(lazi.used_count())         # Count loaded modules.
TestCase = django.test.TestCase  # Trigger lazy loading.
print(lazi.used_count())         # More modules were lazy loaded.
```

```shell
python example.py
```

```python
5
197
```

```python
"""Manual lazy loading example.
"""
import lazi.core                        # Import Lazi.
django = lazi.lazy("django")            # Import stuff.
django_test = lazi.lazy("django.test")  # Import more stuff.
print(lazi.used_count())                # Count loaded modules.
TestCase = django_test.TestCase         # Trigger lazy loading.
print(lazi.used_count())                # Module was lazy loaded.
```

```python
1
2
```

## Configuration

The `lazi.conf` namespace package contains configuration modules
that get autoloaded (in import order) by `lazi.conf.conf`.
It is fully decoupled from the rest of the codebase.

As a result, it's possible configure Lazi by creating `lazi.conf`
modules in your project (within the `lazi.conf` namespace package),
and use conf modules provided by other packages.

Configuration is not yet controllable via environment variables,
but this is planned for the future.

It's also possible to manually change the configuration at runtime,
with the caveat that some variables may have already been used by
`lazi.core`. To avoid this, configure Lazi before importing it:

```python
from lazi.conf import conf
conf.DEBUG_TRACING = True
import lazi.auto
# ...
```


## Metadata

Reference for developers: The json dict below contains Python versioning parameters:
- Soft `min` (ignore rev) & hard `max` compatible versions.
- Recommended `use` & creator's environment `dev` versions.

```json
{
  "python": {
    "version": {
      "min": "3.10.11",
      "max": "3.12",
      "use": "3.11",
      "dev": "3.11.2"
    }
  }
}
```