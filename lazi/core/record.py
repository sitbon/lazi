from __future__ import annotations

from typing import ClassVar, Callable, ForwardRef
from dataclasses import dataclass
from importlib.machinery import ModuleSpec

from lazi.conf import conf
from .util import is_stdlib_or_builtin

__all__ = "SpecRecord",

Finder = ForwardRef("Finder")


@dataclass(slots=True, kw_only=True)
class SpecRecord:
    RECORD: ClassVar[dict[str, SpecRecord]] = {}

    name: str
    finder: Finder
    spec: ModuleSpec | None | Ellipsis = ...
    path: list[str] | None = None
    target: str | None = None
    used: bool = False
    stack: tuple[SpecRecord, ...] = ()

    def __post_init__(self):
        if self.spec is ...:
            self.spec = self.finder.__spec__(self.name, self.path, self.target)

        if (self.spec or conf.SPECR_KEEP_EMPTY) and (self.hook or conf.SPECR_KEEP_0HOOK):
            if self.name in self.RECORD:
                raise ValueError(f"SpecRecord {self.name!r} already exists")

            self.RECORD[self.name] = self

        if self.hook:
            self.finder.LoaderType(self).hook()
        else:
            self.used = self.spec is not None

    def __hash__(self):
        return hash(self.name)

    @property
    def hook(self) -> bool:
        return (
            self.spec and self.spec.origin not in (None, "built-in") and
            (conf.SPECR_HOOK_STDLI or not self.stdlib)
        )

    @property
    def stdlib(self) -> bool:
        return is_stdlib_or_builtin(self.spec)

    @property
    def cached(self) -> bool:
        return self.name in self.RECORD

    @classmethod
    def register(cls, *, finder: Finder, name: str, path: list[str] | None = None, target: str | None = None) -> SpecRecord:
        if name in cls.RECORD:
            return cls.RECORD[name]

        return cls(
            name=name,
            finder=finder,
            path=path,
            target=target,
        )

    @classmethod
    def stack_tree(cls, node_factory: Callable = lambda rec: rec) -> dict[SpecRecord, dict[SpecRecord, ...]]:
        tree = {}

        for record in (record for record in cls.RECORD.values() if record.hook and record.used):
            stack = list(record.stack)
            tree_at = tree

            while stack:
                node = node_factory(stack.pop(0))
                tree_at = tree_at.setdefault(node, {})

            tree_at[node_factory(record)] = {}

        return tree

    def on_preload(self):
        assert not self.used
        self.finder.on_preload(self)

    def on_load(self, stack: tuple[SpecRecord, ...]):
        assert not self.used
        self.used = True
        if conf.SPECR_KEEP_STACK:
            self.stack = stack
            self.finder.on_load(self)
        else:
            self.finder.on_load(self, stack)
