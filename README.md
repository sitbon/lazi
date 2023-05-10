# Lazi: Lazy Imports Everywhere

A lightweight and extensible way to implement lazy imports globally.

## Usage:

```shell
poetry add lazi
```

```python
"""example.py

Automatic lazy loading example.
Install django to run, or change the imports.
"""
import lazi.auto                 # Install import tracking.
import django.test               # Import stuff.
print(len(lazi.auto.RECORD))     # Peek at the internals for demonstration.
TestCase = django.test.TestCase  # Trigger lazy loading.
print(len(lazi.auto.RECORD))     # More modules were lazy loaded.
```

```shell
python example.py
```

```python
6
198
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