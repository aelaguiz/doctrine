from __future__ import annotations

from doctrine import model
from pathlib import Path

from doctrine._compiler.package_diagnostics import package_compile_error
from doctrine._compiler.package_layout import (
    PackageOutputRegistry,
    bundle_ordinary_package_files,
    new_package_output_registry,
    register_package_output_path,
)
from doctrine._compiler.resolved_types import (
    CompiledSection,
    CompiledSkillPackage,
    CompiledSkillPackageFile,
    IndexedUnit,
)
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
            raise package_compile_error(
                code="E291",
                summary="Prompt source path is required for compilation",
                detail=(
                    f"Skill package `{decl.name}` is missing a source path; package "
                    "emission requires a real `SKILL.prompt` file."
                ),
            )
        return source_path.parent

    def _compile_skill_package_bundle_files(
        self,
        decl: model.SkillPackageDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[CompiledSkillPackageFile, ...]:
        source_root = self._skill_package_source_root(unit=unit, decl=decl)
        source_path = unit.prompt_file.source_path
        if source_path is None:
            raise package_compile_error(
                code="E291",
                summary="Prompt source path is required for compilation",
                detail=f"Skill package `{decl.name}` is missing a source path.",
            )

        registry = new_package_output_registry(
            owner_label=f"skill package {decl.name}",
            compiler_owned_paths=("SKILL.md",),
            path_label_singular="Skill package bundled path",
            path_label_plural="Skill package bundled paths",
            read_label="skill package bundled file",
        )
        compiled_files: list[CompiledSkillPackageFile] = []
        ordinary_files: list[Path] = []

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
                            registry=registry,
                        )
                    )
                continue
            if any(
                reserved_dir == bundled_path.parent
                or reserved_dir in bundled_path.parents
                for reserved_dir in reserved_prompt_dirs
            ):
                continue
            ordinary_files.append(bundled_path)

        compiled_files.extend(
            CompiledSkillPackageFile(path=file.path, content=file.content)
            for file in bundle_ordinary_package_files(
                source_root,
                ordinary_files,
                registry=registry,
            )
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
        registry: PackageOutputRegistry,
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
            raise package_compile_error(
                code="E304",
                summary="Invalid skill package bundle",
                detail=(
                    "Nested prompt-bearing skill package files must define exactly one "
                    f"concrete agent in skill package {decl.name}: "
                    f"{prompt_path.relative_to(source_root).as_posix()}"
                ),
                path=prompt_path,
                hints=(
                    "Keep exactly one concrete agent in each bundled agent prompt.",
                ),
            )

        output_path = register_package_output_path(
            prompt_path.relative_to(source_root).with_suffix(".md").as_posix(),
            registry=registry,
            source_path=prompt_path,
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
