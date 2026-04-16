from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib


@dataclass(frozen=True)
class PackageReleaseMetadata:
    distribution_name: str
    version: str
    import_name: str
    pypi_environment: str
    testpypi_environment: str

    @property
    def pypi_project_url(self) -> str:
        return f"https://pypi.org/project/{self.distribution_name}/"

    @property
    def testpypi_project_url(self) -> str:
        return f"https://test.pypi.org/project/{self.distribution_name}/"

    def as_json(self) -> dict[str, str]:
        return {
            "distribution_name": self.distribution_name,
            "version": self.version,
            "import_name": self.import_name,
            "pypi_environment": self.pypi_environment,
            "testpypi_environment": self.testpypi_environment,
            "pypi_project_url": self.pypi_project_url,
            "testpypi_project_url": self.testpypi_project_url,
        }


def load_package_release_metadata(repo_root: Path) -> PackageReleaseMetadata:
    pyproject_path = repo_root / "pyproject.toml"
    try:
        raw = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"`{pyproject_path}` is missing.") from exc
    except tomllib.TOMLDecodeError as exc:
        raise RuntimeError(f"`{pyproject_path}` is not valid TOML.") from exc

    project = raw.get("project")
    if not isinstance(project, dict):
        raise RuntimeError("`pyproject.toml` must contain a `[project]` table.")

    distribution_name = _require_string(project, key="name", table_name="[project]")
    version = _require_string(project, key="version", table_name="[project]")

    tool = raw.get("tool")
    doctrine_tool = tool.get("doctrine") if isinstance(tool, dict) else None
    package = doctrine_tool.get("package") if isinstance(doctrine_tool, dict) else None
    if not isinstance(package, dict):
        raise RuntimeError("`pyproject.toml` must contain a `[tool.doctrine.package]` table.")

    import_name = _require_string(
        package,
        key="import_name",
        table_name="[tool.doctrine.package]",
    )
    pypi_environment = _require_string(
        package,
        key="pypi_environment",
        table_name="[tool.doctrine.package]",
    )
    testpypi_environment = _require_string(
        package,
        key="testpypi_environment",
        table_name="[tool.doctrine.package]",
    )
    return PackageReleaseMetadata(
        distribution_name=distribution_name,
        version=version,
        import_name=import_name,
        pypi_environment=pypi_environment,
        testpypi_environment=testpypi_environment,
    )


def resolve_distribution_artifact(*, dist_dir: Path, artifact_type: str) -> Path:
    if artifact_type == "wheel":
        matches = sorted(dist_dir.glob("*.whl"))
    elif artifact_type == "sdist":
        matches = sorted(dist_dir.glob("*.tar.gz"))
    else:
        raise RuntimeError(f"Unsupported artifact type `{artifact_type}`.")

    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one {artifact_type} artifact in `{dist_dir}`, found {len(matches)}."
        )
    return matches[0].resolve()


