from __future__ import annotations

import textwrap
import unittest

from doctrine import model
from doctrine.parser import parse_text


class GroupedInheritTests(unittest.TestCase):
    def test_grouped_inherit_lowers_across_shipped_inherited_families(self) -> None:
        prompt = parse_text(
            textwrap.dedent(
                """\
                abstract agent BaseAgent:
                    abstract role_home
                    abstract workflow
                    abstract review

                agent ChildAgent[BaseAgent]:
                    inherit {role_home, workflow, review}

                workflow BaseWorkflow: "Base Workflow"
                    opening: "Opening"
                        "Open."
                    closing: "Closing"
                        "Close."
                    law:
                        currentness:
                            current none
                        routing:
                            stop "Stop."

                workflow ChildWorkflow[BaseWorkflow]: "Child Workflow"
                    inherit {opening, closing}
                    law:
                        inherit {currentness, routing}

                analysis BaseAnalysis: "Base Analysis"
                    facts: "Facts"
                        "Fact."

                analysis ChildAnalysis[BaseAnalysis]: "Child Analysis"
                    inherit {facts}

                schema BaseSchema: "Base Schema"
                    sections:
                        summary: "Summary"
                            "Body."
                    groups:
                        packet: "Packet"
                            summary

                schema ChildSchema[BaseSchema]: "Child Schema"
                    inherit {sections, groups}

                document BaseDocument: "Base Document"
                    section intro: "Intro"
                        "Body."

                document ChildDocument[BaseDocument]: "Child Document"
                    inherit {intro}

                skill GroundingSkill: "Grounding Skill"
                    purpose: "Ground."

                skills BaseSkills: "Base Skills"
                    skill primary: GroundingSkill
                        requirement: Required

                skills ChildSkills[BaseSkills]: "Child Skills"
                    inherit {primary}

                inputs BaseInputs: "Base Inputs"
                    draft: "Draft"
                        source: File
                            path: "draft.md"

                inputs ChildInputs[BaseInputs]: "Child Inputs"
                    inherit {draft}

                output shape BaseShape: "Base Shape"
                    kind: JsonObject
                    schema: SharedSchema

                output shape ChildShape[BaseShape]: "Child Shape"
                    inherit {kind, schema}

                output schema BaseOutputSchema: "Base Output Schema"
                    field summary: "Summary"
                        type: string
                    example:
                        summary: "Hello"

                output schema ChildOutputSchema[BaseOutputSchema]: "Child Output Schema"
                    inherit {summary, example}

                output BaseOutput: "Base Output"
                    target: TurnResponse
                    shape: Comment
                    requirement: Required
                    must_include: "Must Include"
                        summary: "Summary"
                            "Body."

                output ChildOutput[BaseOutput]: "Child Output"
                    inherit {target, shape, requirement, must_include}

                review BaseReview: "Base Review"
                    subject: Draft
                    contract: DraftContract
                    comment_output: DraftComment
                    fields:
                        verdict: verdict
                    on_accept: "Accept"
                        current artifact Draft via DraftComment.current_artifact

                review ChildReview[BaseReview]: "Child Review"
                    inherit {fields, on_accept}
                """
            )
        )

        child_agent = prompt.declarations[1]
        self.assertIsInstance(child_agent, model.Agent)
        self.assertEqual(
            tuple(field.key for field in child_agent.fields),
            ("role_home", "workflow", "review"),
        )
        self.assertTrue(all(isinstance(field, model.AuthoredSlotInherit) for field in child_agent.fields))
        self.assertEqual(child_agent.fields[0].source_span, model.SourceSpan(line=7, column=5))

        child_workflow = prompt.declarations[3]
        self.assertIsInstance(child_workflow, model.WorkflowDecl)
        self.assertEqual(tuple(item.key for item in child_workflow.body.items), ("opening", "closing"))
        self.assertTrue(all(isinstance(item, model.InheritItem) for item in child_workflow.body.items))
        self.assertIsNotNone(child_workflow.body.law)
        self.assertEqual(
            tuple(item.key for item in child_workflow.body.law.items),
            ("currentness", "routing"),
        )
        self.assertTrue(all(isinstance(item, model.LawInherit) for item in child_workflow.body.law.items))

        child_analysis = prompt.declarations[5]
        self.assertIsInstance(child_analysis, model.AnalysisDecl)
        self.assertEqual(tuple(item.key for item in child_analysis.body.items), ("facts",))

        child_schema = prompt.declarations[7]
        self.assertIsInstance(child_schema, model.SchemaDecl)
        self.assertEqual(tuple(item.key for item in child_schema.body.items), ("sections", "groups"))

        child_document = prompt.declarations[9]
        self.assertIsInstance(child_document, model.DocumentDecl)
        self.assertEqual(tuple(item.key for item in child_document.body.items), ("intro",))

        child_skills = prompt.declarations[12]
        self.assertIsInstance(child_skills, model.SkillsDecl)
        self.assertEqual(tuple(item.key for item in child_skills.body.items), ("primary",))

        child_inputs = prompt.declarations[14]
        self.assertIsInstance(child_inputs, model.InputsDecl)
        self.assertEqual(tuple(item.key for item in child_inputs.body.items), ("draft",))

        child_shape = prompt.declarations[16]
        self.assertIsInstance(child_shape, model.OutputShapeDecl)
        self.assertEqual(tuple(item.key for item in child_shape.items), ("kind", "schema"))

        child_output_schema = prompt.declarations[18]
        self.assertIsInstance(child_output_schema, model.OutputSchemaDecl)
        self.assertEqual(tuple(item.key for item in child_output_schema.items), ("summary", "example"))

        child_output = prompt.declarations[20]
        self.assertIsInstance(child_output, model.OutputDecl)
        self.assertEqual(
            tuple(item.key for item in child_output.items if isinstance(item, model.InheritItem)),
            ("target", "shape", "requirement", "must_include"),
        )

        child_review = prompt.declarations[22]
        self.assertIsInstance(child_review, model.ReviewDecl)
        self.assertEqual(tuple(item.key for item in child_review.body.items), ("fields", "on_accept"))


if __name__ == "__main__":
    unittest.main()
