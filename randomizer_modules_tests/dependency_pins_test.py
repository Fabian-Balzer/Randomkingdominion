"""pyproject.toml (loose lower bounds) and requirements.txt (exact pins) must agree."""

import tomllib
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOT = Path(__file__).parent.parent


def _pyproject_requirements() -> dict[str, Requirement]:
    with ROOT.joinpath("pyproject.toml").open("rb") as f:
        deps = tomllib.load(f)["project"]["dependencies"]
    return {canonicalize_name(req.name): req for req in map(Requirement, deps)}


def _pinned_versions() -> dict[str, str]:
    pins = {}
    for line in ROOT.joinpath("requirements.txt").read_text().splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        name, version = line.split("==")
        pins[canonicalize_name(name)] = version.strip()
    return pins


def test_every_dependency_is_pinned_and_vice_versa():
    assert set(_pyproject_requirements()) == set(_pinned_versions())


def test_pins_satisfy_the_lower_bounds():
    pins = _pinned_versions()
    for name, req in _pyproject_requirements().items():
        assert req.specifier.contains(pins[name]), f"{name}=={pins[name]} vs. {req}"
