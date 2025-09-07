"""Tests for nipreps_versions."""

from datetime import date
from functools import partial

import pytest
from setuptools_scm import Configuration
from setuptools_scm.version import ScmVersion, meta

from nipreps_versions import nipreps_calver

m = partial(meta, config=Configuration())


@pytest.mark.parametrize(
    ("version", "expected_next"),
    [
        pytest.param(m("22.1.0"), "22.1.0", id="exact"),
        pytest.param(
            m("22.1.0", node_date=date(2022, 12, 31), distance=1, branch="master"),
            "22.2.0.dev1",
            id="new_minor",
        ),
        pytest.param(
            m("22.1.0", node_date=date(2023, 1, 1), distance=1, branch="master"),
            "23.0.0.dev1",
            id="new_year",
        ),
        pytest.param(
            m("22.1.0", node_date=date(2023, 2, 1), distance=1, branch="rel/22.1.1"),
            "22.1.1.dev1",
            id="patch_release",
        ),
        pytest.param(
            m("22.1.0", node_date=date(2022, 12, 31), distance=1, branch="rel/22.2.0"),
            "22.2.0.dev1",
            id="minor_release",
        ),
        pytest.param(
            m("22.1.0", node_date=date(2023, 3, 31), distance=1, branch="maint/22.1.x"),
            "22.1.1.dev1",
            id="maintenance_branch",
        ),
        pytest.param(
            m("23.0.0.dev0", node_date=date(2022, 12, 31), distance=1, branch="master"),
            "23.0.0.dev1",
            id="dev_tag",
        ),
    ],
)
def test_nipreps_calver(version: ScmVersion, expected_next: str) -> None:
    """Test expected version increments."""
    assert nipreps_calver(version) == expected_next
