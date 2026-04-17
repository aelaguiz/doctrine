from __future__ import annotations

from dataclasses import replace
import tempfile
import textwrap
import unittest
from pathlib import Path

from doctrine import model
from doctrine._compiler.context import CompilationContext
from doctrine._compiler.resolved_types import AddressableNode
from doctrine.compiler import CompilationSession
from doctrine.diagnostics import CompileError
from doctrine.parser import parse_file


class CompileDiagnosticTests(unittest.TestCase):
    def _write_prompt(
        self,
        root: Path,
        source: str,
        *,
        rel_path: str = "prompts/AGENTS.prompt",
    ) -> Path:
        prompt_path = root / rel_path
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(textwrap.dedent(source), encoding="utf-8")
        return prompt_path

    def _compile_repo_prompt_error(
        self,
        rel_path: str,
        *,
        agent: str,
    ) -> tuple[Path, CompileError]:
        prompt_path = (Path(__file__).resolve().parents[1] / rel_path).resolve()
        with self.assertRaises(CompileError) as ctx:
            CompilationSession(parse_file(prompt_path)).compile_agent(agent)
        return prompt_path, ctx.exception

    def test_missing_import_points_at_import_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                import shared.missing

                agent Demo:
                    role: "Own the reply."
                    workflow: "Reply"
                        "Answer directly."
                """,
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path))

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E280")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 1)
        self.assertEqual(error.diagnostic.location.column, 1)
        self.assertIn("import shared.missing", str(error))
        self.assertIn("Create the missing prompt file, or fix the import path.", str(error))

    def test_duplicate_module_alias_reports_related_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_prompt(
                root,
                """\
                workflow Greeting: "Greeting"
                    "Say hello."
                """,
                rel_path="prompts/simple/greeting.prompt",
            )
            self._write_prompt(
                root,
                """\
                workflow Object: "Object"
                    "Say world."
                """,
                rel_path="prompts/simple/object.prompt",
            )
            prompt_path = self._write_prompt(
                root,
                """\
                import simple.greeting as shared
                import simple.object as shared

                agent Demo:
                    role: "Own the reply."
                """,
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path))

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E306")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 2)
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(error.diagnostic.related[0].location.line, 1)
        self.assertIn("Duplicate module alias", str(error))
        self.assertIn("Visible import module `shared`", str(error))

    def test_duplicate_imported_symbol_reports_related_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_prompt(
                root,
                """\
                workflow Greeting: "Greeting"
                    "Say hello."
                """,
                rel_path="prompts/simple/greeting.prompt",
            )
            self._write_prompt(
                root,
                """\
                workflow PoliteGreeting: "Polite Greeting"
                    "Say hello politely."
                """,
                rel_path="prompts/simple/nested/polite.prompt",
            )
            prompt_path = self._write_prompt(
                root,
                """\
                from simple.greeting import Greeting
                from simple.nested.polite import PoliteGreeting as Greeting

                agent Demo:
                    role: "Own the reply."
                """,
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path))

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E307")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 2)
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(error.diagnostic.related[0].location.line, 1)
        self.assertIn("Duplicate imported symbol", str(error))
        self.assertIn("Imported symbol `Greeting`", str(error))

    def test_imported_symbol_ownership_conflict_reports_related_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_prompt(
                root,
                """\
                workflow Greeting: "Greeting"
                    "Say hello."
                """,
                rel_path="prompts/shared/greeting.prompt",
            )
            prompt_path = self._write_prompt(
                root,
                """\
                from shared.greeting import Greeting

                workflow Greeting: "Local Greeting"
                    "Keep the local workflow."

                agent Demo:
                    role: "Own the reply."
                    workflow: "Imported Steps"
                        use greeting: Greeting
                """,
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E308")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 9)
        self.assertEqual(len(error.diagnostic.related), 2)
        self.assertEqual(error.diagnostic.related[0].location.line, 3)
        self.assertEqual(error.diagnostic.related[1].location.line, 1)
        self.assertIn("Ambiguous imported symbol ownership", str(error))
        self.assertIn("visible both as a local workflow declaration", str(error))

    def test_duplicate_declaration_name_reports_related_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                table ReleaseGates: "Release Gates"
                    columns:
                        gate: "Gate"

                table ReleaseGates: "Release Gates Again"
                    columns:
                        proof: "Proof"
                """,
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path))

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E288")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 5)
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(error.diagnostic.related[0].location.line, 1)
        self.assertIn("Related:", str(error))
        self.assertIn("first declaration", str(error))

    def test_duplicate_agent_typed_field_reports_related_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                decision PlayableStrategyChoice: "Playable Strategy Choice"
                    candidates minimum 3
                    rank required
                    rejects required
                    winner required
                    rank_by {teaching_fit, product_reality, capstone_coherence, downstream_preservability}

                agent Demo:
                    role: "Own the reply."
                    workflow: "Reply"
                        "Answer directly."
                    decision: PlayableStrategyChoice
                    decision: PlayableStrategyChoice
                """,
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E204")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 13)
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(error.diagnostic.related[0].location.line, 12)
        self.assertIn(
            "Agent `Demo` defines typed field `decision:PlayableStrategyChoice` more than once.",
            str(error),
        )
        self.assertIn("first `decision:PlayableStrategyChoice` field", str(error))

    def test_invalid_project_toml_points_at_the_toml_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pyproject_path = root / "pyproject.toml"
            pyproject_path.write_text(
                textwrap.dedent(
                    """\
                    [tool.doctrine.compile]
                    additional_prompt_roots = ["shared/prompts"
                    """
                ),
                encoding="utf-8",
            )
            prompt_path = self._write_prompt(
                root,
                """\
                agent Demo:
                    role: "Own the reply."
                    workflow: "Reply"
                        "Answer directly."
                """,
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path))

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, pyproject_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 3)
        self.assertIsNotNone(error.diagnostic.location.column)
        self.assertIn('additional_prompt_roots = ["shared/prompts"', str(error))

    def test_invalid_project_config_points_at_the_config_item(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pyproject_path = root / "pyproject.toml"
            pyproject_path.write_text(
                textwrap.dedent(
                    """\
                    [tool.doctrine.compile]
                    additional_prompt_roots = ["shared/not_prompts"]
                    """
                ),
                encoding="utf-8",
            )
            prompt_path = self._write_prompt(
                root,
                """\
                agent Demo:
                    role: "Own the reply."
                    workflow: "Reply"
                        "Answer directly."
                """,
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path))

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E285")
        self.assertEqual(error.diagnostic.location.path, pyproject_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 2)
        self.assertIsNotNone(error.diagnostic.location.column)
        self.assertIn('additional_prompt_roots = ["shared/not_prompts"]', str(error))

    def test_duplicate_route_from_arm_reports_related_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                enum ProofRoute: "Proof Route"
                    accept: "Accept"
                    change: "Change"
                input RouteFacts: "Route Facts"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required
                    route_choice: "Route Choice"
                agent AcceptanceCritic:
                    role: "Accept routed work."
                agent BackupCritic:
                    role: "Backup routed work."
                agent ChangeEngineer:
                    role: "Handle requested changes."
                workflow DuplicateRouteFromWorkflow: "Duplicate Route From Workflow"
                    law:
                        current none
                        route_from RouteFacts.route_choice as ProofRoute:
                            ProofRoute.accept:
                                route "Send to AcceptanceCritic." -> AcceptanceCritic
                            ProofRoute.accept:
                                route "Send to BackupCritic." -> BackupCritic
                            ProofRoute.change:
                                route "Send to ChangeEngineer." -> ChangeEngineer
                agent Demo:
                    role: "Reject duplicate route_from choices."
                    inputs: "Inputs"
                        RouteFacts
                    workflow: DuplicateRouteFromWorkflow
                """,
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E348")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 21)
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(error.diagnostic.related[0].location.line, 19)
        self.assertIn("first `Accept` arm", str(error))
        self.assertIn("Related:", str(error))

    def test_route_from_selector_invalid_source_points_at_selector_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                enum ProofRoute: "Proof Route"
                    accept: "Accept"
                    change: "Change"
                input RouteFacts: "Route Facts"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required
                    route_choice: "Route Choice"
                agent AcceptanceCritic:
                    role: "Accept routed work."
                agent ChangeEngineer:
                    role: "Handle requested changes."
                workflow InvalidComputedRouteFromWorkflow: "Invalid Computed Route From Workflow"
                    law:
                        current none
                        route_from RouteFacts.route_choice == ProofRoute.accept as ProofRoute:
                            ProofRoute.accept:
                                route "Send to AcceptanceCritic." -> AcceptanceCritic
                            ProofRoute.change:
                                route "Send to ChangeEngineer." -> ChangeEngineer
                agent Demo:
                    role: "Keep route_from selectors direct."
                    inputs: "Inputs"
                        RouteFacts
                    workflow: InvalidComputedRouteFromWorkflow
                """,
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E346")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 16)
        self.assertIn("route_from RouteFacts.route_choice == ProofRoute.accept as ProofRoute:", str(error))

    def test_route_from_arm_outside_enum_points_at_arm_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                enum ProofRoute: "Proof Route"
                    accept: "Accept"
                    change: "Change"
                input RouteFacts: "Route Facts"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required
                    route_choice: "Route Choice"
                agent AcceptanceCritic:
                    role: "Accept routed work."
                agent ChangeEngineer:
                    role: "Handle requested changes."
                workflow InvalidRouteFromWorkflow: "Invalid Route From Workflow"
                    law:
                        current none
                        route_from RouteFacts.route_choice as ProofRoute:
                            ProofRoute.accept:
                                route "Send to AcceptanceCritic." -> AcceptanceCritic
                            ReviewVerdict.accepted:
                                route "Send to ChangeEngineer." -> ChangeEngineer
                agent Demo:
                    role: "Reject route_from arms outside the selected enum."
                    inputs: "Inputs"
                        RouteFacts
                    workflow: InvalidRouteFromWorkflow
                """,
            )
            rendered = prompt_path.read_text(encoding="utf-8")
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("            ReviewVerdict.accepted:") + 1,
        )
        self.assertIn("route_from arm must name a member of ProofRoute", str(error))

    def test_route_from_unreachable_else_points_at_else_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                enum ProofRoute: "Proof Route"
                    accept: "Accept"
                    change: "Change"
                input RouteFacts: "Route Facts"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required
                    route_choice: "Route Choice"
                agent AcceptanceCritic:
                    role: "Accept routed work."
                agent ChangeEngineer:
                    role: "Handle requested changes."
                agent BackupCritic:
                    role: "Handle fallback routed work."
                workflow InvalidRouteFromWorkflow: "Invalid Route From Workflow"
                    law:
                        current none
                        route_from RouteFacts.route_choice as ProofRoute:
                            ProofRoute.accept:
                                route "Send to AcceptanceCritic." -> AcceptanceCritic
                            ProofRoute.change:
                                route "Send to ChangeEngineer." -> ChangeEngineer
                            else:
                                route "Send to BackupCritic." -> BackupCritic
                agent Demo:
                    role: "Reject unreachable route_from else arms."
                    inputs: "Inputs"
                        RouteFacts
                    workflow: InvalidRouteFromWorkflow
                """,
            )
            rendered = prompt_path.read_text(encoding="utf-8")
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 23)
        self.assertIn("route_from else is unreachable", str(error))

    def test_route_from_non_exhaustive_points_at_route_from_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                enum ProofRoute: "Proof Route"
                    accept: "Accept"
                    change: "Change"
                input RouteFacts: "Route Facts"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required
                    route_choice: "Route Choice"
                agent AcceptanceCritic:
                    role: "Accept routed work."
                workflow InvalidRouteFromWorkflow: "Invalid Route From Workflow"
                    law:
                        current none
                        route_from RouteFacts.route_choice as ProofRoute:
                            ProofRoute.accept:
                                route "Send to AcceptanceCritic." -> AcceptanceCritic
                agent Demo:
                    role: "Reject non-exhaustive route_from blocks without else."
                    inputs: "Inputs"
                        RouteFacts
                    workflow: InvalidRouteFromWorkflow
                """,
            )
            rendered = prompt_path.read_text(encoding="utf-8")
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        route_from RouteFacts.route_choice as ProofRoute:") + 1,
        )
        self.assertIn("route_from on ProofRoute must be exhaustive or include else", str(error))

    def test_route_target_abstract_agent_points_at_route_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                abstract agent ReviewLead:
                    role: "Accept routed work."

                agent Demo:
                    role: "Reject abstract route targets."
                    workflow: "Route"
                        law:
                            current none
                            route "Hand off to ReviewLead." -> ReviewLead
                """,
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E282")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 9)
        self.assertIn('route "Hand off to ReviewLead." -> ReviewLead', str(error))

    def test_active_when_invalid_source_points_at_active_when_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                workflow InvalidActiveWhenWorkflow: "Invalid Active When Workflow"
                    law:
                        current none
                        active when MissingInput.ready

                agent Demo:
                    role: "Reject invalid active when reads."
                    workflow: InvalidActiveWhenWorkflow
                """,
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 4)
        self.assertIn("active when reads invalid input source", str(error))

    def test_mode_value_outside_enum_points_at_mode_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                enum EditMode: "Edit Mode"
                    manifest_title: "manifest-title"
                    section_summary: "section-summary"

                workflow InvalidModeAwareEdit: "Mode-Aware Edit"
                    law:
                        mode edit_mode = "taxonomy" as EditMode
                        current none

                agent Demo:
                    role: "Reject invalid mode values."
                    workflow: InvalidModeAwareEdit
                """,
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E341")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 7)
        self.assertIn('mode edit_mode = "taxonomy" as EditMode', str(error))

    def test_nonexhaustive_mode_match_points_at_match_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                enum EditMode: "Edit Mode"
                    manifest_title: "manifest-title"
                    section_summary: "section-summary"

                input CurrentHandoff: "Current Handoff"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                workflow InvalidModeAwareEdit: "Mode-Aware Edit"
                    law:
                        mode edit_mode = CurrentHandoff.active_mode as EditMode
                        match edit_mode:
                            EditMode.manifest_title:
                                current none

                agent Demo:
                    role: "Reject nonexhaustive mode matches."
                    workflow: InvalidModeAwareEdit
                    inputs: "Inputs"
                        CurrentHandoff
                """,
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E342")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 13)
        self.assertIn("match edit_mode:", str(error))

    def test_match_arm_outside_enum_points_at_arm_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                enum EditMode: "Edit Mode"
                    manifest_title: "manifest-title"
                    section_summary: "section-summary"

                enum ReviewVerdict: "Review Verdict"
                    accepted: "accepted"
                    changes_requested: "changes requested"

                input CurrentHandoff: "Current Handoff"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                workflow InvalidModeAwareEdit: "Mode-Aware Edit"
                    law:
                        mode edit_mode = CurrentHandoff.active_mode as EditMode
                        match edit_mode:
                            ReviewVerdict.accepted:
                                current none

                agent Demo:
                    role: "Reject match arms outside the declared enum."
                    workflow: InvalidModeAwareEdit
                    inputs: "Inputs"
                        CurrentHandoff
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("            ReviewVerdict.accepted:") + 1,
        )
        self.assertIn("Match arm is outside enum EditMode", str(error))

    def test_handoff_routing_nonrouting_statement_points_at_statement_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                output SimpleReply: "Simple Reply"
                    target: TurnResponse
                    shape: CommentText
                    requirement: Required

                agent Demo:
                    role: "Keep handoff routing limited to route semantics."
                    outputs: "Outputs"
                        SimpleReply

                    handoff_routing: "Handoff Routing"
                        law:
                            current none
                            stop "Reply and stop."
                """,
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E344")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 13)
        self.assertIn("unsupported statement `current none`", str(error))

    def test_mixed_named_and_bare_law_items_report_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                workflow MixedLawWorkflow: "Mixed Law Workflow"
                    law:
                        currentness:
                            current none
                        stop "Reply and stop."

                agent Demo:
                    role: "Reject mixed law block shapes."
                    workflow: MixedLawWorkflow
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        stop "Reply and stop."') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("        currentness:") + 1,
        )
        self.assertIn("first named law section", str(error))

    def test_missing_current_subject_points_at_branch_anchor_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input CurrentHandoff: "Current Handoff"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                agent RoutingOwner:
                    role: "Handle reroutes when specialist work cannot continue."
                    workflow: "Instructions"
                        "Take back the same issue when route-only work cannot continue safely."

                workflow InvalidRouteOnlyTurns: "Route-Only Triage"
                    law:
                        active when CurrentHandoff.missing
                        when CurrentHandoff.missing:
                            stop "Current handoff is missing."
                            route "Route the same issue back to RoutingOwner." -> RoutingOwner

                agent Demo:
                    role: "Trigger an active branch with no current subject."
                    workflow: InvalidRouteOnlyTurns
                    inputs: "Inputs"
                        CurrentHandoff
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E331")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index(
                '            route "Route the same issue back to RoutingOwner." -> RoutingOwner'
            )
            + 1,
        )
        self.assertIn("Add either `current artifact ... via ...` or `current none`", str(error))

    def test_route_only_next_owner_binding_reports_related_route_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input RouteFacts: "Route Facts"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                output RerouteHandoffComment: "Reroute Handoff Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    next_owner: "Next Owner"
                        "Say plainly that RoutingOwner now owns the rerouted turn."

                agent RoutingOwner:
                    role: "Own route-only follow-up when specialist output is missing."
                    workflow: "Route Repairs"
                        "Take back the same issue when route-only work cannot continue safely."

                workflow RouteOnlyReroute: "Route-Only Reroute"
                    law:
                        active when RouteFacts.current_specialist_output_missing and RouteFacts.next_owner_unknown
                        current none
                        stop "No specialist artifact is current for this turn."
                        route "Route the same issue back to RoutingOwner." -> RoutingOwner

                agent Demo:
                    role: "Keep explicit route-only reroutes aligned with the emitted handoff comment."
                    workflow: RouteOnlyReroute
                    inputs: "Inputs"
                        RouteFacts
                    outputs: "Outputs"
                        RerouteHandoffComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E339")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    next_owner: "Next Owner"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index(
                '        route "Route the same issue back to RoutingOwner." -> RoutingOwner'
            )
            + 1,
        )
        self.assertIn("routed branch", str(error))

    def test_multiple_current_subjects_report_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input CurrentHandoff: "Current Handoff"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                output CoordinationComment: "Coordination Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    current_artifact: "Current Artifact"
                        "Name the current artifact."
                    trust_surface:
                        current_artifact

                workflow InvalidRouteOnlyTurns: "Route-Only Triage"
                    law:
                        when CurrentHandoff.missing:
                            current none
                            current artifact CoordinationComment via CoordinationComment.current_artifact

                agent Demo:
                    role: "Trigger conflicting currentness."
                    workflow: InvalidRouteOnlyTurns
                    inputs: "Inputs"
                        CurrentHandoff
                    outputs: "Outputs"
                        CoordinationComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E332")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index(
                "            current artifact CoordinationComment via CoordinationComment.current_artifact"
            )
            + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("            current none") + 1,
        )
        self.assertIn("first current-subject form", str(error))

    def test_current_carrier_output_not_emitted_points_at_current_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input ApprovedPlan: "Approved Plan"
                    source: File
                        path: "unit_root/_authoring/APPROVED_PLAN.md"
                    shape: MarkdownDocument
                    requirement: Required

                output SectionMetadata: "Section Metadata"
                    target: File
                        path: "unit_root/_authoring/section_metadata.json"
                    shape: JsonObject
                    requirement: Required

                output CoordinationHandoff: "Coordination Handoff"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    current_artifact: "Current Artifact"
                        "Name the one artifact that is current now."
                    trust_surface:
                        current_artifact

                workflow InvalidCarryCurrentTruth: "Carry Current Truth"
                    law:
                        current artifact ApprovedPlan via CoordinationHandoff.current_artifact

                agent Demo:
                    role: "Trigger a missing emitted carrier output."
                    workflow: InvalidCarryCurrentTruth
                    inputs: "Inputs"
                        ApprovedPlan
                    outputs: "Outputs"
                        SectionMetadata
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E333")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index(
                "        current artifact ApprovedPlan via CoordinationHandoff.current_artifact"
            )
            + 1,
        )
        self.assertIn("Current carrier output not emitted", str(error))

    def test_current_carrier_field_missing_trust_surface_points_at_current_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input ApprovedPlan: "Approved Plan"
                    source: File
                        path: "unit_root/_authoring/APPROVED_PLAN.md"
                    shape: MarkdownDocument
                    requirement: Required

                output CoordinationHandoff: "Coordination Handoff"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    current_artifact: "Current Artifact"
                        "Name the one artifact that is current now."
                    handoff_summary: "Handoff Summary"
                        "Summarize the current truth."
                    trust_surface:
                        handoff_summary

                workflow InvalidCarryCurrentTruth: "Carry Current Truth"
                    law:
                        current artifact ApprovedPlan via CoordinationHandoff.current_artifact

                agent Demo:
                    role: "Trigger a carrier field that is not trusted downstream."
                    workflow: InvalidCarryCurrentTruth
                    inputs: "Inputs"
                        ApprovedPlan
                    outputs: "Outputs"
                        CoordinationHandoff
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E336")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index(
                "        current artifact ApprovedPlan via CoordinationHandoff.current_artifact"
            )
            + 1,
        )
        self.assertIn("Current carrier field missing from trust surface", str(error))

    def test_invalidation_carrier_field_missing_trust_surface_points_at_invalidate_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output SectionReview: "Section Review"
                    target: File
                        path: "unit_root/_authoring/SECTION_REVIEW.md"
                    shape: MarkdownDocument
                    requirement: Required

                output CoordinationHandoff: "Coordination Handoff"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    current_artifact: "Current Artifact"
                        "Name the one artifact that is current now."
                    invalidations: "Invalidations"
                        "Name any artifacts that are no longer current."
                    trust_surface:
                        current_artifact

                workflow InvalidStructureChange: "Structure Change"
                    law:
                        current none
                        invalidate SectionReview via CoordinationHandoff.invalidations

                agent Demo:
                    role: "Trigger an invalidation carrier outside the trust surface."
                    workflow: InvalidStructureChange
                    outputs: "Outputs"
                        CoordinationHandoff
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E372")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index(
                "        invalidate SectionReview via CoordinationHandoff.invalidations"
            )
            + 1,
        )
        self.assertIn("Invalidation carrier field missing from trust surface", str(error))

    def test_current_none_with_owned_scope_points_at_owned_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input ApprovedPlan: "Approved Plan"
                    source: File
                        path: "unit_root/_authoring/APPROVED_PLAN.md"
                    shape: MarkdownDocument
                    requirement: Required

                workflow InvalidOwnedRouteOnlyTurn: "Invalid Owned Route-Only Turn"
                    law:
                        current none
                        own only ApprovedPlan

                agent Demo:
                    role: "Reject owned scope on route-only turns."
                    workflow: InvalidOwnedRouteOnlyTurn
                    inputs: "Inputs"
                        ApprovedPlan
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        own only ApprovedPlan") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("        current none") + 1,
        )
        self.assertIn("`current none` statement", str(error))

    def test_owned_scope_outside_current_artifact_points_at_own_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output PrimaryManifest: "Primary Manifest"
                    target: File
                        path: "unit_root/_authoring/primary_manifest.json"
                    shape: JsonObject
                    requirement: Required

                output SectionMetadata: "Section Metadata"
                    target: File
                        path: "unit_root/_authoring/section_metadata.json"
                    shape: JsonObject
                    requirement: Required

                output CoordinationHandoff: "Coordination Handoff"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    current_artifact: "Current Artifact"
                        "Name the one artifact that is current now."
                    trust_surface:
                        current_artifact

                workflow InvalidNarrowMetadataEdit: "Narrow Metadata Edit"
                    law:
                        current artifact SectionMetadata via CoordinationHandoff.current_artifact
                        own only PrimaryManifest.title

                agent Demo:
                    role: "Trigger an own path outside the current artifact."
                    workflow: InvalidNarrowMetadataEdit
                    outputs: "Outputs"
                        SectionMetadata
                        CoordinationHandoff
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E351")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        own only PrimaryManifest.title") + 1,
        )
        self.assertIn("Owned scope is outside the allowed modeled surface", str(error))

    def test_preserve_vocabulary_enum_descendant_points_at_preserve_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                enum CriticVerdict: "Critic Verdict"
                    accept: "accept"
                    changes_requested: "changes requested"

                input ReviewTemplate: "Review Template"
                    source: Prompt
                    shape: MarkdownDocument
                    requirement: Required

                output CoordinationHandoff: "Coordination Handoff"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    current_artifact: "Current Artifact"
                        "Name the one artifact that is current now."
                    trust_surface:
                        current_artifact

                workflow PreserveVocabulary: "Preserve Vocabulary"
                    law:
                        current artifact ReviewTemplate via CoordinationHandoff.current_artifact
                        preserve vocabulary CriticVerdict.accept

                agent Demo:
                    role: "Reject enum descendants in preserve vocabulary."
                    workflow: PreserveVocabulary
                    inputs: "Inputs"
                        ReviewTemplate
                    outputs: "Outputs"
                        CoordinationHandoff
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        preserve vocabulary CriticVerdict.accept") + 1,
        )
        self.assertIn("must not descend through fields", str(error))

    def test_current_artifact_invalidation_reports_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output SectionReview: "Section Review"
                    target: File
                        path: "unit_root/_authoring/SECTION_REVIEW.md"
                    shape: MarkdownDocument
                    requirement: Required

                output CoordinationHandoff: "Coordination Handoff"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    current_artifact: "Current Artifact"
                        "Name the one artifact that is current now."
                    invalidations: "Invalidations"
                        "Name any artifacts that are no longer current."
                    trust_surface:
                        current_artifact
                        invalidations

                workflow InvalidStructureChange: "Structure Change"
                    law:
                        current artifact SectionReview via CoordinationHandoff.current_artifact
                        invalidate SectionReview via CoordinationHandoff.invalidations

                agent Demo:
                    role: "Reject invalidating the current artifact."
                    workflow: InvalidStructureChange
                    outputs: "Outputs"
                        SectionReview
                        CoordinationHandoff
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E371")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index(
                "        invalidate SectionReview via CoordinationHandoff.invalidations"
            )
            + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index(
                "        current artifact SectionReview via CoordinationHandoff.current_artifact"
            )
            + 1,
        )
        self.assertIn("current artifact statement", str(error))

    def test_current_artifact_wrong_kind_points_at_current_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                enum MetadataPolishMode: "Metadata Polish Mode"
                    manifest_title: "manifest-title"
                    section_summary: "section-summary"
                output CoordinationHandoff: "Coordination Handoff"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    current_artifact: "Current Artifact"
                        "Name the one artifact that is current now."
                    trust_surface:
                        current_artifact
                workflow InvalidCarryCurrentTruth: "Carry Current Truth"
                    law:
                        current artifact MetadataPolishMode via CoordinationHandoff.current_artifact
                agent Demo:
                    role: "Trigger a wrong-kind current target."
                    workflow: InvalidCarryCurrentTruth
                    outputs: "Outputs"
                        CoordinationHandoff
                """,
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E335")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 14)
        self.assertIn("current artifact MetadataPolishMode via CoordinationHandoff.current_artifact", str(error))

    def test_review_comment_output_not_emitted_points_at_comment_output_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input DraftSpec: "Draft Spec"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                workflow DraftReviewContract: "Draft Review Contract"
                    completeness: "Completeness"
                        "Confirm the draft covers the required sections."

                agent ReviewLead:
                    role: "Own accepted draft follow-up."

                agent DraftAuthor:
                    role: "Fix rejected draft defects."

                output DraftReviewComment: "Draft Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    verdict: "Verdict"
                        "Say whether the review accepted the draft or asked for changes."
                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact this review judged."
                    analysis_performed: "Analysis Performed"
                        "Sum up the review work."
                    output_contents_that_matter: "Output Contents That Matter"
                        "Summarize the parts that matter."
                    next_owner: "Next Owner"
                        "Name the next owner."
                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "Name the failing review gates."

                review DraftReview: "Draft Review"
                    subject: DraftSpec
                    contract: DraftReviewContract
                    comment_output: DraftReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        failing_gates: failure_detail.failing_gates
                        next_owner: next_owner

                    checks: "Checks"
                        accept "The shared draft review contract passes." when contract.passes

                    on_accept:
                        current none
                        route "Accepted draft goes to ReviewLead." -> ReviewLead

                    on_reject:
                        current none
                        route "Rejected draft goes to DraftAuthor." -> DraftAuthor

                agent Demo:
                    role: "Trigger missing review output emission."
                    review: DraftReview
                    inputs: "Inputs"
                        DraftSpec
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E479")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    comment_output: DraftReviewComment") + 1,
        )
        self.assertIn("comment_output: DraftReviewComment", str(error))

    def test_review_multiple_accept_gates_report_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input DraftSpec: "Draft Spec"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                workflow DraftReviewContract: "Draft Review Contract"
                    completeness: "Completeness"
                        "Confirm the draft covers the required sections."

                agent ReviewLead:
                    role: "Own accepted draft follow-up."

                agent DraftAuthor:
                    role: "Fix rejected draft defects."

                output DraftReviewComment: "Draft Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    verdict: "Verdict"
                        "Say whether the review accepted the draft or asked for changes."
                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact this review judged."
                    analysis_performed: "Analysis Performed"
                        "Sum up the review work."
                    output_contents_that_matter: "Output Contents That Matter"
                        "Summarize the parts that matter."
                    next_owner: "Next Owner"
                        "Name the next owner."
                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "Name the failing review gates."

                review DraftReview: "Draft Review"
                    subject: DraftSpec
                    contract: DraftReviewContract
                    comment_output: DraftReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        failing_gates: failure_detail.failing_gates
                        next_owner: next_owner

                    checks: "Checks"
                        accept "First gate passes." when contract.passes
                        accept "Second gate passes." when contract.passes

                    on_accept:
                        current none
                        route "Accepted draft goes to ReviewLead." -> ReviewLead

                    on_reject:
                        current none
                        route "Rejected draft goes to DraftAuthor." -> DraftAuthor

                agent Demo:
                    role: "Reject duplicate accept gates."
                    review: DraftReview
                    inputs: "Inputs"
                        DraftSpec
                    outputs: "Outputs"
                        DraftReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E482")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        accept "Second gate passes." when contract.passes')
            + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('        accept "First gate passes." when contract.passes')
            + 1,
        )
        self.assertIn("first `accept` gate", str(error))
        self.assertIn("Related:", str(error))

    def test_case_selected_review_overlap_reports_related_case_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                enum ReviewMode: "Review Mode"
                    draft_rewrite: "draft-rewrite"
                    metadata_refresh: "metadata-refresh"

                input DraftSpec: "Draft Spec"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                input MetadataRecord: "Metadata Record"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                input ReviewFacts: "Review Facts"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                workflow DraftReviewContract: "Draft Review Contract"
                    completeness: "Completeness"
                        "Confirm the draft covers the required sections."

                workflow MetadataReviewContract: "Metadata Review Contract"
                    freshness: "Freshness"
                        "Confirm the metadata stays current."

                agent RevisionOwner:
                    role: "Own the next revision pass after review."

                output SelectedReviewComment: "Selected Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    verdict: "Verdict"
                        "Say whether the review accepted the selected subject or asked for changes."
                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact this review judged."
                    analysis_performed: "Analysis Performed"
                        "Sum up the review work that led to the verdict."
                    output_contents_that_matter: "Output Contents That Matter"
                        "Sum up the parts of the selected subject the next owner should read first."
                    next_owner: "Next Owner"
                        "Name the next owner."
                    current_artifact: "Current Artifact"
                        "Name the artifact that is current now."
                    trust_surface:
                        current_artifact

                review_family SelectedReviewFamily: "Selected Review"
                    comment_output: SelectedReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        next_owner: next_owner
                        current_artifact: current_artifact

                    selector:
                        mode selected_mode = ReviewFacts.selected_mode as ReviewMode

                    cases:
                        draft_path: "Draft Path"
                            when ReviewMode.draft_rewrite
                            subject: DraftSpec
                            contract: DraftReviewContract
                            checks:
                                accept "The draft review contract passes." when contract.passes
                            on_accept:
                                current artifact DraftSpec via SelectedReviewComment.current_artifact
                                route "Accepted draft rewrite goes to RevisionOwner." -> RevisionOwner
                            on_reject:
                                current artifact DraftSpec via SelectedReviewComment.current_artifact
                                route "Rejected draft rewrite goes to RevisionOwner." -> RevisionOwner

                        duplicate_draft_path: "Duplicate Draft Path"
                            when ReviewMode.draft_rewrite
                            subject: MetadataRecord
                            contract: MetadataReviewContract
                            checks:
                                accept "The metadata review contract passes." when contract.passes
                            on_accept:
                                current artifact MetadataRecord via SelectedReviewComment.current_artifact
                                route "Accepted metadata refresh goes to RevisionOwner." -> RevisionOwner
                            on_reject:
                                current artifact MetadataRecord via SelectedReviewComment.current_artifact
                                route "Rejected metadata refresh goes to RevisionOwner." -> RevisionOwner

                agent Demo:
                    role: "Reject overlapping review cases."
                    review: SelectedReviewFamily
                    inputs: "Inputs"
                        DraftSpec
                        MetadataRecord
                        ReviewFacts
                    outputs: "Outputs"
                        SelectedReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)
            match_lines = [
                line_number
                for line_number, line in enumerate(rendered.splitlines(), start=1)
                if line == "            when ReviewMode.draft_rewrite"
            ]

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E470")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, match_lines[1])
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(error.diagnostic.related[0].location.line, match_lines[0])
        self.assertIn("first case for `draft-rewrite`", str(error))
        self.assertIn("Related:", str(error))

    def test_missing_inherited_review_entry_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input DraftSpec: "Draft Spec"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                workflow PatchedDraftReviewContract: "Patched Draft Review Contract"
                    completeness: "Completeness"
                        "Confirm the draft covers the required sections."

                agent ReviewLead:
                    role: "Own accepted draft follow-up."

                agent DraftAuthor:
                    role: "Repair rejected draft defects."

                output InheritedReviewComment: "Inherited Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    verdict: "Verdict"
                        "Say whether the review accepted the draft or asked for changes."
                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact this review judged."
                    analysis_performed: "Analysis Performed"
                        "Sum up the review work that led to the verdict."
                    output_contents_that_matter: "Output Contents That Matter"
                        "Summarize the parts of the draft the next owner must read first."
                    next_owner: "Next Owner"
                        "Name the next owner."
                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "Name the failing review gates in authored order."

                abstract review BaseDraftReview: "Base Draft Review"
                    comment_output: InheritedReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        failing_gates: failure_detail.failing_gates
                        next_owner: next_owner

                    shared_checks: "Shared Checks"
                        reject "The draft still lacks the shared context." when DraftSpec.context_missing

                review PatchedDraftReview[BaseDraftReview]: "Patched Draft Review"
                    subject: DraftSpec
                    contract: PatchedDraftReviewContract
                    inherit fields

                    child_specifics: "Child Specifics"
                        accept "The patched draft review contract passes." when contract.passes

                    on_accept: "If Accepted"
                        current none
                        route "Accepted draft goes to ReviewLead." -> ReviewLead

                    on_reject: "If Rejected"
                        current none
                        route "Rejected draft goes to DraftAuthor." -> DraftAuthor

                agent Demo:
                    role: "Keep missing inherited review sections from compiling."
                    review: PatchedDraftReview
                    inputs: "Inputs"
                        DraftSpec
                    outputs: "Outputs"
                        InheritedReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E490")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('review PatchedDraftReview[BaseDraftReview]: "Patched Draft Review"')
            + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    shared_checks: "Shared Checks"') + 1,
        )
        self.assertIn("Missing inherited review entry", str(error))
        self.assertIn("Related:", str(error))

    def test_duplicate_review_item_key_reports_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input DraftSpec: "Draft Spec"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                workflow PatchedDraftReviewContract: "Patched Draft Review Contract"
                    completeness: "Completeness"
                        "Confirm the draft covers the required sections."

                agent ReviewLead:
                    role: "Own accepted draft follow-up."

                agent DraftAuthor:
                    role: "Repair rejected draft defects."

                output InheritedReviewComment: "Inherited Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    verdict: "Verdict"
                        "Say whether the review accepted the draft or asked for changes."
                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact this review judged."
                    analysis_performed: "Analysis Performed"
                        "Sum up the review work that led to the verdict."
                    output_contents_that_matter: "Output Contents That Matter"
                        "Summarize the parts of the draft the next owner must read first."
                    next_owner: "Next Owner"
                        "Name the next owner."
                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "Name the failing review gates in authored order."

                abstract review BaseDraftReview: "Base Draft Review"
                    comment_output: InheritedReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        failing_gates: failure_detail.failing_gates
                        next_owner: next_owner

                    shared_checks: "Shared Checks"
                        reject "The draft still lacks the shared context." when DraftSpec.context_missing

                review PatchedDraftReview[BaseDraftReview]: "Patched Draft Review"
                    subject: DraftSpec
                    contract: PatchedDraftReviewContract
                    inherit fields
                    inherit shared_checks
                    override shared_checks:
                        reject "The draft still lacks the shared context." when DraftSpec.context_missing

                    child_specifics: "Child Specifics"
                        accept "The patched draft review contract passes." when contract.passes

                    on_accept: "If Accepted"
                        current none
                        route "Accepted draft goes to ReviewLead." -> ReviewLead

                    on_reject: "If Rejected"
                        current none
                        route "Rejected draft goes to DraftAuthor." -> DraftAuthor

                agent Demo:
                    role: "Keep duplicate inherited review section accounting from compiling."
                    review: PatchedDraftReview
                    inputs: "Inputs"
                        DraftSpec
                    outputs: "Outputs"
                        InheritedReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E491")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    override shared_checks:") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("    inherit shared_checks") + 1,
        )
        self.assertIn("Duplicate review item key", str(error))
        self.assertIn("first `shared_checks` entry", str(error))

    def test_review_contract_without_gates_points_at_contract_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                schema GateLessContract: "Gate-Less Contract"
                    sections:
                        summary: "Summary"
                            "Summarize the reviewed plan."

                input DraftPlan: "Draft Plan"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                output PlanReviewComment: "Plan Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    verdict: "Verdict"
                        "State the review verdict."
                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact."
                    analysis_performed: "Analysis Performed"
                        "Summarize the review analysis."
                    output_contents_that_matter: "Output Contents That Matter"
                        "State what the next owner should read first."
                    next_owner: "Next Owner"
                        "Name the next owner."
                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "List exact failing gates when they fail."

                review InvalidGateLessReview: "Invalid Gate-Less Review"
                    subject: DraftPlan
                    contract: GateLessContract
                    comment_output: PlanReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        failing_gates: failure_detail.failing_gates
                        next_owner: next_owner

                    contract_gate_checks: "Contract Gate Checks"
                        accept "The schema review contract passes." when contract.passes

                    on_accept: "If Accepted"
                        current none

                    on_reject: "If Rejected"
                        current none

                agent Demo:
                    role: "This review references a schema contract with no gates."
                    review: InvalidGateLessReview
                    inputs: "Inputs"
                        DraftPlan
                    outputs: "Outputs"
                        PlanReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E477")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    contract: GateLessContract") + 1,
        )
        self.assertIn("Review contract `GateLessContract`", str(error))

    def test_unknown_review_contract_gate_points_at_gate_ref_line(self) -> None:
        prompt_path, error = self._compile_repo_prompt_error(
            "examples/45_review_contract_gate_export_and_exact_failures/prompts/INVALID_UNKNOWN_CONTRACT_GATE.prompt",
            agent="InvalidUnknownContractGateDemo",
        )
        prompt_lines = prompt_path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(error.diagnostic.code, "E477")
        self.assertEqual(error.diagnostic.location.path, prompt_path)
        self.assertEqual(
            error.diagnostic.location.line,
            prompt_lines.index(
                "        reject contract.missing_gate when DraftSpec.next_action_missing"
            )
            + 1,
        )
        self.assertIn("Unknown review contract gate", str(error))

    def test_review_contract_with_workflow_law_points_at_law_line(self) -> None:
        prompt_path, error = self._compile_repo_prompt_error(
            "examples/45_review_contract_gate_export_and_exact_failures/prompts/INVALID_CONTRACT_TARGET_WITH_LAW.prompt",
            agent="InvalidContractTargetWithLawDemo",
        )
        prompt_lines = prompt_path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(error.diagnostic.code, "E477")
        self.assertEqual(error.diagnostic.location.path, prompt_path)
        self.assertEqual(
            error.diagnostic.location.line,
            prompt_lines.index("        active when DraftSpec.ready_for_execution") + 1,
        )
        self.assertIn("unsupported workflow features", str(error))

    def test_duplicate_review_subject_map_entry_reports_related_line(self) -> None:
        prompt_path, error = self._compile_repo_prompt_error(
            "examples/47_review_multi_subject_mode_and_trigger_carry/prompts/INVALID_DUPLICATE_SUBJECT_MAP_ENTRY.prompt",
            agent="MultiSubjectReviewDemo",
        )
        prompt_lines = prompt_path.read_text(encoding="utf-8").splitlines()
        duplicate_line = "        ReviewMode.draft_rewrite: MetadataRecord"
        first_line = "        ReviewMode.draft_rewrite: DraftSpec"

        self.assertEqual(error.diagnostic.code, "E470")
        self.assertEqual(error.diagnostic.location.path, prompt_path)
        self.assertEqual(
            error.diagnostic.location.line,
            prompt_lines.index(duplicate_line) + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            prompt_lines.index(first_line) + 1,
        )
        self.assertIn("Duplicate review subject_map entry", str(error))
        self.assertIn("Related:", str(error))

    def test_duplicate_review_field_binding_reports_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input DraftSpec: "Draft Spec"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                workflow DraftReviewContract: "Draft Review Contract"
                    completeness: "Completeness"
                        "Confirm the draft covers the required sections."

                agent DraftAuthor:
                    role: "Repair rejected draft defects."
                    workflow: "Revise"
                        "Revise the draft."

                output DraftReviewComment: "Draft Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    verdict: "Verdict"
                        "State the review verdict."
                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact."
                    analysis_performed: "Analysis Performed"
                        "Summarize the review analysis."
                    output_contents_that_matter: "Output Contents That Matter"
                        "State what the next owner should read first."
                    next_owner: "Next Owner"
                        "Name the next owner."
                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "List failing gates when they fail."

                review DuplicateFieldReview: "Duplicate Field Review"
                    subject: DraftSpec
                    contract: DraftReviewContract
                    comment_output: DraftReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        failing_gates: failure_detail.failing_gates
                        next_owner: next_owner
                        next_owner: next_owner

                    checks: "Checks"
                        accept "The shared review contract passes." when contract.passes

                    on_accept: "If Accepted"
                        current none
                        route "Accepted draft stays local." -> DraftAuthor

                    on_reject: "If Rejected"
                        current none
                        route "Rejected draft stays local." -> DraftAuthor

                agent Demo:
                    role: "Keep duplicate review field bindings from compiling."
                    review: DuplicateFieldReview
                    inputs: "Inputs"
                        DraftSpec
                    outputs: "Outputs"
                        DraftReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        next_owner_lines = [
            line_number
            for line_number, line in enumerate(rendered.splitlines(), start=1)
            if line == "        next_owner: next_owner"
        ]
        self.assertEqual(error.diagnostic.code, "E473")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, next_owner_lines[1])
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(error.diagnostic.related[0].location.line, next_owner_lines[0])
        self.assertIn("duplicate binding", str(error))
        self.assertIn("Related:", str(error))

    def test_duplicate_composed_review_contract_gate_reports_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input DraftSpec: "Draft Spec"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                workflow SharedGateA: "Shared Gate A"
                    completeness: "Completeness"
                        "Confirm the draft covers the required sections."

                workflow SharedGateB: "Shared Gate B"
                    completeness: "Completeness"
                        "Confirm the draft still covers the required sections."

                workflow DuplicateGateContract: "Duplicate Gate Contract"
                    use first: SharedGateA
                    use second: SharedGateB

                agent DraftAuthor:
                    role: "Repair rejected draft defects."
                    workflow: "Revise"
                        "Revise the draft."

                output DraftReviewComment: "Draft Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    verdict: "Verdict"
                        "State the review verdict."
                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact."
                    analysis_performed: "Analysis Performed"
                        "Summarize the review analysis."
                    output_contents_that_matter: "Output Contents That Matter"
                        "State what the next owner should read first."
                    next_owner: "Next Owner"
                        "Name the next owner."
                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "List failing gates when they fail."

                review DuplicateGateReview: "Duplicate Gate Review"
                    subject: DraftSpec
                    contract: DuplicateGateContract
                    comment_output: DraftReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        failing_gates: failure_detail.failing_gates
                        next_owner: next_owner

                    checks: "Checks"
                        accept "The shared review contract passes." when contract.passes

                    on_accept: "If Accepted"
                        current none
                        route "Accepted draft stays local." -> DraftAuthor

                    on_reject: "If Rejected"
                        current none
                        route "Rejected draft stays local." -> DraftAuthor

                agent Demo:
                    role: "Keep duplicate composed review contract gates from compiling."
                    review: DuplicateGateReview
                    inputs: "Inputs"
                        DraftSpec
                    outputs: "Outputs"
                        DraftReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        completeness_lines = [
            line_number
            for line_number, line in enumerate(rendered.splitlines(), start=1)
            if line == '    completeness: "Completeness"'
        ]
        self.assertEqual(error.diagnostic.code, "E477")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, completeness_lines[1])
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(error.diagnostic.related[0].location.line, completeness_lines[0])
        self.assertIn("Duplicate review contract gate", str(error))
        self.assertIn("Related:", str(error))

    def test_review_match_without_else_points_at_match_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                enum ReviewMode: "Review Mode"
                    draft_rewrite: "draft-rewrite"
                    metadata_refresh: "metadata-refresh"

                input DraftSpec: "Draft Spec"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                input ReviewFacts: "Review Facts"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                workflow DraftReviewContract: "Draft Review Contract"
                    completeness: "Completeness"
                        "Confirm the draft covers the required sections."

                agent DraftAuthor:
                    role: "Repair rejected draft defects."
                    workflow: "Revise"
                        "Revise the draft."

                output DraftReviewComment: "Draft Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    verdict: "Verdict"
                        "State the review verdict."
                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact."
                    analysis_performed: "Analysis Performed"
                        "Summarize the review analysis."
                    output_contents_that_matter: "Output Contents That Matter"
                        "State what the next owner should read first."
                    next_owner: "Next Owner"
                        "Name the next owner."
                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "List failing gates when they fail."

                review IncompleteMatchReview: "Incomplete Match Review"
                    subject: DraftSpec
                    contract: DraftReviewContract
                    comment_output: DraftReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        failing_gates: failure_detail.failing_gates
                        next_owner: next_owner

                    checks: "Checks"
                        match ReviewFacts.selected_mode:
                            ReviewMode.draft_rewrite:
                                reject "The selected draft still needs changes." when ReviewFacts.force_reject
                        accept "The shared review contract passes." when contract.passes

                    on_accept: "If Accepted"
                        current none
                        route "Accepted draft stays local." -> DraftAuthor

                    on_reject: "If Rejected"
                        current none
                        route "Rejected draft stays local." -> DraftAuthor

                agent Demo:
                    role: "Keep non-total review matches from compiling."
                    review: IncompleteMatchReview
                    inputs: "Inputs"
                        DraftSpec
                        ReviewFacts
                    outputs: "Outputs"
                        DraftReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E484")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        match ReviewFacts.selected_mode:") + 1,
        )
        self.assertIn("include `else`", str(error))

    def test_review_current_carrier_output_not_emitted_uses_review_code(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input DraftSpec: "Draft Spec"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                workflow CurrentTruthReviewContract: "Current Truth Review Contract"
                    completeness: "Completeness"
                        "Confirm the draft covers the required sections."

                agent ReviewLead:
                    role: "Own accepted draft follow-up."

                output CurrentTruthReviewComment: "Current Truth Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    verdict: "Verdict"
                        "State the review verdict."
                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact."
                    analysis_performed: "Analysis Performed"
                        "Summarize the review analysis."
                    output_contents_that_matter: "Output Contents That Matter"
                        "State what the next owner should read first."
                    next_owner: "Next Owner"
                        "Name the next owner."
                    current_artifact: "Current Artifact"
                        "Name the artifact that is current now."
                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "List exact failing gates when they fail."
                    trust_surface:
                        current_artifact

                output SideChannelComment: "Side Channel Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Optional
                    current_artifact: "Current Artifact"
                        "Name the artifact that is current now."
                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "List exact failing gates when they fail."
                    trust_surface:
                        current_artifact

                review CurrentTruthReview: "Current Truth Review"
                    subject: DraftSpec
                    contract: CurrentTruthReviewContract
                    comment_output: CurrentTruthReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        failing_gates: failure_detail.failing_gates
                        next_owner: next_owner

                    current_truth_checks: "Current Truth Checks"
                        accept "The shared review contract passes." when contract.passes

                    on_accept: "If Accepted"
                        current artifact DraftSpec via SideChannelComment.current_artifact
                        route "Accepted draft goes to ReviewLead." -> ReviewLead

                    on_reject: "If Rejected"
                        current artifact DraftSpec via SideChannelComment.current_artifact
                        route "Rejected draft goes to ReviewLead." -> ReviewLead

                agent Demo:
                    role: "Reject review currentness carriers on unbound outputs."
                    review: CurrentTruthReview
                    inputs: "Inputs"
                        DraftSpec
                    outputs: "Outputs"
                        CurrentTruthReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E487")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index(
                "        current artifact DraftSpec via SideChannelComment.current_artifact"
            )
            + 1,
        )
        self.assertIn("Review currentness requires a valid carrier", str(error))

    def test_review_current_carrier_trust_surface_uses_review_code(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input DraftSpec: "Draft Spec"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                workflow CurrentTruthReviewContract: "Current Truth Review Contract"
                    completeness: "Completeness"
                        "Confirm the draft covers the required sections."

                agent ReviewLead:
                    role: "Own accepted draft follow-up."

                output CurrentTruthReviewComment: "Current Truth Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    verdict: "Verdict"
                        "State the review verdict."
                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact."
                    analysis_performed: "Analysis Performed"
                        "Summarize the review analysis."
                    output_contents_that_matter: "Output Contents That Matter"
                        "State what the next owner should read first."
                    next_owner: "Next Owner"
                        "Name the next owner."
                    current_artifact: "Current Artifact"
                        "Name the artifact that is current now."
                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "List exact failing gates when they fail."

                review CurrentTruthReview: "Current Truth Review"
                    subject: DraftSpec
                    contract: CurrentTruthReviewContract
                    comment_output: CurrentTruthReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        failing_gates: failure_detail.failing_gates
                        next_owner: next_owner

                    current_truth_checks: "Current Truth Checks"
                        accept "The shared review contract passes." when contract.passes

                    on_accept: "If Accepted"
                        current artifact DraftSpec via CurrentTruthReviewComment.current_artifact
                        route "Accepted draft goes to ReviewLead." -> ReviewLead

                    on_reject: "If Rejected"
                        current artifact DraftSpec via CurrentTruthReviewComment.current_artifact
                        route "Rejected draft goes to ReviewLead." -> ReviewLead

                agent Demo:
                    role: "Reject review currentness carriers outside the trust surface."
                    review: CurrentTruthReview
                    inputs: "Inputs"
                        DraftSpec
                    outputs: "Outputs"
                        CurrentTruthReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E488")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index(
                "        current artifact DraftSpec via CurrentTruthReviewComment.current_artifact"
            )
            + 1,
        )
        self.assertIn("Review current carrier is missing from trust surface", str(error))

    def test_missing_input_source_points_at_input_header(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input MissingSource: "Missing Source"
                    shape: JsonObject
                    requirement: Required

                agent Demo:
                    role: "Reject inputs without a typed source."
                    inputs: "Inputs"
                        MissingSource
                    workflow: "Reply"
                        "Answer directly."
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E221")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('input MissingSource: "Missing Source"') + 1,
        )
        self.assertIn("Input `MissingSource` is missing a typed `source` field.", str(error))

    def test_output_files_and_target_conflict_reports_related_locations(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output InvalidBundle: "Invalid Bundle"
                    target: TurnResponse
                    shape: Comment
                    files: "Files"
                        transcript: "Transcript"
                            path: "unit_root/TRANSCRIPT.md"
                            shape: MarkdownDocument

                agent Demo:
                    role: "Reject mixed output contracts."
                    outputs: "Outputs"
                        InvalidBundle
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E224")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    files: "Files"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 2)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("    target: TurnResponse") + 1,
        )
        self.assertEqual(
            error.diagnostic.related[1].location.line,
            rendered.splitlines().index("    shape: Comment") + 1,
        )
        self.assertIn("mixes `files` with `target` or `shape`", str(error))
        self.assertIn("conflicting `target` field", str(error))

    def test_output_missing_shape_points_at_target_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output IncompleteOutput: "Incomplete Output"
                    target: TurnResponse

                agent Demo:
                    role: "Reject incomplete output declarations."
                    outputs: "Outputs"
                        IncompleteOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E224")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    target: TurnResponse") + 1,
        )
        self.assertIn("must define either `files` or both `target` and `shape`", str(error))

    def test_duplicate_output_target_config_key_reports_related_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output InvalidFileOutput: "Invalid File Output"
                    target: File
                        path: "unit_root/ONE.md"
                        path: "unit_root/TWO.md"
                    shape: MarkdownDocument

                agent Demo:
                    role: "Reject duplicate output target config keys."
                    outputs: "Outputs"
                        InvalidFileOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E231")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        path: "unit_root/TWO.md"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('        path: "unit_root/ONE.md"') + 1,
        )
        self.assertIn("repeats key `path`", str(error))
        self.assertIn("first `path` config entry", str(error))

    def test_unknown_output_target_config_key_points_at_config_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output InvalidFileOutput: "Invalid File Output"
                    target: File
                        path: "unit_root/ONE.md"
                        mode: "append"
                    shape: MarkdownDocument

                agent Demo:
                    role: "Reject unknown output target config keys."
                    outputs: "Outputs"
                        InvalidFileOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E232")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        mode: "append"') + 1,
        )
        self.assertIn("uses unknown key `mode`", str(error))

    def test_missing_output_target_config_key_points_at_target_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output InvalidFileOutput: "Invalid File Output"
                    target: File
                    shape: MarkdownDocument

                agent Demo:
                    role: "Reject missing required output target config keys."
                    outputs: "Outputs"
                        InvalidFileOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E233")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    target: File") + 1,
        )
        self.assertIn("is missing required key `path`", str(error))

    def test_input_config_entries_must_be_scalar_lines_point_at_bad_config_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input InboxFile: "Inbox File"
                    source: File
                        path: "unit_root/INBOX.md"
                            "This should fail."
                    shape: MarkdownDocument
                    requirement: Required

                agent Demo:
                    role: "Reject config entries with nested bodies."
                    inputs: "Inputs"
                        InboxFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E230")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        path: "unit_root/INBOX.md"') + 1,
        )
        self.assertIn("scalar key/value lines", str(error))

    def test_duplicate_input_config_key_reports_related_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input InboxFile: "Inbox File"
                    source: File
                        path: "unit_root/ONE.md"
                        path: "unit_root/TWO.md"
                    shape: MarkdownDocument
                    requirement: Required

                agent Demo:
                    role: "Reject duplicate config keys."
                    inputs: "Inputs"
                        InboxFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E231")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        path: "unit_root/TWO.md"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('        path: "unit_root/ONE.md"') + 1,
        )
        self.assertIn("repeats key `path`", str(error))

    def test_missing_input_config_key_points_at_source_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input InboxFile: "Inbox File"
                    source: File
                    shape: MarkdownDocument
                    requirement: Required

                agent Demo:
                    role: "Reject missing required config keys."
                    inputs: "Inputs"
                        InboxFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E233")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    source: File") + 1,
        )
        self.assertIn("is missing required key `path`", str(error))

    def test_config_key_declaration_must_use_string_label_points_at_decl_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input source InboxSource: "Inbox Source"
                    required: "Required"
                        path: File

                input InboxFile: "Inbox File"
                    source: InboxSource
                        path: "unit_root/INBOX.md"
                    shape: MarkdownDocument
                    requirement: Required

                agent Demo:
                    role: "Reject non-string config key labels."
                    inputs: "Inputs"
                        InboxFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E234")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        path: File") + 1,
        )
        self.assertIn("must use a string label", str(error))

    def test_imported_duplicate_config_key_declaration_reports_imported_file_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            imported_path = self._write_prompt(
                root,
                """\
                input source InboxSource: "Inbox Source"
                    required: "Required"
                        path: "Path"
                        path: "Path Again"
                """,
                rel_path="prompts/shared/input_source.prompt",
            )
            source = """\
                import shared.input_source

                input InboxFile: "Inbox File"
                    source: shared.input_source.InboxSource
                        path: "unit_root/INBOX.md"
                    shape: MarkdownDocument
                    requirement: Required

                agent Demo:
                    role: "Reject duplicate imported config key declarations."
                    inputs: "Inputs"
                        InboxFile
                """
            imported_rendered = textwrap.dedent(
                """\
                input source InboxSource: "Inbox Source"
                    required: "Required"
                        path: "Path"
                        path: "Path Again"
                """
            )
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E235")
        self.assertEqual(error.diagnostic.location.path, imported_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            imported_rendered.splitlines().index('        path: "Path Again"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            imported_rendered.splitlines().index('        path: "Path"') + 1,
        )
        self.assertIn("repeats config key declaration `path`", str(error))

    def test_missing_local_output_shape_points_at_shape_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenOutput: "Broken Output"
                    target: TurnResponse
                    shape: MissingShape
                    requirement: Required

                agent Demo:
                    role: "Reject missing local output shapes."
                    outputs: "Outputs"
                        BrokenOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E276")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    shape: MissingShape") + 1,
        )
        self.assertIn("does not exist in the current module", str(error))

    def test_missing_local_table_declaration_points_at_named_table_use_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                document ReleaseGuide: "Release Guide"
                    table release_gates: MissingTable required

                output ReleaseGuideFile: "Release Guide File"
                    target: File
                        path: "release_root/RELEASE_GUIDE.md"
                    shape: MarkdownDocument
                    structure: ReleaseGuide
                    requirement: Required

                agent Demo:
                    role: "Ship the file."
                    outputs: "Outputs"
                        ReleaseGuideFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E276")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    table release_gates: MissingTable required") + 1,
        )
        self.assertIn("Missing local table declaration: MissingTable", str(error))

    def test_input_source_must_stay_typed_points_at_source_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input BrokenInput: "Broken Input"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                agent Demo:
                    role: "Reject untyped input source titles."
                    workflow: "Reply"
                        "{{BrokenInput.source.title}}"
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            session = CompilationSession(parse_file(prompt_path))
            context = CompilationContext(session)
            input_decl = session.root_unit.inputs_by_name["BrokenInput"]
            source_item = next(
                item
                for item in input_decl.items
                if isinstance(item, model.RecordScalar) and item.key == "source"
            )
            broken_item = replace(source_item, value="Prompt")
            broken_input_decl = replace(
                input_decl,
                items=tuple(
                    broken_item if item is source_item else item for item in input_decl.items
                ),
            )

            with self.assertRaises(CompileError) as ctx:
                context._display_record_scalar_title(
                    broken_item,
                    node=AddressableNode(
                        unit=session.root_unit,
                        root_decl=broken_input_decl,
                        target=broken_item,
                    ),
                    owner_label="agent Demo workflow",
                    surface_label="workflow prose",
                )

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E275")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    source: Prompt") + 1,
        )
        self.assertIn("Input source must stay typed", str(error))

    def test_output_target_must_stay_typed_points_at_target_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenOutput: "Broken Output"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                agent Demo:
                    role: "Reject untyped output target titles."
                    workflow: "Reply"
                        "{{BrokenOutput.target.title}}"
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            session = CompilationSession(parse_file(prompt_path))
            context = CompilationContext(session)
            output_decl = session.root_unit.outputs_by_name["BrokenOutput"]
            target_item = next(
                item
                for item in output_decl.items
                if isinstance(item, model.RecordScalar) and item.key == "target"
            )
            broken_item = replace(target_item, value="TurnResponse")
            broken_output_decl = replace(
                output_decl,
                items=tuple(
                    broken_item if item is target_item else item for item in output_decl.items
                ),
            )

            with self.assertRaises(CompileError) as ctx:
                context._display_record_scalar_title(
                    broken_item,
                    node=AddressableNode(
                        unit=session.root_unit,
                        root_decl=broken_output_decl,
                        target=broken_item,
                    ),
                    owner_label="agent Demo workflow",
                    surface_label="workflow prose",
                )

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E275")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    target: TurnResponse") + 1,
        )
        self.assertIn("Output target must stay typed", str(error))

    def test_output_structure_requires_markdown_shape_points_at_shape_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                document LessonPlan: "Lesson Plan"
                    section overview: "Overview"
                        "Start with the plan overview."

                output InvalidCommentOutput: "Invalid Comment Output"
                    target: TurnResponse
                    shape: Comment
                    structure: LessonPlan
                    requirement: Required

                agent Demo:
                    role: "Reject non-markdown output structure attachments."
                    outputs: "Outputs"
                        InvalidCommentOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E302")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    shape: Comment") + 1,
        )
        self.assertIn("Output structure requires a markdown-bearing shape", str(error))

    def test_output_attached_schema_without_sections_reports_schema_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input OutlineFile: "Outline File"
                    source: File
                        path: "unit_root/OUTLINE.md"
                    shape: MarkdownDocument
                    requirement: Required

                schema ArtifactOnlySchema: "Artifact Only Schema"
                    artifacts:
                        outline_file: "Outline File"
                            ref: OutlineFile

                output BuildPlan: "Build Plan"
                    target: File
                        path: "unit_root/BUILD_PLAN.md"
                    shape: MarkdownDocument
                    requirement: Required
                    schema: ArtifactOnlySchema

                agent Demo:
                    role: "Reject attached schemas without sections."
                    outputs: "Outputs"
                        BuildPlan
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E302")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('output BuildPlan: "Build Plan"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('schema ArtifactOnlySchema: "Artifact Only Schema"') + 1,
        )
        self.assertIn("Output-attached schema must export at least one section", str(error))
        self.assertIn("attached schema `ArtifactOnlySchema`", str(error))

    def test_cyclic_schema_inheritance_points_at_schema_decl_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input OutlineFile: "Outline File"
                    source: File
                        path: "unit_root/OUTLINE.md"
                    shape: MarkdownDocument
                    requirement: Required

                schema FirstSchema[SecondSchema]: "First Schema"
                    inherit artifacts

                schema SecondSchema[FirstSchema]: "Second Schema"
                    inherit artifacts

                output BuildPlan: "Build Plan"
                    target: File
                        path: "unit_root/BUILD_PLAN.md"
                    shape: MarkdownDocument
                    requirement: Required
                    schema: FirstSchema

                agent Demo:
                    role: "Reject cyclic schema inheritance."
                    outputs: "Outputs"
                        BuildPlan
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('schema FirstSchema[SecondSchema]: "First Schema"') + 1,
        )
        self.assertIn(
            "Cyclic schema inheritance: FirstSchema -> SecondSchema -> FirstSchema",
            str(error),
        )

    def test_missing_inherited_schema_block_reports_related_parent_block_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input OutlineFile: "Outline File"
                    source: File
                        path: "unit_root/OUTLINE.md"
                    shape: MarkdownDocument
                    requirement: Required

                schema BaseSchema: "Base Schema"
                    sections:
                        summary: "Summary"
                            "Summarize the release."

                    artifacts:
                        outline_file: "Outline File"
                            ref: OutlineFile

                schema ChildSchema[BaseSchema]: "Child Schema"
                    override sections:
                        summary: "Summary"
                            "Keep the child summary."

                output BuildPlan: "Build Plan"
                    target: File
                        path: "unit_root/BUILD_PLAN.md"
                    shape: MarkdownDocument
                    requirement: Required
                    schema: ChildSchema

                agent Demo:
                    role: "Reject missing inherited schema blocks."
                    outputs: "Outputs"
                        BuildPlan
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E003")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('schema ChildSchema[BaseSchema]: "Child Schema"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("    artifacts:") + 1,
        )
        self.assertIn("Missing inherited schema block in ChildSchema: artifacts", str(error))

    def test_schema_artifact_wrong_kind_points_at_ref_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                schema BrokenArtifactSchema: "Broken Artifact Schema"
                    sections:
                        summary: "Summary"
                            "Summarize the release."

                    artifacts:
                        schema_ref: "Schema Ref"
                            ref: BrokenArtifactSchema

                output BuildPlan: "Build Plan"
                    target: File
                        path: "unit_root/BUILD_PLAN.md"
                    shape: MarkdownDocument
                    requirement: Required
                    schema: BrokenArtifactSchema

                agent Demo:
                    role: "Reject non-root schema artifact refs."
                    outputs: "Outputs"
                        BuildPlan
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E303")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("            ref: BrokenArtifactSchema") + 1,
        )
        self.assertIn(
            "Schema artifact refs must resolve to input or output declarations",
            str(error),
        )

    def test_unknown_schema_group_member_points_at_group_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input OutlineFile: "Outline File"
                    source: File
                        path: "unit_root/OUTLINE.md"
                    shape: MarkdownDocument
                    requirement: Required

                schema BrokenGroupSchema: "Broken Group Schema"
                    sections:
                        summary: "Summary"
                            "Summarize the release."

                    artifacts:
                        outline_file: "Outline File"
                            ref: OutlineFile

                    groups:
                        publish_packet: "Publish Packet"
                            missing_file

                output BuildPlan: "Build Plan"
                    target: File
                        path: "unit_root/BUILD_PLAN.md"
                    shape: MarkdownDocument
                    requirement: Required
                    schema: BrokenGroupSchema

                agent Demo:
                    role: "Reject unknown schema group members."
                    outputs: "Outputs"
                        BuildPlan
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E303")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        publish_packet: "Publish Packet"') + 1,
        )
        self.assertIn("Unknown schema group member in BrokenGroupSchema: publish_packet.missing_file", str(error))

    def test_output_files_entries_must_be_titled_sections_points_at_bad_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenBundle: "Broken Bundle"
                    files: "Files"
                        path: "unit_root/BROKEN.md"
                    requirement: Required

                agent Demo:
                    role: "Reject non-section output artifacts."
                    outputs: "Outputs"
                        BrokenBundle
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        path: "unit_root/BROKEN.md"') + 1,
        )
        self.assertIn("`files` entries must be titled sections", str(error))

    def test_output_file_entry_missing_shape_points_at_artifact_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenBundle: "Broken Bundle"
                    files: "Files"
                        artifact: "Artifact"
                            path: "unit_root/BROKEN.md"
                    requirement: Required

                agent Demo:
                    role: "Reject output artifacts without shape."
                    outputs: "Outputs"
                        BrokenBundle
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        artifact: "Artifact"') + 1,
        )
        self.assertIn("Output file entry is missing shape in BrokenBundle: artifact", str(error))

    def test_flow_missing_target_agent_reports_file_scoped_e201(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                agent Demo:
                    role: "Own the flow."
                """,
            )
            session = CompilationSession(parse_file(prompt_path))

            with self.assertRaises(CompileError) as ctx:
                session.extract_target_flow_graph_from_units(((session.root_unit, "Missing"),))

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E201")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertIsNone(error.diagnostic.location.line)
        self.assertIn("Missing target agent", str(error))

    def test_flow_abstract_target_agent_reports_file_scoped_e202(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                abstract agent Demo:
                    role: "Own the abstract flow."
                """,
            )
            session = CompilationSession(parse_file(prompt_path))

            with self.assertRaises(CompileError) as ctx:
                session.extract_target_flow_graph_from_units(((session.root_unit, "Demo"),))

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E202")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertIsNone(error.diagnostic.location.line)
        self.assertIn("Abstract agent does not render", str(error))

    def test_flow_cyclic_workflow_composition_points_at_workflow_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                workflow FirstWorkflow: "First Workflow"
                    use second: SecondWorkflow

                workflow SecondWorkflow: "Second Workflow"
                    use first: FirstWorkflow

                agent Demo:
                    role: "Own the flow."
                    workflow: FirstWorkflow
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            session = CompilationSession(parse_file(prompt_path))

            with self.assertRaises(CompileError) as ctx:
                session.extract_target_flow_graph_from_units(((session.root_unit, "Demo"),))

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E283")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('workflow SecondWorkflow: "Second Workflow"') + 1,
        )
        self.assertIn("Workflow composition cycle", str(error))

    def test_flow_duplicate_config_key_reports_related_first_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input BrokenInput: "Broken Input"
                    source: File
                        path: "unit_root/FIRST.md"
                        path: "unit_root/SECOND.md"
                    shape: MarkdownDocument
                    requirement: Required

                agent Demo:
                    role: "Own the flow."
                    inputs: "Inputs"
                        BrokenInput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            session = CompilationSession(parse_file(prompt_path))

            with self.assertRaises(CompileError) as ctx:
                session.extract_target_flow_graph_from_units(((session.root_unit, "Demo"),))

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E231")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        path: "unit_root/SECOND.md"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('        path: "unit_root/FIRST.md"') + 1,
        )
        self.assertIn("Duplicate config key", str(error))
        self.assertIn("first `path` config entry", str(error))

    def test_flow_output_file_entry_missing_shape_points_at_artifact_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenBundle: "Broken Bundle"
                    files: "Files"
                        artifact: "Artifact"
                            path: "unit_root/BROKEN.md"
                    requirement: Required

                agent Demo:
                    role: "Own the flow."
                    outputs: "Outputs"
                        BrokenBundle
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            session = CompilationSession(parse_file(prompt_path))

            with self.assertRaises(CompileError) as ctx:
                session.extract_target_flow_graph_from_units(((session.root_unit, "Demo"),))

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        artifact: "Artifact"') + 1,
        )
        self.assertIn("Output file entry is missing shape in BrokenBundle: artifact", str(error))

    def test_output_record_table_failure_points_at_offending_block_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenOutput: "Broken Output"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    must_include: "Must Include"
                        bullets summary: "Summary"
                            "This should fail."

                agent Demo:
                    role: "Reject non-record must_include blocks."
                    outputs: "Outputs"
                        BrokenOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        bullets summary: "Summary"') + 1,
        )
        self.assertIn("Must Include must stay record-shaped", str(error))

    def test_support_files_entries_must_be_titled_sections_points_at_bad_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenOutput: "Broken Output"
                    target: File
                        path: "unit_root/OUT.md"
                    shape: MarkdownDocument
                    requirement: Required

                    support_files: "Support Files"
                        path: "unit_root/AUDIT.md"

                agent Demo:
                    role: "Reject non-section support files."
                    outputs: "Outputs"
                        BrokenOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        path: "unit_root/AUDIT.md"') + 1,
        )
        self.assertIn("support_files entries must be titled sections", str(error))

    def test_support_files_entry_missing_string_path_points_at_path_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenOutput: "Broken Output"
                    target: File
                        path: "unit_root/OUT.md"
                    shape: MarkdownDocument
                    requirement: Required

                    support_files: "Support Files"
                        audit: "AUDIT.md"
                            path: TurnResponse

                agent Demo:
                    role: "Reject support files without a string path."
                    outputs: "Outputs"
                        BrokenOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("            path: TurnResponse") + 1,
        )
        self.assertIn(
            "support_files entry is missing string path in output BrokenOutput.support_files: audit",
            str(error),
        )

    def test_final_output_requires_output_declaration_points_at_final_output_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                schema ReleaseSchema: "Release Schema"
                    sections:
                        summary: "Summary"
                            "Provide a summary."

                agent InvalidAgent:
                    role: "Try to point final_output at a schema."
                    workflow: "Reply"
                        "Reply and stop."
                    final_output: ReleaseSchema
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("InvalidAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E211")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    final_output: ReleaseSchema") + 1,
        )
        self.assertIn("points at `ReleaseSchema`", str(error))

    def test_final_output_not_emitted_points_at_final_output_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output FinalReply: "Final Reply"
                    target: TurnResponse
                    shape: CommentText
                    requirement: Required

                agent InvalidAgent:
                    role: "Forget to emit the declared final output."
                    workflow: "Reply"
                        "Reply and stop."
                    final_output: FinalReply
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("InvalidAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E212")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    final_output: FinalReply") + 1,
        )
        self.assertIn("not emitted by the concrete turn", str(error))

    def test_final_output_rejects_file_target_points_at_target_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output ReleaseNotesFile: "Release Notes File"
                    target: File
                        path: "artifacts/RELEASE_NOTES.md"
                    shape: MarkdownDocument
                    requirement: Required

                agent InvalidAgent:
                    role: "Try to end with a file."
                    workflow: "Reply"
                        "Reply and stop."
                    outputs: "Outputs"
                        ReleaseNotesFile
                    final_output: ReleaseNotesFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("InvalidAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E213")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    target: File") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("    final_output: ReleaseNotesFile") + 1,
        )
        self.assertIn("not one `TurnResponse` assistant message", str(error))
        self.assertIn("`final_output` field", str(error))

    def test_final_output_example_file_retired_points_at_example_file_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field summary: "Summary"
                        type: string

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema
                    example_file: "examples/repo_status.json"

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E215")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    example_file: "examples/repo_status.json"') + 1,
        )
        self.assertIn("still uses retired `example_file`", str(error))

    def test_final_output_example_mismatch_points_at_example_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field summary: "Summary"
                        type: string

                    example:
                        summary: 7

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E216")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    example:") + 1,
        )
        self.assertIn("does not match the lowered schema", str(error))
        self.assertIn("7 is not of type 'string'", str(error))

    def test_final_output_invalid_json_schema_points_at_schema_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field summary: "Summary"
                        type: definitely_not_a_real_json_schema_type

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E217")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('output schema RepoStatusSchema: "Repo Status Schema"') + 1,
        )
        self.assertIn("not valid Draft 2020-12 JSON Schema", str(error))
        self.assertIn("definitely_not_a_real_json_schema_type", str(error))

    def test_final_output_openai_subset_failure_points_at_schema_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field level_1: "Level 1"
                        type: object
                        field level_2: "Level 2"
                            type: object
                            field level_3: "Level 3"
                                type: object
                                field level_4: "Level 4"
                                    type: object
                                    field level_5: "Level 5"
                                        type: object
                                        field level_6: "Level 6"
                                            type: string

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E218")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('output schema RepoStatusSchema: "Repo Status Schema"') + 1,
        )
        self.assertIn("outside the supported OpenAI structured outputs subset", str(error))
        self.assertIn("nesting exceeds 5 levels", str(error))

    def test_output_schema_inline_enum_requires_values_points_at_type_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field status: "Status"
                        type: enum

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E227")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        type: enum") + 1,
        )
        self.assertIn("missing `values:`", str(error))

    def test_output_schema_values_requires_type_enum_points_at_values_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field status: "Status"
                        type: string
                        values:
                            ok
                            blocked

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E228")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        values:") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("        type: string") + 1,
        )
        self.assertIn("`values:` requires `type: enum`", str(error))

    def test_output_schema_mixed_inline_enum_forms_point_at_legacy_enum_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field status: "Status"
                        type: enum
                        enum:
                            ok
                            blocked

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E229")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        enum:") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("        type: enum") + 1,
        )
        self.assertIn("cannot be mixed", str(error))

    def test_output_schema_legacy_enum_requires_string_points_at_enum_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field status: "Status"
                        type: integer
                        enum:
                            1
                            2

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E229")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        enum:") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("        type: integer") + 1,
        )
        self.assertIn("requires `type: string`", str(error))

    def test_output_schema_required_points_at_required_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field status: "Status"
                        type: string
                        required

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E236")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        required") + 1,
        )
        self.assertIn("Delete `required`", str(error))

    def test_output_schema_optional_points_at_optional_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field status: "Status"
                        type: string
                        optional

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E237")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        optional") + 1,
        )
        self.assertIn("Use `nullable`", str(error))

    def test_output_schema_inherit_without_parent_points_at_inherit_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    inherit status

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    inherit status") + 1,
        )
        self.assertIn("inherit requires an inherited output schema", str(error))

    def test_missing_inherited_output_schema_entry_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema BaseRepoStatusSchema: "Base Repo Status Schema"
                    field status: "Status"
                        type: string

                    field summary: "Summary"
                        type: string

                output schema RepoStatusSchema[BaseRepoStatusSchema]: "Repo Status Schema"
                    inherit status

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E003")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index(
                'output schema RepoStatusSchema[BaseRepoStatusSchema]: "Repo Status Schema"'
            )
            + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    field summary: "Summary"') + 1,
        )
        self.assertIn("Missing inherited output schema entry", str(error))

    def test_duplicate_output_schema_setting_reports_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field status: "Status"
                        type: string
                        type: integer

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        type: integer") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("        type: string") + 1,
        )
        self.assertIn("Duplicate output schema setting", str(error))

    def test_unknown_output_schema_ref_points_at_ref_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output schema RepoStatusSchema: "Repo Status Schema"
                    field status: "Status"
                        ref: MissingStatusSchema

                output shape RepoStatusJson: "Repo Status JSON"
                    kind: JsonObject
                    schema: RepoStatusSchema

                output RepoStatusFinalResponse: "Repo Status Final Response"
                    target: TurnResponse
                    shape: RepoStatusJson
                    requirement: Required

                agent RepoStatusAgent:
                    role: "Report repo status in structured form."
                    workflow: "Summarize"
                        "Summarize the repo state and end with the declared final output."
                    outputs: "Outputs"
                        RepoStatusFinalResponse
                    final_output: RepoStatusFinalResponse
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("RepoStatusAgent")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        ref: MissingStatusSchema") + 1,
        )
        self.assertIn("Unknown output schema ref", str(error))

    def test_missing_inherited_output_entry_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BaseHandoff: "Base Handoff"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    must_include: "Must Include"
                        what_changed: "What Changed"
                            "Say what changed."

                output LessonsLeadOutput[BaseHandoff]: "Lessons Lead Output"
                    inherit target
                    inherit shape
                    inherit requirement

                agent Demo:
                    role: "Fail loud when the child skips an inherited output entry."
                    outputs: "Outputs"
                        LessonsLeadOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E003")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index(
                'output LessonsLeadOutput[BaseHandoff]: "Lessons Lead Output"'
            )
            + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    must_include: "Must Include"') + 1,
        )
        self.assertIn("Missing inherited output entry in LessonsLeadOutput: must_include", str(error))
        self.assertIn("Related:", str(error))

    def test_output_patch_without_parent_points_at_inherit_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output LessonsLeadOutput: "Lessons Lead Output"
                    inherit target
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                agent Demo:
                    role: "Fail loud when output patch syntax appears without a parent."
                    outputs: "Outputs"
                        LessonsLeadOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E252")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    inherit target") + 1,
        )
        self.assertIn("requires an inherited output", str(error))

    def test_duplicate_output_item_key_reports_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BaseHandoff: "Base Handoff"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    standalone_read: "Standalone Read"
                        "Keep the note standalone."

                output LessonsLeadOutput[BaseHandoff]: "Lessons Lead Output"
                    inherit target
                    inherit shape
                    inherit requirement
                    inherit standalone_read
                    override standalone_read: "Standalone Read"
                        "Re-state the note for the local child."

                agent Demo:
                    role: "Reject duplicate inherited output item accounting."
                    outputs: "Outputs"
                        LessonsLeadOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E255")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    override standalone_read: "Standalone Read"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("    inherit standalone_read") + 1,
        )
        self.assertIn("repeats output item key `standalone_read`", str(error))
        self.assertIn("first `standalone_read` entry", str(error))

    def test_output_override_kind_mismatch_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BaseHandoff: "Base Handoff"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    must_include: "Must Include"
                        what_changed: "What Changed"
                            "Say what changed."

                output LessonsLeadOutput[BaseHandoff]: "Lessons Lead Output"
                    inherit target
                    inherit shape
                    inherit requirement
                    override must_include: TurnResponse

                agent Demo:
                    role: "Fail loud when output override kind does not match the parent."
                    outputs: "Outputs"
                        LessonsLeadOutput
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E255")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    override must_include: TurnResponse") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    must_include: "Must Include"') + 1,
        )
        self.assertIn("overrides entry `must_include` with the wrong kind", str(error))
        self.assertIn("Related:", str(error))

    def test_cyclic_output_inheritance_points_at_output_decl_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output FirstReply[SecondReply]: "First Reply"
                    inherit target
                    inherit shape
                    inherit requirement

                output SecondReply[FirstReply]: "Second Reply"
                    inherit target
                    inherit shape
                    inherit requirement

                agent Demo:
                    role: "Reject cyclic output inheritance."
                    outputs: "Outputs"
                        FirstReply
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E251")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('output FirstReply[SecondReply]: "First Reply"') + 1,
        )
        self.assertIn("Output inheritance cycle: FirstReply -> SecondReply -> FirstReply.", str(error))

    def test_inherited_render_profile_entry_points_at_inherit_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BaseReply: "Base Reply"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                output ChildReply[BaseReply]: "Child Reply"
                    inherit target
                    inherit shape
                    inherit requirement
                    inherit render_profile

                agent Demo:
                    role: "Keep inherited output attachments explicit."
                    outputs: "Outputs"
                        ChildReply
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E253")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    inherit render_profile") + 1,
        )
        self.assertIn("cannot inherit undefined key `render_profile`", str(error))

    def test_output_render_profile_requires_one_markdown_artifact_points_at_render_profile_line(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                render_profile CompactComment:
                    properties -> sentence

                output FileBundle: "File Bundle"
                    files: "Files"
                        release_notes: "Release Notes"
                            path: "artifacts/RELEASE_NOTES.md"
                            shape: MarkdownDocument
                            requirement: Required
                    render_profile: CompactComment

                agent Demo:
                    role: "Reject render profiles on file bundles."
                    outputs: "Outputs"
                        FileBundle
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    render_profile: CompactComment") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    files: "Files"') + 1,
        )
        self.assertIn("Output render_profile requires one markdown-bearing output artifact", str(error))

    def test_duplicate_workflow_item_key_reports_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                workflow DuplicateWorkflow: "Duplicate Workflow"
                    step_one: "Step One"
                        "Say hello."
                    step_one: "Step One Again"
                        "Say world."

                agent Demo:
                    role: "Reject duplicate workflow section keys."
                    workflow: DuplicateWorkflow
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E261")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    step_one: "Step One Again"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    step_one: "Step One"') + 1,
        )
        self.assertIn("repeats key `step_one`", str(error))
        self.assertIn("first `step_one` entry", str(error))

    def test_cyclic_workflow_composition_points_at_workflow_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                workflow FirstWorkflow: "First Workflow"
                    use second: SecondWorkflow

                workflow SecondWorkflow: "Second Workflow"
                    use first: FirstWorkflow

                agent Demo:
                    role: "Reject cyclic workflow composition."
                    workflow: FirstWorkflow
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E283")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('workflow SecondWorkflow: "Second Workflow"') + 1,
        )
        self.assertIn("Workflow composition cycle", str(error))

    def test_workflow_patch_without_parent_points_at_inherit_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                workflow ChildWorkflow: "Child Workflow"
                    inherit greeting

                agent Demo:
                    role: "Fail loud when workflow patch syntax appears without a parent."
                    workflow: ChildWorkflow
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E243")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    inherit greeting") + 1,
        )
        self.assertIn("requires an inherited workflow", str(error))

    def test_missing_inherited_workflow_entry_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                workflow BaseWorkflow: "Base Workflow"
                    greeting: "Greeting"
                        "Say hello."
                    closing: "Closing"
                        "Say goodbye."

                workflow ChildWorkflow[BaseWorkflow]: "Child Workflow"
                    inherit greeting

                agent Demo:
                    role: "Keep inherited workflows explicit."
                    workflow: ChildWorkflow
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E003")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('workflow ChildWorkflow[BaseWorkflow]: "Child Workflow"')
            + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    closing: "Closing"') + 1,
        )
        self.assertIn("Missing inherited workflow entry in ChildWorkflow: closing", str(error))
        self.assertIn("Related:", str(error))

    def test_workflow_override_kind_mismatch_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                workflow HelperWorkflow: "Helper Workflow"
                    helper_step: "Helper Step"
                        "Do helper work."

                workflow BaseWorkflow: "Base Workflow"
                    shared_step: "Shared Step"
                        "Do the base work."

                workflow ChildWorkflow[BaseWorkflow]: "Child Workflow"
                    override shared_step: HelperWorkflow

                agent Demo:
                    role: "Reject workflow override kind mismatches."
                    workflow: ChildWorkflow
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E242")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    override shared_step: HelperWorkflow") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    shared_step: "Shared Step"') + 1,
        )
        self.assertIn("overrides `shared_step` with the wrong kind", str(error))
        self.assertIn("Related:", str(error))

    def test_duplicate_inherited_law_subsection_reports_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                workflow BaseWorkflow: "Base Workflow"
                    law:
                        currentness:
                            current none

                workflow ChildWorkflow[BaseWorkflow]: "Child Workflow"
                    law:
                        inherit currentness
                        inherit currentness

                agent Demo:
                    role: "Reject duplicate inherited law subsections."
                    workflow: ChildWorkflow
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E382")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        inherit_lines = [
            line_number
            for line_number, line in enumerate(rendered.splitlines(), start=1)
            if line == "        inherit currentness"
        ]
        self.assertEqual(error.diagnostic.location.line, inherit_lines[1])
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(error.diagnostic.related[0].location.line, inherit_lines[0])
        self.assertIn("accounts for subsection `currentness` more than once", str(error))
        self.assertIn("first `currentness` subsection", str(error))

    def test_missing_inherited_law_subsection_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                workflow BaseWorkflow: "Base Workflow"
                    law:
                        currentness:
                            current none
                        stop_lines:
                            stop "Stop here."

                workflow ChildWorkflow[BaseWorkflow]: "Child Workflow"
                    law:
                        inherit stop_lines

                agent Demo:
                    role: "Keep inherited law sections explicit."
                    workflow: ChildWorkflow
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E383")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        inherit_line = rendered.splitlines().index("        inherit stop_lines") + 1
        self.assertEqual(
            error.diagnostic.location.line,
            inherit_line,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("        currentness:") + 1,
        )
        self.assertIn("omits parent subsection(s) `currentness`", str(error))
        self.assertIn("Related:", str(error))

    def test_duplicate_properties_entry_reports_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output ReviewComment: "Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    properties summary: "Summary"
                        verdict: "Verdict"
                            "Use changes requested when the contract fails."

                        verdict: "Verdict Again"
                            "This should fail."

                agent Demo:
                    role: "Compile the broken review comment."
                    workflow: "Review"
                        "This should fail."
                    outputs: "Outputs"
                        ReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E295")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        verdict: "Verdict Again"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('        verdict: "Verdict"') + 1,
        )
        self.assertIn("properties entry key `verdict`", str(error))
        self.assertIn("first `verdict` properties entry", str(error))

    def test_readable_guard_disallowed_source_points_at_guard_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenComment: "Broken Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    callout scope: "Scope" when BrokenComment.summary_present
                        kind: note
                        "This should fail."

                agent Demo:
                    role: "Compile the broken comment."
                    workflow: "Warn"
                        "This should fail."
                    outputs: "Outputs"
                        BrokenComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E296")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index(
                '    callout scope: "Scope" when BrokenComment.summary_present'
            )
            + 1,
        )
        self.assertIn("Readable guard reads disallowed source", str(error))
        self.assertIn("BrokenComment.summary_present", str(error))

    def test_guard_shell_without_when_reports_guard_line_for_agent_compile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenComment: "Broken Comment"
                    target: TurnResponse
                    shape: Comment

                    guard follow_up when true
                        properties:
                            escalation: "Escalation"
                                "This should fail."

                agent Demo:
                    role: "Compile the broken guard shell."
                    workflow: "Review"
                        "This should fail."
                    outputs: "Outputs"
                        BrokenComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)
            output_decl = next(
                decl for decl in prompt.declarations if isinstance(decl, model.OutputDecl)
            )
            guard_block = next(
                item
                for item in output_decl.items
                if isinstance(item, model.ReadableBlock) and item.kind == "guard"
            )
            mutated_output = replace(
                output_decl,
                items=tuple(
                    replace(item, when_expr=None) if item is guard_block else item
                    for item in output_decl.items
                ),
            )
            mutated_prompt = replace(
                prompt,
                declarations=tuple(
                    mutated_output if decl is output_decl else decl for decl in prompt.declarations
                ),
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(mutated_prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E297")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    guard follow_up when true") + 1,
        )
        self.assertIn("Readable guard shell `output BrokenComment.follow_up`", str(error))
        self.assertIn("must define a guard expression", str(error))

    def test_output_guard_disallowed_source_points_at_guard_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenComment: "Broken Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    summary: "Summary"
                    rewrite_note: "Rewrite Note" when BrokenComment.summary

                agent Demo:
                    role: "Keep output guards on allowed sources."
                    workflow: "Reply"
                        "This should fail."
                    outputs: "Outputs"
                        BrokenComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E338")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index(
                '    rewrite_note: "Rewrite Note" when BrokenComment.summary'
            )
            + 1,
        )
        self.assertIn("Output guard reads disallowed source", str(error))
        self.assertIn("BrokenComment.summary", str(error))

    def test_standalone_read_guarded_detail_points_at_standalone_read_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input RouteFacts: "Route Facts"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                output BrokenComment: "Broken Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    rewrite_note: "Rewrite Note" when RouteFacts.should_rewrite
                    standalone_read: "Standalone Read"
                        "{{BrokenComment:rewrite_note}}"

                agent Demo:
                    role: "Keep standalone read at the branch level."
                    workflow: "Reply"
                        "This should fail."
                    inputs: "Inputs"
                        RouteFacts
                    outputs: "Outputs"
                        BrokenComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E340")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    standalone_read: "Standalone Read"') + 1,
        )
        self.assertIn("Standalone read references guarded output detail", str(error))
        self.assertIn("rewrite_note", str(error))

    def test_unknown_callout_kind_points_at_kind_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output BrokenComment: "Broken Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    callout warning_box: "Warning Box"
                        kind: urgent
                        "This should fail."

                agent Demo:
                    role: "Compile the broken comment."
                    workflow: "Warn"
                        "This should fail."
                    outputs: "Outputs"
                        BrokenComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E297")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        kind: urgent") + 1,
        )
        self.assertIn("unknown callout kind `urgent`", str(error))
        self.assertIn("shipped callout kinds", str(error))

    def test_document_table_without_columns_points_at_table_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                document BrokenGuide: "Broken Guide"
                    table release_gates: "Release Gates"
                        notes:
                            "This should fail."

                output BrokenGuideFile: "Broken Guide File"
                    target: File
                        path: "release_root/BROKEN_GUIDE.md"
                    shape: MarkdownDocument
                    structure: BrokenGuide
                    requirement: Required

                agent Demo:
                    role: "Compile the broken guide."
                    workflow: "Draft"
                        "This should fail."
                    outputs: "Outputs"
                        BrokenGuideFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E297")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    table release_gates: "Release Gates"') + 1,
        )
        self.assertIn("must declare at least one column", str(error))

    def test_duplicate_document_block_key_reports_related_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                document BrokenGuide: "Broken Guide"
                    section summary: "Summary"
                        "Start with the current goal."

                    section summary: "Summary Again"
                        "This should fail."

                output BrokenGuideFile: "Broken Guide File"
                    target: File
                        path: "release_root/BROKEN_GUIDE.md"
                    shape: MarkdownDocument
                    structure: BrokenGuide
                    requirement: Required

                agent Demo:
                    role: "Compile the broken guide."
                    workflow: "Draft"
                        "This should fail."
                    outputs: "Outputs"
                        BrokenGuideFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E295")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    section summary: "Summary Again"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    section summary: "Summary"') + 1,
        )
        self.assertIn("document block key `summary`", str(error))
        self.assertIn("first `summary` document block", str(error))

    def test_guard_shell_without_when_reports_guard_line_for_declaration_compile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                document BrokenGuide: "Broken Guide"
                    guard follow_up when true
                        section escalation: "Escalation"
                            "This should fail."
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)
            document_decl = next(
                decl for decl in prompt.declarations if isinstance(decl, model.DocumentDecl)
            )
            guard_block = next(
                item
                for item in document_decl.body.items
                if isinstance(item, model.ReadableBlock) and item.kind == "guard"
            )
            mutated_document = replace(
                document_decl,
                body=replace(
                    document_decl.body,
                    items=tuple(
                        replace(item, when_expr=None) if item is guard_block else item
                        for item in document_decl.body.items
                    ),
                ),
            )
            mutated_prompt = replace(
                prompt,
                declarations=tuple(
                    mutated_document if decl is document_decl else decl
                    for decl in prompt.declarations
                ),
            )
            session = CompilationSession(mutated_prompt)

            with self.assertRaises(CompileError) as ctx:
                session.compile_readable_declaration("document", "BrokenGuide")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E297")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    guard follow_up when true") + 1,
        )
        self.assertIn("Readable guard shell `follow_up`", str(error))
        self.assertIn("must define a guard expression", str(error))

    def test_workflow_readable_sequence_invalid_item_points_at_block_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                workflow RootReadableGuide: "Guide"
                    sequence read_first:
                        "Read the current issue first."

                agent Demo:
                    role: "Keep workflow readable blocks well formed."
                    workflow: RootReadableGuide
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)
            workflow_decl = next(
                decl for decl in prompt.declarations if isinstance(decl, model.WorkflowDecl)
            )
            sequence_block = next(
                item
                for item in workflow_decl.body.items
                if isinstance(item, model.ReadableBlock) and item.key == "read_first"
            )
            mutated_workflow = replace(
                workflow_decl,
                body=replace(
                    workflow_decl.body,
                    items=tuple(
                        replace(item, payload=("This should fail.",))
                        if item is sequence_block
                        else item
                        for item in workflow_decl.body.items
                    ),
                ),
            )
            mutated_prompt = replace(
                prompt,
                declarations=tuple(
                    mutated_workflow if decl is workflow_decl else decl
                    for decl in prompt.declarations
                ),
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(mutated_prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E297")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    sequence read_first:") + 1,
        )
        self.assertIn("Readable sequence items must stay list entries", str(error))
        self.assertIn("agent Demo workflow.read_first", str(error))

    def test_workflow_readable_image_payload_shape_points_at_block_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                workflow RootReadableGuide: "Guide"
                    image evidence: "Evidence"
                        src: "https://example.com/release.png"
                        alt: "Release checklist screenshot"

                agent Demo:
                    role: "Keep workflow image blocks well formed."
                    workflow: RootReadableGuide
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)
            workflow_decl = next(
                decl for decl in prompt.declarations if isinstance(decl, model.WorkflowDecl)
            )
            image_block = next(
                item
                for item in workflow_decl.body.items
                if isinstance(item, model.ReadableBlock) and item.key == "evidence"
            )
            mutated_workflow = replace(
                workflow_decl,
                body=replace(
                    workflow_decl.body,
                    items=tuple(
                        replace(item, payload=("This should fail.",))
                        if item is image_block
                        else item
                        for item in workflow_decl.body.items
                    ),
                ),
            )
            mutated_prompt = replace(
                prompt,
                declarations=tuple(
                    mutated_workflow if decl is workflow_decl else decl
                    for decl in prompt.declarations
                ),
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(mutated_prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E297")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    image evidence: "Evidence"') + 1,
        )
        self.assertIn("Readable image payload must stay image-shaped", str(error))
        self.assertIn("agent Demo workflow.evidence", str(error))

    def test_workflow_unknown_readable_block_kind_reports_internal_error_with_block_line(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                workflow RootReadableGuide: "Guide"
                    sequence read_first:
                        "Read the current issue first."

                agent Demo:
                    role: "Expose impossible readable kinds as compiler bugs."
                    workflow: RootReadableGuide
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)
            workflow_decl = next(
                decl for decl in prompt.declarations if isinstance(decl, model.WorkflowDecl)
            )
            sequence_block = next(
                item
                for item in workflow_decl.body.items
                if isinstance(item, model.ReadableBlock) and item.key == "read_first"
            )
            mutated_workflow = replace(
                workflow_decl,
                body=replace(
                    workflow_decl.body,
                    items=tuple(
                        replace(item, kind="mystery")
                        if item is sequence_block
                        else item
                        for item in workflow_decl.body.items
                    ),
                ),
            )
            mutated_prompt = replace(
                prompt,
                declarations=tuple(
                    mutated_workflow if decl is workflow_decl else decl
                    for decl in prompt.declarations
                ),
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(mutated_prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E901")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    sequence read_first:") + 1,
        )
        self.assertIn("unsupported readable block kind", str(error))
        self.assertIn("agent Demo workflow.read_first", str(error))

    def test_document_override_without_parent_points_at_override_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                document BrokenGuide: "Broken Guide"
                    override section summary: "Summary"
                        "This should fail."

                output BrokenGuideFile: "Broken Guide File"
                    target: File
                        path: "release_root/BROKEN_GUIDE.md"
                    shape: MarkdownDocument
                    structure: BrokenGuide
                    requirement: Required

                agent Demo:
                    role: "Compile the broken guide."
                    workflow: "Draft"
                        "This should fail."
                    outputs: "Outputs"
                        BrokenGuideFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E305")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    override section summary: "Summary"') + 1,
        )
        self.assertIn("requires an inherited document declaration", str(error))

    def test_document_override_kind_mismatch_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                document LessonPlan: "Lesson Plan"
                    sequence read_order: "Read Order"
                        first: "Read the brief."

                document BrokenLessonPlan[LessonPlan]: "Broken Lesson Plan"
                    override definitions read_order: "Read Order"
                        first: "Read the brief."

                output BrokenLessonPlanFile: "Broken Lesson Plan File"
                    target: File
                        path: "lesson_root/BROKEN_LESSON_PLAN.md"
                    shape: MarkdownDocument
                    structure: BrokenLessonPlan
                    requirement: Required

                agent Demo:
                    role: "Compile the broken lesson plan."
                    workflow: "Adapt"
                        "This should fail."
                    outputs: "Outputs"
                        BrokenLessonPlanFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E305")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    override definitions read_order: "Read Order"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    sequence read_order: "Read Order"') + 1,
        )
        self.assertIn("overrides entry `read_order` with the wrong block kind", str(error))
        self.assertIn("inherited `read_order` entry", str(error))

    def test_missing_inherited_document_entry_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                document BaseGuide: "Base Guide"
                    section summary: "Summary"
                        "Lead with the current goal."

                    sequence read_order: "Read Order"
                        first: "Read the brief."

                document ChildGuide[BaseGuide]: "Child Guide"
                    inherit summary

                output ChildGuideFile: "Child Guide File"
                    target: File
                        path: "guide_root/CHILD_GUIDE.md"
                    shape: MarkdownDocument
                    structure: ChildGuide
                    requirement: Required

                agent Demo:
                    role: "Compile the incomplete child guide."
                    workflow: "Draft"
                        "This should fail."
                    outputs: "Outputs"
                        ChildGuideFile
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E003")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('document ChildGuide[BaseGuide]: "Child Guide"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    sequence read_order: "Read Order"') + 1,
        )
        self.assertIn("Missing inherited document entry in ChildGuide: read_order", str(error))
        self.assertIn("inherited `read_order` entry", str(error))

    def test_skill_package_case_collision_uses_file_scoped_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            prompts.mkdir(parents=True)
            prompt_path = prompts / "SKILL.prompt"
            prompt_path.write_text(
                textwrap.dedent(
                    """\
                    skill package PathCasePreservation: "Path Case Preservation"
                        metadata:
                            name: "path-case-preservation"
                        "Keep companion paths stable."
                    """
                ),
                encoding="utf-8",
            )
            collision_path = prompts / "skill.md"
            collision_path.write_text(
                "This file case-collides with the compiled `SKILL.md` output.\n",
                encoding="utf-8",
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_skill_package()

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E304")
        self.assertEqual(error.diagnostic.location.path, collision_path.resolve())
        self.assertIsNone(error.diagnostic.location.line)
        self.assertIn("case-collides", str(error))

    def test_skill_package_agent_output_collision_reports_related_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            (prompts / "agents").mkdir(parents=True)
            prompt_path = prompts / "SKILL.prompt"
            prompt_path.write_text(
                textwrap.dedent(
                    """\
                    skill package AgentOutputCollision: "Agent Output Collision"
                        metadata:
                            name: "agent-output-collision"
                        "Fail loud when bundled files shadow compiled agent output."
                    """
                ),
                encoding="utf-8",
            )
            bundled_prompt_path = prompts / "agents" / "reviewer.prompt"
            bundled_prompt_path.write_text(
                textwrap.dedent(
                    """\
                    agent Reviewer:
                        role: "Review the bundle."
                    """
                ),
                encoding="utf-8",
            )
            collision_path = prompts / "agents" / "reviewer.md"
            collision_path.write_text(
                "This file collides with the compiled bundled agent markdown.\n",
                encoding="utf-8",
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_skill_package()

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E304")
        self.assertEqual(error.diagnostic.location.path, collision_path.resolve())
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.path,
            bundled_prompt_path.resolve(),
        )
        self.assertIn("Duplicate skill package bundled path", str(error))
        self.assertIn("Related:", str(error))

    def test_skill_package_emit_path_must_end_in_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            prompt_path = self._write_prompt(
                root,
                """\
                document ChecklistGuide: "Checklist Guide"
                    section summary: "Summary"
                        "Use the checklist."

                skill package InvalidEmitPath: "Invalid Emit Path"
                    emit:
                        "references/checklist.txt": ChecklistGuide
                    "Keep the root file short."
                """,
                rel_path="prompts/SKILL.prompt",
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_skill_package()

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E304")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 7)
        self.assertIn("must end in `.md`", str(error))

    def test_skill_package_emit_path_must_stay_under_package_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompt_path = self._write_prompt(
                root,
                """\
                document ChecklistGuide: "Checklist Guide"
                    section summary: "Summary"
                        "Use the checklist."

                skill package InvalidEmitPath: "Invalid Emit Path"
                    emit:
                        "../references/checklist.md": ChecklistGuide
                    "Keep the root file short."
                """,
                rel_path="prompts/SKILL.prompt",
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_skill_package()

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E304")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 7)
        self.assertIn("must stay within the package root", str(error))

    def test_skill_package_emit_ref_must_point_at_document(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompt_path = self._write_prompt(
                root,
                """\
                skill NotADocument: "Not A Document"
                    purpose: "Do not use this as a document."

                skill package WrongKindEmit: "Wrong Kind Emit"
                    emit:
                        "references/checklist.md": NotADocument
                    "Keep the root file short."
                """,
                rel_path="prompts/SKILL.prompt",
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_skill_package()

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E304")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, 6)
        self.assertIn("must point at document declarations", str(error))
        self.assertIn("skill declaration", str(error))

    def test_skill_package_emit_collision_with_raw_file_reports_related_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            (prompts / "references").mkdir(parents=True)
            prompt_path = self._write_prompt(
                root,
                """\
                document ChecklistGuide: "Checklist Guide"
                    section summary: "Summary"
                        "Use the checklist."

                skill package EmitCollision: "Emit Collision"
                    emit:
                        "references/checklist.md": ChecklistGuide
                    "Keep the root file short."
                """,
                rel_path="prompts/SKILL.prompt",
            )
            collision_path = prompts / "references" / "checklist.md"
            collision_path.write_text("This bundled file collides with emitted markdown.\n")
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_skill_package()

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E304")
        self.assertEqual(error.diagnostic.location.path, collision_path.resolve())
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.path,
            prompt_path.resolve(),
        )
        self.assertIn("Duplicate skill package bundled path", str(error))

    def test_skill_package_emit_collision_with_agent_output_reports_related_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            prompts = root / "prompts"
            (prompts / "agents").mkdir(parents=True)
            prompt_path = self._write_prompt(
                root,
                """\
                document ReviewerGuide: "Reviewer Guide"
                    section summary: "Summary"
                        "Guide the reviewer."

                skill package EmitCollision: "Emit Collision"
                    emit:
                        "agents/reviewer.md": ReviewerGuide
                    "Keep the root file short."
                """,
                rel_path="prompts/SKILL.prompt",
            )
            bundled_prompt_path = prompts / "agents" / "reviewer.prompt"
            bundled_prompt_path.write_text(
                textwrap.dedent(
                    """\
                    agent Reviewer:
                        role: "Review the bundle."
                    """
                ),
                encoding="utf-8",
            )
            prompt = parse_file(prompt_path)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(prompt).compile_skill_package()

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E304")
        self.assertEqual(error.diagnostic.location.path, bundled_prompt_path.resolve())
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.path,
            prompt_path.resolve(),
        )
        self.assertIn("Duplicate skill package bundled path", str(error))

    def test_workflow_and_review_conflict_points_at_review_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                agent Demo:
                    role: "Keep workflow and review separate."
                    workflow: "Reply"
                        "Reply directly."
                    review: MissingReview
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E480")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    review: MissingReview") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    workflow: "Reply"') + 1,
        )
        self.assertIn("may not define both `workflow:` and `review:`", str(error))

    def test_agent_slot_law_outside_workflow_points_at_law_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                agent Demo:
                    role: "Keep custom slots readable."
                    notes: "Notes"
                        "Leave this slot as prose only."

                        law:
                            current none
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E345")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    notes: "Notes"') + 1,
        )
        self.assertIn("`law:` is not allowed on authored slot `notes`", str(error))

    def test_legacy_role_workflow_order_points_at_role_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                agent Demo:
                    workflow: "Reply"
                        "This should fail."
                    role: "This role arrives too late."
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E206")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    role: "This role arrives too late."') + 1,
        )
        self.assertIn("Unsupported agent field order", str(error))
        self.assertIn("Expected `role` followed by `workflow`", str(error))

    def test_reserved_authored_slot_key_points_at_slot_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                agent Demo:
                    role: "Reject reserved authored slot keys."
                    abstract outputs
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    abstract outputs") + 1,
        )
        self.assertIn(
            "Reserved typed agent field cannot be used as authored slot in Demo: outputs",
            str(error),
        )

    def test_cyclic_agent_inheritance_points_at_agent_decl_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                agent First[Second]:
                    role: "Keep agent inheritance acyclic."

                agent Second[First]:
                    role: "Reject cycles in authored slot inheritance."
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("First")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E207")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("agent First[Second]:") + 1,
        )
        self.assertIn("Cyclic agent inheritance: First -> Second -> First", str(error))

    def test_duplicate_authored_slot_key_reports_related_first_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                agent Demo:
                    role: "Keep authored slot keys unique."
                    notes: "Notes"
                        "Keep the shared notes compact."
                    notes: "Duplicate Notes"
                        "This second slot should fail."
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    notes: "Duplicate Notes"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    notes: "Notes"') + 1,
        )
        self.assertIn("Duplicate authored slot key in agent Demo: notes", str(error))
        self.assertIn("Related:", str(error))

    def test_inherited_authored_slot_requires_patch_keyword_reports_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                agent Base:
                    role: "Share a reusable authored slot."
                    notes: "Base Notes"
                        "Keep the base notes stable."

                agent Demo[Base]:
                    role: "Use explicit inherit or override for shared slots."
                    notes: "Child Notes"
                        "This direct replacement should fail."
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    notes: "Child Notes"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    notes: "Base Notes"') + 1,
        )
        self.assertIn("Inherited authored slot requires `inherit notes` or `override notes`", str(error))

    def test_abstract_authored_slot_inherit_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                abstract agent Base:
                    role: "Require a child to define notes directly."
                    abstract notes

                agent Demo[Base]:
                    role: "Define inherited abstract slots directly."
                    inherit notes
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E210")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    inherit notes") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("    abstract notes") + 1,
        )
        self.assertIn("must be defined directly in agent Demo: notes", str(error))

    def test_undefined_override_authored_slot_points_at_override_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                agent Base:
                    role: "Keep the parent authored slots narrow."
                    notes: "Base Notes"
                        "Keep only one shared slot."

                agent Demo[Base]:
                    role: "Override only real inherited slots."
                    override checklist: "Checklist"
                        "This key does not exist on the parent."
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E001")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    override checklist: "Checklist"') + 1,
        )
        self.assertIn("Cannot override undefined authored slot in agent Base: checklist", str(error))

    def test_missing_inherited_authored_slot_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                agent Base:
                    role: "Share two concrete authored slots."
                    notes: "Base Notes"
                        "Keep the base notes stable."
                    checklist: "Checklist"
                        "Keep the base checklist stable."

                agent Demo[Base]:
                    role: "Account for every inherited concrete slot."
                    inherit notes
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E003")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("agent Demo[Base]:") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    checklist: "Checklist"') + 1,
        )
        self.assertIn("Missing inherited authored slot in agent Demo: checklist", str(error))

    def test_route_only_missing_current_none_points_at_decl_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input RouteFacts: "Route Facts"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                output HandoffComment: "Handoff Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                agent RoutingOwner:
                    role: "Own the rerouted turn."

                route_only RouteOnlyRepair: "Route Only Repair"
                    facts: RouteFacts
                    handoff_output: HandoffComment
                    routes:
                        else -> RoutingOwner

                agent Demo:
                    role: "Require explicit route-only currentness."
                    workflow: RouteOnlyRepair
                    inputs: "Inputs"
                        RouteFacts
                    outputs: "Outputs"
                        HandoffComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('route_only RouteOnlyRepair: "Route Only Repair"') + 1,
        )
        self.assertIn("route_only must declare `current none`: RouteOnlyRepair", str(error))

    def test_route_only_guard_mismatch_reports_related_output_guard_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input RouteFacts: "Route Facts"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                output RouteRepairComment: "Route Repair Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    rewrite_mode: "Rewrite Mode" when RouteFacts.section_status == "full_rewrite"

                agent RoutingOwner:
                    role: "Handle the local reroute."
                    workflow: "Route"
                        "Keep ownership local."

                route_only RouteRepair: "Route Repair"
                    facts: RouteFacts
                    current none
                    handoff_output: RouteRepairComment
                    guarded:
                        rewrite_mode when section_status == "new"
                    routes:
                        else -> RoutingOwner

                agent Demo:
                    role: "Compile the mismatched route-only guard."
                    workflow: RouteRepair
                    inputs: "Inputs"
                        RouteFacts
                    outputs: "Outputs"
                        RouteRepairComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        rewrite_mode when section_status == "new"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index(
                '    rewrite_mode: "Rewrite Mode" when RouteFacts.section_status == "full_rewrite"'
            )
            + 1,
        )
        self.assertIn("route_only guarded output item does not match output guard", str(error))
        self.assertIn("`rewrite_mode` output guard", str(error))

    def test_route_only_facts_ambiguity_reports_input_and_output_lines(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input RouteFacts: "Route Facts"
                    source: Prompt
                    shape: JsonObject
                    requirement: Required

                output RouteFacts: "Route Facts Output"
                    target: File
                        path: "unit_root/route_facts.json"
                    shape: JsonObject
                    requirement: Required

                output HandoffComment: "Handoff Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                agent RoutingOwner:
                    role: "Own the rerouted turn."

                route_only RouteOnlyRepair: "Route Only Repair"
                    facts: RouteFacts
                    current none
                    handoff_output: HandoffComment
                    routes:
                        else -> RoutingOwner

                agent Demo:
                    role: "Reject ambiguous route-only facts refs."
                    workflow: RouteOnlyRepair
                    inputs: "Inputs"
                        RouteFacts
                    outputs: "Outputs"
                        HandoffComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E270")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    facts: RouteFacts") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 2)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('input RouteFacts: "Route Facts"') + 1,
        )
        self.assertEqual(
            error.diagnostic.related[1].location.line,
            rendered.splitlines().index('output RouteFacts: "Route Facts Output"') + 1,
        )
        self.assertIn("Ambiguous route_only facts in agent Demo slot workflow: RouteFacts", str(error))

    def test_route_only_facts_wrong_kind_points_at_facts_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                workflow RouteFacts: "Route Facts"
                    "This wrong-kind declaration should fail."

                output HandoffComment: "Handoff Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                agent RoutingOwner:
                    role: "Own the rerouted turn."

                route_only RouteOnlyRepair: "Route Only Repair"
                    facts: RouteFacts
                    current none
                    handoff_output: HandoffComment
                    routes:
                        else -> RoutingOwner

                agent Demo:
                    role: "Keep route-only facts on inputs or outputs."
                    workflow: RouteOnlyRepair
                    outputs: "Outputs"
                        HandoffComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    facts: RouteFacts") + 1,
        )
        self.assertIn(
            "route_only facts must resolve to an input or output declaration",
            str(error),
        )

    def test_grounding_missing_target_points_at_decl_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                grounding GroundingGuide: "Grounding Guide"
                    policy:
                        allow repo_search

                agent Demo:
                    role: "Require grounding workflows to name a target."
                    workflow: GroundingGuide
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('grounding GroundingGuide: "Grounding Guide"') + 1,
        )
        self.assertIn("grounding is missing target: GroundingGuide", str(error))

    def test_abstract_review_on_concrete_agent_points_at_review_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output ReviewComment: "Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                abstract review BaseDraftReview: "Base Draft Review"
                    comment_output: ReviewComment

                agent Demo:
                    role: "Keep abstract reviews off concrete agents."
                    review: BaseDraftReview
                    outputs: "Outputs"
                        ReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E494")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    review: BaseDraftReview") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('abstract review BaseDraftReview: "Base Draft Review"')
            + 1,
        )
        self.assertIn("Concrete agent may not attach abstract review", str(error))

    def test_multiple_route_surfaces_report_related_law_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                agent ReviewLead:
                    role: "Own accepted follow-up."

                agent Demo:
                    role: "Keep one route-bearing surface live."
                    workflow: "Reply"
                        law:
                            active when true
                            stop "Reply directly."
                            route "Hand off to ReviewLead." -> ReviewLead

                    handoff_routing: "Handoff Routing"
                        law:
                            active when true
                            stop "Hand off or finish the turn."
                            route "Hand off to ReviewLead from handoff routing." -> ReviewLead
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E343")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    handoff_routing: "Handoff Routing"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    workflow: "Reply"') + 1,
        )
        self.assertIn("workflow, handoff_routing", str(error))
        self.assertIn("live `workflow` route-bearing surface", str(error))

    def test_review_driven_final_output_route_points_at_final_output_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input DraftPlan: "Draft Plan"
                    source: File
                        path: "unit_root/DRAFT_PLAN.md"
                    shape: MarkdownDocument
                    requirement: Required

                schema PlanReviewContract: "Plan Review Contract"
                    sections:
                        summary: "Summary"
                            "Summarize the reviewed plan."

                    gates:
                        outline_complete: "Outline Complete"
                            "Confirm the reviewed plan includes the outline."

                agent ReviewLead:
                    role: "Own accepted plan follow-up."

                agent PlanAuthor:
                    role: "Repair rejected plans."

                output AcceptanceReviewComment: "Acceptance Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    verdict: "Verdict"
                        "State whether the plan passed review."

                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact."

                    analysis_performed: "Analysis Performed"
                        "Summarize the review analysis."

                    output_contents_that_matter: "Output Contents That Matter"
                        "Summarize what the next owner should read first."

                    next_owner: "Next Owner"
                        "Name {{ReviewLead}} when accepted and {{PlanAuthor}} when rejected."

                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "List exact failing gates."

                output OtherReply: "Other Reply"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                review AcceptanceReview: "Acceptance Review"
                    subject: DraftPlan
                    contract: PlanReviewContract
                    comment_output: AcceptanceReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        failing_gates: failure_detail.failing_gates
                        next_owner: next_owner

                    contract_checks: "Contract Checks"
                        accept "The acceptance review contract passes." when contract.passes

                    on_accept: "If Accepted"
                        current none
                        route "Accepted plan returns to ReviewLead." -> ReviewLead

                    on_reject: "If Rejected"
                        current none
                        route "Rejected plan returns to PlanAuthor." -> PlanAuthor

                agent AcceptanceReviewAgent:
                    role: "Keep review-driven final_output.route out of the first cut."
                    review: AcceptanceReview
                    inputs: "Inputs"
                        DraftPlan
                    outputs: "Outputs"
                        AcceptanceReviewComment
                        OtherReply
                    final_output:
                        output: OtherReply
                        route: next_route
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent(
                    "AcceptanceReviewAgent"
                )

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    final_output:") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("    review: AcceptanceReview") + 1,
        )
        self.assertIn("final_output.route is not supported on review-driven agents in v1", str(error))

    def test_skill_purpose_must_be_string_points_at_purpose_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                skill BrokenSkill: "Broken Skill"
                    purpose: Required

                agent Demo:
                    role: "Compile one skill."
                    skills: "Skills"
                        can_run: "Can Run"
                            skill broken_skill: BrokenSkill
                                requirement: Required
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E220")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    purpose: Required") + 1,
        )
        self.assertIn("Skill is missing string purpose", str(error))

    def test_inherited_inputs_block_needs_keyed_entries_reports_related_parent_ref_line(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input ApprovedPlan: "Approved Plan"
                    source: File
                        path: "unit_root/APPROVED_PLAN.md"
                    shape: MarkdownDocument
                    requirement: Required

                inputs BaseInputs: "Inputs"
                    ApprovedPlan

                inputs ReviewInputs[BaseInputs]: "Inputs"
                    inherit approved_plan

                agent Demo:
                    role: "Keep inherited IO blocks patchable."
                    inputs: ReviewInputs
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E247")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('inputs ReviewInputs[BaseInputs]: "Inputs"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("    ApprovedPlan") + 1,
        )
        self.assertIn("contains unkeyed top-level refs", str(error))

    def test_missing_inherited_inputs_entry_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input ApprovedPlan: "Approved Plan"
                    source: File
                        path: "unit_root/APPROVED_PLAN.md"
                    shape: MarkdownDocument
                    requirement: Required

                input AlternatePlan: "Alternate Plan"
                    source: File
                        path: "unit_root/ALTERNATE_PLAN.md"
                    shape: MarkdownDocument
                    requirement: Required

                inputs BaseInputs: "Inputs"
                    approved_plan: "Approved Plan Binding"
                        ApprovedPlan
                    alternate_plan: "Alternate Plan Binding"
                        AlternatePlan

                inputs ReviewInputs[BaseInputs]: "Inputs"
                    inherit approved_plan

                agent Demo:
                    role: "Keep inherited IO blocks explicit."
                    inputs: ReviewInputs
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E003")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('inputs ReviewInputs[BaseInputs]: "Inputs"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    alternate_plan: "Alternate Plan Binding"') + 1,
        )
        self.assertIn("Missing inherited inputs entry in ReviewInputs: alternate_plan", str(error))

    def test_inherited_outputs_block_needs_keyed_entries_reports_related_parent_ref_line(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output ReviewComment: "Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                outputs BareOutputs: "Outputs"
                    ReviewComment

                outputs ChildOutputs[BareOutputs]: "Outputs"
                    "This child should fail before it can inherit the parent block."

                agent Demo:
                    role: "Keep inherited outputs patchable."
                    outputs: ChildOutputs
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E247")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('outputs ChildOutputs[BareOutputs]: "Outputs"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("    ReviewComment") + 1,
        )
        self.assertIn("contains unkeyed top-level refs", str(error))

    def test_duplicate_inherited_outputs_item_key_reports_related_first_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output ReviewComment: "Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                outputs BaseOutputs: "Outputs"
                    review_comment: "Review Comment"
                        ReviewComment

                outputs ChildOutputs[BaseOutputs]: "Outputs"
                    override review_comment: "Review Comment"
                        ReviewComment

                    override review_comment: "Review Comment"
                        ReviewComment

                agent Demo:
                    role: "Keep inherited outputs keys unique."
                    outputs: ChildOutputs
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        override_lines = [
            index + 1
            for index, line in enumerate(rendered.splitlines())
            if line == '    override review_comment: "Review Comment"'
        ]
        self.assertEqual(
            error.diagnostic.location.line,
            override_lines[1],
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            override_lines[0],
        )
        self.assertIn("Duplicate outputs item key in ChildOutputs: review_comment", str(error))

    def test_undefined_inherited_outputs_entry_points_at_inherit_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output ReviewComment: "Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                outputs BaseOutputs: "Outputs"
                    review_comment: "Review Comment"
                        ReviewComment

                outputs ChildOutputs[BaseOutputs]: "Outputs"
                    inherit coordination_handoff

                agent Demo:
                    role: "Keep inherited outputs explicit."
                    outputs: ChildOutputs
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E245")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    inherit coordination_handoff") + 1,
        )
        self.assertIn("cannot inherit undefined key `coordination_handoff`", str(error))

    def test_undefined_override_outputs_entry_points_at_override_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output ReviewComment: "Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                output CoordinationHandoff: "Coordination Handoff"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                outputs BaseOutputs: "Outputs"
                    review_comment: "Review Comment"
                        ReviewComment

                outputs ChildOutputs[BaseOutputs]: "Outputs"
                    override coordination_handoff: "Coordination Handoff"
                        CoordinationHandoff

                agent Demo:
                    role: "Keep inherited outputs scoped to parent keys."
                    outputs: ChildOutputs
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E001")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index(
                '    override coordination_handoff: "Coordination Handoff"'
            )
            + 1,
        )
        self.assertIn(
            "Cannot override undefined outputs entry in outputs BaseOutputs: coordination_handoff",
            str(error),
        )

    def test_missing_inherited_outputs_entry_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output DurableSectionTruth: "Durable Section Truth"
                    target: File
                        path: "section_root/_authoring/durable_section_truth.md"
                    shape: "Markdown Document"
                    requirement: Required

                output CoordinationHandoff: "Coordination Handoff"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                outputs BaseOutputs: "Outputs"
                    durable_section_truth: "Durable Section Truth"
                        DurableSectionTruth
                    coordination_handoff: "Coordination Handoff"
                        CoordinationHandoff

                outputs ChildOutputs[BaseOutputs]: "Outputs"
                    inherit durable_section_truth

                agent Demo:
                    role: "Keep inherited outputs explicit."
                    outputs: ChildOutputs
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E003")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('outputs ChildOutputs[BaseOutputs]: "Outputs"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    coordination_handoff: "Coordination Handoff"') + 1,
        )
        self.assertIn(
            "Missing inherited outputs entry in ChildOutputs: coordination_handoff",
            str(error),
        )

    def test_input_bucket_ref_with_inline_body_points_at_ref_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input ApprovedPlan: "Approved Plan"
                    source: File
                        path: "unit_root/APPROVED_PLAN.md"
                    shape: MarkdownDocument
                    requirement: Required

                agent Demo:
                    role: "Keep input refs bare inside IO buckets."
                    inputs: "Inputs"
                        ApprovedPlan
                            "This should fail."
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E301")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        ApprovedPlan") + 1,
        )
        self.assertIn("Declaration refs cannot define inline bodies", str(error))

    def test_input_bucket_ref_kind_mismatch_points_at_ref_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output ReviewComment: "Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                agent Demo:
                    role: "Keep input buckets on input declarations."
                    inputs: "Inputs"
                        ReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E301")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        ReviewComment") + 1,
        )
        self.assertIn("Inputs refs must resolve to input declarations", str(error))

    def test_input_wrapper_shorthand_ref_kind_mismatch_points_at_ref_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output ReviewComment: "Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                inputs SharedInputs: "Inputs"
                    review_comment: ReviewComment

                agent Demo:
                    role: "Keep input wrapper shorthand on input declarations."
                    inputs: SharedInputs
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E301")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    review_comment: ReviewComment") + 1,
        )
        self.assertIn("Inputs refs must resolve to input declarations", str(error))

    def test_self_ref_without_declaration_root_points_at_review_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                schema PlanReviewContract: "Plan Review Contract"
                    sections:
                        summary: "Summary"
                            "Summarize the reviewed plan."

                    gates:
                        outline_complete: "Outline Complete"
                            "Confirm the reviewed plan includes the outline."

                input DraftPlan: "Draft Plan"
                    source: File
                        path: "unit_root/DRAFT_PLAN.md"
                    shape: MarkdownDocument
                    requirement: Required

                agent ReviewLead:
                    role: "Own accepted plan follow-up."

                agent PlanAuthor:
                    role: "Repair rejected plan defects."

                output PlanReviewComment: "Plan Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    verdict: "Verdict"
                        "State the review verdict."

                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact."

                    analysis_performed: "Analysis Performed"
                        "Summarize the review analysis."

                    output_contents_that_matter: "Output Contents That Matter"
                        "State what the next owner should read first."

                    next_owner: "Next Owner"
                        "Name {{ReviewLead}} when accepted and {{PlanAuthor}} when rejected."

                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "List exact failing gates."

                review SchemaBackedPlanReview: "Schema Backed Plan Review"
                    subject: DraftPlan
                    contract: PlanReviewContract
                    comment_output: PlanReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        failing_gates: failure_detail.failing_gates
                        next_owner: next_owner

                    contract_checks: "Contract Checks"
                        accept "The schema review contract passes." when contract.passes

                    on_accept: "If Accepted"
                        current none
                        "Keep {{self:reviewed_artifact}} aligned."
                        route "Accepted draft returns to ReviewLead." -> ReviewLead

                    on_reject: "If Rejected"
                        current none
                        route "Rejected draft returns to PlanAuthor." -> PlanAuthor

                agent Demo:
                    role: "Fail loud when self has no declaration root."
                    review: SchemaBackedPlanReview
                    inputs: "Inputs"
                        DraftPlan
                    outputs: "Outputs"
                        PlanReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E312")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(error.diagnostic.location.line, None)
        self.assertIn("`self:` needs a declaration-root addressable context", str(error))

    def test_inputs_field_ref_kind_mismatch_points_at_field_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                output ReviewComment: "Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                outputs SharedOutputs: "Outputs"
                    review_comment: "Review Comment"
                        ReviewComment

                agent Demo:
                    role: "Keep inputs fields on inputs blocks."
                    inputs: SharedOutputs
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E248")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    inputs: SharedOutputs") + 1,
        )
        self.assertIn("Inputs fields must resolve to inputs blocks, not outputs blocks", str(error))

    def test_inputs_patch_base_kind_mismatch_points_at_patch_field_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input ApprovedPlan: "Approved Plan"
                    source: File
                        path: "unit_root/APPROVED_PLAN.md"
                    shape: MarkdownDocument
                    requirement: Required

                output ReviewComment: "Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                outputs SharedOutputs: "Outputs"
                    review_comment: "Review Comment"
                        ReviewComment

                abstract agent BaseAgent:
                    role: "Own shared IO."
                    inputs: "Inputs"
                        approved_plan: "Approved Plan"
                            ApprovedPlan

                agent Demo[BaseAgent]:
                    role: "Reject wrong-kind IO patch bases."
                    inputs[SharedOutputs]: "Inputs"
                        approved_plan: "Approved Plan"
                            ApprovedPlan
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E249")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('    inputs[SharedOutputs]: "Inputs"') + 1,
        )
        self.assertIn("Inputs patch fields must inherit from inputs blocks, not outputs blocks", str(error))

    def test_omitted_inputs_wrapper_title_reports_direct_ref_sites(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input LessonsIssueLedger: "Lessons Issue Ledger"
                    source: File
                        path: "catalog/lessons_issue_ledger.json"
                    shape: "JSON Document"
                    requirement: Required

                input ForwardIssueLedger: "Forward Issue Ledger"
                    source: File
                        path: "catalog/forward_issue_ledger.json"
                    shape: "JSON Document"
                    requirement: Advisory

                inputs InvalidSectionDossierInputs: "Your Inputs"
                    issue_ledger:
                        LessonsIssueLedger
                        ForwardIssueLedger

                agent Demo:
                    role: "Keep omitted IO wrapper titles unambiguous."
                    inputs: InvalidSectionDossierInputs
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("    issue_ledger:") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 2)
        related_lines = sorted(
            related.location.line
            for related in error.diagnostic.related
            if related.location is not None
        )
        self.assertEqual(
            related_lines,
            sorted(
                [
                    rendered.splitlines().index("        LessonsIssueLedger") + 1,
                    rendered.splitlines().index("        ForwardIssueLedger") + 1,
                ]
            ),
        )
        self.assertIn("requires exactly one lowerable direct declaration", str(error))

    def test_review_verdict_binding_points_at_field_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input DraftSpec: "Draft Spec"
                    source: File
                        path: "unit_root/DRAFT_SPEC.md"
                    shape: MarkdownDocument
                    requirement: Required
                    "Use the draft under review."

                workflow VerdictReviewContract: "Verdict Review Contract"
                    completeness: "Completeness"
                        "Confirm the draft covers the required sections."

                agent ReviewLead:
                    role: "Own accepted review follow-up."
                    workflow: "Follow Up"
                        "Take accepted review work."

                agent DraftAuthor:
                    role: "Own rejected review follow-up."
                    workflow: "Revise"
                        "Revise the draft."

                output GuardedVerdictReviewComment: "Guarded Verdict Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    verdict: "Verdict" when verdict == ReviewVerdict.changes_requested:
                        "Say whether the review accepted the draft or asked for changes."

                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact this review judged."

                    analysis_performed: "Analysis Performed"
                        "Sum up the review work that led to the verdict."

                    output_contents_that_matter: "Output Contents That Matter"
                        "Summarize the parts of the draft the next owner must read first."

                    next_owner: "Next Owner"
                        "Name the next owner."

                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "Name the failing review gates in authored order."

                review GuardedVerdictReview: "Guarded Verdict Review"
                    subject: DraftSpec
                    contract: VerdictReviewContract
                    comment_output: GuardedVerdictReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        failing_gates: failure_detail.failing_gates
                        next_owner: next_owner

                    checks: "Checks"
                        accept "The shared review contract passes." when contract.passes

                    on_accept: "If Accepted"
                        current none
                        route "Accepted review goes to ReviewLead." -> ReviewLead
                        route "Accepted review also goes to DraftAuthor." -> DraftAuthor

                    on_reject: "If Rejected"
                        current none
                        route "Rejected review goes to DraftAuthor." -> DraftAuthor

                agent Demo:
                    role: "Reject verdict bindings that hide accepted outcomes."
                    review: GuardedVerdictReview
                    inputs: "Inputs"
                        DraftSpec
                    outputs: "Outputs"
                        GuardedVerdictReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E495")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        verdict: verdict")
            + 1,
        )
        self.assertEqual(error.diagnostic.related, ())
        self.assertIn("Resolved review verdict", str(error))

    def test_review_outcome_multiple_currents_report_related_line(self) -> None:
        prompt_path, error = self._compile_repo_prompt_error(
            "examples/49_review_capstone/prompts/INVALID_CURRENT_NONE_AND_CURRENT_ARTIFACT.prompt",
            agent="InvalidCurrentNoneAndCurrentArtifactDemo",
        )
        prompt_lines = prompt_path.read_text(encoding="utf-8").splitlines()

        error = error
        self.assertEqual(error.diagnostic.code, "E486")
        self.assertEqual(error.diagnostic.location.path, prompt_path)
        self.assertEqual(
            error.diagnostic.location.line,
            prompt_lines.index(
                "                current artifact DraftSpec via BrokenCapstoneReviewComment.current_artifact"
            )
            + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            prompt_lines.index("                current none") + 1,
        )
        self.assertIn("first currentness result", str(error))

    def test_review_subject_disambiguation_points_at_outcome_section(self) -> None:
        prompt_path, error = self._compile_repo_prompt_error(
            "examples/47_review_multi_subject_mode_and_trigger_carry/prompts/INVALID_SUBJECT_SET_WITHOUT_DISAMBIGUATION.prompt",
            agent="InvalidSubjectSetWithoutDisambiguationDemo",
        )
        prompt_lines = prompt_path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(error.diagnostic.code, "E489")
        self.assertEqual(error.diagnostic.location.path, prompt_path)
        self.assertEqual(
            error.diagnostic.location.line,
            prompt_lines.index('    on_accept: "If Accepted"') + 1,
        )
        self.assertEqual(error.diagnostic.related, ())
        self.assertIn("branch `on_accept`", str(error))

    def test_review_next_owner_binding_points_at_field_binding_with_route_related_site(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                input DraftSpec: "Draft Spec"
                    source: File
                        path: "unit_root/DRAFT_SPEC.md"
                    shape: MarkdownDocument
                    requirement: Required
                    "Use the draft under review."

                workflow NextOwnerReviewContract: "Next Owner Review Contract"
                    completeness: "Completeness"
                        "Confirm the draft covers the required sections."

                agent ReviewLead:
                    role: "Own accepted review follow-up."
                    workflow: "Follow Up"
                        "Take accepted review work."

                agent DraftAuthor:
                    role: "Own rejected review follow-up."
                    workflow: "Revise"
                        "Revise the draft."

                output GuardedNextOwnerReviewComment: "Guarded Next Owner Review Comment"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required

                    verdict: "Verdict"
                        "Say whether the review accepted the draft or asked for changes."

                    reviewed_artifact: "Reviewed Artifact"
                        "Name the reviewed artifact this review judged."

                    analysis_performed: "Analysis Performed"
                        "Sum up the review work that led to the verdict."

                    output_contents_that_matter: "Output Contents That Matter"
                        "Summarize the parts of the draft the next owner must read first."

                    next_owner: "Next Owner" when verdict == ReviewVerdict.changes_requested:
                        "Name the next owner."

                    failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:
                        failing_gates: "Failing Gates"
                            "Name the failing review gates in authored order."

                review GuardedNextOwnerReview: "Guarded Next Owner Review"
                    subject: DraftSpec
                    contract: NextOwnerReviewContract
                    comment_output: GuardedNextOwnerReviewComment

                    fields:
                        verdict: verdict
                        reviewed_artifact: reviewed_artifact
                        analysis: analysis_performed
                        readback: output_contents_that_matter
                        failing_gates: failure_detail.failing_gates
                        next_owner: next_owner

                    checks: "Checks"
                        reject "The draft still needs changes." when DraftSpec.needs_changes
                        accept "The shared review contract passes." when contract.passes

                    on_accept: "If Accepted"
                        current none
                        route "Accepted review goes to ReviewLead." -> ReviewLead

                    on_reject: "If Rejected"
                        current none
                        route "Rejected review goes to DraftAuthor." -> DraftAuthor

                agent Demo:
                    role: "Reject next-owner bindings that hide routed accept branches."
                    review: GuardedNextOwnerReview
                    inputs: "Inputs"
                        DraftSpec
                    outputs: "Outputs"
                        GuardedNextOwnerReviewComment
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E496")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index("        next_owner: next_owner") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index(
                '        route "Accepted review goes to ReviewLead." -> ReviewLead'
            )
            + 1,
        )
        self.assertIn("resolved route", str(error))

    def test_review_current_none_mismatch_points_at_current_none_line(self) -> None:
        prompt_path, error = self._compile_repo_prompt_error(
            "examples/46_review_current_truth_and_trust_surface/prompts/INVALID_CURRENT_NONE_REQUIRES_GUARDED_CARRIER.prompt",
            agent="InvalidCurrentNoneRequiresGuardedCarrierDemo",
        )
        prompt_lines = prompt_path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(error.diagnostic.code, "E497")
        self.assertEqual(error.diagnostic.location.path, prompt_path)
        self.assertEqual(
            error.diagnostic.location.line,
            prompt_lines.index("        current none") + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            prompt_lines.index('    current_artifact: "Current Artifact"') + 1,
        )
        self.assertIn("carrier field", str(error))

    def test_review_optional_blocked_gate_binding_points_at_field_binding(self) -> None:
        prompt_path, error = self._compile_repo_prompt_error(
            "examples/49_review_capstone/prompts/INVALID_UNGUARDED_BLOCKED_GATE.prompt",
            agent="InvalidUnguardedBlockedGateDemo",
        )
        prompt_lines = prompt_path.read_text(encoding="utf-8").splitlines()

        self.assertEqual(error.diagnostic.code, "E499")
        self.assertEqual(error.diagnostic.location.path, prompt_path)
        self.assertEqual(
            error.diagnostic.location.line,
            prompt_lines.index("        blocked_gate: failure_detail.blocked_gate") + 1,
        )
        self.assertEqual(error.diagnostic.related, ())
        self.assertIn("`blocked_gate`", str(error))

    def test_compile_skill_package_missing_target_reports_file_scoped_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                agent Demo:
                    role: "Keep package compilation explicit."
                """,
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_skill_package()

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertIsNone(error.diagnostic.location.line)
        self.assertIn("Missing target skill package.", str(error))

    def test_compile_readable_missing_target_document_reports_file_scoped_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                agent Demo:
                    role: "Keep readable targets explicit."
                """,
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_readable_declaration(
                    "document",
                    "MissingGuide",
                )

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertIsNone(error.diagnostic.location.line)
        self.assertIn("Missing target document declaration: MissingGuide", str(error))

    def test_compile_readable_unsupported_kind_reports_file_scoped_location(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prompt_path = self._write_prompt(
                root,
                """\
                document Guide: "Guide"
                    section intro: "Intro"
                        "Start here."
                """,
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_readable_declaration(
                    "worksheet",
                    "Guide",
                )

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertIsNone(error.diagnostic.location.line)
        self.assertIn("Unsupported readable declaration kind: worksheet", str(error))

    def test_document_cycle_points_at_document_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                document CycleA[CycleB]: "Cycle A"
                    section intro: "Intro"
                        "Start here."

                document CycleB[CycleA]: "Cycle B"
                    section intro: "Intro"
                        "Stay here."
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_readable_declaration(
                    "document",
                    "CycleA",
                )

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('document CycleA[CycleB]: "Cycle A"') + 1,
        )
        self.assertIn("Cyclic document inheritance", str(error))

    def test_document_definitions_invalid_entry_points_at_definition_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                document BrokenGuide: "Broken Guide"
                    definitions read_order: "Read Order"
                        draft: "Draft"
                            "Review the current draft first."
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)
            document_decl = next(
                decl for decl in prompt.declarations if isinstance(decl, model.DocumentDecl)
            )
            definitions_block = next(
                item
                for item in document_decl.body.items
                if isinstance(item, model.ReadableBlock) and item.kind == "definitions"
            )
            mutated_document = replace(
                document_decl,
                body=replace(
                    document_decl.body,
                    items=tuple(
                        replace(
                            item,
                            payload=(
                                item.payload[0],
                                model.ReadableListItem(
                                    key=None,
                                    text="Wrong shape.",
                                    source_span=item.payload[0].source_span,
                                ),
                            ),
                        )
                        if item is definitions_block
                        else item
                        for item in document_decl.body.items
                    ),
                ),
            )
            mutated_prompt = replace(
                prompt,
                declarations=tuple(
                    mutated_document if decl is document_decl else decl
                    for decl in prompt.declarations
                ),
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(mutated_prompt).compile_readable_declaration(
                    "document",
                    "BrokenGuide",
                )

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E297")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        draft: "Draft"') + 1,
        )
        self.assertIn("Readable definitions entries must stay definition items", str(error))

    def test_skills_cycle_points_at_skills_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                skill GroundingSkill: "Grounding Skill"
                    purpose: "Ground the reply."

                skills CycleA[CycleB]: "Skills"
                    skill primary: GroundingSkill
                        requirement: Required

                skills CycleB[CycleA]: "Skills"
                    skill primary: GroundingSkill
                        requirement: Required

                agent Demo:
                    role: "Use the cyclic skills block."
                    skills: CycleA
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E250")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('skills CycleA[CycleB]: "Skills"') + 1,
        )
        self.assertIn("Cyclic skills inheritance", str(error))

    def test_missing_inherited_skills_entry_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                skill GroundingSkill: "Grounding Skill"
                    purpose: "Ground the reply."

                skills BaseSkills: "Skills"
                    skill primary: GroundingSkill
                        requirement: Required

                skills ChildSkills[BaseSkills]: "Skills"
                    "Keep the inherited shape."

                agent Demo:
                    role: "Keep inherited skills complete."
                    skills: ChildSkills
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_agent("Demo")

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E003")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('skills ChildSkills[BaseSkills]: "Skills"') + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index("    skill primary: GroundingSkill") + 1,
        )
        self.assertIn("Missing inherited skills entry in ChildSkills: primary", str(error))

    def test_analysis_cycle_points_at_analysis_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                analysis CycleA[CycleB]: "Cycle A"
                    facts: "Facts"
                        "Keep moving."

                analysis CycleB[CycleA]: "Cycle B"
                    facts: "Facts"
                        "Keep moving."
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_readable_declaration(
                    "analysis",
                    "CycleA",
                )

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('analysis CycleA[CycleB]: "Cycle A"') + 1,
        )
        self.assertIn("Cyclic analysis inheritance", str(error))

    def test_missing_inherited_analysis_entry_reports_related_parent_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                analysis BaseAnalysis: "Base Analysis"
                    facts: "Facts"
                        "Keep the key fact."

                analysis ChildAnalysis[BaseAnalysis]: "Child Analysis"
                    "Keep the inherited shape."
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(parse_file(prompt_path)).compile_readable_declaration(
                    "analysis",
                    "ChildAnalysis",
                )

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E003")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index(
                'analysis ChildAnalysis[BaseAnalysis]: "Child Analysis"'
            )
            + 1,
        )
        self.assertEqual(len(error.diagnostic.related), 1)
        self.assertEqual(
            error.diagnostic.related[0].location.line,
            rendered.splitlines().index('    facts: "Facts"') + 1,
        )
        self.assertIn("Missing inherited analysis entry in ChildAnalysis: facts", str(error))

    def test_analysis_empty_basis_points_at_statement_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = """\
                analysis BrokenAnalysis: "Broken Analysis"
                    stages: "Stages"
                        prove "Release plan" from {CurrentPlan}

                input CurrentPlan: "Current Plan"
                    source: File
                        path: "unit_root/CURRENT_PLAN.md"
                    shape: MarkdownDocument
                    requirement: Required
                """
            rendered = textwrap.dedent(source)
            prompt_path = self._write_prompt(root, source)
            prompt = parse_file(prompt_path)
            analysis_decl = next(
                decl for decl in prompt.declarations if isinstance(decl, model.AnalysisDecl)
            )
            section = analysis_decl.body.items[0]
            prove_stmt = section.items[0]
            mutated_analysis = replace(
                analysis_decl,
                body=replace(
                    analysis_decl.body,
                    items=(
                        replace(
                            section,
                            items=(
                                replace(
                                    prove_stmt,
                                    basis=model.LawPathSet(
                                        paths=(),
                                        source_span=prove_stmt.basis.source_span,
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            )
            mutated_prompt = replace(
                prompt,
                declarations=tuple(
                    mutated_analysis if decl is analysis_decl else decl
                    for decl in prompt.declarations
                ),
            )

            with self.assertRaises(CompileError) as ctx:
                CompilationSession(mutated_prompt).compile_readable_declaration(
                    "analysis",
                    "BrokenAnalysis",
                )

        error = ctx.exception
        self.assertEqual(error.diagnostic.code, "E299")
        self.assertEqual(error.diagnostic.location.path, prompt_path.resolve())
        self.assertEqual(
            error.diagnostic.location.line,
            rendered.splitlines().index('        prove "Release plan" from {CurrentPlan}') + 1,
        )
        self.assertIn("Analysis basis may not be empty", str(error))


if __name__ == "__main__":
    unittest.main()
