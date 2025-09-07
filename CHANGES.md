# Changelog

## Releases

### 1.1.0 (7 September 2025)

* API change: Remove `nipreps_versions.__version__`
* Drop Python 3.8 and 3.9 support, test up to Python 3.14
* Check for potential `None` case identified by type checking

### 1.0.4 (4 November 2023)

* Update tests to accommodate changes in `setuptools_scm` API and generated files
* Drop Python 3.7 support, test on 3.12
* Switch from black and isort to ruff
* Convert deprecated `datetime.utcnow()` to `datetime.now(tz=timezone.utc)`

### 1.0.3 (1 February 2023)

* Require `setuptools_scm >= 7` to ensure compatible installations

### 1.0.2 (1 January 2023)

* Resolve test failure with year change. Make test of date-specific behavior
  explicit.

### 1.0.1 (21 December 2022)

* Improvements to package metadata for PyPI
* README fixes

### 1.0.0 (21 December 2022)

* Initial release.