def smoke_test_distribution(
    *,
    repo_root: Path,
    artifact_type: str,
    dist_dir: Path,
) -> None:
    metadata = load_package_release_metadata(repo_root)
    artifact_path = resolve_distribution_artifact(dist_dir=dist_dir, artifact_type=artifact_type)

    with tempfile.TemporaryDirectory(prefix="doctrine-package-smoke-") as temp_dir:
        temp_root = Path(temp_dir)
        project_root = temp_root / "smoke-project"
        prompts_root = project_root / "prompts"
        output_root = project_root / "build"
        venv_root = temp_root / "venv"
        python_path = _venv_python(venv_root)

        _run([sys.executable, "-m", "venv", str(venv_root)], cwd=repo_root)
        _run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], cwd=repo_root)
        _run([str(python_path), "-m", "pip", "install", str(artifact_path)], cwd=repo_root)

        prompts_root.mkdir(parents=True)
        (prompts_root / "AGENTS.prompt").write_text(
            'output schema HelloPayload: "Hello Payload"\n'
            '    field summary: "Summary"\n'
            '        type: string\n'
            "\n"
            'output shape HelloJson: "Hello JSON"\n'
            "    kind: JsonObject\n"
            "    schema: HelloPayload\n"
            "\n"
            'output HelloWorldReply: "Hello World Reply"\n'
            "    target: TurnResponse\n"
            "    shape: HelloJson\n"
            "    requirement: Required\n"
            "\n"
            "agent HelloWorld:\n"
            '    role: "You are the hello world agent."\n'
            "\n"
            '    workflow: "Instruction"\n'
            '        "Say hello world."\n'
            "\n"
            '    outputs: "Outputs"\n'
            "        HelloWorldReply\n"
            "\n"
            "    final_output: HelloWorldReply\n",
            encoding="utf-8",
        )
        (project_root / "pyproject.toml").write_text(
            "\n".join(
                [
                    "[project]",
                    'name = "doctrine-smoke"',
                    'version = "0.0.0"',
                    "",
                    "[tool.doctrine.emit]",
                    "",
                    "[[tool.doctrine.emit.targets]]",
                    'name = "smoke"',
                    'entrypoint = "prompts/AGENTS.prompt"',
                    'output_dir = "build"',
                    "",
                ]
            ),
            encoding="utf-8",
        )

        _run(
            [
                str(python_path),
                "-m",
                f"{metadata.import_name}.emit_docs",
                "--pyproject",
                str(project_root / "pyproject.toml"),
                "--target",
                "smoke",
            ],
            cwd=project_root,
        )

        agents_path = output_root / "hello_world" / "AGENTS.md"
        if not agents_path.is_file():
            raise RuntimeError(
                f"Smoke output is missing the emitted AGENTS.md file: `{agents_path}`."
            )
        agents_text = agents_path.read_text(encoding="utf-8")
        if "Say hello world." not in agents_text:
            raise RuntimeError(
                f"Smoke output under `{agents_path}` did not contain the expected compiled text."
            )
        if "#### Payload Fields" not in agents_text:
            raise RuntimeError(
                f"Smoke output under `{agents_path}` is missing the structured payload table."
            )
        if "#### Example" in agents_text:
            raise RuntimeError(
                f"Smoke output under `{agents_path}` rendered an unexpected Example section."
            )
        schema_path = output_root / "hello_world" / "schemas" / "hello_world_reply.schema.json"
        if not schema_path.is_file():
            raise RuntimeError(f"Smoke output is missing the emitted schema file: `{schema_path}`.")
        contract_path = output_root / "hello_world" / "final_output.contract.json"
        if not contract_path.is_file():
            raise RuntimeError(
                f"Smoke output is missing the emitted final-output contract: `{contract_path}`."
            )


def write_github_outputs(*, metadata: PackageReleaseMetadata, output_path: Path) -> None:
    lines = [
        f"distribution_name={metadata.distribution_name}",
        f"version={metadata.version}",
        f"import_name={metadata.import_name}",
        f"pypi_environment={metadata.pypi_environment}",
        f"testpypi_environment={metadata.testpypi_environment}",
        f"pypi_project_url={metadata.pypi_project_url}",
        f"testpypi_project_url={metadata.testpypi_project_url}",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _venv_python(venv_root: Path) -> Path:
    if sys.platform == "win32":
        return venv_root / "Scripts" / "python.exe"
    return venv_root / "bin" / "python"


def _run(command: list[str], *, cwd: Path) -> None:
    completed = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if completed.returncode == 0:
        return
    detail = (completed.stderr or completed.stdout).strip()
    if not detail:
        detail = f"Command exited with status {completed.returncode}."
    raise RuntimeError(
        f"Command failed: {' '.join(command)}\n{detail}"
    )


def _require_string(raw: dict[object, object], *, key: str, table_name: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"`{table_name}.{key}` must be a non-empty string.")
    return value.strip()

def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read Doctrine package release metadata and run package smoke checks."
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    metadata = subparsers.add_parser(
        "metadata",
        help="Print package release metadata for repo-owned workflows.",
    )
    metadata.add_argument(
        "--repo-root",
        default=".",
        help="Repo root that contains `pyproject.toml`.",
    )
    metadata.add_argument(
        "--format",
        choices=("json", "github-output"),
        default="json",
        help="Output format.",
    )
    metadata.add_argument(
        "--output",
        help="Output file path for `github-output` format.",
    )

    smoke = subparsers.add_parser(
        "smoke",
        help="Install one built dist artifact in a fresh venv and compile a temp project.",
    )
    smoke.add_argument(
        "--repo-root",
        default=".",
        help="Repo root that contains `pyproject.toml`.",
    )
    smoke.add_argument(
        "--artifact-type",
        choices=("wheel", "sdist"),
        required=True,
        help="Dist artifact type to smoke test.",
    )
    smoke.add_argument(
        "--dist-dir",
        default="dist",
        help="Directory that contains built dist artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    try:
        if args.command == "metadata":
            metadata = load_package_release_metadata(repo_root)
            if args.format == "json":
                print(json.dumps(metadata.as_json(), sort_keys=True))
                return 0
            if not args.output:
                raise RuntimeError("`metadata --format github-output` requires `--output`.")
            write_github_outputs(metadata=metadata, output_path=Path(args.output).resolve())
            return 0

        smoke_test_distribution(
            repo_root=repo_root,
            artifact_type=args.artifact_type,
            dist_dir=(repo_root / args.dist_dir).resolve(),
        )
        return 0
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
