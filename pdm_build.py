from pathlib import Path
from shutil import copy
from subprocess import run

from pdm.backend.hooks import Context


def pdm_build_update_files(context: Context, files: dict[str, Path]) -> None:
    if context.target == "sdist":
        context.ensure_build_dir()
        copy(files["uv.lock"], context.build_dir / "uv.lock")
        context.config.write_to(context.build_dir / "pyproject.toml")
        run(["uv", "lock"], cwd=context.build_dir, check=True)
