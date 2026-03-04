"""Unit tests for package metadata required by documented CLI behavior."""

from pathlib import Path
import tomllib


def test_pyproject_declares_mdaug_console_script():
    """pyproject defines the documented mdaug console script entrypoint."""
    project_data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    scripts = project_data.get("project", {}).get("scripts", {})
    assert scripts.get("mdaug") == "mdaug.cli.app:main"


def test_pyproject_declares_yaml_runtime_dependency():
    """pyproject includes YAML parser dependency used by runtime config loading."""
    project_data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    dependencies = project_data.get("project", {}).get("dependencies", [])
    assert any(dependency.lower().startswith("pyyaml") for dependency in dependencies)
