"""Lazi statistics & tracing.
"""
import sys
from dataclasses import dataclass, field

from .finder import Finder, __finder__


@dataclass(slots=True, frozen=True)
class Stat:

    # Number Finder specs that have hooked loaders.
    find_hook: int = field(default_factory=lambda: sum(
            sum(1 for spec in finder.specs.values() if not isinstance(spec.loader, finder.Loader))
            for finder in __finder__.__finders__
        ))

    # Total number of Finder specs.
    find_spec: int = field(default_factory=lambda: sum(
            len(finder.specs)
            for finder in __finder__.__finders__
        ))

    # Total number of Finder instances.
    find_toti: int = field(default_factory=lambda: sum(1 for finder in __finder__.__finders__))

    # Number of modules in the init state.
    load_init: int = field(default_factory=lambda: sum(
            sum(1 for spec in finder.specs.values() if spec.loader_state is finder.Loader.State.INIT)
            for finder in __finder__.__finders__
        ))

    # Number of modules in the created state.
    load_crea: int = field(default_factory=lambda: sum(
        sum(1 for spec in finder.specs.values() if spec.loader_state is finder.Loader.State.CREA)
        for finder in __finder__.__finders__
    ))

    # Number of modules loaded lazily.
    load_lazy: int = field(default_factory=lambda: sum(
            sum(1 for spec in finder.specs.values() if spec.loader_state is finder.Loader.State.LAZY)
            for finder in __finder__.__finders__
        ))

    # Number of modules executing.
    load_exec: int = field(default_factory=lambda: sum(
            sum(1 for spec in finder.specs.values() if spec.loader_state is finder.Loader.State.EXEC)
            for finder in __finder__.__finders__
        ))

    # Number of modules loaded fully.
    load_full: int = field(default_factory=lambda: sum(
            sum(1 for spec in finder.specs.values() if spec.loader_state is finder.Loader.State.LOAD)
            for finder in __finder__.__finders__
        ))

    # Number of modules with loader in dead state.
    load_dead: int = field(default_factory=lambda: sum(
            sum(1 for spec in finder.specs.values() if spec.loader_state is finder.Loader.State.DEAD)
            for finder in __finder__.__finders__
        ))

    # Number of specs with unknown loader state.
    load_wtaf: int = field(default_factory=lambda: sum(
            sum(
                1 for spec in finder.specs.values()
                if spec.loader_state is not None
                and not isinstance(spec.loader_state, finder.Loader.State)
            )
            for finder in __finder__.__finders__
        ))

    # Number of modules with no loader state.
    load_none: int = field(default_factory=lambda: sum(
            sum(1 for spec in finder.specs.values() if spec.loader_state is None)
            for finder in __finder__.__finders__
        ))

    # Number of specs with a hooked loader. Should be the sum of all the load_* stats above.
    load_hook: int = field(default_factory=lambda: sum(
            sum(1 for spec in finder.specs.values() if isinstance(spec.loader, finder.Loader))
            for finder in __finder__.__finders__
        ))

    # Total number of specs found in sys.modules with a hooked loader.
    load_syst: int = field(default_factory=lambda: sum(
            1 for mod in sys.modules.values()
            if isinstance(getattr(mod, "__loader__", None), Finder.Loader)
        ))

    syst_totl: int = field(default_factory=lambda: len(sys.modules))
