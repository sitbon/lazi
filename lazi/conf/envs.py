"""Set conf vars from env vars.
"""
import os as _os
import types as _types
import typing as _typing


_type_map: dict[type] = {
    bool: lambda valu: valu.lower() in ("1", "true", "yes", "on"),
    int: int,
    float: float,
    str: str,
    bytes: bytes,
    list: lambda valu: valu.split(","),
    tuple: lambda valu: tuple(valu.split(",")),
    set: lambda valu: set(valu.split(",")),
    dict: lambda valu: dict(_.split(":", 1) for _ in valu.split(",")),
    _types.NoneType: lambda valu: None if not valu else _types.NoneType(valu),  # type: ignore
}


def parse_item(typp: type, valu: str) -> object:
    if isinstance(typp, _types.UnionType):
        args = _typing.get_args(typp)
        if not valu and _types.NoneType in args:
            return None
        for typ in args:
            try:
                return _type_map[typ](valu)
            except (ValueError, TypeError):
                continue
    return _type_map[typp](valu)


def load():
    from lazi.conf import base
    typd: dict[str, type] = _typing.get_type_hints(base)
    keys: set[str] = base.CONF_KEYS | base.__meta__.get("keys", set())

    for key in (_ for _ in keys if _ in _os.environ and _ in typd):
        if (value := _os.getenv(key, no := object())) is not no:
            globals()[key] = parse_item(typd[key], value)


load()
