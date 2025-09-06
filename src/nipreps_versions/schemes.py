from datetime import date, datetime, timezone

from packaging.version import Version
from setuptools_scm.version import (
    SEMVER_MINOR,
    ScmVersion,
    _parse_version_tag,
    guess_next_simple_semver,
    guess_next_version,
)


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

    head_date = node_date or datetime.now(timezone.utc).date()

    tag = version_cls(str(version.tag))

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
        return str(version_cls(f"{head_date:%y}.0.0"))

    return guess_next_simple_semver(version, retain=SEMVER_MINOR)
