from . import base
import os


DEBUG_TRACING = int(os.getenv("DEBUG_TRACING", base.DEBUG_TRACING))
