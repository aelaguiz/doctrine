from __future__ import annotations

from pathlib import Path, PurePosixPath

from doctrine._compiler.resolved_types import *  # noqa: F401,F403
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown


class CompileSkillPackageMixin:
    """Skill package compile helpers for CompilationContext."""

    def _skill_package_source_root(
        self,
        *,
        unit: IndexedUnit,
        decl: model.SkillPackageDecl,
    ) -> Path:
        source_path = unit.prompt_file.source_path
        if source_path is None:
            raise CompileError(
                f"Skill package {decl.name} is missing a source path; package emission requires a real `SKILL.prompt` file."
            )
        return source_path.parent

    def _validate_skill_package_bundle_path(
        self,
        path_text: str,
        *,
        owner_label: str,
        seen_exact: set[str],
        seen_folded: dict[str, str],
    ) -> str:
        if "\\" in path_text:
            raise CompileError(
                f"Skill package bundled paths must use `/` separators in {owner_label}: {path_text}"
            )
        path = PurePosixPath(path_text)
        parts = path.parts
        if not parts:
            raise CompileError(f"Skill package bundled path is empty in {owner_label}")
        if path.is_absolute():
            raise CompileError(
                f"Skill package bundled paths must be relative in {owner_label}: {path_text}"
            )
        if any(part in {"", ".", ".."} for part in parts):
            raise CompileError(
                f"Skill package bundled path must stay within the package root in {owner_label}: {path_text}"
            )
        if path.name in {"", ".", ".."}:
            raise CompileError(
                f"Skill package bundled path must name a file in {owner_label}: {path_text}"
            )
        normalized = path.as_posix()
        if normalized in seen_exact:
            raise CompileError(
                f"Duplicate skill package bundled path in {owner_label}: {normalized}"
            )
        folded = normalized.casefold()
        prior = seen_folded.get(folded)
        if prior is not None:
            raise CompileError(
                f"Skill package bundled path case-collides in {owner_label}: {normalized} vs {prior}"
            )
        seen_exact.add(normalized)
        seen_folded[folded] = normalized
        return normalized

    def _compile_skill_package_bundle_files(
        self,
        decl: model.SkillPackageDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[CompiledSkillPackageFile, ...]:
        source_root = self._skill_package_source_root(unit=unit, decl=decl)
        source_path = unit.prompt_file.source_path
        if source_path is None:
            raise CompileError(f"Skill package {decl.name} is missing a source path.")

        seen_exact: set[str] = {"SKILL.md"}
        seen_folded: dict[str, str] = {"skill.md": "SKILL.md"}
        compiled_files: list[CompiledSkillPackageFile] = []

        source_files = sorted(path for path in source_root.rglob("*") if path.is_file())
        reserved_prompt_dirs = {
            path.parent
            for path in source_files
            if path.suffix == ".prompt"
            and path.parent != source_root
            and not self._is_skill_package_bundled_agent_prompt(
                path,
                source_root=source_root,
            )
        }
        for bundled_path in source_files:
            if bundled_path == source_path:
                continue
            if bundled_path.suffix == ".prompt":
                if self._is_skill_package_bundled_agent_prompt(
                    bundled_path,
                    source_root=source_root,
                ):
                    compiled_files.append(
                        self._compile_skill_package_nested_prompt(
                            bundled_path,
                            decl=decl,
                            source_root=source_root,
                            seen_exact=seen_exact,
                            seen_folded=seen_folded,
                        )
                    )
                continue
            if any(
                reserved_dir == bundled_path.parent
                or reserved_dir in bundled_path.parents
                for reserved_dir in reserved_prompt_dirs
            ):
                continue

            rel_path = bundled_path.relative_to(source_root).as_posix()
            normalized_path = self._validate_skill_package_bundle_path(
                rel_path,
                owner_label=f"skill package {decl.name}",
                seen_exact=seen_exact,
                seen_folded=seen_folded,
            )
            try:
                content = bundled_path.read_bytes()
            except OSError as exc:
                raise CompileError(
                    f"Could not read skill package bundled file in skill package {decl.name}: {normalized_path}"
                ).ensure_location(path=bundled_path) from exc

            compiled_files.append(
                CompiledSkillPackageFile(path=normalized_path, content=content)
            )

        return tuple(compiled_files)

    def _is_skill_package_bundled_agent_prompt(
        self,
        prompt_path: Path,
        *,
        source_root: Path,
    ) -> bool:
        if prompt_path.suffix != ".prompt" or prompt_path.parent == source_root:
            return False
        rel_path = prompt_path.relative_to(source_root)
        return bool(rel_path.parts) and rel_path.parts[0] == "agents"

    def _compile_skill_package_nested_prompt(
        self,
        prompt_path: Path,
        *,
        decl: model.SkillPackageDecl,
        source_root: Path,
        seen_exact: set[str],
        seen_folded: dict[str, str],
    ) -> CompiledSkillPackageFile:
        from doctrine._compiler.session import CompilationSession

        prompt_file = parse_file(prompt_path)
        nested_session = CompilationSession(
            prompt_file,
            project_config=self.session.project_config,
        )
        concrete_agents = tuple(
            agent
            for agent in nested_session.root_unit.agents_by_name.values()
            if not agent.abstract
        )
        if len(concrete_agents) != 1:
            raise CompileError(
                "Nested prompt-bearing skill package files must define exactly one concrete agent "
                f"in skill package {decl.name}: {prompt_path.relative_to(source_root).as_posix()}"
            ).ensure_location(path=prompt_path)

        output_path = self._validate_skill_package_bundle_path(
            prompt_path.relative_to(source_root).with_suffix(".md").as_posix(),
            owner_label=f"skill package {decl.name}",
            seen_exact=seen_exact,
            seen_folded=seen_folded,
        )
        compiled_agent = nested_session.compile_agent(concrete_agents[0].name)
        return CompiledSkillPackageFile(
            path=output_path,
            content=render_markdown(compiled_agent).encode("utf-8"),
        )

    def _compile_skill_package_decl(
        self,
        decl: model.SkillPackageDecl,
        *,
        unit: IndexedUnit,
    ) -> CompiledSkillPackage:
        frontmatter: list[tuple[str, str]] = [("name", decl.metadata.name or decl.name)]
        if decl.metadata.description is not None:
            frontmatter.append(("description", decl.metadata.description))
        if decl.metadata.version is not None:
            frontmatter.append(("version", decl.metadata.version))
        if decl.metadata.license is not None:
            frontmatter.append(("license", decl.metadata.license))

        return CompiledSkillPackage(
            name=decl.name,
            title=decl.title,
            frontmatter=tuple(frontmatter),
            root=CompiledSection(
                title=decl.title,
                body=self._compile_record_support_items(
                    decl.items,
                    unit=unit,
                    owner_label=f"skill package {decl.name}",
                    surface_label="skill package prose",
                ),
            ),
            files=self._compile_skill_package_bundle_files(decl, unit=unit),
        )
