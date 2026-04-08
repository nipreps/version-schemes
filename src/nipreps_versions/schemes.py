from contextlib import suppress
from datetime import date

from packaging.version import Version

# Internal APIs to keep tabs on
from setuptools_scm.version import (
    SEMVER_MINOR,
    guess_next_simple_semver,
    guess_next_version,
    tag_to_version,
)
from vcs_versioning import ScmVersion


def nipreps_calver(version: ScmVersion) -> str:
    if version.exact:
        return version.format_with("{tag}")
    return version.format_next_version(
        next_calver,
        node_date=version.node_date,
        version_cls=version.config.version_cls,
    )


def next_calver(
    version: ScmVersion,
    node_date: date | None = None,
    version_cls: type[Version] | None = None,
) -> str:
    """Nipreps calver takes the form YY.MINOR.PATCH"""
    if version_cls is None:
        version_cls = Version

    # use provided time to allow context access
    head_date = node_date or version.time.date()

    tag = version_cls(str(version.tag))

    # Tag the start of a branch with <YEAR>.<MINOR>.<PATCH>.dev0
    # to hard-code anticipated version
    if tag.is_devrelease:
        return guess_next_version(version)

    # rel/ and maint/ branches tell us the next version
    if (branch := version.branch) is not None:
        # maint/ branches may end in ".x", which parse as invalid versions
        branch_series = branch.split("/")[-1].replace(".x", ".0")
        if version.config.tag_regex.match(branch_series):
            branch_ver = None
            with suppress(Exception):
                branch_ver = tag_to_version(branch_series, version.config)

            match branch_ver:
                case Version(major=tag.major, minor=tag.minor):
                    # We're in a release/maintenance branch, next is a patch/rc/beta bump
                    return guess_next_version(version)

    if head_date.year % 1000 != tag.major:
        return str(version_cls(f"{head_date:%y}.0.0"))

    return guess_next_simple_semver(version, retain=SEMVER_MINOR)
