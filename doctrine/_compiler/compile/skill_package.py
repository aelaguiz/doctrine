from __future__ import annotations

from doctrine import model
from pathlib import Path

from doctrine._compiler.indexing import skill_package_id, unit_declarations
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
    SkillPackageHostCompileContext,
)
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown, render_readable_block


class CompileSkillPackageMixin:
    """Skill package compile helpers for CompilationContext."""

    def _new_skill_package_host_context(
        self,
        *,
        unit: IndexedUnit,
        decl: model.SkillPackageDecl,
    ) -> SkillPackageHostCompileContext:
        return SkillPackageHostCompileContext(
            package_unit=unit,
            package_decl=decl,
            package_id=skill_package_id(decl),
            host_slots_by_key={slot.key: slot for slot in decl.host_contract},
        )

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
        registry: PackageOutputRegistry,
    ) -> tuple[CompiledSkillPackageFile, ...]:
        source_root = self._skill_package_source_root(unit=unit, decl=decl)
        source_path = unit.prompt_file.source_path
        if source_path is None:
            raise package_compile_error(
                code="E291",
                summary="Prompt source path is required for compilation",
                detail=f"Skill package `{decl.name}` is missing a source path.",
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

    def _compile_skill_package_emitted_docs(
        self,
        decl: model.SkillPackageDecl,
        *,
        unit: IndexedUnit,
        registry: PackageOutputRegistry,
    ) -> tuple[CompiledSkillPackageFile, ...]:
        source_path = unit.prompt_file.source_path
        if source_path is None:
            raise package_compile_error(
                code="E291",
                summary="Prompt source path is required for compilation",
                detail=f"Skill package `{decl.name}` is missing a source path.",
            )

        compiled_files: list[CompiledSkillPackageFile] = []
        for entry in decl.emit_entries:
            output_path = self._register_skill_package_emitted_doc_path(
                entry,
                decl=decl,
                source_path=source_path,
                registry=registry,
            )
            target_unit, document_decl = self._resolve_skill_package_emitted_document_ref(
                entry,
                unit=unit,
            )
            with self._with_skill_package_artifact_context(
                path=output_path,
                kind="document",
                source=".".join((*target_unit.module_parts, document_decl.name)) or document_decl.name,
            ):
                compiled_document = self._compile_document_decl(document_decl, unit=target_unit)
            compiled_files.append(
                CompiledSkillPackageFile(
                    path=output_path,
                    content=self._render_skill_package_companion_markdown(compiled_document),
                )
            )
        return tuple(compiled_files)

    def _register_skill_package_emitted_doc_path(
        self,
        entry: model.SkillPackageEmitEntry,
        *,
        decl: model.SkillPackageDecl,
        source_path: Path,
        registry: PackageOutputRegistry,
    ) -> str:
        if not entry.path.endswith(".md"):
            raise package_compile_error(
                code="E304",
                summary="Invalid skill package bundle",
                detail=(
                    "Skill package emitted document paths must end in `.md` "
                    f"in skill package {decl.name}: {entry.path}"
                ),
                path=source_path,
                source_span=entry.source_span,
                hints=("Map each `emit:` entry to one package-relative Markdown file.",),
            )
        return register_package_output_path(
            entry.path,
            registry=registry,
            source_path=source_path,
            source_span=entry.source_span,
        )

    def _resolve_skill_package_emitted_document_ref(
        self,
        entry: model.SkillPackageEmitEntry,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.DocumentDecl]:
        lookup_targets = self._decl_lookup_targets(entry.ref, unit=unit)
        if not any(
            unit_declarations(lookup_target.unit).documents_by_name.get(
                lookup_target.declaration_name
            )
            is not None
            for lookup_target in lookup_targets
        ):
            dotted_name = (
                ".".join((*entry.ref.module_parts, entry.ref.declaration_name))
                if entry.ref.module_parts
                else entry.ref.declaration_name
            )
            for lookup_target in lookup_targets:
                actual_kind = self._named_non_output_decl_kind(
                    lookup_target.declaration_name,
                    unit=lookup_target.unit,
                )
                if actual_kind is not None:
                    raise package_compile_error(
                        code="E304",
                        summary="Invalid skill package bundle",
                        detail=(
                            "Skill package `emit:` entries must point at document declarations, "
                            f"but `{dotted_name}` is a {actual_kind}."
                        ),
                        path=unit.prompt_file.source_path,
                        source_span=entry.ref.source_span,
                    )
        return self._resolve_document_ref(entry.ref, unit=unit)

    def _render_skill_package_companion_markdown(
        self,
        compiled_document: CompiledSection,
    ) -> bytes:
        rendered = render_readable_block(compiled_document, depth=1).rstrip()
        return (rendered + "\n").encode("utf-8")

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

        entrypoint_path = source_root / "SKILL.prompt"
        nested_session = CompilationSession(
            parse_file(entrypoint_path),
            project_config=self.session.project_config,
            skill_package_host_context=self._active_skill_package_host_context(),
        )
        prompt_unit = nested_session.root_flow.units_by_path.get(prompt_path.resolve())
        if prompt_unit is None:
            raise package_compile_error(
                code="E901",
                summary="Internal compiler error",
                detail=(
                    "Internal compiler error: nested skill package prompt is not part of the "
                    f"indexed flow: {prompt_path.relative_to(source_root).as_posix()}"
                ),
                path=prompt_path,
                hints=("This is a compiler bug, not a prompt authoring error.",),
            )
        concrete_agents = tuple(
            agent
            for agent in unit_declarations(prompt_unit).agents_by_name.values()
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
        with self._with_skill_package_artifact_context(
            path=output_path,
            kind="agent",
            source=prompt_path.relative_to(source_root).as_posix(),
        ):
            compiled_agent = nested_session.compile_agent_from_unit(
                prompt_unit,
                concrete_agents[0].name,
            )
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

        registry = new_package_output_registry(
            owner_label=f"skill package {decl.name}",
            compiler_owned_paths=("SKILL.md", "SKILL.contract.json"),
            path_label_singular="Skill package bundled path",
            path_label_plural="Skill package bundled paths",
            read_label="skill package bundled file",
        )
        host_context = self._new_skill_package_host_context(unit=unit, decl=decl)
        with self._with_skill_package_host_context(host_context):
            with self._with_skill_package_artifact_context(
                path="SKILL.md",
                kind="skill_package_root",
            ):
                root = CompiledSection(
                    title=decl.title,
                    body=self._compile_record_support_items(
                        decl.items,
                        unit=unit,
                        owner_label=f"skill package {decl.name}",
                        surface_label="skill package prose",
                    ),
                )
            emitted_docs = self._compile_skill_package_emitted_docs(
                decl,
                unit=unit,
                registry=registry,
            )
            bundled_files = self._compile_skill_package_bundle_files(
                decl,
                unit=unit,
                registry=registry,
            )

        return CompiledSkillPackage(
            name=decl.name,
            title=decl.title,
            frontmatter=tuple(frontmatter),
            root=root,
            contract=host_context.compiled_contract(),
            files=(*emitted_docs, *bundled_files),
        )
