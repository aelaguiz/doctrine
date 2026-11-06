from __future__ import annotations

import unittest
import json

from tests.ws3_support import HomeProject
from doctrine.homes import compile_homes
from doctrine.emit_common import load_emit_targets

from tests import test_late_binding
from doctrine.diagnostics import CompileError
from doctrine.flow_renderer import render_flow_d2
from doctrine.renderer import render_markdown


class TeamTests(unittest.TestCase):
    session = test_late_binding.LateBindingTests.session

    def test_member_name_and_folder(self):
        compiled = self.session('team T: "Team"\n    home: "pods/core"\n    member tech_lead: "Lead"\n        role: "{{agent:key}} {{agent:home}} {{agent:folder}}"\n').compile_agent('T.tech_lead')
        self.assertEqual(compiled.name, 'T.tech_lead')
        self.assertEqual(render_markdown(compiled), 'tech_lead pods/core/tech-lead tech-lead\n')

    def test_member_ref_resolves_in_route(self):
        session = self.session('''team T: "Team"
    home: "pod"
    member qa: "QA"
        role: "QA."
agent A:
    role: "Ask {{T.qa}} or {{T.qa:title}}."
    work: "Work"
        send: "Send"
            route "Send" -> T.qa
''')
        rendered = render_markdown(session.compile_agent('A'))
        self.assertIn('Ask QA or QA.', rendered)
        self.assertIn('Send', rendered)
        self.assertIn('QA', rendered)

    def test_abstract_team_stamps_members_per_team(self):
        session = self.session('''abstract agent R:
    role: "{{team:title}} {{agent:title}}"
abstract team Base:
    member qa[R]: "QA"
team One[Base]: "One"
    home: "one"
team Two[Base]: "Two"
    home: "two"
''')
        self.assertEqual(render_markdown(session.compile_agent('One.qa')), 'One QA\n')
        self.assertEqual(render_markdown(session.compile_agent('Two.qa')), 'Two QA\n')

    def test_overlay_render_order(self):
        session = self.session('''abstract agent R:
    role: "Role."
    first: "First"
        "First."
    second: "Second"
        "Second."
team T: "Team"
    home: "t"
    member qa[R]: "QA"
        own: "Own"
            "Own."
    member lead[R]: "Lead"
        inherit *
        own: "Own"
            "Own."
''')
        self.assertEqual(render_markdown(session.compile_agent('T.qa')), 'Role.\n\n## Own\n\nOwn.\n\n## First\n\nFirst.\n\n## Second\n\nSecond.\n')
        rendered = render_markdown(session.compile_agent('T.lead'))
        self.assertLess(rendered.index('## Second'), rendered.index('## Own'))

    def test_team_doctrine_stays_out_of_member_home(self):
        session = self.session('team T: "Team"\n    home: "t"\n    role: "Team only."\n    shared: "Shared"\n        "Team doctrine."\n    member qa: "QA"\n        role: "Member only."\n')
        self.assertIn('Team doctrine.', render_markdown(session.compile_agent('T')))
        self.assertEqual(render_markdown(session.compile_agent('T.qa')), 'Member only.\n')

    def test_tree_from_paths_only(self):
        session = self.session('''team Outer: "Outer"
    home: "."
    values:
        word: "outer"
team Sibling: "Sibling"
    home: "elsewhere"
    values:
        word: "sibling"
team Inner: "Inner"
    home: "deep/nested"
    member qa: "QA"
        role: "{{agent:word}}"
''')
        self.assertEqual(render_markdown(session.compile_agent('Inner.qa')), 'outer\n')

    def test_roster_skips_row_without_value(self):
        rendered = render_markdown(self.session(self.roster_source()).compile_agent('T'))
        self.assertIn('| Test | QA |', rendered)
        self.assertNotIn('| Lead |', rendered)

    def test_roster_static_rows_follow(self):
        rendered = render_markdown(self.session(self.roster_source()).compile_agent('T'))
        self.assertLess(rendered.index('| Test | QA |'), rendered.index('| Goal | Owner |'))

    def roster_source(self):
        return '''team T: "Team"
    home: "t"
    work: "Work"
        roster calls: "Calls"
            what: "What" = "{{agent:calls}}"
            who: "Who" = "{{agent:title}}"
            rows:
                owner:
                    what: "Goal"
                    who: "Owner"
    member qa: "QA"
        role: "QA."
        values:
            calls: "Test"
    member lead: "Lead"
        role: "Lead."
'''

    def test_member_refs_cross_module_with_inherited_fields(self):
        session = self.session('''import roles
team T: "Team"
    home: "t"
    member qa[roles.R]: "QA"
        own: "Own"
            "Own."
''', {'prompts/roles/AGENTS.prompt': '''analysis A: "Analysis"
    "Use this analysis."
input I: "Input"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required
export abstract agent R:
    role: "Role."
    inputs: "Inputs"
        I
    analysis: A
'''})
        rendered = render_markdown(session.compile_agent('T.qa'))
        self.assertIn('Use this analysis.', rendered)
        self.assertIn('Input', rendered)

    def test_missing_and_abstract_members_fail(self):
        for target in ('T.absent', 'Base.qa'):
            with self.subTest(target=target):
                session = self.session('abstract team Base:\n    member qa: "QA"\n        role: "QA."\nteam T[Base]: "Team"\n    home: "t"\nagent A:\n    role: "Ask {{' + target + '}}."\n')
                with self.assertRaises(CompileError) as caught:
                    session.compile_agent('A')
                self.assertEqual(caught.exception.code, 'E276')

    def test_team_and_visible_module_name_is_e270(self):
        session = self.session('''import T
team T: "Team"
    home: "t"
    member qa: "QA"
        role: "Test."
agent A:
    role: "Ask {{T.qa}}."
''', {'prompts/T/AGENTS.prompt': 'export agent qa:\n    role: "Other QA."\n'})
        with self.assertRaises(CompileError) as caught:
            session.compile_agent('A')
        self.assertEqual(caught.exception.code, 'E270')

    def test_member_can_inherit_another_member(self):
        session = self.session('''abstract team Base:
    member qa: "QA"
        role: "QA {{agent:title}}."
        work: "Work"
            "Test."
abstract team Middle[Base]:
    values:
        unit: "change"
team T[Middle]: "Team"
    home: "t"
    member senior[T.qa]: "Senior"
''')
        self.assertEqual(render_markdown(session.compile_agent('T.senior')), 'QA Senior.\n\n## Work\n\nTest.\n')

    def test_exported_member_ref(self):
        session = self.session('import pod\nagent A[pod.T.qa]:\n    inherit *\n', {'prompts/pod/AGENTS.prompt': 'export team T: "Team"\n    home: "t"\n    member qa: "QA"\n        role: "Test."\n'})
        self.assertEqual(render_markdown(session.compile_agent('A')), 'Test.\n')

    def test_parent_member_values_keep_source_module(self):
        session = self.session('import pod\nagent A[pod.T.qa]:\n    inherit *\n', {
            'prompts/roles/AGENTS.prompt': '''workflow W: "Original"
    "Text."
export abstract team Base:
    member qa: "QA"
        role: "{{agent:word}}"
        values:
            word: "{{W:title}}"
''',
            'prompts/pod/AGENTS.prompt': '''import roles
export team T[roles.Base]: "Team"
    home: "t"
''',
        })
        self.assertEqual(render_markdown(session.compile_agent('A')), 'Original\n')

    def test_rule_member_target(self):
        session = self.session('''team T: "Team"
    home: "t"
    member qa: "QA"
        role: "Test."
agent Worker[T.qa]:
    inherit *
rule R: "Keep QA"
    scope:
        agent_tag: Worker
    assertions:
        requires inherit T.qa
    message: "Keep the role."
''')
        self.assertEqual(render_markdown(session.compile_agent('Worker')), 'Test.\n')

    def test_roster_in_member_and_document(self):
        session = self.session('''document D: "Doc"
    roster calls: "Calls"
        who: "Who" = "{{agent:title}}"
input I: "Input"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required
    structure: D
team T: "Team"
    home: "t"
    member qa: "QA"
        role: "QA."
        inputs: "Inputs"
            I
''')
        self.assertIn('| QA |', render_markdown(session.compile_agent('T.qa')))

    def test_team_home_and_field_errors(self):
        for source, detail in (
            ('team T: "Team"\n    home: "../t"\n', '`home: "../t"` must be a relative path with no `..` and no trailing `/`.'),
            ('team T: "Team"\n    home: "/t"\n', '`home: "/t"` must be a relative path with no `..` and no trailing `/`.'),
            ('team T: "Team"\n    home: "t/"\n', '`home: "t/"` must be a relative path with no `..` and no trailing `/`.'),
            ('abstract team T:\n    home: "t"\n', "Abstract team `T` can't have `home:`."),
            ('team T: "Team"\n    home: "t"\n    inputs: "Inputs"\n        "Wrong."\n', "Team `T` can't hold `inputs`. A team takes `role`, `values`, `budget`, slots, and members."),
            ('team T: "Team"\n    home: "t"\n    qa: "Work"\n        "Work."\n    member qa: "QA"\n        role: "QA."\n', 'Team `T` uses key `qa` twice.'),
        ):
            with self.subTest(source=source), self.assertRaises(CompileError) as caught:
                self.session(source + ('team Concrete[T]: \"Concrete\"\n    home: \"concrete\"\n' if source.startswith('abstract') else '')).compile_agent('Concrete' if source.startswith('abstract') else 'T')
            self.assertEqual(caught.exception.code, 'E606')
            self.assertEqual(caught.exception.diagnostic.detail, detail)

    def test_roster_column_and_row_errors(self):
        for body, detail in (
            ('            who: "Who" = "No member"\n', 'Column `who` has no `{{agent:...}}` in its cell.'),
            ('            who: "Who" = "{{agent:title}}"\n            rows:\n                owner:\n                    wrong: "Owner"\n', '`rows:` names unknown column `wrong`.'),
            ('            who: "Who" = "{{agent:title}}"\n            what: "What" = "{{agent:title}}"\n            rows:\n                owner:\n                    who: "Owner"\n', 'Row `owner` leaves column `what` empty.'),
        ):
            with self.subTest(body=body), self.assertRaises(CompileError) as caught:
                self.session('team T: "Team"\n    home: "t"\n    work: "Work"\n        roster r: "Roster"\n' + body).compile_agent('T')
            self.assertEqual(caught.exception.code, 'E609')
            self.assertEqual(caught.exception.diagnostic.detail, detail)

    def test_override_member_needs_a_parent_member(self):
        with self.assertRaises(CompileError) as caught:
            self.session('abstract team Base:\n    member qa: "QA"\n        role: "Test."\nteam T[Base]: "Team"\n    home: "t"\n    override member absent: "Absent"\n        role: "Role."\n').compile_agent('T')
        self.assertEqual(caught.exception.code, 'E001')
        self.assertEqual(caught.exception.diagnostic.detail, 'Cannot override undefined authored slot in agent T: absent')

    def test_grouped_inherit_in_member(self):
        session = self.session('''abstract agent Role:
    role: "Role."
    work: "Work"
        "Work."
team T: "Team"
    home: "t"
    member qa[Role]: "QA"
        inherit {role, work}
''')
        self.assertEqual(render_markdown(session.compile_agent('T.qa')), 'Role.\n\n## Work\n\nWork.\n')

    def test_roster_team_typo_is_e601(self):
        for first, second in (
            ('{{agent:title}} {{team:typo}}', '{{agent:title}}'),
            ('{{agent:absent}}', '{{agent:title}} {{team:typo}}'),
        ):
            source = self.roster_source().replace('{{agent:calls}}', first).replace('= "{{agent:title}}"', '= "' + second + '"')
            with self.subTest(first=first, second=second), self.assertRaises(CompileError) as caught:
                self.session(source).compile_agent('T')
            self.assertEqual(caught.exception.code, 'E601')
            self.assertIn('- `team:typo` at ', caught.exception.diagnostic.detail)

    def test_roster_skipping_every_member_is_e601(self):
        source = self.roster_source().replace('{{agent:calls}}', '{{agent:typo}}')
        with self.assertRaises(CompileError) as caught:
            self.session(source).compile_agent('T')
        self.assertEqual(caught.exception.code, 'E601')
        self.assertIn('- `agent:typo` at ', caught.exception.diagnostic.detail)

    def test_flow_graph_routes_to_a_member(self):
        team = 'team T: "Team"\n    home: "t"\n    member qa: "QA"\n        role: "Test."\n'
        for location in ('local', 'sibling', 'imported'):
            target = 'pod.T.qa' if location == 'imported' else 'T.qa'
            for route in ('workflow', 'route_field'):
                source = 'agent A:\n    role: "Route."\n'
                if route == 'workflow':
                    source += '    work: "Work"\n        send: "Send"\n            route "Send" -> ' + target + '\n'
                else:
                    source = 'output schema S: "Schema"\n    route field next: "Next"\n        send: "Send" -> ' + target + '\n    example:\n        next: "send"\noutput shape Shape: "Shape"\n    kind: JsonObject\n    schema: S\noutput O: "Output"\n    target: TurnResponse\n    shape: Shape\n    requirement: Required\n' + source + '    outputs: "Outputs"\n        O\n    final_output:\n        output: O\n        route: next\n'
                files = {}
                if location == 'local':
                    source = team + source
                elif location == 'sibling':
                    files['prompts/pod.prompt'] = team
                else:
                    source = 'import pod\n' + source
                    files['prompts/pod/AGENTS.prompt'] = 'export ' + team
                with self.subTest(location=location, route=route):
                    graph = self.session(source, files).extract_target_flow_graph(('A',))
                    self.assertIn('T.qa', [agent.name for agent in graph.agents])
                    self.assertTrue(any(edge.target_name == 'T.qa' and edge.kind == 'authored_route' for edge in graph.edges))
                    self.assertIn('QA', render_flow_d2(graph))

    def test_team_and_agent_cannot_share_a_name(self):
        team = 'team Same: "Team"\n    home: "t"\n'
        agent = 'agent Same:\n    role: "Role."\n'
        for first, second in ((team, agent), (agent, team)):
            for sibling in (False, True):
                with self.subTest(first=first, sibling=sibling), self.assertRaises(CompileError) as caught:
                    self.session(first if sibling else first + second, {'prompts/sibling.prompt': second} if sibling else {})
                self.assertEqual(caught.exception.code, 'E316' if sibling else 'E288')

    def test_second_home_is_e606(self):
        with self.assertRaises(CompileError) as caught:
            self.session('team T: "Team"\n    home: "first"\n    home: "second"\n').compile_agent('T')
        self.assertEqual(caught.exception.code, 'E606')
        self.assertEqual(caught.exception.diagnostic.detail, 'Team `T` uses key `home` twice.')


class TeamHomeTests(HomeProject, unittest.TestCase):
    def test_team_contract_order_and_sections(self):
        root = HomeProject.project(self, 'abstract team Base:\n    member qa: "QA"\n        role: "Test."\n        work: "Work"\n            "Test it."\nteam T[Base]: "Team"\n    home: "t"\n    member lead: "Lead"\n        role: "Lead."\n')
        homes, files = compile_homes(load_emit_targets(root / 'pyproject.toml')['homes'])
        members = json.loads(files['t/TEAM.contract.json'])['members']
        self.assertEqual([member['key'] for member in members], ['qa', 'lead'])
        self.assertEqual(members[0]['sections'], ['Work'])
        self.assertEqual(homes['t/qa']['compiled'].fields[0].origin[0], 'Base.qa')

    def test_e607_member_folder_collides_with_team(self):
        root = HomeProject.project(self, 'team A: "A"\n    home: "a"\n    member qa: "QA"\n        role: "Test."\nteam B: "B"\n    home: "a/qa"\n    role: "Other."\n')
        code, _, error = HomeProject.cli(self, root, 'build', '.')
        self.assertEqual(code, 1)
        self.assertIn('`A.qa` and `B` both land at `a/qa`.', error)
