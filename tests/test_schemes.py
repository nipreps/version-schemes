from datetime import date
from functools import partial

import pytest
from setuptools_scm.config import Configuration
from setuptools_scm.version import meta

from nipreps_versions.schemes import nipreps_calver

m = partial(meta, config=Configuration())


@pytest.mark.parametrize(
    "version, expected_next",
    [
        pytest.param(m("22.1.0"), "22.1.0", id="exact"),
    ],
)
def test_nipreps_calver(version, expected_next):
    assert nipreps_calver(version) == expected_next
