

def test_array():
    from lazi.util import debug
    from lazi.core.finder import Finder

    with Finder():
        debug.trace("-> import array ->")
        import array
        debug.trace("^- import array -^")
        debug.trace("-> dir(array.array) ->")
        dir(array.array)
        debug.trace("^- dir(array.array) -^")


if __name__ == "__main__":
    test_array()
