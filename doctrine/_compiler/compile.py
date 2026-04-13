from __future__ import annotations

from pathlib import Path, PurePosixPath

from doctrine._compiler.shared import *  # noqa: F401,F403
from doctrine._compiler.shared import (
    _ADDRESSABLE_ROOT_REGISTRIES,
    _BUILTIN_INPUT_SOURCES,
    _BUILTIN_OUTPUT_TARGETS,
    _BUILTIN_RENDER_PROFILE_NAMES,
    _INTERPOLATION_EXPR_RE,
    _INTERPOLATION_RE,
    _READABLE_DECL_REGISTRIES,
    _RESERVED_AGENT_FIELD_KEYS,
    _REVIEW_CONTRACT_FACT_KEYS,
    _REVIEW_GUARD_FIELD_NAMES,
    _REVIEW_OPTIONAL_FIELD_NAMES,
    _REVIEW_REQUIRED_FIELD_NAMES,
    _REVIEW_VERDICT_TEXT,
    _SCHEMA_FAMILY_TITLES,
    _agent_typed_field_key,
    _default_worker_count,
    _display_addressable_ref,
    _dotted_decl_name,
    _dotted_ref_name,
    _humanize_key,
    _law_path_from_name_ref,
    _lowercase_initial,
    _name_ref_from_dotted_name,
    _resolve_render_profile_mode,
    _semantic_render_target_for_block,
)
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown, render_readable_block


