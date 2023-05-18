
__all__ = "oid",


def oid(obj, /):
    return hex(id(obj))[2:].upper()
