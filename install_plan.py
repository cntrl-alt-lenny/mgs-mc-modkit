# Game-neutral, versioned planning lifecycle (also embedded in install.py).
from contextlib import ExitStack
from dataclasses import dataclass


class ReplanRequired(RuntimeError):
    """Confirmed inputs changed; collect and confirm a fresh plan."""


@dataclass(frozen=True)
class AudioAcceptance:
    source: str
    sha256: str
    game: str
    role: str
    classification: str
    explicit: bool


@dataclass(frozen=True)
class PlanPackage:
    name: str
    version: str
    source: str
    sha256: str
    role: str = "package"
    acceptance: object = None


@dataclass(frozen=True)
class PlanGame:
    key: str
    path: str
    steam_root: str
    settings: str
    packages: tuple
    inputs: str
    incompatibilities: tuple = ()


@dataclass(frozen=True)
class InstallPlan:
    games: tuple
    schema: int = 1
    profile: str = "vanilla-faithful"

    def validate(self):
        if self.schema != 1 or self.profile != "vanilla-faithful" or not self.games:
            raise ValueError("Unsupported or empty installation plan")
        if len({g.key for g in self.games}) != len(self.games):
            raise ValueError("Duplicate games in installation plan")
        if len({g.path for g in self.games}) != len(self.games):
            raise ValueError("Games cannot share a destination")
        for game in self.games:
            if game.incompatibilities:
                raise ValueError("Incompatible plan: " + "; ".join(game.incompatibilities))
            if not game.packages:
                raise ValueError("Game has no payloads")
            for package in game.packages:
                if len(package.sha256) != 64 or any(
                        c not in "0123456789abcdef" for c in package.sha256):
                    raise ValueError("Payload requires an exact SHA-256 identity")
                if package.role != "package":
                    accepted = package.acceptance
                    if (not isinstance(accepted, AudioAcceptance) or
                            (accepted.source, accepted.sha256, accepted.game, accepted.role) !=
                            (package.source, package.sha256, game.key, package.role) or
                            accepted.classification not in
                            ("ok", "unknown_mod", "missing_identity", "mismatch", "ambiguous") or
                            (accepted.classification != "ok" and accepted.explicit is not True)):
                        raise ReplanRequired("Supplied audio acceptance is missing or changed; select and confirm again")


@dataclass(frozen=True)
class PreparedGame:
    game: PlanGame
    actions: tuple
    identities: tuple
    mods: tuple
    required_bytes: int


@dataclass(frozen=True)
class PreparedPlan:
    plan: InstallPlan
    games: tuple


def prepare_plan(plan, adapter, workspace):
    """Stage every game before allowing the executor to open a transaction."""
    plan.validate()
    adapter.recheck(plan)
    games = []
    for index, game in enumerate(plan.games):
        adapter.check_cancelled()
        games.append(adapter.prepare(game, workspace, index))
    prepared = PreparedPlan(plan, tuple(games))
    adapter.recheck(plan)
    adapter.check_prepared(prepared)
    adapter.check_space(prepared)
    return prepared


def execute_plan(prepared, adapter, outcomes):
    """No UI callbacks: locks, recheck all inputs, then independent commits."""
    prepared.plan.validate()
    if tuple(g.game for g in prepared.games) != prepared.plan.games:
        raise ValueError("Prepared games do not match plan order")
    with ExitStack() as locks:
        # A stable lock order prevents competing plans from deadlocking.
        for game in sorted(prepared.plan.games, key=lambda g: g.path):
            locks.enter_context(adapter.lock(game))
        adapter.recheck(prepared.plan)
        adapter.check_prepared(prepared)
        adapter.check_space(prepared)
        for index, game in enumerate(prepared.games):
            adapter.check_cancelled()
            adapter.execute(game, index, outcomes)
