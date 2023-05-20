

def test_array():
    """NOTE: This is one test where the internal traces are never shown for some reason.
    """
    from lazi.util import debug
    from lazi.core.finder import Finder

    with Finder() as finder:
        debug.trace(f"-> import array ->")
        import array
        debug.trace("^- import array -^")
        debug.trace("-> dir(array.array) ->")
        dir(array.array)
        debug.trace("^- dir(array.array) -^")

    finder.invalidate_caches()


# if __name__ == "__main__":
#     test_array()
