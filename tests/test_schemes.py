from datetime import date, datetime, timezone

import pytest
from vcs_versioning import Configuration, ScmVersion
from vcs_versioning._scm_version import meta
from vcs_versioning.overrides import GlobalOverrides

from nipreps_versions.schemes import next_calver, nipreps_calver


def m(*args, **kwargs) -> ScmVersion:  # type:ignore[no-untyped-def]  # noqa: ANN002,ANN003
    with GlobalOverrides.from_env("SETUPTOOLS_SCM"):
        return meta(*args, config=Configuration(), **kwargs)


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
        pytest.param(
            m("26.0.0", distance=1, branch="maint/26.1.xx"),
            "26.1.0.dev1",
            id="invalid_branch_version",
        ),
    ],
)
def test_nipreps_calver(version: ScmVersion, expected_next: str) -> None:
    assert nipreps_calver(version) == expected_next


def test_next_calver() -> None:
    # Omit optional arguments always passed by nipreps_calver
    assert (
        next_calver(m("1.0.0", distance=1, branch="master"))
        == f"{datetime.now(timezone.utc):%y}.0.0"
    )
