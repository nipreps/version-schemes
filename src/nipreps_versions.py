"""Version schemes for NiPreps projects.

NiPreps Version Schemes
=======================

This package provides a ``setuptools_scm`` plugin for version schemes used
by the NiPreps family of projects.

Usage
-----

To use the plugin, add ``nipreps_versions`` to the ``build-system.requires``
list in your ``pyproject.toml`` file, and set the ``version_scheme`` option
in the ``[tool.setuptools_scm]`` section to one of the available schemes.

Example::

    [build-system]
    requires = ["setuptools", "setuptools_scm", "nipreps_versions"]
    build-backend = "setuptools.build_meta"

    [tool.setuptools_scm]
    version_scheme = "nipreps-calver"

``setuptools_scm`` works with other build backends, and configuring it
may differ slightly, depending on the backend. See the documentation for
your build backend for details.


Available Schemes
-----------------

+------------------+--------------------------+
| Scheme           | Definition               |
+==================+==========================+
| nipreps-calver   | :func:`nipreps_calver`   |
+------------------+--------------------------+

.. autofunction:: nipreps_versions.nipreps_calver

"""

from collections.abc import Callable
from datetime import datetime, timezone
from functools import wraps

from setuptools_scm.version import (
    SEMVER_MINOR,
    ScmVersion,
    _parse_version_tag,
    guess_next_simple_semver,
    guess_next_version,
)

__all__ = ["nipreps_calver"]


def scheme(guess_next: Callable[[ScmVersion], str]) -> Callable[[ScmVersion], str]:
    """Create a setuptools_scm version scheme from a calculator function."""

    @wraps(guess_next)
    def wrapper(version: ScmVersion) -> str:
        if version.exact:
            return version.format_with("{tag}")
        return version.format_next_version(guess_next)

    return wrapper


@scheme
def nipreps_calver(version: ScmVersion) -> str:
    """Nipreps CalVer takes the form YY.MINOR.PATCH.

    This is a Calendar Versioning scheme, where the major version is the
    last two digits of the year, and the minor and patch versions are
    incremented as needed. The intended use case is for projects that
    want to convey the date of the most recent new features, but do not
    want to imply any particular release cadence or semantic versioning.

    A "minor series" is a series of releases that share a ``YY.MINOR.`` prefix,
    and a new minor series indicates that new features or possibly breaking
    changes have been introduced. A patch release indicates that only bug fixes
    have been introduced.

    If released within the same year, a new minor series will increment the
    minor version by one. When the year changes, the major version increments
    by one, and the minor version resets to zero.

    Git branch names are used to determine whether the next version will be a new
    minor release or a patch release. By default, the next version is computed as
    a new minor release. For example, if the last tag was 21.0.0, the next version
    would be 21.1.0 if the year is still 2021. If the year changes to 2022, the
    next version will be 22.0.0.

    If the branch name is ``*/YY.MINOR.*``, and the most recent tag is
    ``YY.MINOR.PATCH``, then the next version is computed as a patch release,
    and the patch version is incremented by one. For example, if the last tag
    was 21.0.0, and the branch name is ``maint/21.0.x``, then the next version is
    21.0.1, and development versions would be ``21.0.1.devN``
    Likewise, ``rel/21.0.1`` would also indicate that the next version is 21.0.1.
    Patch releases do not depend on the year of release, and may be released
    at any time without incrementing the major or minor versions.

    Note that specific version numbers in the branch name are not treated as
    authoritative. `rel/21.0.1` after a `21.0.1` tag would produce a development
    version of `21.0.2.devN`, not `21.0.1.devN`. Likewise, a `rel/21.0.2` branch
    after a `21.0.0` tag would produce a development version of `21.0.1.devN`,

    In order to specifically override the default behavior, a development tag may
    be set on the branch. The main use case for this is to indicate that no new
    minor releases are expected in the current year. For example, if the last tag
    was 21.2.0, you may want to indicate that the next release will be 22.0.0, by
    creating a tag ``22.0.0.dev0`` on the branch.

    Parameters
    ----------
    version : ScmVersion
      The version object provided by setuptools_scm. We use the fields
      ``tag``, ``branch``, ``node_date``, and ``config``.

    Returns
    -------
    version : str
    """
    head_date = version.node_date or datetime.now(timezone.utc).date()

    tag = version.config.version_cls(str(version.tag))

    # Tag the start of a branch with <YEAR>.<MINOR>.<PATCH>.dev0
    # to hard-code anticipated version
    if tag.is_devrelease:
        return guess_next_version(version)

    # rel/ and maint/ branches tell us the next version
    if (branch := version.branch) is not None:
        branch_ver_data = _parse_version_tag(branch.split("/")[-1], version.config)
        if branch_ver_data is not None:
            branch_ver = branch_ver_data["version"]
            tag_ver_up_to_minor = str(version.tag).split(".")[:SEMVER_MINOR]
            branch_ver_up_to_minor = branch_ver.split(".")[:SEMVER_MINOR]
            if branch_ver_up_to_minor == tag_ver_up_to_minor:
                # We're in a release/maintenance branch, next is a patch/rc/beta bump:
                return guess_next_version(version)

    if head_date.year % 1000 != tag.major:
        return str(version.config.version_cls(f"{head_date:%y}.0.0"))

    return guess_next_simple_semver(version, retain=SEMVER_MINOR)
