from setuptools_scm.version import ScmVersion


def nipreps_degenerate(version: ScmVersion) -> str:
    """Testing"""
    if version.exact:
        return version.format_with("{tag}")
    return "1.0.0"