class CompileMixin:
    """Compile helper owner for CompilationContext."""

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
            if path.suffix == ".prompt" and path.parent != source_root
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
                content = bundled_path.read_text()
            except UnicodeDecodeError as exc:
                raise CompileError(
                    f"Skill package bundled files must be UTF-8 text in skill package {decl.name}: {normalized_path}"
                ).ensure_location(path=bundled_path) from exc
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
            content=render_markdown(compiled_agent),
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

    def _compile_agent_decl(self, agent: model.Agent, *, unit: IndexedUnit) -> CompiledAgent:
        self._enforce_legacy_role_workflow_order(agent)
        resolved_slot_states = self._resolve_agent_slots(agent, unit=unit)
        agent_contract = self._resolve_agent_contract(agent, unit=unit)
        unresolved_abstract_slots = [
            slot.key
            for slot in resolved_slot_states
            if isinstance(slot, ResolvedAbstractAgentSlot)
        ]
        if unresolved_abstract_slots:
            missing = ", ".join(unresolved_abstract_slots)
            raise CompileError(
                f"E209 Concrete agent is missing abstract authored slots in agent {agent.name}: {missing}"
            )
        resolved_slots = {
            slot.key: slot.body
            for slot in resolved_slot_states
            if isinstance(slot, ResolvedAgentSlot)
        }
        has_workflow_slot = "workflow" in resolved_slots
        review_fields = [
            field for field in agent.fields if isinstance(field, model.ReviewField)
        ]
        final_output_fields = [
            field for field in agent.fields if isinstance(field, model.FinalOutputField)
        ]
        if has_workflow_slot and review_fields:
            raise CompileError(
                f"Concrete agent may not define both `workflow` and `review`: {agent.name}"
            )
        review_output_contexts = self._review_output_contexts_for_agent(agent, unit=unit)
        route_output_contexts = self._route_output_contexts_for_agent(
            agent,
            unit=unit,
            resolved_slots=resolved_slots,
            agent_contract=agent_contract,
        )
        primary_review_output_context = self._primary_review_output_context(
            review_output_contexts
        )
        field_specs: list[AgentFieldCompileSpec] = []
        seen_role = False
        seen_typed_fields: set[str] = set()

        for field in agent.fields:
            if isinstance(field, model.RoleScalar):
                if seen_role:
                    raise CompileError(f"Duplicate role field in agent {agent.name}")
                seen_role = True
                field_specs.append(AgentFieldCompileSpec(field=field))
                continue

            if isinstance(field, model.RoleBlock):
                if seen_role:
                    raise CompileError(f"Duplicate role field in agent {agent.name}")
                seen_role = True
                field_specs.append(AgentFieldCompileSpec(field=field))
                continue

            if isinstance(
                field,
                (
                    model.AuthoredSlotField,
                    model.AuthoredSlotAbstract,
                    model.AuthoredSlotInherit,
                    model.AuthoredSlotOverride,
                ),
            ):
                slot_body = resolved_slots.get(field.key)
                if slot_body is None:
                    raise CompileError(
                        f"Internal compiler error: missing resolved authored slot in agent {agent.name}: {field.key}"
                    )
                field_specs.append(AgentFieldCompileSpec(field=field, slot_body=slot_body))
                continue

            field_key = _agent_typed_field_key(field)
            if field_key in seen_typed_fields:
                raise CompileError(f"Duplicate typed field in agent {agent.name}: {field_key}")
            seen_typed_fields.add(field_key)
            field_specs.append(AgentFieldCompileSpec(field=field))

        if not seen_role:
            raise CompileError(f"Concrete agent is missing role field: {agent.name}")

        final_output = (
            self._compile_final_output_spec(
                agent_name=agent.name,
                field=final_output_fields[0],
                unit=unit,
                agent_contract=agent_contract,
                review_output_contexts=review_output_contexts,
                route_output_contexts=route_output_contexts,
                fallback_review_semantics=(
                    primary_review_output_context[1]
                    if primary_review_output_context is not None
                    else None
                ),
            )
            if final_output_fields
            else None
        )
        compiled_fields = self._compile_agent_fields(
            field_specs,
            agent_name=agent.name,
            unit=unit,
            agent_contract=agent_contract,
            review_output_contexts=review_output_contexts,
            route_output_contexts=route_output_contexts,
            final_output=final_output,
        )
        return CompiledAgent(name=agent.name, fields=compiled_fields, final_output=final_output)

    def _compile_agent_fields(
        self,
        specs: list[AgentFieldCompileSpec],
        *,
        agent_name: str,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]],
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]],
        final_output: CompiledFinalOutputSpec | None,
    ) -> tuple[CompiledField, ...]:
        if len(specs) <= 1:
            compiled = [
                self._compile_agent_field(
                    spec,
                    agent_name=agent_name,
                    unit=unit,
                    agent_contract=agent_contract,
                    review_output_contexts=review_output_contexts,
                    route_output_contexts=route_output_contexts,
                    final_output=final_output,
                )
                for spec in specs
            ]
            return tuple(field for field in compiled if field is not None)

        with ThreadPoolExecutor(max_workers=_default_worker_count(len(specs))) as executor:
            futures = [
                executor.submit(
                    self.session._compile_agent_field_task,
                    spec,
                    agent_name=agent_name,
                    unit=unit,
                    agent_contract=agent_contract,
                    review_output_contexts=review_output_contexts,
                    route_output_contexts=route_output_contexts,
                    final_output=final_output,
                )
                for spec in specs
            ]
            return tuple(
                field
                for future in futures
                if (field := future.result()) is not None
            )

    def _compile_agent_field(
        self,
        spec: AgentFieldCompileSpec,
        *,
        agent_name: str,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]],
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]],
        final_output: CompiledFinalOutputSpec | None,
    ) -> CompiledField | None:
        field = spec.field

        if isinstance(field, model.RoleScalar):
            return model.RoleScalar(
                text=self._interpolate_authored_prose_string(
                    field.text,
                    unit=unit,
                    owner_label=f"agent {agent_name}",
                    surface_label="role prose",
                )
            )

        if isinstance(field, model.RoleBlock):
            return CompiledSection(
                title=field.title,
                body=tuple(
                    self._interpolate_authored_prose_line(
                        line,
                        unit=unit,
                        owner_label=f"agent {agent_name}",
                        surface_label="role prose",
                    )
                    for line in field.lines
                ),
            )

        if isinstance(
            field,
            (
                model.AuthoredSlotField,
                model.AuthoredSlotAbstract,
                model.AuthoredSlotInherit,
                model.AuthoredSlotOverride,
            ),
        ):
            if spec.slot_body is None:
                raise CompileError(
                    f"Internal compiler error: missing resolved authored slot in agent {agent_name}"
                )
            if field.key == "workflow":
                return self._compile_resolved_workflow(
                    spec.slot_body,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=f"agent {agent_name} workflow",
                )
            return self._compile_resolved_workflow(spec.slot_body)

        if isinstance(field, model.InputsField):
            return self._compile_inputs_field(
                field,
                unit=unit,
                owner_label=f"agent {agent_name}",
            )
        if isinstance(field, model.OutputsField):
            return self._compile_outputs_field(
                field,
                unit=unit,
                owner_label=f"agent {agent_name}",
                review_output_contexts=review_output_contexts,
                route_output_contexts=route_output_contexts,
                excluded_output_keys=(
                    frozenset({final_output.output_key}) if final_output is not None else frozenset()
                ),
            )
        if isinstance(field, model.AnalysisField):
            analysis_unit, analysis_decl = self._resolve_analysis_ref(field.value, unit=unit)
            return self._compile_analysis_decl(analysis_decl, unit=analysis_unit)
        if isinstance(field, model.DecisionField):
            decision_unit, decision_decl = self._resolve_decision_ref(field.value, unit=unit)
            return self._compile_decision_decl(decision_decl, unit=decision_unit)
        if isinstance(field, model.SkillsField):
            return self._compile_skills_field(field, unit=unit)
        if isinstance(field, model.ReviewField):
            review_unit, review_decl = self._resolve_review_ref(field.value, unit=unit)
            if review_decl.abstract:
                raise CompileError(
                    "Concrete agents may not attach abstract reviews directly: "
                    f"{_dotted_decl_name(review_unit.module_parts, review_decl.name)}"
                )
            return self._compile_review_decl(
                review_decl,
                unit=review_unit,
                agent_contract=agent_contract,
                owner_label=f"agent {agent_name} review",
            )
        if isinstance(field, model.FinalOutputField):
            if final_output is None or final_output.section is None:
                raise CompileError(
                    f"Internal compiler error: missing compiled final_output in agent {agent_name}"
                )
            return final_output.section

        raise CompileError(
            f"Unsupported agent field in {agent_name}: {type(field).__name__}"
        )

    def _compile_final_output_spec(
        self,
        *,
        agent_name: str,
        field: model.FinalOutputField,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]],
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]],
        fallback_review_semantics: ReviewSemanticContext | None = None,
    ) -> CompiledFinalOutputSpec:
        owner_label = f"agent {agent_name} final_output"
        output_unit, output_decl = self._resolve_final_output_decl(
            field.value,
            unit=unit,
            owner_label=owner_label,
        )
        output_key = (output_unit.module_parts, output_decl.name)
        if output_key not in agent_contract.outputs:
            raise CompileError(
                "E212 final_output output is not emitted by the concrete turn in "
                f"agent {agent_name}: {_dotted_decl_name(output_unit.module_parts, output_decl.name)}"
            )
        review_semantics = self._review_output_context_for_key(
            review_output_contexts,
            output_key,
        )
        if review_semantics is None:
            review_semantics = fallback_review_semantics
        route_semantics = self._route_output_context_for_key(
            route_output_contexts,
            output_key,
        )

        scalar_items, section_items, extras = self._split_record_items(
            output_decl.items,
            scalar_keys={"target", "shape", "requirement"},
            section_keys={"files"},
            owner_label=f"output {output_decl.name}",
        )
        target_item = scalar_items.get("target")
        shape_item = scalar_items.get("shape")
        requirement_item = scalar_items.get("requirement")
        files_section = section_items.get("files")

        if (
            files_section is not None
            or target_item is None
            or shape_item is None
            or not isinstance(target_item.value, model.NameRef)
            or not self._is_builtin_turn_response_target_ref(target_item.value)
        ):
            raise CompileError(
                "E213 final_output must designate one TurnResponse output, not files or another "
                f"target, in agent {agent_name}: {_dotted_decl_name(output_unit.module_parts, output_decl.name)}"
            )
        explicit_render_profile, render_profile = self._resolve_output_render_profiles(
            output_decl,
            unit=output_unit,
            files_section=files_section,
            shape_item=shape_item,
        )
        self._validate_output_guard_sections(
            output_decl,
            unit=output_unit,
            allow_review_semantics=review_semantics is not None,
            allow_route_semantics=route_semantics is not None,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
        )

        requirement = (
            self._display_symbol_value(
                requirement_item.value,
                unit=output_unit,
                owner_label=f"output {output_decl.name}",
                surface_label="output fields",
            )
            if requirement_item is not None
            else None
        )
        shape_name = self._final_output_shape_name(shape_item.value)
        shape_title = self._display_output_shape(
            shape_item.value,
            unit=output_unit,
            owner_label=output_decl.name,
            surface_label="output fields",
        )
        json_summary = self._resolve_final_output_json_shape_summary(
            shape_item.value,
            unit=output_unit,
        )
        section = self._compile_final_output_section(
            output_decl,
            unit=output_unit,
            requirement=requirement,
            shape_title=shape_title,
            json_summary=json_summary,
            extras=extras,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
            render_profile=render_profile,
            explicit_render_profile=explicit_render_profile,
        )
        return CompiledFinalOutputSpec(
            output_key=output_key,
            output_name=output_decl.name,
            output_title=output_decl.title,
            target_title="Turn Response",
            shape_name=shape_name,
            shape_title=shape_title,
            requirement=requirement,
            format_mode="json_schema" if json_summary is not None else "prose",
            schema_name=json_summary.schema_decl.name if json_summary is not None else None,
            schema_title=json_summary.schema_decl.title if json_summary is not None else None,
            schema_profile=json_summary.schema_profile if json_summary is not None else None,
            schema_file=json_summary.schema_file if json_summary is not None else None,
            example_file=json_summary.example_file if json_summary is not None else None,
            resolved_schema_file=json_summary.resolved_schema_file if json_summary is not None else None,
            resolved_example_file=json_summary.resolved_example_file if json_summary is not None else None,
            section=section,
        )

    def _compile_final_output_section(
        self,
        output_decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        requirement: str | None,
        shape_title: str,
        json_summary: FinalOutputJsonShapeSummary | None,
        extras: tuple[model.AnyRecordItem, ...],
        review_semantics: ReviewSemanticContext | None,
        route_semantics: RouteSemanticContext | None,
        render_profile: ResolvedRenderProfile | None,
        explicit_render_profile: ResolvedRenderProfile | None,
    ) -> CompiledSection:
        format_label = self._final_output_format_label(output_decl, unit=unit, json_summary=json_summary)
        metadata_rows = [
            ("Message kind", "Final assistant message"),
            ("Format", format_label),
            ("Shape", shape_title),
        ]
        if json_summary is not None:
            metadata_rows.append(("Schema", json_summary.schema_decl.title))
            if json_summary.schema_profile is not None:
                metadata_rows.append(("Profile", json_summary.schema_profile))
            if json_summary.schema_file is not None:
                metadata_rows.append(("Schema file", f"`{json_summary.schema_file}`"))
            if json_summary.example_file is not None:
                metadata_rows.append(("Example file", f"`{json_summary.example_file}`"))
        if requirement is not None:
            metadata_rows.append(("Requirement", requirement))

        body: list[CompiledBodyItem] = [
            "> **Final answer contract**",
            "> "
            + (
                "End the turn with one schema-backed final assistant message."
                if json_summary is not None
                else "End the turn with one final assistant message that satisfies this contract."
            ),
            "",
            *self._pipe_table_lines(("Contract", "Value"), tuple(metadata_rows)),
        ]

        if json_summary is not None and json_summary.payload_rows:
            body.extend(
                [
                    "",
                    CompiledSection(
                        title="Payload Shape",
                        body=tuple(
                            self._pipe_table_lines(
                                ("Field", "Type", "Meaning"),
                                json_summary.payload_rows,
                            )
                        ),
                    ),
                ]
            )

        if json_summary is not None and json_summary.example_text is not None:
            body.extend(
                [
                    "",
                    CompiledSection(
                        title="Example Shape",
                        body=(
                            f"```json",
                            *json_summary.example_text.rstrip("\n").splitlines(),
                            "```",
                        ),
                    ),
                ]
            )

        if output_decl.schema_ref is not None:
            schema_unit, schema_decl = self._resolve_schema_ref(output_decl.schema_ref, unit=unit)
            resolved_schema = self._resolve_schema_decl(schema_decl, unit=schema_unit)
            if not resolved_schema.sections:
                raise CompileError(
                    f"Output-attached schema must export at least one section in output {output_decl.name}: {schema_decl.name}"
                )
            body.extend(
                [
                    "",
                    CompiledSection(
                        title=f"Schema: {schema_decl.title}",
                        body=(self._compile_schema_sections_block(resolved_schema),),
                    ),
                ]
            )

        if output_decl.structure_ref is not None:
            document_unit, document_decl = self._resolve_document_ref(output_decl.structure_ref, unit=unit)
            resolved_document = self._resolve_document_decl(document_decl, unit=document_unit)
            body.extend(
                [
                    "",
                    CompiledSection(
                        title=f"Structure: {document_decl.title}",
                        body=self._compile_document_body(
                            resolved_document,
                            unit=document_unit,
                        ),
                        render_profile=explicit_render_profile or resolved_document.render_profile,
                    ),
                ]
            )

        trust_surface_section = (
            self._compile_trust_surface_section(
                output_decl,
                unit=unit,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )
            if output_decl.trust_surface
            else None
        )

        if json_summary is not None:
            body.extend(
                self._compile_output_support_items(
                    json_summary.extra_items,
                    unit=json_summary.shape_unit,
                    owner_label=f"output shape {json_summary.shape_decl.name}",
                    surface_label="final_output shape support",
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                    insert_item_spacers=True,
                )
            )
        body.extend(
            self._compile_output_support_items(
                extras,
                unit=unit,
                owner_label=f"output {output_decl.name}",
                surface_label="final_output support",
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
                trust_surface_section=trust_surface_section,
                standalone_title="Read It Cold",
                insert_item_spacers=True,
            )
        )

        return CompiledSection(
            title="Final Output",
            body=(
                CompiledSection(
                    title=output_decl.title,
                    body=tuple(body),
                    render_profile=render_profile,
                ),
            ),
        )

    def _compile_output_support_items(
        self,
        items: tuple[model.AnyRecordItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
        trust_surface_section: CompiledSection | None = None,
        standalone_title: str = "Standalone Read",
        insert_item_spacers: bool = False,
    ) -> list[CompiledBodyItem]:
        compiled: list[CompiledBodyItem] = []
        rendered_trust_surface = False
        for item in items:
            if (
                trust_surface_section is not None
                and not rendered_trust_surface
                and isinstance(item, model.RecordSection)
                and item.key == "standalone_read"
            ):
                compiled.append(trust_surface_section)
                rendered_trust_surface = True
            rendered_items = list(
                self._compile_record_item(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
            )
            if (
                isinstance(item, model.RecordSection)
                and item.key == "standalone_read"
                and standalone_title != "Standalone Read"
            ):
                rendered_items = [
                    replace(rendered, title=standalone_title)
                    if isinstance(rendered, CompiledSection)
                    else rendered
                    for rendered in rendered_items
                ]
            if compiled and insert_item_spacers:
                compiled.append("")
            compiled.extend(rendered_items)
        if trust_surface_section is not None and not rendered_trust_surface:
            if compiled and insert_item_spacers:
                compiled.append("")
            compiled.append(trust_surface_section)
        return compiled

    def _compile_inputs_field(
        self,
        field: model.InputsField,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> CompiledSection:
        return self._compile_io_field(
            field=field,
            unit=unit,
            field_kind="inputs",
            owner_label=owner_label,
        )

    def _compile_outputs_field(
        self,
        field: model.OutputsField,
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> CompiledSection | None:
        return self._compile_io_field(
            field=field,
            unit=unit,
            field_kind="outputs",
            owner_label=owner_label,
            review_output_contexts=review_output_contexts,
            route_output_contexts=route_output_contexts,
            excluded_output_keys=excluded_output_keys,
        )

    def _compile_io_field(
        self,
        field: model.InputsField | model.OutputsField,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> CompiledSection | None:
        if field.parent_ref is not None:
            resolved = self._resolve_io_field_patch(
                field,
                unit=unit,
                field_kind=field_kind,
                owner_label=owner_label,
                review_output_contexts=review_output_contexts,
                route_output_contexts=route_output_contexts,
                excluded_output_keys=excluded_output_keys,
            )
            if field_kind == "outputs" and self._resolved_io_body_is_empty(resolved):
                return None
            return self._compile_resolved_io_body(resolved)

        if isinstance(field.value, tuple):
            if field.title is None:
                raise CompileError(
                    f"Internal compiler error: {field_kind} field is missing title in {owner_label}"
                )
            compiled_section = CompiledSection(
                title=field.title,
                body=self._compile_contract_bucket_items(
                    field.value,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=f"{field_kind} field `{field.title}`",
                    review_output_contexts=review_output_contexts,
                    route_output_contexts=route_output_contexts,
                    excluded_output_keys=excluded_output_keys,
                ),
            )
            if field_kind == "outputs" and not compiled_section.body:
                return None
            return compiled_section

        if isinstance(field.value, model.NameRef):
            resolved = self._resolve_io_field_ref(
                field.value,
                unit=unit,
                field_kind=field_kind,
                review_output_contexts=review_output_contexts,
                route_output_contexts=route_output_contexts,
                excluded_output_keys=excluded_output_keys,
            )
            if field_kind == "outputs" and self._resolved_io_body_is_empty(resolved):
                return None
            return self._compile_resolved_io_body(resolved)

        raise CompileError(
            f"Internal compiler error: unsupported {field_kind} field value in {owner_label}: "
            f"{type(field.value).__name__}"
        )

    def _compile_resolved_io_body(self, io_body: ResolvedIoBody) -> CompiledSection:
        body: list[CompiledBodyItem] = list(io_body.preamble)
        for item in io_body.items:
            body.append(item.section)
        return CompiledSection(title=io_body.title, body=tuple(body))

    def _compile_skills_field(
        self, field: model.SkillsField, *, unit: IndexedUnit
    ) -> CompiledSection:
        return self._compile_resolved_skills(
            self._resolve_skills_value(
                field.value,
                unit=unit,
                owner_label="agent skills field",
            )
        )

    def _compile_contract_bucket_items(
        self,
        items: tuple[model.RecordItem, ...],
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> tuple[CompiledBodyItem, ...]:
        return self._resolve_contract_bucket_items(
            items,
            unit=unit,
            field_kind=field_kind,
            owner_label=owner_label,
            review_output_contexts=review_output_contexts,
            route_output_contexts=route_output_contexts,
            excluded_output_keys=excluded_output_keys,
        ).body

    def _compile_contract_bucket_ref(
        self,
        item: model.RecordRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        review_output_contexts: frozenset[tuple[OutputDeclKey, ReviewSemanticContext]] = frozenset(),
        route_output_contexts: frozenset[tuple[OutputDeclKey, RouteSemanticContext]] = frozenset(),
        excluded_output_keys: frozenset[OutputDeclKey] = frozenset(),
    ) -> CompiledSection | None:
        resolved_ref = self._resolve_contract_bucket_ref_entry(
            item,
            unit=unit,
            field_kind=field_kind,
            owner_label=owner_label,
            review_output_contexts=review_output_contexts,
            route_output_contexts=route_output_contexts,
            excluded_output_keys=excluded_output_keys,
        )
        if resolved_ref is None:
            return None
        section, _artifact = resolved_ref
        return section

    def _compile_resolved_skills(self, skills_body: ResolvedSkillsBody) -> CompiledSection:
        body: list[CompiledBodyItem] = list(skills_body.preamble)
        for item in skills_body.items:
            if isinstance(item, ResolvedSkillsSection):
                body.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_resolved_skills_section_items(item.items),
                    )
                )
                continue
            body.append(self._compile_resolved_skill_entry(item))
        return CompiledSection(title=skills_body.title, body=tuple(body))

    def _compile_resolved_skills_section_items(
        self,
        items: tuple[ResolvedSkillsSectionBodyItem, ...],
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                body.append(item)
                continue
            body.append(self._compile_resolved_skill_entry(item))
        return tuple(body)

    def _compile_resolved_skill_entry(self, entry: ResolvedSkillEntry) -> CompiledSection:
        target_unit = entry.target_unit
        skill_decl = entry.skill_decl
        scalar_items, _section_items, extras = self._split_record_items(
            skill_decl.items,
            scalar_keys={"purpose"},
            owner_label=f"skill {skill_decl.name}",
        )
        purpose_item = scalar_items.get("purpose")
        if purpose_item is None or not isinstance(purpose_item.value, str):
            raise CompileError(f"Skill is missing string purpose: {skill_decl.name}")

        metadata_scalars, _metadata_sections, metadata_extras = self._split_record_items(
            entry.items,
            scalar_keys={"requirement", "reason"},
            owner_label=f"skill reference {skill_decl.name}",
        )

        body: list[CompiledBodyItem] = []
        purpose_body: list[CompiledBodyItem] = [
            self._interpolate_authored_prose_string(
                purpose_item.value,
                unit=target_unit,
                owner_label=f"skill {skill_decl.name}",
                surface_label="skill purpose",
            )
        ]
        requirement = metadata_scalars.get("requirement")
        if (
            requirement is not None
            and self._value_to_symbol(
                requirement.value,
                unit=entry.metadata_unit,
                owner_label=f"skill reference {skill_decl.name}",
                surface_label="skill reference metadata",
            )
            == "Required"
        ):
            purpose_body.extend(
                [
                    "",
                    "This skill is required for this role. If you cannot locate it, stop and escalate instead of guessing.",
                ]
            )
        body.append(CompiledSection(title="Purpose", body=tuple(purpose_body)))

        for extra in extras:
            body.extend(
                self._compile_record_item(
                    extra,
                    unit=target_unit,
                    owner_label=f"skill {skill_decl.name}",
                    surface_label="skill prose",
                )
            )

        reason = metadata_scalars.get("reason")
        if reason is not None:
            if not isinstance(reason.value, str):
                raise CompileError(
                    f"Skill reference reason must be a string in {skill_decl.name}"
                )
            body.append(
                CompiledSection(
                    title="Reason",
                    body=(
                        self._interpolate_authored_prose_string(
                            reason.value,
                            unit=entry.metadata_unit,
                            owner_label=f"skill reference {skill_decl.name}",
                            surface_label="skill reason",
                        ),
                    ),
                )
            )

        for extra in metadata_extras:
            body.extend(
                self._compile_record_item(
                    extra,
                    unit=entry.metadata_unit,
                    owner_label=f"skill reference {skill_decl.name}",
                    surface_label="skill reference prose",
                )
            )

        return CompiledSection(title=skill_decl.title, body=tuple(body))

    def _compile_analysis_decl(
        self,
        decl: model.AnalysisDecl,
        *,
        unit: IndexedUnit,
    ) -> CompiledSection:
        resolved = self._resolve_analysis_decl(decl, unit=unit)
        body: list[CompiledBodyItem] = list(resolved.preamble)
        for item in resolved.items:
            if body and body[-1] != "":
                body.append("")
            body.append(
                CompiledSection(
                    title=item.title,
                    body=self._compile_analysis_section_body(item.items, unit=item.unit),
                    semantic_target="analysis.stages",
                )
            )
        return CompiledSection(
            title=resolved.title,
            body=tuple(body),
            render_profile=resolved.render_profile or ResolvedRenderProfile(name="ContractMarkdown"),
        )

    def _compile_analysis_section_body(
        self,
        items: tuple[ResolvedAnalysisSectionItem, ...],
        *,
        unit: IndexedUnit,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                body.append(item)
                continue
            if isinstance(item, ResolvedSectionRef):
                body.append(f"- {item.label}")
                continue
            if isinstance(item, model.ProveStmt):
                body.append(
                    f"Prove {item.target_title} from {self._render_analysis_basis(item.basis, unit=unit)}."
                )
                continue
            if isinstance(item, model.DeriveStmt):
                body.append(
                    f"Derive {item.target_title} from {self._render_analysis_basis(item.basis, unit=unit)}."
                )
                continue
            if isinstance(item, model.ClassifyStmt):
                _enum_unit, enum_decl = self._resolve_enum_ref(item.enum_ref, unit=unit)
                body.append(f"Classify {item.target_title} using {enum_decl.title}.")
                continue
            if isinstance(item, model.CompareStmt):
                sentence = (
                    f"Compare {item.target_title} against {self._render_analysis_basis(item.basis, unit=unit)}."
                )
                if item.using_expr is not None:
                    sentence += (
                        f" Use {self._render_analysis_using_expr(item.using_expr, unit=unit)} as the comparison basis."
                    )
                body.append(sentence)
                continue
            if isinstance(item, model.DefendStmt):
                body.append(
                    f"Defend {item.target_title} using {self._render_analysis_basis(item.basis, unit=unit)}."
                )
                continue
            raise CompileError(
                f"Internal compiler error: unsupported analysis item {type(item).__name__}"
            )
        return tuple(body)

    def _compile_decision_decl(
        self,
        decl: model.DecisionDecl,
        *,
        unit: IndexedUnit,
    ) -> CompiledSection:
        body: list[CompiledBodyItem] = [
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=f"decision {decl.name}",
                surface_label="decision prose",
                ambiguous_label="decision prose interpolation ref",
            )
            for line in decl.body.preamble
        ]
        for item in decl.body.items:
            if isinstance(item, model.DecisionMinimumCandidates):
                body.append(
                    f"Build at least {item.count} candidates before choosing a winner."
                )
                continue
            if isinstance(item, model.DecisionRequiredItem):
                body.append(self._render_decision_required_item(item))
                continue
            if isinstance(item, model.DecisionChooseWinner):
                body.append("Choose exactly one winner.")
                continue
            if isinstance(item, model.DecisionRankBy):
                dimensions = self._natural_language_join(
                    [_humanize_key(dimension) for dimension in item.dimensions]
                )
                body.append(f"Rank by {dimensions}.")
                continue
            raise CompileError(
                f"Internal compiler error: unsupported decision item {type(item).__name__}"
            )
        render_profile = (
            self._resolve_render_profile_ref(decl.render_profile_ref, unit=unit)
            if decl.render_profile_ref is not None
            else ResolvedRenderProfile(name="ContractMarkdown")
        )
        return CompiledSection(
            title=decl.title,
            body=tuple(body),
            render_profile=render_profile,
        )

    def _compile_schema_decl(
        self,
        decl: model.SchemaDecl,
        *,
        unit: IndexedUnit,
    ) -> CompiledSection:
        resolved = self._resolve_schema_decl(decl, unit=unit)
        body: list[CompiledBodyItem] = list(resolved.preamble)
        blocks: list[CompiledReadableBlock] = []
        if resolved.sections:
            blocks.append(self._compile_schema_sections_block(resolved))
        if resolved.gates:
            blocks.append(self._compile_schema_gates_block(resolved))
        if resolved.artifacts:
            blocks.append(self._compile_schema_artifacts_block(resolved))
        if resolved.groups:
            blocks.append(self._compile_schema_groups_block(resolved))
        for index, block in enumerate(blocks):
            if body and index == 0:
                body.append("")
            elif index > 0:
                body.append("")
            body.append(block)
        return CompiledSection(
            title=resolved.title,
            body=tuple(body),
            render_profile=resolved.render_profile or ResolvedRenderProfile(name="ContractMarkdown"),
        )

    def _compile_schema_sections_block(
        self,
        schema_body: ResolvedSchemaBody,
    ) -> CompiledSection:
        return CompiledSection(
            title="Required Sections",
            body=tuple(
                CompiledSection(title=item.title, body=item.body) for item in schema_body.sections
            ),
        )

    def _compile_schema_gates_block(
        self,
        schema_body: ResolvedSchemaBody,
    ) -> CompiledSection:
        return CompiledSection(
            title="Contract Gates",
            body=tuple(
                CompiledSection(title=item.title, body=item.body) for item in schema_body.gates
            ),
        )

    def _compile_schema_artifacts_block(
        self,
        schema_body: ResolvedSchemaBody,
    ) -> CompiledBulletsBlock:
        return CompiledBulletsBlock(
            title="Artifact Inventory",
            items=tuple(item.title for item in schema_body.artifacts),
        )

    def _compile_schema_groups_block(
        self,
        schema_body: ResolvedSchemaBody,
    ) -> CompiledSection:
        artifact_titles = {item.key: item.title for item in schema_body.artifacts}
        body: list[str] = []
        for group in schema_body.groups:
            body.append(f"- {group.title}")
            for member_key in group.members:
                body.append(f"  - {artifact_titles[member_key]}")
        return CompiledSection(title="Surface Groups", body=tuple(body))

    def _compile_document_decl(
        self,
        decl: model.DocumentDecl,
        *,
        unit: IndexedUnit,
    ) -> CompiledSection:
        resolved = self._resolve_document_decl(decl, unit=unit)
        return CompiledSection(
            title=resolved.title,
            body=self._compile_document_body(resolved, unit=unit),
            render_profile=resolved.render_profile or ResolvedRenderProfile(name="ContractMarkdown"),
        )

    def _compile_document_body(
        self,
        document_body: ResolvedDocumentBody,
        *,
        unit: IndexedUnit,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = list(document_body.preamble)
        for item in document_body.items:
            if body and body[-1] != "":
                body.append("")
            body.append(self._compile_document_block(item, unit=unit))
        return tuple(body)

    def _compile_document_block(
        self,
        block: model.DocumentBlock,
        *,
        unit: IndexedUnit,
    ) -> CompiledReadableBlock:
        when_text = self._readable_guard_text(block.when_expr, unit=unit)
        title = None if block.kind == "properties" and block.anonymous else (
            block.title or _humanize_key(block.key)
        )
        if block.kind == "section":
            return CompiledSection(
                title=title or _humanize_key(block.key),
                body=self._compile_document_section_payload(block.payload, unit=unit),
                requirement=block.requirement,
                when_text=when_text,
                emit_metadata=block.requirement is not None or block.when_expr is not None,
                semantic_target=_semantic_render_target_for_block(block.kind, block.key),
            )
        if block.kind in {"sequence", "bullets", "checklist"}:
            compiled_cls = {
                "sequence": CompiledSequenceBlock,
                "bullets": CompiledBulletsBlock,
                "checklist": CompiledChecklistBlock,
            }[block.kind]
            return compiled_cls(
                title=title or _humanize_key(block.key),
                items=self._compile_readable_list_payload(block.payload),
                requirement=block.requirement,
                when_text=when_text,
                item_schema=block.item_schema,
                semantic_target=_semantic_render_target_for_block(block.kind, block.key),
            )
        if block.kind == "properties":
            payload = self._compile_readable_properties_payload(block.payload)
            return CompiledPropertiesBlock(
                title=title,
                entries=payload.entries,
                requirement=block.requirement,
                when_text=when_text,
                anonymous=block.anonymous,
            )
        if block.kind == "definitions":
            return CompiledDefinitionsBlock(
                title=title or _humanize_key(block.key),
                items=self._compile_readable_definitions_payload(block.payload),
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "table":
            return CompiledTableBlock(
                title=title or _humanize_key(block.key),
                table=self._compile_resolved_readable_table_payload(block.payload, unit=unit),
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "guard":
            if when_text is None:
                raise CompileError("Readable guard shells must define a guard expression.")
            return CompiledGuardBlock(
                title=title or _humanize_key(block.key),
                body=self._compile_document_section_payload(block.payload, unit=unit),
                when_text=when_text,
            )
        if block.kind == "callout":
            payload = self._compile_readable_callout_payload(block.payload)
            return CompiledCalloutBlock(
                title=title or _humanize_key(block.key),
                body=payload.body,
                kind=payload.kind,
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "code":
            payload = self._compile_readable_code_payload(block.payload)
            return CompiledCodeBlock(
                title=title or _humanize_key(block.key),
                text=payload.text,
                language=payload.language,
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind in {"markdown", "html"}:
            payload = self._compile_readable_raw_text_payload(block.payload)
            return CompiledRawTextBlock(
                title=title or _humanize_key(block.key),
                text=payload.text,
                kind=block.kind,
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "footnotes":
            payload = self._compile_readable_footnotes_payload(block.payload)
            return CompiledFootnotesBlock(
                title=title or _humanize_key(block.key),
                entries=payload.entries,
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "image":
            payload = self._compile_readable_image_payload(block.payload)
            return CompiledImageBlock(
                title=title or _humanize_key(block.key),
                src=payload.src,
                alt=payload.alt,
                caption=payload.caption,
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "rule":
            return CompiledRuleBlock(
                requirement=block.requirement,
                when_text=when_text,
            )
        raise CompileError(
            f"Internal compiler error: unsupported document block kind {block.kind}"
        )

    def _compile_document_section_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
    ) -> tuple[CompiledBodyItem, ...]:
        if not isinstance(payload, tuple):
            raise CompileError("Document section payload must stay block-like.")
        body: list[CompiledBodyItem] = []
        for item in payload:
            if isinstance(item, (str, model.EmphasizedLine)):
                body.append(item)
                continue
            body.append(self._compile_document_block(item, unit=unit))
        return tuple(body)

    def _compile_readable_list_payload(
        self,
        payload: model.ReadablePayload,
    ) -> tuple[model.ProseLine, ...]:
        if not isinstance(payload, tuple):
            raise CompileError("Readable list payload must stay list-shaped.")
        items: list[model.ProseLine] = []
        for item in payload:
            if not isinstance(item, model.ReadableListItem):
                raise CompileError("Readable list payload contains an invalid item.")
            items.append(item.text)
        return tuple(items)

    def _compile_readable_definitions_payload(
        self,
        payload: model.ReadablePayload,
    ) -> tuple[model.ReadableDefinitionItem, ...]:
        if not isinstance(payload, tuple):
            raise CompileError("Readable definitions payload must stay definition-shaped.")
        items: list[model.ReadableDefinitionItem] = []
        for item in payload:
            if not isinstance(item, model.ReadableDefinitionItem):
                raise CompileError("Readable definitions payload contains an invalid item.")
            items.append(item)
        return tuple(items)

    def _compile_readable_properties_payload(
        self,
        payload: model.ReadablePayload,
    ) -> model.ReadablePropertiesData:
        if not isinstance(payload, model.ReadablePropertiesData):
            raise CompileError("Readable properties payload must stay properties-shaped.")
        return payload

    def _compile_readable_table_payload(
        self,
        payload: model.ReadablePayload,
    ) -> model.ReadableTableData:
        if not isinstance(payload, model.ReadableTableData):
            raise CompileError("Readable table payload must stay table-shaped.")
        if not payload.columns:
            raise CompileError("Readable table must declare at least one column.")
        return payload

    def _compile_resolved_readable_table_payload(
        self,
        payload: model.ReadablePayload,
        *,
        unit: IndexedUnit,
    ) -> CompiledTableData:
        table = self._compile_readable_table_payload(payload)
        compiled_rows: list[CompiledTableRow] = []
        for row in table.rows:
            compiled_cells: list[CompiledTableCell] = []
            for cell in row.cells:
                if cell.body is not None:
                    compiled_cells.append(
                        CompiledTableCell(
                            key=cell.key,
                            body=self._compile_document_section_payload(cell.body, unit=unit),
                        )
                    )
                    continue
                compiled_cells.append(CompiledTableCell(key=cell.key, text=cell.text or ""))
            compiled_rows.append(CompiledTableRow(key=row.key, cells=tuple(compiled_cells)))

        return CompiledTableData(
            columns=tuple(
                CompiledTableColumn(key=column.key, title=column.title, body=column.body)
                for column in table.columns
            ),
            rows=tuple(compiled_rows),
            notes=table.notes,
            row_schema=table.row_schema,
        )

    def _compile_readable_callout_payload(
        self,
        payload: model.ReadablePayload,
    ) -> model.ReadableCalloutData:
        if not isinstance(payload, model.ReadableCalloutData):
            raise CompileError("Readable callout payload must stay callout-shaped.")
        return payload

    def _compile_readable_code_payload(
        self,
        payload: model.ReadablePayload,
    ) -> model.ReadableCodeData:
        if not isinstance(payload, model.ReadableCodeData):
            raise CompileError("Readable code payload must stay code-shaped.")
        return payload

    def _compile_readable_raw_text_payload(
        self,
        payload: model.ReadablePayload,
    ) -> model.ReadableRawTextData:
        if not isinstance(payload, model.ReadableRawTextData):
            raise CompileError("Readable raw text payload must stay text-shaped.")
        if "\n" not in payload.text:
            raise CompileError("Raw text readable blocks must use a multiline string.")
        return payload

    def _compile_readable_footnotes_payload(
        self,
        payload: model.ReadablePayload,
    ) -> model.ReadableFootnotesData:
        if not isinstance(payload, model.ReadableFootnotesData):
            raise CompileError("Readable footnotes payload must stay footnotes-shaped.")
        return payload

    def _compile_readable_image_payload(
        self,
        payload: model.ReadablePayload,
    ) -> model.ReadableImageData:
        if not isinstance(payload, model.ReadableImageData):
            raise CompileError("Readable image payload must stay image-shaped.")
        return payload

    def _compile_input_decl(self, decl: model.InputDecl, *, unit: IndexedUnit) -> CompiledSection:
        scalar_items, _section_items, extras = self._split_record_items(
            decl.items,
            scalar_keys={"source", "shape", "requirement"},
            owner_label=f"input {decl.name}",
        )
        source_item = scalar_items.get("source")
        shape_item = scalar_items.get("shape")
        requirement_item = scalar_items.get("requirement")
        if source_item is None:
            raise CompileError(f"Input is missing typed source: {decl.name}")
        if not isinstance(source_item.value, model.NameRef):
            raise CompileError(f"Input source must stay typed: {decl.name}")
        if shape_item is None:
            raise CompileError(f"Input is missing shape: {decl.name}")
        if requirement_item is None:
            raise CompileError(f"Input is missing requirement: {decl.name}")

        source_spec = self._resolve_input_source_spec(source_item.value, unit=unit)
        body: list[CompiledBodyItem] = [f"- Source: {source_spec.title}"]
        body.extend(
            self._compile_config_lines(
                source_item.body or (),
                spec=source_spec,
                unit=unit,
                owner_label=f"input {decl.name} source",
            )
        )
        body.append(
            f"- Shape: {self._display_symbol_value(shape_item.value, unit=unit, owner_label=f'input {decl.name}', surface_label='input fields')}"
        )
        body.append(
            f"- Requirement: {self._display_symbol_value(requirement_item.value, unit=unit, owner_label=f'input {decl.name}', surface_label='input fields')}"
        )
        if decl.structure_ref is not None:
            document_unit, document_decl = self._resolve_document_ref(decl.structure_ref, unit=unit)
            if not self._is_markdown_shape_value(shape_item.value, unit=unit):
                raise CompileError(
                    f"Input structure requires a markdown-bearing shape in input {decl.name}"
                )
            body.append(f"- Structure: {document_decl.title}")
            body.append("")
            body.append(
                CompiledSection(
                    title=f"Structure: {document_decl.title}",
                    body=self._compile_document_body(
                        self._resolve_document_decl(document_decl, unit=document_unit),
                        unit=document_unit,
                    ),
                )
            )

        if extras:
            body.append("")
            body.extend(
                self._compile_record_support_items(
                    extras,
                    unit=unit,
                    owner_label=f"input {decl.name}",
                    surface_label="input prose",
                )
            )

        return CompiledSection(title=decl.title, body=tuple(body))

    def _compile_output_decl(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        allow_review_semantics: bool = False,
        allow_route_semantics: bool = False,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
    ) -> CompiledSection:
        self._validate_output_guard_sections(
            decl,
            unit=unit,
            allow_review_semantics=allow_review_semantics,
            allow_route_semantics=allow_route_semantics,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
        )
        scalar_items, section_items, extras = self._split_record_items(
            decl.items,
            scalar_keys={"target", "shape", "requirement"},
            section_keys={"files"},
            owner_label=f"output {decl.name}",
        )

        target_item = scalar_items.get("target")
        shape_item = scalar_items.get("shape")
        requirement_item = scalar_items.get("requirement")
        files_section = section_items.get("files")

        if files_section is not None and (target_item is not None or shape_item is not None):
            raise CompileError(
                f"Output mixes `files` with `target` or `shape`: {decl.name}"
            )
        if files_section is None and (target_item is None or shape_item is None):
            raise CompileError(
                f"Output must define either `files` or both `target` and `shape`: {decl.name}"
            )

        explicit_render_profile, render_profile = self._resolve_output_render_profiles(
            decl,
            unit=unit,
            files_section=files_section,
            shape_item=shape_item,
        )

        body: list[CompiledBodyItem] = []
        if files_section is not None:
            body.extend(
                self._compile_output_files(
                    files_section,
                    unit=unit,
                    output_name=decl.name,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
            )
        else:
            if not isinstance(target_item.value, model.NameRef):
                raise CompileError(f"Output target must stay typed: {decl.name}")
            target_spec = self._resolve_output_target_spec(target_item.value, unit=unit)
            body.append(f"- Target: {target_spec.title}")
            body.extend(
                self._compile_config_lines(
                    target_item.body or (),
                    spec=target_spec,
                    unit=unit,
                    owner_label=f"output {decl.name} target",
                )
            )
            body.append(
                f"- Shape: {self._display_output_shape(shape_item.value, unit=unit, owner_label=decl.name, surface_label='output fields')}"
            )

        if requirement_item is not None:
            body.append(
                f"- Requirement: {self._display_symbol_value(requirement_item.value, unit=unit, owner_label=f'output {decl.name}', surface_label='output fields')}"
            )
        if decl.schema_ref is not None:
            schema_unit, schema_decl = self._resolve_schema_ref(decl.schema_ref, unit=unit)
            resolved_schema = self._resolve_schema_decl(schema_decl, unit=schema_unit)
            if not resolved_schema.sections:
                raise CompileError(
                    f"Output-attached schema must export at least one section in output {decl.name}: {schema_decl.name}"
                )
            body.append(f"- Schema: {schema_decl.title}")
            body.append("")
            body.append(self._compile_schema_sections_block(resolved_schema))
        if decl.structure_ref is not None:
            if files_section is not None:
                raise CompileError(
                    f"Output structure requires one markdown-bearing output artifact in {decl.name}"
                )
            if shape_item is None or not self._is_markdown_shape_value(shape_item.value, unit=unit):
                raise CompileError(
                    f"Output structure requires a markdown-bearing shape in output {decl.name}"
                )
            document_unit, document_decl = self._resolve_document_ref(decl.structure_ref, unit=unit)
            resolved_document = self._resolve_document_decl(document_decl, unit=document_unit)
            body.append(f"- Structure: {document_decl.title}")
            body.append("")
            body.append(
                CompiledSection(
                    title=f"Structure: {document_decl.title}",
                    body=self._compile_document_body(
                        resolved_document,
                        unit=document_unit,
                    ),
                    render_profile=explicit_render_profile or resolved_document.render_profile,
                )
            )

        trust_surface_section = (
            self._compile_trust_surface_section(
                decl,
                unit=unit,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )
            if decl.trust_surface
            else None
        )

        if extras:
            support_items = self._compile_output_support_items(
                extras,
                unit=unit,
                owner_label=f"output {decl.name}",
                surface_label="output prose",
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
                trust_surface_section=trust_surface_section,
            )
            body.append("")
            body.extend(support_items)
        elif trust_surface_section is not None:
            body.append("")
            body.append(trust_surface_section)

        return CompiledSection(
            title=decl.title,
            body=tuple(body),
            render_profile=render_profile,
        )

    def _compile_review_decl(
        self,
        review_decl: model.ReviewDecl,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> CompiledSection:
        resolved = self._resolve_review_decl(review_decl, unit=unit)
        if resolved.comment_output is None:
            raise CompileError(f"Review is missing comment_output: {review_decl.name}")
        if resolved.fields is None:
            raise CompileError(f"Review is missing fields: {review_decl.name}")
        if resolved.cases:
            return self._compile_case_selected_review_decl(
                review_decl,
                resolved=resolved,
                unit=unit,
                agent_contract=agent_contract,
                owner_label=owner_label,
            )
        if resolved.subject is None:
            raise CompileError(f"Review is missing subject: {review_decl.name}")
        if resolved.contract is None:
            raise CompileError(f"Review is missing contract: {review_decl.name}")

        subjects = self._resolve_review_subjects(
            resolved.subject,
            unit=unit,
            owner_label=owner_label,
        )
        subject_keys = {
            (subject_unit.module_parts, subject_decl.name) for subject_unit, subject_decl in subjects
        }
        if resolved.subject_map is not None:
            self._resolved_review_subject_map(
                resolved.subject_map,
                unit=unit,
                owner_label=owner_label,
                subject_keys=subject_keys,
            )
        contract_spec = self._resolve_review_contract_spec(
            resolved.contract.contract_ref,
            unit=unit,
            owner_label=owner_label,
        )
        comment_output_unit, comment_output_decl = self._resolve_output_decl(
            resolved.comment_output.output_ref,
            unit=unit,
        )
        comment_output_key = (comment_output_unit.module_parts, comment_output_decl.name)
        if comment_output_key not in agent_contract.outputs:
            raise CompileError(
                f"Review comment_output must be emitted by the concrete turn in {owner_label}: "
                f"{comment_output_decl.name}"
            )

        pre_sections: list[model.ReviewSection] = []
        on_accept: model.ReviewOutcomeSection | None = None
        on_reject: model.ReviewOutcomeSection | None = None
        for item in resolved.items:
            if isinstance(item, model.ReviewSection):
                pre_sections.append(item)
                continue
            if item.key == "on_accept":
                on_accept = item
            elif item.key == "on_reject":
                on_reject = item

        if on_accept is None:
            raise CompileError(f"Review is missing on_accept: {review_decl.name}")
        if on_reject is None:
            raise CompileError(f"Review is missing on_reject: {review_decl.name}")

        section_titles = {section.key: self._review_section_title(section) for section in pre_sections}
        gate_observation = self._review_gate_observation(comment_output_decl)
        accept_gate_count = 0
        any_block_gates = False
        for section in pre_sections:
            accept_gate_count += self._count_review_accept_stmts(section.items)
            any_block_gates = any_block_gates or self._review_items_contain_blocks(section.items)
            self._validate_review_pre_outcome_items(
                section.items,
                unit=unit,
                owner_label=f"{owner_label}.{section.key}",
                contract_spec=contract_spec,
                section_titles=section_titles,
                agent_contract=agent_contract,
            )
        if accept_gate_count != 1:
            raise CompileError(
                f"Review must define exactly one accept gate in {owner_label}: found {accept_gate_count}"
            )
        pre_outcome_branches = self._resolve_review_pre_outcome_branches(
            pre_sections,
            unit=unit,
            contract_spec=contract_spec,
            section_titles=section_titles,
            owner_label=owner_label,
            gate_observation=gate_observation,
        )
        accept_gate_branches = tuple(
            branch for branch in pre_outcome_branches if branch.verdict == _REVIEW_VERDICT_TEXT["accept"]
        )
        reject_gate_branches = tuple(
            branch
            for branch in pre_outcome_branches
            if branch.verdict == _REVIEW_VERDICT_TEXT["changes_requested"]
        )

        carried_fields = {
            field_name
            for field_name in (
                *self._collect_review_carried_fields(on_accept.items),
                *self._collect_review_carried_fields(on_reject.items),
            )
        }
        field_bindings = self._validate_review_field_bindings(
            resolved.fields,
            output_decl=comment_output_decl,
            output_unit=comment_output_unit,
            owner_label=owner_label,
            require_blocked_gate=any_block_gates,
            require_active_mode="active_mode" in carried_fields,
            require_trigger_reason="trigger_reason" in carried_fields,
        )
        review_semantics = ReviewSemanticContext(
            review_module_parts=unit.module_parts,
            output_module_parts=comment_output_unit.module_parts,
            output_name=comment_output_decl.name,
            field_bindings=tuple(field_bindings.items()),
            contract_gates=contract_spec.gates,
        )

        accept_branches = self._validate_review_outcome_section(
            on_accept,
            unit=unit,
            owner_label=owner_label,
            agent_contract=agent_contract,
            comment_output_decl=comment_output_decl,
            comment_output_unit=comment_output_unit,
            next_owner_field_path=field_bindings["next_owner"],
            field_bindings=field_bindings,
            subject_keys=subject_keys,
            subject_map=resolved.subject_map,
            blocked_gate_required=any_block_gates,
            gate_branches=accept_gate_branches,
        )
        reject_branches = self._validate_review_outcome_section(
            on_reject,
            unit=unit,
            owner_label=owner_label,
            agent_contract=agent_contract,
            comment_output_decl=comment_output_decl,
            comment_output_unit=comment_output_unit,
            next_owner_field_path=field_bindings["next_owner"],
            field_bindings=field_bindings,
            subject_keys=subject_keys,
            subject_map=resolved.subject_map,
            blocked_gate_required=any_block_gates,
            gate_branches=reject_gate_branches,
        )
        self._validate_review_current_artifact_alignment(
            (*accept_branches, *reject_branches),
            output_decl=comment_output_decl,
            output_unit=comment_output_unit,
            owner_label=owner_label,
        )
        self._validate_review_optional_field_alignment(
            (*accept_branches, *reject_branches),
            output_decl=comment_output_decl,
            output_unit=comment_output_unit,
            field_bindings=field_bindings,
            owner_label=owner_label,
        )

        body: list[CompiledBodyItem] = [
            self._render_review_subject_summary(subjects),
            f"Shared review contract: {contract_spec.title}.",
        ]
        for section in pre_sections:
            if body and body[-1] != "":
                body.append("")
            body.append(
                CompiledSection(
                    title=self._review_section_title(section),
                    body=self._compile_review_pre_outcome_section_body(
                        section.items,
                        unit=unit,
                        contract_spec=contract_spec,
                        section_titles=section_titles,
                        owner_label=f"{owner_label}.{section.key}",
                        review_semantics=review_semantics,
                    ),
                    semantic_target=(
                        "review.contract_checks" if section.key == "contract_checks" else None
                    ),
                )
            )

        for key, section in (("on_accept", on_accept), ("on_reject", on_reject)):
            if body and body[-1] != "":
                body.append("")
            body.append(
                CompiledSection(
                    title=section.title or ("If Accepted" if key == "on_accept" else "If Rejected"),
                    body=self._compile_review_outcome_section_body(
                        section.items,
                        unit=unit,
                        owner_label=f"{owner_label}.{key}",
                        review_semantics=review_semantics,
                    ),
                )
            )

        return CompiledSection(title=resolved.title, body=tuple(body))

    def _compile_case_selected_review_decl(
        self,
        review_decl: model.ReviewDecl,
        *,
        resolved: ResolvedReviewBody,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> CompiledSection:
        if resolved.selector is None:
            raise CompileError(
                f"Case-selected review is missing selector: {review_decl.name}"
            )
        if resolved.subject is not None or resolved.contract is not None or resolved.subject_map is not None:
            raise CompileError(
                f"Case-selected review must declare subject and contract inside cases: {review_decl.name}"
            )

        comment_output_unit, comment_output_decl = self._resolve_output_decl(
            resolved.comment_output.output_ref,
            unit=unit,
        )
        comment_output_key = (comment_output_unit.module_parts, comment_output_decl.name)
        if comment_output_key not in agent_contract.outputs:
            raise CompileError(
                f"Review comment_output must be emitted by the concrete turn in {owner_label}: "
                f"{comment_output_decl.name}"
            )

        pre_sections = [
            item for item in resolved.items if isinstance(item, model.ReviewSection)
        ]
        outcome_sections = [
            item for item in resolved.items if isinstance(item, model.ReviewOutcomeSection)
        ]
        if outcome_sections:
            raise CompileError(
                f"Case-selected review must keep on_accept and on_reject inside cases: {review_decl.name}"
            )

        enum_decl = self._try_resolve_enum_decl(resolved.selector.enum_ref, unit=unit)
        if enum_decl is None:
            raise CompileError(
                f"Review selector must resolve to a closed enum in {owner_label}: "
                f"{_dotted_ref_name(resolved.selector.enum_ref)}"
            )

        seen_case_members: dict[str, str] = {}
        expected_case_members = {member.value for member in enum_decl.members}
        for case in resolved.cases:
            if len(case.subject.subjects) != 1:
                raise CompileError(
                    f"Review case must declare exactly one subject in {owner_label}: {case.key}"
                )
            for option in case.head.options:
                resolved_option = self._resolve_review_match_option(option, unit=unit)
                if resolved_option is None:
                    raise CompileError(
                        f"Review case selector must resolve to {enum_decl.name} in {owner_label}: {case.key}"
                    )
                option_enum_decl, member_value = resolved_option
                if option_enum_decl.name != enum_decl.name:
                    raise CompileError(
                        f"Review case selector must resolve to {enum_decl.name} in {owner_label}: {case.key}"
                    )
                previous_case = seen_case_members.get(member_value)
                if previous_case is not None:
                    raise CompileError(
                        f"Review cases overlap in {owner_label}: {previous_case}, {case.key}"
                    )
                seen_case_members[member_value] = case.key
        if set(seen_case_members) != expected_case_members:
            raise CompileError(f"Review cases must be exhaustive in {owner_label}")

        shared_titles = {
            section.key: self._review_section_title(section) for section in pre_sections
        }
        gate_observation = self._review_gate_observation(comment_output_decl)
        all_contract_gates: list[ReviewContractGate] = []
        seen_contract_gate_keys: set[str] = set()
        all_accept_branches: list[ResolvedReviewAgreementBranch] = []
        all_reject_branches: list[ResolvedReviewAgreementBranch] = []

        carried_fields = {
            field_name
            for case in resolved.cases
            for field_name in (
                *self._collect_review_carried_fields(case.on_accept.items),
                *self._collect_review_carried_fields(case.on_reject.items),
            )
        }
        field_bindings = self._validate_review_field_bindings(
            resolved.fields,
            output_decl=comment_output_decl,
            output_unit=comment_output_unit,
            owner_label=owner_label,
            require_blocked_gate=any(
                self._review_items_contain_blocks(section.items) for section in pre_sections
            )
            or any(self._review_items_contain_blocks(case.checks) for case in resolved.cases),
            require_active_mode=(
                resolved.selector.field_name == "active_mode" or "active_mode" in carried_fields
            ),
            require_trigger_reason="trigger_reason" in carried_fields,
        )

        body: list[CompiledBodyItem] = [
            f"Selected review mode: {enum_decl.title}.",
        ]

        for case in resolved.cases:
            contract_spec = self._resolve_review_contract_spec(
                case.contract.contract_ref,
                unit=unit,
                owner_label=f"{owner_label}.cases.{case.key}",
            )
            for gate in contract_spec.gates:
                if gate.key in seen_contract_gate_keys:
                    continue
                seen_contract_gate_keys.add(gate.key)
                all_contract_gates.append(gate)

        review_semantics = ReviewSemanticContext(
            review_module_parts=unit.module_parts,
            output_module_parts=comment_output_unit.module_parts,
            output_name=comment_output_decl.name,
            field_bindings=tuple(field_bindings.items()),
            contract_gates=tuple(all_contract_gates),
        )

        shared_contract_spec = ReviewContractSpec(
            kind="review",
            title="Selected Review Contract",
            gates=tuple(all_contract_gates),
        )

        for section in pre_sections:
            if body and body[-1] != "":
                body.append("")
            body.append(
                CompiledSection(
                    title=self._review_section_title(section),
                    body=self._compile_review_pre_outcome_section_body(
                        section.items,
                        unit=unit,
                        contract_spec=shared_contract_spec,
                        section_titles=shared_titles,
                        owner_label=f"{owner_label}.{section.key}",
                        review_semantics=review_semantics,
                    ),
                )
            )

        for case in resolved.cases:
            subjects = self._resolve_review_subjects(
                case.subject,
                unit=unit,
                owner_label=f"{owner_label}.cases.{case.key}",
            )
            subject_keys = {
                (subject_unit.module_parts, subject_decl.name)
                for subject_unit, subject_decl in subjects
            }
            contract_spec = self._resolve_review_contract_spec(
                case.contract.contract_ref,
                unit=unit,
                owner_label=f"{owner_label}.cases.{case.key}",
            )
            case_checks = model.ReviewSection(
                key=f"{case.key}_checks",
                title="Checks",
                items=case.checks,
            )
            case_pre_sections = [*pre_sections, case_checks]
            case_titles = {
                **shared_titles,
                case_checks.key: self._review_section_title(case_checks),
            }
            accept_gate_count = 0
            any_block_gates = False
            for section in case_pre_sections:
                accept_gate_count += self._count_review_accept_stmts(section.items)
                any_block_gates = any_block_gates or self._review_items_contain_blocks(section.items)
                self._validate_review_pre_outcome_items(
                    section.items,
                    unit=unit,
                    owner_label=f"{owner_label}.cases.{case.key}.{section.key}",
                    contract_spec=contract_spec,
                    section_titles=case_titles,
                    agent_contract=agent_contract,
                )
            if accept_gate_count != 1:
                raise CompileError(
                    f"Review case must define exactly one accept gate in {owner_label}: {case.key}"
                )

            pre_outcome_branches = self._resolve_review_pre_outcome_branches(
                case_pre_sections,
                unit=unit,
                contract_spec=contract_spec,
                section_titles=case_titles,
                owner_label=f"{owner_label}.cases.{case.key}",
                gate_observation=gate_observation,
            )
            accept_gate_branches = tuple(
                branch
                for branch in pre_outcome_branches
                if branch.verdict == _REVIEW_VERDICT_TEXT["accept"]
            )
            reject_gate_branches = tuple(
                branch
                for branch in pre_outcome_branches
                if branch.verdict == _REVIEW_VERDICT_TEXT["changes_requested"]
            )
            accept_branches = self._validate_review_outcome_section(
                case.on_accept,
                unit=unit,
                owner_label=f"{owner_label}.cases.{case.key}",
                agent_contract=agent_contract,
                comment_output_decl=comment_output_decl,
                comment_output_unit=comment_output_unit,
                next_owner_field_path=field_bindings["next_owner"],
                field_bindings=field_bindings,
                subject_keys=subject_keys,
                subject_map=None,
                blocked_gate_required=any_block_gates,
                gate_branches=accept_gate_branches,
            )
            reject_branches = self._validate_review_outcome_section(
                case.on_reject,
                unit=unit,
                owner_label=f"{owner_label}.cases.{case.key}",
                agent_contract=agent_contract,
                comment_output_decl=comment_output_decl,
                comment_output_unit=comment_output_unit,
                next_owner_field_path=field_bindings["next_owner"],
                field_bindings=field_bindings,
                subject_keys=subject_keys,
                subject_map=None,
                blocked_gate_required=any_block_gates,
                gate_branches=reject_gate_branches,
            )
            all_accept_branches.extend(accept_branches)
            all_reject_branches.extend(reject_branches)

            case_body: list[CompiledBodyItem] = [
                self._render_review_subject_summary(subjects),
                f"Shared review contract: {contract_spec.title}.",
            ]
            if case_body and case_body[-1] != "":
                case_body.append("")
            case_body.append(
                CompiledSection(
                    title=self._review_section_title(case_checks),
                    body=self._compile_review_pre_outcome_section_body(
                        case.checks,
                        unit=unit,
                        contract_spec=contract_spec,
                        section_titles=case_titles,
                        owner_label=f"{owner_label}.cases.{case.key}.checks",
                        review_semantics=review_semantics,
                    ),
                )
            )
            for key, section in (("on_accept", case.on_accept), ("on_reject", case.on_reject)):
                if case_body and case_body[-1] != "":
                    case_body.append("")
                case_body.append(
                    CompiledSection(
                        title=section.title or ("If Accepted" if key == "on_accept" else "If Rejected"),
                        body=self._compile_review_outcome_section_body(
                            section.items,
                            unit=unit,
                            owner_label=f"{owner_label}.cases.{case.key}.{key}",
                            review_semantics=review_semantics,
                        ),
                    )
                )
            if body and body[-1] != "":
                body.append("")
            body.append(CompiledSection(title=case.title, body=tuple(case_body)))

        self._validate_review_current_artifact_alignment(
            (*all_accept_branches, *all_reject_branches),
            output_decl=comment_output_decl,
            output_unit=comment_output_unit,
            owner_label=owner_label,
        )
        self._validate_review_optional_field_alignment(
            (*all_accept_branches, *all_reject_branches),
            output_decl=comment_output_decl,
            output_unit=comment_output_unit,
            field_bindings=field_bindings,
            owner_label=owner_label,
        )
        return CompiledSection(title=resolved.title, body=tuple(body))

    def _compile_review_pre_outcome_section_body(
        self,
        items: tuple[model.ReviewPreOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        contract_spec: ReviewContractSpec,
        section_titles: dict[str, str],
        owner_label: str,
        review_semantics: ReviewSemanticContext,
    ) -> tuple[CompiledBodyItem, ...]:
        lines: list[CompiledBodyItem] = []
        for item in items:
            rendered = self._render_review_pre_outcome_item(
                item,
                unit=unit,
                contract_spec=contract_spec,
                section_titles=section_titles,
                owner_label=owner_label,
                review_semantics=review_semantics,
            )
            if not rendered:
                continue
            if lines and lines[-1] != "":
                lines.append("")
            lines.extend(rendered)
        return tuple(lines)

    def _compile_review_outcome_section_body(
        self,
        items: tuple[model.ReviewOutcomeStmt, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        review_semantics: ReviewSemanticContext,
    ) -> tuple[CompiledBodyItem, ...]:
        lines: list[CompiledBodyItem] = []
        for item in items:
            rendered = self._render_review_outcome_item(
                item,
                unit=unit,
                owner_label=owner_label,
                review_semantics=review_semantics,
            )
            if not rendered:
                continue
            if lines and lines[-1] != "":
                lines.append("")
            lines.extend(rendered)
        return tuple(lines)

    def _compile_trust_surface_section(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> CompiledSection:
        lines: list[CompiledBodyItem] = []
        for item in decl.trust_surface:
            field_node = self._resolve_output_field_node(
                decl,
                path=item.path,
                unit=unit,
                owner_label=f"output {decl.name}",
                surface_label="trust_surface",
                review_semantics=review_semantics,
            )
            label = self._display_addressable_target_value(
                field_node,
                owner_label=f"output {decl.name}",
                surface_label="trust_surface",
                route_semantics=route_semantics,
                render_profile=render_profile,
            ).text
            if item.when_expr is not None:
                label = self._render_trust_surface_label(
                    label,
                    item.when_expr,
                    unit=unit,
                )
            lines.append(f"- {label}")
        return CompiledSection(title="Trust Surface", body=tuple(lines))

    def _compile_output_files(
        self,
        section: model.RecordSection,
        *,
        unit: IndexedUnit,
        output_name: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        for item in section.items:
            if not isinstance(item, model.RecordSection):
                raise CompileError(
                    f"`files` entries must be titled sections in output {output_name}"
                )
            scalar_items, _section_items, extras = self._split_record_items(
                item.items,
                scalar_keys={"path", "shape"},
                owner_label=f"output {output_name} file {item.key}",
            )
            path_item = scalar_items.get("path")
            shape_item = scalar_items.get("shape")
            if path_item is None or not isinstance(path_item.value, str):
                raise CompileError(
                    f"Output file entry is missing string path in {output_name}: {item.key}"
                )
            if shape_item is None:
                raise CompileError(
                    f"Output file entry is missing shape in {output_name}: {item.key}"
                )
            body.append(f"- {item.title}: `{path_item.value}`")
            body.append(
                f"- {item.title} Shape: {self._display_output_shape(shape_item.value, unit=unit, owner_label=f'output {output_name} file {item.key}', surface_label='output file fields')}"
            )
            if extras:
                body.append("")
                body.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_record_support_items(
                            extras,
                            unit=unit,
                            owner_label=f"output {output_name} file {item.key}",
                            surface_label="output file prose",
                            review_semantics=review_semantics,
                            route_semantics=route_semantics,
                            render_profile=render_profile,
                        ),
                    )
                )
        return tuple(body)

    def _compile_record_support_items(
        self,
        items: tuple[model.AnyRecordItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        for item in items:
            body.extend(
                self._compile_record_item(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
            )
        return tuple(body)

    def _compile_record_item(
        self,
        item: model.AnyRecordItem,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        if isinstance(item, (str, model.EmphasizedLine)):
            return (
                self._interpolate_authored_prose_line(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                ),
            )

        if isinstance(item, model.RecordSection):
            return (
                CompiledSection(
                    title=item.title,
                    body=self._compile_record_support_items(
                        item.items,
                        unit=unit,
                        owner_label=f"{owner_label}.{item.key}",
                        surface_label=surface_label,
                        review_semantics=review_semantics,
                        route_semantics=route_semantics,
                        render_profile=render_profile,
                    ),
                ),
            )

        if isinstance(item, model.ReadableBlock):
            return (
                self._compile_authored_readable_block(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                    section_body_compiler=lambda payload, nested_owner_label: self._compile_record_support_items(
                        payload,
                        unit=unit,
                        owner_label=nested_owner_label,
                        surface_label=surface_label,
                        review_semantics=review_semantics,
                        route_semantics=self._narrow_route_semantics(
                            route_semantics,
                            item.when_expr,
                            unit=unit,
                        ) if item.when_expr is not None else route_semantics,
                        render_profile=render_profile,
                    ),
                ),
            )

        if isinstance(item, model.GuardedOutputSection):
            guarded_route_semantics = self._narrow_route_semantics(
                route_semantics,
                item.when_expr,
                unit=unit,
            )
            condition = self._render_condition_expr(item.when_expr, unit=unit)
            body: list[CompiledBodyItem] = [f"Rendered only when {condition}."]
            compiled_items = self._compile_record_support_items(
                item.items,
                unit=unit,
                owner_label=f"{owner_label}.{item.key}",
                surface_label=surface_label,
                review_semantics=review_semantics,
                route_semantics=guarded_route_semantics,
                render_profile=render_profile,
            )
            if compiled_items:
                body.append("")
                body.extend(compiled_items)
            return (CompiledSection(title=item.title, body=tuple(body)),)

        if isinstance(item, model.RecordScalar):
            return self._compile_fallback_scalar(
                item,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )

        if isinstance(item, model.RecordRef):
            body = (
                self._compile_record_support_items(
                    item.body,
                    unit=unit,
                    owner_label=f"{owner_label}.{_dotted_ref_name(item.ref)}",
                    surface_label=surface_label,
                    review_semantics=review_semantics,
                    route_semantics=route_semantics,
                    render_profile=render_profile,
                )
                if item.body is not None
                else ()
            )
            return (
                CompiledSection(
                    title=self._display_ref(item.ref, unit=unit),
                    body=body,
                ),
            )

        raise CompileError(f"Unsupported record item: {type(item).__name__}")

    def _compile_fallback_scalar(
        self,
        item: model.RecordScalar,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        label = _humanize_key(item.key)
        value = self._format_scalar_value(
            item.value,
            unit=unit,
            owner_label=f"{owner_label}.{item.key}",
            surface_label=surface_label,
            review_semantics=review_semantics,
            route_semantics=route_semantics,
            render_profile=render_profile,
        )
        if item.body is None:
            return (f"- {label}: {value}",)

        body: list[CompiledBodyItem] = [value]
        body.extend(
            self._compile_record_support_items(
                item.body,
                unit=unit,
                owner_label=f"{owner_label}.{item.key}",
                surface_label=surface_label,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
                render_profile=render_profile,
            )
        )
        return (CompiledSection(title=label, body=tuple(body)),)

    def _compile_authored_readable_block(
        self,
        block: model.ReadableBlock,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        section_body_compiler,
        review_semantics: ReviewSemanticContext | None = None,
        route_semantics: RouteSemanticContext | None = None,
        render_profile: ResolvedRenderProfile | None = None,
    ) -> CompiledReadableBlock:
        if block.when_expr is not None:
            self._validate_readable_guard_expr(
                block.when_expr,
                unit=unit,
                owner_label=owner_label,
                allow_review_semantics=review_semantics is not None,
                allow_route_semantics=route_semantics is not None,
                review_semantics=review_semantics,
                route_semantics=route_semantics,
            )
        block_route_semantics = self._narrow_route_semantics(
            route_semantics,
            block.when_expr,
            unit=unit,
        )
        when_text = self._readable_guard_text(block.when_expr, unit=unit)
        title = None if block.kind == "properties" and block.anonymous else (
            block.title or _humanize_key(block.key)
        )
        block_owner_label = f"{owner_label}.{block.key}"
        if block.kind == "section":
            payload = self._require_tuple_payload(
                block.payload,
                owner_label=block_owner_label,
                kind="section",
            )
            return CompiledSection(
                title=title or _humanize_key(block.key),
                body=section_body_compiler(payload, block_owner_label),
                requirement=block.requirement,
                when_text=when_text,
                emit_metadata=True,
                semantic_target=_semantic_render_target_for_block(block.kind, block.key),
            )
        if block.kind in {"sequence", "bullets", "checklist"}:
            items: list[model.ProseLine] = []
            seen_keys: set[str] = set()
            for list_item in self._require_tuple_payload(
                block.payload,
                owner_label=block_owner_label,
                kind=block.kind,
            ):
                if not isinstance(list_item, model.ReadableListItem):
                    raise CompileError(
                        f"Readable {block.kind} items must stay list entries in {block_owner_label}"
                    )
                if list_item.key is not None:
                    if list_item.key in seen_keys:
                        raise CompileError(
                            f"Duplicate {block.kind} item key in {block_owner_label}: {list_item.key}"
                        )
                    seen_keys.add(list_item.key)
                items.append(
                    self._interpolate_authored_prose_line(
                        list_item.text,
                        unit=unit,
                        owner_label=block_owner_label,
                        surface_label=f"{block.kind} item prose",
                        ambiguous_label=f"{block.kind} item interpolation ref",
                        review_semantics=review_semantics,
                        route_semantics=block_route_semantics,
                        render_profile=render_profile,
                    )
                )
            item_schema = self._resolve_readable_inline_schema(
                block.item_schema,
                unit=unit,
                owner_label=block_owner_label,
                schema_label="item_schema",
                surface_label=f"{block.kind} item schema",
                review_semantics=review_semantics,
                route_semantics=block_route_semantics,
                render_profile=render_profile,
            )
            compiled_cls = {
                "sequence": CompiledSequenceBlock,
                "bullets": CompiledBulletsBlock,
                "checklist": CompiledChecklistBlock,
            }[block.kind]
            return compiled_cls(
                title=title,
                items=tuple(items),
                requirement=block.requirement,
                when_text=when_text,
                item_schema=item_schema,
                semantic_target=_semantic_render_target_for_block(block.kind, block.key),
            )
        if block.kind == "properties":
            properties = self._resolve_readable_properties_payload(
                block.payload,
                unit=unit,
                owner_label=block_owner_label,
                review_semantics=review_semantics,
                route_semantics=block_route_semantics,
                render_profile=render_profile,
            )
            return CompiledPropertiesBlock(
                title=title,
                entries=properties.entries,
                requirement=block.requirement,
                when_text=when_text,
                anonymous=block.anonymous,
            )
        if block.kind == "definitions":
            definitions: list[model.ReadableDefinitionItem] = []
            seen_keys: set[str] = set()
            for definition in self._require_tuple_payload(
                block.payload,
                owner_label=block_owner_label,
                kind="definitions",
            ):
                if not isinstance(definition, model.ReadableDefinitionItem):
                    raise CompileError(
                        f"Readable definitions entries must stay definition items in {block_owner_label}"
                    )
                if definition.key in seen_keys:
                    raise CompileError(
                        f"Duplicate definitions item key in {block_owner_label}: {definition.key}"
                    )
                seen_keys.add(definition.key)
                definitions.append(
                    replace(
                        definition,
                        body=tuple(
                            self._interpolate_authored_prose_line(
                                line,
                                unit=unit,
                                owner_label=f"{block_owner_label}.{definition.key}",
                                surface_label="definitions prose",
                                ambiguous_label="definitions prose interpolation ref",
                                review_semantics=review_semantics,
                                route_semantics=block_route_semantics,
                                render_profile=render_profile,
                            )
                            for line in definition.body
                        ),
                    )
                )
            return CompiledDefinitionsBlock(
                title=title,
                items=tuple(definitions),
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "table":
            if not isinstance(block.payload, model.ReadableTableData):
                raise CompileError(
                    f"Readable table payload must stay table-shaped in {block_owner_label}"
                )
            resolved_columns: list[CompiledTableColumn] = []
            column_keys: set[str] = set()
            for column in block.payload.columns:
                if column.key in column_keys:
                    raise CompileError(
                        f"Duplicate table column key in {block_owner_label}: {column.key}"
                    )
                column_keys.add(column.key)
                resolved_columns.append(
                    CompiledTableColumn(
                        key=column.key,
                        title=column.title,
                        body=tuple(
                            self._interpolate_authored_prose_line(
                                line,
                                unit=unit,
                                owner_label=f"{block_owner_label}.columns.{column.key}",
                                surface_label="table column prose",
                                ambiguous_label="table column interpolation ref",
                                review_semantics=review_semantics,
                                route_semantics=block_route_semantics,
                                render_profile=render_profile,
                            )
                            for line in column.body
                        ),
                    )
                )
            if not resolved_columns:
                raise CompileError(
                    f"Readable table must declare at least one column in {block_owner_label}"
                )
            resolved_rows: list[CompiledTableRow] = []
            row_keys: set[str] = set()
            for row in block.payload.rows:
                if row.key in row_keys:
                    raise CompileError(
                        f"Duplicate table row key in {block_owner_label}: {row.key}"
                    )
                row_keys.add(row.key)
                cell_keys: set[str] = set()
                resolved_cells: list[CompiledTableCell] = []
                for cell in row.cells:
                    if cell.key not in column_keys:
                        raise CompileError(
                            f"Table row references an unknown column in {block_owner_label}: {cell.key}"
                        )
                    if cell.key in cell_keys:
                        raise CompileError(
                            f"Duplicate table row cell in {block_owner_label}.{row.key}: {cell.key}"
                        )
                    cell_keys.add(cell.key)
                    if cell.body is not None:
                        resolved_cells.append(
                            CompiledTableCell(
                                key=cell.key,
                                body=section_body_compiler(
                                    cell.body,
                                    f"{block_owner_label}.{row.key}.{cell.key}",
                                ),
                            )
                        )
                        continue
                    cell_text = self._interpolate_authored_prose_string(
                        cell.text or "",
                        unit=unit,
                        owner_label=f"{block_owner_label}.{row.key}.{cell.key}",
                        surface_label="table cell prose",
                        ambiguous_label="table cell interpolation ref",
                        review_semantics=review_semantics,
                        route_semantics=block_route_semantics,
                        render_profile=render_profile,
                    )
                    if "\n" in cell_text:
                        raise CompileError(
                            "Readable table inline cells must stay single-line in "
                            f"{block_owner_label}.{row.key}.{cell.key}; nested tables require structured cell bodies."
                        )
                    resolved_cells.append(CompiledTableCell(key=cell.key, text=cell_text))
                resolved_rows.append(CompiledTableRow(key=row.key, cells=tuple(resolved_cells)))
            resolved_notes = tuple(
                self._interpolate_authored_prose_line(
                    line,
                    unit=unit,
                    owner_label=block_owner_label,
                    surface_label="table notes",
                    ambiguous_label="table note interpolation ref",
                    review_semantics=review_semantics,
                    route_semantics=block_route_semantics,
                    render_profile=render_profile,
                )
                for line in block.payload.notes
            )
            row_schema = self._resolve_readable_inline_schema(
                block.row_schema or block.payload.row_schema,
                unit=unit,
                owner_label=block_owner_label,
                schema_label="row_schema",
                surface_label="table row schema",
                review_semantics=review_semantics,
                route_semantics=block_route_semantics,
                render_profile=render_profile,
            )
            return CompiledTableBlock(
                title=title or _humanize_key(block.key),
                table=CompiledTableData(
                    columns=tuple(resolved_columns),
                    rows=tuple(resolved_rows),
                    notes=resolved_notes,
                    row_schema=row_schema,
                ),
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "guard":
            payload = self._require_tuple_payload(
                block.payload,
                owner_label=block_owner_label,
                kind="guard",
            )
            if when_text is None:
                raise CompileError(
                    f"Readable guard shells must define a guard expression in {block_owner_label}"
                )
            return CompiledGuardBlock(
                title=title or _humanize_key(block.key),
                body=section_body_compiler(payload, block_owner_label),
                when_text=when_text,
            )
        if block.kind == "callout":
            if not isinstance(block.payload, model.ReadableCalloutData):
                raise CompileError(
                    f"Readable callout payload must stay callout-shaped in {block_owner_label}"
                )
            if block.payload.kind is not None and block.payload.kind not in {
                "required",
                "important",
                "warning",
                "note",
            }:
                raise CompileError(
                    f"Unknown callout kind in {block_owner_label}: {block.payload.kind}"
                )
            return CompiledCalloutBlock(
                title=title or _humanize_key(block.key),
                kind=block.payload.kind,
                body=tuple(
                    self._interpolate_authored_prose_line(
                        line,
                        unit=unit,
                        owner_label=block_owner_label,
                        surface_label="callout prose",
                        ambiguous_label="callout interpolation ref",
                        review_semantics=review_semantics,
                        route_semantics=block_route_semantics,
                        render_profile=render_profile,
                    )
                    for line in block.payload.body
                ),
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "code":
            if not isinstance(block.payload, model.ReadableCodeData):
                raise CompileError(
                    f"Readable code payload must stay code-shaped in {block_owner_label}"
                )
            if "\n" not in block.payload.text:
                raise CompileError(
                    f"Code block text must use a multiline string in {block_owner_label}"
                )
            return CompiledCodeBlock(
                title=title or _humanize_key(block.key),
                text=block.payload.text,
                language=block.payload.language,
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind in {"markdown", "html"}:
            if not isinstance(block.payload, model.ReadableRawTextData):
                raise CompileError(
                    f"Readable {block.kind} payload must stay text-shaped in {block_owner_label}"
                )
            text = self._interpolate_authored_prose_string(
                block.payload.text,
                unit=unit,
                owner_label=block_owner_label,
                surface_label=f"{block.kind} text",
                ambiguous_label=f"{block.kind} interpolation ref",
                review_semantics=review_semantics,
                route_semantics=block_route_semantics,
                render_profile=render_profile,
            )
            if "\n" not in text:
                raise CompileError(
                    f"Raw {block.kind} blocks must use a multiline string in {block_owner_label}"
                )
            return CompiledRawTextBlock(
                title=title or _humanize_key(block.key),
                text=text,
                kind=block.kind,
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "footnotes":
            footnotes = self._resolve_readable_footnotes_payload(
                block.payload,
                unit=unit,
                owner_label=block_owner_label,
                review_semantics=review_semantics,
                route_semantics=block_route_semantics,
                render_profile=render_profile,
            )
            return CompiledFootnotesBlock(
                title=title or _humanize_key(block.key),
                entries=footnotes.entries,
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "image":
            if not isinstance(block.payload, model.ReadableImageData):
                raise CompileError(f"Readable image payload must stay image-shaped in {block_owner_label}")
            return CompiledImageBlock(
                title=title or _humanize_key(block.key),
                src=self._interpolate_authored_prose_string(
                    block.payload.src,
                    unit=unit,
                    owner_label=block_owner_label,
                    surface_label="image src",
                    ambiguous_label="image src interpolation ref",
                    review_semantics=review_semantics,
                    route_semantics=block_route_semantics,
                    render_profile=render_profile,
                ),
                alt=self._interpolate_authored_prose_string(
                    block.payload.alt,
                    unit=unit,
                    owner_label=block_owner_label,
                    surface_label="image alt",
                    ambiguous_label="image alt interpolation ref",
                    review_semantics=review_semantics,
                    route_semantics=block_route_semantics,
                    render_profile=render_profile,
                ),
                caption=(
                    self._interpolate_authored_prose_string(
                        block.payload.caption,
                        unit=unit,
                        owner_label=block_owner_label,
                        surface_label="image caption",
                        ambiguous_label="image caption interpolation ref",
                        review_semantics=review_semantics,
                        route_semantics=block_route_semantics,
                        render_profile=render_profile,
                    )
                    if block.payload.caption is not None
                    else None
                ),
                requirement=block.requirement,
                when_text=when_text,
            )
        if block.kind == "rule":
            return CompiledRuleBlock(
                requirement=block.requirement,
                when_text=when_text,
            )
        raise CompileError(f"Unsupported readable block kind in {block_owner_label}: {block.kind}")

    def _compile_config_lines(
        self,
        config_items: tuple[model.RecordItem, ...],
        *,
        spec: ConfigSpec,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        seen_keys: set[str] = set()
        allowed_keys = {**spec.required_keys, **spec.optional_keys}

        for item in config_items:
            if not isinstance(item, model.RecordScalar) or item.body is not None:
                raise CompileError(f"Config entries must be scalar key/value lines in {owner_label}")
            if item.key in seen_keys:
                raise CompileError(f"Duplicate config key in {owner_label}: {item.key}")
            seen_keys.add(item.key)
            if item.key not in allowed_keys:
                raise CompileError(f"Unknown config key in {owner_label}: {item.key}")
            body.append(
                f"- {allowed_keys[item.key]}: {self._format_scalar_value(item.value, unit=unit, owner_label=f'{owner_label}.{item.key}', surface_label='config values')}"
            )

        missing_required = [
            key for key in spec.required_keys if key not in seen_keys
        ]
        if missing_required:
            missing = ", ".join(missing_required)
            raise CompileError(f"Missing required config key in {owner_label}: {missing}")

        return tuple(body)

    def _compile_workflow_decl(
        self,
        workflow_decl: model.WorkflowDecl,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract | None = None,
    ) -> CompiledSection:
        workflow_key = (unit.module_parts, workflow_decl.name)
        if workflow_key in self._workflow_compile_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._workflow_compile_stack, workflow_key]
            )
            raise CompileError(f"Cyclic workflow composition: {cycle}")

        self._workflow_compile_stack.append(workflow_key)
        try:
            return self._compile_resolved_workflow(
                self._resolve_workflow_decl(workflow_decl, unit=unit),
                unit=unit,
                agent_contract=agent_contract,
                owner_label=f"workflow {_dotted_decl_name(unit.module_parts, workflow_decl.name)}",
            )
        finally:
            self._workflow_compile_stack.pop()

    def _compile_resolved_workflow(
        self,
        workflow_body: ResolvedWorkflowBody,
        *,
        unit: IndexedUnit | None = None,
        agent_contract: AgentContract | None = None,
        owner_label: str | None = None,
    ) -> CompiledSection:
        body: list[CompiledBodyItem] = list(workflow_body.preamble)
        if workflow_body.law is not None:
            if unit is None or agent_contract is None or owner_label is None:
                raise CompileError(
                    "Internal compiler error: workflow law requires unit, agent contract, and owner label"
                )
            if body and body[-1] != "":
                body.append("")
            body.extend(
                self._compile_workflow_law(
                    workflow_body.law,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                )
            )
        for item in workflow_body.items:
            if body and body[-1] != "":
                body.append("")
            if isinstance(item, ResolvedSectionItem):
                body.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_section_body(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{item.key}",
                        ),
                    )
                )
                continue

            if isinstance(item, ResolvedWorkflowSkillsItem):
                body.append(self._compile_resolved_skills(item.body))
                continue

            body.append(
                self._compile_workflow_decl(
                    item.workflow_decl,
                    unit=item.target_unit,
                    agent_contract=agent_contract,
                )
            )

        return CompiledSection(title=workflow_body.title, body=tuple(body))

    def _compile_workflow_law(
        self,
        law_body: model.LawBody,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> tuple[CompiledBodyItem, ...]:
        flat_items = self._flatten_law_items(law_body, owner_label=owner_label)
        self._validate_workflow_law(
            flat_items,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
        )

        lines: list[str] = []
        mode_bindings: dict[str, model.ModeStmt] = {}
        for item in flat_items:
            rendered: list[str] = []
            if isinstance(item, model.ActiveWhenStmt):
                rendered.append(
                    f"This pass runs only when {self._render_condition_expr(item.expr, unit=unit)}."
                )
            elif isinstance(item, model.ModeStmt):
                mode_bindings[item.name] = item
                fixed_mode = self._resolve_constant_enum_member(item.expr, unit=unit)
                if fixed_mode is not None:
                    rendered.append(f"Active mode: {fixed_mode}.")
            elif isinstance(item, model.MatchStmt):
                rendered.extend(
                    self._render_match_stmt(
                        item,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        mode_bindings=mode_bindings,
                    )
                )
            elif isinstance(item, model.WhenStmt):
                rendered.extend(
                    self._render_when_stmt(
                        item,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        mode_bindings=mode_bindings,
                    )
                )
            else:
                rendered.extend(
                    self._render_law_stmt_lines(
                        item,
                        unit=unit,
                        agent_contract=agent_contract,
                        owner_label=owner_label,
                        bullet=False,
                    )
                )

            if not rendered:
                continue
            if lines:
                lines.append("")
            lines.extend(rendered)

        return tuple(lines)

    def _compile_section_body(
        self,
        items: tuple[ResolvedSectionBodyItem, ...],
        *,
        unit: IndexedUnit | None = None,
        owner_label: str | None = None,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        previous_kind: str | None = None

        for item in items:
            current_kind = "ref" if isinstance(item, ResolvedSectionRef) else "prose"
            if previous_kind is not None and current_kind != previous_kind and body:
                if body[-1] != "":
                    body.append("")

            if isinstance(item, (str, model.EmphasizedLine)):
                body.append(item)
            elif isinstance(item, ResolvedSectionItem):
                body.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_section_body(
                            item.items,
                            unit=unit,
                            owner_label=(
                                f"{owner_label}.{item.key}" if owner_label is not None else None
                            ),
                        ),
                    )
                )
            elif isinstance(item, model.ReadableBlock):
                if unit is None or owner_label is None:
                    raise CompileError(
                        "Internal compiler error: workflow readable block compilation requires unit and owner label"
                    )
                body.append(
                    self._compile_authored_readable_block(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="workflow section bodies",
                        section_body_compiler=lambda payload, nested_owner_label: self._compile_section_body(
                            self._resolve_section_body_items(
                                payload,
                                unit=unit,
                                owner_label=nested_owner_label,
                            ),
                            unit=unit,
                            owner_label=nested_owner_label,
                        ),
                    )
                )
            elif isinstance(item, ResolvedRouteLine):
                body.append(f"{item.label} -> {item.target_display_name}")
            else:
                body.append(f"- {item.label}")

            previous_kind = current_kind

        return tuple(body)
