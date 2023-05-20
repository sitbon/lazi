

def test_asyncio():
    from lazi.util import debug
    from lazi.core import lazi
    
    with lazi:
        debug.trace("-> import asyncio ->")
        import asyncio
        debug.trace("^- import asyncio -^")
        debug.trace("-> coroutines = asyncio.coroutines ->")
        coroutines = asyncio.coroutines
        debug.trace("^- coroutines = asyncio.coroutines -^")

    lazi.invalidate_caches()
