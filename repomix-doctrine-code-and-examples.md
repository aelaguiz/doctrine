This file is a merged representation of a subset of the codebase, containing specifically included files and files not matching ignore patterns, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: doctrine/**/*.py, doctrine/**/*.lark, examples/**/*.md, examples/**/*.prompt, examples/**/cases.toml
- Files matching these patterns are excluded: example_agents/**, editors/vscode/tests/snap/**, **/__pycache__/**
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
doctrine/
  grammars/
    doctrine.lark
  __init__.py
  compiler.py
  diagnostic_smoke.py
  diagnostics.py
  emit_docs.py
  indenter.py
  model.py
  parser.py
  renderer.py
  verify_corpus.py
examples/
  01_hello_world/
    prompts/
      AGENTS.prompt
      INVALID_COMPILE_REORDERED.prompt
      INVALID_PARSE_MISSING_COLON.prompt
    ref/
      AGENTS.md
    cases.toml
  02_sections/
    prompts/
      AGENTS.prompt
      INVALID_DUPLICATE_SECTION_KEY.prompt
    ref/
      AGENTS.md
    cases.toml
  03_imports/
    prompts/
      broken/
        syntax.prompt
      chains/
        absolute/
          briefing.prompt
          closing.prompt
          opening.prompt
        deep/
          base/
            final_note.prompt
            topic.prompt
          levels/
            one/
              two/
                entry.prompt
              detail.prompt
        relative/
          entry.prompt
          leaf.prompt
        shared/
          context.prompt
          wrap_up.prompt
      invalid_duplicates/
        duplicate_names.prompt
      simple/
        nested/
          polite.prompt
        greeting.prompt
        object.prompt
      AGENTS.prompt
      INVALID_DUPLICATE_DECLARATION.prompt
      INVALID_IMPORTED_PARSE.prompt
      INVALID_MISSING_MODULE.prompt
      INVALID_UNRESOLVED_SYMBOL.prompt
    ref/
      AGENTS.md
    cases.toml
  04_inheritance/
    prompts/
      shared/
        greeters.prompt
        workflows.prompt
      AGENTS.prompt
    ref/
      hello_world_greeter/
        AGENTS.md
      imported_workflow_greeter/
        AGENTS.md
      inheritance_demo/
        AGENTS.md
    cases.toml
  05_workflow_merge/
    prompts/
      AGENTS.prompt
      INVALID_MISSING_INHERITED_ENTRY.prompt
    ref/
      invalid_override_briefing_agent/
        COMPILER_ERROR.md
      ordered_briefing_agent/
        AGENTS.md
      retitled_briefing_agent/
        AGENTS.md
    cases.toml
  06_nested_workflows/
    prompts/
      AGENTS.prompt
    ref/
      inherited_structured_briefing_agent/
        AGENTS.md
      inline_briefing_agent/
        AGENTS.md
      revised_structured_briefing_agent/
        AGENTS.md
      structured_briefing_agent/
        AGENTS.md
    cases.toml
  07_handoffs/
    build_ref/
      project_lead/
        AGENTS.md
      research_specialist/
        AGENTS.md
      writing_specialist/
        AGENTS.md
    prompts/
      AGENTS.prompt
      INVALID_REFERENCED_SLOT_WITH_INLINE_BODY.prompt
    ref/
      project_lead/
        AGENTS.md
      research_specialist/
        AGENTS.md
      writing_specialist/
        AGENTS.md
    cases.toml
  08_inputs/
    prompts/
      AGENTS.prompt
    ref/
      custom_source_input_agent/
        AGENTS.md
      env_input_agent/
        AGENTS.md
      path_input_agent/
        AGENTS.md
      prompt_input_agent/
        AGENTS.md
    cases.toml
  09_outputs/
    prompts/
      AGENTS.prompt
    ref/
      custom_target_output_agent/
        AGENTS.md
      file_output_agent/
        AGENTS.md
      json_file_output_agent/
        AGENTS.md
      turn_response_output_agent/
        AGENTS.md
    cases.toml
  10_routing_and_stop_rules/
    prompts/
      AGENTS.prompt
    ref/
      acceptance_reviewer/
        AGENTS.md
      project_lead/
        AGENTS.md
      section_author/
        AGENTS.md
      writing_specialist/
        AGENTS.md
    cases.toml
  11_skills_and_tools/
    prompts/
      AGENTS.prompt
    ref/
      lesson_copywriter/
        AGENTS.md
    cases.toml
  12_role_home_composition/
    prompts/
      AGENTS.prompt
    ref/
      lessons_copywriter/
        AGENTS.md
      lessons_project_lead/
        AGENTS.md
    cases.toml
  13_critic_protocol/
    prompts/
      AGENTS.prompt
    ref/
      acceptance_critic/
        AGENTS.md
      project_lead/
        AGENTS.md
      section_author/
        AGENTS.md
    cases.toml
  14_handoff_truth/
    build_ref/
      acceptance_critic/
        AGENTS.md
      project_lead/
        AGENTS.md
      section_author/
        AGENTS.md
    prompts/
      contracts/
        inputs.prompt
        outputs.prompt
      roles/
        acceptance_critic.prompt
        project_lead.prompt
        section_author.prompt
      AGENTS.prompt
    ref/
      acceptance_critic/
        AGENTS.md
      project_lead/
        AGENTS.md
      section_author/
        AGENTS.md
    cases.toml
  15_workflow_body_refs/
    prompts/
      shared/
        contracts.prompt
      AGENTS.prompt
      INVALID_AMBIGUOUS_REF.prompt
      INVALID_WORKFLOW_REF.prompt
    ref/
      workflow_section_refs_demo/
        AGENTS.md
    cases.toml
  16_workflow_string_interpolation/
    prompts/
      shared/
        contracts.prompt
      AGENTS.prompt
      INVALID_AMBIGUOUS_INTERPOLATION.prompt
      INVALID_FIELD_PATH.prompt
      INVALID_WORKFLOW_INTERPOLATION.prompt
    ref/
      workflow_string_interpolation_demo/
        AGENTS.md
    cases.toml
  17_agent_mentions/
    prompts/
      shared/
        roles.prompt
      AGENTS.prompt
      INVALID_ABSTRACT_AGENT_MENTION.prompt
      INVALID_AMBIGUOUS_AGENT_REF.prompt
      INVALID_WORKFLOW_MENTION.prompt
    ref/
      agent_mentions_demo/
        AGENTS.md
    cases.toml
  18_rich_io_buckets/
    prompts/
      AGENTS.prompt
      INVALID_OUTPUT_BUCKET_REF_BODY.prompt
      INVALID_OUTPUT_BUCKET_ROUTE.prompt
      INVALID_OUTPUT_BUCKET_SCALAR.prompt
      INVALID_OUTPUT_BUCKET_WRONG_KIND_REF.prompt
    ref/
      rich_io_bucket_agent/
        AGENTS.md
    cases.toml
  19_emphasized_prose_lines/
    prompts/
      AGENTS.prompt
      INVALID_PARSE_UNKNOWN_EMPHASIS.prompt
    ref/
      AGENTS.md
    cases.toml
  20_authored_prose_interpolation/
    prompts/
      AGENTS.prompt
      INVALID_AMBIGUOUS_RECORD_PROSE.prompt
      INVALID_ROLE_FIELD_PATH.prompt
      INVALID_ROUTE_LABEL_NONSCALAR.prompt
      INVALID_SKILL_PURPOSE_WORKFLOW_REF.prompt
    ref/
      AGENTS.md
    cases.toml
  21_first_class_skills_blocks/
    prompts/
      AGENTS.prompt
    cases.toml
  22_skills_block_inheritance/
    prompts/
      AGENTS.prompt
      INVALID_CYCLIC_SKILLS_INHERITANCE.prompt
    cases.toml
  23_first_class_io_blocks/
    prompts/
      AGENTS.prompt
      INVALID_WRONG_KIND_FIELD_REF.prompt
    cases.toml
  24_io_block_inheritance/
    prompts/
      AGENTS.prompt
      INVALID_MISSING_INHERITED_ENTRY.prompt
      INVALID_OVERRIDE.prompt
      INVALID_PATCH_WITHOUT_PARENT.prompt
      INVALID_UNDEFINED_INHERIT.prompt
      INVALID_UNKEYED_PARENT_REF.prompt
    cases.toml
  25_abstract_agent_io_override/
    prompts/
      AGENTS.prompt
      INVALID_WRONG_PATCH_BASE.prompt
    cases.toml
  26_abstract_authored_slots/
    prompts/
      AGENTS.prompt
      INVALID_MISSING_ABSTRACT_SLOT.prompt
      INVALID_MISSING_MULTIPLE_ABSTRACT_SLOTS.prompt
      INVALID_OVERRIDE_ABSTRACT_SLOT.prompt
    ref/
      acceptance_reviewer/
        AGENTS.md
    cases.toml
  27_addressable_record_paths/
    prompts/
      AGENTS.prompt
      INVALID_NON_ADDRESSABLE_RECORD_PATH.prompt
      INVALID_UNKNOWN_RECORD_PATH.prompt
    ref/
      addressable_record_paths_demo/
        AGENTS.md
    cases.toml
  28_addressable_workflow_paths/
    prompts/
      AGENTS.prompt
      INVALID_BARE_WORKFLOW_ROOT.prompt
      INVALID_UNKNOWN_WORKFLOW_PATH.prompt
      SELF_AND_DESCENT.prompt
    ref/
      workflow_path_refs_demo/
        AGENTS.md
    cases.toml
  29_enums/
    prompts/
      AGENTS.prompt
      INVALID_DUPLICATE_ENUM_MEMBER.prompt
      INVALID_UNKNOWN_ENUM_MEMBER.prompt
    ref/
      enum_refs_demo/
        AGENTS.md
    cases.toml
  30_law_route_only_turns/
    prompts/
      AGENTS.prompt
      INVALID_ACTIVE_BRANCH_WITHOUT_CURRENT.prompt
      INVALID_CURRENT_NONE_AND_CURRENT_ARTIFACT.prompt
      INVALID_ROUTE_WITHOUT_LABEL.prompt
      INVALID_ROUTE_WITHOUT_TARGET.prompt
    ref/
      route_only_turns_demo/
        AGENTS.md
    cases.toml
  31_currentness_and_trust_surface/
    prompts/
      AGENTS.prompt
      INVALID_CARRIER_OUTPUT_NOT_EMITTED.prompt
      INVALID_CURRENT_ARTIFACT_WITHOUT_VIA.prompt
      INVALID_CURRENT_OUTPUT_NOT_EMITTED.prompt
      INVALID_CURRENT_TARGET_WRONG_KIND.prompt
      INVALID_VIA_FIELD_NOT_IN_TRUST_SURFACE.prompt
      INVALID_VIA_UNKNOWN_OUTPUT_FIELD.prompt
    ref/
      current_approved_plan_demo/
        AGENTS.md
      current_section_metadata_demo/
        AGENTS.md
    cases.toml
  32_modes_and_match/
    prompts/
      AGENTS.prompt
      INVALID_ACTIVE_BRANCH_WITHOUT_CURRENT_AFTER_MATCH.prompt
      INVALID_DUPLICATE_CURRENT_IN_MATCH_ARM.prompt
      INVALID_MODE_VALUE_OUTSIDE_ENUM.prompt
      INVALID_NONEXHAUSTIVE_MODE_MATCH.prompt
    ref/
      mode_aware_edit_demo/
        AGENTS.md
    cases.toml
  33_scope_and_exact_preservation/
    prompts/
      AGENTS.prompt
      INVALID_OWN_AND_EXACT_PRESERVE_OVERLAP.prompt
      INVALID_OWN_AND_FORBID_OVERLAP.prompt
      INVALID_OWN_PATH_NOT_ADDRESSABLE.prompt
      INVALID_OWN_PATH_NOT_ROOTED_IN_CURRENT_ARTIFACT.prompt
    ref/
      narrow_metadata_edit_demo/
        AGENTS.md
    cases.toml
  34_structure_mapping_and_vocabulary_preservation/
    prompts/
      AGENTS.prompt
      INVALID_UNKNOWN_MAPPING_PRESERVE_TARGET.prompt
      INVALID_UNKNOWN_STRUCTURE_PRESERVE_TARGET.prompt
      INVALID_UNKNOWN_VOCABULARY_PRESERVE_TARGET.prompt
    ref/
      preserve_mapping_demo/
        AGENTS.md
      preserve_structure_demo/
        AGENTS.md
      preserve_vocabulary_demo/
        AGENTS.md
    cases.toml
  35_basis_roles_and_rewrite_evidence/
    prompts/
      AGENTS.prompt
      INVALID_CURRENT_ARTIFACT_IGNORED_FOR_TRUTH.prompt
      INVALID_SUPPORT_ONLY_AND_IGNORE_COMPARISON_CONTRADICTION.prompt
    ref/
      rewrite_aware_polish_demo/
        AGENTS.md
    cases.toml
  36_invalidation_and_rebuild/
    build_ref/
      blocked_section_review_demo/
        AGENTS.md
      rebuild_section_review_demo/
        AGENTS.md
      routing_owner/
        AGENTS.md
      structure_change_demo/
        AGENTS.md
    prompts/
      AGENTS.prompt
      INVALID_CURRENT_ARTIFACT_AND_INVALIDATION_SAME_TARGET.prompt
      INVALID_INVALIDATION_FIELD_NOT_IN_TRUST_SURFACE.prompt
      INVALID_INVALIDATION_WITHOUT_VIA.prompt
    ref/
      blocked_section_review_demo/
        AGENTS.md
      rebuild_section_review_demo/
        AGENTS.md
      structure_change_demo/
        AGENTS.md
    cases.toml
  37_law_reuse_and_patching/
    prompts/
      AGENTS.prompt
      INVALID_BARE_LAW_STATEMENT_IN_INHERITED_CHILD.prompt
      INVALID_DUPLICATE_INHERITED_LAW_SECTION.prompt
      INVALID_MISSING_INHERITED_LAW_SECTION.prompt
      INVALID_OVERRIDE_UNKNOWN_LAW_SECTION.prompt
    ref/
      base_metadata_polish_demo/
        AGENTS.md
      rewrite_aware_metadata_polish_demo/
        AGENTS.md
    cases.toml
  38_metadata_polish_capstone/
    prompts/
      AGENTS.prompt
    ref/
      metadata_polish_capstone_demo/
        AGENTS.md
      rewrite_aware_metadata_polish_capstone_demo/
        AGENTS.md
    cases.toml
  README.md
```

# Files

## File: doctrine/__init__.py
````python
"""Doctrine language bootstrap package."""

from doctrine.diagnostics import CompileError, EmitError, ParseError, DoctrineError

__all__ = [
    "CompileError",
    "EmitError",
    "ParseError",
    "DoctrineError",
]
````

## File: doctrine/indenter.py
````python
"""Indentation handling for the Doctrine bootstrap grammar."""

from lark.indenter import Indenter


class DoctrineIndenter(Indenter):
    """Minimal stock-Lark indenter for the bootstrap grammar."""

    NL_type = "_NL"
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 8
````

## File: examples/01_hello_world/prompts/INVALID_COMPILE_REORDERED.prompt
````
agent ReorderedFields:
    workflow: "Instruction"
        "This fixture should fail during compile."

    role: "You are a broken agent."
````

## File: examples/01_hello_world/prompts/INVALID_PARSE_MISSING_COLON.prompt
````
agent MissingColon
    role: "You are a broken agent."

    workflow: "Instruction"
        "This fixture should fail during parse."
````

## File: examples/02_sections/prompts/INVALID_DUPLICATE_SECTION_KEY.prompt
````
agent DuplicateSectionKeysDemo:
    role: "You are the duplicate section key demonstration agent."

    workflow: "Steps"
        "This example should fail before rendering."

        step_one: "Step One"
            "Say hello."

        step_one: "Step One Again"
            "Say world."
````

## File: examples/03_imports/prompts/broken/syntax.prompt
````
workflow BrokenWorkflow: "Broken Workflow"
    broken_section:
        "This imported module is intentionally invalid."
````

## File: examples/03_imports/prompts/chains/absolute/closing.prompt
````
workflow Closing: "Closing"
    "End with one clear next step."
````

## File: examples/03_imports/prompts/chains/absolute/opening.prompt
````
workflow Opening: "Opening"
    "State the topic."
````

## File: examples/03_imports/prompts/chains/deep/base/final_note.prompt
````
workflow FinalNote: "Final Note"
    "End with the final shared note."
````

## File: examples/03_imports/prompts/chains/deep/base/topic.prompt
````
workflow RootTopic: "Root Topic"
    "Name the root topic once."
````

## File: examples/03_imports/prompts/chains/shared/context.prompt
````
workflow SharedContext: "Shared Context"
    "Start with the shared context."
````

## File: examples/03_imports/prompts/chains/shared/wrap_up.prompt
````
workflow SharedWrapUp: "Shared Wrap-Up"
    "Finish with a shared wrap-up."
````

## File: examples/03_imports/prompts/invalid_duplicates/duplicate_names.prompt
````
workflow DuplicateGreeting: "Duplicate Greeting"
    "Say hello once."


workflow DuplicateGreeting: "Duplicate Greeting Again"
    "Say hello twice."
````

## File: examples/03_imports/prompts/simple/nested/polite.prompt
````
workflow PoliteGreeting: "Polite Greeting"
    "Say hello politely and keep the tone warm."
````

## File: examples/03_imports/prompts/simple/greeting.prompt
````
workflow Greeting: "Greeting"
    "Say hello."
````

## File: examples/03_imports/prompts/simple/object.prompt
````
workflow Object: "Object"
    "Say world."
````

## File: examples/03_imports/prompts/INVALID_DUPLICATE_DECLARATION.prompt
````
import invalid_duplicates.duplicate_names


agent DuplicateDeclarationDemo:
    role: "You are the duplicate declaration demonstration agent."

    workflow: "Imported Steps"
        "This example should fail before rendering."

        use duplicate_greeting: invalid_duplicates.duplicate_names.DuplicateGreeting
````

## File: examples/03_imports/prompts/INVALID_IMPORTED_PARSE.prompt
````
import simple.greeting
import broken.syntax


agent ImportedParseFailureDemo:
    role: "You are the imported parse failure demonstration agent."

    workflow: "Imported Steps"
        "This example should fail while loading an imported module."

        use greeting: simple.greeting.Greeting
````

## File: examples/03_imports/prompts/INVALID_MISSING_MODULE.prompt
````
import simple.greeting
import simple.missing


agent MissingModuleDemo:
    role: "You are the missing module demonstration agent."

    workflow: "Imported Steps"
        "This example should fail before rendering."

        use greeting: simple.greeting.Greeting
````

## File: examples/03_imports/prompts/INVALID_UNRESOLVED_SYMBOL.prompt
````
import simple.greeting


agent UnresolvedImportedSymbolDemo:
    role: "You are the unresolved symbol demonstration agent."

    workflow: "Imported Steps"
        "This example should fail before rendering."

        use missing_greeting: simple.greeting.MissingGreeting
````

## File: examples/04_inheritance/prompts/shared/greeters.prompt
````
abstract agent BaseGreeter:
    role: "You are the base greeter."

    workflow: "Shared Instructions"
        "Use the shared greeting below."

        greeting: "Greeting"
            "Say hello."

        object: "Object"
            "Say world."


# This agent stays abstract because concrete leaf agents inherit from it.
# It adds shared doctrine that imported children can still reuse directly.
abstract agent PoliteGreeter[BaseGreeter]:
    role: "You are the polite greeter."

    workflow: "Shared Instructions"
        inherit greeting
        inherit object

        courtesy: "Courtesy"
            "Keep the tone warm and direct."
````

## File: examples/04_inheritance/prompts/shared/workflows.prompt
````
workflow BaseGreeting: "Shared Instructions"
    "Use the shared greeting below."

    greeting: "Greeting"
        "Say hello."

    object: "Object"
        "Say world."
````

## File: examples/04_inheritance/ref/hello_world_greeter/AGENTS.md
````markdown
You are the hello world greeter.

## Hello World Instructions

### Greeting

Say hello.

### Courtesy

Keep the tone warm and direct.

### Object

Say world.
````

## File: examples/04_inheritance/ref/imported_workflow_greeter/AGENTS.md
````markdown
You are the imported workflow greeter.

## Imported Workflow Instructions

This workflow inherits its structure from an imported parent.

### Greeting

Say hello.

### Courtesy

Keep the tone warm and direct.

### Object

Say imported world.
````

## File: examples/04_inheritance/ref/inheritance_demo/AGENTS.md
````markdown
You are the inheritance demonstration agent.

## Inherited Steps

Follow the inherited steps below.
This child keeps the shared greeting and replaces the final step.

### Greeting

Say hello.

### Courtesy

Keep the tone warm and direct.

### Object

Say inherited world.
````

## File: examples/05_workflow_merge/prompts/INVALID_MISSING_INHERITED_ENTRY.prompt
````
abstract agent BaseBriefingAgent:
    role: "You are the base briefing agent."

    workflow: "Briefing"
        opening: "Opening"
            "State the topic."

        main_point: "Main Point"
            "Give the original main point."

        closing: "Closing"
            "Wrap up the briefing."


agent MissingInheritedEntryBriefingAgent[BaseBriefingAgent]:
    role: "You are the missing inherited entry briefing agent."

    workflow: "Briefing"
        inherit opening

        override main_point:
            "Give the revised main point."
````

## File: examples/06_nested_workflows/ref/inherited_structured_briefing_agent/AGENTS.md
````markdown
You are the inherited structured briefing agent.

## Inherited Revised Briefing

This file inherits the outer briefing structure.
It keeps preparation and replaces delivery through outer workflow inheritance.

### Preparation

Start with the topic and the audience before you deliver the briefing.

#### Topic

State the topic in one line.

#### Audience

Name who the briefing is for.

### Delivery

Move through the briefing in the revised sequence.

#### Opening

State the situation.

#### Context Note

Add one sentence of missing context before the main point.

#### Main Point

Give the revised main point directly.

#### Closing

End with the next step.
````

## File: examples/06_nested_workflows/ref/inline_briefing_agent/AGENTS.md
````markdown
You are the inline briefing agent.

## Briefing

Deliver the briefing in the order below.

### Opening

State the topic.

### Main Point

Give the main point directly.

### Closing

End with the next step.
````

## File: examples/06_nested_workflows/ref/revised_structured_briefing_agent/AGENTS.md
````markdown
You are the revised structured briefing agent.

## Revised Briefing

This file is the runtime guide for a structured briefing.
This version keeps preparation and revises delivery through workflow reuse.

### Preparation

Start with the topic and the audience before you deliver the briefing.

#### Topic

State the topic in one line.

#### Audience

Name who the briefing is for.

### Delivery

Move through the briefing in the revised sequence.

#### Opening

State the situation.

#### Context Note

Add one sentence of missing context before the main point.

#### Main Point

Give the revised main point directly.

#### Closing

End with the next step.
````

## File: examples/06_nested_workflows/ref/structured_briefing_agent/AGENTS.md
````markdown
You are the structured briefing agent.

## Briefing

This file is the runtime guide for a structured briefing.

### Preparation

Start with the topic and the audience before you deliver the briefing.

#### Topic

State the topic in one line.

#### Audience

Name who the briefing is for.

### Delivery

Move through the briefing in a fixed sequence.

#### Opening

State the situation.

#### Main Point

Give the main point directly.

#### Closing

End with the next step.
````

## File: examples/06_nested_workflows/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "inline briefing agent renders flat local sections"
status = "active"
kind = "render_contract"
agent = "InlineBriefingAgent"
assertion = "exact_lines"
approx_ref = "ref/inline_briefing_agent/AGENTS.md"
expected_lines = [
  "You are the inline briefing agent.",
  "",
  "## Briefing",
  "",
  "Deliver the briefing in the order below.",
  "",
  "### Opening",
  "",
  "State the topic.",
  "",
  "### Main Point",
  "",
  "Give the main point directly.",
  "",
  "### Closing",
  "",
  "End with the next step.",
]

[[cases]]
name = "structured briefing agent composes named workflows"
status = "active"
kind = "render_contract"
agent = "StructuredBriefingAgent"
assertion = "exact_lines"
approx_ref = "ref/structured_briefing_agent/AGENTS.md"
expected_lines = [
  "You are the structured briefing agent.",
  "",
  "## Briefing",
  "",
  "This file is the runtime guide for a structured briefing.",
  "",
  "### Preparation",
  "",
  "Start with the topic and the audience before you deliver the briefing.",
  "",
  "#### Topic",
  "",
  "State the topic in one line.",
  "",
  "#### Audience",
  "",
  "Name who the briefing is for.",
  "",
  "### Delivery",
  "",
  "Move through the briefing in a fixed sequence.",
  "",
  "#### Opening",
  "",
  "State the situation.",
  "",
  "#### Main Point",
  "",
  "Give the main point directly.",
  "",
  "#### Closing",
  "",
  "End with the next step.",
]

[[cases]]
name = "revised structured briefing agent retargets delivery through workflow reuse"
status = "active"
kind = "render_contract"
agent = "RevisedStructuredBriefingAgent"
assertion = "exact_lines"
approx_ref = "ref/revised_structured_briefing_agent/AGENTS.md"
expected_lines = [
  "You are the revised structured briefing agent.",
  "",
  "## Revised Briefing",
  "",
  "This file is the runtime guide for a structured briefing.",
  "This version keeps preparation and revises delivery through workflow reuse.",
  "",
  "### Preparation",
  "",
  "Start with the topic and the audience before you deliver the briefing.",
  "",
  "#### Topic",
  "",
  "State the topic in one line.",
  "",
  "#### Audience",
  "",
  "Name who the briefing is for.",
  "",
  "### Delivery",
  "",
  "Move through the briefing in the revised sequence.",
  "",
  "#### Opening",
  "",
  "State the situation.",
  "",
  "#### Context Note",
  "",
  "Add one sentence of missing context before the main point.",
  "",
  "#### Main Point",
  "",
  "Give the revised main point directly.",
  "",
  "#### Closing",
  "",
  "End with the next step.",
]

[[cases]]
name = "inherited structured briefing agent patches outer composition keys"
status = "active"
kind = "render_contract"
agent = "InheritedStructuredBriefingAgent"
assertion = "exact_lines"
approx_ref = "ref/inherited_structured_briefing_agent/AGENTS.md"
expected_lines = [
  "You are the inherited structured briefing agent.",
  "",
  "## Inherited Revised Briefing",
  "",
  "This file inherits the outer briefing structure.",
  "It keeps preparation and replaces delivery through outer workflow inheritance.",
  "",
  "### Preparation",
  "",
  "Start with the topic and the audience before you deliver the briefing.",
  "",
  "#### Topic",
  "",
  "State the topic in one line.",
  "",
  "#### Audience",
  "",
  "Name who the briefing is for.",
  "",
  "### Delivery",
  "",
  "Move through the briefing in the revised sequence.",
  "",
  "#### Opening",
  "",
  "State the situation.",
  "",
  "#### Context Note",
  "",
  "Add one sentence of missing context before the main point.",
  "",
  "#### Main Point",
  "",
  "Give the revised main point directly.",
  "",
  "#### Closing",
  "",
  "End with the next step.",
]
````

## File: examples/07_handoffs/build_ref/project_lead/AGENTS.md
````markdown
Core job: start the work, route it to Research Specialist, and take it back after Writing Specialist finishes.

## Your Job

Start the issue with a clear route.
Route the first owner change.
Keep the issue on a truthful route when work is blocked or routing goes stale.
Take the issue back after the final specialist return and close it out honestly.

## Read First

Start by reading Your Job.
Then read Workflow Core.

## Workflow Core

This file is the runtime guide for a simple multi-agent routing pattern.

### Same-Issue Workflow

Keep the whole job on one issue from setup through final return.
Keep one owner at a time on that issue.
The normal order is Project Lead -> Research Specialist -> Writing Specialist -> Project Lead.
Route the first owner change to Research Specialist.
After Research Specialist, the next owner is Writing Specialist.
After Writing Specialist, the next owner is Project Lead.
If the route is broken or the work is blocked before specialist work begins, keep or return the work to Project Lead.

### Next Owner

When ready to start the work -> ResearchSpecialist
If the route is broken or the work is blocked before specialist work begins -> ProjectLead

### Owner Change Comment

Every owner-change comment should say:
- what this turn changed
- the next owner when ownership is changing now
- the exact blocker when the issue is blocked
````

## File: examples/07_handoffs/build_ref/research_specialist/AGENTS.md
````markdown
Core job: do the research lane's work and route it to Writing Specialist.

## Your Job

Take the work only when Project Lead routes it to you.
Do the research lane's work.
Keep the work ready for the next lane.
Do not route the work anywhere except Writing Specialist or Project Lead.

## Read First

Read Your Job first. Then read Workflow Core.

## Workflow Core

### Same-Issue Workflow

Keep the work on the same issue.
Do only this lane's job.
Route to the next owner only when the current lane is honestly ready.
If the work is blocked or the route is unclear, return it to Project Lead.

### Next Owner

When ready -> WritingSpecialist
If blocked or the route is unclear -> ProjectLead

### Owner Change Comment

Every owner-change comment should say:
- what changed
- what the next owner should use now
- the next owner when ownership is changing now
````

## File: examples/07_handoffs/build_ref/writing_specialist/AGENTS.md
````markdown
Core job: do the writing lane's work and route it back to Project Lead.

## Your Job

Take the work only when Research Specialist hands it to you.
Do the writing lane's work.
Keep the work within the scope already set upstream.
Route the work back to Project Lead when the lane is complete or blocked.

## Read First

Read Your Job first. Then read Workflow Core.

## Workflow Core

### Same-Issue Workflow

Keep the work on the same issue.
Do only this lane's job.
Route to the next owner only when the current lane is honestly ready.
If the work is blocked or the route is unclear, return it to Project Lead.

### Next Owner

When ready -> ProjectLead
If blocked or the route is unclear -> ProjectLead

### Owner Change Comment

Every owner-change comment should say:
- what changed
- what the next owner should use now
- the next owner when ownership is changing now
````

## File: examples/07_handoffs/prompts/INVALID_REFERENCED_SLOT_WITH_INLINE_BODY.prompt
````
workflow ReadFirst: "Read First"
    "Read Your Job first. Then read Workflow Core."


abstract agent SameIssueRole:
    read_first: ReadFirst


agent BrokenRole[SameIssueRole]:
    role: "Core job: exercise the invalid authored-slot parse path."

    override read_first: ReadFirst
        "This inline body is invalid because the slot already references a named workflow."
````

## File: examples/08_inputs/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "custom input source renders typed source config"
status = "active"
kind = "render_contract"
agent = "CustomSourceInputAgent"
assertion = "exact_lines"
expected_lines = [
  "Core job: use a design spec from a custom typed input source.",
  "",
  "## Your Job",
  "",
  "Use the custom source configuration to find the design document.",
  "Fail if the required design source data is missing.",
  "",
  "## Inputs",
  "",
  "### Design Spec",
  "",
  "- Source: Figma Document",
  "- URL: `https://figma.com/design/abc123/Example-Design`",
  "- Node: `12:34`",
  "- Shape: Design Document",
  "- Requirement: Required",
  "",
  "Use this design document when the turn depends on a specific Figma source.",
]
````

## File: examples/09_outputs/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "multi-file output contract renders typed file surfaces"
status = "active"
kind = "render_contract"
agent = "JsonFileOutputAgent"
assertion = "exact_lines"
expected_lines = [
  "Core job: write the lesson manifest as structured JSON.",
  "",
  "## Your Job",
  "",
  "Write the lesson manifest JSON to the required file.",
  "",
  "## Outputs",
  "",
  "### Lesson Manifest Output",
  "",
  "- Built Lesson: `lesson_root/_authoring/lesson_manifest.json`",
  "- Built Lesson Shape: Lesson Manifest JSON",
  "- Validation File: `lesson_root/_authoring/MANIFEST_VALIDATION.md`",
  "- Validation File Shape: Markdown Document",
  "",
  "#### Must Include",
  "",
  "##### Built Lesson",
  "",
  "The built lesson in lesson_manifest.json.",
  "",
  "##### Route Choice",
  "",
  "In MANIFEST_VALIDATION.md, name the route chosen for each step.",
  "",
  "##### Validation Record",
  "",
  "In MANIFEST_VALIDATION.md, name the exact validation command or commands that ran and what passed or failed.",
  "",
  "##### Placeholder Copy Status",
  "",
  "In MANIFEST_VALIDATION.md, say whether placeholder copy is still present.",
  "",
  "#### Support Files",
  "",
  "##### GUIDED_WALKTHROUGH_LENGTH_REPORT.md",
  "",
  "- Path: `lesson_root/GUIDED_WALKTHROUGH_LENGTH_REPORT.md`",
  "- When: `Guided-walkthrough pacing is in scope.`",
  "",
  "#### Standalone Read",
  "",
  "A downstream role should be able to read lesson_manifest.json and MANIFEST_VALIDATION.md and understand what was built and what was validated.",
  "",
  "#### Notes",
  "",
  "Interpret `lesson_root/...` from the current work context and surrounding instructions.",
  "This example keeps that interpretation as explained guidance, not as a separate root primitive.",
  "Keep validator command details, validator output, and placeholder-copy status in MANIFEST_VALIDATION.md unless a modeled support file truly owns them.",
]
````

## File: examples/10_routing_and_stop_rules/prompts/AGENTS.prompt
````
# This example shows routing and stop rules through ordinary authored slots in
# the shipped subset.
# `output` says what the agent emits.
# The routing and stop sections say:
# - who owns next if the work is accepted
# - what happens if the work is not ready
# - when the turn is complete
# - when to stop and escalate instead of guessing
#
# This example stays intentionally narrow.
# It takes the repeated reviewer pattern from `99` and earns only:
# - a separate accepted path and not-ready path
# - explicit routes with `route "..." -> AgentName`
# - ordinary authored slots instead of a reserved turn-resolution field
# - a soft completion condition and a hard failure rule
#
# It does not try to model packets, proof files, or a full critic DSL.

input CurrentIssuePlan: "Current Issue Plan"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required
    "Use the current issue plan to understand the intended lane order."


input SectionDossier: "Section Dossier"
    source: File
        path: "section_root/_authoring/SECTION_DOSSIER.md"
    shape: MarkdownDocument
    requirement: Required
    "Review the current dossier before issuing a verdict."


output shape ReviewVerdictText: "Review Verdict Text"
    kind: PlainText


output ReviewVerdictResponse: "Review Verdict Response"
    target: TurnResponse
    shape: ReviewVerdictText
    requirement: Required

    must_include: "Must Include"
        verdict: "Verdict"
            "State `accept` or `changes requested` explicitly."

        next_owner: "Next Owner"
            "Name the honest next owner."

        reason: "Reason"
            "Give the short reason for the verdict and route."

    standalone_read: "Standalone Read"
        "A downstream reader should be able to read this response alone and understand the verdict and reroute."

    example: "Example"
        "- verdict: changes requested"
        "- next owner: SectionAuthor"
        "- reason: the dossier does not make the scope boundary explicit yet"


agent ProjectLead:
    role: "Core job: take the issue back when routing is unclear and keep the same-issue route honest."

    your_job: "Your Job"
        "Take the issue back when the right owner is unclear."
        "Repair the route honestly."


agent SectionAuthor:
    role: "Core job: revise the section dossier when review sends the work back."

    your_job: "Your Job"
        "Revise the dossier when review requests changes."


agent WritingSpecialist:
    role: "Core job: continue the next normal lane after the review is accepted."

    your_job: "Your Job"
        "Take the issue only after the review is accepted."
        "Continue the next normal lane."


agent AcceptanceReviewer:
    role: "Core job: review the current section dossier, return an explicit verdict, and route it honestly."

    your_job: "Your Job"
        "Review the section dossier against the current issue plan."
        "Return one explicit verdict."
        "Route the issue to the honest next owner."
        "Stop and escalate instead of guessing when required review inputs are missing."

    inputs: "Inputs"
        CurrentIssuePlan
        SectionDossier

    outputs: "Outputs"
        ReviewVerdictResponse

    routing: "Routing"
        next_owner_if_accepted: "Next Owner If Accepted"
            route "If accepted" -> WritingSpecialist

        if_the_work_is_not_ready: "If The Work Is Not Ready"
            route "If changes are required" -> SectionAuthor
            route "If the right owner is unclear" -> ProjectLead

    when_to_stop: "When To Stop"
        stop_here_if: "Stop Here If"
            "Stop when the verdict is explicit and the next owner is clear."

        hard_stop_rule: "Hard Stop Rule"
            "If the required dossier file is missing, stop and escalate."
            "Do not guess from stale notes or old packet copies."
````

## File: examples/10_routing_and_stop_rules/ref/acceptance_reviewer/AGENTS.md
````markdown
# Acceptance Reviewer

Core job: review the current section dossier, return an explicit verdict, and route it honestly.

## Your Job

- Review the section dossier against the current issue plan.
- Return one explicit verdict.
- Route the issue to the honest next owner.
- Stop and escalate instead of guessing when required review inputs are missing.

## Inputs

### Current Issue Plan

- Source: Prompt
- Shape: Markdown document
- Requirement: Required

Use the current issue plan to understand the intended lane order.

### Section Dossier

- Source: File
- Path: `section_root/_authoring/SECTION_DOSSIER.md`
- Shape: Markdown document
- Requirement: Required

Review the current dossier before issuing a verdict.

## Outputs

### Review Verdict Response

- Target: TurnResponse
- Shape: Review Verdict Text
- Requirement: Required

#### Must Include

- Verdict: state `accept` or `changes requested` explicitly.
- Next Owner: name the honest next owner.
- Reason: give the short reason for the verdict and route.

#### Standalone Read

A downstream reader should be able to read this response alone and understand the verdict and reroute.

#### Example

```text
- verdict: changes requested
- next owner: SectionAuthor
- reason: the dossier does not make the scope boundary explicit yet
```

## Routing

### Next Owner If Accepted

- If accepted -> WritingSpecialist

### If The Work Is Not Ready

- If changes are required -> SectionAuthor
- If the right owner is unclear -> ProjectLead

## When To Stop

### Stop Here If

Stop when the verdict is explicit and the next owner is clear.

### Hard Stop Rule

- If the required dossier file is missing, stop and escalate.
- Do not guess from stale notes or old packet copies.
````

## File: examples/10_routing_and_stop_rules/ref/project_lead/AGENTS.md
````markdown
# Project Lead

Core job: take the issue back when routing is unclear and keep the same-issue route honest.

## Your Job

- Take the issue back when the right owner is unclear.
- Repair the route honestly.
````

## File: examples/10_routing_and_stop_rules/ref/section_author/AGENTS.md
````markdown
# Section Author

Core job: revise the section dossier when review sends the work back.

## Your Job

- Revise the dossier when review requests changes.
````

## File: examples/10_routing_and_stop_rules/ref/writing_specialist/AGENTS.md
````markdown
# Writing Specialist

Core job: continue the next normal lane after the review is accepted.

## Your Job

- Take the issue only after the review is accepted.
- Continue the next normal lane.
````

## File: examples/10_routing_and_stop_rules/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "routing and stop rules render through ordinary authored slots"
status = "active"
kind = "render_contract"
agent = "AcceptanceReviewer"
assertion = "exact_lines"
expected_lines = [
  "Core job: review the current section dossier, return an explicit verdict, and route it honestly.",
  "",
  "## Your Job",
  "",
  "Review the section dossier against the current issue plan.",
  "Return one explicit verdict.",
  "Route the issue to the honest next owner.",
  "Stop and escalate instead of guessing when required review inputs are missing.",
  "",
  "## Inputs",
  "",
  "### Current Issue Plan",
  "",
  "- Source: Prompt",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "Use the current issue plan to understand the intended lane order.",
  "",
  "### Section Dossier",
  "",
  "- Source: File",
  "- Path: `section_root/_authoring/SECTION_DOSSIER.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "Review the current dossier before issuing a verdict.",
  "",
  "## Outputs",
  "",
  "### Review Verdict Response",
  "",
  "- Target: Turn Response",
  "- Shape: Review Verdict Text",
  "- Requirement: Required",
  "",
  "#### Must Include",
  "",
  "##### Verdict",
  "",
  "State `accept` or `changes requested` explicitly.",
  "",
  "##### Next Owner",
  "",
  "Name the honest next owner.",
  "",
  "##### Reason",
  "",
  "Give the short reason for the verdict and route.",
  "",
  "#### Standalone Read",
  "",
  "A downstream reader should be able to read this response alone and understand the verdict and reroute.",
  "",
  "#### Example",
  "",
  "- verdict: changes requested",
  "- next owner: SectionAuthor",
  "- reason: the dossier does not make the scope boundary explicit yet",
  "",
  "## Routing",
  "",
  "### Next Owner If Accepted",
  "",
  "If accepted -> WritingSpecialist",
  "",
  "### If The Work Is Not Ready",
  "",
  "If changes are required -> SectionAuthor",
  "If the right owner is unclear -> ProjectLead",
  "",
  "## When To Stop",
  "",
  "### Stop Here If",
  "",
  "Stop when the verdict is explicit and the next owner is clear.",
  "",
  "### Hard Stop Rule",
  "",
  "If the required dossier file is missing, stop and escalate.",
  "Do not guess from stale notes or old packet copies.",
]
````

## File: examples/13_critic_protocol/ref/project_lead/AGENTS.md
````markdown
# Project Lead

Core job: take the issue back when routing is unclear or when accepted work needs the next normal owner.

## Your Job

- Take the issue back when the critic says the route is unclear.
- Own the next normal lane after accepted review.
````

## File: examples/13_critic_protocol/ref/section_author/AGENTS.md
````markdown
# Section Author

Core job: revise the dossier when critic review sends the work back.

## Your Job

- Revise the dossier and validation record when the critic requests changes.
````

## File: examples/14_handoff_truth/build_ref/acceptance_critic/AGENTS.md
````markdown
Core job: review the exact current dossier and validation record named in the handoff.

## Your Job

Read the exact files named in the handoff.
Review only the current dossier and validation record for this turn.
````

## File: examples/14_handoff_truth/build_ref/project_lead/AGENTS.md
````markdown
Core job: take the issue back when the route is unclear or the current brief is missing.

## Your Job

Repair the route honestly.
Restore the missing current input before rerouting the work.
````

## File: examples/14_handoff_truth/prompts/contracts/inputs.prompt
````
input CurrentIssuePlan: "Current Issue Plan"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required
    "Use the current issue plan to understand the intended lane and current scope."


input SectionBrief: "Section Brief"
    source: File
        path: "section_root/_authoring/BRIEF.md"
    shape: MarkdownDocument
    requirement: Required
    "Use the current brief as the upstream scope for this turn."


input PriorReviewNotes: "Prior Review Notes"
    source: File
        path: "section_root/_authoring/PRIOR_REVIEW_NOTES.md"
    shape: MarkdownDocument
    requirement: Advisory
    "Use this only for continuity when it exists."
    "Do not treat it as proof of the current turn."
````

## File: examples/14_handoff_truth/prompts/contracts/outputs.prompt
````
output target IssueComment: "Issue Comment"
    required: "Required Target Keys"
        issue: "Issue"


output shape HandoffCommentText: "Handoff Comment Text"
    kind: CommentText


output SectionDossierOutput: "Section Dossier Output"
    files: "Files"
        current_dossier: "Current Dossier"
            path: "section_root/_authoring/SECTION_DOSSIER.md"
            shape: MarkdownDocument

        validation_record: "Validation Record"
            path: "section_root/_authoring/DOSSIER_VALIDATION.md"
            shape: MarkdownDocument

    requirement: Required

    must_include: "Must Include"
        current_dossier: "Current Dossier"
            "SECTION_DOSSIER.md must reflect the current section proposal for this turn."

        validation_record: "Validation Record"
            "DOSSIER_VALIDATION.md must say what checks ran, what passed or failed, or what did not run yet."

    standalone_read: "Standalone Read"
        "A downstream reader should be able to read SECTION_DOSSIER.md and DOSSIER_VALIDATION.md and understand the current proposal and its validation basis."


output SectionAuthorHandoff: "Section Author Handoff"
    target: IssueComment
        issue: "CURRENT_ISSUE"
    shape: HandoffCommentText
    requirement: Required

    must_include: "Must Include"
        what_changed: "What Changed"
            "Say what changed in this turn."

        use_now: "Use Now"
            "Name the exact current files the next owner should read now."

        review_files: "Review Files"
            "Either name the current review files explicitly or say plainly that no current review files apply yet."

        next_owner: "Next Owner"
            "Name the honest next owner."

    standalone_read: "Standalone Read"
        "A downstream reader should be able to read this comment alone and understand what changed, which files are current now, whether review files apply, and who owns next."

    example: "Example"
        "- changed: rewrote the dossier scope and added the validation record"
        "- use now: SECTION_DOSSIER.md and DOSSIER_VALIDATION.md"
        "- review files: no current review files apply yet"
        "- next owner: AcceptanceCritic"
````

## File: examples/14_handoff_truth/prompts/roles/acceptance_critic.prompt
````
workflow AcceptanceCriticJob: "Your Job"
    "Read the exact files named in the handoff."
    "Review only the current dossier and validation record for this turn."
````

## File: examples/14_handoff_truth/prompts/roles/project_lead.prompt
````
workflow ProjectLeadJob: "Your Job"
    "Repair the route honestly."
    "Restore the missing current input before rerouting the work."
````

## File: examples/14_handoff_truth/prompts/roles/section_author.prompt
````
workflow SectionAuthorJob: "Your Job"
    "Read the current issue plan and current brief before you write."
    "Use prior review notes only as continuity help, not as proof."
    "Write the current dossier and current validation record."
    "Leave one handoff comment that names the exact files to use now."
    "Say plainly whether current review files apply yet."
    "Route the issue to the honest next owner."
````

## File: examples/14_handoff_truth/ref/acceptance_critic/AGENTS.md
````markdown
# Acceptance Critic

Core job: review the exact current dossier and validation record named in the handoff.

## Your Job

- Read the exact files named in the handoff.
- Review only the current dossier and validation record for this turn.
````

## File: examples/14_handoff_truth/ref/project_lead/AGENTS.md
````markdown
# Project Lead

Core job: take the issue back when the route is unclear or the current brief is missing.

## Your Job

- Repair the route honestly.
- Restore the missing current input before rerouting the work.
````

## File: examples/15_workflow_body_refs/prompts/shared/contracts.prompt
````
input CurrentIssuePlan: "Current Issue Plan"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required
    "Use the current issue plan to confirm the intended owner and next step."


input TrackMetadata: "Track Metadata"
    source: File
        path: "track_root/track.meta.json"
    shape: JsonObject
    requirement: Required
    "Use this file as the current track metadata truth."
````

## File: examples/15_workflow_body_refs/prompts/AGENTS.prompt
````
# This example adds one narrow workflow-body feature:
# titled workflow sections can mix prose strings with named declaration refs.
#
# Use this when the workflow needs to point at typed declarations without
# restating their path, shape, or requirement inline.
#
# The workflow section keeps read order and usage guidance readable.
# The declaration itself still owns the full contract truth.
# Bare refs in workflow sections render as bullets using the declaration title.
# Imported dotted refs work here too.
# Workflow reuse still belongs to `use`, not to bare workflow refs.

import shared.contracts


workflow ImmediateLocalRead: "Immediate Local Read"
    read_now: "Read Now"
        "Start with the current routing truth."
        shared.contracts.CurrentIssuePlan
        LatestNamedFilesComment
        shared.contracts.TrackMetadata
        "If current concepts exist for this section, read them before nearby context."
        CurrentConcepts

    when_you_finish: "When You Finish"
        "Leave the next owner one current output contract instead of a vague note."
        FinalHandoffComment


input LatestNamedFilesComment: "Latest Named Files Comment"
    source: File
        path: "track_root/_authoring/LATEST_NAMED_FILES_COMMENT.md"
    shape: MarkdownDocument
    requirement: Required
    "Use this comment to confirm which files are current now."


input CurrentConcepts: "Current Concepts"
    source: File
        path: "section_root/_authoring/CONCEPTS.md"
    shape: MarkdownDocument
    requirement: Advisory
    "Use this only when the section already has live concepts to preserve."


output FinalHandoffComment: "Final Handoff Comment"
    target: TurnResponse
    shape: MarkdownDocument
    requirement: Required
    "Use this output contract when you leave the next owner one clear update."


agent WorkflowSectionRefsDemo:
    role: "Keep workflow guidance readable while still pointing directly at the typed contracts it depends on."

    read_first: ImmediateLocalRead

    inputs: "Inputs"
        shared.contracts.CurrentIssuePlan
        LatestNamedFilesComment
        shared.contracts.TrackMetadata
        CurrentConcepts

    outputs: "Outputs"
        FinalHandoffComment
````

## File: examples/15_workflow_body_refs/prompts/INVALID_AMBIGUOUS_REF.prompt
````
# Bare workflow section refs must resolve to exactly one allowed declaration
# family. If a name matches more than one allowed declaration kind, fail loud.

input SharedThing: "Shared Thing Input"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required


skill SharedThing: "Shared Thing Skill"
    purpose: "Prove that ambiguous bare workflow section refs fail loud."


workflow InvalidAmbiguousBodyRefs: "Invalid Ambiguous Body Refs"
    bad: "Bad"
        SharedThing


agent InvalidAmbiguousBodyRefsAgent:
    role: "This agent exists only to trigger the compile-fail contract."

    read_first: InvalidAmbiguousBodyRefs
````

## File: examples/15_workflow_body_refs/prompts/INVALID_WORKFLOW_REF.prompt
````
# Bare workflow refs are intentionally not allowed inside titled workflow
# sections. Use `use` when a workflow needs to compose another workflow.

workflow SharedRead: "Shared Read"
    first: "First"
        "Read this first."


workflow InvalidWorkflowBodyRefs: "Invalid Workflow Body Refs"
    bad: "Bad"
        SharedRead


agent InvalidWorkflowBodyRefsAgent:
    role: "This agent exists only to trigger the compile-fail contract."

    read_first: InvalidWorkflowBodyRefs
````

## File: examples/15_workflow_body_refs/ref/workflow_section_refs_demo/AGENTS.md
````markdown
Keep workflow guidance readable while still pointing directly at the typed contracts it depends on.

## Immediate Local Read

### Read Now

Start with the current routing truth.

- Current Issue Plan
- Latest Named Files Comment
- Track Metadata

If current concepts exist for this section, read them before nearby context.

- Current Concepts

### When You Finish

Leave the next owner one current output contract instead of a vague note.

- Final Handoff Comment

## Inputs

### Current Issue Plan

- Source: Prompt
- Shape: Markdown Document
- Requirement: Required

Use the current issue plan to confirm the intended owner and next step.

### Latest Named Files Comment

- Source: File
- Path: `track_root/_authoring/LATEST_NAMED_FILES_COMMENT.md`
- Shape: Markdown Document
- Requirement: Required

Use this comment to confirm which files are current now.

### Track Metadata

- Source: File
- Path: `track_root/track.meta.json`
- Shape: Json Object
- Requirement: Required

Use this file as the current track metadata truth.

### Current Concepts

- Source: File
- Path: `section_root/_authoring/CONCEPTS.md`
- Shape: Markdown Document
- Requirement: Advisory

Use this only when the section already has live concepts to preserve.

## Outputs

### Final Handoff Comment

- Target: Turn Response
- Shape: Markdown Document
- Requirement: Required

Use this output contract when you leave the next owner one clear update.
````

## File: examples/16_workflow_string_interpolation/prompts/shared/contracts.prompt
````
input CurrentIssuePlan: "Current Issue Plan"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required
    "Use the current issue plan to confirm the intended owner and next step."


input TrackMetadata: "Track Metadata"
    source: File
        path: "track_root/track.meta.json"
    shape: JsonObject
    requirement: Required
    "Use this file as the current track metadata truth."
````

## File: examples/16_workflow_string_interpolation/prompts/AGENTS.prompt
````
# This example adds one narrow workflow-string feature:
# workflow strings can interpolate named declaration data inline with `{{...}}`.
#
# Use this when the workflow needs one natural sentence instead of a block list.
# Keep `15_workflow_body_refs` for list-style mention sections.
# The declaration still owns the full typed contract truth.
#
# `{{Ref}}` renders the declaration title.
# `{{Ref:field.path}}` resolves one scalar field from the declaration contract.
# The author still owns punctuation, filenames, and backticks around placeholders.

import shared.contracts


workflow ImmediateLocalRead: "Immediate Local Read"
    read_now: "Read Now"
        "Read the current issue, the current Issue Plan And Route, the latest issue comment that names the current files, track.meta.json at `{{shared.contracts.TrackMetadata:source.path}}`, any current CONCEPTS.md at `{{CurrentConcepts:source.path}}`, and nearby section context only as support evidence to re-earn."

    handoff_shape: "Handoff Shape"
        "When you stop, leave one {{FinalHandoffComment}} through {{FinalHandoffComment:target.title}}."


input CurrentConcepts: "Current Concepts"
    source: File
        path: "section_root/_authoring/CONCEPTS.md"
    shape: MarkdownDocument
    requirement: Advisory
    "Use this only when the section already has live concepts to preserve."


output FinalHandoffComment: "Final Handoff Comment"
    target: TurnResponse
    shape: MarkdownDocument
    requirement: Required
    "Use this output contract when you leave the next owner one clear update."


agent WorkflowStringInterpolationDemo:
    role: "Keep one workflow sentence readable while still pulling the typed contract truth from named declarations."

    read_first: ImmediateLocalRead

    inputs: "Inputs"
        shared.contracts.CurrentIssuePlan
        shared.contracts.TrackMetadata
        CurrentConcepts

    outputs: "Outputs"
        FinalHandoffComment
````

## File: examples/16_workflow_string_interpolation/prompts/INVALID_AMBIGUOUS_INTERPOLATION.prompt
````
# Inline workflow interpolation must resolve one allowed declaration family.
# If a local bare ref matches more than one allowed declaration kind, fail loud.

input SharedThing: "Shared Thing Input"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required


skill SharedThing: "Shared Thing Skill"
    purpose: "Prove that ambiguous workflow-string refs fail loud."


workflow InvalidAmbiguousInterpolation: "Invalid Ambiguous Interpolation"
    bad: "Bad"
        "Read {{SharedThing:title}} before you continue."


agent InvalidAmbiguousInterpolationAgent:
    role: "This agent exists only to trigger the compile-fail contract."

    read_first: InvalidAmbiguousInterpolation
````

## File: examples/16_workflow_string_interpolation/prompts/INVALID_FIELD_PATH.prompt
````
# Inline workflow interpolation should fail loud when the field path does not
# resolve to a real scalar contract field.

import shared.contracts


workflow InvalidFieldPathInterpolation: "Invalid Field Path Interpolation"
    bad: "Bad"
        "Read `{{shared.contracts.TrackMetadata:source.missing}}` before you continue."


agent InvalidFieldPathInterpolationAgent:
    role: "This agent exists only to trigger the compile-fail contract."

    read_first: InvalidFieldPathInterpolation
````

## File: examples/16_workflow_string_interpolation/prompts/INVALID_WORKFLOW_INTERPOLATION.prompt
````
# Workflow refs are intentionally not valid inside workflow-string interpolation.
# Use `use` when a workflow needs to compose another workflow.

workflow SharedRead: "Shared Read"
    first: "First"
        "Read this first."


workflow InvalidWorkflowStringInterpolation: "Invalid Workflow String Interpolation"
    bad: "Bad"
        "Read {{SharedRead}} before you continue."


agent InvalidWorkflowStringInterpolationAgent:
    role: "This agent exists only to trigger the compile-fail contract."

    read_first: InvalidWorkflowStringInterpolation
````

## File: examples/16_workflow_string_interpolation/ref/workflow_string_interpolation_demo/AGENTS.md
````markdown
Keep one workflow sentence readable while still pulling the typed contract truth from named declarations.

## Immediate Local Read

### Read Now

Read the current issue, the current Issue Plan And Route, the latest issue comment that names the current files, track.meta.json at `track_root/track.meta.json`, any current CONCEPTS.md at `section_root/_authoring/CONCEPTS.md`, and nearby section context only as support evidence to re-earn.

### Handoff Shape

When you stop, leave one Final Handoff Comment through Turn Response.

## Inputs

### Current Issue Plan

- Source: Prompt
- Shape: Markdown Document
- Requirement: Required

Use the current issue plan to confirm the intended owner and next step.

### Track Metadata

- Source: File
- Path: `track_root/track.meta.json`
- Shape: Json Object
- Requirement: Required

Use this file as the current track metadata truth.

### Current Concepts

- Source: File
- Path: `section_root/_authoring/CONCEPTS.md`
- Shape: Markdown Document
- Requirement: Advisory

Use this only when the section already has live concepts to preserve.

## Outputs

### Final Handoff Comment

- Target: Turn Response
- Shape: Markdown Document
- Requirement: Required

Use this output contract when you leave the next owner one clear update.
````

## File: examples/17_agent_mentions/prompts/shared/roles.prompt
````
# Shared owner roles for imported agent-mention examples.

abstract agent AbstractEscalationOwner:
    role: "This abstract owner exists only to prove that abstract agent mentions fail loud."


agent AcceptanceCritic:
    role: "Review the exact current files and return one honest verdict."
````

## File: examples/17_agent_mentions/prompts/AGENTS.prompt
````
# This example extends the existing workflow-mention surfaces one narrow step:
# concrete agents can now be mentioned in workflow prose and as block refs.
#
# Use this when the workflow needs to name a current owner without turning
# that sentence into a route line.
# `route` still owns actual owner transitions.
# `{{AgentRef}}` and `{{AgentRef:name}}` render the raw agent declaration name.
# Bare agent refs in titled workflow sections also render as raw-name bullets.

import shared.roles


workflow HandoffMentions: "Handoff Mentions"
    owner_names_in_prose: "Owner Names In Prose"
        "If the route is unclear, return the same issue to {{ProjectLead}}."
        "If the work is ready for review, hand it to {{shared.roles.AcceptanceCritic:name}}."

    owner_names_as_block_mentions: "Owner Names As Block Mentions"
        ProjectLead
        shared.roles.AcceptanceCritic

    actual_transition: "Actual Transition"
        "Naming an owner is not a route by itself."
        route "If the work is ready for review" -> shared.roles.AcceptanceCritic


agent ProjectLead:
    role: "Own route repair when the next owner is unclear."


agent AgentMentionsDemo:
    role: "Keep owner names readable in workflow prose without pretending that a mention is a route."

    read_first: HandoffMentions
````

## File: examples/17_agent_mentions/prompts/INVALID_ABSTRACT_AGENT_MENTION.prompt
````
import shared.roles


workflow InvalidAbstractAgentMention: "Invalid Abstract Agent Mention"
    owner_names: "Owner Names"
        "Do not materialize {{shared.roles.AbstractEscalationOwner}} as a current owner."


agent InvalidAbstractAgentMentionDemo:
    role: "This prompt exists only to prove that abstract agent mentions fail loud."

    read_first: InvalidAbstractAgentMention
````

## File: examples/17_agent_mentions/prompts/INVALID_AMBIGUOUS_AGENT_REF.prompt
````
workflow InvalidAmbiguousAgentRef: "Invalid Ambiguous Agent Ref"
    owner_names: "Owner Names"
        SharedThing


input SharedThing: "Shared Thing"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required
    "This input creates a deliberate bare-name collision."


agent SharedThing:
    role: "This agent creates the other side of the deliberate bare-name collision."


agent InvalidAmbiguousAgentMentionDemo:
    role: "This prompt exists only to prove that ambiguous agent mentions fail loud."

    read_first: InvalidAmbiguousAgentRef
````

## File: examples/17_agent_mentions/prompts/INVALID_WORKFLOW_MENTION.prompt
````
workflow SharedRead: "Shared Read"
    "Read this first."


workflow InvalidWorkflowMention: "Invalid Workflow Mention"
    owner_names: "Owner Names"
        "Do not use {{SharedRead}} as if a workflow were a materialized owner mention."


agent InvalidWorkflowMentionDemo:
    role: "This prompt exists only to prove that workflow mentions stay rejected."

    read_first: InvalidWorkflowMention
````

## File: examples/17_agent_mentions/ref/agent_mentions_demo/AGENTS.md
````markdown
Keep owner names readable in workflow prose without pretending that a mention is a route.

## Handoff Mentions

### Owner Names In Prose

If the route is unclear, return the same issue to ProjectLead.
If the work is ready for review, hand it to AcceptanceCritic.

### Owner Names As Block Mentions

- ProjectLead
- AcceptanceCritic

### Actual Transition

Naming an owner is not a route by itself.
If the work is ready for review -> AcceptanceCritic
````

## File: examples/18_rich_io_buckets/prompts/AGENTS.prompt
````
# This example shows rich `inputs` and `outputs` buckets.
# - They can mix plain prose, titled groups, and typed declaration refs.
# - Existing bare ref lists still work.
# - The typed refs stay kind-specific.

input CurrentSectionPlan: "Current Section Plan"
    source: File
        path: "section_root/_authoring/SECTION_PLAN.md"
    shape: "Markdown Document"
    requirement: Required

    notes: "Notes"
        "Treat the current plan as the live section baseline."


input PriorReviewNotes: "Prior Review Notes"
    source: File
        path: "section_root/_authoring/PRIOR_REVIEW_NOTES.md"
    shape: "Markdown Document"
    requirement: Advisory


output DossierFile: "Dossier File"
    target: File
        path: "section_root/_authoring/dossier_engineer.md"
    shape: "Dossier Document"
    requirement: Required

    standalone_read: "Standalone Read"
        "A downstream reader should be able to read dossier_engineer.md alone and understand the current dossier truth."


output DossierSummary: "Dossier Summary"
    target: TurnResponse
    shape: "Turn Summary Text"
    requirement: Required

    purpose: "Purpose"
        "Summarize what changed and point the reader at dossier_engineer.md."


agent RichIoBucketAgent:
    role: "Core job: gather the section inputs and publish the current dossier truth."

    your_job: "Your Job"
        "Use the current plan as truth and keep prior review notes as continuity help only."
        "Always write the dossier file before you summarize the turn."

    inputs: "Inputs"
        "Read these inputs in order."

        planning_truth: "Planning Truth"
            CurrentSectionPlan

        continuity_only: "Continuity Only"
            "Use prior review notes only as continuity help, not as proof."
            PriorReviewNotes

    outputs: "Outputs"
        "Always produce these outputs when you own dossier work."
        "The file artifact is the durable truth. The turn summary points at that truth."

        file_truth: "File Truth"
            "Write this to disk before you summarize the turn."
            DossierFile

        turn_summary: "Turn Summary"
            "Use the turn response to say what changed and where the durable file lives."
            DossierSummary
````

## File: examples/18_rich_io_buckets/prompts/INVALID_OUTPUT_BUCKET_REF_BODY.prompt
````
output DossierFile: "Dossier File"
    target: File
        path: "section_root/_authoring/dossier_engineer.md"
    shape: "Dossier Document"
    requirement: Required


agent InvalidOutputBucketRefBody:
    role: "Core job: trigger an invalid inline body on an output ref."

    outputs: "Outputs"
        DossierFile
            "This explanation belongs in prose or a titled group, not on the ref itself."
````

## File: examples/18_rich_io_buckets/prompts/INVALID_OUTPUT_BUCKET_ROUTE.prompt
````
output DossierFile: "Dossier File"
    target: File
        path: "section_root/_authoring/dossier_engineer.md"
    shape: "Dossier Document"
    requirement: Required


agent InvalidOutputBucketRoute:
    role: "Core job: trigger an invalid route line in outputs."

    outputs: "Outputs"
        route "Send next" -> ProjectLead
        DossierFile
````

## File: examples/18_rich_io_buckets/prompts/INVALID_OUTPUT_BUCKET_SCALAR.prompt
````
output DossierFile: "Dossier File"
    target: File
        path: "section_root/_authoring/dossier_engineer.md"
    shape: "Dossier Document"
    requirement: Required


agent InvalidOutputBucketScalar:
    role: "Core job: trigger an invalid scalar keyed item in outputs."

    outputs: "Outputs"
        notes: "Notes"
        DossierFile
````

## File: examples/18_rich_io_buckets/prompts/INVALID_OUTPUT_BUCKET_WRONG_KIND_REF.prompt
````
input CurrentSectionPlan: "Current Section Plan"
    source: File
        path: "section_root/_authoring/SECTION_PLAN.md"
    shape: "Markdown Document"
    requirement: Required


agent InvalidOutputBucketWrongKindRef:
    role: "Core job: trigger an input ref inside outputs."

    outputs: "Outputs"
        CurrentSectionPlan
````

## File: examples/18_rich_io_buckets/ref/rich_io_bucket_agent/AGENTS.md
````markdown
Core job: gather the section inputs and publish the current dossier truth.

## Your Job

Use the current plan as truth and keep prior review notes as continuity help only.
Always write the dossier file before you summarize the turn.

## Inputs

Read these inputs in order.

### Planning Truth

#### Current Section Plan

- Source: File
- Path: `section_root/_authoring/SECTION_PLAN.md`
- Shape: Markdown Document
- Requirement: Required

##### Notes

Treat the current plan as the live section baseline.

### Continuity Only

Use prior review notes only as continuity help, not as proof.

#### Prior Review Notes

- Source: File
- Path: `section_root/_authoring/PRIOR_REVIEW_NOTES.md`
- Shape: Markdown Document
- Requirement: Advisory

## Outputs

Always produce these outputs when you own dossier work.
The file artifact is the durable truth. The turn summary points at that truth.

### File Truth

Write this to disk before you summarize the turn.

#### Dossier File

- Target: File
- Path: `section_root/_authoring/dossier_engineer.md`
- Shape: Dossier Document
- Requirement: Required

##### Standalone Read

A downstream reader should be able to read dossier_engineer.md alone and understand the current dossier truth.

### Turn Summary

Use the turn response to say what changed and where the durable file lives.

#### Dossier Summary

- Target: Turn Response
- Shape: Turn Summary Text
- Requirement: Required

##### Purpose

Summarize what changed and point the reader at dossier_engineer.md.
````

## File: examples/19_emphasized_prose_lines/prompts/INVALID_PARSE_UNKNOWN_EMPHASIS.prompt
````
agent InvalidUnknownEmphasis:
    role: "Role"
        critical "This line should fail during parse."

    workflow: "Instructions"
        "This agent exists only to trigger the parse-fail contract."
````

## File: examples/19_emphasized_prose_lines/ref/AGENTS.md
````markdown
## Role

**REQUIRED**: Read this file end to end before you act.
**IMPORTANT**: Keep the current plan as truth.

## Instructions

**WARNING**: Start from Current Plan, not from memory.
**NOTE**: Treat old notes as continuity help only.

### Final Check

**REQUIRED**: Confirm the path at `track_root/current-plan.md` before you route.
**NOTE**: Do not guess from stale notes or old copies.

## Inputs

**IMPORTANT**: Read these inputs before you write anything.

### Current Plan

- Source: File
- Path: `track_root/current-plan.md`
- Shape: Markdown Document
- Requirement: Required

**NOTE**: Use this file as the current plan truth.
````

## File: examples/19_emphasized_prose_lines/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "emphasized prose lines render fixed labels across shipped prose surfaces"
status = "active"
kind = "render_contract"
agent = "EmphasizedProseLinesDemo"
assertion = "exact_lines"
approx_ref = "ref/AGENTS.md"
expected_lines = [
  "## Role",
  "",
  "**REQUIRED**: Read this file end to end before you act.",
  "**IMPORTANT**: Keep the current plan as truth.",
  "",
  "## Instructions",
  "",
  "**WARNING**: Start from Current Plan, not from memory.",
  "**NOTE**: Treat old notes as continuity help only.",
  "",
  "### Final Check",
  "",
  "**REQUIRED**: Confirm the path at `track_root/current-plan.md` before you route.",
  "**NOTE**: Do not guess from stale notes or old copies.",
  "",
  "## Inputs",
  "",
  "**IMPORTANT**: Read these inputs before you write anything.",
  "",
  "### Current Plan",
  "",
  "- Source: File",
  "- Path: `track_root/current-plan.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "**NOTE**: Use this file as the current plan truth.",
]

[[cases]]
name = "unsupported emphasis labels fail in parse stage"
status = "active"
kind = "parse_fail"
prompt = "prompts/INVALID_PARSE_UNKNOWN_EMPHASIS.prompt"
exception_type = "ParseError"
error_code = "E101"
message_contains = [
  "critical",
  "Expected one of",
]
````

## File: examples/20_authored_prose_interpolation/prompts/INVALID_AMBIGUOUS_RECORD_PROSE.prompt
````
input SharedThing: "Shared Thing Input"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required


skill SharedThing: "Shared Thing Skill"
    purpose: "Prove that ambiguous record-prose refs fail loud."


agent InvalidAmbiguousRecordProseDemo:
    role: "This prompt exists only to trigger the compile-fail contract."

    inputs: "Inputs"
        "Read {{SharedThing:title}} before you continue."
````

## File: examples/20_authored_prose_interpolation/prompts/INVALID_ROLE_FIELD_PATH.prompt
````
input CurrentPlan: "Current Plan"
    source: File
        path: "track_root/current-plan.md"
    shape: MarkdownDocument
    requirement: Required


agent InvalidRoleFieldPathInterpolationDemo:
    role: "Read `{{CurrentPlan:source.missing}}` before you continue."
````

## File: examples/20_authored_prose_interpolation/ref/AGENTS.md
````markdown
Use `track_root/current-plan.md` as the current plan truth before you act.

## Read First

### Start Here

Read Current Plan before you act.

## Inputs

Read Current Plan before you write.

### Planning Truth

Keep the current plan at `track_root/current-plan.md` in scope.

#### Current Plan

- Source: File
- Path: `track_root/current-plan.md`
- Shape: Markdown Document
- Requirement: Required

Use this as the current plan truth.

## Skills

### Can Run

#### Grounding Skill

##### Purpose

Ground new claims against Current Plan before you write.

##### Provides

Keep `track_root/current-plan.md` in scope when you cite current plan truth.

##### Reason

Ask ProjectLead for an owner decision only when the plan truly needs one.

## Outputs

### Turn Response

- Target: Turn Response
- Shape: Markdown Document
- Requirement: Required

Use this output when you leave the next owner one clear update.

## How To Route

### Routing Rules

Leave the next owner one Turn Response.
If ProjectLead must step in -> ProjectLead
````

## File: examples/21_first_class_skills_blocks/prompts/AGENTS.prompt
````
# This example promotes `skills` into a first-class block.
#
# A `skills` block can now be:
# - a top-level reusable declaration
# - referenced directly from an agent
# - referenced from a workflow
# - authored inline inside a workflow
#
# The rendered result should stay one clear skills section wherever it appears.

skill GroundingSkill: "Grounding Skill"
    purpose: "Ground the current claim before you write."


skill FindSkills: "Find Skills"
    purpose: "Find the right repo skill before you guess."


skills SharedSkills: "Skills And Tools"
    how_to_use: "How To Use"
        "Start with the skill that directly matches the current job."

    can_run: "Can Run"
        skill grounding: GroundingSkill
            requirement: Required

    discover_with: "Discover With"
        skill find_skills: FindSkills
            requirement: Advisory


workflow SharedRoleHome: "Role Home"
    start_here: "Start Here"
        "Read the current packet before you act."

    skills: SharedSkills


workflow InlineSkillsRoleHome: "Role Home"
    start_here: "Start Here"
        "Read the current packet before you act."

    skills: "Skills And Tools"
        setup: "Setup"
            "Use this inline skills block when the workflow itself owns the guidance."

        can_run: "Can Run"
            skill find_skills: FindSkills
                reason: "Use this when the job needs skill discovery before execution."


agent AgentSkillsBlockDemo:
    role: "Use the shared skills block directly on the agent."
    skills: SharedSkills


agent WorkflowReferencedSkillsBlockDemo:
    role: "Use the shared skills block through a workflow."
    role_home: SharedRoleHome


agent WorkflowInlineSkillsBlockDemo:
    role: "Use an inline workflow-owned skills block."
    role_home: InlineSkillsRoleHome
````

## File: examples/21_first_class_skills_blocks/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "agents can reference top-level skills blocks directly"
status = "active"
kind = "render_contract"
agent = "AgentSkillsBlockDemo"
assertion = "exact_lines"
expected_lines = [
  "Use the shared skills block directly on the agent.",
  "",
  "## Skills And Tools",
  "",
  "### How To Use",
  "",
  "Start with the skill that directly matches the current job.",
  "",
  "### Can Run",
  "",
  "#### Grounding Skill",
  "",
  "##### Purpose",
  "",
  "Ground the current claim before you write.",
  "",
  "This skill is required for this role. If you cannot locate it, stop and escalate instead of guessing.",
  "",
  "### Discover With",
  "",
  "#### Find Skills",
  "",
  "##### Purpose",
  "",
  "Find the right repo skill before you guess.",
]

[[cases]]
name = "workflows can reference top-level skills blocks"
status = "active"
kind = "render_contract"
agent = "WorkflowReferencedSkillsBlockDemo"
assertion = "exact_lines"
expected_lines = [
  "Use the shared skills block through a workflow.",
  "",
  "## Role Home",
  "",
  "### Start Here",
  "",
  "Read the current packet before you act.",
  "",
  "### Skills And Tools",
  "",
  "#### How To Use",
  "",
  "Start with the skill that directly matches the current job.",
  "",
  "#### Can Run",
  "",
  "##### Grounding Skill",
  "",
  "###### Purpose",
  "",
  "Ground the current claim before you write.",
  "",
  "This skill is required for this role. If you cannot locate it, stop and escalate instead of guessing.",
  "",
  "#### Discover With",
  "",
  "##### Find Skills",
  "",
  "###### Purpose",
  "",
  "Find the right repo skill before you guess.",
]

[[cases]]
name = "workflows can author inline skills blocks"
status = "active"
kind = "render_contract"
agent = "WorkflowInlineSkillsBlockDemo"
assertion = "exact_lines"
expected_lines = [
  "Use an inline workflow-owned skills block.",
  "",
  "## Role Home",
  "",
  "### Start Here",
  "",
  "Read the current packet before you act.",
  "",
  "### Skills And Tools",
  "",
  "#### Setup",
  "",
  "Use this inline skills block when the workflow itself owns the guidance.",
  "",
  "#### Can Run",
  "",
  "##### Find Skills",
  "",
  "###### Purpose",
  "",
  "Find the right repo skill before you guess.",
  "",
  "###### Reason",
  "",
  "Use this when the job needs skill discovery before execution.",
]
````

## File: examples/22_skills_block_inheritance/prompts/INVALID_CYCLIC_SKILLS_INHERITANCE.prompt
````
skill GroundingSkill: "Grounding Skill"
    purpose: "Ground the current claim before you write."


skills CycleA[CycleB]: "Skills"
    inherit primary


skills CycleB[CycleA]: "Skills"
    inherit primary


agent InvalidSkillsCycleDemo:
    role: "Use the cyclic skills block to prove fail-loud cycle diagnostics."
    skills: CycleA
````

## File: examples/23_first_class_io_blocks/prompts/AGENTS.prompt
````
input ScopedCatalogTruth: "Scoped Catalog Truth"
    source: File
        path: "catalog/scoped_catalog_truth.json"
    shape: "JSON Document"
    requirement: Required


input BroaderCurriculumContext: "Broader Curriculum Context"
    source: File
        path: "catalog/broader_curriculum_context.json"
    shape: "JSON Document"
    requirement: Advisory


output DurableSectionTruth: "Durable Section Truth"
    target: File
        path: "section_root/_authoring/durable_section_truth.md"
    shape: "Markdown Document"
    requirement: Required


output CoordinationHandoff: "Coordination Handoff"
    target: TurnResponse
    shape: "Comment"
    requirement: Required


inputs SharedSectionInputs: "Your Inputs"
    "Read these inputs in order."

    scoped_catalog_truth: "Scoped Catalog Truth"
        ScopedCatalogTruth

    broader_curriculum_context: "Broader Curriculum Context"
        "Use this as support evidence, not as section truth."
        BroaderCurriculumContext


outputs SharedSectionOutputs: "Your Outputs"
    "Always produce both outputs."

    durable_section_truth: "Durable Section Truth"
        DurableSectionTruth

    coordination_handoff: "Coordination Handoff"
        CoordinationHandoff


agent FirstClassIoBlocksDemo:
    role: "Use shared inputs and outputs blocks directly on the agent."
    inputs: SharedSectionInputs
    outputs: SharedSectionOutputs
````

## File: examples/23_first_class_io_blocks/prompts/INVALID_WRONG_KIND_FIELD_REF.prompt
````
inputs SharedSectionInputs: "Your Inputs"
    packet: "Packet"
        SharedCatalogPacket


outputs SharedSectionOutputs: "Your Outputs"
    handoff: "Handoff"
        SharedHandoff


input SharedCatalogPacket: "Shared Catalog Packet"
    source: File
        path: "catalog/shared_catalog_packet.json"
    shape: "JSON Document"
    requirement: Required


output SharedHandoff: "Shared Handoff"
    target: TurnResponse
    shape: "Comment"
    requirement: Required


agent InvalidWrongKindFieldRef:
    role: "Trigger a wrong-kind first-class IO field ref."
    inputs: SharedSectionOutputs
````

## File: examples/23_first_class_io_blocks/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "agents can reference first-class inputs and outputs blocks directly"
status = "active"
kind = "render_contract"
agent = "FirstClassIoBlocksDemo"
assertion = "exact_lines"
expected_lines = [
  "Use shared inputs and outputs blocks directly on the agent.",
  "",
  "## Your Inputs",
  "",
  "Read these inputs in order.",
  "",
  "### Scoped Catalog Truth",
  "",
  "#### Scoped Catalog Truth",
  "",
  "- Source: File",
  "- Path: `catalog/scoped_catalog_truth.json`",
  "- Shape: JSON Document",
  "- Requirement: Required",
  "",
  "### Broader Curriculum Context",
  "",
  "Use this as support evidence, not as section truth.",
  "",
  "#### Broader Curriculum Context",
  "",
  "- Source: File",
  "- Path: `catalog/broader_curriculum_context.json`",
  "- Shape: JSON Document",
  "- Requirement: Advisory",
  "",
  "## Your Outputs",
  "",
  "Always produce both outputs.",
  "",
  "### Durable Section Truth",
  "",
  "#### Durable Section Truth",
  "",
  "- Target: File",
  "- Path: `section_root/_authoring/durable_section_truth.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "### Coordination Handoff",
  "",
  "#### Coordination Handoff",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
]

[[cases]]
name = "wrong-kind first-class io field refs fail loud"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_WRONG_KIND_FIELD_REF.prompt"
agent = "InvalidWrongKindFieldRef"
exception_type = "CompileError"
error_code = "E248"
message_contains = [
  "Inputs fields must resolve to inputs blocks, not outputs blocks",
  "SharedSectionOutputs",
]
````

## File: examples/24_io_block_inheritance/prompts/AGENTS.prompt
````
input ScopedCatalogTruth: "Scoped Catalog Truth"
    source: File
        path: "catalog/scoped_catalog_truth.json"
    shape: "JSON Document"
    requirement: Required


input ContinuityOnlyPacket: "Continuity Only Packet"
    source: File
        path: "catalog/continuity_only_packet.json"
    shape: "JSON Document"
    requirement: Advisory


input ForwardContinuityPacket: "Forward Continuity Packet"
    source: File
        path: "catalog/forward_continuity_packet.json"
    shape: "JSON Document"
    requirement: Advisory


output DurableSectionTruth: "Durable Section Truth"
    target: File
        path: "section_root/_authoring/durable_section_truth.md"
    shape: "Markdown Document"
    requirement: Required


output CoordinationHandoff: "Coordination Handoff"
    target: TurnResponse
    shape: "Comment"
    requirement: Required


inputs BaseSectionInputs: "Your Inputs"
    "Read these inputs in order."

    scoped_catalog_truth: "Scoped Catalog Truth"
        ScopedCatalogTruth

    continuity_only: "Continuity Only"
        "Use continuity evidence to re-earn the section."
        ContinuityOnlyPacket


inputs ReviewSectionInputs[BaseSectionInputs]: "Your Inputs"
    inherit scoped_catalog_truth

    override continuity_only: "Continuity Only"
        "Use continuity evidence to re-earn the section."
        "Read one section ahead when the review calls for it."
        ForwardContinuityPacket


outputs BaseSectionOutputs: "Your Outputs"
    "Always produce both outputs."

    durable_section_truth: "Durable Section Truth"
        DurableSectionTruth

    coordination_handoff: "Coordination Handoff"
        CoordinationHandoff


outputs ReviewSectionOutputs[BaseSectionOutputs]: "Your Outputs"
    inherit durable_section_truth

    override coordination_handoff: "Coordination Handoff"
        "Point the next owner at the reviewed dossier truth."
        CoordinationHandoff


agent IoBlockInheritanceDemo:
    role: "Use inherited inputs and outputs blocks for review work."
    inputs: ReviewSectionInputs
    outputs: ReviewSectionOutputs
````

## File: examples/24_io_block_inheritance/prompts/INVALID_MISSING_INHERITED_ENTRY.prompt
````
output DurableSectionTruth: "Durable Section Truth"
    target: File
        path: "section_root/_authoring/durable_section_truth.md"
    shape: "Markdown Document"
    requirement: Required


output CoordinationHandoff: "Coordination Handoff"
    target: TurnResponse
    shape: "Comment"
    requirement: Required


outputs BaseSectionOutputs: "Your Outputs"
    durable_section_truth: "Durable Section Truth"
        DurableSectionTruth

    coordination_handoff: "Coordination Handoff"
        CoordinationHandoff


outputs InvalidMissingOutputs[BaseSectionOutputs]: "Your Outputs"
    inherit durable_section_truth


agent InvalidMissingInheritedIoEntryDemo:
    role: "Trigger a missing inherited IO block entry."
    outputs: InvalidMissingOutputs
````

## File: examples/24_io_block_inheritance/prompts/INVALID_OVERRIDE.prompt
````
input ScopedCatalogTruth: "Scoped Catalog Truth"
    source: File
        path: "catalog/scoped_catalog_truth.json"
    shape: "JSON Document"
    requirement: Required


inputs BaseSectionInputs: "Your Inputs"
    scoped_catalog_truth: "Scoped Catalog Truth"
        ScopedCatalogTruth


inputs InvalidOverrideInputs[BaseSectionInputs]: "Your Inputs"
    inherit scoped_catalog_truth

    override continuity_only: "Continuity Only"
        "This override should fail because the parent does not define the key."


agent InvalidOverrideIoBlockDemo:
    role: "Trigger an invalid IO block override."
    inputs: InvalidOverrideInputs
````

## File: examples/24_io_block_inheritance/prompts/INVALID_PATCH_WITHOUT_PARENT.prompt
````
input ScopedCatalogTruth: "Scoped Catalog Truth"
    source: File
        path: "catalog/scoped_catalog_truth.json"
    shape: "JSON Document"
    requirement: Required


inputs InvalidStandalonePatch: "Your Inputs"
    inherit scoped_catalog_truth


agent InvalidPatchWithoutParentIoDemo:
    role: "Trigger IO patch syntax without an inherited block."
    inputs: InvalidStandalonePatch
````

## File: examples/24_io_block_inheritance/prompts/INVALID_UNDEFINED_INHERIT.prompt
````
input ScopedCatalogTruth: "Scoped Catalog Truth"
    source: File
        path: "catalog/scoped_catalog_truth.json"
    shape: "JSON Document"
    requirement: Required


inputs BaseSectionInputs: "Your Inputs"
    scoped_catalog_truth: "Scoped Catalog Truth"
        ScopedCatalogTruth


inputs InvalidUndefinedInheritInputs[BaseSectionInputs]: "Your Inputs"
    inherit continuity_only


agent InvalidUndefinedInheritIoDemo:
    role: "Trigger inheritance of an undefined IO block entry."
    inputs: InvalidUndefinedInheritInputs
````

## File: examples/24_io_block_inheritance/prompts/INVALID_UNKEYED_PARENT_REF.prompt
````
input SharedCatalogPacket: "Shared Catalog Packet"
    source: File
        path: "catalog/shared_catalog_packet.json"
    shape: "JSON Document"
    requirement: Required


inputs BareInputs: "Your Inputs"
    SharedCatalogPacket


inputs InvalidInheritedInputs[BareInputs]: "Your Inputs"
    "This child should fail before it can inherit the parent block."


agent InvalidUnkeyedParentIoDemo:
    role: "Trigger inheritance from an IO block with an unkeyed top-level ref."
    inputs: InvalidInheritedInputs
````

## File: examples/24_io_block_inheritance/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "named inputs and outputs blocks inherit and patch explicitly"
status = "active"
kind = "render_contract"
agent = "IoBlockInheritanceDemo"
assertion = "exact_lines"
expected_lines = [
  "Use inherited inputs and outputs blocks for review work.",
  "",
  "## Your Inputs",
  "",
  "### Scoped Catalog Truth",
  "",
  "#### Scoped Catalog Truth",
  "",
  "- Source: File",
  "- Path: `catalog/scoped_catalog_truth.json`",
  "- Shape: JSON Document",
  "- Requirement: Required",
  "",
  "### Continuity Only",
  "",
  "Use continuity evidence to re-earn the section.",
  "Read one section ahead when the review calls for it.",
  "",
  "#### Forward Continuity Packet",
  "",
  "- Source: File",
  "- Path: `catalog/forward_continuity_packet.json`",
  "- Shape: JSON Document",
  "- Requirement: Advisory",
  "",
  "## Your Outputs",
  "",
  "### Durable Section Truth",
  "",
  "#### Durable Section Truth",
  "",
  "- Target: File",
  "- Path: `section_root/_authoring/durable_section_truth.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "### Coordination Handoff",
  "",
  "Point the next owner at the reviewed dossier truth.",
  "",
  "#### Coordination Handoff",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
]

[[cases]]
name = "invalid io block override fails with E001"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_OVERRIDE.prompt"
agent = "InvalidOverrideIoBlockDemo"
exception_type = "CompileError"
error_code = "E001"
message_contains = [
  "Cannot override undefined inputs entry in inputs BaseSectionInputs",
  "continuity_only",
]

[[cases]]
name = "missing inherited io block entry fails with E003"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_MISSING_INHERITED_ENTRY.prompt"
agent = "InvalidMissingInheritedIoEntryDemo"
exception_type = "CompileError"
error_code = "E003"
message_contains = [
  "Missing inherited outputs entry in InvalidMissingOutputs",
  "coordination_handoff",
]

[[cases]]
name = "undefined io block inherit fails with E245"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_UNDEFINED_INHERIT.prompt"
agent = "InvalidUndefinedInheritIoDemo"
exception_type = "CompileError"
error_code = "E245"
message_contains = [
  "cannot inherit undefined key `continuity_only`",
]

[[cases]]
name = "io patch syntax without inherited block fails with E246"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_PATCH_WITHOUT_PARENT.prompt"
agent = "InvalidPatchWithoutParentIoDemo"
exception_type = "CompileError"
error_code = "E246"
message_contains = [
  "requires an inherited inputs block in `InvalidStandalonePatch`",
  "scoped_catalog_truth",
]

[[cases]]
name = "inherited io blocks fail loud when parent has unkeyed top-level refs"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_UNKEYED_PARENT_REF.prompt"
agent = "InvalidUnkeyedParentIoDemo"
exception_type = "CompileError"
error_code = "E247"
message_contains = [
  "contains unkeyed top-level refs",
  "Shared Catalog Packet",
]
````

## File: examples/25_abstract_agent_io_override/prompts/AGENTS.prompt
````
input ScopedCatalogTruth: "Scoped Catalog Truth"
    source: File
        path: "catalog/scoped_catalog_truth.json"
    shape: "JSON Document"
    requirement: Required


input ContinuityOnlyPacket: "Continuity Only Packet"
    source: File
        path: "catalog/continuity_only_packet.json"
    shape: "JSON Document"
    requirement: Advisory


input ForwardContinuityPacket: "Forward Continuity Packet"
    source: File
        path: "catalog/forward_continuity_packet.json"
    shape: "JSON Document"
    requirement: Advisory


output DurableSectionTruth: "Durable Section Truth"
    target: File
        path: "section_root/_authoring/durable_section_truth.md"
    shape: "Markdown Document"
    requirement: Required


output CoordinationHandoff: "Coordination Handoff"
    target: TurnResponse
    shape: "Comment"
    requirement: Required


inputs BaseSectionInputs: "Your Inputs"
    "Read these inputs in order."

    scoped_catalog_truth: "Scoped Catalog Truth"
        ScopedCatalogTruth

    continuity_only: "Continuity Only"
        "Use continuity evidence to re-earn the section."
        ContinuityOnlyPacket


outputs BaseSectionOutputs: "Your Outputs"
    "Always produce both outputs."

    durable_section_truth: "Durable Section Truth"
        DurableSectionTruth

    coordination_handoff: "Coordination Handoff"
        CoordinationHandoff


# This abstract parent shares named IO defaults. The child patches the named
# blocks directly; the parent agent fields are not themselves the patch surface.
abstract agent BaseSectionRole:
    role: "Use the shared section role defaults."
    inputs: BaseSectionInputs
    outputs: BaseSectionOutputs


agent ReuseSectionRole[BaseSectionRole]:
    role: "Reuse the parent's shared section IO blocks directly."
    inputs: BaseSectionInputs
    outputs: BaseSectionOutputs


agent OverrideSectionRole[BaseSectionRole]:
    role: "Override the parent's shared section IO blocks through named block patching."

    inputs[BaseSectionInputs]: "Your Inputs"
        inherit scoped_catalog_truth

        override continuity_only: "Continuity Only"
            "Use continuity evidence to re-earn the section."
            "Read one section ahead only when the issue says continuity matters."
            ForwardContinuityPacket

    outputs[BaseSectionOutputs]: "Your Outputs"
        inherit durable_section_truth

        override coordination_handoff: "Coordination Handoff"
            "Tell the next owner what changed and where the dossier truth lives."
            CoordinationHandoff
````

## File: examples/25_abstract_agent_io_override/prompts/INVALID_WRONG_PATCH_BASE.prompt
````
input ScopedCatalogTruth: "Scoped Catalog Truth"
    source: File
        path: "catalog/scoped_catalog_truth.json"
    shape: "JSON Document"
    requirement: Required


output CoordinationHandoff: "Coordination Handoff"
    target: TurnResponse
    shape: "Comment"
    requirement: Required


inputs BaseSectionInputs: "Your Inputs"
    scoped_catalog_truth: "Scoped Catalog Truth"
        ScopedCatalogTruth


outputs BaseSectionOutputs: "Your Outputs"
    coordination_handoff: "Coordination Handoff"
        CoordinationHandoff


abstract agent BaseSectionRole:
    role: "Use the shared section role defaults."
    inputs: BaseSectionInputs
    outputs: BaseSectionOutputs


agent InvalidWrongPatchBase[BaseSectionRole]:
    role: "Trigger a wrong-kind IO patch base."

    inputs[BaseSectionOutputs]: "Your Inputs"
        override scoped_catalog_truth: "Scoped Catalog Truth"
            ScopedCatalogTruth
````

## File: examples/25_abstract_agent_io_override/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "concrete child can reuse abstract parent io blocks directly"
status = "active"
kind = "render_contract"
agent = "ReuseSectionRole"
assertion = "exact_lines"
expected_lines = [
  "Reuse the parent's shared section IO blocks directly.",
  "",
  "## Your Inputs",
  "",
  "Read these inputs in order.",
  "",
  "### Scoped Catalog Truth",
  "",
  "#### Scoped Catalog Truth",
  "",
  "- Source: File",
  "- Path: `catalog/scoped_catalog_truth.json`",
  "- Shape: JSON Document",
  "- Requirement: Required",
  "",
  "### Continuity Only",
  "",
  "Use continuity evidence to re-earn the section.",
  "",
  "#### Continuity Only Packet",
  "",
  "- Source: File",
  "- Path: `catalog/continuity_only_packet.json`",
  "- Shape: JSON Document",
  "- Requirement: Advisory",
  "",
  "## Your Outputs",
  "",
  "Always produce both outputs.",
  "",
  "### Durable Section Truth",
  "",
  "#### Durable Section Truth",
  "",
  "- Target: File",
  "- Path: `section_root/_authoring/durable_section_truth.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "### Coordination Handoff",
  "",
  "#### Coordination Handoff",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
]

[[cases]]
name = "concrete child can override abstract parent io blocks directly"
status = "active"
kind = "render_contract"
agent = "OverrideSectionRole"
assertion = "exact_lines"
expected_lines = [
  "Override the parent's shared section IO blocks through named block patching.",
  "",
  "## Your Inputs",
  "",
  "### Scoped Catalog Truth",
  "",
  "#### Scoped Catalog Truth",
  "",
  "- Source: File",
  "- Path: `catalog/scoped_catalog_truth.json`",
  "- Shape: JSON Document",
  "- Requirement: Required",
  "",
  "### Continuity Only",
  "",
  "Use continuity evidence to re-earn the section.",
  "Read one section ahead only when the issue says continuity matters.",
  "",
  "#### Forward Continuity Packet",
  "",
  "- Source: File",
  "- Path: `catalog/forward_continuity_packet.json`",
  "- Shape: JSON Document",
  "- Requirement: Advisory",
  "",
  "## Your Outputs",
  "",
  "### Durable Section Truth",
  "",
  "#### Durable Section Truth",
  "",
  "- Target: File",
  "- Path: `section_root/_authoring/durable_section_truth.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "### Coordination Handoff",
  "",
  "Tell the next owner what changed and where the dossier truth lives.",
  "",
  "#### Coordination Handoff",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
]

[[cases]]
name = "wrong-kind abstract-parent io patch bases fail loud"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_WRONG_PATCH_BASE.prompt"
agent = "InvalidWrongPatchBase"
exception_type = "CompileError"
error_code = "E249"
message_contains = [
  "Inputs patch fields must inherit from inputs blocks, not outputs blocks",
  "BaseSectionOutputs",
]
````

## File: examples/26_abstract_authored_slots/prompts/AGENTS.prompt
````
# This example introduces `abstract <slot_key>` for authored agent slots.
# - it declares a required authored slot without placeholder prose
# - abstract descendants may defer inherited abstract slots
# - concrete children must define every remaining abstract slot directly
# - `inherit` and `override` do not satisfy an abstract slot requirement

workflow SharedReadFirst: "Read First"
    "Read Your Job first."
    "Then read Workflow Core and Routing."


workflow SharedStandards: "Standards And Support"
    "Keep the review tied to the current issue."
    "Leave one clear next owner."


workflow AcceptanceReviewerJob: "Your Job"
    "Review the section against the current scope."
    "Accept only when the work is ready for the next owner."
    "Return weak or unclear work honestly."


workflow AcceptanceReviewerWorkflowCore: "Workflow Core"
    review_scope: "Review Scope"
        "Check the current source of truth before you accept the work."
        "Do not invent new scope on a review turn."

    handoff_rule: "Handoff Rule"
        "When you accept the work, route it to ProjectLead."
        "When the work is not ready, route it back to SectionAuthor."


workflow AcceptanceReviewerRouting: "Routing"
    accepted: "Accepted"
        route "If the work is accepted" -> ProjectLead

    changes_requested: "Changes Requested"
        route "If the work needs changes" -> SectionAuthor


agent ProjectLead:
    role: "Receive accepted review work."


agent SectionAuthor:
    role: "Receive review work that needs changes."


abstract agent ReviewRoleBase:
    read_first: SharedReadFirst
    standards_and_support: SharedStandards
    abstract your_job
    abstract workflow_core
    abstract routing


abstract agent DeferredReviewRole[ReviewRoleBase]:
    inherit read_first
    inherit standards_and_support


agent AcceptanceReviewer[DeferredReviewRole]:
    role: "Review the section honestly and route it to the next owner only when it is ready."

    your_job: AcceptanceReviewerJob
    inherit read_first
    workflow_core: AcceptanceReviewerWorkflowCore
    routing: AcceptanceReviewerRouting
    inherit standards_and_support
````

## File: examples/26_abstract_authored_slots/prompts/INVALID_MISSING_ABSTRACT_SLOT.prompt
````
abstract agent ReviewRoleBase:
    abstract your_job
    abstract workflow_core


agent InvalidConcreteMissingWorkflowCore[ReviewRoleBase]:
    role: "Trigger one missing abstract authored slot."

    your_job: "Your Job"
        "Do the current review job honestly."
````

## File: examples/26_abstract_authored_slots/prompts/INVALID_MISSING_MULTIPLE_ABSTRACT_SLOTS.prompt
````
abstract agent ReviewRoleBase:
    abstract workflow_core
    abstract routing


agent InvalidConcreteMissingMultiple[ReviewRoleBase]:
    role: "Trigger multiple missing abstract authored slots."
````

## File: examples/26_abstract_authored_slots/prompts/INVALID_OVERRIDE_ABSTRACT_SLOT.prompt
````
workflow ReplacementWorkflowCore: "Workflow Core"
    "Replacement workflow core."


abstract agent ReviewRoleBase:
    abstract workflow_core


agent InvalidOverrideAbstractWorkflowCore[ReviewRoleBase]:
    role: "Trigger invalid override against an abstract authored slot."

    override workflow_core: ReplacementWorkflowCore
````

## File: examples/26_abstract_authored_slots/ref/acceptance_reviewer/AGENTS.md
````markdown
Review the section honestly and route it to the next owner only when it is ready.

## Your Job

Review the section against the current scope.
Accept only when the work is ready for the next owner.
Return weak or unclear work honestly.

## Read First

Read Your Job first.
Then read Workflow Core and Routing.

## Workflow Core

### Review Scope

Check the current source of truth before you accept the work.
Do not invent new scope on a review turn.

### Handoff Rule

When you accept the work, route it to ProjectLead.
When the work is not ready, route it back to SectionAuthor.

## Routing

### Accepted

If the work is accepted -> ProjectLead

### Changes Requested

If the work needs changes -> SectionAuthor

## Standards And Support

Keep the review tied to the current issue.
Leave one clear next owner.
````

## File: examples/26_abstract_authored_slots/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "abstract authored slots require concrete children to define required slots directly"
status = "active"
kind = "render_contract"
agent = "AcceptanceReviewer"
assertion = "exact_lines"
approx_ref = "ref/acceptance_reviewer/AGENTS.md"
expected_lines = [
  "Review the section honestly and route it to the next owner only when it is ready.",
  "",
  "## Your Job",
  "",
  "Review the section against the current scope.",
  "Accept only when the work is ready for the next owner.",
  "Return weak or unclear work honestly.",
  "",
  "## Read First",
  "",
  "Read Your Job first.",
  "Then read Workflow Core and Routing.",
  "",
  "## Workflow Core",
  "",
  "### Review Scope",
  "",
  "Check the current source of truth before you accept the work.",
  "Do not invent new scope on a review turn.",
  "",
  "### Handoff Rule",
  "",
  "When you accept the work, route it to ProjectLead.",
  "When the work is not ready, route it back to SectionAuthor.",
  "",
  "## Routing",
  "",
  "### Accepted",
  "",
  "If the work is accepted -> ProjectLead",
  "",
  "### Changes Requested",
  "",
  "If the work needs changes -> SectionAuthor",
  "",
  "## Standards And Support",
  "",
  "Keep the review tied to the current issue.",
  "Leave one clear next owner.",
]

[[cases]]
name = "concrete child missing one abstract authored slot fails with E209"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_MISSING_ABSTRACT_SLOT.prompt"
agent = "InvalidConcreteMissingWorkflowCore"
exception_type = "CompileError"
error_code = "E209"
message_contains = [
  "Concrete agent is missing abstract authored slots",
  "must define abstract authored slots",
  "`workflow_core`",
]

[[cases]]
name = "concrete child missing multiple abstract authored slots groups them in one E209"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_MISSING_MULTIPLE_ABSTRACT_SLOTS.prompt"
agent = "InvalidConcreteMissingMultiple"
exception_type = "CompileError"
error_code = "E209"
message_contains = [
  "Concrete agent is missing abstract authored slots",
  "must define abstract authored slots",
  "`workflow_core`",
  "`routing`",
]

[[cases]]
name = "override does not satisfy an abstract authored slot requirement"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_OVERRIDE_ABSTRACT_SLOT.prompt"
agent = "InvalidOverrideAbstractWorkflowCore"
exception_type = "CompileError"
error_code = "E210"
message_contains = [
  "Abstract authored slot must be defined directly",
  "cannot satisfy abstract authored slot",
  "`workflow_core`",
  "Define the slot directly with `slot_key: ...`.",
]
````

## File: examples/27_addressable_record_paths/prompts/AGENTS.prompt
````
# This example makes explicitly keyed nested record items addressable through
# arbitrary dotted paths.
# - path refs can target titled nested sections and scalar leaves inside record
#   declarations
# - workflow section bodies accept `Decl:path.to.child`
# - generic scalar values can reuse `Decl:path.to.child` without flattening the
#   source declaration

workflow ReadFirst: "Read First"
    read_now: "Read Now"
        SectionConceptsTermsFileOutput:title
        SectionConceptsTermsFileOutput:must_include.analysis.tables.concept_ladder_table.title
        SectionConceptsTermsFileOutput:must_include.analysis.tables.concept_ladder_table
        "Build {{SectionConceptsTermsFileOutput:must_include.analysis.tables.title}} inside {{SectionConceptsTermsFileOutput:title}} before you finalize `{{SectionConceptsTermsFileOutput:target.path}}`."


output SectionConceptsTermsFileOutput: "Section Concepts Terms File"
    target: File
        path: "section_root/_authoring/SECTION_CONCEPTS_AND_TERMS.md"
    shape: MarkdownDocument
    requirement: Required

    must_include: "Must Include"
        analysis: "Analysis"
            tables: "Tables"
                concept_ladder_table: "Concept Ladder Table"
                    "Map what earlier sections already taught and what the learner should learn next."

        ids: "Concept IDs"
            "Keep ids stable when the section already has accepted concepts."


skill ConceptsTermsSkill: "Concepts Terms Skill"
    purpose: "Use {{SectionConceptsTermsFileOutput:must_include.analysis.tables.concept_ladder_table}} before you finalize the document."

    canonical_table: SectionConceptsTermsFileOutput:must_include.analysis.tables.concept_ladder_table
    canonical_path: SectionConceptsTermsFileOutput:target.path


agent AddressableRecordPathsDemo:
    role: "Keep deep contract paths readable without flattening the contract."

    read_first: ReadFirst

    skills: "Skills"
        can_run: "Can Run"
            skill concepts_terms: ConceptsTermsSkill

    outputs: "Outputs"
        SectionConceptsTermsFileOutput
````

## File: examples/27_addressable_record_paths/prompts/INVALID_NON_ADDRESSABLE_RECORD_PATH.prompt
````
workflow ReadFirst: "Read First"
    read_now: "Read Now"
        "Build {{SectionConceptsTermsFileOutput:target.path.file_name}} before you finalize the file."


output SectionConceptsTermsFileOutput: "Section Concepts Terms File"
    target: File
        path: "section_root/_authoring/SECTION_CONCEPTS_AND_TERMS.md"
    shape: MarkdownDocument
    requirement: Required


agent InvalidNonAddressableRecordPathDemo:
    role: "Trigger a deep record path that walks past a scalar leaf."
    read_first: ReadFirst

    outputs: "Outputs"
        SectionConceptsTermsFileOutput
````

## File: examples/27_addressable_record_paths/prompts/INVALID_UNKNOWN_RECORD_PATH.prompt
````
workflow ReadFirst: "Read First"
    read_now: "Read Now"
        "Build {{SectionConceptsTermsFileOutput:must_include.analysis.tables.missing_table}} before you finalize the file."


output SectionConceptsTermsFileOutput: "Section Concepts Terms File"
    target: File
        path: "section_root/_authoring/SECTION_CONCEPTS_AND_TERMS.md"
    shape: MarkdownDocument
    requirement: Required

    must_include: "Must Include"
        analysis: "Analysis"
            tables: "Tables"
                concept_ladder_table: "Concept Ladder Table"
                    "Map what earlier sections already taught and what the learner should learn next."


agent InvalidUnknownRecordPathDemo:
    role: "Trigger an unknown deep record path."
    read_first: ReadFirst

    outputs: "Outputs"
        SectionConceptsTermsFileOutput
````

## File: examples/28_addressable_workflow_paths/prompts/AGENTS.prompt
````
# This example makes nested workflow sections addressable through path-bearing
# refs.
# - workflow section bodies may nest titled sections recursively
# - path refs can point at child sets or deep nested workflow items
# - generic scalar values can reuse workflow paths without flattening the
#   workflow declaration

workflow ReviewRules: "Review Rules"
    gates: "Gates"
        build: "Build"
            check_build_honesty: "Check Build Honesty"
                "Compare the current build to the plan before you accept it."

        copy: "Copy"
            check_copy_scope: "Check Copy Scope"
                "Reject copy that invents scope beyond the current issue."


workflow ReadFirst: "Read First"
    review_sequence: "Review Sequence"
        ReviewRules:gates
        ReviewRules:gates.build.check_build_honesty
        "Run {{ReviewRules:gates.build.check_build_honesty}} before you route the work."


output ReviewComment: "Review Comment"
    target: TurnResponse
    shape: MarkdownDocument
    requirement: Required

    gate_family: ReviewRules:gates
    honest_gate: ReviewRules:gates.build.check_build_honesty


agent WorkflowPathRefsDemo:
    role: "Keep workflow-owned review gates addressable without flattening the workflow."

    read_first: ReadFirst

    outputs: "Outputs"
        ReviewComment
````

## File: examples/28_addressable_workflow_paths/prompts/INVALID_BARE_WORKFLOW_ROOT.prompt
````
workflow ReviewRules: "Review Rules"
    gates: "Gates"
        build: "Build"
            check_build_honesty: "Check Build Honesty"
                "Compare the current build to the plan before you accept it."


workflow ReadFirst: "Read First"
    review_sequence: "Review Sequence"
        ReviewRules


output ReviewComment: "Review Comment"
    target: TurnResponse
    shape: MarkdownDocument
    requirement: Required


agent InvalidBareWorkflowRootDemo:
    role: "Trigger a bare workflow root ref where a path is required."
    read_first: ReadFirst

    outputs: "Outputs"
        ReviewComment
````

## File: examples/28_addressable_workflow_paths/prompts/INVALID_UNKNOWN_WORKFLOW_PATH.prompt
````
workflow ReviewRules: "Review Rules"
    gates: "Gates"
        build: "Build"
            check_build_honesty: "Check Build Honesty"
                "Compare the current build to the plan before you accept it."


workflow ReadFirst: "Read First"
    review_sequence: "Review Sequence"
        "Run {{ReviewRules:gates.build.missing_gate}} before you route the work."


output ReviewComment: "Review Comment"
    target: TurnResponse
    shape: MarkdownDocument
    requirement: Required


agent InvalidUnknownWorkflowPathDemo:
    role: "Trigger an unknown workflow path segment."
    read_first: ReadFirst

    outputs: "Outputs"
        ReviewComment
````

## File: examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt
````
# This prompt exercises the self-addressed addressable-root fix and the nested
# descent surfaces the editor also needs to follow.

skill GroundingSkill: "Grounding Skill"
    purpose: "Ground the current claim before you write."


skills SharedSkills: "Shared Skills"
    "Keep {{SharedSkills:can_run.grounding}} available before you act."

    can_run: "Can Run"
        skill grounding: GroundingSkill


workflow ReviewRules: "Review Rules"
    "Run {{ReviewRules:gates.build.check_build_honesty}} before you review anything else."

    gates: "Gates"
        build: "Build"
            check_build_honesty: "Check Build Honesty"
                "Compare the current build to the plan before you accept it."


workflow WorkflowRoot: "Workflow Root"
    use shared: ReviewRules

    skills: SharedSkills

    review_sequence: "Review Sequence"
        WorkflowRoot:shared.title
        WorkflowRoot:skills.title
        WorkflowRoot:shared.gates.build.check_build_honesty
        WorkflowRoot:skills.can_run.grounding
        "Run {{WorkflowRoot:shared.gates.build.check_build_honesty}} with {{WorkflowRoot:skills.can_run.grounding}}."


agent SelfAddressableRootsDemo:
    role: "Keep self-addressed and workflow-owned nested paths stable."

    workflow: WorkflowRoot
````

## File: examples/28_addressable_workflow_paths/ref/workflow_path_refs_demo/AGENTS.md
````markdown
Keep workflow-owned review gates addressable without flattening the workflow.

## Read First

### Review Sequence

- Gates
- Check Build Honesty

Run Check Build Honesty before you route the work.

## Outputs

### Review Comment

- Target: Turn Response
- Shape: Markdown Document
- Requirement: Required

- Gate Family: Gates
- Honest Gate: Check Build Honesty
````

## File: examples/28_addressable_workflow_paths/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "workflow paths resolve child sets and deep nested workflow items"
status = "active"
kind = "render_contract"
agent = "WorkflowPathRefsDemo"
assertion = "exact_lines"
approx_ref = "ref/workflow_path_refs_demo/AGENTS.md"
expected_lines = [
  "Keep workflow-owned review gates addressable without flattening the workflow.",
  "",
  "## Read First",
  "",
  "### Review Sequence",
  "",
  "- Gates",
  "- Check Build Honesty",
  "",
  "Run Check Build Honesty before you route the work.",
  "",
  "## Outputs",
  "",
  "### Review Comment",
  "",
  "- Target: Turn Response",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "- Gate Family: Gates",
  "- Honest Gate: Check Build Honesty",
]

[[cases]]
name = "bare workflow roots still fail on readable surfaces"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_BARE_WORKFLOW_ROOT.prompt"
agent = "InvalidBareWorkflowRootDemo"
exception_type = "CompileError"
error_code = "E271"
message_contains = [
  "Workflow refs are not allowed in workflow section bodies",
  "use `use` for workflow composition",
  "ReviewRules",
]

[[cases]]
name = "unknown workflow path segments fail loud"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_UNKNOWN_WORKFLOW_PATH.prompt"
agent = "InvalidUnknownWorkflowPathDemo"
exception_type = "CompileError"
error_code = "E273"
message_contains = [
  "Unknown addressable path on workflow strings",
  "ReviewRules:gates.build.missing_gate",
]

[[cases]]
name = "self-addressed workflow and skills roots resolve without false cycles"
status = "active"
kind = "render_contract"
prompt = "prompts/SELF_AND_DESCENT.prompt"
agent = "SelfAddressableRootsDemo"
assertion = "exact_lines"
expected_lines = [
  "Keep self-addressed and workflow-owned nested paths stable.",
  "",
  "## Workflow Root",
  "",
  "### Review Rules",
  "",
  "Run Check Build Honesty before you review anything else.",
  "",
  "#### Gates",
  "",
  "##### Build",
  "",
  "###### Check Build Honesty",
  "",
  "Compare the current build to the plan before you accept it.",
  "",
  "### Shared Skills",
  "",
  "Keep Grounding Skill available before you act.",
  "",
  "#### Can Run",
  "",
  "##### Grounding Skill",
  "",
  "###### Purpose",
  "",
  "Ground the current claim before you write.",
  "",
  "### Review Sequence",
  "",
  "- Review Rules",
  "- Shared Skills",
  "- Check Build Honesty",
  "- Grounding Skill",
  "",
  "Run Check Build Honesty with Grounding Skill.",
]
````

## File: examples/29_enums/prompts/AGENTS.prompt
````
# This example adds top-level enums for closed vocabularies with addressable
# members.
# - enums have titled roots and flat keyed string members
# - interpolation may render the enum title or a concrete member literal
# - generic scalar values may reuse enum titles and members without copying
#   bare strings

enum CriticVerdict: "Critic Verdict"
    accept: "accept"
    changes_requested: "changes requested"


enum StepKind: "Step Kind"
    guided_walkthrough: "guided_walkthrough"
    scripted_hand: "scripted_hand"


workflow ReadFirst: "Read First"
    verdict_rules: "Verdict Rules"
        "Use the {{CriticVerdict}} vocabulary and return {{CriticVerdict:accept}} or {{CriticVerdict:changes_requested}}."
        "Keep {{StepKind:guided_walkthrough}} distinct from {{StepKind:scripted_hand}}."


output ReviewDecision: "Review Decision"
    target: TurnResponse
    shape: MarkdownDocument
    requirement: Required

    verdict_family: CriticVerdict
    accepted_value: CriticVerdict:accept
    changes_requested_value: CriticVerdict:changes_requested
    walkthrough_kind: StepKind:guided_walkthrough


agent EnumRefsDemo:
    role: "Keep closed vocabularies declared once instead of copying bare strings."

    read_first: ReadFirst

    outputs: "Outputs"
        ReviewDecision
````

## File: examples/29_enums/prompts/INVALID_DUPLICATE_ENUM_MEMBER.prompt
````
enum CriticVerdict: "Critic Verdict"
    accept: "accept"
    accept: "accept again"


workflow ReadFirst: "Read First"
    verdict_rules: "Verdict Rules"
        "Use {{CriticVerdict}} when you review."


output ReviewDecision: "Review Decision"
    target: TurnResponse
    shape: MarkdownDocument
    requirement: Required


agent InvalidDuplicateEnumMemberDemo:
    role: "Trigger duplicate enum member validation."
    read_first: ReadFirst

    outputs: "Outputs"
        ReviewDecision
````

## File: examples/29_enums/prompts/INVALID_UNKNOWN_ENUM_MEMBER.prompt
````
enum CriticVerdict: "Critic Verdict"
    accept: "accept"
    changes_requested: "changes requested"


workflow ReadFirst: "Read First"
    verdict_rules: "Verdict Rules"
        "Return {{CriticVerdict:missing_member}} only when the work is ready."


output ReviewDecision: "Review Decision"
    target: TurnResponse
    shape: MarkdownDocument
    requirement: Required


agent InvalidUnknownEnumMemberDemo:
    role: "Trigger an unknown enum member ref."
    read_first: ReadFirst

    outputs: "Outputs"
        ReviewDecision
````

## File: examples/29_enums/ref/enum_refs_demo/AGENTS.md
````markdown
Keep closed vocabularies declared once instead of copying bare strings.

## Read First

### Verdict Rules

Use the Critic Verdict vocabulary and return accept or changes requested.
Keep guided_walkthrough distinct from scripted_hand.

## Outputs

### Review Decision

- Target: Turn Response
- Shape: Markdown Document
- Requirement: Required

- Verdict Family: Critic Verdict
- Accepted Value: accept
- Changes Requested Value: changes requested
- Walkthrough Kind: guided_walkthrough
````

## File: examples/29_enums/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "enums provide titled roots and addressable member literals"
status = "active"
kind = "render_contract"
agent = "EnumRefsDemo"
assertion = "exact_lines"
approx_ref = "ref/enum_refs_demo/AGENTS.md"
expected_lines = [
  "Keep closed vocabularies declared once instead of copying bare strings.",
  "",
  "## Read First",
  "",
  "### Verdict Rules",
  "",
  "Use the Critic Verdict vocabulary and return accept or changes requested.",
  "Keep guided_walkthrough distinct from scripted_hand.",
  "",
  "## Outputs",
  "",
  "### Review Decision",
  "",
  "- Target: Turn Response",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "- Verdict Family: Critic Verdict",
  "- Accepted Value: accept",
  "- Changes Requested Value: changes requested",
  "- Walkthrough Kind: guided_walkthrough",
]

[[cases]]
name = "unknown enum members fail loud"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_UNKNOWN_ENUM_MEMBER.prompt"
agent = "InvalidUnknownEnumMemberDemo"
exception_type = "CompileError"
error_code = "E273"
message_contains = [
  "Unknown addressable path on workflow strings",
  "CriticVerdict:missing_member",
]

[[cases]]
name = "duplicate enum member keys fail loud"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_DUPLICATE_ENUM_MEMBER.prompt"
agent = "InvalidDuplicateEnumMemberDemo"
exception_type = "CompileError"
error_code = "E293"
message_contains = [
  "Duplicate enum member key",
  "enum CriticVerdict",
  "accept",
]
````

## File: examples/30_law_route_only_turns/prompts/AGENTS.prompt
````
input CurrentHandoff: "Current Handoff"
    source: Prompt
    shape: JsonObject
    requirement: Required
    "Use the host-provided handoff facts that say whether the current handoff is missing or unclear."


output CoordinationComment: "Coordination Comment"
    target: TurnResponse
    shape: Comment
    requirement: Required

    standalone_read: "Standalone Read"
        "A downstream owner should be able to read this comment alone and understand that no current artifact was carried forward."


agent RoutingOwner:
    role: "Own explicit reroutes when specialist work cannot continue."
    workflow: "Instructions"
        "Take back the same issue when route-only work cannot continue safely."


workflow RouteOnlyTurns: "Route-Only Triage"
    "Handle turns that can only stop and reroute."

    law:
        active when CurrentHandoff.missing or CurrentHandoff.unclear

        when CurrentHandoff.missing:
            current none
            stop "Current handoff is missing."
            route "Route the same issue back to RoutingOwner." -> RoutingOwner

        when CurrentHandoff.unclear:
            current none
            stop "Current handoff is unclear."
            route "Route the same issue back to RoutingOwner." -> RoutingOwner


agent RouteOnlyTurnsDemo:
    role: "Keep route-only work explicit when no durable artifact is current."
    workflow: RouteOnlyTurns
    inputs: "Inputs"
        CurrentHandoff
    outputs: "Outputs"
        CoordinationComment
````

## File: examples/30_law_route_only_turns/prompts/INVALID_ACTIVE_BRANCH_WITHOUT_CURRENT.prompt
````
input CurrentHandoff: "Current Handoff"
    source: Prompt
    shape: JsonObject
    requirement: Required


agent RoutingOwner:
    role: "Own explicit reroutes when specialist work cannot continue."
    workflow: "Instructions"
        "Take back the same issue when route-only work cannot continue safely."


workflow InvalidRouteOnlyTurns: "Route-Only Triage"
    law:
        active when CurrentHandoff.missing

        when CurrentHandoff.missing:
            stop "Current handoff is missing."
            route "Route the same issue back to RoutingOwner." -> RoutingOwner


agent InvalidActiveBranchWithoutCurrent:
    role: "Trigger an active branch with no current subject."
    workflow: InvalidRouteOnlyTurns
    inputs: "Inputs"
        CurrentHandoff
````

## File: examples/30_law_route_only_turns/prompts/INVALID_CURRENT_NONE_AND_CURRENT_ARTIFACT.prompt
````
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


agent InvalidCurrentNoneAndCurrentArtifact:
    role: "Trigger conflicting currentness."
    workflow: InvalidRouteOnlyTurns
    inputs: "Inputs"
        CurrentHandoff
````

## File: examples/30_law_route_only_turns/prompts/INVALID_ROUTE_WITHOUT_LABEL.prompt
````
agent RoutingOwner:
    role: "Own explicit reroutes when specialist work cannot continue."
    workflow: "Instructions"
        "Take back the same issue when route-only work cannot continue safely."


workflow InvalidRouteOnlyTurns: "Route-Only Triage"
    law:
        current none
        route -> RoutingOwner
````

## File: examples/30_law_route_only_turns/prompts/INVALID_ROUTE_WITHOUT_TARGET.prompt
````
agent RoutingOwner:
    role: "Own explicit reroutes when specialist work cannot continue."
    workflow: "Instructions"
        "Take back the same issue when route-only work cannot continue safely."


workflow InvalidRouteOnlyTurns: "Route-Only Triage"
    law:
        current none
        route "Route the same issue back to RoutingOwner." ->
````

## File: examples/31_currentness_and_trust_surface/prompts/AGENTS.prompt
````
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

    standalone_read: "Standalone Read"
        "A downstream owner must be able to read this output alone and know which artifact is current now."


workflow CarryCurrentPlanTruth: "Carry Current Truth"
    "Keep one current artifact explicit and portable."

    law:
        current artifact ApprovedPlan via CoordinationHandoff.current_artifact


workflow CarryCurrentOutputTruth: "Carry Current Truth"
    "Keep one current artifact explicit and portable."

    law:
        current artifact SectionMetadata via CoordinationHandoff.current_artifact


agent CurrentApprovedPlanDemo:
    role: "Carry one portable current artifact through a declared handoff field."
    workflow: CarryCurrentPlanTruth
    inputs: "Inputs"
        ApprovedPlan
    outputs: "Outputs"
        CoordinationHandoff


agent CurrentSectionMetadataDemo:
    role: "Carry a newly produced artifact as the current downstream truth."
    workflow: CarryCurrentOutputTruth
    outputs: "Outputs"
        SectionMetadata
        CoordinationHandoff
````

## File: examples/31_currentness_and_trust_surface/prompts/INVALID_CARRIER_OUTPUT_NOT_EMITTED.prompt
````
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


agent InvalidCarrierOutputNotEmitted:
    role: "Trigger a missing emitted carrier output."
    workflow: InvalidCarryCurrentTruth
    outputs: "Outputs"
        SectionMetadata
````

## File: examples/31_currentness_and_trust_surface/prompts/INVALID_CURRENT_ARTIFACT_WITHOUT_VIA.prompt
````
input ApprovedPlan: "Approved Plan"
    source: File
        path: "unit_root/_authoring/APPROVED_PLAN.md"
    shape: MarkdownDocument
    requirement: Required


workflow InvalidCarryCurrentTruth: "Carry Current Truth"
    law:
        current artifact ApprovedPlan


agent InvalidCurrentArtifactWithoutVia:
    role: "Trigger a missing current carrier."
    workflow: InvalidCarryCurrentTruth
````

## File: examples/31_currentness_and_trust_surface/prompts/INVALID_CURRENT_OUTPUT_NOT_EMITTED.prompt
````
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
        current artifact SectionMetadata via CoordinationHandoff.current_artifact


agent InvalidCurrentOutputNotEmitted:
    role: "Trigger a current output artifact that is never emitted."
    workflow: InvalidCarryCurrentTruth
    outputs: "Outputs"
        CoordinationHandoff
````

## File: examples/31_currentness_and_trust_surface/prompts/INVALID_CURRENT_TARGET_WRONG_KIND.prompt
````
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


agent InvalidCurrentTargetWrongKind:
    role: "Trigger a wrong-kind current target."
    workflow: InvalidCarryCurrentTruth
    outputs: "Outputs"
        CoordinationHandoff
````

## File: examples/31_currentness_and_trust_surface/prompts/INVALID_VIA_FIELD_NOT_IN_TRUST_SURFACE.prompt
````
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


agent InvalidViaFieldNotInTrustSurface:
    role: "Trigger a carrier field that is not trusted downstream."
    workflow: InvalidCarryCurrentTruth
    outputs: "Outputs"
        CoordinationHandoff
````

## File: examples/31_currentness_and_trust_surface/prompts/INVALID_VIA_UNKNOWN_OUTPUT_FIELD.prompt
````
input ApprovedPlan: "Approved Plan"
    source: File
        path: "unit_root/_authoring/APPROVED_PLAN.md"
    shape: MarkdownDocument
    requirement: Required


output CoordinationHandoff: "Coordination Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

    handoff_summary: "Handoff Summary"
        "Summarize the current truth."

    trust_surface:
        handoff_summary


workflow InvalidCarryCurrentTruth: "Carry Current Truth"
    law:
        current artifact ApprovedPlan via CoordinationHandoff.current_artifact


agent InvalidViaUnknownOutputField:
    role: "Trigger an unknown carrier field."
    workflow: InvalidCarryCurrentTruth
    outputs: "Outputs"
        CoordinationHandoff
````

## File: examples/32_modes_and_match/prompts/INVALID_MODE_VALUE_OUTSIDE_ENUM.prompt
````
enum EditMode: "Edit Mode"
    manifest_title: "manifest-title"
    section_summary: "section-summary"


workflow InvalidModeAwareEdit: "Mode-Aware Edit"
    law:
        mode edit_mode = "taxonomy" as EditMode
        current none


agent InvalidModeValueOutsideEnum:
    role: "Trigger a mode value outside the enum."
    workflow: InvalidModeAwareEdit
````

## File: examples/34_structure_mapping_and_vocabulary_preservation/prompts/AGENTS.prompt
````
enum CriticVerdict: "Critic Verdict"
    accept: "accept"
    changes_requested: "changes requested"


input ApprovedStructure: "Approved Structure"
    source: File
        path: "unit_root/_authoring/APPROVED_STRUCTURE.md"
    shape: MarkdownDocument
    requirement: Required


input SlotMapping: "Slot Mapping"
    source: File
        path: "unit_root/_authoring/slot_mapping.json"
    shape: JsonObject
    requirement: Required


input ReviewTemplate: "Review Template"
    source: File
        path: "unit_root/_authoring/review_template.md"
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

    standalone_read: "Standalone Read"
        "A downstream owner must be able to read this output alone and know which artifact remains current now."


workflow PreserveStructure: "Preserve Structure"
    law:
        current artifact ApprovedStructure via CoordinationHandoff.current_artifact
        preserve structure ApprovedStructure


workflow PreserveMapping: "Preserve Mapping"
    law:
        current artifact SlotMapping via CoordinationHandoff.current_artifact
        preserve mapping SlotMapping


workflow PreserveVocabulary: "Preserve Vocabulary"
    law:
        current artifact ReviewTemplate via CoordinationHandoff.current_artifact
        preserve vocabulary CriticVerdict


agent PreserveStructureDemo:
    role: "Preserve document skeletons while allowing a narrow wording pass."
    workflow: PreserveStructure
    inputs: "Inputs"
        ApprovedStructure
    outputs: "Outputs"
        CoordinationHandoff


agent PreserveMappingDemo:
    role: "Keep source-to-target mappings stable during a narrow update."
    workflow: PreserveMapping
    inputs: "Inputs"
        SlotMapping
    outputs: "Outputs"
        CoordinationHandoff


agent PreserveVocabularyDemo:
    role: "Keep closed vocabulary stable while revising the surrounding guidance."
    workflow: PreserveVocabulary
    inputs: "Inputs"
        ReviewTemplate
    outputs: "Outputs"
        CoordinationHandoff
````

## File: examples/34_structure_mapping_and_vocabulary_preservation/prompts/INVALID_UNKNOWN_VOCABULARY_PRESERVE_TARGET.prompt
````
input ReviewTemplate: "Review Template"
    source: File
        path: "unit_root/_authoring/review_template.md"
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


workflow InvalidPreserveVocabulary: "Preserve Vocabulary"
    law:
        current artifact ReviewTemplate via CoordinationHandoff.current_artifact
        preserve vocabulary MissingVerdictEnum


agent InvalidUnknownVocabularyPreserveTarget:
    role: "Trigger an unknown vocabulary preserve target."
    workflow: InvalidPreserveVocabulary
    outputs: "Outputs"
        CoordinationHandoff
````

## File: examples/35_basis_roles_and_rewrite_evidence/prompts/AGENTS.prompt
````
enum RewriteRegime: "Rewrite Regime"
    carry_forward: "carry-forward"
    rewrite: "rewrite"


input CurrentHandoff: "Current Handoff"
    source: Prompt
    shape: JsonObject
    requirement: Required
    "Use the host-provided handoff facts that say whether this pass is a rewrite."


input AcceptedPeerSet: "Accepted Peer Set"
    source: File
        path: "catalog/accepted_peers.json"
    shape: JsonObject
    requirement: Advisory


input StaleMetadataNotes: "Stale Metadata Notes"
    source: File
        path: "unit_root/_authoring/stale_metadata_notes.md"
    shape: MarkdownDocument
    requirement: Advisory


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

    comparison_basis: "Comparison Basis"
        "Name any comparison-only inputs used in this pass."

    rewrite_exclusions: "Rewrite Evidence Exclusions"
        "Name any fields whose old values do not count as rewrite evidence."

    trust_surface:
        current_artifact
        comparison_basis
        rewrite_exclusions when CurrentHandoff.rewrite_regime == RewriteRegime.rewrite

    standalone_read: "Standalone Read"
        "A downstream owner must be able to read this output alone and know what is current now, what was comparison-only, and what old wording no longer counts as rewrite evidence."


workflow RewriteAwarePolish: "Rewrite-Aware Polish"
    law:
        current artifact SectionMetadata via CoordinationHandoff.current_artifact
        support_only AcceptedPeerSet for comparison
        ignore {SectionMetadata.name, SectionMetadata.description} for rewrite_evidence when CurrentHandoff.rewrite_regime == RewriteRegime.rewrite
        ignore StaleMetadataNotes for truth


agent RewriteAwarePolishDemo:
    role: "Separate comparison help, live truth, and rewrite evidence."
    workflow: RewriteAwarePolish
    inputs: "Inputs"
        CurrentHandoff
        AcceptedPeerSet
        StaleMetadataNotes
    outputs: "Outputs"
        SectionMetadata
        CoordinationHandoff
````

## File: examples/36_invalidation_and_rebuild/build_ref/routing_owner/AGENTS.md
````markdown
Own explicit reroutes when specialist work cannot continue.

## Instructions

Take back the same issue when rebuild work is required.
````

## File: examples/36_invalidation_and_rebuild/prompts/INVALID_CURRENT_ARTIFACT_AND_INVALIDATION_SAME_TARGET.prompt
````
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


agent InvalidCurrentArtifactAndInvalidationSameTarget:
    role: "Trigger invalidation of the current artifact."
    workflow: InvalidStructureChange
    outputs: "Outputs"
        SectionReview
        CoordinationHandoff
````

## File: examples/36_invalidation_and_rebuild/prompts/INVALID_INVALIDATION_FIELD_NOT_IN_TRUST_SURFACE.prompt
````
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


agent InvalidInvalidationFieldNotInTrustSurface:
    role: "Trigger an invalidation carrier outside the trust surface."
    workflow: InvalidStructureChange
    outputs: "Outputs"
        CoordinationHandoff
````

## File: examples/36_invalidation_and_rebuild/prompts/INVALID_INVALIDATION_WITHOUT_VIA.prompt
````
output SectionReview: "Section Review"
    target: File
        path: "unit_root/_authoring/SECTION_REVIEW.md"
    shape: MarkdownDocument
    requirement: Required


workflow InvalidStructureChange: "Structure Change"
    law:
        current none
        invalidate SectionReview


agent InvalidInvalidationWithoutVia:
    role: "Trigger an invalidation without a carrier."
    workflow: InvalidStructureChange
````

## File: doctrine/diagnostic_smoke.py
````python
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from doctrine.compiler import compile_prompt
from doctrine.diagnostics import diagnostic_to_dict
from doctrine.emit_docs import main as emit_docs_main
from doctrine.parser import parse_file


class SmokeFailure(RuntimeError):
    """Raised when the direct diagnostic smoke checks fail."""


def main() -> int:
    _check_transform_errors_surface_as_parse_errors()
    _check_compile_missing_role_has_specific_code()
    _check_emit_docs_handles_invalid_toml_without_traceback()
    _check_emit_docs_uses_specific_code_for_missing_entrypoint()
    _check_emit_docs_uses_entrypoint_stem_for_output_name()
    _check_diagnostic_to_dict_is_json_safe()
    print("diagnostic smoke checks passed")
    return 0


def _check_transform_errors_surface_as_parse_errors() -> None:
    source = """workflow Shared: "Shared"
    "hi"

agent Demo:
    role: "hi"
    override workflow: Shared
        "body"
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        try:
            parse_file(prompt_path)
        except Exception as exc:
            _expect(type(exc).__name__ == "ParseError", f"expected ParseError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E105", f"expected E105, got {getattr(exc, 'code', None)}")
            rendered = str(exc)
            _expect("Invalid authored slot body" in rendered, rendered)
            _expect("override workflow" in rendered, rendered)
            return
        raise SmokeFailure("expected transformer-stage parse failure, but parsing succeeded")


def _check_compile_missing_role_has_specific_code() -> None:
    source = """agent MissingRole:
    workflow: "Instructions"
        "No role here."
"""
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, source)
        prompt = parse_file(prompt_path)
        try:
            compile_prompt(prompt, "MissingRole")
        except Exception as exc:
            _expect(type(exc).__name__ == "CompileError", f"expected CompileError, got {type(exc).__name__}")
            _expect(getattr(exc, "code", None) == "E205", f"expected E205, got {getattr(exc, 'code', None)}")
            _expect("missing role field" in str(exc), str(exc))
            return
        raise SmokeFailure("expected compile failure for missing role field, but compilation succeeded")


def _check_emit_docs_handles_invalid_toml_without_traceback() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        pyproject = root / "pyproject.toml"
        pyproject.write_text("[tool.doctrine.emit\n")
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = emit_docs_main(["--pyproject", str(pyproject), "--target", "x"])
        output = stderr.getvalue()
        _expect(exit_code == 1, f"expected exit code 1, got {exit_code}")
        _expect("E506 emit error: Invalid emit config TOML" in output, output)
        _expect("Traceback" not in output, output)


def _check_emit_docs_uses_specific_code_for_missing_entrypoint() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[tool.doctrine.emit]
[[tool.doctrine.emit.targets]]
name = "bad"
entrypoint = "prompts/OTHER.prompt"
output_dir = "build"
"""
        )
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exit_code = emit_docs_main(["--pyproject", str(pyproject), "--target", "bad"])
        output = stderr.getvalue()
        _expect(exit_code == 1, f"expected exit code 1, got {exit_code}")
        _expect("E512 emit error" in output, output)
        _expect("entrypoint does not exist" in output, output)


def _check_emit_docs_uses_entrypoint_stem_for_output_name() -> None:
    with TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        prompts = root / "prompts" / "demo" / "agents" / "demo_agent"
        prompts.mkdir(parents=True)
        agents_prompt = prompts / "AGENTS.prompt"
        soul_prompt = prompts / "SOUL.prompt"
        agents_prompt.write_text(
            """agent DemoAgent:
    role: "You are Demo Agent."
"""
        )
        soul_prompt.write_text(
            """agent DemoAgent:
    role: "You are Demo Agent. Let this background shape your tone."
"""
        )
        pyproject = root / "pyproject.toml"
        pyproject.write_text(
            """[tool.doctrine.emit]
[[tool.doctrine.emit.targets]]
name = "demo_agents"
entrypoint = "prompts/demo/agents/demo_agent/AGENTS.prompt"
output_dir = "build"

[[tool.doctrine.emit.targets]]
name = "demo_soul"
entrypoint = "prompts/demo/agents/demo_agent/SOUL.prompt"
output_dir = "build"
"""
        )
        exit_code = emit_docs_main(
            [
                "--pyproject",
                str(pyproject),
                "--target",
                "demo_agents",
                "--target",
                "demo_soul",
            ]
        )
        _expect(exit_code == 0, f"expected exit code 0, got {exit_code}")
        agents_path = root / "build" / "demo" / "agents" / "demo_agent" / "AGENTS.md"
        soul_path = root / "build" / "demo" / "agents" / "demo_agent" / "SOUL.md"
        _expect(agents_path.is_file(), f"missing emitted AGENTS.md: {agents_path}")
        _expect(soul_path.is_file(), f"missing emitted SOUL.md: {soul_path}")


def _check_diagnostic_to_dict_is_json_safe() -> None:
    with TemporaryDirectory() as tmp_dir:
        prompt_path = _write_prompt(tmp_dir, 'agent Broken\n    role: "x"\n')
        try:
            parse_file(prompt_path)
        except Exception as exc:
            payload = diagnostic_to_dict(exc)
            json.dumps(payload)
            return
        raise SmokeFailure("expected parse failure for JSON-safety check, but parsing succeeded")


def _write_prompt(tmp_dir: str, source: str) -> Path:
    root = Path(tmp_dir)
    prompts = root / "prompts"
    prompts.mkdir()
    prompt_path = prompts / "AGENTS.prompt"
    prompt_path.write_text(source)
    return prompt_path


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeFailure(message)


if __name__ == "__main__":
    raise SystemExit(main())
````

## File: doctrine/emit_docs.py
````python
from __future__ import annotations

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

from doctrine import model
from doctrine.compiler import compile_prompt
from doctrine.diagnostics import DiagnosticLocation, EmitError, DoctrineError
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT_FILE_NAME = "pyproject.toml"
_CAMEL_BOUNDARY_RE = re.compile(r"(?<!^)(?=[A-Z])")
SUPPORTED_ENTRYPOINTS = ("AGENTS.prompt", "SOUL.prompt")


@dataclass(slots=True, frozen=True)
class EmitTarget:
    name: str
    entrypoint: Path
    output_dir: Path


def main(argv: list[str] | None = None) -> int:
    try:
        args = _build_arg_parser().parse_args(argv)
        config_path = resolve_pyproject_path(args.pyproject)
        targets = load_emit_targets(config_path)

        for target_name in args.target:
            target = targets.get(target_name)
            if target is None:
                raise _emit_error(
                    "E501",
                    "Unknown emit target",
                    f"Emit target `{target_name}` is not defined in `pyproject.toml`.",
                    location=_path_location(config_path),
                )
            emitted = emit_target(target)
            print(
                f"{target.name}: emitted {len(emitted)} file(s) to {_display_path(target.output_dir)}"
            )
        return 0
    except DoctrineError as exc:
        print(exc, file=sys.stderr)
        return 1


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Emit compiled Markdown trees for configured Doctrine targets."
    )
    parser.add_argument(
        "--pyproject",
        help=(
            "Path to the pyproject.toml that defines [tool.doctrine.emit]. "
            "Defaults to the nearest parent pyproject.toml from the current working directory."
        ),
    )
    parser.add_argument(
        "--target",
        action="append",
        required=True,
        help="Configured target name from [tool.doctrine.emit.targets]. Repeat to emit multiple targets.",
    )
    return parser


def resolve_pyproject_path(
    pyproject_path: str | Path | None = None,
    *,
    start_dir: str | Path | None = None,
) -> Path:
    base_dir = (Path(start_dir) if start_dir is not None else Path.cwd()).resolve()

    if pyproject_path is not None:
        candidate = Path(pyproject_path)
        if not candidate.is_absolute():
            candidate = base_dir / candidate
        resolved = candidate.resolve()
        if resolved.name != PYPROJECT_FILE_NAME:
            raise _emit_error(
                "E507",
                "Emit config path must point at pyproject.toml",
                f"Emit config must point at `pyproject.toml`, got `{resolved}`.",
                location=_path_location(resolved),
            )
        if not resolved.is_file():
            raise _emit_error(
                "E504",
                "Missing pyproject.toml",
                f"Missing `pyproject.toml`: `{resolved}`.",
                location=_path_location(resolved),
            )
        return resolved

    for candidate_dir in [base_dir, *base_dir.parents]:
        candidate = candidate_dir / PYPROJECT_FILE_NAME
        if candidate.is_file():
            return candidate.resolve()

    raise _emit_error(
        "E504",
        "Missing pyproject.toml",
        f"Could not find `pyproject.toml` in `{base_dir}` or any parent directory.",
        location=_path_location(base_dir),
    )


def load_emit_targets(
    pyproject_path: str | Path | None = None,
    *,
    start_dir: str | Path | None = None,
) -> dict[str, EmitTarget]:
    config_path = resolve_pyproject_path(pyproject_path, start_dir=start_dir)

    try:
        raw = tomllib.loads(config_path.read_text())
    except tomllib.TOMLDecodeError as exc:
        raise EmitError.from_toml_decode(path=config_path, exc=exc) from exc
    emit = (
        raw.get("tool", {})
        .get("doctrine", {})
        .get("emit", {})
    )
    raw_targets = emit.get("targets")
    if not isinstance(raw_targets, list) or not raw_targets:
        raise _emit_error(
            "E503",
            "Missing emit targets",
            "The current `pyproject.toml` does not define any `[tool.doctrine.emit.targets]`.",
            location=_path_location(config_path),
        )

    config_dir = config_path.parent
    targets: dict[str, EmitTarget] = {}
    for index, raw_target in enumerate(raw_targets, start=1):
        if not isinstance(raw_target, dict):
            raise _emit_error(
                "E508",
                "Emit target must be a TOML table",
                f"Emit target #{index} must be a TOML table.",
                location=_path_location(config_path),
            )

        name = _require_str(raw_target, "name", label=f"emit target #{index}")
        if name in targets:
            raise _emit_error(
                "E509",
                "Duplicate emit target name",
                f"Emit target `{name}` is defined more than once.",
                location=_path_location(config_path),
            )

        entrypoint = _resolve_config_file(
            config_dir,
            _require_str(raw_target, "entrypoint", label=f"emit target {name}"),
            label=f"emit target {name} entrypoint",
        )
        if entrypoint.name not in SUPPORTED_ENTRYPOINTS:
            raise _emit_error(
                "E510",
                "Emit target entrypoint must be AGENTS.prompt or SOUL.prompt",
                f"Emit target `{name}` must point at an `AGENTS.prompt` or `SOUL.prompt` entrypoint, got `{entrypoint.name}`.",
                location=_path_location(entrypoint),
            )

        output_dir = _resolve_config_path(
            config_dir,
            _require_str(raw_target, "output_dir", label=f"emit target {name}"),
        )
        if output_dir.is_file():
            raise _emit_error(
                "E511",
                "Emit target output_dir is a file",
                f"Emit target `{name}` output_dir is a file: `{output_dir}`.",
                location=_path_location(output_dir),
            )

        targets[name] = EmitTarget(name=name, entrypoint=entrypoint, output_dir=output_dir)

    return targets


def emit_target(
    target: EmitTarget,
    *,
    output_dir_override: Path | None = None,
) -> tuple[Path, ...]:
    try:
        prompt_file = parse_file(target.entrypoint)
    except DoctrineError as exc:
        raise exc.prepend_trace(
            f"emit target `{target.name}` entrypoint",
            location=_path_location(target.entrypoint),
        )
    agent_names = _root_concrete_agents(prompt_file)
    if not agent_names:
        raise _emit_error(
            "E502",
            "Emit target has no concrete agents",
            f"Emit target `{target.name}` has no concrete agents in `{target.entrypoint}`.",
            location=_path_location(target.entrypoint),
        )

    output_root = (output_dir_override or target.output_dir).resolve()
    emitted_dir = output_root / _entrypoint_relative_dir(target.entrypoint)

    emitted_paths: list[Path] = []
    seen_paths: dict[Path, str] = {}
    for agent_name in agent_names:
        emit_path = _emit_path_for_agent(
            emitted_dir,
            agent_name,
            output_name=_entrypoint_output_name(target.entrypoint),
        )
        prior_agent = seen_paths.get(emit_path)
        if prior_agent is not None:
            raise _emit_error(
                "E505",
                "Emit target path collision",
                f"Emit target `{target.name}` maps both `{prior_agent}` and `{agent_name}` to `{emit_path}`.",
                location=_path_location(emit_path),
            )
        seen_paths[emit_path] = agent_name

        try:
            rendered = render_markdown(compile_prompt(prompt_file, agent_name))
        except DoctrineError as exc:
            raise exc.prepend_trace(
                f"emit target `{target.name}`",
                location=_path_location(target.entrypoint),
            )
        emit_path.parent.mkdir(parents=True, exist_ok=True)
        emit_path.write_text(rendered)
        emitted_paths.append(emit_path)

    return tuple(emitted_paths)


def _emit_path_for_agent(emitted_dir: Path, agent_name: str, *, output_name: str) -> Path:
    agent_slug = _agent_slug(agent_name)
    if emitted_dir.parts and emitted_dir.parts[-1] == agent_slug:
        return emitted_dir / output_name
    return emitted_dir / agent_slug / output_name


def _root_concrete_agents(prompt_file: model.PromptFile) -> tuple[str, ...]:
    names = [
        declaration.name
        for declaration in prompt_file.declarations
        if isinstance(declaration, model.Agent) and not declaration.abstract
    ]
    return tuple(names)


def _entrypoint_relative_dir(entrypoint: Path) -> Path:
    resolved = entrypoint.resolve()
    for candidate in [resolved.parent, *resolved.parents]:
        if candidate.name == "prompts":
            rel_dir = resolved.relative_to(candidate).parent
            return Path() if rel_dir == Path(".") else rel_dir
    raise _emit_error(
        "E514",
        "Could not resolve prompts root",
        f"Could not resolve `prompts/` root for `{resolved}`.",
        location=_path_location(resolved),
    )


def _entrypoint_output_name(entrypoint: Path) -> str:
    return f"{entrypoint.stem}.md"


def _agent_slug(name: str) -> str:
    return _CAMEL_BOUNDARY_RE.sub("_", name).lower()


def _resolve_config_file(config_dir: Path, value: str, *, label: str) -> Path:
    path = _resolve_config_path(config_dir, value)
    if not path.is_file():
        raise _emit_error(
            "E512",
            "Emit config path does not exist",
            f"{label} does not exist: {value}",
            location=_path_location(path),
        )
    return path


def _resolve_config_path(config_dir: Path, value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = config_dir / candidate
    return candidate.resolve()


def _require_str(raw: dict[str, object], key: str, *, label: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str):
        raise _emit_error(
            "E513",
            "Emit config value must be a string",
            f"{label}.{key} must be a string.",
        )
    return value


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _path_location(path: Path | None) -> DiagnosticLocation | None:
    if path is None:
        return None
    return DiagnosticLocation(path=path.resolve())


def _emit_error(
    code: str,
    summary: str,
    detail: str,
    *,
    location: DiagnosticLocation | None = None,
    hints: tuple[str, ...] = (),
) -> EmitError:
    return EmitError.from_parts(
        code=code,
        summary=summary,
        detail=detail,
        location=location,
        hints=hints,
    )


if __name__ == "__main__":
    raise SystemExit(main())
````

## File: doctrine/renderer.py
````python
from __future__ import annotations

from doctrine.compiler import CompiledAgent, CompiledSection
from doctrine.model import EmphasizedLine, RoleScalar


def render_markdown(agent: CompiledAgent) -> str:
    sections: list[str] = []
    for field in agent.fields:
        if isinstance(field, RoleScalar):
            sections.append(field.text)
            continue
        sections.append(_render_section(field, depth=2))
    return "\n\n".join(section for section in sections if section) + "\n"


def _render_section(section: CompiledSection, *, depth: int) -> str:
    lines = [f"{'#' * depth} {section.title}"]
    body_lines: list[str] = []

    for item in section.body:
        if isinstance(item, str):
            body_lines.append(item)
            continue
        if isinstance(item, EmphasizedLine):
            body_lines.append(f"**{item.kind.upper()}**: {item.text}")
            continue

        if body_lines and body_lines[-1] != "":
            body_lines.append("")
        body_lines.extend(_render_section(item, depth=depth + 1).splitlines())

    while body_lines and body_lines[-1] == "":
        body_lines.pop()

    if not body_lines:
        return "\n".join(lines)

    return "\n".join([*lines, "", *body_lines])
````

## File: doctrine/verify_corpus.py
````python
from __future__ import annotations

import argparse
import tempfile
import tomllib
from dataclasses import dataclass
from difflib import unified_diff
from pathlib import Path
from typing import Any

from doctrine.compiler import compile_prompt
from doctrine.diagnostics import DoctrineError
from doctrine.emit_docs import EmitError, emit_target, load_emit_targets
from doctrine.parser import parse_file
from doctrine.renderer import render_markdown

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILD_CONTRACT_REF_DIR = "build_ref"


class ManifestError(RuntimeError):
    """Raised when a case manifest is structurally invalid."""


class VerificationError(RuntimeError):
    """Raised when a case result does not match its contract."""


@dataclass(slots=True, frozen=True)
class CaseSpec:
    manifest_path: Path
    example_dir: Path
    name: str
    kind: str
    prompt_path: Path
    approx_ref_path: Path | None
    agent: str | None = None
    build_target: str | None = None
    assertion: str | None = None
    expected_lines: tuple[str, ...] = ()
    exception_type: str | None = None
    error_code: str | None = None
    message_contains: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class CaseResult:
    case: CaseSpec
    result: str
    detail: str


@dataclass(slots=True, frozen=True)
class RefDiff:
    case: CaseSpec
    label: str
    diff: str


@dataclass(slots=True)
class VerificationReport:
    manifest_errors: list[str]
    case_results: list[CaseResult]
    ref_diffs: list[RefDiff]
    surfaced_inconsistencies: list[str]

    def failed(self) -> bool:
        return bool(
            self.manifest_errors
            or any(result.result == "FAIL" for result in self.case_results)
            or self.surfaced_inconsistencies
        )


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    report = verify_corpus(args.manifest or None)
    print(format_report(report))
    return 1 if report.failed() else 0


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify Doctrine example manifests.")
    parser.add_argument(
        "--manifest",
        action="append",
        help="Repo-relative path to a single cases.toml manifest. Repeat to run multiple manifests.",
    )
    return parser


def verify_corpus(manifest_args: list[str] | None = None) -> VerificationReport:
    manifest_errors: list[str] = []
    case_results: list[CaseResult] = []
    ref_diffs: list[RefDiff] = []
    surfaced_inconsistencies: list[str] = []

    try:
        manifests = _resolve_manifest_paths(manifest_args)
    except ManifestError as exc:
        return VerificationReport(
            manifest_errors=[str(exc)],
            case_results=case_results,
            ref_diffs=ref_diffs,
            surfaced_inconsistencies=surfaced_inconsistencies,
        )

    cases: list[CaseSpec] = []
    for manifest_path in manifests:
        try:
            cases.extend(_load_manifest(manifest_path))
        except ManifestError as exc:
            manifest_errors.append(f"{_display_path(manifest_path)}: {exc}")

    for case in cases:
        try:
            if case.kind == "render_contract":
                case_results.append(_run_render_contract(case, ref_diffs))
            elif case.kind == "build_contract":
                case_results.append(_run_build_contract(case))
            elif case.kind == "parse_fail":
                case_results.append(_run_parse_fail(case))
            elif case.kind == "compile_fail":
                case_results.append(_run_compile_fail(case))
            else:  # pragma: no cover - blocked by manifest validation
                raise ManifestError(f"Unsupported case kind {case.kind!r}.")
        except Exception as exc:  # pragma: no cover - exercised by the command itself
            case_results.append(
                CaseResult(case=case, result="FAIL", detail=_format_case_failure(exc))
            )

    return VerificationReport(
        manifest_errors=manifest_errors,
        case_results=case_results,
        ref_diffs=ref_diffs,
        surfaced_inconsistencies=surfaced_inconsistencies,
    )


def _resolve_manifest_paths(manifest_args: list[str] | None) -> tuple[Path, ...]:
    if manifest_args:
        resolved = tuple(_resolve_repo_path(manifest) for manifest in manifest_args)
    else:
        resolved = tuple(sorted((REPO_ROOT / "examples").glob("*/cases.toml")))

    if not resolved:
        raise ManifestError("No manifest files were found.")

    missing = [path for path in resolved if not path.is_file()]
    if missing:
        formatted = ", ".join(str(path.relative_to(REPO_ROOT)) for path in missing)
        raise ManifestError(f"Missing manifest file(s): {formatted}")

    return resolved


def _resolve_repo_path(path_str: str) -> Path:
    candidate = Path(path_str)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    return candidate.resolve()


def _load_manifest(path: Path) -> tuple[CaseSpec, ...]:
    try:
        raw = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as exc:
        raise ManifestError(f"Invalid TOML: {exc}") from exc

    if not isinstance(raw, dict):
        raise ManifestError("Manifest root must be a TOML table.")

    schema_version = raw.get("schema_version")
    if schema_version != 1:
        raise ManifestError(f"Expected schema_version = 1, got {schema_version!r}.")

    example_dir = path.parent.resolve()
    default_prompt_rel = _require_str(raw, "default_prompt")
    default_prompt_path = _resolve_example_path(
        example_dir, default_prompt_rel, label="default_prompt"
    )

    raw_cases = raw.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ManifestError("Manifest must define at least one [[cases]] entry.")

    seen_names: set[str] = set()
    cases: list[CaseSpec] = []
    for index, raw_case in enumerate(raw_cases, start=1):
        if not isinstance(raw_case, dict):
            raise ManifestError(f"cases[{index}] must be a TOML table.")
        case = _load_case(
            manifest_path=path.resolve(),
            example_dir=example_dir,
            default_prompt_path=default_prompt_path,
            default_prompt_rel=default_prompt_rel,
            raw_case=raw_case,
            case_index=index,
        )
        if case.name in seen_names:
            raise ManifestError(f"Duplicate case name {case.name!r} in {path.name}.")
        seen_names.add(case.name)
        cases.append(case)

    return tuple(cases)


def _load_case(
    *,
    manifest_path: Path,
    example_dir: Path,
    default_prompt_path: Path,
    default_prompt_rel: str,
    raw_case: dict[str, Any],
    case_index: int,
) -> CaseSpec:
    name = _require_str(raw_case, "name", case_index=case_index)
    _require_choice(raw_case, "status", {"active"}, case_index=case_index)
    kind = _require_choice(
        raw_case,
        "kind",
        {"render_contract", "build_contract", "parse_fail", "compile_fail"},
        case_index=case_index,
    )

    prompt_rel = raw_case.get("prompt", default_prompt_rel)
    if not isinstance(prompt_rel, str):
        raise ManifestError(f"cases[{case_index}].prompt must be a string when provided.")
    prompt_path = (
        default_prompt_path
        if prompt_rel == default_prompt_rel
        else _resolve_example_path(example_dir, prompt_rel, label=f"cases[{case_index}].prompt")
    )

    approx_ref_rel = raw_case.get("approx_ref")
    approx_ref_path: Path | None = None
    if approx_ref_rel is not None:
        if not isinstance(approx_ref_rel, str):
            raise ManifestError(
                f"cases[{case_index}].approx_ref must be a string when provided."
            )
        approx_ref_path = _resolve_example_path(
            example_dir, approx_ref_rel, label=f"cases[{case_index}].approx_ref"
        )

    if kind == "render_contract":
        agent = _require_str(raw_case, "agent", case_index=case_index)
        assertion = _require_choice(
            raw_case, "assertion", {"exact_lines"}, case_index=case_index
        )
        expected_lines = _require_string_list(
            raw_case, "expected_lines", case_index=case_index
        )
        return CaseSpec(
            manifest_path=manifest_path,
            example_dir=example_dir,
            name=name,
            kind=kind,
            prompt_path=prompt_path,
            approx_ref_path=approx_ref_path,
            agent=agent,
            assertion=assertion,
            expected_lines=expected_lines,
        )

    if kind == "build_contract":
        build_target = _require_str(raw_case, "build_target", case_index=case_index)
        return CaseSpec(
            manifest_path=manifest_path,
            example_dir=example_dir,
            name=name,
            kind=kind,
            prompt_path=prompt_path,
            approx_ref_path=approx_ref_path,
            build_target=build_target,
        )

    exception_type = _require_str(raw_case, "exception_type", case_index=case_index)
    error_code = raw_case.get("error_code")
    if error_code is not None and not isinstance(error_code, str):
        raise ManifestError(f"cases[{case_index}].error_code must be a string when provided.")
    message_contains = _require_string_list(
        raw_case, "message_contains", case_index=case_index
    )

    agent: str | None = None
    if kind == "compile_fail":
        agent = _require_str(raw_case, "agent", case_index=case_index)

    return CaseSpec(
        manifest_path=manifest_path,
        example_dir=example_dir,
        name=name,
        kind=kind,
        prompt_path=prompt_path,
        approx_ref_path=approx_ref_path,
        agent=agent,
        exception_type=exception_type,
        error_code=error_code,
        message_contains=message_contains,
    )


def _resolve_example_path(example_dir: Path, rel_path: str, *, label: str) -> Path:
    resolved = (example_dir / rel_path).resolve()
    try:
        resolved.relative_to(example_dir)
    except ValueError as exc:
        raise ManifestError(
            f"{label} escapes the owning example directory: {rel_path!r}."
        ) from exc

    if not resolved.is_file():
        raise ManifestError(f"{label} does not exist: {rel_path!r}.")

    return resolved


def _run_render_contract(case: CaseSpec, ref_diffs: list[RefDiff]) -> CaseResult:
    prompt_file = parse_file(case.prompt_path)
    compiled = compile_prompt(prompt_file, case.agent or "")
    rendered = render_markdown(compiled)
    ref_diff = _build_contract_ref_diff(
        case,
        expected_lines=tuple(rendered.splitlines()),
        output_label=f"rendered://{case.agent}",
    )
    if ref_diff is not None:
        ref_diffs.append(ref_diff)

    actual_lines = tuple(rendered.splitlines())
    if actual_lines != case.expected_lines:
        diff = _build_diff(
            case.expected_lines,
            actual_lines,
            fromfile=f"expected://{case.name}",
            tofile=f"rendered://{case.agent}",
        )
        raise VerificationError(
            "Rendered output did not match the prompt-derived contract.\n"
            + diff
        )

    return CaseResult(
        case=case,
        result="PASS",
        detail="render matched exact_lines contract",
    )


def _run_parse_fail(case: CaseSpec) -> CaseResult:
    try:
        parse_file(case.prompt_path)
    except Exception as exc:
        _assert_expected_exception(case, exc)
        return CaseResult(case=case, result="PASS", detail="parse failed as expected")

    raise VerificationError("Expected parse to fail, but it succeeded.")


def _run_build_contract(case: CaseSpec) -> CaseResult:
    try:
        targets = load_emit_targets(start_dir=REPO_ROOT)
        target = targets.get(case.build_target or "")
        if target is None:
            raise VerificationError(f"Unknown build target: {case.build_target}")
    except EmitError as exc:
        raise VerificationError(str(exc)) from exc

    expected_root = case.example_dir / BUILD_CONTRACT_REF_DIR
    if not expected_root.is_dir():
        raise VerificationError(
            "Checked-in build reference tree does not exist for target "
            f"{target.name}: {expected_root}"
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        actual_root = Path(temp_dir)
        try:
            emit_target(target, output_dir_override=actual_root)
        except EmitError as exc:
            raise VerificationError(str(exc)) from exc

        diff = _build_tree_diff(expected_root=expected_root, actual_root=actual_root)
        if diff is not None:
            raise VerificationError(
                "Emitted build tree did not match the checked-in build contract.\n" + diff
            )

    return CaseResult(
        case=case,
        result="PASS",
        detail="build matched checked-in tree",
    )


def _run_compile_fail(case: CaseSpec) -> CaseResult:
    prompt_file = parse_file(case.prompt_path)
    try:
        compile_prompt(prompt_file, case.agent or "")
    except Exception as exc:
        _assert_expected_exception(case, exc)
        return CaseResult(case=case, result="PASS", detail="compile failed as expected")

    raise VerificationError("Expected compile to fail, but it succeeded.")


def _assert_expected_exception(case: CaseSpec, exc: Exception) -> None:
    actual_type = type(exc).__name__
    if actual_type != case.exception_type:
        raise VerificationError(
            f"Expected {case.exception_type}, got {actual_type}: {exc}"
        )

    actual_code = getattr(exc, "code", None)
    if case.error_code is not None and actual_code != case.error_code:
        raise VerificationError(
            f"Expected error code {case.error_code}, got {actual_code}: {exc}"
        )

    message = str(exc)
    missing = [snippet for snippet in case.message_contains if snippet not in message]
    if missing:
        joined = ", ".join(repr(snippet) for snippet in missing)
        raise VerificationError(
            f"{case.exception_type} did not include required excerpt(s): {joined}"
        )


def _build_contract_ref_diff(
    case: CaseSpec, *, expected_lines: tuple[str, ...], output_label: str
) -> RefDiff | None:
    if case.approx_ref_path is None:
        return None

    ref_lines = tuple(case.approx_ref_path.read_text().splitlines())
    if ref_lines == expected_lines:
        return None

    return RefDiff(
        case=case,
        label=f"{case.approx_ref_path.relative_to(REPO_ROOT)} vs {case.name}",
        diff=_build_diff(
            ref_lines,
            expected_lines,
            fromfile=str(case.approx_ref_path.relative_to(REPO_ROOT)),
            tofile=output_label,
        ),
    )


def _build_diff(
    before_lines: tuple[str, ...],
    after_lines: tuple[str, ...],
    *,
    fromfile: str,
    tofile: str,
) -> str:
    return "".join(
        unified_diff(
            [line + "\n" for line in before_lines],
            [line + "\n" for line in after_lines],
            fromfile=fromfile,
            tofile=tofile,
        )
    )


def _build_tree_diff(*, expected_root: Path, actual_root: Path) -> str | None:
    expected_files = {
        path.relative_to(expected_root): path
        for path in expected_root.rglob("*")
        if path.is_file()
    }
    actual_files = {
        path.relative_to(actual_root): path
        for path in actual_root.rglob("*")
        if path.is_file()
    }

    lines: list[str] = []

    missing = sorted(expected_files.keys() - actual_files.keys())
    if missing:
        lines.append("Missing emitted files:")
        for rel_path in missing:
            lines.append(f"- {rel_path.as_posix()}")

    unexpected = sorted(actual_files.keys() - expected_files.keys())
    if unexpected:
        if lines:
            lines.append("")
        lines.append("Unexpected emitted files:")
        for rel_path in unexpected:
            lines.append(f"- {rel_path.as_posix()}")

    common = sorted(expected_files.keys() & actual_files.keys())
    for rel_path in common:
        expected_lines = tuple(expected_files[rel_path].read_text().splitlines())
        actual_lines = tuple(actual_files[rel_path].read_text().splitlines())
        if expected_lines == actual_lines:
            continue
        if lines:
            lines.append("")
        rel_label = rel_path.as_posix()
        lines.append(
            _build_diff(
                expected_lines,
                actual_lines,
                fromfile=f"expected://{rel_label}",
                tofile=f"emitted://{rel_label}",
            ).rstrip("\n")
        )

    return "\n".join(lines) if lines else None


def format_report(report: VerificationReport) -> str:
    lines: list[str] = []

    if report.manifest_errors:
        lines.append("Manifest errors:")
        for error in report.manifest_errors:
            lines.append(f"- {error}")
        lines.append("")

    lines.append("Case results:")
    if report.case_results:
        for result in report.case_results:
            case_path = _display_path(result.case.manifest_path)
            lines.append(
                f"- {result.result} {case_path} :: {result.case.name} :: {result.detail}"
            )
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Checked ref diffs:")
    if report.ref_diffs:
        for ref_diff in report.ref_diffs:
            lines.append(f"- {ref_diff.label}")
            lines.append(ref_diff.diff.rstrip("\n"))
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Surfaced inconsistencies:")
    if report.surfaced_inconsistencies:
        for inconsistency in report.surfaced_inconsistencies:
            lines.append(f"- {inconsistency}")
    else:
        # Keep the reporting lane explicit even when this run settles cleanly.
        lines.append("- None surfaced during this run.")

    return "\n".join(lines)


def _require_str(raw: dict[str, Any], key: str, *, case_index: int | None = None) -> str:
    value = raw.get(key)
    if not isinstance(value, str):
        location = key if case_index is None else f"cases[{case_index}].{key}"
        raise ManifestError(f"{location} must be a string.")
    return value


def _require_choice(
    raw: dict[str, Any],
    key: str,
    allowed: set[str],
    *,
    case_index: int | None = None,
) -> str:
    value = _require_str(raw, key, case_index=case_index)
    if value not in allowed:
        location = key if case_index is None else f"cases[{case_index}].{key}"
        allowed_str = ", ".join(sorted(repr(item) for item in allowed))
        raise ManifestError(f"{location} must be one of {allowed_str}, got {value!r}.")
    return value


def _require_string_list(
    raw: dict[str, Any], key: str, *, case_index: int | None = None
) -> tuple[str, ...]:
    value = raw.get(key)
    location = key if case_index is None else f"cases[{case_index}].{key}"
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ManifestError(f"{location} must be a list of strings.")
    return tuple(value)


def _format_case_failure(exc: Exception) -> str:
    if isinstance(exc, DoctrineError):
        return f"{type(exc).__name__} [{exc.code}]:\n{exc}"
    return f"{type(exc).__name__}: {exc}"


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
````

## File: examples/01_hello_world/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "hello world scalar role renders opening prose"
status = "active"
kind = "render_contract"
agent = "HelloWorld"
assertion = "exact_lines"
approx_ref = "ref/AGENTS.md"
expected_lines = [
  "You are the hello world agent.",
  "",
  "## Instruction",
  "",
  "Say hello world.",
]

[[cases]]
name = "hello world headed role renders headed opening section"
status = "active"
kind = "render_contract"
agent = "HelloWorld2"
assertion = "exact_lines"
expected_lines = [
  "## Role",
  "",
  "You are the hello world agent.",
  "",
  "## Instruction",
  "",
  "Say hello world.",
]

[[cases]]
name = "missing agent colon fails in parse stage"
status = "active"
kind = "parse_fail"
prompt = "prompts/INVALID_PARSE_MISSING_COLON.prompt"
exception_type = "ParseError"
error_code = "E101"
message_contains = [
  "Expected one of",
  "COLON",
]

[[cases]]
name = "reordered fields fail in compile stage"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_COMPILE_REORDERED.prompt"
agent = "ReorderedFields"
exception_type = "CompileError"
error_code = "E206"
message_contains = [
  "expected `role` followed by `workflow`",
]
````

## File: examples/03_imports/prompts/chains/absolute/briefing.prompt
````
import .opening
import .closing


workflow AbsoluteBriefing: "Absolute Briefing"
    "This file composes sibling imports through dotted package paths."

    use opening: chains.absolute.opening.Opening
    use closing: chains.absolute.closing.Closing
````

## File: examples/03_imports/prompts/chains/deep/levels/one/two/entry.prompt
````
import ..detail
import ....base.final_note


workflow DeepRelativeChain: "Deep Relative Chain"
    "This file uses both a sibling-relative import and a multi-level parent-relative import."

    use deep_detail: chains.deep.levels.one.detail.DeepDetail
    use final_note: chains.deep.base.final_note.FinalNote
````

## File: examples/03_imports/prompts/chains/deep/levels/one/detail.prompt
````
import ...base.topic


workflow DeepDetail: "Deep Detail"
    "This file walks back up the package tree with `...` before following the path forward again."

    use root_topic: chains.deep.base.topic.RootTopic
````

## File: examples/03_imports/prompts/chains/relative/entry.prompt
````
import .leaf
import ..shared.wrap_up


workflow RelativeChain: "Relative Chain"
    "This file chains a sibling-relative import with a parent-relative import."

    use leaf_step: chains.relative.leaf.LeafStep
    use shared_wrap_up: chains.shared.wrap_up.SharedWrapUp
````

## File: examples/03_imports/prompts/chains/relative/leaf.prompt
````
import ..shared.context


workflow LeafStep: "Leaf Step"
    "This module reaches back to its parent package before following the path forward again."

    use shared_context: chains.shared.context.SharedContext
````

## File: examples/05_workflow_merge/ref/ordered_briefing_agent/AGENTS.md
````markdown
You are the ordered briefing agent.

## Ordered Briefing

Deliver the revised briefing in the explicit order below.
This child places inherited, overridden, and new sections on purpose.

### Opening

State the topic.

### Context Note

Add the missing context before the main point.

### Main Point

Give the revised main point.

### Supporting Point

Add one supporting detail.

### Closing

Wrap up the briefing.

### Follow Up

Invite one follow-up question.
````

## File: examples/05_workflow_merge/ref/retitled_briefing_agent/AGENTS.md
````markdown
You are the retitled briefing agent.

## Revised Briefing

Deliver the revised briefing below.
This child keeps the structure but changes one section title on purpose.

### Opening

State the topic.

### Revised Main Point

Give the revised main point.

### Supporting Point

Add one supporting detail.

### Closing

Wrap up the briefing.
````

## File: examples/05_workflow_merge/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "ordered briefing agent explicitly patches inherited order"
status = "active"
kind = "render_contract"
agent = "OrderedBriefingAgent"
assertion = "exact_lines"
approx_ref = "ref/ordered_briefing_agent/AGENTS.md"
expected_lines = [
  "You are the ordered briefing agent.",
  "",
  "## Ordered Briefing",
  "",
  "Deliver the revised briefing in the explicit order below.",
  "This child places inherited, overridden, and new sections on purpose.",
  "",
  "### Opening",
  "",
  "State the topic.",
  "",
  "### Context Note",
  "",
  "Add the missing context before the main point.",
  "",
  "### Main Point",
  "",
  "Give the revised main point.",
  "",
  "### Supporting Point",
  "",
  "Add one supporting detail.",
  "",
  "### Closing",
  "",
  "Wrap up the briefing.",
  "",
  "### Follow Up",
  "",
  "Invite one follow-up question.",
]

[[cases]]
name = "retitled briefing agent keeps inherited structure with a title override"
status = "active"
kind = "render_contract"
agent = "RetitledBriefingAgent"
assertion = "exact_lines"
approx_ref = "ref/retitled_briefing_agent/AGENTS.md"
expected_lines = [
  "You are the retitled briefing agent.",
  "",
  "## Revised Briefing",
  "",
  "Deliver the revised briefing below.",
  "This child keeps the structure but changes one section title on purpose.",
  "",
  "### Opening",
  "",
  "State the topic.",
  "",
  "### Revised Main Point",
  "",
  "Give the revised main point.",
  "",
  "### Supporting Point",
  "",
  "Add one supporting detail.",
  "",
  "### Closing",
  "",
  "Wrap up the briefing.",
]

[[cases]]
name = "invalid override fails with E001"
status = "active"
kind = "compile_fail"
agent = "InvalidOverrideBriefingAgent"
exception_type = "CompileError"
error_code = "E001"
message_contains = [
  "E001",
  "context_note",
]

[[cases]]
name = "missing inherited entry fails with E003"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_MISSING_INHERITED_ENTRY.prompt"
agent = "MissingInheritedEntryBriefingAgent"
exception_type = "CompileError"
error_code = "E003"
message_contains = [
  "E003",
  "closing",
]
````

## File: examples/06_nested_workflows/prompts/AGENTS.prompt
````
# Model 1: simple local workflows can still live inline inside an agent.
# This is still just a local workflow owned by this one agent.
# There is no inherited parent workflow at this level, so there is nothing
# to account for explicitly and no inherited order to preserve.
agent InlineBriefingAgent:
    role: "You are the inline briefing agent."

    workflow: "Briefing"
        "Deliver the briefing in the order below."

        opening: "Opening"
            "State the topic."

        main_point: "Main Point"
            "Give the main point directly."

        closing: "Closing"
            "End with the next step."


# Model 2: nested or reusable structure should live in named workflows.
# `Preparation` and `Delivery` are real named workflow declarations.
# That gives nested structure a stable identity and lets workflow inheritance
# use the same explicit ordered patching rules we already use elsewhere.
workflow Preparation: "Preparation"
    "Start with the topic and the audience before you deliver the briefing."

    topic: "Topic"
        "State the topic in one line."

    audience: "Audience"
        "Name who the briefing is for."


workflow Delivery: "Delivery"
    "Move through the briefing in a fixed sequence."

    opening: "Opening"
        "State the situation."

    main_point: "Main Point"
        "Give the main point directly."

    closing: "Closing"
        "End with the next step."

# This is the inherited case.
# Because `RevisedDelivery` extends `Delivery`, it must still account for each
# inherited entry exactly once:
# - `inherit opening` keeps the inherited entry in this exact position
# - `context_note: "Context Note"` adds a new entry at this exact position
# - `override main_point:` replaces the inherited entry in this exact position
# - `inherit closing` keeps the inherited entry in this exact position
# This is the same explicit patching model as `05_workflow_merge`, just applied
# to a named workflow instead of an agent-owned workflow block.
workflow RevisedDelivery[Delivery]: "Delivery"
    "Move through the briefing in the revised sequence."

    inherit opening

    context_note: "Context Note"
        "Add one sentence of missing context before the main point."

    override main_point:
        "Give the revised main point directly."

    inherit closing

# These agent-level workflows are local composition surfaces.
# Named workflows are included through keyed `use` entries such as
# `use preparation: Preparation`.
# - the local key is the outer composition identity
# - the referenced workflow is the reusable inner structure
# - this is composition, not inheritance
# That means this outer `workflow: "Briefing"` block can put strings or local
# entries around them freely because there is no inherited outer workflow being
# patched yet.
agent StructuredBriefingAgent:
    role: "You are the structured briefing agent."

    workflow: "Briefing"
        "This file is the runtime guide for a structured briefing."

        use preparation: Preparation
        use delivery: Delivery

# Same idea here: this is still local composition at the outer workflow level.
# The inherited behavior is inside `RevisedDelivery[Delivery]`, not in this
# agent's `workflow: "Revised Briefing"` block.
# The `use` entries still matter, though: they give the outer workflow stable
# local identities that a later inheriting child can patch directly.
agent RevisedStructuredBriefingAgent:
    role: "You are the revised structured briefing agent."

    workflow: "Revised Briefing"
        "This file is the runtime guide for a structured briefing."
        "This version keeps preparation and revises delivery through workflow reuse."

        use preparation: Preparation
        use delivery: RevisedDelivery

# Model 4: once outer composition uses keyed `use` entries, a child agent can
# inherit that outer workflow and patch it directly.
# - `inherit preparation` keeps the inherited composed piece in place
# - `override delivery: RevisedDelivery` retargets that outer composition key
#   to a different named workflow without forcing the child to restate the
#   whole outer structure
agent InheritedStructuredBriefingAgent[StructuredBriefingAgent]:
    role: "You are the inherited structured briefing agent."

    workflow: "Inherited Revised Briefing"
        "This file inherits the outer briefing structure."
        "It keeps preparation and replaces delivery through outer workflow inheritance."

        inherit preparation
        override delivery: RevisedDelivery
````

## File: examples/08_inputs/ref/custom_source_input_agent/AGENTS.md
````markdown
# Custom Source Input Agent

Core job: use a design spec from a custom typed input source.

## Your Job

- Use the custom source configuration to find the design document.
- Fail if the required design source data is missing.

## Inputs

### Design Spec

- Source: Figma Document
- URL: `https://figma.com/design/abc123/Example-Design`
- Node: `12:34`
- Shape: Design document
- Requirement: Required

Use this design document when the turn depends on a specific Figma source.
````

## File: examples/08_inputs/ref/env_input_agent/AGENTS.md
````markdown
# Env Input Agent

Core job: locate the tracker checkout from an environment variable before doing any tracker work.

## Your Job

- Look up the tracker root from the environment variable.
- Fail if the environment variable is missing.

## Inputs

### Tracker Root

- Source: EnvVar
- Variable: `TRACKER_ROOT`
- Shape: Directory path
- Requirement: Required

This environment variable points to the tracker checkout root.
````

## File: examples/08_inputs/ref/path_input_agent/AGENTS.md
````markdown
# Path Input Agent

Core job: revise a section plan using path-based file input.

## Your Job

- Read the required section plan from the named path.
- Use the previous summary only if continuity matters for the current turn.
- Fail if the required section plan is missing.

## Inputs

### Section Plan

- Source: File
- Path: `section_root/_authoring/SECTION_PLAN.md`
- Shape: Markdown document
- Requirement: Required

Read this file before changing section planning.

### Previous Summary

- Source: File
- Path: `section_root/_authoring/PREVIOUS_SUMMARY.md`
- Shape: Markdown document
- Requirement: Advisory

Use this only if continuity with earlier work matters for the current turn.
````

## File: examples/08_inputs/ref/prompt_input_agent/AGENTS.md
````markdown
# Prompt Input Agent

Core job: summarize the current issue from prompt-provided input.

## Your Job

- Read the current issue from the prompt.
- Summarize it clearly and briefly.

## Inputs

### Current Issue

- Source: Prompt
- Shape: Markdown document
- Requirement: Required

This content is already present in the invocation prompt.
````

## File: examples/09_outputs/ref/turn_response_output_agent/AGENTS.md
````markdown
# Turn Response Output Agent

Core job: return a short issue summary in the turn response.

## Your Job

- Return the issue summary in the turn response.

## Outputs

### Issue Summary Response

- Target: TurnResponse
- Shape: Issue Summary Text
- Requirement: Required

#### Purpose

Give a short human-readable summary back in the turn.

#### Expected Structure

- State the issue in one or two sentences.
- End with the main blocker or next step if one matters.
````

## File: examples/13_critic_protocol/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "critic protocol stays expressible with existing primitives"
status = "active"
kind = "render_contract"
agent = "AcceptanceCritic"
assertion = "exact_lines"
expected_lines = [
  "Core job: review the current dossier, issue an explicit verdict, and route the same issue honestly.",
  "",
  "## Your Job",
  "",
  "Review the current dossier against the current issue plan.",
  "Return one explicit verdict.",
  "Write the gate log that supports that verdict.",
  "Route the issue to the honest next owner.",
  "Stop and escalate instead of guessing when required review inputs are missing.",
  "",
  "## Read First",
  "",
  "### Read Order",
  "",
  "Read Your Job first.",
  "Then read Workflow Core and How To Take A Turn.",
  "Then read Inputs, Outputs, Review Routing, When To Stop, Skills, and Standards And Support.",
  "",
  "### Current Review Scope",
  "",
  "Read the current issue plan, the current dossier, and the current validation record before you issue a verdict.",
  "",
  "## Workflow Core",
  "",
  "### Same-Issue Review",
  "",
  "Keep review on the same issue as the producer turn.",
  "Judge the current named files, not stale copies or remembered context.",
  "",
  "### Verdict Rule",
  "",
  "Return one explicit verdict: `accept` or `changes requested`.",
  "Name the honest next owner for that verdict.",
  "",
  "### Handoff Rule",
  "",
  "If the work is accepted, route the issue forward.",
  "If the work is not ready, route it back to the honest producer.",
  "If the route is unclear, send it to Project Lead instead of guessing.",
  "",
  "## How To Take A Turn",
  "",
  "### Turn Sequence",
  "",
  "Read the required review inputs.",
  "Check the work against the current issue plan and the named validation record.",
  "Write the verdict and gate log.",
  "Route the issue to the honest next owner and stop.",
  "",
  "### Guardrails",
  "",
  "Do not approve work you cannot support from the current review inputs.",
  "Do not bounce the work for vague reasons.",
  "Do not guess when required review inputs are missing.",
  "",
  "## Inputs",
  "",
  "### Current Issue Plan",
  "",
  "- Source: Prompt",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "Use the current issue plan to understand the intended acceptance bar and next normal owner.",
  "",
  "### Section Dossier",
  "",
  "- Source: File",
  "- Path: `section_root/_authoring/SECTION_DOSSIER.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "Review the current dossier as the main artifact under review.",
  "",
  "### Dossier Validation Record",
  "",
  "- Source: File",
  "- Path: `section_root/_authoring/DOSSIER_VALIDATION.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "Use the current validation record to understand what checks ran and what passed or failed.",
  "",
  "## Outputs",
  "",
  "### Critic Review Output",
  "",
  "- Review Verdict: `section_root/_authoring/REVIEW_VERDICT.md`",
  "- Review Verdict Shape: Markdown Document",
  "- Run Gate Log: `section_root/_authoring/RUN_GATE_LOG.md`",
  "- Run Gate Log Shape: Markdown Document",
  "",
  "#### Must Include",
  "",
  "##### Verdict",
  "",
  "REVIEW_VERDICT.md must state `accept` or `changes requested` explicitly.",
  "",
  "##### Next Owner",
  "",
  "REVIEW_VERDICT.md must name the honest next owner.",
  "",
  "##### Reason",
  "",
  "REVIEW_VERDICT.md must give the short reason for the verdict and route.",
  "",
  "##### Gate Results",
  "",
  "RUN_GATE_LOG.md must list every failed gate or say that all named gates passed.",
  "",
  "##### Evidence Used",
  "",
  "RUN_GATE_LOG.md must record the validation evidence the critic actually relied on.",
  "",
  "#### Standalone Read",
  "",
  "A downstream reader should be able to read REVIEW_VERDICT.md and RUN_GATE_LOG.md and understand the verdict, route, and review basis.",
  "",
  "## Review Routing",
  "",
  "### Next Owner If Accepted",
  "",
  "If accepted -> ProjectLead",
  "",
  "### If The Work Is Not Ready",
  "",
  "If changes are required -> SectionAuthor",
  "If the route is unclear -> ProjectLead",
  "",
  "## When To Stop",
  "",
  "### Stop Here If",
  "",
  "Stop when the verdict is explicit, the next owner is clear, and the gate log matches the actual review basis.",
  "",
  "### Hard Stop Rule",
  "",
  "If a required review input is missing, stop and escalate.",
  "Do not approve from memory, stale notes, or old copies.",
  "",
  "## Skills",
  "",
  "### Can Run",
  "",
  "#### lesson-review-checklist",
  "",
  "##### Purpose",
  "",
  "Run the repo's current checklist for critic review of a section dossier.",
  "",
  "##### Use When",
  "",
  "Use this when the role needs a repeatable review pass against the current dossier contract.",
  "",
  "## Standards And Support",
  "",
  "### Review Rules",
  "",
  "Judge only the work that is currently in scope for this issue.",
  "A failed gate should name the actual missing or incorrect thing.",
  "",
  "### Evidence Rule",
  "",
  "Record the evidence you actually relied on in the gate log.",
  "If the validation record is missing or stale, do not pretend the work was validated.",
  "",
  "### Diff Tools",
  "",
  "Use repo-owned diff tools when you need to isolate what changed in the current dossier.",
  "",
  "### Validator Runner",
  "",
  "Use the named dossier validator when the validation record depends on a rerun.",
  "Record the exact command and result in RUN_GATE_LOG.md.",
]
````

## File: examples/14_handoff_truth/build_ref/section_author/AGENTS.md
````markdown
Core job: turn the current brief into the current dossier, leave one honest handoff, and route the same issue truthfully.

## Your Job

Read the current issue plan and current brief before you write.
Use prior review notes only as continuity help, not as proof.
Write the current dossier and current validation record.
Leave one handoff comment that names the exact files to use now.
Say plainly whether current review files apply yet.
Route the issue to the honest next owner.

## Inputs

### Current Issue Plan

- Source: Prompt
- Shape: Markdown Document
- Requirement: Required

Use the current issue plan to understand the intended lane and current scope.

### Section Brief

- Source: File
- Path: `section_root/_authoring/BRIEF.md`
- Shape: Markdown Document
- Requirement: Required

Use the current brief as the upstream scope for this turn.

### Prior Review Notes

- Source: File
- Path: `section_root/_authoring/PRIOR_REVIEW_NOTES.md`
- Shape: Markdown Document
- Requirement: Advisory

Use this only for continuity when it exists.
Do not treat it as proof of the current turn.

## Outputs

### Section Dossier Output

- Current Dossier: `section_root/_authoring/SECTION_DOSSIER.md`
- Current Dossier Shape: Markdown Document
- Validation Record: `section_root/_authoring/DOSSIER_VALIDATION.md`
- Validation Record Shape: Markdown Document
- Requirement: Required

#### Must Include

##### Current Dossier

SECTION_DOSSIER.md must reflect the current section proposal for this turn.

##### Validation Record

DOSSIER_VALIDATION.md must say what checks ran, what passed or failed, or what did not run yet.

#### Standalone Read

A downstream reader should be able to read SECTION_DOSSIER.md and DOSSIER_VALIDATION.md and understand the current proposal and its validation basis.

### Section Author Handoff

- Target: Issue Comment
- Issue: `CURRENT_ISSUE`
- Shape: Handoff Comment Text
- Requirement: Required

#### Must Include

##### What Changed

Say what changed in this turn.

##### Use Now

Name the exact current files the next owner should read now.

##### Review Files

Either name the current review files explicitly or say plainly that no current review files apply yet.

##### Next Owner

Name the honest next owner.

#### Standalone Read

A downstream reader should be able to read this comment alone and understand what changed, which files are current now, whether review files apply, and who owns next.

#### Example

- changed: rewrote the dossier scope and added the validation record
- use now: SECTION_DOSSIER.md and DOSSIER_VALIDATION.md
- review files: no current review files apply yet
- next owner: AcceptanceCritic

## Handoff Routing

### Next Owner If Ready

If the dossier is ready for review -> AcceptanceCritic

### If The Work Is Not Ready

If the route is unclear or the current brief is missing -> ProjectLead

## When To Stop

### Stop Here If

Stop when the handoff comment names the exact files to use now and the next owner is clear.

### Hard Stop Rule

If the current brief is missing, stop and escalate.
Do not point the next owner at stale notes, old copies, or a folder name instead of exact files.
````

## File: examples/14_handoff_truth/ref/section_author/AGENTS.md
````markdown
# Section Author

Core job: turn the current brief into the current dossier, leave one honest handoff, and route the same issue truthfully.

## Your Job

- Read the current issue plan and current brief before you write.
- Use prior review notes only as continuity help, not as proof.
- Write the current dossier and current validation record.
- Leave one handoff comment that names the exact files to use now.
- Say plainly whether current review files apply yet.
- Route the issue to the honest next owner.

## Inputs

### Current Issue Plan

- Source: Prompt
- Shape: Markdown document
- Requirement: Required

Use the current issue plan to understand the intended lane and current scope.

### Section Brief

- Source: File
- Path: `section_root/_authoring/BRIEF.md`
- Shape: Markdown document
- Requirement: Required

Use the current brief as the upstream scope for this turn.

### Prior Review Notes

- Source: File
- Path: `section_root/_authoring/PRIOR_REVIEW_NOTES.md`
- Shape: Markdown document
- Requirement: Advisory

Use this only for continuity when it exists.
Do not treat it as proof of the current turn.

## Outputs

### Section Dossier Output

- Current Dossier: `section_root/_authoring/SECTION_DOSSIER.md`
- Current Dossier Shape: MarkdownDocument
- Validation Record: `section_root/_authoring/DOSSIER_VALIDATION.md`
- Validation Record Shape: MarkdownDocument
- Requirement: Required

#### Must Include

- Current Dossier: `SECTION_DOSSIER.md` must reflect the current section proposal for this turn.
- Validation Record: `DOSSIER_VALIDATION.md` must say what checks ran, what passed or failed, or what did not run yet.

#### Standalone Read

A downstream reader should be able to read `SECTION_DOSSIER.md` and `DOSSIER_VALIDATION.md` and understand the current proposal and its validation basis.

### Section Author Handoff

- Target: Issue Comment
- Issue: `CURRENT_ISSUE`
- Shape: Handoff Comment Text
- Requirement: Required

#### Must Include

- What Changed: say what changed in this turn.
- Use Now: name the exact current files the next owner should read now.
- Review Files: either name the current review files explicitly or say plainly that no current review files apply yet.
- Next Owner: name the honest next owner.

#### Standalone Read

A downstream reader should be able to read this comment alone and understand what changed, which files are current now, whether review files apply, and who owns next.

#### Example

```text
- changed: rewrote the dossier scope and added the validation record
- use now: SECTION_DOSSIER.md and DOSSIER_VALIDATION.md
- review files: no current review files apply yet
- next owner: AcceptanceCritic
```

## Handoff Routing

### Next Owner If Ready

- If the dossier is ready for review -> AcceptanceCritic

### If The Work Is Not Ready

- If the route is unclear or the current brief is missing -> ProjectLead

## When To Stop

### Stop Here If

Stop when the handoff comment names the exact files to use now and the next owner is clear.

### Hard Stop Rule

- If the current brief is missing, stop and escalate.
- Do not point the next owner at stale notes, old copies, or a folder name instead of exact files.
````

## File: examples/15_workflow_body_refs/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "workflow section bodies mix prose with local and imported declaration refs"
status = "active"
kind = "render_contract"
agent = "WorkflowSectionRefsDemo"
assertion = "exact_lines"
approx_ref = "ref/workflow_section_refs_demo/AGENTS.md"
expected_lines = [
  "Keep workflow guidance readable while still pointing directly at the typed contracts it depends on.",
  "",
  "## Immediate Local Read",
  "",
  "### Read Now",
  "",
  "Start with the current routing truth.",
  "",
  "- Current Issue Plan",
  "- Latest Named Files Comment",
  "- Track Metadata",
  "",
  "If current concepts exist for this section, read them before nearby context.",
  "",
  "- Current Concepts",
  "",
  "### When You Finish",
  "",
  "Leave the next owner one current output contract instead of a vague note.",
  "",
  "- Final Handoff Comment",
  "",
  "## Inputs",
  "",
  "### Current Issue Plan",
  "",
  "- Source: Prompt",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "Use the current issue plan to confirm the intended owner and next step.",
  "",
  "### Latest Named Files Comment",
  "",
  "- Source: File",
  "- Path: `track_root/_authoring/LATEST_NAMED_FILES_COMMENT.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "Use this comment to confirm which files are current now.",
  "",
  "### Track Metadata",
  "",
  "- Source: File",
  "- Path: `track_root/track.meta.json`",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "Use this file as the current track metadata truth.",
  "",
  "### Current Concepts",
  "",
  "- Source: File",
  "- Path: `section_root/_authoring/CONCEPTS.md`",
  "- Shape: Markdown Document",
  "- Requirement: Advisory",
  "",
  "Use this only when the section already has live concepts to preserve.",
  "",
  "## Outputs",
  "",
  "### Final Handoff Comment",
  "",
  "- Target: Turn Response",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "Use this output contract when you leave the next owner one clear update.",
]

[[cases]]
name = "bare workflow refs are rejected in workflow section bodies"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_WORKFLOW_REF.prompt"
agent = "InvalidWorkflowBodyRefsAgent"
exception_type = "CompileError"
error_code = "E271"
message_contains = [
  "Workflow refs are not allowed in workflow section bodies",
  "use `use` for workflow composition",
  "SharedRead",
]

[[cases]]
name = "ambiguous bare workflow section refs fail loud"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_AMBIGUOUS_REF.prompt"
agent = "InvalidAmbiguousBodyRefsAgent"
exception_type = "CompileError"
error_code = "E270"
message_contains = [
  "Ambiguous workflow section declaration ref",
  "SharedThing",
  "input declaration",
  "skill declaration",
]
````

## File: examples/17_agent_mentions/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "workflow mentions render local and imported concrete agent names"
status = "active"
kind = "render_contract"
agent = "AgentMentionsDemo"
assertion = "exact_lines"
approx_ref = "ref/agent_mentions_demo/AGENTS.md"
expected_lines = [
  "Keep owner names readable in workflow prose without pretending that a mention is a route.",
  "",
  "## Handoff Mentions",
  "",
  "### Owner Names In Prose",
  "",
  "If the route is unclear, return the same issue to ProjectLead.",
  "If the work is ready for review, hand it to AcceptanceCritic.",
  "",
  "### Owner Names As Block Mentions",
  "",
  "- ProjectLead",
  "- AcceptanceCritic",
  "",
  "### Actual Transition",
  "",
  "Naming an owner is not a route by itself.",
  "If the work is ready for review -> AcceptanceCritic",
]

[[cases]]
name = "abstract agent mentions are rejected"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_ABSTRACT_AGENT_MENTION.prompt"
agent = "InvalidAbstractAgentMentionDemo"
exception_type = "CompileError"
error_code = "E272"
message_contains = [
  "Abstract agent refs are not allowed",
  "workflow strings",
  "shared.roles.AbstractEscalationOwner",
]

[[cases]]
name = "workflow mentions are still rejected"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_WORKFLOW_MENTION.prompt"
agent = "InvalidWorkflowMentionDemo"
exception_type = "CompileError"
error_code = "E271"
message_contains = [
  "Workflow refs are not allowed in workflow strings",
  "use `use` for workflow composition",
  "SharedRead",
]

[[cases]]
name = "ambiguous agent mention refs fail loud"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_AMBIGUOUS_AGENT_REF.prompt"
agent = "InvalidAmbiguousAgentMentionDemo"
exception_type = "CompileError"
error_code = "E270"
message_contains = [
  "Ambiguous workflow section declaration ref",
  "SharedThing",
  "agent declaration",
  "input declaration",
]
````

## File: examples/18_rich_io_buckets/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "rich io buckets render prose, titled groups, and typed refs"
status = "active"
kind = "render_contract"
agent = "RichIoBucketAgent"
assertion = "exact_lines"
expected_lines = [
  "Core job: gather the section inputs and publish the current dossier truth.",
  "",
  "## Your Job",
  "",
  "Use the current plan as truth and keep prior review notes as continuity help only.",
  "Always write the dossier file before you summarize the turn.",
  "",
  "## Inputs",
  "",
  "Read these inputs in order.",
  "",
  "### Planning Truth",
  "",
  "#### Current Section Plan",
  "",
  "- Source: File",
  "- Path: `section_root/_authoring/SECTION_PLAN.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "##### Notes",
  "",
  "Treat the current plan as the live section baseline.",
  "",
  "### Continuity Only",
  "",
  "Use prior review notes only as continuity help, not as proof.",
  "",
  "#### Prior Review Notes",
  "",
  "- Source: File",
  "- Path: `section_root/_authoring/PRIOR_REVIEW_NOTES.md`",
  "- Shape: Markdown Document",
  "- Requirement: Advisory",
  "",
  "## Outputs",
  "",
  "Always produce these outputs when you own dossier work.",
  "The file artifact is the durable truth. The turn summary points at that truth.",
  "",
  "### File Truth",
  "",
  "Write this to disk before you summarize the turn.",
  "",
  "#### Dossier File",
  "",
  "- Target: File",
  "- Path: `section_root/_authoring/dossier_engineer.md`",
  "- Shape: Dossier Document",
  "- Requirement: Required",
  "",
  "##### Standalone Read",
  "",
  "A downstream reader should be able to read dossier_engineer.md alone and understand the current dossier truth.",
  "",
  "### Turn Summary",
  "",
  "Use the turn response to say what changed and where the durable file lives.",
  "",
  "#### Dossier Summary",
  "",
  "- Target: Turn Response",
  "- Shape: Turn Summary Text",
  "- Requirement: Required",
  "",
  "##### Purpose",
  "",
  "Summarize what changed and point the reader at dossier_engineer.md.",
]
approx_ref = "ref/rich_io_bucket_agent/AGENTS.md"

[[cases]]
name = "scalar keyed items fail loud inside outputs buckets"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_OUTPUT_BUCKET_SCALAR.prompt"
agent = "InvalidOutputBucketScalar"
exception_type = "CompileError"
error_code = "E299"
message_contains = [
  "Scalar keyed items are not allowed in outputs field `Outputs`",
  "notes",
]

[[cases]]
name = "route lines fail loud inside outputs buckets"
status = "active"
kind = "parse_fail"
prompt = "prompts/INVALID_OUTPUT_BUCKET_ROUTE.prompt"
exception_type = "ParseError"
error_code = "E101"
message_contains = [
  "Unexpected token",
  "\"Send next\"",
]

[[cases]]
name = "inline bodies on output refs fail loud"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_OUTPUT_BUCKET_REF_BODY.prompt"
agent = "InvalidOutputBucketRefBody"
exception_type = "CompileError"
error_code = "E299"
message_contains = [
  "Declaration refs cannot define inline bodies in outputs field `Outputs`",
  "DossierFile",
]

[[cases]]
name = "wrong-kind refs fail loud inside outputs buckets"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_OUTPUT_BUCKET_WRONG_KIND_REF.prompt"
agent = "InvalidOutputBucketWrongKindRef"
exception_type = "CompileError"
error_code = "E299"
message_contains = [
  "Outputs refs must resolve to output declarations, not input declarations",
  "CurrentSectionPlan",
]
````

## File: examples/19_emphasized_prose_lines/prompts/AGENTS.prompt
````
# This example adds one narrow prose-line feature:
# fixed emphasis labels can lead certain prose lines without embedding raw markdown.
#
# The supported labels are `required`, `important`, `warning`, and `note`.
# They work in workflow prose, role prose, and record prose surfaces.
# Emphasis lines on those prose surfaces still support `{{...}}` interpolation.

input CurrentPlan: "Current Plan"
    source: File
        path: "track_root/current-plan.md"
    shape: MarkdownDocument
    requirement: Required
    note "Use this file as the current plan truth."


agent EmphasizedProseLinesDemo:
    role: "Role"
        required "Read this file end to end before you act."
        important "Keep the current plan as truth."

    workflow: "Instructions"
        warning "Start from {{CurrentPlan:title}}, not from memory."
        note "Treat old notes as continuity help only."

        final_check: "Final Check"
            required "Confirm the path at `{{CurrentPlan:source.path}}` before you route."
            note "Do not guess from stale notes or old copies."

    inputs: "Inputs"
        important "Read these inputs before you write anything."
        CurrentPlan
````

## File: examples/20_authored_prose_interpolation/prompts/AGENTS.prompt
````
# This example widens `{{...}}` from workflow-only prose to authored prose surfaces.
#
# Titles and config metadata stay literal.
# Authored prose interpolation now works in:
# - role prose
# - workflow prose
# - record prose
# - skill purpose
# - skill reference reason
# - route labels

workflow ReadFirst: "Read First"
    start_here: "Start Here"
        "Read {{CurrentPlan}} before you act."


workflow HowToRoute: "How To Route"
    routing_rules: "Routing Rules"
        "Leave the next owner one {{TurnResponse}}."
        route "If {{ProjectLead}} must step in" -> ProjectLead


input CurrentPlan: "Current Plan"
    source: File
        path: "track_root/current-plan.md"
    shape: MarkdownDocument
    requirement: Required
    "Use this as the current plan truth."


output TurnResponse: "Turn Response"
    target: TurnResponse
    shape: MarkdownDocument
    requirement: Required
    "Use this output when you leave the next owner one clear update."


skill GroundingSkill: "Grounding Skill"
    purpose: "Ground new claims against {{CurrentPlan}} before you write."

    provides: "Provides"
        "Keep `{{CurrentPlan:source.path}}` in scope when you cite current plan truth."


agent ProjectLead:
    role: "Project Lead"


agent AuthoredProseInterpolationDemo:
    role: "Use `{{CurrentPlan:source.path}}` as the current plan truth before you act."

    read_first: ReadFirst

    inputs: "Inputs"
        "Read {{CurrentPlan}} before you write."

        planning_truth: "Planning Truth"
            "Keep the current plan at `{{CurrentPlan:source.path}}` in scope."
            CurrentPlan

    skills: "Skills"
        can_run: "Can Run"
            skill grounding: GroundingSkill
                reason: "Ask {{ProjectLead}} for an owner decision only when the plan truly needs one."

    outputs: "Outputs"
        TurnResponse

    ending_your_turn: HowToRoute
````

## File: examples/20_authored_prose_interpolation/prompts/INVALID_ROUTE_LABEL_NONSCALAR.prompt
````
workflow InvalidRouteLabelInterpolation: "Invalid Route Label Interpolation"
    routing_rules: "Routing Rules"
        route "If {{CurrentPlan:source.path.file_name}} is missing" -> ProjectLead


input CurrentPlan: "Current Plan"
    source: File
        path: "track_root/current-plan.md"
    shape: MarkdownDocument
    requirement: Required


agent ProjectLead:
    role: "Project Lead"


agent InvalidRouteLabelInterpolationDemo:
    role: "This prompt exists only to trigger the compile-fail contract."

    ending_your_turn: InvalidRouteLabelInterpolation
````

## File: examples/20_authored_prose_interpolation/prompts/INVALID_SKILL_PURPOSE_WORKFLOW_REF.prompt
````
workflow SharedRead: "Shared Read"
    "Read this first."


skill BrokenSkill: "Broken Skill"
    purpose: "Start with {{SharedRead}} before you act."


agent InvalidSkillPurposeInterpolationDemo:
    role: "This prompt exists only to trigger the compile-fail contract."

    skills: "Skills"
        can_run: "Can Run"
            skill broken: BrokenSkill
                requirement: Advisory
````

## File: examples/20_authored_prose_interpolation/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "authored prose interpolates across role, record, skill, and route surfaces"
status = "active"
kind = "render_contract"
agent = "AuthoredProseInterpolationDemo"
assertion = "exact_lines"
approx_ref = "ref/AGENTS.md"
expected_lines = [
  "Use `track_root/current-plan.md` as the current plan truth before you act.",
  "",
  "## Read First",
  "",
  "### Start Here",
  "",
  "Read Current Plan before you act.",
  "",
  "## Inputs",
  "",
  "Read Current Plan before you write.",
  "",
  "### Planning Truth",
  "",
  "Keep the current plan at `track_root/current-plan.md` in scope.",
  "",
  "#### Current Plan",
  "",
  "- Source: File",
  "- Path: `track_root/current-plan.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "Use this as the current plan truth.",
  "",
  "## Skills",
  "",
  "### Can Run",
  "",
  "#### Grounding Skill",
  "",
  "##### Purpose",
  "",
  "Ground new claims against Current Plan before you write.",
  "",
  "##### Provides",
  "",
  "Keep `track_root/current-plan.md` in scope when you cite current plan truth.",
  "",
  "##### Reason",
  "",
  "Ask ProjectLead for an owner decision only when the plan truly needs one.",
  "",
  "## Outputs",
  "",
  "### Turn Response",
  "",
  "- Target: Turn Response",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "Use this output when you leave the next owner one clear update.",
  "",
  "## How To Route",
  "",
  "### Routing Rules",
  "",
  "Leave the next owner one Turn Response.",
  "If ProjectLead must step in -> ProjectLead",
]

[[cases]]
name = "workflow refs stay rejected in skill purpose interpolation"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_SKILL_PURPOSE_WORKFLOW_REF.prompt"
agent = "InvalidSkillPurposeInterpolationDemo"
exception_type = "CompileError"
error_code = "E271"
message_contains = [
  "Workflow refs are not allowed in skill purpose",
  "use `use` for workflow composition",
  "SharedRead",
]

[[cases]]
name = "unknown interpolation fields fail loud in role prose"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_ROLE_FIELD_PATH.prompt"
agent = "InvalidRoleFieldPathInterpolationDemo"
exception_type = "CompileError"
error_code = "E273"
message_contains = [
  "Unknown addressable path on role prose",
  "CurrentPlan:source.missing",
]

[[cases]]
name = "route label interpolation paths must stay addressable"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_ROUTE_LABEL_NONSCALAR.prompt"
agent = "InvalidRouteLabelInterpolationDemo"
exception_type = "CompileError"
error_code = "E274"
message_contains = [
  "Addressable path must stay addressable on route labels",
  "CurrentPlan:source.path.file_name",
]

[[cases]]
name = "ambiguous refs fail loud in record prose interpolation"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_AMBIGUOUS_RECORD_PROSE.prompt"
agent = "InvalidAmbiguousRecordProseDemo"
exception_type = "CompileError"
error_code = "E270"
message_contains = [
  "Ambiguous inputs prose interpolation ref",
  "SharedThing",
  "input declaration",
  "skill declaration",
]
````

## File: examples/22_skills_block_inheritance/prompts/AGENTS.prompt
````
# This example adds inheritance and explicit patching for named `skills` blocks.
#
# The rules match workflow-style patching:
# - inherited entries must be accounted for exactly once
# - `inherit` keeps a parent entry as-is
# - `override` replaces a parent entry by key
#
# Individual skill entries now carry stable keys so top-level skills blocks can
# patch them cleanly.

skill GroundingSkill: "Grounding Skill"
    purpose: "Ground the current claim before you write."


skill CopyRewriteSkill: "Copy Rewrite Skill"
    purpose: "Rewrite reader-facing text without changing the underlying guide job."


skill FindSkills: "Find Skills"
    purpose: "Find the right repo skill before you guess."


skills BaseLessonSkills: "Skills"
    how_to_use: "How To Use"
        "Start with the skill that directly matches the current job."

    skill primary: GroundingSkill
        requirement: Required

    support: "Support"
        skill find_skills: FindSkills
            requirement: Advisory


skills CopywriterSkills[BaseLessonSkills]: "Skills"
    inherit how_to_use

    override primary: CopyRewriteSkill
        requirement: Required
        reason: "For this role, rewriting is the lead capability."

    override support: "Support"
        skill find_skills: FindSkills
            requirement: Advisory

        skill grounding: GroundingSkill
            requirement: Advisory


agent SkillsInheritanceDemo:
    role: "Use the inherited skills block for this role."
    skills: CopywriterSkills
````

## File: examples/27_addressable_record_paths/ref/addressable_record_paths_demo/AGENTS.md
````markdown
Keep deep contract paths readable without flattening the contract.

## Read First

### Read Now

- Section Concepts Terms File
- Concept Ladder Table
- Concept Ladder Table

Build Tables inside Section Concepts Terms File before you finalize `section_root/_authoring/SECTION_CONCEPTS_AND_TERMS.md`.

## Skills

### Can Run

#### Concepts Terms Skill

##### Purpose

Use Concept Ladder Table before you finalize the document.
- Canonical Table: Concept Ladder Table
- Canonical Path: `section_root/_authoring/SECTION_CONCEPTS_AND_TERMS.md`

## Outputs

### Section Concepts Terms File

- Target: File
- Path: `section_root/_authoring/SECTION_CONCEPTS_AND_TERMS.md`
- Shape: Markdown Document
- Requirement: Required

#### Must Include

##### Analysis

###### Tables

####### Concept Ladder Table

Map what earlier sections already taught and what the learner should learn next.

##### Concept IDs

Keep ids stable when the section already has accepted concepts.
````

## File: examples/27_addressable_record_paths/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "deep record paths resolve titled nested items and scalar leaves"
status = "active"
kind = "render_contract"
agent = "AddressableRecordPathsDemo"
assertion = "exact_lines"
approx_ref = "ref/addressable_record_paths_demo/AGENTS.md"
expected_lines = [
  "Keep deep contract paths readable without flattening the contract.",
  "",
  "## Read First",
  "",
  "### Read Now",
  "",
  "- Section Concepts Terms File",
  "- Concept Ladder Table",
  "- Concept Ladder Table",
  "",
  "Build Tables inside Section Concepts Terms File before you finalize `section_root/_authoring/SECTION_CONCEPTS_AND_TERMS.md`.",
  "",
  "## Skills",
  "",
  "### Can Run",
  "",
  "#### Concepts Terms Skill",
  "",
  "##### Purpose",
  "",
  "Use Concept Ladder Table before you finalize the document.",
  "- Canonical Table: Concept Ladder Table",
  "- Canonical Path: `section_root/_authoring/SECTION_CONCEPTS_AND_TERMS.md`",
  "",
  "## Outputs",
  "",
  "### Section Concepts Terms File",
  "",
  "- Target: File",
  "- Path: `section_root/_authoring/SECTION_CONCEPTS_AND_TERMS.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "#### Must Include",
  "",
  "##### Analysis",
  "",
  "###### Tables",
  "",
  "####### Concept Ladder Table",
  "",
  "Map what earlier sections already taught and what the learner should learn next.",
  "",
  "##### Concept IDs",
  "",
  "Keep ids stable when the section already has accepted concepts.",
]

[[cases]]
name = "unknown deep record path fails loud"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_UNKNOWN_RECORD_PATH.prompt"
agent = "InvalidUnknownRecordPathDemo"
exception_type = "CompileError"
error_code = "E273"
message_contains = [
  "Unknown addressable path on workflow strings",
  "SectionConceptsTermsFileOutput:must_include.analysis.tables.missing_table",
]

[[cases]]
name = "deep record path cannot walk past a scalar leaf"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_NON_ADDRESSABLE_RECORD_PATH.prompt"
agent = "InvalidNonAddressableRecordPathDemo"
exception_type = "CompileError"
error_code = "E274"
message_contains = [
  "Addressable path must stay addressable on workflow strings",
  "SectionConceptsTermsFileOutput:target.path.file_name",
]
````

## File: examples/30_law_route_only_turns/ref/route_only_turns_demo/AGENTS.md
````markdown
Keep route-only work explicit when no durable artifact is current.

## Route-Only Triage

Handle turns that can only stop and reroute.

This pass runs only when current handoff is missing or current handoff is unclear.

If current handoff is missing:
- There is no current artifact for this turn.
- Stop: Current handoff is missing.
- Route the same issue back to RoutingOwner.

If current handoff is unclear:
- There is no current artifact for this turn.
- Stop: Current handoff is unclear.
- Route the same issue back to RoutingOwner.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether the current handoff is missing or unclear.

## Outputs

### Coordination Comment

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Standalone Read

A downstream owner should be able to read this comment alone and understand that no current artifact was carried forward.
````

## File: examples/30_law_route_only_turns/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "law can express route-only turns with no current artifact"
status = "active"
kind = "render_contract"
agent = "RouteOnlyTurnsDemo"
assertion = "exact_lines"
approx_ref = "ref/route_only_turns_demo/AGENTS.md"
expected_lines = [
  "Keep route-only work explicit when no durable artifact is current.",
  "",
  "## Route-Only Triage",
  "",
  "Handle turns that can only stop and reroute.",
  "",
  "This pass runs only when current handoff is missing or current handoff is unclear.",
  "",
  "If current handoff is missing:",
  "- There is no current artifact for this turn.",
  "- Stop: Current handoff is missing.",
  "- Route the same issue back to RoutingOwner.",
  "",
  "If current handoff is unclear:",
  "- There is no current artifact for this turn.",
  "- Stop: Current handoff is unclear.",
  "- Route the same issue back to RoutingOwner.",
  "",
  "## Inputs",
  "",
  "### Current Handoff",
  "",
  "- Source: Prompt",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "Use the host-provided handoff facts that say whether the current handoff is missing or unclear.",
  "",
  "## Outputs",
  "",
  "### Coordination Comment",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
  "",
  "#### Standalone Read",
  "",
  "A downstream owner should be able to read this comment alone and understand that no current artifact was carried forward.",
]

[[cases]]
name = "current none cannot coexist with current artifact in one active branch"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_CURRENT_NONE_AND_CURRENT_ARTIFACT.prompt"
agent = "InvalidCurrentNoneAndCurrentArtifact"
exception_type = "CompileError"
error_code = "E332"
message_contains = [
  "Multiple current-subject forms",
  "current none",
  "current artifact",
]

[[cases]]
name = "every active law branch still needs one current subject"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_ACTIVE_BRANCH_WITHOUT_CURRENT.prompt"
agent = "InvalidActiveBranchWithoutCurrent"
exception_type = "CompileError"
error_code = "E331"
message_contains = [
  "Missing current-subject form",
]

[[cases]]
name = "route statements still require labels"
status = "active"
kind = "parse_fail"
prompt = "prompts/INVALID_ROUTE_WITHOUT_LABEL.prompt"
exception_type = "ParseError"
error_code = "E131"
message_contains = [
  "Missing route label",
]

[[cases]]
name = "route statements still require explicit targets"
status = "active"
kind = "parse_fail"
prompt = "prompts/INVALID_ROUTE_WITHOUT_TARGET.prompt"
exception_type = "ParseError"
error_code = "E132"
message_contains = [
  "Missing route target",
]
````

## File: examples/31_currentness_and_trust_surface/ref/current_approved_plan_demo/AGENTS.md
````markdown
Carry one portable current artifact through a declared handoff field.

## Carry Current Truth

Keep one current artifact explicit and portable.

Current artifact: Approved Plan.

## Inputs

### Approved Plan

- Source: File
- Path: `unit_root/_authoring/APPROVED_PLAN.md`
- Shape: Markdown Document
- Requirement: Required

## Outputs

### Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Trust Surface

- Current Artifact

#### Standalone Read

A downstream owner must be able to read this output alone and know which artifact is current now.
````

## File: examples/31_currentness_and_trust_surface/ref/current_section_metadata_demo/AGENTS.md
````markdown
Carry a newly produced artifact as the current downstream truth.

## Carry Current Truth

Keep one current artifact explicit and portable.

Current artifact: Section Metadata.

## Outputs

### Section Metadata

- Target: File
- Path: `unit_root/_authoring/section_metadata.json`
- Shape: Json Object
- Requirement: Required

### Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Trust Surface

- Current Artifact

#### Standalone Read

A downstream owner must be able to read this output alone and know which artifact is current now.
````

## File: examples/32_modes_and_match/prompts/AGENTS.prompt
````
enum EditMode: "Edit Mode"
    manifest_title: "manifest-title"
    section_summary: "section-summary"


input CurrentHandoff: "Current Handoff"
    source: Prompt
    shape: JsonObject
    requirement: Required
    "Use the host-provided handoff facts that say whether edit work is owed, which mode is active, and which preserve basis stays authoritative."


input ApprovedPlan: "Approved Plan"
    source: File
        path: "unit_root/_authoring/APPROVED_PLAN.md"
    shape: MarkdownDocument
    requirement: Required


input ApprovedStructure: "Approved Structure"
    source: File
        path: "unit_root/_authoring/APPROVED_STRUCTURE.md"
    shape: MarkdownDocument
    requirement: Required


output CoordinationHandoff: "Coordination Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

    current_artifact: "Current Artifact"
        "Name the one artifact that is current now."

    active_mode: "Active Mode"
        "Name the active mode for this pass."

    trust_surface:
        current_artifact
        active_mode

    standalone_read: "Standalone Read"
        "A downstream owner must be able to read this output alone and know which artifact is current now and which mode is active."


workflow ModeAwareEdit: "Mode-Aware Edit"
    "Edit in exactly one typed mode and carry that mode through the handoff."

    law:
        active when CurrentHandoff.owes_edit
        mode edit_mode = CurrentHandoff.active_mode as EditMode

        match edit_mode:
            EditMode.manifest_title:
                current artifact ApprovedPlan via CoordinationHandoff.current_artifact
                must CurrentHandoff.preserve_basis == ApprovedPlan

            EditMode.section_summary:
                current artifact ApprovedStructure via CoordinationHandoff.current_artifact
                must CurrentHandoff.preserve_basis == ApprovedStructure


agent ModeAwareEditDemo:
    role: "Edit in exactly one typed mode and carry that mode through the handoff."
    workflow: ModeAwareEdit
    inputs: "Inputs"
        CurrentHandoff
        ApprovedPlan
        ApprovedStructure
    outputs: "Outputs"
        CoordinationHandoff
````

## File: examples/32_modes_and_match/prompts/INVALID_ACTIVE_BRANCH_WITHOUT_CURRENT_AFTER_MATCH.prompt
````
enum EditMode: "Edit Mode"
    manifest_title: "manifest-title"
    section_summary: "section-summary"


input CurrentHandoff: "Current Handoff"
    source: Prompt
    shape: JsonObject
    requirement: Required


input ApprovedStructure: "Approved Structure"
    source: File
        path: "unit_root/_authoring/APPROVED_STRUCTURE.md"
    shape: MarkdownDocument
    requirement: Required


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

    trust_surface:
        current_artifact


workflow InvalidModeAwareEdit: "Mode-Aware Edit"
    law:
        mode edit_mode = CurrentHandoff.active_mode as EditMode

        match edit_mode:
            EditMode.manifest_title:
                current artifact ApprovedPlan via CoordinationHandoff.current_artifact

            EditMode.section_summary:
                must CurrentHandoff.preserve_basis == ApprovedStructure


agent InvalidActiveBranchWithoutCurrentAfterMatch:
    role: "Trigger a match arm with no current subject."
    workflow: InvalidModeAwareEdit
    inputs: "Inputs"
        CurrentHandoff
        ApprovedPlan
        ApprovedStructure
    outputs: "Outputs"
        CoordinationHandoff
````

## File: examples/32_modes_and_match/prompts/INVALID_DUPLICATE_CURRENT_IN_MATCH_ARM.prompt
````
enum EditMode: "Edit Mode"
    manifest_title: "manifest-title"
    section_summary: "section-summary"


input CurrentHandoff: "Current Handoff"
    source: Prompt
    shape: JsonObject
    requirement: Required


input ApprovedPlan: "Approved Plan"
    source: File
        path: "unit_root/_authoring/APPROVED_PLAN.md"
    shape: MarkdownDocument
    requirement: Required


input ApprovedStructure: "Approved Structure"
    source: File
        path: "unit_root/_authoring/APPROVED_STRUCTURE.md"
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


workflow InvalidModeAwareEdit: "Mode-Aware Edit"
    law:
        mode edit_mode = CurrentHandoff.active_mode as EditMode

        match edit_mode:
            EditMode.manifest_title:
                current artifact ApprovedPlan via CoordinationHandoff.current_artifact
                current artifact ApprovedStructure via CoordinationHandoff.current_artifact

            EditMode.section_summary:
                current artifact ApprovedStructure via CoordinationHandoff.current_artifact


agent InvalidDuplicateCurrentInMatchArm:
    role: "Trigger duplicate current bindings in one match arm."
    workflow: InvalidModeAwareEdit
    inputs: "Inputs"
        CurrentHandoff
        ApprovedPlan
        ApprovedStructure
    outputs: "Outputs"
        CoordinationHandoff
````

## File: examples/32_modes_and_match/prompts/INVALID_NONEXHAUSTIVE_MODE_MATCH.prompt
````
enum EditMode: "Edit Mode"
    manifest_title: "manifest-title"
    section_summary: "section-summary"


input CurrentHandoff: "Current Handoff"
    source: Prompt
    shape: JsonObject
    requirement: Required


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

    trust_surface:
        current_artifact


workflow InvalidModeAwareEdit: "Mode-Aware Edit"
    law:
        mode edit_mode = CurrentHandoff.active_mode as EditMode

        match edit_mode:
            EditMode.manifest_title:
                current artifact ApprovedPlan via CoordinationHandoff.current_artifact


agent InvalidNonexhaustiveModeMatch:
    role: "Trigger a nonexhaustive mode match."
    workflow: InvalidModeAwareEdit
    inputs: "Inputs"
        CurrentHandoff
        ApprovedPlan
    outputs: "Outputs"
        CoordinationHandoff
````

## File: examples/33_scope_and_exact_preservation/prompts/AGENTS.prompt
````
enum MetadataEditMode: "Metadata Edit Mode"
    name_only: "name-only"
    summary_refresh: "summary-refresh"


input CurrentHandoff: "Current Handoff"
    source: Prompt
    shape: JsonObject
    requirement: Required
    "Use the host-provided handoff facts that say which metadata edit mode is active."


input ApprovedPlan: "Approved Plan"
    source: File
        path: "unit_root/_authoring/APPROVED_PLAN.md"
    shape: MarkdownDocument
    requirement: Required


input ApprovedStructure: "Approved Structure"
    source: File
        path: "unit_root/_authoring/APPROVED_STRUCTURE.md"
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

    standalone_read: "Standalone Read"
        "A downstream owner must be able to read this output alone and know which artifact is current now."


workflow NarrowMetadataEdit: "Narrow Metadata Edit"
    "Keep narrow ownership explicit and preserve every unowned field."

    law:
        mode edit_mode = CurrentHandoff.active_mode as MetadataEditMode

        match edit_mode:
            MetadataEditMode.name_only:
                current artifact SectionMetadata via CoordinationHandoff.current_artifact
                own only SectionMetadata.name
                preserve exact SectionMetadata.* except SectionMetadata.name
                preserve decisions ApprovedPlan

            MetadataEditMode.summary_refresh:
                current artifact SectionMetadata via CoordinationHandoff.current_artifact
                own only {SectionMetadata.name, SectionMetadata.description}
                preserve exact SectionMetadata.* except {SectionMetadata.name, SectionMetadata.description}
                preserve decisions ApprovedStructure
                forbid {SectionMetadata.taxonomy, SectionMetadata.flags}


agent NarrowMetadataEditDemo:
    role: "Keep narrow ownership explicit and preserve every unowned field."
    workflow: NarrowMetadataEdit
    inputs: "Inputs"
        CurrentHandoff
        ApprovedPlan
        ApprovedStructure
    outputs: "Outputs"
        SectionMetadata
        CoordinationHandoff
````

## File: examples/33_scope_and_exact_preservation/prompts/INVALID_OWN_AND_EXACT_PRESERVE_OVERLAP.prompt
````
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
        own only SectionMetadata.name
        preserve exact SectionMetadata.*


agent InvalidOwnAndExactPreserveOverlap:
    role: "Trigger owned scope that overlaps exact preservation."
    workflow: InvalidNarrowMetadataEdit
    outputs: "Outputs"
        SectionMetadata
        CoordinationHandoff
````

## File: examples/33_scope_and_exact_preservation/prompts/INVALID_OWN_AND_FORBID_OVERLAP.prompt
````
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
        own only SectionMetadata.name
        forbid SectionMetadata.name


agent InvalidOwnAndForbidOverlap:
    role: "Trigger overlap between owned and forbidden scope."
    workflow: InvalidNarrowMetadataEdit
    outputs: "Outputs"
        SectionMetadata
        CoordinationHandoff
````

## File: examples/34_structure_mapping_and_vocabulary_preservation/prompts/INVALID_UNKNOWN_MAPPING_PRESERVE_TARGET.prompt
````
input SlotMapping: "Slot Mapping"
    source: File
        path: "unit_root/_authoring/slot_mapping.json"
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


workflow InvalidPreserveMapping: "Preserve Mapping"
    law:
        current artifact SlotMapping via CoordinationHandoff.current_artifact
        preserve mapping MissingMapping


agent InvalidUnknownMappingPreserveTarget:
    role: "Trigger an unknown mapping preserve target."
    workflow: InvalidPreserveMapping
    outputs: "Outputs"
        CoordinationHandoff
````

## File: examples/34_structure_mapping_and_vocabulary_preservation/prompts/INVALID_UNKNOWN_STRUCTURE_PRESERVE_TARGET.prompt
````
input ApprovedStructure: "Approved Structure"
    source: File
        path: "unit_root/_authoring/APPROVED_STRUCTURE.md"
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


workflow InvalidPreserveStructure: "Preserve Structure"
    law:
        current artifact ApprovedStructure via CoordinationHandoff.current_artifact
        preserve structure MissingStructure


agent InvalidUnknownStructurePreserveTarget:
    role: "Trigger an unknown structure preserve target."
    workflow: InvalidPreserveStructure
    outputs: "Outputs"
        CoordinationHandoff
````

## File: examples/34_structure_mapping_and_vocabulary_preservation/ref/preserve_mapping_demo/AGENTS.md
````markdown
Keep source-to-target mappings stable during a narrow update.

## Preserve Mapping

Current artifact: Slot Mapping.

Preserve mapping `SlotMapping`.

## Inputs

### Slot Mapping

- Source: File
- Path: `unit_root/_authoring/slot_mapping.json`
- Shape: Json Object
- Requirement: Required

## Outputs

### Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Trust Surface

- Current Artifact

#### Standalone Read

A downstream owner must be able to read this output alone and know which artifact remains current now.
````

## File: examples/34_structure_mapping_and_vocabulary_preservation/ref/preserve_structure_demo/AGENTS.md
````markdown
Preserve document skeletons while allowing a narrow wording pass.

## Preserve Structure

Current artifact: Approved Structure.

Preserve structure `ApprovedStructure`.

## Inputs

### Approved Structure

- Source: File
- Path: `unit_root/_authoring/APPROVED_STRUCTURE.md`
- Shape: Markdown Document
- Requirement: Required

## Outputs

### Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Trust Surface

- Current Artifact

#### Standalone Read

A downstream owner must be able to read this output alone and know which artifact remains current now.
````

## File: examples/34_structure_mapping_and_vocabulary_preservation/ref/preserve_vocabulary_demo/AGENTS.md
````markdown
Keep closed vocabulary stable while revising the surrounding guidance.

## Preserve Vocabulary

Current artifact: Review Template.

Preserve vocabulary `CriticVerdict`.

## Inputs

### Review Template

- Source: File
- Path: `unit_root/_authoring/review_template.md`
- Shape: Markdown Document
- Requirement: Required

## Outputs

### Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Trust Surface

- Current Artifact

#### Standalone Read

A downstream owner must be able to read this output alone and know which artifact remains current now.
````

## File: examples/34_structure_mapping_and_vocabulary_preservation/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "preserve structure can keep document skeletons stable"
status = "active"
kind = "render_contract"
agent = "PreserveStructureDemo"
assertion = "exact_lines"
approx_ref = "ref/preserve_structure_demo/AGENTS.md"
expected_lines = [
  "Preserve document skeletons while allowing a narrow wording pass.",
  "",
  "## Preserve Structure",
  "",
  "Current artifact: Approved Structure.",
  "",
  "Preserve structure `ApprovedStructure`.",
  "",
  "## Inputs",
  "",
  "### Approved Structure",
  "",
  "- Source: File",
  "- Path: `unit_root/_authoring/APPROVED_STRUCTURE.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "## Outputs",
  "",
  "### Coordination Handoff",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
  "",
  "#### Current Artifact",
  "",
  "Name the one artifact that is current now.",
  "",
  "#### Trust Surface",
  "",
  "- Current Artifact",
  "",
  "#### Standalone Read",
  "",
  "A downstream owner must be able to read this output alone and know which artifact remains current now.",
]

[[cases]]
name = "preserve mapping can keep source-to-target assignments stable"
status = "active"
kind = "render_contract"
agent = "PreserveMappingDemo"
assertion = "exact_lines"
approx_ref = "ref/preserve_mapping_demo/AGENTS.md"
expected_lines = [
  "Keep source-to-target mappings stable during a narrow update.",
  "",
  "## Preserve Mapping",
  "",
  "Current artifact: Slot Mapping.",
  "",
  "Preserve mapping `SlotMapping`.",
  "",
  "## Inputs",
  "",
  "### Slot Mapping",
  "",
  "- Source: File",
  "- Path: `unit_root/_authoring/slot_mapping.json`",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "## Outputs",
  "",
  "### Coordination Handoff",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
  "",
  "#### Current Artifact",
  "",
  "Name the one artifact that is current now.",
  "",
  "#### Trust Surface",
  "",
  "- Current Artifact",
  "",
  "#### Standalone Read",
  "",
  "A downstream owner must be able to read this output alone and know which artifact remains current now.",
]

[[cases]]
name = "preserve vocabulary can keep closed term sets stable"
status = "active"
kind = "render_contract"
agent = "PreserveVocabularyDemo"
assertion = "exact_lines"
approx_ref = "ref/preserve_vocabulary_demo/AGENTS.md"
expected_lines = [
  "Keep closed vocabulary stable while revising the surrounding guidance.",
  "",
  "## Preserve Vocabulary",
  "",
  "Current artifact: Review Template.",
  "",
  "Preserve vocabulary `CriticVerdict`.",
  "",
  "## Inputs",
  "",
  "### Review Template",
  "",
  "- Source: File",
  "- Path: `unit_root/_authoring/review_template.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "## Outputs",
  "",
  "### Coordination Handoff",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
  "",
  "#### Current Artifact",
  "",
  "Name the one artifact that is current now.",
  "",
  "#### Trust Surface",
  "",
  "- Current Artifact",
  "",
  "#### Standalone Read",
  "",
  "A downstream owner must be able to read this output alone and know which artifact remains current now.",
]

[[cases]]
name = "structure preservation targets must be addressable"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_UNKNOWN_STRUCTURE_PRESERVE_TARGET.prompt"
agent = "InvalidUnknownStructurePreserveTarget"
exception_type = "CompileError"
error_code = "E355"
message_contains = [
  "Preserve target is unknown",
  "MissingStructure",
]

[[cases]]
name = "mapping preservation targets must be addressable"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_UNKNOWN_MAPPING_PRESERVE_TARGET.prompt"
agent = "InvalidUnknownMappingPreserveTarget"
exception_type = "CompileError"
error_code = "E355"
message_contains = [
  "Preserve target is unknown",
  "MissingMapping",
]

[[cases]]
name = "vocabulary preservation targets must stay known"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_UNKNOWN_VOCABULARY_PRESERVE_TARGET.prompt"
agent = "InvalidUnknownVocabularyPreserveTarget"
exception_type = "CompileError"
error_code = "E355"
message_contains = [
  "Preserve target is unknown",
  "MissingVerdictEnum",
]
````

## File: examples/35_basis_roles_and_rewrite_evidence/prompts/INVALID_CURRENT_ARTIFACT_IGNORED_FOR_TRUTH.prompt
````
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


workflow InvalidRewriteAwarePolish: "Rewrite-Aware Polish"
    law:
        current artifact SectionMetadata via CoordinationHandoff.current_artifact
        ignore SectionMetadata for truth


agent InvalidCurrentArtifactIgnoredForTruth:
    role: "Trigger truth-ignore on the current artifact."
    workflow: InvalidRewriteAwarePolish
    outputs: "Outputs"
        SectionMetadata
        CoordinationHandoff
````

## File: examples/35_basis_roles_and_rewrite_evidence/prompts/INVALID_SUPPORT_ONLY_AND_IGNORE_COMPARISON_CONTRADICTION.prompt
````
input AcceptedPeerSet: "Accepted Peer Set"
    source: File
        path: "catalog/accepted_peers.json"
    shape: JsonObject
    requirement: Advisory


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


workflow InvalidRewriteAwarePolish: "Rewrite-Aware Polish"
    law:
        current artifact SectionMetadata via CoordinationHandoff.current_artifact
        support_only AcceptedPeerSet for comparison
        ignore AcceptedPeerSet for comparison


agent InvalidSupportOnlyAndIgnoreComparisonContradiction:
    role: "Trigger contradictory comparison basis roles."
    workflow: InvalidRewriteAwarePolish
    outputs: "Outputs"
        SectionMetadata
        CoordinationHandoff
````

## File: examples/35_basis_roles_and_rewrite_evidence/ref/rewrite_aware_polish_demo/AGENTS.md
````markdown
Separate comparison help, live truth, and rewrite evidence.

## Rewrite-Aware Polish

Current artifact: Section Metadata.

Accepted Peer Set is comparison-only support.

When CurrentHandoff.rewrite_regime is rewrite, ignore {`SectionMetadata.name`, `SectionMetadata.description`} for rewrite evidence.

Stale Metadata Notes does not count as truth for this pass.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether this pass is a rewrite.

### Accepted Peer Set

- Source: File
- Path: `catalog/accepted_peers.json`
- Shape: Json Object
- Requirement: Advisory

### Stale Metadata Notes

- Source: File
- Path: `unit_root/_authoring/stale_metadata_notes.md`
- Shape: Markdown Document
- Requirement: Advisory

## Outputs

### Section Metadata

- Target: File
- Path: `unit_root/_authoring/section_metadata.json`
- Shape: Json Object
- Requirement: Required

### Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Comparison Basis

Name any comparison-only inputs used in this pass.

#### Rewrite Evidence Exclusions

Name any fields whose old values do not count as rewrite evidence.

#### Trust Surface

- Current Artifact
- Comparison Basis
- Rewrite Evidence Exclusions on rewrite passes

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now, what was comparison-only, and what old wording no longer counts as rewrite evidence.
````

## File: examples/35_basis_roles_and_rewrite_evidence/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "basis roles can separate comparison help truth and rewrite evidence"
status = "active"
kind = "render_contract"
agent = "RewriteAwarePolishDemo"
assertion = "exact_lines"
approx_ref = "ref/rewrite_aware_polish_demo/AGENTS.md"
expected_lines = [
  "Separate comparison help, live truth, and rewrite evidence.",
  "",
  "## Rewrite-Aware Polish",
  "",
  "Current artifact: Section Metadata.",
  "",
  "Accepted Peer Set is comparison-only support.",
  "",
  "When CurrentHandoff.rewrite_regime is rewrite, ignore {`SectionMetadata.name`, `SectionMetadata.description`} for rewrite evidence.",
  "",
  "Stale Metadata Notes does not count as truth for this pass.",
  "",
  "## Inputs",
  "",
  "### Current Handoff",
  "",
  "- Source: Prompt",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "Use the host-provided handoff facts that say whether this pass is a rewrite.",
  "",
  "### Accepted Peer Set",
  "",
  "- Source: File",
  "- Path: `catalog/accepted_peers.json`",
  "- Shape: Json Object",
  "- Requirement: Advisory",
  "",
  "### Stale Metadata Notes",
  "",
  "- Source: File",
  "- Path: `unit_root/_authoring/stale_metadata_notes.md`",
  "- Shape: Markdown Document",
  "- Requirement: Advisory",
  "",
  "## Outputs",
  "",
  "### Section Metadata",
  "",
  "- Target: File",
  "- Path: `unit_root/_authoring/section_metadata.json`",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "### Coordination Handoff",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
  "",
  "#### Current Artifact",
  "",
  "Name the one artifact that is current now.",
  "",
  "#### Comparison Basis",
  "",
  "Name any comparison-only inputs used in this pass.",
  "",
  "#### Rewrite Evidence Exclusions",
  "",
  "Name any fields whose old values do not count as rewrite evidence.",
  "",
  "#### Trust Surface",
  "",
  "- Current Artifact",
  "- Comparison Basis",
  "- Rewrite Evidence Exclusions on rewrite passes",
  "",
  "#### Standalone Read",
  "",
  "A downstream owner must be able to read this output alone and know what is current now, what was comparison-only, and what old wording no longer counts as rewrite evidence.",
]

[[cases]]
name = "comparison support cannot also be ignored for comparison"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_SUPPORT_ONLY_AND_IGNORE_COMPARISON_CONTRADICTION.prompt"
agent = "InvalidSupportOnlyAndIgnoreComparisonContradiction"
exception_type = "CompileError"
error_code = "E362"
message_contains = [
  "Comparison-only basis contradiction",
]

[[cases]]
name = "the current artifact cannot be ignored for truth"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_CURRENT_ARTIFACT_IGNORED_FOR_TRUTH.prompt"
agent = "InvalidCurrentArtifactIgnoredForTruth"
exception_type = "CompileError"
error_code = "E361"
message_contains = [
  "Current artifact ignored for truth",
]
````

## File: examples/36_invalidation_and_rebuild/prompts/AGENTS.prompt
````
input CurrentHandoff: "Current Handoff"
    source: Prompt
    shape: JsonObject
    requirement: Required
    "Use the host-provided handoff facts that say whether structure changed, whether Section Review is invalidated, and whether rebuild work is requested."


output SectionMetadata: "Section Metadata"
    target: File
        path: "unit_root/_authoring/section_metadata.json"
    shape: JsonObject
    requirement: Required


output SectionReview: "Section Review"
    target: File
        path: "unit_root/_authoring/SECTION_REVIEW.md"
    shape: MarkdownDocument
    requirement: Required


output InvalidationHandoff: "Invalidation Handoff"
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

    standalone_read: "Standalone Read"
        "A downstream owner must be able to read this output alone and know what is current now and what is no longer current."


output BlockedReviewHandoff: "Blocked Review Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

    invalidations: "Invalidations"
        "Name any artifacts that are still no longer current."

    trust_surface:
        invalidations

    standalone_read: "Standalone Read"
        "A downstream owner must be able to read this output alone and know what is no longer current."


output RebuildHandoff: "Rebuild Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

    current_artifact: "Current Artifact"
        "Name the one artifact that is current now."

    trust_surface:
        current_artifact

    standalone_read: "Standalone Read"
        "A downstream owner must be able to read this output alone and know what is current now."


agent RoutingOwner:
    role: "Own explicit reroutes when specialist work cannot continue."
    workflow: "Instructions"
        "Take back the same issue when rebuild work is required."


workflow StructureChange: "Structure Change"
    law:
        active when CurrentHandoff.structure_changed
        current artifact SectionMetadata via InvalidationHandoff.current_artifact
        invalidate SectionReview via InvalidationHandoff.invalidations
        stop "Structure moved; downstream review is no longer current."
        route "Route the same issue back to RoutingOwner for rebuild." -> RoutingOwner


workflow BlockedSectionReview: "Blocked Section Review"
    law:
        active when CurrentHandoff.section_review_invalidated
        current none
        stop "Section Review is invalidated until rebuild work completes."
        route "Route the same issue back to RoutingOwner until review is rebuilt." -> RoutingOwner


workflow RebuildSectionReview: "Rebuild Section Review"
    law:
        active when CurrentHandoff.rebuild_requested
        current artifact SectionReview via RebuildHandoff.current_artifact


agent StructureChangeDemo:
    role: "Invalidate downstream review when structure changes."
    workflow: StructureChange
    inputs: "Inputs"
        CurrentHandoff
    outputs: "Outputs"
        SectionMetadata
        InvalidationHandoff


agent BlockedSectionReviewDemo:
    role: "Do not keep reviewing against invalidated downstream truth."
    workflow: BlockedSectionReview
    inputs: "Inputs"
        CurrentHandoff
    outputs: "Outputs"
        BlockedReviewHandoff


agent RebuildSectionReviewDemo:
    role: "Rebuild invalidated review work and reissue it as current truth."
    workflow: RebuildSectionReview
    inputs: "Inputs"
        CurrentHandoff
    outputs: "Outputs"
        SectionReview
        RebuildHandoff
````

## File: examples/37_law_reuse_and_patching/prompts/AGENTS.prompt
````
enum RewriteRegime: "Rewrite Regime"
    carry_forward: "carry-forward"
    rewrite: "rewrite"


input CurrentHandoff: "Current Handoff"
    source: Prompt
    shape: JsonObject
    requirement: Required
    "Use the host-provided handoff facts that say whether the preserve basis remains clear, whether this pass is a rewrite, and whether structure changed."


input AcceptedPeerSet: "Accepted Peer Set"
    source: File
        path: "catalog/accepted_peers.json"
    shape: JsonObject
    requirement: Advisory


output SectionMetadata: "Section Metadata"
    target: File
        path: "unit_root/_authoring/section_metadata.json"
    shape: JsonObject
    requirement: Required


output SectionReview: "Section Review"
    target: File
        path: "unit_root/_authoring/SECTION_REVIEW.md"
    shape: MarkdownDocument
    requirement: Required


output BaseCoordinationHandoff: "Base Coordination Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

    current_artifact: "Current Artifact"
        "Name the one artifact that is current now."

    comparison_basis: "Comparison Basis"
        "Name any comparison-only artifacts used in this pass."

    trust_surface:
        current_artifact
        comparison_basis

    standalone_read: "Standalone Read"
        "A downstream owner must be able to read this output alone and know what is current now and what was comparison-only."


output RewriteAwareCoordinationHandoff: "Rewrite-Aware Coordination Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

    current_artifact: "Current Artifact"
        "Name the one artifact that is current now."

    comparison_basis: "Comparison Basis"
        "Name any comparison-only artifacts used in this pass."

    rewrite_exclusions: "Rewrite Evidence Exclusions"
        "Name any fields whose old values do not count as rewrite evidence."

    invalidations: "Invalidations"
        "Name any artifacts that are no longer current."

    trust_surface:
        current_artifact
        comparison_basis
        rewrite_exclusions when CurrentHandoff.rewrite_regime == RewriteRegime.rewrite
        invalidations when CurrentHandoff.structure_changed

    standalone_read: "Standalone Read"
        "A downstream owner must be able to read this output alone and know what is current now, what was comparison-only, what old wording does not count as rewrite evidence on rewrite passes, and what is no longer current when structure changed."


agent RoutingOwner:
    role: "Own explicit reroutes when specialist work cannot continue."
    workflow: "Instructions"
        "Take back the same issue when workflow law requires a reroute."


workflow BaseMetadataPolish: "Base Metadata Polish"
    law:
        currentness:
            current artifact SectionMetadata via BaseCoordinationHandoff.current_artifact

        evidence:
            support_only AcceptedPeerSet for comparison

        reroute_on_unclear:
            when unclear(CurrentHandoff.preserve_basis):
                stop "Preserve basis is unclear."
                route "Route the same issue back to RoutingOwner." -> RoutingOwner


workflow RewriteAwareMetadataPolish[BaseMetadataPolish]: "Rewrite-Aware Metadata Polish"
    law:
        inherit reroute_on_unclear

        override currentness:
            current artifact SectionMetadata via RewriteAwareCoordinationHandoff.current_artifact

        override evidence:
            support_only AcceptedPeerSet for comparison
            ignore SectionMetadata.description for rewrite_evidence when CurrentHandoff.rewrite_regime == RewriteRegime.rewrite

        invalidation:
            when CurrentHandoff.structure_changed:
                invalidate SectionReview via RewriteAwareCoordinationHandoff.invalidations
                stop "Structure changed; downstream review is no longer current."
                route "Route the same issue back to RoutingOwner." -> RoutingOwner


agent BaseMetadataPolishDemo:
    role: "Keep reusable law subsections explicit in the base workflow."
    workflow: BaseMetadataPolish
    inputs: "Inputs"
        CurrentHandoff
        AcceptedPeerSet
    outputs: "Outputs"
        SectionMetadata
        BaseCoordinationHandoff


agent RewriteAwareMetadataPolishDemo:
    role: "Patch inherited law explicitly and add rewrite-only evidence rules."
    workflow: RewriteAwareMetadataPolish
    inputs: "Inputs"
        CurrentHandoff
        AcceptedPeerSet
    outputs: "Outputs"
        SectionMetadata
        RewriteAwareCoordinationHandoff
````

## File: examples/37_law_reuse_and_patching/prompts/INVALID_BARE_LAW_STATEMENT_IN_INHERITED_CHILD.prompt
````
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


workflow BaseMetadataPolish: "Base Metadata Polish"
    law:
        currentness:
            current artifact SectionMetadata via CoordinationHandoff.current_artifact


workflow ChildMetadataPolish[BaseMetadataPolish]: "Child Metadata Polish"
    law:
        inherit currentness
        current none


agent InvalidBareLawStatementInInheritedChild:
    role: "Trigger a bare law statement in an inherited child."
    workflow: ChildMetadataPolish
    outputs: "Outputs"
        SectionMetadata
        CoordinationHandoff
````

## File: examples/37_law_reuse_and_patching/prompts/INVALID_DUPLICATE_INHERITED_LAW_SECTION.prompt
````
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


workflow BaseMetadataPolish: "Base Metadata Polish"
    law:
        currentness:
            current artifact SectionMetadata via CoordinationHandoff.current_artifact


workflow ChildMetadataPolish[BaseMetadataPolish]: "Child Metadata Polish"
    law:
        inherit currentness
        inherit currentness


agent InvalidDuplicateInheritedLawSection:
    role: "Trigger duplicate inherited law accounting."
    workflow: ChildMetadataPolish
    outputs: "Outputs"
        SectionMetadata
        CoordinationHandoff
````

## File: examples/37_law_reuse_and_patching/prompts/INVALID_MISSING_INHERITED_LAW_SECTION.prompt
````
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


workflow BaseMetadataPolish: "Base Metadata Polish"
    law:
        currentness:
            current artifact SectionMetadata via CoordinationHandoff.current_artifact

        stop_lines:
            stop "Mode or preserve basis is unclear."


workflow ChildMetadataPolish[BaseMetadataPolish]: "Child Metadata Polish"
    law:
        inherit stop_lines


agent InvalidMissingInheritedLawSection:
    role: "Trigger an inherited law section omission."
    workflow: ChildMetadataPolish
    outputs: "Outputs"
        SectionMetadata
        CoordinationHandoff
````

## File: examples/37_law_reuse_and_patching/prompts/INVALID_OVERRIDE_UNKNOWN_LAW_SECTION.prompt
````
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


workflow BaseMetadataPolish: "Base Metadata Polish"
    law:
        currentness:
            current artifact SectionMetadata via CoordinationHandoff.current_artifact


workflow ChildMetadataPolish[BaseMetadataPolish]: "Child Metadata Polish"
    law:
        inherit currentness
        override missing_section:
            current none


agent InvalidOverrideUnknownLawSection:
    role: "Trigger an override of an unknown law section."
    workflow: ChildMetadataPolish
    outputs: "Outputs"
        SectionMetadata
        CoordinationHandoff
````

## File: examples/38_metadata_polish_capstone/prompts/AGENTS.prompt
````
enum MetadataPolishMode: "Metadata Polish Mode"
    manifest_title: "manifest-title"
    section_summary: "section-summary"


enum RewriteRegime: "Rewrite Regime"
    carry_forward: "carry-forward"
    rewrite: "rewrite"


input CurrentHandoff: "Current Handoff"
    source: Prompt
    shape: JsonObject
    requirement: Required
    "Use the host-provided handoff facts that say whether metadata polish is owed, which mode is active, which preserve basis remains authoritative, whether peer comparison is in play, whether this pass is a rewrite, and whether structure changed."


input ApprovedPlan: "Approved Plan"
    source: File
        path: "unit_root/_authoring/APPROVED_PLAN.md"
    shape: MarkdownDocument
    requirement: Required


input ApprovedStructure: "Approved Structure"
    source: File
        path: "unit_root/_authoring/APPROVED_STRUCTURE.md"
    shape: MarkdownDocument
    requirement: Required


input AcceptedPeerSet: "Accepted Peer Set"
    source: File
        path: "catalog/accepted_peers.json"
    shape: JsonObject
    requirement: Advisory


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


output SectionReview: "Section Review"
    target: File
        path: "unit_root/_authoring/SECTION_REVIEW.md"
    shape: MarkdownDocument
    requirement: Required


output BaseCoordinationHandoff: "Base Coordination Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

    current_artifact: "Current Artifact"
        "Name the one artifact that is current now."

    active_mode: "Active Mode"
        "Name the one active mode for this pass."

    preserve_basis: "Preserve Basis"
        "Name the upstream declaration whose decisions remain authoritative."

    comparison_basis: "Comparison Basis"
        "Name any comparison-only artifacts used in this pass."

    trust_surface:
        current_artifact
        active_mode
        preserve_basis
        comparison_basis when CurrentHandoff.peer_comparison_used

    standalone_read: "Standalone Read"
        "A downstream owner must be able to read this output alone and know what is current now, which mode is active, and why that preserve basis remains authoritative."


output RewriteAwareCoordinationHandoff: "Rewrite-Aware Coordination Handoff"
    target: TurnResponse
    shape: Comment
    requirement: Required

    current_artifact: "Current Artifact"
        "Name the one artifact that is current now."

    active_mode: "Active Mode"
        "Name the one active mode for this pass."

    preserve_basis: "Preserve Basis"
        "Name the upstream declaration whose decisions remain authoritative."

    comparison_basis: "Comparison Basis"
        "Name any comparison-only artifacts used in this pass."

    rewrite_exclusions: "Rewrite Evidence Exclusions"
        "Name any fields whose old values do not count as rewrite evidence."

    invalidations: "Invalidations"
        "Name any artifacts that are no longer current."

    trust_surface:
        current_artifact
        active_mode
        preserve_basis
        comparison_basis when CurrentHandoff.peer_comparison_used
        rewrite_exclusions when CurrentHandoff.rewrite_regime == RewriteRegime.rewrite
        invalidations when CurrentHandoff.structure_changed

    standalone_read: "Standalone Read"
        "A downstream owner must be able to read this output alone and know what is current now, which mode is active, why that preserve basis remains authoritative, what old wording does not count as rewrite evidence on rewrite passes, and what is no longer current when structure changed."


agent RoutingOwner:
    role: "Own explicit reroutes when the current specialist cannot continue."
    workflow: "Instructions"
        "Take back the same issue when metadata polish cannot continue safely."


workflow BaseMetadataPolish: "Metadata Polish"
    "Handle the last narrow wording pass after structure is already locked."

    law:
        activation:
            active when CurrentHandoff.owes_metadata_polish

        mode_selection:
            mode pass_mode = CurrentHandoff.active_mode as MetadataPolishMode

        currentness:
            match pass_mode:
                MetadataPolishMode.manifest_title:
                    current artifact PrimaryManifest via BaseCoordinationHandoff.current_artifact
                    must CurrentHandoff.preserve_basis == ApprovedPlan

                MetadataPolishMode.section_summary:
                    current artifact SectionMetadata via BaseCoordinationHandoff.current_artifact
                    must CurrentHandoff.preserve_basis == ApprovedStructure

        scope:
            match pass_mode:
                MetadataPolishMode.manifest_title:
                    own only PrimaryManifest.title
                    preserve exact PrimaryManifest.* except PrimaryManifest.title
                    preserve decisions ApprovedPlan

                MetadataPolishMode.section_summary:
                    own only {SectionMetadata.name, SectionMetadata.description}
                    preserve exact SectionMetadata.* except {SectionMetadata.name, SectionMetadata.description}
                    preserve decisions ApprovedStructure
                    forbid {SectionMetadata.taxonomy, SectionMetadata.flags}

        evidence:
            support_only AcceptedPeerSet for comparison

        stop_lines:
            when unclear(pass_mode, CurrentHandoff.preserve_basis):
                stop "Mode or preserve basis is unclear."
                route "Route the same issue back to RoutingOwner." -> RoutingOwner


workflow RewriteAwareMetadataPolish[BaseMetadataPolish]: "Metadata Polish"
    law:
        inherit activation
        inherit mode_selection
        inherit scope

        override currentness:
            match pass_mode:
                MetadataPolishMode.manifest_title:
                    current artifact PrimaryManifest via RewriteAwareCoordinationHandoff.current_artifact
                    must CurrentHandoff.preserve_basis == ApprovedPlan

                MetadataPolishMode.section_summary:
                    current artifact SectionMetadata via RewriteAwareCoordinationHandoff.current_artifact
                    must CurrentHandoff.preserve_basis == ApprovedStructure

        override evidence:
            support_only AcceptedPeerSet for comparison

            ignore PrimaryManifest.title for rewrite_evidence when pass_mode == MetadataPolishMode.manifest_title and CurrentHandoff.rewrite_regime == RewriteRegime.rewrite

            ignore {SectionMetadata.name, SectionMetadata.description} for rewrite_evidence when pass_mode == MetadataPolishMode.section_summary and CurrentHandoff.rewrite_regime == RewriteRegime.rewrite

        override stop_lines:
            when CurrentHandoff.structure_changed:
                invalidate SectionReview via RewriteAwareCoordinationHandoff.invalidations
                stop "Structure moved; downstream review is no longer current."
                route "Route the same issue back to RoutingOwner for rebuild." -> RoutingOwner

            when unclear(pass_mode, CurrentHandoff.preserve_basis):
                stop "Mode or preserve basis is unclear."
                route "Route the same issue back to RoutingOwner." -> RoutingOwner


workflow ManifestTitleMetadataPolish[BaseMetadataPolish]: "Metadata Polish"
    law:
        inherit activation

        override mode_selection:
            mode pass_mode = MetadataPolishMode.manifest_title as MetadataPolishMode

        inherit currentness
        inherit scope
        inherit evidence
        inherit stop_lines


workflow RewriteAwareSectionSummaryMetadataPolish[RewriteAwareMetadataPolish]: "Metadata Polish"
    law:
        inherit activation

        override mode_selection:
            mode pass_mode = MetadataPolishMode.section_summary as MetadataPolishMode

        inherit currentness
        inherit scope
        inherit evidence
        inherit stop_lines


agent MetadataPolishCapstoneDemo:
    role: "Handle the last narrow wording pass after structure is already locked."
    workflow: ManifestTitleMetadataPolish
    inputs: "Inputs"
        CurrentHandoff
        ApprovedPlan
        ApprovedStructure
        AcceptedPeerSet
    outputs: "Outputs"
        PrimaryManifest
        BaseCoordinationHandoff


agent RewriteAwareMetadataPolishCapstoneDemo:
    role: "Handle the last narrow wording pass after structure is already locked."
    workflow: RewriteAwareSectionSummaryMetadataPolish
    inputs: "Inputs"
        CurrentHandoff
        ApprovedPlan
        ApprovedStructure
        AcceptedPeerSet
    outputs: "Outputs"
        SectionMetadata
        RewriteAwareCoordinationHandoff
````

## File: doctrine/grammars/doctrine.lark
````
%import common.CNAME
%import common.ESCAPED_STRING
%import common.SH_COMMENT
%import common.SIGNED_NUMBER
%import common.WS_INLINE

%ignore WS_INLINE

%declare _INDENT _DEDENT

start: prompt_file

prompt_file: _NL* declaration+ _NL*

?declaration: import_decl
            | workflow_decl
            | skills_decl
            | inputs_decl
            | input_source_decl
            | input_decl
            | outputs_decl
            | output_target_decl
            | output_shape_decl
            | output_decl
            | json_schema_decl
            | skill_decl
            | enum_decl
            | abstract_agent
            | agent

import_decl: "import" import_path _NL

workflow_decl: "workflow" CNAME inheritance? ":" string _NL _INDENT workflow_body _DEDENT
skills_decl: "skills" CNAME inheritance? ":" string _NL _INDENT skills_body _DEDENT
inputs_decl: "inputs" CNAME inheritance? ":" string _NL _INDENT io_body _DEDENT
input_source_decl: "input" "source" CNAME ":" string _NL _INDENT record_body _DEDENT
input_decl: "input" CNAME ":" string _NL _INDENT record_body _DEDENT
outputs_decl: "outputs" CNAME inheritance? ":" string _NL _INDENT io_body _DEDENT
output_target_decl: "output" "target" CNAME ":" string _NL _INDENT record_body _DEDENT
output_shape_decl: "output" "shape" CNAME ":" string _NL _INDENT record_body _DEDENT
output_decl: "output" CNAME ":" string _NL _INDENT output_body _DEDENT
json_schema_decl: "json" "schema" CNAME ":" string _NL _INDENT record_body _DEDENT
skill_decl: "skill" CNAME ":" string _NL _INDENT record_body _DEDENT
enum_decl: "enum" CNAME ":" string _NL _INDENT enum_body _DEDENT

agent: "agent" CNAME inheritance? ":" _NL _INDENT agent_field+ _DEDENT
abstract_agent: "abstract" "agent" CNAME inheritance? ":" _NL _INDENT agent_field+ _DEDENT
inheritance: "[" name_ref "]"

// Reserved typed fields stay explicit. Every other non-reserved key is an
// authored workflow slot, which keeps the grammar open without making typed
// contract fields magical.
?agent_field: role_field
            | inputs_patch_field
            | inputs_inline_field
            | inputs_ref_field
            | outputs_patch_field
            | outputs_inline_field
            | outputs_ref_field
            | skills_field
            | agent_slot_abstract
            | agent_slot_inherit
            | agent_slot_override
            | agent_slot_field

role_field: "role" ":" string _NL role_body?
role_body: _INDENT block_lines _DEDENT

// Inputs and outputs reuse the record body so roles can mix prose, titled
// groups, and typed declaration refs without growing a second mini-language.
inputs_inline_field: "inputs" ":" string _NL _INDENT record_body _DEDENT
inputs_ref_field: "inputs" ":" name_ref _NL?
inputs_patch_field: "inputs" inheritance ":" string _NL _INDENT io_body _DEDENT
outputs_inline_field: "outputs" ":" string _NL _INDENT record_body _DEDENT
outputs_ref_field: "outputs" ":" name_ref _NL?
outputs_patch_field: "outputs" inheritance ":" string _NL _INDENT io_body _DEDENT
skills_field: "skills" ":" string _NL _INDENT skills_body _DEDENT
            | "skills" ":" name_ref _NL?

agent_slot_field: CNAME ":" slot_value _NL slot_body?
agent_slot_abstract: "abstract" CNAME _NL?
agent_slot_inherit: "inherit" CNAME _NL?
agent_slot_override: "override" CNAME ":" slot_value _NL slot_body?

?slot_value: string | name_ref
slot_body: _INDENT workflow_body _DEDENT

workflow_body: workflow_body_line+

workflow_string: prose_line _NL?
workflow_body_line: workflow_string
                  | workflow_item
                  | law_block

?workflow_item: workflow_skills_inline
              | workflow_skills_ref
              | local_section
              | workflow_use
              | workflow_inherit
              | workflow_override_skills_inline
              | workflow_override_skills_ref
              | workflow_override_section
              | workflow_override_use

workflow_skills_inline: "skills" ":" string _NL _INDENT skills_body _DEDENT
workflow_skills_ref: "skills" ":" name_ref _NL?
local_section: CNAME ":" string _NL _INDENT workflow_section_body _DEDENT
workflow_use: "use" CNAME ":" name_ref _NL?
workflow_inherit: "inherit" CNAME _NL?
workflow_override_skills_inline: "override" "skills" ":" string _NL _INDENT skills_body _DEDENT
workflow_override_skills_ref: "override" "skills" ":" name_ref _NL?
workflow_override_section: "override" CNAME ":" string? _NL _INDENT workflow_section_body _DEDENT
workflow_override_use: "override" CNAME ":" name_ref _NL?

workflow_section_body: workflow_section_item+
?workflow_section_item: prose_line _NL?
                      | route_stmt
                      | local_section
                      | workflow_section_ref_item
workflow_section_ref_item: path_ref _NL?
                         | name_ref _NL?

skills_body: skills_body_line+

skills_string: prose_line _NL?
skills_body_line: skills_string
                | skills_item

?skills_item: skills_section
            | skill_entry
            | skills_inherit
            | skills_override_section
            | skills_override_entry

skills_section: CNAME ":" string _NL _INDENT skills_section_body _DEDENT
skill_entry: "skill" CNAME ":" name_ref _NL skill_entry_body?
skills_inherit: "inherit" CNAME _NL?
skills_override_section: "override" CNAME ":" string? _NL _INDENT skills_section_body _DEDENT
skills_override_entry: "override" CNAME ":" name_ref _NL skill_entry_body?
skill_entry_body: _INDENT record_body _DEDENT

skills_section_body: skills_section_item+
?skills_section_item: prose_line _NL?
                    | skill_entry

io_body: io_body_line+

io_string: prose_line _NL?
io_body_line: io_string
            | io_item

?io_item: io_section
        | record_ref_item
        | io_inherit
        | io_override_section

io_section: CNAME ":" string _NL _INDENT record_body _DEDENT
io_inherit: "inherit" CNAME _NL?
io_override_section: "override" CNAME ":" string? _NL _INDENT record_body _DEDENT

output_body: output_body_line+
output_body_line: record_text
                | record_keyed_item
                | record_ref_item
                | trust_surface_block

trust_surface_block: "trust_surface" ":" _NL _INDENT trust_surface_item+ _DEDENT
trust_surface_item: field_path trust_surface_when? _NL?
trust_surface_when: "when" expr

record_body: record_item+
?record_item: record_text
            | record_keyed_item
            | record_ref_item

record_text: prose_line _NL?
record_keyed_item: CNAME ":" record_head _NL record_item_body?
record_ref_item: name_ref _NL record_item_body?
record_item_body: _INDENT record_body _DEDENT

?record_head: string | path_ref | name_ref

enum_body: enum_member+
enum_member: CNAME ":" string _NL?

ref_list: ref_item+
ref_item: name_ref _NL?

route_stmt: "route" string "->" name_ref _NL?

law_block: "law" ":" _NL _INDENT law_body _DEDENT
law_body: law_item+
?law_item: law_stmt
         | law_section
         | law_inherit
         | law_override_section

law_section: CNAME ":" _NL _INDENT law_stmt+ _DEDENT
law_inherit: "inherit" CNAME _NL?
law_override_section: "override" CNAME ":" _NL _INDENT law_stmt+ _DEDENT

?law_stmt: active_when_stmt
         | mode_stmt
         | must_stmt
         | current_artifact_stmt
         | current_none_stmt
         | own_only_stmt
         | preserve_stmt
         | support_only_stmt
         | ignore_stmt
         | invalidate_stmt
         | forbid_stmt
         | when_stmt
         | match_stmt
         | stop_stmt
         | law_route_stmt

active_when_stmt: "active" "when" expr _NL
mode_stmt: "mode" CNAME "=" expr "as" name_ref _NL
must_stmt: "must" expr _NL
current_artifact_stmt: "current" "artifact" law_path "via" law_path _NL
current_none_stmt: "current" "none" _NL
own_only_stmt: "own" "only" path_set_expr law_when_clause? _NL
preserve_stmt: "preserve" preserve_kind path_set_expr law_when_clause? _NL
support_only_stmt: "support_only" path_set_expr "for" "comparison" law_when_clause? _NL
ignore_stmt: "ignore" path_set_expr "for" ignore_basis_list law_when_clause? _NL
           | "ignore" path_set_expr law_when_clause? _NL
invalidate_stmt: "invalidate" law_path "via" law_path law_when_clause? _NL
forbid_stmt: "forbid" path_set_expr law_when_clause? _NL
when_stmt: "when" expr ":" _NL _INDENT law_stmt+ _DEDENT
match_stmt: "match" expr ":" _NL _INDENT match_case+ _DEDENT
stop_stmt: "stop" string law_when_clause? _NL
         | "stop" law_when_clause _NL
         | "stop" _NL
law_route_stmt: "route" string "->" name_ref law_when_clause? _NL

match_case: match_head ":" _NL _INDENT law_stmt+ _DEDENT
?match_head: expr
           | "else" -> else_match_head

preserve_kind: "exact"      -> preserve_exact
             | "structure"  -> preserve_structure
             | "decisions"  -> preserve_decisions
             | "mapping"    -> preserve_mapping
             | "vocabulary" -> preserve_vocabulary

ignore_basis_list: ignore_basis ("," ignore_basis)*
ignore_basis: "truth"            -> ignore_basis_truth
            | "comparison"       -> ignore_basis_comparison
            | "rewrite_evidence" -> ignore_basis_rewrite_evidence

law_when_clause: "when" expr

?path_set_expr: path_set_base ("except" path_set_base)*
?path_set_base: law_path
              | "{" law_path ("," law_path)* "}"

law_path: dotted_name LAW_WILDCARD?

field_path: CNAME ("." CNAME)*

?expr: or_expr
?or_expr: and_expr
        | or_expr "or" and_expr   -> expr_or
?and_expr: comparison_expr
         | and_expr "and" comparison_expr -> expr_and
?comparison_expr: expr_atom
                | expr_atom "==" expr_atom -> expr_eq
                | expr_atom "!=" expr_atom -> expr_ne
                | expr_atom ">" expr_atom  -> expr_gt
                | expr_atom ">=" expr_atom -> expr_gte
                | expr_atom "<" expr_atom  -> expr_lt
                | expr_atom "<=" expr_atom -> expr_lte
                | expr_atom "in" expr_atom -> expr_in
?expr_atom: dotted_name           -> expr_ref
          | string
          | SIGNED_NUMBER         -> expr_number
          | "true"                -> expr_true
          | "false"               -> expr_false
          | expr_call
          | "(" expr ")"

expr_call: CNAME "(" expr ("," expr)* ")"

path_ref: PATH_REF
name_ref: dotted_name
import_path: absolute_import_path | relative_import_path
absolute_import_path: dotted_name
relative_import_path: DOTS dotted_name
dotted_name: CNAME ("." CNAME)*

block_lines: prose_line (_NL prose_line)* _NL?

?prose_line: string
           | emphasized_line

emphasized_line: REQUIRED_KEYWORD string -> required_line
               | IMPORTANT_KEYWORD string -> important_line
               | WARNING_KEYWORD string -> warning_line
               | NOTE_KEYWORD string -> note_line

?string: ESCAPED_STRING

REQUIRED_KEYWORD.2: /required(?=[ \t]*")/
IMPORTANT_KEYWORD.2: /important(?=[ \t]*")/
WARNING_KEYWORD.2: /warning(?=[ \t]*")/
NOTE_KEYWORD.2: /note(?=[ \t]*")/
PATH_REF: /[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*:[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*/
LAW_WILDCARD: ".*"

DOTS: /\.+/

// `_NL` owns newlines, indentation whitespace, and standalone comment lines so
// the stock Indenter can derive _INDENT/_DEDENT without a side preprocessor.
// Keeping comment lines here avoids a strict-mode regex collision with `%ignore`.
_NL: (/\r?\n[\t ]*/ | SH_COMMENT)+
````

## File: doctrine/compiler.py
````python
from __future__ import annotations

import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TypeAlias

from doctrine import model
from doctrine.diagnostics import CompileError, DiagnosticLocation, DoctrineError
from doctrine.parser import parse_file


@dataclass(slots=True, frozen=True)
class CompiledSection:
    title: str
    body: tuple[CompiledBodyItem, ...]


@dataclass(slots=True, frozen=True)
class CompiledAgent:
    name: str
    fields: tuple[CompiledField, ...]


CompiledBodyItem: TypeAlias = model.ProseLine | CompiledSection
CompiledField: TypeAlias = model.RoleScalar | CompiledSection
ReadableDecl: TypeAlias = (
    model.Agent
    | model.InputDecl
    | model.InputSourceDecl
    | model.OutputDecl
    | model.OutputTargetDecl
    | model.OutputShapeDecl
    | model.JsonSchemaDecl
    | model.SkillDecl
    | model.EnumDecl
)
AddressableRootDecl: TypeAlias = ReadableDecl | model.WorkflowDecl | model.SkillsDecl
AddressableTarget: TypeAlias = (
    AddressableRootDecl
    | model.RecordScalar
    | model.RecordSection
    | model.EnumMember
    | "ResolvedSectionItem"
    | "ResolvedUseItem"
    | "ResolvedWorkflowSkillsItem"
    | "ResolvedSkillsSection"
    | "ResolvedSkillEntry"
)


@dataclass(slots=True, frozen=True)
class IndexedUnit:
    module_parts: tuple[str, ...]
    prompt_file: model.PromptFile
    imports: tuple[model.ImportDecl, ...]
    workflows_by_name: dict[str, model.WorkflowDecl]
    inputs_blocks_by_name: dict[str, model.InputsDecl]
    inputs_by_name: dict[str, model.InputDecl]
    input_sources_by_name: dict[str, model.InputSourceDecl]
    outputs_blocks_by_name: dict[str, model.OutputsDecl]
    outputs_by_name: dict[str, model.OutputDecl]
    output_targets_by_name: dict[str, model.OutputTargetDecl]
    output_shapes_by_name: dict[str, model.OutputShapeDecl]
    json_schemas_by_name: dict[str, model.JsonSchemaDecl]
    skills_by_name: dict[str, model.SkillDecl]
    skills_blocks_by_name: dict[str, model.SkillsDecl]
    enums_by_name: dict[str, model.EnumDecl]
    agents_by_name: dict[str, model.Agent]
    imported_units: dict[tuple[str, ...], "IndexedUnit"]


@dataclass(slots=True, frozen=True)
class ResolvedRouteLine:
    label: str
    target_name: str


@dataclass(slots=True, frozen=True)
class ResolvedSectionRef:
    label: str


ResolvedSectionBodyItem: TypeAlias = (
    model.ProseLine | ResolvedRouteLine | ResolvedSectionRef | "ResolvedSectionItem"
)


@dataclass(slots=True, frozen=True)
class ResolvedSectionItem:
    key: str
    title: str
    items: tuple[ResolvedSectionBodyItem, ...]


@dataclass(slots=True, frozen=True)
class ResolvedUseItem:
    key: str
    target_unit: IndexedUnit
    workflow_decl: model.WorkflowDecl


@dataclass(slots=True, frozen=True)
class ResolvedSkillEntry:
    key: str
    metadata_unit: IndexedUnit
    target_unit: IndexedUnit
    skill_decl: model.SkillDecl
    items: tuple[model.RecordItem, ...]


ResolvedSkillsSectionBodyItem: TypeAlias = model.ProseLine | ResolvedSkillEntry


@dataclass(slots=True, frozen=True)
class ResolvedSkillsSection:
    key: str
    title: str
    items: tuple[ResolvedSkillsSectionBodyItem, ...]


ResolvedSkillsItem = ResolvedSkillsSection | ResolvedSkillEntry


@dataclass(slots=True, frozen=True)
class ResolvedSkillsBody:
    title: str
    preamble: tuple[model.ProseLine, ...]
    items: tuple[ResolvedSkillsItem, ...]


@dataclass(slots=True, frozen=True)
class ResolvedIoSection:
    key: str
    section: CompiledSection


@dataclass(slots=True, frozen=True)
class ResolvedIoRef:
    section: CompiledSection


ResolvedIoItem = ResolvedIoSection | ResolvedIoRef


@dataclass(slots=True, frozen=True)
class ResolvedIoBody:
    title: str
    preamble: tuple[model.ProseLine, ...]
    items: tuple[ResolvedIoItem, ...]


@dataclass(slots=True, frozen=True)
class ResolvedWorkflowSkillsItem:
    key: str
    body: ResolvedSkillsBody


ResolvedWorkflowItem = ResolvedSectionItem | ResolvedUseItem | ResolvedWorkflowSkillsItem


@dataclass(slots=True, frozen=True)
class ResolvedWorkflowBody:
    title: str
    preamble: tuple[model.ProseLine, ...]
    items: tuple[ResolvedWorkflowItem, ...]
    law: model.LawBody | None = None


@dataclass(slots=True, frozen=True)
class AgentContract:
    inputs: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.InputDecl]]
    outputs: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.OutputDecl]]


@dataclass(slots=True, frozen=True)
class LawBranch:
    activation_exprs: tuple[model.Expr, ...] = ()
    mode_bindings: tuple[model.ModeStmt, ...] = ()
    current_subjects: tuple[model.CurrentArtifactStmt | model.CurrentNoneStmt, ...] = ()
    musts: tuple[model.MustStmt, ...] = ()
    owns: tuple[model.OwnOnlyStmt, ...] = ()
    preserves: tuple[model.PreserveStmt, ...] = ()
    supports: tuple[model.SupportOnlyStmt, ...] = ()
    ignores: tuple[model.IgnoreStmt, ...] = ()
    forbids: tuple[model.ForbidStmt, ...] = ()
    invalidations: tuple[model.InvalidateStmt, ...] = ()
    stops: tuple[model.StopStmt, ...] = ()
    routes: tuple[model.LawRouteStmt, ...] = ()


@dataclass(slots=True, frozen=True)
class ResolvedLawPath:
    unit: IndexedUnit
    decl: model.InputDecl | model.OutputDecl | model.EnumDecl
    remainder: tuple[str, ...]
    wildcard: bool = False


@dataclass(slots=True, frozen=True)
class ResolvedAgentSlot:
    key: str
    body: ResolvedWorkflowBody


@dataclass(slots=True, frozen=True)
class ResolvedAbstractAgentSlot:
    key: str


ResolvedAgentSlotState = ResolvedAgentSlot | ResolvedAbstractAgentSlot


@dataclass(slots=True, frozen=True)
class ConfigSpec:
    title: str
    required_keys: dict[str, str]
    optional_keys: dict[str, str]


@dataclass(slots=True, frozen=True)
class DisplayValue:
    text: str
    kind: str


@dataclass(slots=True, frozen=True)
class AddressableNode:
    unit: IndexedUnit
    root_decl: AddressableRootDecl
    target: AddressableTarget


_CAMEL_BOUNDARY_RE = re.compile(r"(?<!^)(?=[A-Z])")
_INTERPOLATION_EXPR_RE = re.compile(
    r"\s*"
    r"([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*)"
    r"(?:\s*:\s*([A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*))?"
    r"\s*"
)
_INTERPOLATION_RE = re.compile(r"\{\{([^{}]+)\}\}")
# Reserved typed fields get their own compiler paths. Every other key is an
# authored workflow slot, with one legacy carve-out: the old `workflow` field
# still preserves 01-06 body inheritance semantics instead of switching to a
# second slot-patching dialect.
_RESERVED_AGENT_FIELD_KEYS = {"role", "inputs", "outputs", "skills"}

_BUILTIN_INPUT_SOURCES = {
    "Prompt": ConfigSpec(title="Prompt", required_keys={}, optional_keys={}),
    "File": ConfigSpec(title="File", required_keys={"path": "Path"}, optional_keys={}),
    "EnvVar": ConfigSpec(title="EnvVar", required_keys={"env": "Env"}, optional_keys={}),
}

_BUILTIN_OUTPUT_TARGETS = {
    "TurnResponse": ConfigSpec(title="Turn Response", required_keys={}, optional_keys={}),
    "File": ConfigSpec(title="File", required_keys={"path": "Path"}, optional_keys={}),
}

_READABLE_DECL_REGISTRIES = (
    ("agent declaration", "agents_by_name"),
    ("input declaration", "inputs_by_name"),
    ("input source declaration", "input_sources_by_name"),
    ("output declaration", "outputs_by_name"),
    ("output target declaration", "output_targets_by_name"),
    ("output shape declaration", "output_shapes_by_name"),
    ("json schema declaration", "json_schemas_by_name"),
    ("skill declaration", "skills_by_name"),
    ("enum declaration", "enums_by_name"),
)

_ADDRESSABLE_ROOT_REGISTRIES = (
    *_READABLE_DECL_REGISTRIES,
    ("workflow declaration", "workflows_by_name"),
    ("skills block", "skills_blocks_by_name"),
)


class CompilationContext:
    def __init__(self, prompt_file: model.PromptFile):
        self.prompt_root = _resolve_prompt_root(prompt_file.source_path)
        self._module_cache: dict[tuple[str, ...], IndexedUnit] = {}
        self._loading_modules: set[tuple[str, ...]] = set()
        self._workflow_compile_stack: list[tuple[tuple[str, ...], str]] = []
        self._workflow_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._workflow_addressable_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._skills_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._skills_addressable_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._inputs_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._outputs_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._agent_slot_resolution_stack: list[tuple[tuple[str, ...], str]] = []
        self._resolved_workflow_cache: dict[tuple[tuple[str, ...], str], ResolvedWorkflowBody] = {}
        self._addressable_workflow_cache: dict[
            tuple[tuple[str, ...], str], ResolvedWorkflowBody
        ] = {}
        self._resolved_skills_cache: dict[tuple[tuple[str, ...], str], ResolvedSkillsBody] = {}
        self._addressable_skills_cache: dict[
            tuple[tuple[str, ...], str], ResolvedSkillsBody
        ] = {}
        self._resolved_inputs_cache: dict[tuple[tuple[str, ...], str], ResolvedIoBody] = {}
        self._resolved_outputs_cache: dict[tuple[tuple[str, ...], str], ResolvedIoBody] = {}
        self._resolved_agent_slot_cache: dict[
            tuple[tuple[str, ...], str],
            tuple[ResolvedAgentSlotState, ...],
        ] = {}
        self.root_unit = self._index_unit(prompt_file, module_parts=())

    def compile_agent(self, agent_name: str) -> CompiledAgent:
        agent = self.root_unit.agents_by_name.get(agent_name)
        if agent is None:
            raise CompileError(f"Missing target agent: {agent_name}")
        if agent.abstract:
            raise CompileError(f"Abstract agent does not render: {agent_name}")
        return self._compile_agent_decl(agent, unit=self.root_unit)

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
        compiled_fields: list[CompiledField] = []
        seen_role = False
        seen_typed_fields: set[str] = set()

        for field in agent.fields:
            if isinstance(field, model.RoleScalar):
                if seen_role:
                    raise CompileError(f"Duplicate role field in agent {agent.name}")
                compiled_fields.append(
                    model.RoleScalar(
                        text=self._interpolate_authored_prose_string(
                            field.text,
                            unit=unit,
                            owner_label=f"agent {agent.name}",
                            surface_label="role prose",
                        )
                    )
                )
                seen_role = True
                continue

            if isinstance(field, model.RoleBlock):
                if seen_role:
                    raise CompileError(f"Duplicate role field in agent {agent.name}")
                compiled_fields.append(
                    CompiledSection(
                        title=field.title,
                        body=tuple(
                            self._interpolate_authored_prose_line(
                                line,
                                unit=unit,
                                owner_label=f"agent {agent.name}",
                                surface_label="role prose",
                            )
                            for line in field.lines
                        ),
                    )
                )
                seen_role = True
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
                if field.key == "workflow":
                    compiled_fields.append(
                        self._compile_resolved_workflow(
                            slot_body,
                            unit=unit,
                            agent_contract=agent_contract,
                            owner_label=f"agent {agent.name} workflow",
                        )
                    )
                else:
                    compiled_fields.append(self._compile_resolved_workflow(slot_body))
                continue

            field_key = self._typed_field_key(field)
            if field_key in seen_typed_fields:
                raise CompileError(f"Duplicate typed field in agent {agent.name}: {field_key}")
            seen_typed_fields.add(field_key)

            if isinstance(field, model.InputsField):
                compiled_fields.append(
                    self._compile_inputs_field(
                        field,
                        unit=unit,
                        owner_label=f"agent {agent.name}",
                    )
                )
                continue
            if isinstance(field, model.OutputsField):
                compiled_fields.append(
                    self._compile_outputs_field(
                        field,
                        unit=unit,
                        owner_label=f"agent {agent.name}",
                    )
                )
                continue
            if isinstance(field, model.SkillsField):
                compiled_fields.append(self._compile_skills_field(field, unit=unit))
                continue

            raise CompileError(
                f"Unsupported agent field in {agent.name}: {type(field).__name__}"
            )

        if not seen_role:
            raise CompileError(f"Concrete agent is missing role field: {agent.name}")

        return CompiledAgent(name=agent.name, fields=tuple(compiled_fields))

    def _typed_field_key(self, field: model.Field) -> str:
        if isinstance(field, model.InputsField):
            return "inputs"
        if isinstance(field, model.OutputsField):
            return "outputs"
        if isinstance(field, model.SkillsField):
            return "skills"
        return type(field).__name__

    def _resolve_agent_contract(self, agent: model.Agent, *, unit: IndexedUnit) -> AgentContract:
        inputs: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.InputDecl]] = {}
        outputs: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.OutputDecl]] = {}

        for field in agent.fields:
            if isinstance(field, model.InputsField):
                self._collect_input_decls_from_io_value(field.value, unit=unit, sink=inputs)
            elif isinstance(field, model.OutputsField):
                self._collect_output_decls_from_io_value(field.value, unit=unit, sink=outputs)

        return AgentContract(inputs=inputs, outputs=outputs)

    def _collect_input_decls_from_io_value(
        self,
        value: model.IoFieldValue,
        *,
        unit: IndexedUnit,
        sink: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.InputDecl]],
    ) -> None:
        if isinstance(value, tuple):
            self._collect_input_decls_from_record_items(value, unit=unit, sink=sink)
            return
        if isinstance(value, model.IoBody):
            self._collect_input_decls_from_io_items(value.items, unit=unit, sink=sink)
            return
        if self._ref_exists_in_registry(
            value,
            unit=unit,
            registry_name="outputs_blocks_by_name",
        ):
            raise CompileError(
                "Inputs fields must resolve to inputs blocks, not outputs blocks: "
                f"{_dotted_ref_name(value)}"
            )
        target_unit, decl = self._resolve_inputs_block_ref(value, unit=unit)
        self._collect_input_decls_from_io_items(decl.body.items, unit=target_unit, sink=sink)

    def _collect_output_decls_from_io_value(
        self,
        value: model.IoFieldValue,
        *,
        unit: IndexedUnit,
        sink: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.OutputDecl]],
    ) -> None:
        if isinstance(value, tuple):
            self._collect_output_decls_from_record_items(value, unit=unit, sink=sink)
            return
        if isinstance(value, model.IoBody):
            self._collect_output_decls_from_io_items(value.items, unit=unit, sink=sink)
            return
        if self._ref_exists_in_registry(
            value,
            unit=unit,
            registry_name="inputs_blocks_by_name",
        ):
            raise CompileError(
                "Outputs fields must resolve to outputs blocks, not inputs blocks: "
                f"{_dotted_ref_name(value)}"
            )
        target_unit, decl = self._resolve_outputs_block_ref(value, unit=unit)
        self._collect_output_decls_from_io_items(decl.body.items, unit=target_unit, sink=sink)

    def _collect_input_decls_from_io_items(
        self,
        items: tuple[model.IoItem, ...],
        *,
        unit: IndexedUnit,
        sink: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.InputDecl]],
    ) -> None:
        for item in items:
            if isinstance(item, model.RecordSection):
                self._collect_input_decls_from_record_items(item.items, unit=unit, sink=sink)
            elif isinstance(item, model.RecordRef):
                if self._ref_exists_in_registry(
                    item.ref,
                    unit=unit,
                    registry_name="outputs_by_name",
                ):
                    raise CompileError(
                        "Inputs refs must resolve to input declarations, not output declarations: "
                        f"{_dotted_ref_name(item.ref)}"
                    )
                target_unit, decl = self._resolve_input_decl(item.ref, unit=unit)
                sink[(target_unit.module_parts, decl.name)] = (target_unit, decl)
            elif isinstance(item, model.OverrideIoSection):
                self._collect_input_decls_from_record_items(item.items, unit=unit, sink=sink)

    def _collect_output_decls_from_io_items(
        self,
        items: tuple[model.IoItem, ...],
        *,
        unit: IndexedUnit,
        sink: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.OutputDecl]],
    ) -> None:
        for item in items:
            if isinstance(item, model.RecordSection):
                self._collect_output_decls_from_record_items(item.items, unit=unit, sink=sink)
            elif isinstance(item, model.RecordRef):
                if self._ref_exists_in_registry(
                    item.ref,
                    unit=unit,
                    registry_name="inputs_by_name",
                ):
                    raise CompileError(
                        "Outputs refs must resolve to output declarations, not input declarations: "
                        f"{_dotted_ref_name(item.ref)}"
                    )
                target_unit, decl = self._resolve_output_decl(item.ref, unit=unit)
                sink[(target_unit.module_parts, decl.name)] = (target_unit, decl)
            elif isinstance(item, model.OverrideIoSection):
                self._collect_output_decls_from_record_items(item.items, unit=unit, sink=sink)

    def _collect_input_decls_from_record_items(
        self,
        items: tuple[model.RecordItem, ...],
        *,
        unit: IndexedUnit,
        sink: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.InputDecl]],
    ) -> None:
        for item in items:
            if isinstance(item, model.RecordSection):
                self._collect_input_decls_from_record_items(item.items, unit=unit, sink=sink)
            elif isinstance(item, model.RecordRef):
                if self._ref_exists_in_registry(
                    item.ref,
                    unit=unit,
                    registry_name="outputs_by_name",
                ):
                    raise CompileError(
                        "Inputs refs must resolve to input declarations, not output declarations: "
                        f"{_dotted_ref_name(item.ref)}"
                    )
                target_unit, decl = self._resolve_input_decl(item.ref, unit=unit)
                sink[(target_unit.module_parts, decl.name)] = (target_unit, decl)

    def _collect_output_decls_from_record_items(
        self,
        items: tuple[model.RecordItem, ...],
        *,
        unit: IndexedUnit,
        sink: dict[tuple[tuple[str, ...], str], tuple[IndexedUnit, model.OutputDecl]],
    ) -> None:
        for item in items:
            if isinstance(item, model.RecordSection):
                self._collect_output_decls_from_record_items(item.items, unit=unit, sink=sink)
            elif isinstance(item, model.RecordRef):
                if self._ref_exists_in_registry(
                    item.ref,
                    unit=unit,
                    registry_name="inputs_by_name",
                ):
                    raise CompileError(
                        "Outputs refs must resolve to output declarations, not input declarations: "
                        f"{_dotted_ref_name(item.ref)}"
                    )
                target_unit, decl = self._resolve_output_decl(item.ref, unit=unit)
                sink[(target_unit.module_parts, decl.name)] = (target_unit, decl)

    def _enforce_legacy_role_workflow_order(self, agent: model.Agent) -> None:
        if len(agent.fields) != 2:
            return

        first, second = agent.fields
        if isinstance(first, (model.RoleScalar, model.RoleBlock)):
            return
        if not isinstance(second, (model.RoleScalar, model.RoleBlock)):
            return
        if not isinstance(first, model.AuthoredSlotField) or first.key != "workflow":
            return

        raise CompileError(
            f"Agent {agent.name} is outside the shipped subset: expected `role` followed by `workflow`."
        )

    def _resolve_agent_slots(
        self, agent: model.Agent, *, unit: IndexedUnit
    ) -> tuple[ResolvedAgentSlotState, ...]:
        agent_key = (unit.module_parts, agent.name)
        cached = self._resolved_agent_slot_cache.get(agent_key)
        if cached is not None:
            return cached

        if agent_key in self._agent_slot_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._agent_slot_resolution_stack, agent_key]
            )
            raise CompileError(f"Cyclic agent inheritance: {cycle}")

        self._agent_slot_resolution_stack.append(agent_key)
        try:
            parent_slots: tuple[ResolvedAgentSlotState, ...] = ()
            parent_label: str | None = None
            if agent.parent_ref is not None:
                parent_unit, parent_agent = self._resolve_parent_agent_decl(agent, unit=unit)
                parent_slots = self._resolve_agent_slots(parent_agent, unit=parent_unit)
                parent_label = f"agent {_dotted_decl_name(parent_unit.module_parts, parent_agent.name)}"

            parent_slots_by_key = {slot.key: slot for slot in parent_slots}
            resolved_slots: list[ResolvedAgentSlotState] = []
            seen_slot_keys: set[str] = set()
            accounted_parent_concrete_keys: set[str] = set()

            for field in agent.fields:
                if isinstance(field, model.AuthoredSlotField):
                    self._ensure_valid_authored_slot_key(field.key, agent.name)
                    if field.key in seen_slot_keys:
                        raise CompileError(
                            f"Duplicate authored slot key in agent {agent.name}: {field.key}"
                        )
                    seen_slot_keys.add(field.key)

                    parent_slot = parent_slots_by_key.get(field.key)
                    if isinstance(parent_slot, ResolvedAgentSlot):
                        if field.key == "workflow" and isinstance(field.value, model.WorkflowBody):
                            resolved_body = self._resolve_workflow_body(
                                field.value,
                                unit=unit,
                                owner_label=f"agent {agent.name} slot workflow",
                                parent_workflow=parent_slot.body,
                                parent_label=f"{parent_label} slot workflow",
                            )
                            accounted_parent_concrete_keys.add(field.key)
                            resolved_slots.append(
                                ResolvedAgentSlot(key=field.key, body=resolved_body)
                            )
                            continue
                        raise CompileError(
                            f"Inherited authored slot requires `inherit {field.key}` or `override {field.key}` in agent {agent.name}"
                        )
                    if isinstance(parent_slot, ResolvedAbstractAgentSlot):
                        resolved_slots.append(
                            ResolvedAgentSlot(
                                key=field.key,
                                body=self._resolve_slot_value(
                                    field.value,
                                    unit=unit,
                                    owner_label=f"agent {agent.name} slot {field.key}",
                                ),
                            )
                        )
                        continue

                    resolved_slots.append(
                        ResolvedAgentSlot(
                            key=field.key,
                            body=self._resolve_slot_value(
                                field.value,
                                unit=unit,
                                owner_label=f"agent {agent.name} slot {field.key}",
                            ),
                        )
                    )
                    continue

                if isinstance(field, model.AuthoredSlotAbstract):
                    self._ensure_valid_authored_slot_key(field.key, agent.name)
                    if field.key in seen_slot_keys:
                        raise CompileError(
                            f"Duplicate authored slot key in agent {agent.name}: {field.key}"
                        )
                    seen_slot_keys.add(field.key)
                    parent_slot = parent_slots_by_key.get(field.key)
                    if isinstance(parent_slot, ResolvedAgentSlot):
                        accounted_parent_concrete_keys.add(field.key)
                    resolved_slots.append(ResolvedAbstractAgentSlot(key=field.key))
                    continue

                if isinstance(field, model.AuthoredSlotInherit):
                    self._ensure_valid_authored_slot_key(field.key, agent.name)
                    if field.key in seen_slot_keys:
                        raise CompileError(
                            f"Duplicate authored slot key in agent {agent.name}: {field.key}"
                        )
                    seen_slot_keys.add(field.key)
                    parent_slot = parent_slots_by_key.get(field.key)
                    if parent_slot is None:
                        label = parent_label or f"agent {agent.name}"
                        raise CompileError(
                            f"Cannot inherit undefined authored slot in {label}: {field.key}"
                        )
                    if isinstance(parent_slot, ResolvedAbstractAgentSlot):
                        label = parent_label or f"agent {agent.name}"
                        raise CompileError(
                            f"E210 Abstract authored slot in {label} must be defined directly in agent {agent.name}: {field.key}"
                        )
                    accounted_parent_concrete_keys.add(field.key)
                    resolved_slots.append(parent_slot)
                    continue

                if isinstance(field, model.AuthoredSlotOverride):
                    self._ensure_valid_authored_slot_key(field.key, agent.name)
                    if field.key in seen_slot_keys:
                        raise CompileError(
                            f"Duplicate authored slot key in agent {agent.name}: {field.key}"
                        )
                    seen_slot_keys.add(field.key)
                    parent_slot = parent_slots_by_key.get(field.key)
                    if parent_slot is None:
                        label = parent_label or f"agent {agent.name}"
                        raise CompileError(
                            f"E001 Cannot override undefined authored slot in {label}: {field.key}"
                        )
                    if isinstance(parent_slot, ResolvedAbstractAgentSlot):
                        label = parent_label or f"agent {agent.name}"
                        raise CompileError(
                            f"E210 Abstract authored slot in {label} must be defined directly in agent {agent.name}: {field.key}"
                        )
                    accounted_parent_concrete_keys.add(field.key)
                    resolved_slots.append(
                        ResolvedAgentSlot(
                            key=field.key,
                            body=self._resolve_slot_value(
                                field.value,
                                unit=unit,
                                owner_label=f"agent {agent.name} slot {field.key}",
                            ),
                        )
                    )

            missing_parent_keys = [
                parent_slot.key
                for parent_slot in parent_slots
                if isinstance(parent_slot, ResolvedAgentSlot)
                and parent_slot.key not in accounted_parent_concrete_keys
            ]
            if missing_parent_keys:
                missing = ", ".join(missing_parent_keys)
                raise CompileError(
                    f"E003 Missing inherited authored slot in agent {agent.name}: {missing}"
                )

            for parent_slot in parent_slots:
                if (
                    isinstance(parent_slot, ResolvedAbstractAgentSlot)
                    and parent_slot.key not in seen_slot_keys
                ):
                    resolved_slots.append(parent_slot)

            resolved = tuple(resolved_slots)
            self._resolved_agent_slot_cache[agent_key] = resolved
            return resolved
        finally:
            self._agent_slot_resolution_stack.pop()

    def _ensure_valid_authored_slot_key(self, key: str, agent_name: str) -> None:
        if key in _RESERVED_AGENT_FIELD_KEYS:
            raise CompileError(
                f"Reserved typed agent field cannot be used as authored slot in {agent_name}: {key}"
            )

    def _resolve_slot_value(
        self,
        value: model.WorkflowSlotValue,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedWorkflowBody:
        if isinstance(value, model.WorkflowBody):
            return self._resolve_workflow_body(
                value,
                unit=unit,
                owner_label=owner_label,
            )
        target_unit, workflow_decl = self._resolve_workflow_ref(value, unit=unit)
        return self._resolve_workflow_decl(workflow_decl, unit=target_unit)

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
    ) -> CompiledSection:
        return self._compile_io_field(
            field=field,
            unit=unit,
            field_kind="outputs",
            owner_label=owner_label,
        )

    def _compile_io_field(
        self,
        field: model.InputsField | model.OutputsField,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
    ) -> CompiledSection:
        if field.parent_ref is not None:
            resolved = self._resolve_io_field_patch(
                field,
                unit=unit,
                field_kind=field_kind,
                owner_label=owner_label,
            )
            return self._compile_resolved_io_body(resolved)

        if isinstance(field.value, tuple):
            if field.title is None:
                raise CompileError(
                    f"Internal compiler error: {field_kind} field is missing title in {owner_label}"
                )
            return CompiledSection(
                title=field.title,
                body=self._compile_contract_bucket_items(
                    field.value,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=f"{field_kind} field `{field.title}`",
                ),
            )

        if isinstance(field.value, model.NameRef):
            resolved = self._resolve_io_field_ref(
                field.value,
                unit=unit,
                field_kind=field_kind,
            )
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

    def _resolve_io_field_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
    ) -> ResolvedIoBody:
        if field_kind == "inputs":
            if self._ref_exists_in_registry(
                ref,
                unit=unit,
                registry_name="outputs_blocks_by_name",
            ):
                raise CompileError(
                    "Inputs fields must resolve to inputs blocks, not outputs blocks: "
                    f"{_dotted_ref_name(ref)}"
                )
            target_unit, inputs_decl = self._resolve_inputs_block_ref(ref, unit=unit)
            return self._resolve_inputs_decl(inputs_decl, unit=target_unit)

        if self._ref_exists_in_registry(
            ref,
            unit=unit,
            registry_name="inputs_blocks_by_name",
        ):
            raise CompileError(
                "Outputs fields must resolve to outputs blocks, not inputs blocks: "
                f"{_dotted_ref_name(ref)}"
            )
        target_unit, outputs_decl = self._resolve_outputs_block_ref(ref, unit=unit)
        return self._resolve_outputs_decl(outputs_decl, unit=target_unit)

    def _resolve_io_field_patch(
        self,
        field: model.InputsField | model.OutputsField,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
    ) -> ResolvedIoBody:
        parent_ref = field.parent_ref
        if parent_ref is None:
            raise CompileError(
                f"Internal compiler error: {field_kind} patch field is missing parent ref in {owner_label}"
            )
        if not isinstance(field.value, model.IoBody) or field.title is None:
            raise CompileError(
                f"Internal compiler error: {field_kind} patch field is missing body in {owner_label}"
            )

        if field_kind == "inputs":
            if self._ref_exists_in_registry(
                parent_ref,
                unit=unit,
                registry_name="outputs_blocks_by_name",
            ):
                raise CompileError(
                    "Inputs patch fields must inherit from inputs blocks, not outputs blocks: "
                    f"{_dotted_ref_name(parent_ref)}"
                )
            parent_unit, parent_decl = self._resolve_inputs_block_ref(parent_ref, unit=unit)
            parent_body = self._resolve_inputs_decl(parent_decl, unit=parent_unit)
        else:
            if self._ref_exists_in_registry(
                parent_ref,
                unit=unit,
                registry_name="inputs_blocks_by_name",
            ):
                raise CompileError(
                    "Outputs patch fields must inherit from outputs blocks, not inputs blocks: "
                    f"{_dotted_ref_name(parent_ref)}"
                )
            parent_unit, parent_decl = self._resolve_outputs_block_ref(parent_ref, unit=unit)
            parent_body = self._resolve_outputs_decl(parent_decl, unit=parent_unit)

        return self._resolve_io_body(
            field.value,
            unit=unit,
            field_kind=field_kind,
            owner_label=owner_label,
            parent_io=parent_body,
            parent_label=f"{field_kind} {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}",
        )

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
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                body.append(
                    self._interpolate_authored_prose_line(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label=f"{field_kind} prose",
                    )
                )
                continue

            if isinstance(item, model.RecordSection):
                body.append(
                    CompiledSection(
                        title=item.title,
                        body=self._compile_contract_bucket_items(
                            item.items,
                            unit=unit,
                            field_kind=field_kind,
                            owner_label=f"{field_kind} section `{item.title}`",
                        ),
                    )
                )
                continue

            if isinstance(item, model.RecordRef):
                body.append(
                    self._compile_contract_bucket_ref(
                        item,
                        unit=unit,
                        field_kind=field_kind,
                        owner_label=owner_label,
                    )
                )
                continue

            if isinstance(item, model.RecordScalar):
                raise CompileError(
                    f"Scalar keyed items are not allowed in {owner_label}: {item.key}"
                )

            raise CompileError(
                f"Unsupported {field_kind} bucket item in {owner_label}: {type(item).__name__}"
            )

        return tuple(body)

    def _compile_contract_bucket_ref(
        self,
        item: model.RecordRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
    ) -> CompiledSection:
        if item.body is not None:
            raise CompileError(
                f"Declaration refs cannot define inline bodies in {owner_label}: "
                f"{_dotted_ref_name(item.ref)}"
            )

        if field_kind == "inputs":
            if self._ref_exists_in_registry(item.ref, unit=unit, registry_name="outputs_by_name"):
                raise CompileError(
                    "Inputs refs must resolve to input declarations, not output declarations: "
                    f"{_dotted_ref_name(item.ref)}"
                )
            target_unit, decl = self._resolve_input_decl(item.ref, unit=unit)
            return self._compile_input_decl(decl, unit=target_unit)

        if self._ref_exists_in_registry(item.ref, unit=unit, registry_name="inputs_by_name"):
            raise CompileError(
                "Outputs refs must resolve to output declarations, not input declarations: "
                f"{_dotted_ref_name(item.ref)}"
            )
        target_unit, decl = self._resolve_output_decl(item.ref, unit=unit)
        return self._compile_output_decl(decl, unit=target_unit)

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
        self, decl: model.OutputDecl, *, unit: IndexedUnit
    ) -> CompiledSection:
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

        body: list[CompiledBodyItem] = []
        if files_section is not None:
            body.extend(self._compile_output_files(files_section, unit=unit, output_name=decl.name))
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

        trust_surface_section = (
            self._compile_trust_surface_section(decl, unit=unit)
            if decl.trust_surface
            else None
        )

        if extras:
            support_items: list[CompiledBodyItem] = []
            rendered_trust_surface = False
            for item in extras:
                if (
                    trust_surface_section is not None
                    and not rendered_trust_surface
                    and isinstance(item, model.RecordSection)
                    and item.key == "standalone_read"
                ):
                    support_items.append(trust_surface_section)
                    rendered_trust_surface = True
                support_items.extend(
                    self._compile_record_item(
                        item,
                        unit=unit,
                        owner_label=f"output {decl.name}",
                        surface_label="output prose",
                    )
                )
            if trust_surface_section is not None and not rendered_trust_surface:
                support_items.append(trust_surface_section)
            body.append("")
            body.extend(support_items)
        elif trust_surface_section is not None:
            body.append("")
            body.append(trust_surface_section)

        return CompiledSection(title=decl.title, body=tuple(body))

    def _compile_trust_surface_section(
        self,
        decl: model.OutputDecl,
        *,
        unit: IndexedUnit,
    ) -> CompiledSection:
        lines: list[CompiledBodyItem] = []
        for item in decl.trust_surface:
            field_node = self._resolve_output_field_node(
                decl,
                path=item.path,
                unit=unit,
                owner_label=f"output {decl.name}",
                surface_label="trust_surface",
            )
            label = self._display_addressable_target_value(
                field_node,
                owner_label=f"output {decl.name}",
                surface_label="trust_surface",
            ).text
            if item.when_expr is not None:
                label = self._render_trust_surface_label(
                    label,
                    item.when_expr,
                    unit=unit,
                )
            lines.append(f"- {label}")
        return CompiledSection(title="Trust Surface", body=tuple(lines))

    def _render_trust_surface_label(
        self,
        label: str,
        when_expr: model.Expr,
        *,
        unit: IndexedUnit,
    ) -> str:
        if (
            isinstance(when_expr, model.ExprBinary)
            and when_expr.op == "=="
            and self._resolve_constant_enum_member(when_expr.right, unit=unit) == "rewrite"
        ):
            return f"{label} on rewrite passes"

        condition = self._render_condition_expr(when_expr, unit=unit)
        if condition.startswith("peer comparison"):
            return f"{label} when peer comparison is used"
        return f"{label} when {condition}"

    def _compile_output_files(
        self,
        section: model.RecordSection,
        *,
        unit: IndexedUnit,
        output_name: str,
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
                        ),
                    )
                )
        return tuple(body)

    def _compile_record_support_items(
        self,
        items: tuple[model.RecordItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
    ) -> tuple[CompiledBodyItem, ...]:
        body: list[CompiledBodyItem] = []
        for item in items:
            body.extend(
                self._compile_record_item(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                )
            )
        return tuple(body)

    def _compile_record_item(
        self,
        item: model.RecordItem,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
    ) -> tuple[CompiledBodyItem, ...]:
        if isinstance(item, (str, model.EmphasizedLine)):
            return (
                self._interpolate_authored_prose_line(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
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
                    ),
                ),
            )

        if isinstance(item, model.RecordScalar):
            return self._compile_fallback_scalar(
                item,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
            )

        if isinstance(item, model.RecordRef):
            body = (
                self._compile_record_support_items(
                    item.body,
                    unit=unit,
                    owner_label=f"{owner_label}.{_dotted_ref_name(item.ref)}",
                    surface_label=surface_label,
                )
                if item.body is not None
                else ()
            )
            return (
                CompiledSection(
                    title=self._display_ref(item.ref),
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
    ) -> tuple[CompiledBodyItem, ...]:
        label = _humanize_key(item.key)
        value = self._format_scalar_value(
            item.value,
            unit=unit,
            owner_label=f"{owner_label}.{item.key}",
            surface_label=surface_label,
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
            )
        )
        return (CompiledSection(title=label, body=tuple(body)),)

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

    def _resolve_input_source_spec(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> ConfigSpec:
        if not ref.module_parts:
            builtin = _BUILTIN_INPUT_SOURCES.get(ref.declaration_name)
            if builtin is not None:
                return builtin
            local_decl = unit.input_sources_by_name.get(ref.declaration_name)
            if local_decl is not None:
                return self._config_spec_from_decl(local_decl, owner_label=f"input source {local_decl.name}")

        target_unit, decl = self._resolve_input_source_decl(ref, unit=unit)
        return self._config_spec_from_decl(decl, owner_label=f"input source {decl.name}")

    def _resolve_output_target_spec(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> ConfigSpec:
        if not ref.module_parts:
            builtin = _BUILTIN_OUTPUT_TARGETS.get(ref.declaration_name)
            if builtin is not None:
                return builtin
            local_decl = unit.output_targets_by_name.get(ref.declaration_name)
            if local_decl is not None:
                return self._config_spec_from_decl(
                    local_decl,
                    owner_label=f"output target {local_decl.name}",
                )

        target_unit, decl = self._resolve_output_target_decl(ref, unit=unit)
        return self._config_spec_from_decl(decl, owner_label=f"output target {decl.name}")

    def _config_spec_from_decl(
        self,
        decl: model.InputSourceDecl | model.OutputTargetDecl,
        *,
        owner_label: str,
    ) -> ConfigSpec:
        _scalar_items, section_items, extras = self._split_record_items(
            decl.items,
            section_keys={"required", "optional"},
            owner_label=owner_label,
        )
        if extras:
            # Extra prose is fine on the declaration; it does not affect config validation.
            pass
        required_section = section_items.get("required")
        optional_section = section_items.get("optional")
        required_keys = (
            self._key_labels_from_section(required_section, owner_label=owner_label)
            if required_section is not None
            else {}
        )
        optional_keys = (
            self._key_labels_from_section(optional_section, owner_label=owner_label)
            if optional_section is not None
            else {}
        )
        return ConfigSpec(title=decl.title, required_keys=required_keys, optional_keys=optional_keys)

    def _key_labels_from_section(
        self,
        section: model.RecordSection,
        *,
        owner_label: str,
    ) -> dict[str, str]:
        labels: dict[str, str] = {}
        for item in section.items:
            if not isinstance(item, model.RecordScalar) or item.body is not None:
                raise CompileError(
                    f"Config key declarations must be simple titled scalars in {owner_label}"
                )
            if not isinstance(item.value, str):
                raise CompileError(
                    f"Config key declarations must use string labels in {owner_label}: {item.key}"
                )
            if item.key in labels:
                raise CompileError(f"Duplicate config key declaration in {owner_label}: {item.key}")
            labels[item.key] = item.value
        return labels

    def _display_output_shape(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str | None = None,
        surface_label: str | None = None,
    ) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, model.AddressableRef):
            raise CompileError(
                f"Output shape must stay typed: {owner_label or surface_label or 'output'}"
            )
        if value.module_parts:
            _target_unit, decl = self._resolve_output_shape_decl(value, unit=unit)
            return decl.title
        local_decl = unit.output_shapes_by_name.get(value.declaration_name)
        if local_decl is not None:
            return local_decl.title
        return _humanize_key(value.declaration_name)

    def _display_symbol_value(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str | None = None,
        surface_label: str | None = None,
    ) -> str:
        return self._display_scalar_value(
            value,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
        ).text

    def _format_scalar_value(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str | None = None,
        surface_label: str | None = None,
    ) -> str:
        display = self._display_scalar_value(
            value,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
        )
        if display.kind == "string_literal":
            return f"`{display.text}`"
        return display.text

    def _display_scalar_value(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str | None = None,
        surface_label: str | None = None,
    ) -> DisplayValue:
        if isinstance(value, str):
            return DisplayValue(text=value, kind="string_literal")
        if isinstance(value, model.NameRef):
            enum_decl = self._try_resolve_enum_decl(value, unit=unit)
            if enum_decl is not None:
                return DisplayValue(text=enum_decl.title, kind="title")
            return DisplayValue(text=self._display_ref(value), kind="symbol")
        if owner_label is None or surface_label is None:
            raise CompileError(
                "Internal compiler error: addressable refs require an owner label and surface label"
            )
        return self._resolve_addressable_ref_value(
            value,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            ambiguous_label=f"{surface_label} addressable ref",
            missing_local_label=surface_label,
        )

    def _value_to_symbol(
        self,
        value: model.RecordScalarValue,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
    ) -> str:
        display = self._display_scalar_value(
            value,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
        )
        return display.text

    def _display_ref(self, ref: model.NameRef) -> str:
        if ref.module_parts:
            return ".".join((*ref.module_parts, ref.declaration_name))
        return _humanize_key(ref.declaration_name)

    def _try_resolve_enum_decl(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
    ) -> model.EnumDecl | None:
        try:
            lookup_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        except CompileError:
            return None
        return lookup_unit.enums_by_name.get(ref.declaration_name)

    def _resolve_workflow_decl(
        self, workflow_decl: model.WorkflowDecl, *, unit: IndexedUnit
    ) -> ResolvedWorkflowBody:
        workflow_key = (unit.module_parts, workflow_decl.name)
        cached = self._resolved_workflow_cache.get(workflow_key)
        if cached is not None:
            return cached

        if workflow_key in self._workflow_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._workflow_resolution_stack, workflow_key]
            )
            raise CompileError(f"Cyclic workflow inheritance: {cycle}")

        self._workflow_resolution_stack.append(workflow_key)
        try:
            parent_workflow: ResolvedWorkflowBody | None = None
            parent_label: str | None = None
            if workflow_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_workflow_decl(
                    workflow_decl,
                    unit=unit,
                )
                parent_workflow = self._resolve_workflow_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"workflow {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_workflow_body(
                workflow_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, workflow_decl.name),
                parent_workflow=parent_workflow,
                parent_label=parent_label,
            )
            self._resolved_workflow_cache[workflow_key] = resolved
            return resolved
        finally:
            self._workflow_resolution_stack.pop()

    def _resolve_skills_decl(
        self, skills_decl: model.SkillsDecl, *, unit: IndexedUnit
    ) -> ResolvedSkillsBody:
        skills_key = (unit.module_parts, skills_decl.name)
        cached = self._resolved_skills_cache.get(skills_key)
        if cached is not None:
            return cached

        if skills_key in self._skills_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._skills_resolution_stack, skills_key]
            )
            raise CompileError(f"Cyclic skills inheritance: {cycle}")

        self._skills_resolution_stack.append(skills_key)
        try:
            parent_skills: ResolvedSkillsBody | None = None
            parent_label: str | None = None
            if skills_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_skills_decl(
                    skills_decl,
                    unit=unit,
                )
                parent_skills = self._resolve_skills_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"skills {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_skills_body(
                skills_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, skills_decl.name),
                parent_skills=parent_skills,
                parent_label=parent_label,
            )
            self._resolved_skills_cache[skills_key] = resolved
            return resolved
        finally:
            self._skills_resolution_stack.pop()

    def _resolve_workflow_for_addressable_paths(
        self,
        workflow_decl: model.WorkflowDecl,
        *,
        unit: IndexedUnit,
    ) -> ResolvedWorkflowBody:
        workflow_key = (unit.module_parts, workflow_decl.name)
        if (
            workflow_key in self._workflow_resolution_stack
            or workflow_key in self._workflow_addressable_resolution_stack
        ):
            return self._resolve_workflow_addressable_decl(workflow_decl, unit=unit)
        return self._resolve_workflow_decl(workflow_decl, unit=unit)

    def _resolve_skills_for_addressable_paths(
        self,
        skills_decl: model.SkillsDecl,
        *,
        unit: IndexedUnit,
    ) -> ResolvedSkillsBody:
        skills_key = (unit.module_parts, skills_decl.name)
        if (
            skills_key in self._skills_resolution_stack
            or skills_key in self._skills_addressable_resolution_stack
        ):
            return self._resolve_skills_addressable_decl(skills_decl, unit=unit)
        return self._resolve_skills_decl(skills_decl, unit=unit)

    def _resolve_workflow_addressable_decl(
        self, workflow_decl: model.WorkflowDecl, *, unit: IndexedUnit
    ) -> ResolvedWorkflowBody:
        workflow_key = (unit.module_parts, workflow_decl.name)
        cached = self._addressable_workflow_cache.get(workflow_key)
        if cached is not None:
            return cached

        if workflow_key in self._workflow_addressable_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [
                    *self._workflow_addressable_resolution_stack,
                    workflow_key,
                ]
            )
            raise CompileError(f"Cyclic workflow inheritance: {cycle}")

        self._workflow_addressable_resolution_stack.append(workflow_key)
        try:
            parent_workflow: ResolvedWorkflowBody | None = None
            parent_label: str | None = None
            if workflow_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_workflow_decl(
                    workflow_decl,
                    unit=unit,
                )
                parent_workflow = self._resolve_workflow_for_addressable_paths(
                    parent_decl,
                    unit=parent_unit,
                )
                parent_label = (
                    f"workflow {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_workflow_addressable_body(
                workflow_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, workflow_decl.name),
                parent_workflow=parent_workflow,
                parent_label=parent_label,
            )
            self._addressable_workflow_cache[workflow_key] = resolved
            return resolved
        finally:
            self._workflow_addressable_resolution_stack.pop()

    def _resolve_skills_addressable_decl(
        self, skills_decl: model.SkillsDecl, *, unit: IndexedUnit
    ) -> ResolvedSkillsBody:
        skills_key = (unit.module_parts, skills_decl.name)
        cached = self._addressable_skills_cache.get(skills_key)
        if cached is not None:
            return cached

        if skills_key in self._skills_addressable_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [
                    *self._skills_addressable_resolution_stack,
                    skills_key,
                ]
            )
            raise CompileError(f"Cyclic skills inheritance: {cycle}")

        self._skills_addressable_resolution_stack.append(skills_key)
        try:
            parent_skills: ResolvedSkillsBody | None = None
            parent_label: str | None = None
            if skills_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_skills_decl(
                    skills_decl,
                    unit=unit,
                )
                parent_skills = self._resolve_skills_for_addressable_paths(
                    parent_decl,
                    unit=parent_unit,
                )
                parent_label = (
                    f"skills {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_skills_addressable_body(
                skills_decl.body,
                unit=unit,
                owner_label=_dotted_decl_name(unit.module_parts, skills_decl.name),
                parent_skills=parent_skills,
                parent_label=parent_label,
            )
            self._addressable_skills_cache[skills_key] = resolved
            return resolved
        finally:
            self._skills_addressable_resolution_stack.pop()

    def _resolve_inputs_decl(
        self, inputs_decl: model.InputsDecl, *, unit: IndexedUnit
    ) -> ResolvedIoBody:
        inputs_key = (unit.module_parts, inputs_decl.name)
        cached = self._resolved_inputs_cache.get(inputs_key)
        if cached is not None:
            return cached

        if inputs_key in self._inputs_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._inputs_resolution_stack, inputs_key]
            )
            raise CompileError(f"Cyclic inputs inheritance: {cycle}")

        self._inputs_resolution_stack.append(inputs_key)
        try:
            parent_io: ResolvedIoBody | None = None
            parent_label: str | None = None
            if inputs_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_inputs_decl(
                    inputs_decl,
                    unit=unit,
                )
                parent_io = self._resolve_inputs_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"inputs {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_io_body(
                inputs_decl.body,
                unit=unit,
                field_kind="inputs",
                owner_label=_dotted_decl_name(unit.module_parts, inputs_decl.name),
                parent_io=parent_io,
                parent_label=parent_label,
            )
            self._resolved_inputs_cache[inputs_key] = resolved
            return resolved
        finally:
            self._inputs_resolution_stack.pop()

    def _resolve_outputs_decl(
        self, outputs_decl: model.OutputsDecl, *, unit: IndexedUnit
    ) -> ResolvedIoBody:
        outputs_key = (unit.module_parts, outputs_decl.name)
        cached = self._resolved_outputs_cache.get(outputs_key)
        if cached is not None:
            return cached

        if outputs_key in self._outputs_resolution_stack:
            cycle = " -> ".join(
                ".".join(parts + (name,)) or name
                for parts, name in [*self._outputs_resolution_stack, outputs_key]
            )
            raise CompileError(f"Cyclic outputs inheritance: {cycle}")

        self._outputs_resolution_stack.append(outputs_key)
        try:
            parent_io: ResolvedIoBody | None = None
            parent_label: str | None = None
            if outputs_decl.parent_ref is not None:
                parent_unit, parent_decl = self._resolve_parent_outputs_decl(
                    outputs_decl,
                    unit=unit,
                )
                parent_io = self._resolve_outputs_decl(parent_decl, unit=parent_unit)
                parent_label = (
                    f"outputs {_dotted_decl_name(parent_unit.module_parts, parent_decl.name)}"
                )

            resolved = self._resolve_io_body(
                outputs_decl.body,
                unit=unit,
                field_kind="outputs",
                owner_label=_dotted_decl_name(unit.module_parts, outputs_decl.name),
                parent_io=parent_io,
                parent_label=parent_label,
            )
            self._resolved_outputs_cache[outputs_key] = resolved
            return resolved
        finally:
            self._outputs_resolution_stack.pop()

    def _resolve_skills_value(
        self,
        value: model.SkillsValue,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedSkillsBody:
        if isinstance(value, model.NameRef):
            target_unit, skills_decl = self._resolve_skills_ref(value, unit=unit)
            return self._resolve_skills_decl(skills_decl, unit=target_unit)
        return self._resolve_skills_body(
            value,
            unit=unit,
            owner_label=owner_label,
        )

    def _resolve_skills_value_for_addressable_paths(
        self,
        value: model.SkillsValue,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedSkillsBody:
        if isinstance(value, model.NameRef):
            target_unit, skills_decl = self._resolve_skills_ref(value, unit=unit)
            return self._resolve_skills_for_addressable_paths(skills_decl, unit=target_unit)
        return self._resolve_skills_addressable_body(
            value,
            unit=unit,
            owner_label=owner_label,
        )

    def _resolve_io_body(
        self,
        io_body: model.IoBody,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
        parent_io: ResolvedIoBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedIoBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label=f"{field_kind} prose",
                ambiguous_label=f"{field_kind} prose interpolation ref",
            )
            for line in io_body.preamble
        )
        if parent_io is None:
            return ResolvedIoBody(
                title=io_body.title,
                preamble=resolved_preamble,
                items=self._resolve_non_inherited_io_items(
                    io_body.items,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=owner_label,
                ),
            )

        unkeyed_parent_titles = [
            item.section.title for item in parent_io.items if isinstance(item, ResolvedIoRef)
        ]
        if unkeyed_parent_titles:
            details = ", ".join(unkeyed_parent_titles)
            raise CompileError(
                f"Cannot inherit {field_kind} block with unkeyed top-level refs in {parent_label}: {details}"
            )

        parent_items_by_key = {
            item.key: item for item in parent_io.items if isinstance(item, ResolvedIoSection)
        }
        resolved_items: list[ResolvedIoItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in io_body.items:
            if isinstance(item, model.RecordRef):
                resolved_items.append(
                    self._resolve_io_ref_item(
                        item,
                        unit=unit,
                        field_kind=field_kind,
                        owner_label=owner_label,
                    )
                )
                continue

            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate {field_kind} item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.RecordSection):
                resolved_items.append(
                    self._resolve_io_section_item(
                        item,
                        unit=unit,
                        field_kind=field_kind,
                    )
                )
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined {field_kind} entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined {field_kind} entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if not isinstance(item, model.OverrideIoSection):
                raise CompileError(
                    f"Internal compiler error: unsupported {field_kind} override in {owner_label}: {type(item).__name__}"
                )
            resolved_items.append(
                ResolvedIoSection(
                    key=key,
                    section=CompiledSection(
                        title=item.title if item.title is not None else parent_item.section.title,
                        body=self._compile_contract_bucket_items(
                            item.items,
                            unit=unit,
                            field_kind=field_kind,
                            owner_label=(
                                f"{field_kind} section `{item.title if item.title is not None else parent_item.section.title}`"
                            ),
                        ),
                    ),
                )
            )

        missing_keys = [
            item.key for item in parent_io.items if isinstance(item, ResolvedIoSection) and item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited {field_kind} entry in {owner_label}: {missing}"
            )

        return ResolvedIoBody(
            title=io_body.title,
            preamble=resolved_preamble,
            items=tuple(resolved_items),
        )

    def _resolve_skills_body(
        self,
        skills_body: model.SkillsBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_skills: ResolvedSkillsBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedSkillsBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label="skills prose",
                ambiguous_label="skills prose interpolation ref",
            )
            for line in skills_body.preamble
        )
        if parent_skills is None:
            return ResolvedSkillsBody(
                title=skills_body.title,
                preamble=resolved_preamble,
                items=self._resolve_non_inherited_skills_items(
                    skills_body.items,
                    unit=unit,
                    owner_label=owner_label,
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_skills.items}
        resolved_items: list[ResolvedSkillsItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in skills_body.items:
            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate skills item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.SkillsSection):
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_skills_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.SkillEntry):
                resolved_items.append(
                    self._resolve_skill_entry(
                        item,
                        unit=unit,
                    )
                )
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined skills entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined skills entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if isinstance(item, model.OverrideSkillsSection):
                if not isinstance(parent_item, ResolvedSkillsSection):
                    raise CompileError(
                        f"Override kind mismatch for skills entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title if item.title is not None else parent_item.title,
                        items=self._resolve_skills_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if not isinstance(parent_item, ResolvedSkillEntry):
                raise CompileError(
                    f"Override kind mismatch for skills entry in {owner_label}: {key}"
                )
            resolved_items.append(
                self._resolve_skill_entry(
                    item,
                    unit=unit,
                )
            )

        missing_keys = [
            parent_item.key
            for parent_item in parent_skills.items
            if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited skills entry in {owner_label}: {missing}"
            )

        return ResolvedSkillsBody(
            title=skills_body.title,
            preamble=resolved_preamble,
            items=tuple(resolved_items),
        )

    def _resolve_workflow_body(
        self,
        workflow_body: model.WorkflowBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_workflow: ResolvedWorkflowBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedWorkflowBody:
        resolved_preamble = tuple(
            self._interpolate_authored_prose_line(
                line,
                unit=unit,
                owner_label=owner_label,
                surface_label="workflow strings",
                ambiguous_label="workflow string interpolation ref",
            )
            for line in workflow_body.preamble
        )
        if parent_workflow is None:
            return ResolvedWorkflowBody(
                title=workflow_body.title,
                preamble=resolved_preamble,
                items=self._resolve_non_inherited_items(
                    workflow_body.items,
                    unit=unit,
                    owner_label=owner_label,
                ),
                law=self._resolve_law_body(
                    workflow_body.law,
                    owner_label=owner_label,
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_workflow.items}
        resolved_items: list[ResolvedWorkflowItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in workflow_body.items:
            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate workflow item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.LocalSection):
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title,
                        items=self._resolve_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
                    )
                )
                continue

            if isinstance(item, model.WorkflowSkillsItem):
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined workflow entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined workflow entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if isinstance(item, model.OverrideSection):
                if not isinstance(parent_item, ResolvedSectionItem):
                    raise CompileError(
                        f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title if item.title is not None else parent_item.title,
                        items=self._resolve_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.OverrideWorkflowSkillsItem):
                if not isinstance(parent_item, ResolvedWorkflowSkillsItem):
                    raise CompileError(
                        f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if not isinstance(parent_item, ResolvedUseItem):
                raise CompileError(
                    f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                )
            target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
            resolved_items.append(
                ResolvedUseItem(
                    key=key,
                    target_unit=target_unit,
                    workflow_decl=workflow_decl,
                )
            )

        missing_keys = [
            parent_item.key
            for parent_item in parent_workflow.items
            if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited workflow entry in {owner_label}: {missing}"
            )

        return ResolvedWorkflowBody(
            title=workflow_body.title,
            preamble=resolved_preamble,
            items=tuple(resolved_items),
            law=self._resolve_law_body(
                workflow_body.law,
                owner_label=owner_label,
                parent_law=parent_workflow.law,
                parent_label=parent_label,
            ),
        )

    def _resolve_law_body(
        self,
        law_body: model.LawBody | None,
        *,
        owner_label: str,
        parent_law: model.LawBody | None = None,
        parent_label: str | None = None,
    ) -> model.LawBody | None:
        if law_body is None:
            return parent_law
        if parent_law is None:
            return law_body

        parent_items = parent_law.items
        parent_has_sections = all(
            isinstance(item, model.LawSection) for item in parent_items
        )
        child_has_named_items = all(
            isinstance(
                item,
                (model.LawSection, model.LawInherit, model.LawOverrideSection),
            )
            for item in law_body.items
        )

        if not parent_has_sections or not child_has_named_items:
            raise CompileError(
                f"Inherited law blocks must use named sections only in {owner_label}"
            )

        parent_items_by_key = {
            item.key: item for item in parent_items if isinstance(item, model.LawSection)
        }
        resolved_items: list[model.LawTopLevelItem] = []
        accounted_keys: set[str] = set()

        for item in law_body.items:
            if isinstance(item, model.LawSection):
                if item.key in parent_items_by_key:
                    raise CompileError(
                        f"Inherited law block accounts for the same parent subsection more than once in {owner_label}: {item.key}"
                    )
                resolved_items.append(item)
                continue

            parent_item = parent_items_by_key.get(item.key)
            if parent_item is None:
                raise CompileError(
                    f"Cannot override undefined law section in {parent_label}: {item.key}"
                )
            if item.key in accounted_keys:
                raise CompileError(
                    f"Inherited law block accounts for the same parent subsection more than once in {owner_label}: {item.key}"
                )
            accounted_keys.add(item.key)

            if isinstance(item, model.LawInherit):
                resolved_items.append(parent_item)
            else:
                resolved_items.append(model.LawSection(key=item.key, items=item.items))

        missing_keys = sorted(set(parent_items_by_key) - accounted_keys)
        if missing_keys:
            raise CompileError(
                f"Inherited law block omits parent subsection(s) in {owner_label}: {', '.join(missing_keys)}"
            )

        return model.LawBody(items=tuple(resolved_items))

    def _resolve_skills_addressable_body(
        self,
        skills_body: model.SkillsBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_skills: ResolvedSkillsBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedSkillsBody:
        if parent_skills is None:
            return ResolvedSkillsBody(
                title=skills_body.title,
                preamble=(),
                items=self._resolve_non_inherited_addressable_skills_items(
                    skills_body.items,
                    unit=unit,
                    owner_label=owner_label,
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_skills.items}
        resolved_items: list[ResolvedSkillsItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in skills_body.items:
            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate skills item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.SkillsSection):
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_addressable_skills_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if isinstance(item, model.SkillEntry):
                resolved_items.append(self._resolve_skill_entry(item, unit=unit))
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined skills entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined skills entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if isinstance(item, model.OverrideSkillsSection):
                if not isinstance(parent_item, ResolvedSkillsSection):
                    raise CompileError(
                        f"Override kind mismatch for skills entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title if item.title is not None else parent_item.title,
                        items=self._resolve_addressable_skills_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if not isinstance(parent_item, ResolvedSkillEntry):
                raise CompileError(
                    f"Override kind mismatch for skills entry in {owner_label}: {key}"
                )
            resolved_items.append(self._resolve_skill_entry(item, unit=unit))

        missing_keys = [
            parent_item.key
            for parent_item in parent_skills.items
            if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited skills entry in {owner_label}: {missing}"
            )

        return ResolvedSkillsBody(
            title=skills_body.title,
            preamble=(),
            items=tuple(resolved_items),
        )

    def _resolve_workflow_addressable_body(
        self,
        workflow_body: model.WorkflowBody,
        *,
        unit: IndexedUnit,
        owner_label: str,
        parent_workflow: ResolvedWorkflowBody | None = None,
        parent_label: str | None = None,
    ) -> ResolvedWorkflowBody:
        if parent_workflow is None:
            return ResolvedWorkflowBody(
                title=workflow_body.title,
                preamble=(),
                items=self._resolve_non_inherited_addressable_workflow_items(
                    workflow_body.items,
                    unit=unit,
                    owner_label=owner_label,
                ),
                law=self._resolve_law_body(
                    workflow_body.law,
                    owner_label=owner_label,
                ),
            )

        parent_items_by_key = {item.key: item for item in parent_workflow.items}
        resolved_items: list[ResolvedWorkflowItem] = []
        emitted_keys: set[str] = set()
        accounted_keys: set[str] = set()

        for item in workflow_body.items:
            key = item.key
            if key in emitted_keys:
                raise CompileError(f"Duplicate workflow item key in {owner_label}: {key}")
            emitted_keys.add(key)

            if isinstance(item, model.LocalSection):
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title,
                        items=self._resolve_addressable_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
                    )
                )
                continue

            if isinstance(item, model.WorkflowSkillsItem):
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value_for_addressable_paths(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            parent_item = parent_items_by_key.get(key)
            if isinstance(item, model.InheritItem):
                if parent_item is None:
                    raise CompileError(
                        f"Cannot inherit undefined workflow entry in {parent_label}: {key}"
                    )
                accounted_keys.add(key)
                resolved_items.append(parent_item)
                continue

            if parent_item is None:
                raise CompileError(
                    f"E001 Cannot override undefined workflow entry in {parent_label}: {key}"
                )

            accounted_keys.add(key)
            if isinstance(item, model.OverrideSection):
                if not isinstance(parent_item, ResolvedSectionItem):
                    raise CompileError(
                        f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title if item.title is not None else parent_item.title,
                        items=self._resolve_addressable_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if isinstance(item, model.OverrideWorkflowSkillsItem):
                if not isinstance(parent_item, ResolvedWorkflowSkillsItem):
                    raise CompileError(
                        f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                    )
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value_for_addressable_paths(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if not isinstance(parent_item, ResolvedUseItem):
                raise CompileError(
                    f"Override kind mismatch for workflow entry in {owner_label}: {key}"
                )
            target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
            resolved_items.append(
                ResolvedUseItem(
                    key=key,
                    target_unit=target_unit,
                    workflow_decl=workflow_decl,
                )
            )

        missing_keys = [
            parent_item.key
            for parent_item in parent_workflow.items
            if parent_item.key not in accounted_keys
        ]
        if missing_keys:
            missing = ", ".join(missing_keys)
            raise CompileError(
                f"E003 Missing inherited workflow entry in {owner_label}: {missing}"
            )

        return ResolvedWorkflowBody(
            title=workflow_body.title,
            preamble=(),
            items=tuple(resolved_items),
            law=self._resolve_law_body(
                workflow_body.law,
                owner_label=owner_label,
                parent_law=parent_workflow.law,
                parent_label=parent_label,
            ),
        )

    def _resolve_non_inherited_items(
        self,
        workflow_items: tuple[model.WorkflowItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedWorkflowItem, ...]:
        resolved_items: list[ResolvedWorkflowItem] = []
        seen_keys: set[str] = set()

        for item in workflow_items:
            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate workflow item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.LocalSection):
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title,
                        items=self._resolve_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
                    )
                )
                continue

            if isinstance(item, model.WorkflowSkillsItem):
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited workflow in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _resolve_non_inherited_addressable_workflow_items(
        self,
        workflow_items: tuple[model.WorkflowItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedWorkflowItem, ...]:
        resolved_items: list[ResolvedWorkflowItem] = []
        seen_keys: set[str] = set()

        for item in workflow_items:
            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate workflow item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.LocalSection):
                resolved_items.append(
                    ResolvedSectionItem(
                        key=key,
                        title=item.title,
                        items=self._resolve_addressable_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if isinstance(item, model.WorkflowUse):
                target_unit, workflow_decl = self._resolve_workflow_ref(item.target, unit=unit)
                resolved_items.append(
                    ResolvedUseItem(
                        key=key,
                        target_unit=target_unit,
                        workflow_decl=workflow_decl,
                    )
                )
                continue

            if isinstance(item, model.WorkflowSkillsItem):
                resolved_items.append(
                    ResolvedWorkflowSkillsItem(
                        key=key,
                        body=self._resolve_skills_value_for_addressable_paths(
                            item.value,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited workflow in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _resolve_non_inherited_skills_items(
        self,
        skills_items: tuple[model.SkillsItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSkillsItem, ...]:
        resolved_items: list[ResolvedSkillsItem] = []
        seen_keys: set[str] = set()

        for item in skills_items:
            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate skills item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.SkillsSection):
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_skills_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{key}",
                        ),
                    )
                )
                continue

            if isinstance(item, model.SkillEntry):
                resolved_items.append(self._resolve_skill_entry(item, unit=unit))
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited skills block in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _resolve_non_inherited_addressable_skills_items(
        self,
        skills_items: tuple[model.SkillsItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSkillsItem, ...]:
        resolved_items: list[ResolvedSkillsItem] = []
        seen_keys: set[str] = set()

        for item in skills_items:
            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate skills item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.SkillsSection):
                resolved_items.append(
                    ResolvedSkillsSection(
                        key=key,
                        title=item.title,
                        items=self._resolve_addressable_skills_section_body_items(
                            item.items,
                            unit=unit,
                        ),
                    )
                )
                continue

            if isinstance(item, model.SkillEntry):
                resolved_items.append(self._resolve_skill_entry(item, unit=unit))
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited skills block in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _resolve_non_inherited_io_items(
        self,
        io_items: tuple[model.IoItem, ...],
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
    ) -> tuple[ResolvedIoItem, ...]:
        resolved_items: list[ResolvedIoItem] = []
        seen_keys: set[str] = set()

        for item in io_items:
            if isinstance(item, model.RecordRef):
                resolved_items.append(
                    self._resolve_io_ref_item(
                        item,
                        unit=unit,
                        field_kind=field_kind,
                        owner_label=owner_label,
                    )
                )
                continue

            key = item.key
            if key in seen_keys:
                raise CompileError(f"Duplicate {field_kind} item key in {owner_label}: {key}")
            seen_keys.add(key)

            if isinstance(item, model.RecordSection):
                resolved_items.append(
                    self._resolve_io_section_item(
                        item,
                        unit=unit,
                        field_kind=field_kind,
                    )
                )
                continue

            item_label = "inherit" if isinstance(item, model.InheritItem) else "override"
            raise CompileError(
                f"{item_label} requires an inherited {field_kind} block in {owner_label}: {key}"
            )

        return tuple(resolved_items)

    def _resolve_io_section_item(
        self,
        item: model.RecordSection,
        *,
        unit: IndexedUnit,
        field_kind: str,
    ) -> ResolvedIoSection:
        return ResolvedIoSection(
            key=item.key,
            section=CompiledSection(
                title=item.title,
                body=self._compile_contract_bucket_items(
                    item.items,
                    unit=unit,
                    field_kind=field_kind,
                    owner_label=f"{field_kind} section `{item.title}`",
                ),
            ),
        )

    def _resolve_io_ref_item(
        self,
        item: model.RecordRef,
        *,
        unit: IndexedUnit,
        field_kind: str,
        owner_label: str,
    ) -> ResolvedIoRef:
        return ResolvedIoRef(
            section=self._compile_contract_bucket_ref(
                item,
                unit=unit,
                field_kind=field_kind,
                owner_label=owner_label,
            )
        )

    def _resolve_skills_section_body_items(
        self,
        items: tuple[model.SkillsSectionItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSkillsSectionBodyItem, ...]:
        resolved: list[ResolvedSkillsSectionBodyItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                resolved.append(
                    self._interpolate_authored_prose_line(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="skills prose",
                        ambiguous_label="skills prose interpolation ref",
                    )
                )
                continue
            resolved.append(self._resolve_skill_entry(item, unit=unit))
        return tuple(resolved)

    def _resolve_addressable_skills_section_body_items(
        self,
        items: tuple[model.SkillsSectionItem, ...],
        *,
        unit: IndexedUnit,
    ) -> tuple[ResolvedSkillsSectionBodyItem, ...]:
        resolved: list[ResolvedSkillsSectionBodyItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                continue
            resolved.append(self._resolve_skill_entry(item, unit=unit))
        return tuple(resolved)

    def _resolve_skill_entry(
        self,
        entry: model.SkillEntry | model.OverrideSkillEntry,
        *,
        unit: IndexedUnit,
    ) -> ResolvedSkillEntry:
        target_unit, skill_decl = self._resolve_skill_decl(entry.target, unit=unit)
        return ResolvedSkillEntry(
            key=entry.key,
            metadata_unit=unit,
            target_unit=target_unit,
            skill_decl=skill_decl,
            items=entry.items,
        )

    def _resolve_section_body_items(
        self,
        items: tuple[model.SectionBodyItem, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> tuple[ResolvedSectionBodyItem, ...]:
        resolved: list[ResolvedSectionBodyItem] = []
        for item in items:
            if isinstance(item, str):
                resolved.append(
                    self._interpolate_authored_prose_string(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="workflow strings",
                        ambiguous_label="workflow string interpolation ref",
                    )
                )
                continue
            if isinstance(item, model.EmphasizedLine):
                resolved.append(
                    self._interpolate_authored_prose_line(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="workflow strings",
                        ambiguous_label="workflow string interpolation ref",
                    )
                )
                continue
            if isinstance(item, model.LocalSection):
                resolved.append(
                    ResolvedSectionItem(
                        key=item.key,
                        title=item.title,
                        items=self._resolve_section_body_items(
                            item.items,
                            unit=unit,
                            owner_label=f"{owner_label}.{item.key}",
                        ),
                    )
                )
                continue
            if isinstance(item, model.SectionBodyRef):
                resolved.append(
                    self._resolve_section_body_ref(item.ref, unit=unit, owner_label=owner_label)
                )
                continue
            self._validate_route_target(item.target, unit=unit)
            resolved.append(
                ResolvedRouteLine(
                    label=self._interpolate_authored_prose_string(
                        item.label,
                        unit=unit,
                        owner_label=owner_label,
                        surface_label="route labels",
                    ),
                    target_name=item.target.declaration_name,
                )
            )
        return tuple(resolved)

    def _resolve_addressable_section_body_items(
        self,
        items: tuple[model.SectionBodyItem, ...],
        *,
        unit: IndexedUnit,
    ) -> tuple[ResolvedSectionBodyItem, ...]:
        resolved: list[ResolvedSectionBodyItem] = []
        for item in items:
            if not isinstance(item, model.LocalSection):
                continue
            resolved.append(
                ResolvedSectionItem(
                    key=item.key,
                    title=item.title,
                    items=self._resolve_addressable_section_body_items(
                        item.items,
                        unit=unit,
                    ),
                )
            )
        return tuple(resolved)

    def _resolve_section_body_ref(
        self,
        ref: model.AddressableRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> ResolvedSectionRef:
        value = self._resolve_addressable_ref_value(
            ref,
            unit=unit,
            owner_label=owner_label,
            surface_label="workflow section bodies",
            ambiguous_label="workflow section declaration ref",
            missing_local_label="workflow section body",
        )
        return ResolvedSectionRef(label=value.text)

    def _interpolate_authored_prose_string(
        self,
        value: str,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str | None = None,
    ) -> str:
        if "{{" not in value and "}}" not in value:
            return value

        parts: list[str] = []
        cursor = 0
        for match in _INTERPOLATION_RE.finditer(value):
            between = value[cursor:match.start()]
            if "{{" in between or "}}" in between:
                raise CompileError(
                    f"Malformed interpolation in {owner_label}: {value}"
                )
            parts.append(between)
            parts.append(
                self._resolve_authored_prose_interpolation_expr(
                    match.group(1),
                    unit=unit,
                    owner_label=owner_label,
                    surface_label=surface_label,
                    ambiguous_label=ambiguous_label,
                )
            )
            cursor = match.end()

        tail = value[cursor:]
        if "{{" in tail or "}}" in tail:
            raise CompileError(
                f"Malformed interpolation in {owner_label}: {value}"
            )
        parts.append(tail)
        return "".join(parts)

    def _interpolate_authored_prose_line(
        self,
        value: model.ProseLine,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str | None = None,
    ) -> model.ProseLine:
        if isinstance(value, str):
            return self._interpolate_authored_prose_string(
                value,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ambiguous_label=ambiguous_label,
            )
        return model.EmphasizedLine(
            kind=value.kind,
            text=self._interpolate_authored_prose_string(
                value.text,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ambiguous_label=ambiguous_label,
            ),
        )

    def _resolve_authored_prose_interpolation_expr(
        self,
        expression: str,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str | None = None,
    ) -> str:
        match = _INTERPOLATION_EXPR_RE.fullmatch(expression)
        if match is None:
            raise CompileError(
                f"Invalid interpolation in {owner_label}: {{{{{expression}}}}}"
            )

        ref = model.AddressableRef(
            root=_name_ref_from_dotted_name(match.group(1)),
            path=tuple(match.group(2).split(".")) if match.group(2) is not None else (),
        )
        return self._resolve_addressable_ref_value(
            ref,
            unit=unit,
            owner_label=owner_label,
            surface_label=surface_label,
            ambiguous_label=ambiguous_label or f"{surface_label} interpolation ref",
            missing_local_label=surface_label,
        ).text

    def _resolve_readable_decl(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str,
        missing_local_label: str,
    ) -> tuple[IndexedUnit, ReadableDecl]:
        target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        matches = self._find_readable_decl_matches(
            ref.declaration_name,
            unit=target_unit,
        )
        dotted_name = _dotted_ref_name(ref) if ref.module_parts else ref.declaration_name

        if len(matches) == 1:
            decl = matches[0][1]
            if isinstance(decl, model.Agent) and decl.abstract:
                raise CompileError(
                    f"Abstract agent refs are not allowed in {surface_label}; "
                    f"mention a concrete agent instead: {dotted_name}"
                )
            return target_unit, decl

        if len(matches) > 1:
            labels = ", ".join(label for label, _decl in matches)
            raise CompileError(
                f"Ambiguous {ambiguous_label} in {owner_label}: "
                f"{dotted_name} matches {labels}"
            )

        if target_unit.workflows_by_name.get(ref.declaration_name) is not None:
            raise CompileError(
                f"Workflow refs are not allowed in {surface_label}; "
                f"use `use` for workflow composition: {dotted_name}"
            )

        if ref.module_parts:
            raise CompileError(f"Missing imported declaration: {dotted_name}")

        raise CompileError(
            f"Missing local declaration ref in {missing_local_label} {owner_label}: "
            f"{ref.declaration_name}"
        )

    def _resolve_addressable_ref_value(
        self,
        ref: model.AddressableRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
        ambiguous_label: str,
        missing_local_label: str,
    ) -> DisplayValue:
        ref_label = _display_addressable_ref(ref)
        if not ref.path:
            target_unit, decl = self._resolve_readable_decl(
                ref.root,
                unit=unit,
                owner_label=owner_label,
                surface_label=surface_label,
                ambiguous_label=ambiguous_label,
                missing_local_label=missing_local_label,
            )
            return self._display_addressable_target_value(
                AddressableNode(unit=target_unit, root_decl=decl, target=decl),
                owner_label=owner_label,
                surface_label=surface_label,
            )

        target_unit, decl = self._resolve_addressable_root_decl(
            ref.root,
            unit=unit,
            owner_label=owner_label,
            ambiguous_label=ambiguous_label,
            missing_local_label=missing_local_label,
        )
        return self._resolve_addressable_path_value(
            AddressableNode(unit=target_unit, root_decl=decl, target=decl),
            ref.path,
            owner_label=owner_label,
            surface_label=surface_label,
            ref_label=ref_label,
        )

    def _resolve_addressable_root_decl(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        owner_label: str,
        ambiguous_label: str,
        missing_local_label: str,
    ) -> tuple[IndexedUnit, AddressableRootDecl]:
        target_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
        matches = self._find_addressable_root_matches(
            ref.declaration_name,
            unit=target_unit,
        )
        dotted_name = _dotted_ref_name(ref) if ref.module_parts else ref.declaration_name

        if len(matches) == 1:
            decl = matches[0][1]
            if isinstance(decl, model.Agent) and decl.abstract:
                raise CompileError(
                    "Abstract agent refs are not allowed in addressable paths; "
                    f"mention a concrete agent instead: {dotted_name}"
                )
            return target_unit, decl

        if len(matches) > 1:
            labels = ", ".join(label for label, _decl in matches)
            raise CompileError(
                f"Ambiguous {ambiguous_label} in {owner_label}: "
                f"{dotted_name} matches {labels}"
            )

        if ref.module_parts:
            raise CompileError(f"Missing imported declaration: {dotted_name}")

        raise CompileError(
            f"Missing local declaration ref in {missing_local_label} {owner_label}: "
            f"{ref.declaration_name}"
        )

    def _resolve_addressable_path_value(
        self,
        start: AddressableNode,
        path: tuple[str, ...],
        *,
        owner_label: str,
        surface_label: str,
        ref_label: str,
    ) -> DisplayValue:
        current = start

        for index, segment in enumerate(path):
            is_last = index == len(path) - 1
            if is_last and isinstance(current.target, model.Agent) and segment == "name":
                return DisplayValue(text=current.target.name, kind="symbol")
            if is_last and segment == "title":
                title = self._display_addressable_title(
                    current,
                    owner_label=owner_label,
                    surface_label=surface_label,
                )
                if title is not None:
                    return DisplayValue(text=title, kind="title")
            if is_last and segment in {"name", "title"}:
                raise CompileError(
                    f"Unknown addressable path on {surface_label} in {owner_label}: "
                    f"{ref_label}"
                )

            children = self._get_addressable_children(current)
            if children is None:
                raise CompileError(
                    "Addressable path must stay addressable on "
                    f"{surface_label} in {owner_label}: {ref_label}"
                )
            next_node = children.get(segment)
            if next_node is None:
                raise CompileError(
                    f"Unknown addressable path on {surface_label} in {owner_label}: "
                    f"{ref_label}"
                )
            current = next_node

        return self._display_addressable_target_value(
            current,
            owner_label=owner_label,
            surface_label=surface_label,
        )

    def _get_addressable_children(
        self,
        node: AddressableNode,
    ) -> dict[str, AddressableNode] | None:
        target = node.target
        if isinstance(
            target,
            (
                model.InputDecl,
                model.InputSourceDecl,
                model.OutputDecl,
                model.OutputTargetDecl,
                model.OutputShapeDecl,
                model.JsonSchemaDecl,
                model.SkillDecl,
            ),
        ):
            return self._record_items_to_addressable_children(
                target.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, model.RecordScalar):
            if target.body is None:
                return None
            return self._record_items_to_addressable_children(
                target.body,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, model.RecordSection):
            return self._record_items_to_addressable_children(
                target.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, model.WorkflowDecl):
            workflow_body = self._resolve_workflow_for_addressable_paths(
                target,
                unit=node.unit,
            )
            return self._workflow_items_to_addressable_children(
                workflow_body.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, ResolvedSectionItem):
            return self._workflow_section_items_to_addressable_children(
                target.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, ResolvedUseItem):
            workflow_body = self._resolve_workflow_for_addressable_paths(
                target.workflow_decl,
                unit=target.target_unit,
            )
            return self._workflow_items_to_addressable_children(
                workflow_body.items,
                unit=target.target_unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, ResolvedWorkflowSkillsItem):
            return self._skills_items_to_addressable_children(
                target.body.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, model.SkillsDecl):
            skills_body = self._resolve_skills_for_addressable_paths(
                target,
                unit=node.unit,
            )
            return self._skills_items_to_addressable_children(
                skills_body.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, ResolvedSkillsSection):
            return self._skills_section_items_to_addressable_children(
                target.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, ResolvedSkillEntry):
            if not target.items:
                return None
            return self._record_items_to_addressable_children(
                target.items,
                unit=node.unit,
                root_decl=node.root_decl,
            )
        if isinstance(target, model.EnumDecl):
            return {
                member.key: AddressableNode(
                    unit=node.unit,
                    root_decl=node.root_decl,
                    target=member,
                )
                for member in target.members
            }
        return None

    def _record_items_to_addressable_children(
        self,
        items: tuple[model.RecordItem, ...],
        *,
        unit: IndexedUnit,
        root_decl: AddressableRootDecl,
    ) -> dict[str, AddressableNode]:
        children: dict[str, AddressableNode] = {}
        for item in items:
            if isinstance(item, (model.RecordScalar, model.RecordSection)):
                children[item.key] = AddressableNode(
                    unit=unit,
                    root_decl=root_decl,
                    target=item,
                )
        return children

    def _workflow_items_to_addressable_children(
        self,
        items: tuple[ResolvedWorkflowItem, ...],
        *,
        unit: IndexedUnit,
        root_decl: AddressableRootDecl,
    ) -> dict[str, AddressableNode]:
        children: dict[str, AddressableNode] = {}
        for item in items:
            children[item.key] = AddressableNode(unit=unit, root_decl=root_decl, target=item)
        return children

    def _workflow_section_items_to_addressable_children(
        self,
        items: tuple[ResolvedSectionBodyItem, ...],
        *,
        unit: IndexedUnit,
        root_decl: AddressableRootDecl,
    ) -> dict[str, AddressableNode]:
        children: dict[str, AddressableNode] = {}
        for item in items:
            if isinstance(item, ResolvedSectionItem):
                children[item.key] = AddressableNode(
                    unit=unit,
                    root_decl=root_decl,
                    target=item,
                )
        return children

    def _skills_items_to_addressable_children(
        self,
        items: tuple[ResolvedSkillsItem, ...],
        *,
        unit: IndexedUnit,
        root_decl: AddressableRootDecl,
    ) -> dict[str, AddressableNode]:
        children: dict[str, AddressableNode] = {}
        for item in items:
            children[item.key] = AddressableNode(unit=unit, root_decl=root_decl, target=item)
        return children

    def _skills_section_items_to_addressable_children(
        self,
        items: tuple[ResolvedSkillsSectionBodyItem, ...],
        *,
        unit: IndexedUnit,
        root_decl: AddressableRootDecl,
    ) -> dict[str, AddressableNode]:
        children: dict[str, AddressableNode] = {}
        for item in items:
            if isinstance(item, ResolvedSkillEntry):
                children[item.key] = AddressableNode(
                    unit=unit,
                    root_decl=root_decl,
                    target=item,
                )
        return children

    def _display_addressable_target_value(
        self,
        node: AddressableNode,
        *,
        owner_label: str,
        surface_label: str,
    ) -> DisplayValue:
        target = node.target
        if isinstance(target, model.Agent):
            return DisplayValue(text=target.name, kind="symbol")
        if isinstance(target, model.WorkflowDecl):
            return DisplayValue(text=target.body.title, kind="title")
        if isinstance(target, model.SkillsDecl):
            return DisplayValue(text=target.body.title, kind="title")
        if isinstance(target, model.EnumDecl):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(
            target,
            (
                model.InputDecl,
                model.InputSourceDecl,
                model.OutputDecl,
                model.OutputTargetDecl,
                model.OutputShapeDecl,
                model.JsonSchemaDecl,
                model.SkillDecl,
            ),
        ):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, model.RecordSection):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, model.RecordScalar):
            if target.body is not None:
                return DisplayValue(
                    text=self._display_record_scalar_title(
                        target,
                        node=node,
                        owner_label=owner_label,
                        surface_label=surface_label,
                    ),
                    kind="title",
                )
            return self._display_scalar_value(
                target.value,
                unit=node.unit,
                owner_label=owner_label,
                surface_label=surface_label,
            )
        if isinstance(target, model.EnumMember):
            return DisplayValue(text=target.value, kind="symbol")
        if isinstance(target, ResolvedSectionItem):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, ResolvedUseItem):
            return DisplayValue(text=target.workflow_decl.body.title, kind="title")
        if isinstance(target, ResolvedWorkflowSkillsItem):
            return DisplayValue(text=target.body.title, kind="title")
        if isinstance(target, ResolvedSkillsSection):
            return DisplayValue(text=target.title, kind="title")
        if isinstance(target, ResolvedSkillEntry):
            return DisplayValue(text=target.skill_decl.title, kind="title")
        raise CompileError(
            f"Internal compiler error: unsupported addressable target {type(target).__name__}"
        )

    def _display_addressable_title(
        self,
        node: AddressableNode,
        *,
        owner_label: str,
        surface_label: str,
    ) -> str | None:
        target = node.target
        if isinstance(target, model.Agent):
            return None
        if isinstance(target, model.RecordScalar):
            return self._display_record_scalar_title(
                target,
                node=node,
                owner_label=owner_label,
                surface_label=surface_label,
            )
        return self._display_addressable_target_value(
            node,
            owner_label=owner_label,
            surface_label=surface_label,
        ).text

    def _display_record_scalar_title(
        self,
        item: model.RecordScalar,
        *,
        node: AddressableNode,
        owner_label: str,
        surface_label: str,
    ) -> str:
        root_decl = node.root_decl
        if isinstance(root_decl, model.InputDecl) and item.key == "source":
            if not isinstance(item.value, model.NameRef):
                raise CompileError(f"Input source must stay typed: {root_decl.name}")
            return self._resolve_input_source_spec(item.value, unit=node.unit).title

        if isinstance(root_decl, model.OutputDecl) and item.key == "target":
            if not isinstance(item.value, model.NameRef):
                raise CompileError(f"Output target must stay typed: {root_decl.name}")
            return self._resolve_output_target_spec(item.value, unit=node.unit).title

        if isinstance(root_decl, model.OutputDecl) and item.key == "shape":
            return self._display_output_shape(
                item.value,
                unit=node.unit,
                owner_label=root_decl.name,
                surface_label=surface_label,
            )

        return self._display_symbol_value(
            item.value,
            unit=node.unit,
            owner_label=owner_label,
            surface_label=surface_label,
        )

    def _resolve_readable_decl_lookup_unit(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> IndexedUnit:
        if not ref.module_parts or ref.module_parts == unit.module_parts:
            return unit

        target_unit = unit.imported_units.get(ref.module_parts)
        if target_unit is None:
            raise CompileError(f"Missing import module: {'.'.join(ref.module_parts)}")
        return target_unit

    def _find_readable_decl_matches(
        self,
        declaration_name: str,
        *,
        unit: IndexedUnit,
    ) -> tuple[tuple[str, ReadableDecl], ...]:
        matches: list[tuple[str, ReadableDecl]] = []
        for label, registry_name in _READABLE_DECL_REGISTRIES:
            decl = getattr(unit, registry_name).get(declaration_name)
            if decl is not None:
                matches.append((label, decl))
        return tuple(matches)

    def _find_addressable_root_matches(
        self,
        declaration_name: str,
        *,
        unit: IndexedUnit,
    ) -> tuple[tuple[str, AddressableRootDecl], ...]:
        matches: list[tuple[str, AddressableRootDecl]] = []
        for label, registry_name in _ADDRESSABLE_ROOT_REGISTRIES:
            decl = getattr(unit, registry_name).get(declaration_name)
            if decl is not None:
                matches.append((label, decl))
        return tuple(matches)

    def _display_readable_decl(self, decl: ReadableDecl) -> str:
        if isinstance(decl, model.Agent):
            return decl.name
        return decl.title

    def _validate_route_target(self, ref: model.NameRef, *, unit: IndexedUnit) -> None:
        _target_unit, agent = self._resolve_agent_ref(ref, unit=unit)
        if agent.abstract:
            dotted_name = _dotted_ref_name(ref)
            raise CompileError(f"Route target must be a concrete agent: {dotted_name}")

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
                        body=self._compile_section_body(item.items),
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
                        owner_label=owner_label,
                        mode_bindings=mode_bindings,
                    )
                )
            elif isinstance(item, model.WhenStmt):
                rendered.extend(
                    self._render_when_stmt(
                        item,
                        unit=unit,
                        owner_label=owner_label,
                        mode_bindings=mode_bindings,
                    )
                )
            else:
                rendered.extend(
                    self._render_law_stmt_lines(
                        item,
                        unit=unit,
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

    def _flatten_law_items(
        self,
        law_body: model.LawBody,
        *,
        owner_label: str,
    ) -> tuple[model.LawStmt, ...]:
        has_sections = any(isinstance(item, model.LawSection) for item in law_body.items)
        if has_sections:
            if not all(isinstance(item, model.LawSection) for item in law_body.items):
                raise CompileError(
                    f"Law blocks may not mix named sections with bare law statements in {owner_label}"
                )
            flattened: list[model.LawStmt] = []
            for item in law_body.items:
                flattened.extend(item.items)
            return tuple(flattened)
        return tuple(law_body.items)

    def _render_match_stmt(
        self,
        stmt: model.MatchStmt,
        *,
        unit: IndexedUnit,
        owner_label: str,
        mode_bindings: dict[str, model.ModeStmt],
    ) -> list[str]:
        fixed_mode: str | None = None
        if isinstance(stmt.expr, model.ExprRef) and len(stmt.expr.parts) == 1:
            mode_stmt = mode_bindings.get(stmt.expr.parts[0])
            if mode_stmt is not None:
                fixed_mode = self._resolve_constant_enum_member(mode_stmt.expr, unit=unit)

        if fixed_mode is not None:
            for case in stmt.cases:
                if case.head is None or self._render_expr(case.head, unit=unit) == fixed_mode:
                    return self._render_law_stmt_block(
                        case.items,
                        unit=unit,
                        owner_label=owner_label,
                        bullet=False,
                    )
            return []

        labels = [
            self._render_expr(case.head, unit=unit)
            for case in stmt.cases
            if case.head is not None
        ]
        lines = ["Work in exactly one mode:"]
        lines.extend(f"- {label}" for label in labels)
        for case in stmt.cases:
            if case.head is None:
                heading = "Else:"
            else:
                heading = f"If mode is {self._render_expr(case.head, unit=unit)}:"
            lines.extend(["", heading])
            lines.extend(
                self._render_law_stmt_block(
                    case.items,
                    unit=unit,
                    owner_label=owner_label,
                    bullet=True,
                )
            )
        return lines

    def _render_when_stmt(
        self,
        stmt: model.WhenStmt,
        *,
        unit: IndexedUnit,
        owner_label: str,
        mode_bindings: dict[str, model.ModeStmt],
    ) -> list[str]:
        lines = [f"If {self._render_condition_expr(stmt.expr, unit=unit)}:"]
        lines.extend(
            self._render_law_stmt_block(
                stmt.items,
                unit=unit,
                owner_label=owner_label,
                bullet=True,
                mode_bindings=mode_bindings,
            )
        )
        return lines

    def _render_law_stmt_block(
        self,
        items: tuple[model.LawStmt, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        bullet: bool,
        mode_bindings: dict[str, model.ModeStmt] | None = None,
    ) -> list[str]:
        mode_bindings = dict(mode_bindings or {})
        lines: list[str] = []
        for item in items:
            if isinstance(item, model.ModeStmt):
                mode_bindings[item.name] = item
            if isinstance(item, model.MatchStmt):
                rendered = self._render_match_stmt(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    mode_bindings=mode_bindings,
                )
            elif isinstance(item, model.WhenStmt):
                rendered = self._render_when_stmt(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    mode_bindings=mode_bindings,
                )
            else:
                rendered = self._render_law_stmt_lines(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    bullet=bullet,
                )
            if (
                lines
                and rendered
                and not (
                    bullet
                    and lines[-1].startswith("- ")
                    and all(line.startswith("- ") for line in rendered)
                )
            ):
                lines.append("")
            lines.extend(rendered)
        return lines

    def _render_law_stmt_lines(
        self,
        stmt: model.LawStmt,
        *,
        unit: IndexedUnit,
        owner_label: str,
        bullet: bool,
    ) -> list[str]:
        if isinstance(stmt, model.CurrentArtifactStmt):
            text = f"Current artifact: {self._display_law_path_root(stmt.target, unit=unit)}."
        elif isinstance(stmt, model.CurrentNoneStmt):
            text = "There is no current artifact for this turn."
        elif isinstance(stmt, model.MustStmt):
            text = self._render_must_stmt(stmt, unit=unit)
        elif isinstance(stmt, model.OwnOnlyStmt):
            text = f"Own only {self._render_path_set(stmt.target)}."
        elif isinstance(stmt, model.PreserveStmt):
            text = f"Preserve {stmt.kind} {self._render_path_set(stmt.target)}."
        elif isinstance(stmt, model.SupportOnlyStmt):
            text = (
                f"{self._render_path_set_subject(stmt.target, unit=unit)} is comparison-only support."
            )
        elif isinstance(stmt, model.IgnoreStmt):
            text = self._render_ignore_stmt(stmt, unit=unit)
        elif isinstance(stmt, model.ForbidStmt):
            text = f"Do not modify {self._render_path_set(stmt.target)}."
        elif isinstance(stmt, model.InvalidateStmt):
            text = f"{self._display_law_path_root(stmt.target, unit=unit)} is no longer current."
        elif isinstance(stmt, model.StopStmt):
            message = stmt.message or ""
            if message and not message.endswith("."):
                message += "."
            text = "Stop." if stmt.message is None else f"Stop: {message}"
        elif isinstance(stmt, model.LawRouteStmt):
            text = stmt.label if stmt.label.endswith(".") else f"{stmt.label}."
        elif isinstance(stmt, model.ActiveWhenStmt):
            text = f"This pass runs only when {self._render_condition_expr(stmt.expr, unit=unit)}."
        elif isinstance(stmt, model.ModeStmt):
            fixed_mode = self._resolve_constant_enum_member(stmt.expr, unit=unit)
            return [] if fixed_mode is None else [f"Active mode: {fixed_mode}."]
        else:
            return []

        if bullet:
            return [f"- {text}"]
        return [text]

    def _render_must_stmt(self, stmt: model.MustStmt, *, unit: IndexedUnit) -> str:
        if (
            isinstance(stmt.expr, model.ExprBinary)
            and stmt.expr.op == "=="
            and isinstance(stmt.expr.left, model.ExprRef)
        ):
            return f"Must {self._render_expr(stmt.expr.left, unit=unit)} == {self._render_expr(stmt.expr.right, unit=unit)}."
        return f"Must {self._render_expr(stmt.expr, unit=unit)}."

    def _render_ignore_stmt(self, stmt: model.IgnoreStmt, *, unit: IndexedUnit) -> str:
        target = self._render_path_set(stmt.target)
        if stmt.bases == ("rewrite_evidence",):
            prefix = "Ignore"
            if stmt.when_expr is not None:
                prefix = f"When {self._render_condition_expr(stmt.when_expr, unit=unit)}, ignore"
            return f"{prefix} {target} for rewrite evidence."
        if stmt.bases == ("truth",) or not stmt.bases:
            return f"{self._render_path_set_subject(stmt.target, unit=unit)} does not count as truth for this pass."
        return f"Ignore {target} for {', '.join(stmt.bases)}."

    def _render_path_set_subject(
        self,
        target: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
        *,
        unit: IndexedUnit,
    ) -> str:
        target = self._coerce_path_set(target)
        if len(target.paths) == 1 and not target.except_paths:
            path = target.paths[0]
            if not path.wildcard:
                return self._display_law_path_root(path, unit=unit)
        return self._render_path_set(target)

    def _render_path_set(
        self,
        target: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
    ) -> str:
        target = self._coerce_path_set(target)
        parts = [self._render_law_path(path) for path in target.paths]
        rendered = ", ".join(parts)
        if len(parts) > 1:
            rendered = "{" + rendered + "}"
        if target.except_paths:
            rendered += " except " + ", ".join(
                self._render_law_path(path) for path in target.except_paths
            )
        return rendered

    def _render_law_path(self, path: model.LawPath) -> str:
        text = ".".join(path.parts)
        if path.wildcard:
            text += ".*"
        return f"`{text}`"

    def _render_condition_expr(self, expr: model.Expr, *, unit: IndexedUnit) -> str:
        if isinstance(expr, model.ExprRef):
            return self._render_condition_ref(expr, unit=unit)
        if isinstance(expr, model.ExprBinary):
            left = self._render_condition_expr(expr.left, unit=unit)
            right = self._render_condition_expr(expr.right, unit=unit)
            joiner = expr.op
            if expr.op == "==":
                return f"{left} is {right}"
            if expr.op == "!=":
                return f"{left} is not {right}"
            return f"{left} {joiner} {right}"
        if isinstance(expr, model.ExprCall):
            args = ", ".join(self._render_expr(arg, unit=unit) for arg in expr.args)
            return f"{_humanize_key(expr.name).lower()}({args})"
        return self._render_expr(expr, unit=unit)

    def _render_condition_ref(self, ref: model.ExprRef, *, unit: IndexedUnit) -> str:
        parts = ref.parts
        if not parts:
            return ""
        key = parts[-1]
        if key == "missing":
            return f"{self._render_ref_root(parts[:-1], unit=unit)} is missing"
        if key == "unclear":
            return f"{self._render_ref_root(parts[:-1], unit=unit)} is unclear"
        if key.startswith("owes_"):
            return f"{_humanize_key(key.removeprefix('owes_')).lower()} is owed now"
        if key.endswith("_changed"):
            return f"{_humanize_key(key).lower()}"
        if key.endswith("_invalidated"):
            return f"{_humanize_key(key).lower()}"
        if key.endswith("_requested"):
            return f"{_humanize_key(key).lower()}"
        if key.endswith("_used"):
            return f"{_humanize_key(key).lower()}"
        return self._render_expr(ref, unit=unit)

    def _render_ref_root(self, parts: tuple[str, ...], *, unit: IndexedUnit) -> str:
        if not parts:
            return "this turn"
        try:
            root_path = model.LawPath(parts=parts)
            return self._display_law_path_root(root_path, unit=unit).lower()
        except CompileError:
            return _humanize_key(parts[-1]).lower()

    def _render_expr(self, expr: model.Expr, *, unit: IndexedUnit) -> str:
        if isinstance(expr, model.ExprRef):
            return self._render_expr_ref(expr, unit=unit)
        if isinstance(expr, model.ExprBinary):
            return (
                f"{self._render_expr(expr.left, unit=unit)} {expr.op} "
                f"{self._render_expr(expr.right, unit=unit)}"
            )
        if isinstance(expr, model.ExprCall):
            args = ", ".join(self._render_expr(arg, unit=unit) for arg in expr.args)
            return f"{expr.name}({args})"
        if isinstance(expr, str):
            return expr
        if isinstance(expr, bool):
            return "true" if expr else "false"
        return str(expr)

    def _render_expr_ref(self, expr: model.ExprRef, *, unit: IndexedUnit) -> str:
        constant = self._resolve_constant_enum_member(expr, unit=unit)
        if constant is not None:
            return constant
        return ".".join(expr.parts)

    def _resolve_constant_enum_member(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
    ) -> str | None:
        if isinstance(expr, str):
            return expr
        if not isinstance(expr, model.ExprRef) or len(expr.parts) < 2:
            return None
        name_ref = _name_ref_from_dotted_name(".".join(expr.parts[:-1]))
        enum_decl = self._try_resolve_enum_decl(name_ref, unit=unit)
        if enum_decl is None:
            return None
        member = next((member for member in enum_decl.members if member.key == expr.parts[-1]), None)
        if member is None:
            return None
        return member.value

    def _validate_workflow_law(
        self,
        items: tuple[model.LawStmt, ...],
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> None:
        self._validate_law_stmt_tree(
            items,
            unit=unit,
            owner_label=owner_label,
        )
        branches = self._collect_law_leaf_branches(items, unit=unit)
        if not branches:
            branches = (LawBranch(),)

        for branch in branches:
            if len(branch.current_subjects) != 1:
                current_labels = ", ".join(
                    "current none"
                    if isinstance(subject, model.CurrentNoneStmt)
                    else "current artifact"
                    for subject in branch.current_subjects
                )
                if current_labels:
                    raise CompileError(
                        "Active leaf branch resolves more than one current-subject form "
                        f"({current_labels}) in {owner_label}"
                    )
                raise CompileError(
                    f"Active leaf branch must resolve exactly one current-subject form in {owner_label}"
                )
            current = branch.current_subjects[0]
            if isinstance(current, model.CurrentNoneStmt) and branch.owns:
                raise CompileError(
                    f"`current none` cannot appear with owned scope in {owner_label}"
                )
            current_target_key: tuple[tuple[str, ...], str] | None = None
            if isinstance(current, model.CurrentArtifactStmt):
                current_target_key = self._validate_current_artifact_stmt(
                    current,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                )
                for own in branch.owns:
                    self._validate_owned_scope(
                        own,
                        unit=unit,
                        owner_label=owner_label,
                        current_target=current,
                    )
                for invalidate in branch.invalidations:
                    if self._law_paths_match(current.target, invalidate.target):
                        raise CompileError(
                            f"The current artifact cannot be invalidated in the same active branch in {owner_label}"
                        )
            for invalidate in branch.invalidations:
                self._validate_invalidation_stmt(
                    invalidate,
                    unit=unit,
                    agent_contract=agent_contract,
                    owner_label=owner_label,
                )
            for support in branch.supports:
                for ignore in branch.ignores:
                    if "comparison" in ignore.bases and self._path_sets_overlap(
                        support.target,
                        ignore.target,
                    ):
                        raise CompileError(
                            f"support_only and ignore for comparison contradict in {owner_label}"
                        )
            if current_target_key is not None:
                for ignore in branch.ignores:
                    if ("truth" in ignore.bases or not ignore.bases) and self._path_set_contains_path(
                        ignore.target,
                        current.target,
                    ):
                        raise CompileError(
                            f"The current artifact cannot be ignored for truth in {owner_label}"
                        )
            for own in branch.owns:
                own_target = self._coerce_path_set(own.target)
                for forbid in branch.forbids:
                    if self._path_sets_overlap(own_target, forbid.target):
                        raise CompileError(
                            f"Owned and forbidden scope overlap in {owner_label}"
                        )
                for preserve in branch.preserves:
                    if preserve.kind == "exact" and any(
                        self._path_set_contains_path(preserve.target, path)
                        for path in own_target.paths
                    ):
                            raise CompileError(
                                f"Owned scope overlaps exact-preserved scope in {owner_label}"
                            )

    def _validate_law_stmt_tree(
        self,
        items: tuple[model.LawStmt, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        mode_bindings: dict[str, model.ModeStmt] | None = None,
    ) -> None:
        local_mode_bindings = dict(mode_bindings or {})
        for item in items:
            if isinstance(item, model.ModeStmt):
                self._validate_mode_stmt(item, unit=unit, owner_label=owner_label)
                local_mode_bindings[item.name] = item
                continue
            if isinstance(item, model.MatchStmt):
                self._validate_match_stmt(
                    item,
                    unit=unit,
                    owner_label=owner_label,
                    mode_bindings=local_mode_bindings,
                )
                for case in item.cases:
                    self._validate_law_stmt_tree(
                        case.items,
                        unit=unit,
                        owner_label=owner_label,
                        mode_bindings=local_mode_bindings,
                    )
                continue
            if isinstance(item, model.WhenStmt):
                self._validate_law_stmt_tree(
                    item.items,
                    unit=unit,
                    owner_label=owner_label,
                    mode_bindings=local_mode_bindings,
                )
                continue
            if isinstance(item, model.CurrentArtifactStmt):
                self._validate_law_path_root(
                    item.target,
                    unit=unit,
                    owner_label=owner_label,
                    statement_label="current artifact",
                    allowed_kinds=("input", "output"),
                )
                continue
            if isinstance(item, model.InvalidateStmt):
                self._validate_law_path_root(
                    item.target,
                    unit=unit,
                    owner_label=owner_label,
                    statement_label="invalidate",
                    allowed_kinds=("input", "output"),
                )
                continue
            if isinstance(item, (model.OwnOnlyStmt, model.SupportOnlyStmt, model.IgnoreStmt, model.ForbidStmt)):
                self._validate_path_set_roots(
                    item.target,
                    unit=unit,
                    owner_label=owner_label,
                    statement_label=self._law_stmt_name(item),
                    allowed_kinds=("input", "output"),
                )
                continue
            if isinstance(item, model.PreserveStmt):
                if item.kind == "vocabulary":
                    self._validate_path_set_roots(
                        item.target,
                        unit=unit,
                        owner_label=owner_label,
                        statement_label="preserve vocabulary",
                        allowed_kinds=("enum",),
                    )
                else:
                    self._validate_path_set_roots(
                        item.target,
                        unit=unit,
                        owner_label=owner_label,
                        statement_label=f"preserve {item.kind}",
                        allowed_kinds=("input", "output"),
                    )
                continue
            if isinstance(item, model.LawRouteStmt):
                self._validate_route_target(item.target, unit=unit)

    def _validate_mode_stmt(
        self,
        stmt: model.ModeStmt,
        *,
        unit: IndexedUnit,
        owner_label: str,
    ) -> None:
        enum_unit, enum_decl = self._resolve_decl_ref(
            stmt.enum_ref,
            unit=unit,
            registry_name="enums_by_name",
            missing_label="enum declaration",
        )
        fixed_mode = self._resolve_constant_enum_member(stmt.expr, unit=enum_unit)
        if fixed_mode is None:
            return
        if not any(member.value == fixed_mode for member in enum_decl.members):
            raise CompileError(
                f"Mode value is outside enum {enum_decl.name} in {owner_label}: {fixed_mode}"
            )

    def _validate_match_stmt(
        self,
        stmt: model.MatchStmt,
        *,
        unit: IndexedUnit,
        owner_label: str,
        mode_bindings: dict[str, model.ModeStmt],
    ) -> None:
        enum_decl = self._resolve_match_enum_decl(
            stmt.expr,
            unit=unit,
            mode_bindings=mode_bindings,
        )
        if enum_decl is None:
            return

        if any(case.head is None for case in stmt.cases):
            return

        seen_members: set[str] = set()
        for case in stmt.cases:
            if case.head is None:
                continue
            member_value = self._resolve_constant_enum_member(case.head, unit=unit)
            if member_value is None:
                continue
            if not any(member.value == member_value for member in enum_decl.members):
                raise CompileError(
                    f"Match arm is outside enum {enum_decl.name} in {owner_label}: {member_value}"
                )
            seen_members.add(member_value)

        expected_members = {member.value for member in enum_decl.members}
        if seen_members != expected_members:
            raise CompileError(
                f"match on {enum_decl.name} must be exhaustive or include else in {owner_label}"
            )

    def _resolve_match_enum_decl(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        mode_bindings: dict[str, model.ModeStmt],
    ) -> model.EnumDecl | None:
        if not isinstance(expr, model.ExprRef) or len(expr.parts) != 1:
            return None
        mode_stmt = mode_bindings.get(expr.parts[0])
        if mode_stmt is None:
            return None
        enum_unit, enum_decl = self._resolve_decl_ref(
            mode_stmt.enum_ref,
            unit=unit,
            registry_name="enums_by_name",
            missing_label="enum declaration",
        )
        _ = enum_unit
        return enum_decl

    def _collect_law_leaf_branches(
        self,
        items: tuple[model.LawStmt, ...],
        *,
        unit: IndexedUnit,
        branch: LawBranch | None = None,
    ) -> tuple[LawBranch, ...]:
        branches = (branch or LawBranch(),)
        index = 0
        while index < len(items):
            item = items[index]
            if isinstance(item, model.WhenStmt):
                when_items: list[model.WhenStmt] = []
                while index < len(items) and isinstance(items[index], model.WhenStmt):
                    when_items.append(items[index])
                    index += 1
                next_branches: list[LawBranch] = []
                for current_branch in branches:
                    for when_item in when_items:
                        next_branches.extend(
                            self._collect_law_leaf_branches(
                                when_item.items,
                                unit=unit,
                                branch=current_branch,
                            )
                        )
                branches = tuple(next_branches)
                continue
            if isinstance(item, model.WhenStmt):
                next_branches: list[LawBranch] = []
                for current_branch in branches:
                    next_branches.extend(
                        self._collect_law_leaf_branches(
                            item.items,
                            unit=unit,
                            branch=current_branch,
                        )
                    )
                branches = tuple(next_branches)
                continue
            if isinstance(item, model.MatchStmt):
                next_branches = []
                for current_branch in branches:
                    for case in self._select_match_cases(
                        item,
                        unit=unit,
                        branch=current_branch,
                    ):
                        next_branches.extend(
                            self._collect_law_leaf_branches(
                                case.items,
                                unit=unit,
                                branch=current_branch,
                            )
                        )
                branches = tuple(next_branches)
                index += 1
                continue
            branches = tuple(self._branch_with_stmt(current_branch, item) for current_branch in branches)
            index += 1
        return branches

    def _select_match_cases(
        self,
        stmt: model.MatchStmt,
        *,
        unit: IndexedUnit,
        branch: LawBranch,
    ) -> tuple[model.MatchArm, ...]:
        fixed_mode = self._resolve_fixed_match_value(stmt.expr, unit=unit, branch=branch)
        if fixed_mode is None:
            return stmt.cases

        exact_matches = tuple(
            case
            for case in stmt.cases
            if case.head is not None
            and self._resolve_constant_enum_member(case.head, unit=unit) == fixed_mode
        )
        if exact_matches:
            return exact_matches
        else_matches = tuple(case for case in stmt.cases if case.head is None)
        if else_matches:
            return else_matches
        return stmt.cases

    def _resolve_fixed_match_value(
        self,
        expr: model.Expr,
        *,
        unit: IndexedUnit,
        branch: LawBranch,
    ) -> str | None:
        if not isinstance(expr, model.ExprRef) or len(expr.parts) != 1:
            return None
        for mode_stmt in reversed(branch.mode_bindings):
            if mode_stmt.name == expr.parts[0]:
                return self._resolve_constant_enum_member(mode_stmt.expr, unit=unit)
        return None

    def _branch_with_stmt(self, branch: LawBranch, stmt: model.LawStmt) -> LawBranch:
        if isinstance(stmt, model.ActiveWhenStmt):
            return replace(branch, activation_exprs=(*branch.activation_exprs, stmt.expr))
        if isinstance(stmt, model.ModeStmt):
            return replace(branch, mode_bindings=(*branch.mode_bindings, stmt))
        if isinstance(stmt, (model.CurrentArtifactStmt, model.CurrentNoneStmt)):
            return replace(branch, current_subjects=(*branch.current_subjects, stmt))
        if isinstance(stmt, model.MustStmt):
            return replace(branch, musts=(*branch.musts, stmt))
        if isinstance(stmt, model.OwnOnlyStmt):
            return replace(branch, owns=(*branch.owns, stmt))
        if isinstance(stmt, model.PreserveStmt):
            return replace(branch, preserves=(*branch.preserves, stmt))
        if isinstance(stmt, model.SupportOnlyStmt):
            return replace(branch, supports=(*branch.supports, stmt))
        if isinstance(stmt, model.IgnoreStmt):
            return replace(branch, ignores=(*branch.ignores, stmt))
        if isinstance(stmt, model.ForbidStmt):
            return replace(branch, forbids=(*branch.forbids, stmt))
        if isinstance(stmt, model.InvalidateStmt):
            return replace(branch, invalidations=(*branch.invalidations, stmt))
        if isinstance(stmt, model.StopStmt):
            return replace(branch, stops=(*branch.stops, stmt))
        if isinstance(stmt, model.LawRouteStmt):
            return replace(branch, routes=(*branch.routes, stmt))
        return branch

    def _validate_current_artifact_stmt(
        self,
        stmt: model.CurrentArtifactStmt,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> tuple[tuple[str, ...], str]:
        target = self._validate_law_path_root(
            stmt.target,
            unit=unit,
            owner_label=owner_label,
            statement_label="current artifact",
            allowed_kinds=("input", "output"),
        )
        if target.remainder or target.wildcard:
            raise CompileError(
                f"current artifact must stay rooted at one input or output artifact in {owner_label}: "
                f"{'.'.join(stmt.target.parts)}"
            )

        carrier = self._validate_carrier_path(
            stmt.carrier,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label="current artifact",
        )
        if isinstance(target.decl, model.OutputDecl):
            target_key = (target.unit.module_parts, target.decl.name)
            if target_key not in agent_contract.outputs:
                raise CompileError(
                    f"current artifact output must be emitted by the concrete turn in {owner_label}: "
                    f"{target.decl.name}"
                )
        return (target.unit.module_parts, target.decl.name)

    def _validate_invalidation_stmt(
        self,
        stmt: model.InvalidateStmt,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
    ) -> None:
        target = self._validate_law_path_root(
            stmt.target,
            unit=unit,
            owner_label=owner_label,
            statement_label="invalidate",
            allowed_kinds=("input", "output"),
        )
        if target.remainder or target.wildcard:
            raise CompileError(
                f"invalidate must name one full input or output artifact in {owner_label}: "
                f"{'.'.join(stmt.target.parts)}"
            )
        self._validate_carrier_path(
            stmt.carrier,
            unit=unit,
            agent_contract=agent_contract,
            owner_label=owner_label,
            statement_label="invalidate",
        )

    def _validate_carrier_path(
        self,
        carrier: model.LawPath,
        *,
        unit: IndexedUnit,
        agent_contract: AgentContract,
        owner_label: str,
        statement_label: str,
    ) -> ResolvedLawPath:
        resolved = self._validate_law_path_root(
            carrier,
            unit=unit,
            owner_label=owner_label,
            statement_label=f"{statement_label} carrier",
            allowed_kinds=("output",),
        )
        if not isinstance(resolved.decl, model.OutputDecl):
            raise CompileError(
                f"{statement_label} via carrier must stay rooted in an emitted output in {owner_label}"
            )
        if not resolved.remainder or resolved.wildcard:
            raise CompileError(
                f"{statement_label} requires an explicit `via` field on an emitted output in {owner_label}"
            )

        output_key = (resolved.unit.module_parts, resolved.decl.name)
        if output_key not in agent_contract.outputs:
            raise CompileError(
                f"{statement_label} carrier output must be emitted by the concrete turn in {owner_label}: "
                f"{resolved.decl.name}"
            )

        self._resolve_output_field_node(
            resolved.decl,
            path=resolved.remainder,
            unit=resolved.unit,
            owner_label=owner_label,
            surface_label=f"{statement_label} via",
        )
        if not any(item.path == resolved.remainder for item in resolved.decl.trust_surface):
            raise CompileError(
                f"{statement_label} carrier field must be listed in trust_surface in {owner_label}: "
                f"{'.'.join(resolved.remainder)}"
            )
        return resolved

    def _validate_owned_scope(
        self,
        stmt: model.OwnOnlyStmt,
        *,
        unit: IndexedUnit,
        owner_label: str,
        current_target: model.CurrentArtifactStmt,
    ) -> None:
        target = self._coerce_path_set(stmt.target)
        current_root = self._validate_law_path_root(
            current_target.target,
            unit=unit,
            owner_label=owner_label,
            statement_label="current artifact",
            allowed_kinds=("input", "output"),
        )
        for path in target.paths:
            resolved = self._validate_law_path_root(
                path,
                unit=unit,
                owner_label=owner_label,
                statement_label="own only",
                allowed_kinds=("input", "output"),
            )
            if (
                resolved.unit.module_parts != current_root.unit.module_parts
                or resolved.decl.name != current_root.decl.name
            ):
                raise CompileError(
                    f"own only must stay rooted in the current artifact in {owner_label}: "
                    f"{'.'.join(path.parts)}"
                )

    def _validate_path_set_roots(
        self,
        target: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
        *,
        unit: IndexedUnit,
        owner_label: str,
        statement_label: str,
        allowed_kinds: tuple[str, ...],
    ) -> None:
        target = self._coerce_path_set(target)
        for path in (*target.paths, *target.except_paths):
            self._validate_law_path_root(
                path,
                unit=unit,
                owner_label=owner_label,
                statement_label=statement_label,
                allowed_kinds=allowed_kinds,
            )

    def _validate_law_path_root(
        self,
        path: model.LawPath,
        *,
        unit: IndexedUnit,
        owner_label: str,
        statement_label: str,
        allowed_kinds: tuple[str, ...],
    ) -> ResolvedLawPath:
        resolved = self._resolve_law_path(
            path,
            unit=unit,
            owner_label=owner_label,
            statement_label=statement_label,
            allowed_kinds=allowed_kinds,
        )
        if isinstance(resolved.decl, model.EnumDecl) and resolved.remainder:
            raise CompileError(
                f"{statement_label} enum targets must not descend through fields in {owner_label}: "
                f"{'.'.join(path.parts)}"
            )
        return resolved

    def _resolve_law_path(
        self,
        path: model.LawPath,
        *,
        unit: IndexedUnit,
        owner_label: str,
        statement_label: str,
        allowed_kinds: tuple[str, ...],
    ) -> ResolvedLawPath:
        matches: list[ResolvedLawPath] = []
        for split_index in range(1, len(path.parts) + 1):
            ref = model.NameRef(
                module_parts=path.parts[: split_index - 1],
                declaration_name=path.parts[split_index - 1],
            )
            try:
                lookup_unit = self._resolve_readable_decl_lookup_unit(ref, unit=unit)
            except CompileError:
                continue
            remainder = path.parts[split_index:]
            if "input" in allowed_kinds:
                input_decl = lookup_unit.inputs_by_name.get(ref.declaration_name)
                if input_decl is not None:
                    matches.append(
                        ResolvedLawPath(
                            unit=lookup_unit,
                            decl=input_decl,
                            remainder=remainder,
                            wildcard=path.wildcard,
                        )
                    )
            if "output" in allowed_kinds:
                output_decl = lookup_unit.outputs_by_name.get(ref.declaration_name)
                if output_decl is not None:
                    matches.append(
                        ResolvedLawPath(
                            unit=lookup_unit,
                            decl=output_decl,
                            remainder=remainder,
                            wildcard=path.wildcard,
                        )
                    )
            if "enum" in allowed_kinds:
                enum_decl = lookup_unit.enums_by_name.get(ref.declaration_name)
                if enum_decl is not None:
                    matches.append(
                        ResolvedLawPath(
                            unit=lookup_unit,
                            decl=enum_decl,
                            remainder=remainder,
                            wildcard=path.wildcard,
                        )
                    )

        unique_matches: list[ResolvedLawPath] = []
        seen: set[tuple[tuple[str, ...], str, tuple[str, ...], str]] = set()
        for match in matches:
            key = (
                match.unit.module_parts,
                match.decl.name,
                match.remainder,
                type(match.decl).__name__,
            )
            if key in seen:
                continue
            seen.add(key)
            unique_matches.append(match)

        if len(unique_matches) == 1:
            return unique_matches[0]
        if len(unique_matches) > 1:
            choices = ", ".join(
                _dotted_decl_name(match.unit.module_parts, match.decl.name)
                for match in unique_matches
            )
            raise CompileError(
                f"Ambiguous {statement_label} path in {owner_label}: "
                f"{'.'.join(path.parts)} matches {choices}"
            )

        allowed_text = " or ".join(allowed_kinds)
        raise CompileError(
            f"{statement_label} target must resolve to a declared {allowed_text} in {owner_label}: "
            f"{'.'.join(path.parts)}"
        )

    def _resolve_output_field_node(
        self,
        decl: model.OutputDecl,
        *,
        path: tuple[str, ...],
        unit: IndexedUnit,
        owner_label: str,
        surface_label: str,
    ) -> AddressableNode:
        current_node = AddressableNode(unit=unit, root_decl=decl, target=decl)
        if not path:
            return current_node
        for segment in path:
            children = self._get_addressable_children(current_node)
            if children is None or segment not in children:
                raise CompileError(
                    f"Unknown output field on {surface_label} in {owner_label}: "
                    f"{decl.name}.{'.'.join(path)}"
                )
            current_node = children[segment]
        return current_node

    def _law_paths_match(self, left: model.LawPath, right: model.LawPath) -> bool:
        return self._law_path_contains_path(left, right) or self._law_path_contains_path(right, left)

    def _law_path_contains_path(self, container: model.LawPath, path: model.LawPath) -> bool:
        if len(container.parts) > len(path.parts):
            return False
        if path.parts[: len(container.parts)] != container.parts:
            return False
        if len(container.parts) == len(path.parts):
            return container.wildcard or not path.wildcard or container.wildcard == path.wildcard
        return container.wildcard

    def _path_set_contains_path(
        self,
        target: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
        path: model.LawPath,
    ) -> bool:
        target = self._coerce_path_set(target)
        if not any(self._law_path_contains_path(base, path) for base in target.paths):
            return False
        if any(self._law_path_contains_path(excluded, path) for excluded in target.except_paths):
            return False
        return True

    def _path_sets_overlap(
        self,
        left: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
        right: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
    ) -> bool:
        left = self._coerce_path_set(left)
        right = self._coerce_path_set(right)
        for path in left.paths:
            if self._path_set_contains_path(right, path):
                return True
        for path in right.paths:
            if self._path_set_contains_path(left, path):
                return True
        return False

    def _display_law_path_root(
        self,
        path: model.LawPath,
        *,
        unit: IndexedUnit,
    ) -> str:
        try:
            resolved = self._resolve_law_path(
                path,
                unit=unit,
                owner_label="workflow law",
                statement_label="law path",
                allowed_kinds=("input", "output", "enum"),
            )
        except CompileError:
            return ".".join(path.parts)
        title = self._display_readable_decl(resolved.decl)
        if not resolved.remainder:
            return title
        return f"{title}.{'.'.join(resolved.remainder)}"

    def _coerce_path_set(
        self,
        target: model.LawPathSet | model.LawPath | tuple[model.LawPath, ...],
    ) -> model.LawPathSet:
        if isinstance(target, model.LawPathSet):
            return target
        if isinstance(target, tuple):
            return model.LawPathSet(paths=target)
        return model.LawPathSet(paths=(target,))

    def _law_stmt_name(self, stmt: model.LawStmt) -> str:
        if isinstance(stmt, model.OwnOnlyStmt):
            return "own only"
        if isinstance(stmt, model.SupportOnlyStmt):
            return "support_only"
        if isinstance(stmt, model.IgnoreStmt):
            return "ignore"
        if isinstance(stmt, model.ForbidStmt):
            return "forbid"
        return type(stmt).__name__

    def _compile_section_body(
        self,
        items: tuple[ResolvedSectionBodyItem, ...],
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
                        body=self._compile_section_body(item.items),
                    )
                )
            elif isinstance(item, ResolvedRouteLine):
                body.append(f"{item.label} -> {item.target_name}")
            else:
                body.append(f"- {item.label}")

            previous_kind = current_kind

        return tuple(body)

    def _split_record_items(
        self,
        items: tuple[model.RecordItem, ...],
        *,
        scalar_keys: set[str] | None = None,
        section_keys: set[str] | None = None,
        owner_label: str,
    ) -> tuple[dict[str, model.RecordScalar], dict[str, model.RecordSection], tuple[model.RecordItem, ...]]:
        scalar_keys = scalar_keys or set()
        section_keys = section_keys or set()
        scalar_items: dict[str, model.RecordScalar] = {}
        section_items: dict[str, model.RecordSection] = {}
        extras: list[model.RecordItem] = []

        for item in items:
            if isinstance(item, model.RecordScalar) and item.key in scalar_keys:
                if item.key in scalar_items:
                    raise CompileError(f"Duplicate record key in {owner_label}: {item.key}")
                scalar_items[item.key] = item
                continue
            if isinstance(item, model.RecordSection) and item.key in section_keys:
                if item.key in section_items:
                    raise CompileError(f"Duplicate record key in {owner_label}: {item.key}")
                section_items[item.key] = item
                continue
            extras.append(item)

        return scalar_items, section_items, tuple(extras)

    def _resolve_workflow_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.WorkflowDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="workflows_by_name",
            missing_label="workflow declaration",
        )

    def _resolve_skills_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.SkillsDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="skills_blocks_by_name",
            missing_label="skills declaration",
        )

    def _resolve_inputs_block_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.InputsDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="inputs_blocks_by_name",
            missing_label="inputs block",
        )

    def _resolve_outputs_block_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputsDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="outputs_blocks_by_name",
            missing_label="outputs block",
        )

    def _resolve_parent_workflow_decl(
        self,
        workflow_decl: model.WorkflowDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.WorkflowDecl]:
        parent_ref = workflow_decl.parent_ref
        if parent_ref is None:
            raise CompileError(
                f"Internal compiler error: workflow has no parent ref: {workflow_decl.name}"
            )
        if not parent_ref.module_parts:
            parent_decl = unit.workflows_by_name.get(parent_ref.declaration_name)
            if parent_decl is None:
                raise CompileError(
                    f"Missing parent workflow for {workflow_decl.name}: {parent_ref.declaration_name}"
                )
            return unit, parent_decl
        return self._resolve_workflow_ref(parent_ref, unit=unit)

    def _resolve_parent_skills_decl(
        self,
        skills_decl: model.SkillsDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.SkillsDecl]:
        parent_ref = skills_decl.parent_ref
        if parent_ref is None:
            raise CompileError(
                f"Internal compiler error: skills has no parent ref: {skills_decl.name}"
            )
        if not parent_ref.module_parts:
            parent_decl = unit.skills_blocks_by_name.get(parent_ref.declaration_name)
            if parent_decl is None:
                raise CompileError(
                    f"Missing parent skills for {skills_decl.name}: {parent_ref.declaration_name}"
                )
            return unit, parent_decl
        return self._resolve_skills_ref(parent_ref, unit=unit)

    def _resolve_parent_inputs_decl(
        self,
        inputs_decl: model.InputsDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.InputsDecl]:
        parent_ref = inputs_decl.parent_ref
        if parent_ref is None:
            raise CompileError(
                f"Internal compiler error: inputs block has no parent ref: {inputs_decl.name}"
            )
        if not parent_ref.module_parts:
            parent_decl = unit.inputs_blocks_by_name.get(parent_ref.declaration_name)
            if parent_decl is None:
                raise CompileError(
                    f"Missing parent inputs block for {inputs_decl.name}: {parent_ref.declaration_name}"
                )
            return unit, parent_decl
        return self._resolve_inputs_block_ref(parent_ref, unit=unit)

    def _resolve_parent_outputs_decl(
        self,
        outputs_decl: model.OutputsDecl,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.OutputsDecl]:
        parent_ref = outputs_decl.parent_ref
        if parent_ref is None:
            raise CompileError(
                f"Internal compiler error: outputs block has no parent ref: {outputs_decl.name}"
            )
        if not parent_ref.module_parts:
            parent_decl = unit.outputs_blocks_by_name.get(parent_ref.declaration_name)
            if parent_decl is None:
                raise CompileError(
                    f"Missing parent outputs block for {outputs_decl.name}: {parent_ref.declaration_name}"
                )
            return unit, parent_decl
        return self._resolve_outputs_block_ref(parent_ref, unit=unit)

    def _resolve_input_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.InputDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="inputs_by_name",
            missing_label="input declaration",
        )

    def _resolve_input_source_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.InputSourceDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="input_sources_by_name",
            missing_label="input source declaration",
        )

    def _resolve_output_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="outputs_by_name",
            missing_label="output declaration",
        )

    def _resolve_output_target_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputTargetDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="output_targets_by_name",
            missing_label="output target declaration",
        )

    def _resolve_output_shape_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.OutputShapeDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="output_shapes_by_name",
            missing_label="output shape declaration",
        )

    def _resolve_skill_decl(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.SkillDecl]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="skills_by_name",
            missing_label="skill declaration",
        )

    def _resolve_agent_ref(
        self, ref: model.NameRef, *, unit: IndexedUnit
    ) -> tuple[IndexedUnit, model.Agent]:
        return self._resolve_decl_ref(
            ref,
            unit=unit,
            registry_name="agents_by_name",
            missing_label="agent declaration",
        )

    def _resolve_parent_agent_decl(
        self,
        agent: model.Agent,
        *,
        unit: IndexedUnit,
    ) -> tuple[IndexedUnit, model.Agent]:
        parent_ref = agent.parent_ref
        if parent_ref is None:
            raise CompileError(f"Internal compiler error: agent has no parent ref: {agent.name}")
        if not parent_ref.module_parts:
            parent_agent = unit.agents_by_name.get(parent_ref.declaration_name)
            if parent_agent is None:
                raise CompileError(
                    f"Missing parent agent for {agent.name}: {parent_ref.declaration_name}"
                )
            return unit, parent_agent
        return self._resolve_agent_ref(parent_ref, unit=unit)

    def _resolve_decl_ref(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        registry_name: str,
        missing_label: str,
    ):
        if not ref.module_parts:
            registry = getattr(unit, registry_name)
            decl = registry.get(ref.declaration_name)
            if decl is None:
                raise CompileError(f"Missing local {missing_label}: {ref.declaration_name}")
            return unit, decl

        if ref.module_parts == unit.module_parts:
            registry = getattr(unit, registry_name)
            decl = registry.get(ref.declaration_name)
            if decl is None:
                dotted_name = _dotted_ref_name(ref)
                raise CompileError(f"Missing imported declaration: {dotted_name}")
            return unit, decl

        target_unit = unit.imported_units.get(ref.module_parts)
        if target_unit is None:
            raise CompileError(f"Missing import module: {'.'.join(ref.module_parts)}")

        registry = getattr(target_unit, registry_name)
        decl = registry.get(ref.declaration_name)
        if decl is None:
            dotted_name = _dotted_ref_name(ref)
            raise CompileError(f"Missing imported declaration: {dotted_name}")
        return target_unit, decl

    def _ref_exists_in_registry(
        self,
        ref: model.NameRef,
        *,
        unit: IndexedUnit,
        registry_name: str,
    ) -> bool:
        if not ref.module_parts or ref.module_parts == unit.module_parts:
            registry = getattr(unit, registry_name)
            return registry.get(ref.declaration_name) is not None

        target_unit = unit.imported_units.get(ref.module_parts)
        if target_unit is None:
            return False

        registry = getattr(target_unit, registry_name)
        return registry.get(ref.declaration_name) is not None

    def _index_unit(
        self, prompt_file: model.PromptFile, *, module_parts: tuple[str, ...]
    ) -> IndexedUnit:
        imports: list[model.ImportDecl] = []
        workflows_by_name: dict[str, model.WorkflowDecl] = {}
        skills_blocks_by_name: dict[str, model.SkillsDecl] = {}
        inputs_blocks_by_name: dict[str, model.InputsDecl] = {}
        inputs_by_name: dict[str, model.InputDecl] = {}
        input_sources_by_name: dict[str, model.InputSourceDecl] = {}
        outputs_blocks_by_name: dict[str, model.OutputsDecl] = {}
        outputs_by_name: dict[str, model.OutputDecl] = {}
        output_targets_by_name: dict[str, model.OutputTargetDecl] = {}
        output_shapes_by_name: dict[str, model.OutputShapeDecl] = {}
        json_schemas_by_name: dict[str, model.JsonSchemaDecl] = {}
        skills_by_name: dict[str, model.SkillDecl] = {}
        agents_by_name: dict[str, model.Agent] = {}
        enums_by_name: dict[str, model.EnumDecl] = {}

        for declaration in prompt_file.declarations:
            if isinstance(declaration, model.ImportDecl):
                imports.append(declaration)
                continue
            if isinstance(declaration, model.WorkflowDecl):
                self._register_decl(workflows_by_name, declaration.name, module_parts)
                workflows_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.SkillsDecl):
                self._register_decl(skills_blocks_by_name, declaration.name, module_parts)
                skills_blocks_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.InputsDecl):
                self._register_decl(inputs_blocks_by_name, declaration.name, module_parts)
                inputs_blocks_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.InputDecl):
                self._register_decl(inputs_by_name, declaration.name, module_parts)
                inputs_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.InputSourceDecl):
                self._register_decl(input_sources_by_name, declaration.name, module_parts)
                input_sources_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.OutputsDecl):
                self._register_decl(outputs_blocks_by_name, declaration.name, module_parts)
                outputs_blocks_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.OutputDecl):
                self._register_decl(outputs_by_name, declaration.name, module_parts)
                outputs_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.OutputTargetDecl):
                self._register_decl(output_targets_by_name, declaration.name, module_parts)
                output_targets_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.OutputShapeDecl):
                self._register_decl(output_shapes_by_name, declaration.name, module_parts)
                output_shapes_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.JsonSchemaDecl):
                self._register_decl(json_schemas_by_name, declaration.name, module_parts)
                json_schemas_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.SkillDecl):
                self._register_decl(skills_by_name, declaration.name, module_parts)
                skills_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.EnumDecl):
                self._register_decl(enums_by_name, declaration.name, module_parts)
                self._validate_enum_decl(
                    declaration,
                    owner_label=f"enum {_dotted_decl_name(module_parts, declaration.name)}",
                )
                enums_by_name[declaration.name] = declaration
                continue
            if isinstance(declaration, model.Agent):
                self._register_decl(agents_by_name, declaration.name, module_parts)
                agents_by_name[declaration.name] = declaration
                continue
            raise CompileError(f"Unsupported declaration type: {type(declaration).__name__}")

        imported_units: dict[tuple[str, ...], IndexedUnit] = {}
        for import_decl in imports:
            resolved_module_parts = _resolve_import_path(import_decl.path, module_parts=module_parts)
            try:
                imported_units[resolved_module_parts] = self._load_module(resolved_module_parts)
            except DoctrineError as exc:
                importer_path = prompt_file.source_path
                raise exc.prepend_trace(
                    f"resolve import `{'.'.join(resolved_module_parts)}`",
                    location=_path_location(importer_path),
                )

        return IndexedUnit(
            module_parts=module_parts,
            prompt_file=prompt_file,
            imports=tuple(imports),
            workflows_by_name=workflows_by_name,
            inputs_blocks_by_name=inputs_blocks_by_name,
            inputs_by_name=inputs_by_name,
            input_sources_by_name=input_sources_by_name,
            outputs_blocks_by_name=outputs_blocks_by_name,
            outputs_by_name=outputs_by_name,
            output_targets_by_name=output_targets_by_name,
            output_shapes_by_name=output_shapes_by_name,
            json_schemas_by_name=json_schemas_by_name,
            skills_by_name=skills_by_name,
            skills_blocks_by_name=skills_blocks_by_name,
            enums_by_name=enums_by_name,
            agents_by_name=agents_by_name,
            imported_units=imported_units,
        )

    def _register_decl(
        self,
        registry: dict[str, object],
        name: str,
        module_parts: tuple[str, ...],
    ) -> None:
        if name in registry:
            dotted_name = ".".join((*module_parts, name)) or name
            raise CompileError(f"Duplicate declaration name: {dotted_name}")

    def _validate_enum_decl(self, decl: model.EnumDecl, *, owner_label: str) -> None:
        seen_keys: set[str] = set()
        for member in decl.members:
            if member.key in seen_keys:
                raise CompileError(f"Duplicate enum member key in {owner_label}: {member.key}")
            seen_keys.add(member.key)

    def _load_module(self, module_parts: tuple[str, ...]) -> IndexedUnit:
        cached = self._module_cache.get(module_parts)
        if cached is not None:
            return cached

        if module_parts in self._loading_modules:
            raise CompileError(f"Cyclic import module: {'.'.join(module_parts)}")

        module_path = self.prompt_root.joinpath(*module_parts).with_suffix(".prompt")
        if not module_path.is_file():
            raise CompileError(f"Missing import module: {'.'.join(module_parts)}")

        self._loading_modules.add(module_parts)
        try:
            try:
                prompt_file = parse_file(module_path)
                indexed = self._index_unit(prompt_file, module_parts=module_parts)
            except DoctrineError as exc:
                raise exc.prepend_trace(
                    f"load import module `{'.'.join(module_parts)}`",
                    location=_path_location(module_path),
                ).ensure_location(path=module_path)
            self._module_cache[module_parts] = indexed
            return indexed
        finally:
            self._loading_modules.remove(module_parts)


def compile_prompt(prompt_file: model.PromptFile, agent_name: str) -> CompiledAgent:
    try:
        return CompilationContext(prompt_file).compile_agent(agent_name)
    except DoctrineError as exc:
        raise exc.prepend_trace(
            f"compile agent `{agent_name}`",
            location=_path_location(prompt_file.source_path),
        ).ensure_location(path=prompt_file.source_path)


def _resolve_prompt_root(source_path: Path | None) -> Path:
    if source_path is None:
        raise CompileError("Prompt source path is required for compilation.")

    resolved = source_path.resolve()
    for candidate in [resolved.parent, *resolved.parents]:
        if candidate.name == "prompts":
            return candidate

    raise CompileError(f"Could not resolve prompts/ root for {resolved}.")


def _resolve_import_path(
    import_path: model.ImportPath, *, module_parts: tuple[str, ...]
) -> tuple[str, ...]:
    if import_path.level == 0:
        return import_path.module_parts

    current_package_parts = module_parts[:-1] if module_parts else ()
    parent_walk = import_path.level - 1
    package_parts = (
        current_package_parts[:-parent_walk] if parent_walk else current_package_parts
    )
    if parent_walk > len(current_package_parts):
        dotted_import = "." * import_path.level + ".".join(import_path.module_parts)
        raise CompileError(f"Relative import walks above prompts root: {dotted_import}")

    return (*package_parts, *import_path.module_parts)


def _dotted_decl_name(module_parts: tuple[str, ...], name: str) -> str:
    return ".".join((*module_parts, name)) if module_parts else name


def _dotted_ref_name(ref: model.NameRef) -> str:
    return ".".join((*ref.module_parts, ref.declaration_name))


def _name_ref_from_dotted_name(dotted_name: str) -> model.NameRef:
    parts = tuple(dotted_name.split("."))
    return model.NameRef(module_parts=parts[:-1], declaration_name=parts[-1])


def _path_location(path: Path | None) -> DiagnosticLocation | None:
    if path is None:
        return None
    return DiagnosticLocation(path=path.resolve())


def _humanize_key(value: str) -> str:
    value = value.replace("_", " ")
    value = _CAMEL_BOUNDARY_RE.sub(" ", value)
    words = value.split()
    return " ".join(word if word.isupper() else word.capitalize() for word in words)


def _display_addressable_ref(ref: model.AddressableRef) -> str:
    root = _dotted_ref_name(ref.root)
    if not ref.path:
        return root
    return f"{root}:{'.'.join(ref.path)}"
````

## File: doctrine/model.py
````python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias


@dataclass(slots=True, frozen=True)
class EmphasizedLine:
    kind: str
    text: str


ProseLine: TypeAlias = str | EmphasizedLine


@dataclass(slots=True, frozen=True)
class RoleScalar:
    text: str


@dataclass(slots=True, frozen=True)
class RoleBlock:
    title: str
    lines: tuple[ProseLine, ...]


@dataclass(slots=True, frozen=True)
class ImportPath:
    level: int
    module_parts: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class ImportDecl:
    path: ImportPath


@dataclass(slots=True, frozen=True)
class NameRef:
    module_parts: tuple[str, ...]
    declaration_name: str


@dataclass(slots=True, frozen=True)
class ExprRef:
    parts: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class ExprCall:
    name: str
    args: tuple["Expr", ...]


@dataclass(slots=True, frozen=True)
class ExprBinary:
    op: str
    left: "Expr"
    right: "Expr"


Expr: TypeAlias = ExprRef | ExprCall | ExprBinary | str | int | bool


@dataclass(slots=True, frozen=True)
class LawPath:
    parts: tuple[str, ...]
    wildcard: bool = False


@dataclass(slots=True, frozen=True)
class LawPathSet:
    paths: tuple[LawPath, ...]
    except_paths: tuple[LawPath, ...] = ()


@dataclass(slots=True, frozen=True)
class TrustSurfaceItem:
    path: tuple[str, ...]
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class ActiveWhenStmt:
    expr: Expr


@dataclass(slots=True, frozen=True)
class ModeStmt:
    name: str
    expr: Expr
    enum_ref: NameRef


@dataclass(slots=True, frozen=True)
class MustStmt:
    expr: Expr


@dataclass(slots=True, frozen=True)
class CurrentArtifactStmt:
    target: LawPath
    carrier: LawPath


@dataclass(slots=True, frozen=True)
class CurrentNoneStmt:
    pass


@dataclass(slots=True, frozen=True)
class OwnOnlyStmt:
    target: LawPathSet
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class PreserveStmt:
    kind: str
    target: LawPathSet
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class SupportOnlyStmt:
    target: LawPathSet
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class IgnoreStmt:
    target: LawPathSet
    bases: tuple[str, ...]
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class InvalidateStmt:
    target: LawPath
    carrier: LawPath
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class ForbidStmt:
    target: LawPathSet
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class WhenStmt:
    expr: Expr
    items: tuple["LawStmt", ...]


@dataclass(slots=True, frozen=True)
class MatchArm:
    head: Expr | None
    items: tuple["LawStmt", ...]


@dataclass(slots=True, frozen=True)
class MatchStmt:
    expr: Expr
    cases: tuple[MatchArm, ...]


@dataclass(slots=True, frozen=True)
class StopStmt:
    message: str | None = None
    when_expr: Expr | None = None


@dataclass(slots=True, frozen=True)
class LawRouteStmt:
    label: str
    target: NameRef
    when_expr: Expr | None = None


LawStmt: TypeAlias = (
    ActiveWhenStmt
    | ModeStmt
    | MustStmt
    | CurrentArtifactStmt
    | CurrentNoneStmt
    | OwnOnlyStmt
    | PreserveStmt
    | SupportOnlyStmt
    | IgnoreStmt
    | InvalidateStmt
    | ForbidStmt
    | WhenStmt
    | MatchStmt
    | StopStmt
    | LawRouteStmt
)


@dataclass(slots=True, frozen=True)
class LawSection:
    key: str
    items: tuple[LawStmt, ...]


@dataclass(slots=True, frozen=True)
class LawInherit:
    key: str


@dataclass(slots=True, frozen=True)
class LawOverrideSection:
    key: str
    items: tuple[LawStmt, ...]


LawTopLevelItem: TypeAlias = LawStmt | LawSection | LawInherit | LawOverrideSection


@dataclass(slots=True, frozen=True)
class LawBody:
    items: tuple[LawTopLevelItem, ...]


@dataclass(slots=True, frozen=True)
class AddressableRef:
    root: NameRef
    path: tuple[str, ...] = ()


@dataclass(slots=True, frozen=True)
class RouteLine:
    label: str
    target: NameRef


@dataclass(slots=True, frozen=True)
class SectionBodyRef:
    ref: AddressableRef


SectionBodyItem: TypeAlias = ProseLine | RouteLine | SectionBodyRef | "LocalSection"


@dataclass(slots=True, frozen=True)
class LocalSection:
    key: str
    title: str
    items: tuple[SectionBodyItem, ...]


@dataclass(slots=True, frozen=True)
class WorkflowUse:
    key: str
    target: NameRef


@dataclass(slots=True, frozen=True)
class InheritItem:
    key: str


@dataclass(slots=True, frozen=True)
class OverrideSection:
    key: str
    title: str | None
    items: tuple[SectionBodyItem, ...]


@dataclass(slots=True, frozen=True)
class OverrideUse:
    key: str
    target: NameRef


RecordScalarValue: TypeAlias = str | NameRef | AddressableRef


@dataclass(slots=True, frozen=True)
class RecordScalar:
    key: str
    value: RecordScalarValue
    body: tuple["RecordItem", ...] | None = None


@dataclass(slots=True, frozen=True)
class RecordSection:
    key: str
    title: str
    items: tuple["RecordItem", ...]


@dataclass(slots=True, frozen=True)
class RecordRef:
    ref: NameRef
    body: tuple["RecordItem", ...] | None = None


RecordItem: TypeAlias = ProseLine | RecordScalar | RecordSection | RecordRef


@dataclass(slots=True, frozen=True)
class SkillEntry:
    key: str
    target: NameRef
    items: tuple[RecordItem, ...] = ()


SkillsSectionItem: TypeAlias = ProseLine | SkillEntry


@dataclass(slots=True, frozen=True)
class SkillsSection:
    key: str
    title: str
    items: tuple[SkillsSectionItem, ...]


@dataclass(slots=True, frozen=True)
class OverrideSkillEntry:
    key: str
    target: NameRef
    items: tuple[RecordItem, ...] = ()


@dataclass(slots=True, frozen=True)
class OverrideSkillsSection:
    key: str
    title: str | None
    items: tuple[SkillsSectionItem, ...]


SkillsItem: TypeAlias = (
    SkillsSection | SkillEntry | InheritItem | OverrideSkillsSection | OverrideSkillEntry
)


@dataclass(slots=True, frozen=True)
class SkillsBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[SkillsItem, ...]


SkillsValue: TypeAlias = SkillsBody | NameRef


@dataclass(slots=True, frozen=True)
class OverrideIoSection:
    key: str
    title: str | None
    items: tuple[RecordItem, ...]


IoItem: TypeAlias = RecordSection | RecordRef | InheritItem | OverrideIoSection


@dataclass(slots=True, frozen=True)
class IoBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[IoItem, ...]


IoFieldValue: TypeAlias = tuple[RecordItem, ...] | NameRef | IoBody


@dataclass(slots=True, frozen=True)
class WorkflowSkillsItem:
    key: str
    value: SkillsValue


@dataclass(slots=True, frozen=True)
class OverrideWorkflowSkillsItem:
    key: str
    value: SkillsValue


WorkflowItem: TypeAlias = (
    LocalSection
    | WorkflowUse
    | InheritItem
    | OverrideSection
    | OverrideUse
    | WorkflowSkillsItem
    | OverrideWorkflowSkillsItem
)


@dataclass(slots=True, frozen=True)
class WorkflowBody:
    title: str
    preamble: tuple[ProseLine, ...]
    items: tuple[WorkflowItem, ...]
    law: LawBody | None = None


@dataclass(slots=True, frozen=True)
class WorkflowDecl:
    name: str
    body: WorkflowBody
    parent_ref: NameRef | None = None


@dataclass(slots=True, frozen=True)
class SkillsDecl:
    name: str
    body: SkillsBody
    parent_ref: NameRef | None = None


WorkflowSlotValue: TypeAlias = WorkflowBody | NameRef


@dataclass(slots=True, frozen=True)
class AuthoredSlotField:
    key: str
    value: WorkflowSlotValue


@dataclass(slots=True, frozen=True)
class AuthoredSlotAbstract:
    key: str


@dataclass(slots=True, frozen=True)
class AuthoredSlotInherit:
    key: str


@dataclass(slots=True, frozen=True)
class AuthoredSlotOverride:
    key: str
    value: WorkflowSlotValue


@dataclass(slots=True, frozen=True)
class InputsField:
    title: str | None
    value: IoFieldValue
    parent_ref: NameRef | None = None


@dataclass(slots=True, frozen=True)
class OutputsField:
    title: str | None
    value: IoFieldValue
    parent_ref: NameRef | None = None


@dataclass(slots=True, frozen=True)
class SkillsField:
    value: SkillsValue


Field: TypeAlias = (
    RoleScalar
    | RoleBlock
    | AuthoredSlotField
    | AuthoredSlotAbstract
    | AuthoredSlotInherit
    | AuthoredSlotOverride
    | InputsField
    | OutputsField
    | SkillsField
)


@dataclass(slots=True, frozen=True)
class Agent:
    name: str
    fields: tuple[Field, ...]
    abstract: bool = False
    parent_ref: NameRef | None = None


@dataclass(slots=True, frozen=True)
class InputDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]


@dataclass(slots=True, frozen=True)
class InputsDecl:
    name: str
    body: IoBody
    parent_ref: NameRef | None = None


@dataclass(slots=True, frozen=True)
class InputSourceDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]


@dataclass(slots=True, frozen=True)
class OutputDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]
    trust_surface: tuple[TrustSurfaceItem, ...] = ()


@dataclass(slots=True, frozen=True)
class OutputsDecl:
    name: str
    body: IoBody
    parent_ref: NameRef | None = None


@dataclass(slots=True, frozen=True)
class OutputTargetDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]


@dataclass(slots=True, frozen=True)
class OutputShapeDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]


@dataclass(slots=True, frozen=True)
class JsonSchemaDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]


@dataclass(slots=True, frozen=True)
class SkillDecl:
    name: str
    title: str
    items: tuple[RecordItem, ...]


@dataclass(slots=True, frozen=True)
class EnumMember:
    key: str
    value: str


@dataclass(slots=True, frozen=True)
class EnumDecl:
    name: str
    title: str
    members: tuple[EnumMember, ...]


Declaration: TypeAlias = (
    ImportDecl
    | WorkflowDecl
    | SkillsDecl
    | Agent
    | InputsDecl
    | InputDecl
    | InputSourceDecl
    | OutputsDecl
    | OutputDecl
    | OutputTargetDecl
    | OutputShapeDecl
    | JsonSchemaDecl
    | SkillDecl
    | EnumDecl
)


@dataclass(slots=True, frozen=True)
class PromptFile:
    declarations: tuple[Declaration, ...]
    source_path: Path | None = None
````

## File: doctrine/parser.py
````python
from __future__ import annotations

import ast
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path

from lark import Lark, Transformer, v_args
from lark.exceptions import UnexpectedInput, VisitError

from doctrine import model
from doctrine.diagnostics import ParseError, TransformParseFailure
from doctrine.indenter import DoctrineIndenter


@dataclass(slots=True, frozen=True)
class WorkflowBodyParts:
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.WorkflowItem, ...]
    law: model.LawBody | None = None


@dataclass(slots=True, frozen=True)
class SkillsBodyParts:
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.SkillsItem, ...]


@dataclass(slots=True, frozen=True)
class IoBodyParts:
    preamble: tuple[model.ProseLine, ...]
    items: tuple[model.IoItem, ...]


@dataclass(slots=True, frozen=True)
class OutputBodyParts:
    items: tuple[model.RecordItem, ...]
    trust_surface: tuple[model.TrustSurfaceItem, ...]


class ToAst(Transformer):
    def CNAME(self, token):
        return str(token)

    def DOTS(self, token):
        return str(token)

    def PATH_REF(self, token):
        return str(token)

    def ESCAPED_STRING(self, token):
        return ast.literal_eval(str(token))

    def SIGNED_NUMBER(self, token):
        return int(str(token))

    @v_args(inline=True)
    def start(self, prompt_file):
        return prompt_file

    def prompt_file(self, items):
        return model.PromptFile(declarations=tuple(items))

    @v_args(inline=True)
    def inheritance(self, parent_ref):
        return parent_ref

    def agent(self, items):
        return self._agent(items, abstract=False)

    def abstract_agent(self, items):
        return self._agent(items, abstract=True)

    def _agent(self, items, *, abstract: bool):
        name = items[0]
        parent_ref: model.NameRef | None = None
        fields_start = 1
        if len(items) > 1 and isinstance(items[1], model.NameRef):
            parent_ref = items[1]
            fields_start = 2
        return model.Agent(
            name=name,
            fields=tuple(items[fields_start:]),
            abstract=abstract,
            parent_ref=parent_ref,
        )

    @v_args(inline=True)
    def import_decl(self, path):
        return model.ImportDecl(path=path)

    @v_args(inline=True)
    def import_path(self, path):
        return path

    @v_args(inline=True)
    def absolute_import_path(self, module_parts):
        return model.ImportPath(level=0, module_parts=tuple(module_parts))

    @v_args(inline=True)
    def relative_import_path(self, dots, module_parts):
        return model.ImportPath(level=len(dots), module_parts=tuple(module_parts))

    def dotted_name(self, items):
        return tuple(items)

    @v_args(inline=True)
    def name_ref(self, dotted_name):
        parts = tuple(dotted_name)
        return model.NameRef(module_parts=parts[:-1], declaration_name=parts[-1])

    @v_args(inline=True)
    def path_ref(self, raw_ref):
        root_name, path_name = raw_ref.split(":", 1)
        return model.AddressableRef(
            root=_name_ref_from_dotted_name(root_name),
            path=tuple(path_name.split(".")),
        )

    def role_body(self, items):
        return items[0]

    @v_args(inline=True)
    def role_field(self, title_or_text, body=None):
        if body is None:
            return model.RoleScalar(text=title_or_text)
        return model.RoleBlock(title=title_or_text, lines=tuple(body))

    @v_args(inline=True)
    def inputs_inline_field(self, title, items):
        return model.InputsField(title=title, value=tuple(items))

    @v_args(inline=True)
    def inputs_ref_field(self, ref):
        return model.InputsField(title=None, value=ref)

    @v_args(inline=True)
    def inputs_patch_field(self, parent_ref, title, body):
        return model.InputsField(
            title=title,
            value=self._io_body(title, body),
            parent_ref=parent_ref,
        )

    @v_args(inline=True)
    def outputs_inline_field(self, title, items):
        return model.OutputsField(title=title, value=tuple(items))

    @v_args(inline=True)
    def outputs_ref_field(self, ref):
        return model.OutputsField(title=None, value=ref)

    @v_args(inline=True)
    def outputs_patch_field(self, parent_ref, title, body):
        return model.OutputsField(
            title=title,
            value=self._io_body(title, body),
            parent_ref=parent_ref,
        )

    @v_args(inline=True)
    def skills_field(self, title_or_ref, body=None):
        return model.SkillsField(value=self._skills_value(title_or_ref, body))

    @v_args(inline=True)
    def agent_slot_field(self, key, value, body=None):
        return model.AuthoredSlotField(key=key, value=self._workflow_slot_value(value, body))

    @v_args(inline=True)
    def agent_slot_abstract(self, key):
        return model.AuthoredSlotAbstract(key=key)

    @v_args(inline=True)
    def agent_slot_inherit(self, key):
        return model.AuthoredSlotInherit(key=key)

    @v_args(inline=True)
    def agent_slot_override(self, key, value, body=None):
        return model.AuthoredSlotOverride(
            key=key,
            value=self._workflow_slot_value(value, body),
        )

    def _workflow_slot_value(
        self,
        value: str | model.NameRef,
        body: WorkflowBodyParts | None,
    ) -> model.WorkflowSlotValue:
        if body is None:
            return value
        if isinstance(value, model.NameRef):
            raise ValueError("Authored workflow slot references cannot also define an inline body.")
        return model.WorkflowBody(
            title=value,
            preamble=body.preamble,
            items=body.items,
            law=body.law,
        )

    def _skills_value(
        self,
        value: str | model.NameRef,
        body: SkillsBodyParts | None,
    ) -> model.SkillsValue:
        if body is None:
            if isinstance(value, str):
                raise ValueError("Inline skills blocks must define an indented body.")
            return value
        if isinstance(value, model.NameRef):
            raise ValueError("Skills references cannot also define an inline body.")
        return model.SkillsBody(title=value, preamble=body.preamble, items=body.items)

    def _io_body(self, title: str, body: IoBodyParts) -> model.IoBody:
        return model.IoBody(title=title, preamble=body.preamble, items=body.items)

    def slot_body(self, items):
        return items[0]

    @v_args(inline=True)
    def workflow_decl(self, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        workflow_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            workflow_body = body
        return model.WorkflowDecl(
            name=name,
            body=model.WorkflowBody(
                title=title,
                preamble=workflow_body.preamble,
                items=workflow_body.items,
                law=workflow_body.law,
            ),
            parent_ref=parent_ref,
        )

    @v_args(inline=True)
    def skills_decl(self, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        skills_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            skills_body = body
        return model.SkillsDecl(
            name=name,
            body=model.SkillsBody(
                title=title,
                preamble=skills_body.preamble,
                items=skills_body.items,
            ),
            parent_ref=parent_ref,
        )

    @v_args(inline=True)
    def inputs_decl(self, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        io_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            io_body = body
        return model.InputsDecl(
            name=name,
            body=self._io_body(title, io_body),
            parent_ref=parent_ref,
        )

    @v_args(inline=True)
    def input_decl(self, name, title, items):
        return model.InputDecl(name=name, title=title, items=tuple(items))

    @v_args(inline=True)
    def input_source_decl(self, name, title, items):
        return model.InputSourceDecl(name=name, title=title, items=tuple(items))

    @v_args(inline=True)
    def output_decl(self, name, title, body):
        return model.OutputDecl(
            name=name,
            title=title,
            items=body.items,
            trust_surface=body.trust_surface,
        )

    @v_args(inline=True)
    def output_body_line(self, value):
        return value

    def output_body(self, items):
        record_items: list[model.RecordItem] = []
        trust_surface: tuple[model.TrustSurfaceItem, ...] = ()
        for item in items:
            if isinstance(item, tuple) and item and isinstance(item[0], model.TrustSurfaceItem):
                if trust_surface:
                    raise TransformParseFailure(
                        "Output declarations may define `trust_surface` only once.",
                        hints=("Keep exactly one `trust_surface:` block per output declaration.",),
                    )
                trust_surface = tuple(item)
                continue
            record_items.append(item)
        return OutputBodyParts(items=tuple(record_items), trust_surface=trust_surface)

    def trust_surface_block(self, items):
        return tuple(items)

    @v_args(inline=True)
    def trust_surface_item(self, path, when_expr=None):
        return model.TrustSurfaceItem(path=tuple(path), when_expr=when_expr)

    @v_args(inline=True)
    def trust_surface_when(self, expr):
        return expr

    @v_args(inline=True)
    def outputs_decl(self, name, parent_ref_or_title, title_or_body, body=None):
        parent_ref: model.NameRef | None = None
        title = parent_ref_or_title
        io_body = title_or_body
        if body is not None:
            parent_ref = parent_ref_or_title
            title = title_or_body
            io_body = body
        return model.OutputsDecl(
            name=name,
            body=self._io_body(title, io_body),
            parent_ref=parent_ref,
        )

    @v_args(inline=True)
    def output_target_decl(self, name, title, items):
        return model.OutputTargetDecl(name=name, title=title, items=tuple(items))

    @v_args(inline=True)
    def output_shape_decl(self, name, title, items):
        return model.OutputShapeDecl(name=name, title=title, items=tuple(items))

    @v_args(inline=True)
    def json_schema_decl(self, name, title, items):
        return model.JsonSchemaDecl(name=name, title=title, items=tuple(items))

    @v_args(inline=True)
    def skill_decl(self, name, title, items):
        return model.SkillDecl(name=name, title=title, items=tuple(items))

    @v_args(inline=True)
    def enum_decl(self, name, title, members):
        return model.EnumDecl(name=name, title=title, members=tuple(members))

    def enum_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def enum_member(self, key, value):
        return model.EnumMember(key=key, value=value)

    def workflow_preamble(self, items):
        return tuple(items)

    def workflow_items(self, items):
        return tuple(items)

    @v_args(inline=True)
    def workflow_string(self, value):
        return value

    @v_args(inline=True)
    def workflow_body_line(self, value):
        return value

    @v_args(inline=True)
    def skills_string(self, value):
        return value

    @v_args(inline=True)
    def skills_body_line(self, value):
        return value

    @v_args(inline=True)
    def required_line(self, _keyword, text):
        return model.EmphasizedLine(kind="required", text=text)

    @v_args(inline=True)
    def important_line(self, _keyword, text):
        return model.EmphasizedLine(kind="important", text=text)

    @v_args(inline=True)
    def warning_line(self, _keyword, text):
        return model.EmphasizedLine(kind="warning", text=text)

    @v_args(inline=True)
    def note_line(self, _keyword, text):
        return model.EmphasizedLine(kind="note", text=text)

    def workflow_body(self, items):
        preamble: list[model.ProseLine] = []
        workflow_items: list[model.WorkflowItem] = []
        law: model.LawBody | None = None
        for item in items:
            if isinstance(item, model.LawBody):
                if law is not None:
                    raise TransformParseFailure(
                        "Workflow declarations may define `law` only once.",
                        hints=("Keep exactly one `law:` block per workflow body.",),
                    )
                law = item
                continue
            if isinstance(item, (str, model.EmphasizedLine)):
                if workflow_items or law is not None:
                    raise TransformParseFailure(
                        "Workflow prose lines must appear before keyed workflow entries.",
                        hints=(
                            "Move prose lines to the top of the workflow body or put them inside a titled section.",
                        ),
                    )
                preamble.append(item)
                continue
            workflow_items.append(item)
        return WorkflowBodyParts(
            preamble=tuple(preamble),
            items=tuple(workflow_items),
            law=law,
        )

    def workflow_section_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def workflow_section_ref_item(self, ref):
        if isinstance(ref, model.NameRef):
            ref = model.AddressableRef(root=ref)
        return model.SectionBodyRef(ref=ref)

    @v_args(inline=True)
    def local_section(self, key, title, items):
        return model.LocalSection(key=key, title=title, items=tuple(items))

    @v_args(inline=True)
    def workflow_use(self, key, target):
        return model.WorkflowUse(key=key, target=target)

    @v_args(inline=True)
    def workflow_inherit(self, key):
        return model.InheritItem(key=key)

    @v_args(inline=True)
    def workflow_skills_inline(self, title, body):
        return model.WorkflowSkillsItem(
            key="skills",
            value=self._skills_value(title, body),
        )

    @v_args(inline=True)
    def workflow_skills_ref(self, ref):
        return model.WorkflowSkillsItem(
            key="skills",
            value=self._skills_value(ref, None),
        )

    @v_args(inline=True)
    def workflow_override_skills_inline(self, title, body):
        return model.OverrideWorkflowSkillsItem(
            key="skills",
            value=self._skills_value(title, body),
        )

    @v_args(inline=True)
    def workflow_override_skills_ref(self, ref):
        return model.OverrideWorkflowSkillsItem(
            key="skills",
            value=self._skills_value(ref, None),
        )

    @v_args(inline=True)
    def workflow_override_section(self, key, title_or_items, items=None):
        title: str | None = None
        section_items = title_or_items
        if items is not None:
            title = title_or_items
            section_items = items
        return model.OverrideSection(key=key, title=title, items=tuple(section_items))

    @v_args(inline=True)
    def workflow_override_use(self, key, target):
        return model.OverrideUse(key=key, target=target)

    @v_args(inline=True)
    def law_block(self, body):
        return body

    def law_body(self, items):
        return model.LawBody(items=tuple(items))

    def law_section(self, items):
        return model.LawSection(key=items[0], items=tuple(items[1:]))

    @v_args(inline=True)
    def law_inherit(self, key):
        return model.LawInherit(key=key)

    def law_override_section(self, items):
        return model.LawOverrideSection(key=items[0], items=tuple(items[1:]))

    @v_args(inline=True)
    def active_when_stmt(self, expr):
        return model.ActiveWhenStmt(expr=expr)

    @v_args(inline=True)
    def mode_stmt(self, name, expr, enum_ref):
        return model.ModeStmt(name=name, expr=expr, enum_ref=enum_ref)

    @v_args(inline=True)
    def must_stmt(self, expr):
        return model.MustStmt(expr=expr)

    @v_args(inline=True)
    def current_artifact_stmt(self, target, carrier):
        return model.CurrentArtifactStmt(target=target, carrier=carrier)

    def current_none_stmt(self, _items):
        return model.CurrentNoneStmt()

    @v_args(inline=True)
    def own_only_stmt(self, target, when_expr=None):
        return model.OwnOnlyStmt(target=target, when_expr=when_expr)

    def preserve_stmt(self, items):
        kind = items[0]
        target = items[1]
        when_expr: model.Expr | None = items[2] if len(items) > 2 else None
        return model.PreserveStmt(kind=kind, target=target, when_expr=when_expr)

    @v_args(inline=True)
    def support_only_stmt(self, target, when_expr=None):
        return model.SupportOnlyStmt(target=target, when_expr=when_expr)

    def ignore_stmt(self, items):
        target = items[0]
        bases: tuple[str, ...] = ()
        when_expr: model.Expr | None = None
        for extra in items[1:]:
            if isinstance(extra, tuple):
                bases = extra
            else:
                when_expr = extra
        return model.IgnoreStmt(target=target, bases=bases, when_expr=when_expr)

    @v_args(inline=True)
    def invalidate_stmt(self, target, carrier, when_expr=None):
        return model.InvalidateStmt(target=target, carrier=carrier, when_expr=when_expr)

    @v_args(inline=True)
    def forbid_stmt(self, target, when_expr=None):
        return model.ForbidStmt(target=target, when_expr=when_expr)

    def when_stmt(self, items):
        return model.WhenStmt(expr=items[0], items=tuple(items[1:]))

    @v_args(inline=True)
    def match_stmt(self, expr, *cases):
        return model.MatchStmt(expr=expr, cases=tuple(cases))

    def match_case(self, items):
        head = items[0]
        if head == "__ELSE__":
            head = None
        return model.MatchArm(head=head, items=tuple(items[1:]))

    def else_match_head(self, _items):
        return "__ELSE__"

    @v_args(inline=True)
    def stop_stmt(self, message=None, when_expr=None):
        if message is not None and not isinstance(message, str):
            when_expr = message
            message = None
        return model.StopStmt(message=message, when_expr=when_expr)

    @v_args(inline=True)
    def law_route_stmt(self, label, target, when_expr=None):
        return model.LawRouteStmt(label=label, target=target, when_expr=when_expr)

    def preserve_exact(self, _items):
        return "exact"

    def preserve_structure(self, _items):
        return "structure"

    def preserve_decisions(self, _items):
        return "decisions"

    def preserve_mapping(self, _items):
        return "mapping"

    def preserve_vocabulary(self, _items):
        return "vocabulary"

    def ignore_basis_list(self, items):
        return tuple(items)

    def ignore_basis_truth(self, _items):
        return "truth"

    def ignore_basis_comparison(self, _items):
        return "comparison"

    def ignore_basis_rewrite_evidence(self, _items):
        return "rewrite_evidence"

    @v_args(inline=True)
    def law_when_clause(self, expr):
        return expr

    def path_set_expr(self, items):
        paths: list[model.LawPath] = []
        except_paths: list[model.LawPath] = []
        if items:
            first = items[0]
            if isinstance(first, tuple):
                paths.extend(first)
            else:
                paths.append(first)
            for extra in items[1:]:
                if isinstance(extra, tuple):
                    except_paths.extend(extra)
                else:
                    except_paths.append(extra)
        return model.LawPathSet(paths=tuple(paths), except_paths=tuple(except_paths))

    def path_set_base(self, items):
        if len(items) == 1 and isinstance(items[0], model.LawPath):
            return items[0]
        return tuple(items)

    def law_path(self, items):
        parts = list(items[0])
        wildcard = len(items) > 1
        return model.LawPath(parts=tuple(parts), wildcard=wildcard)

    def law_path_wildcard(self, _items):
        return "*"

    def field_path(self, items):
        return tuple(items)

    @v_args(inline=True)
    def expr_ref(self, parts):
        return model.ExprRef(parts=tuple(parts))

    @v_args(inline=True)
    def expr_number(self, value):
        return value

    def expr_true(self, _items):
        return True

    def expr_false(self, _items):
        return False

    def expr_call(self, items):
        return model.ExprCall(name=items[0], args=tuple(items[1:]))

    @v_args(inline=True)
    def expr_or(self, left, right):
        return model.ExprBinary(op="or", left=left, right=right)

    @v_args(inline=True)
    def expr_and(self, left, right):
        return model.ExprBinary(op="and", left=left, right=right)

    @v_args(inline=True)
    def expr_eq(self, left, right):
        return model.ExprBinary(op="==", left=left, right=right)

    @v_args(inline=True)
    def expr_ne(self, left, right):
        return model.ExprBinary(op="!=", left=left, right=right)

    @v_args(inline=True)
    def expr_gt(self, left, right):
        return model.ExprBinary(op=">", left=left, right=right)

    @v_args(inline=True)
    def expr_gte(self, left, right):
        return model.ExprBinary(op=">=", left=left, right=right)

    @v_args(inline=True)
    def expr_lt(self, left, right):
        return model.ExprBinary(op="<", left=left, right=right)

    @v_args(inline=True)
    def expr_lte(self, left, right):
        return model.ExprBinary(op="<=", left=left, right=right)

    @v_args(inline=True)
    def expr_in(self, left, right):
        return model.ExprBinary(op="in", left=left, right=right)

    @v_args(inline=True)
    def skill_entry(self, key, target, body=None):
        return model.SkillEntry(
            key=key,
            target=target,
            items=tuple(body or ()),
        )

    @v_args(inline=True)
    def skills_inherit(self, key):
        return model.InheritItem(key=key)

    @v_args(inline=True)
    def skills_override_entry(self, key, target, body=None):
        return model.OverrideSkillEntry(
            key=key,
            target=target,
            items=tuple(body or ()),
        )

    @v_args(inline=True)
    def skills_section(self, key, title, items):
        return model.SkillsSection(key=key, title=title, items=tuple(items))

    @v_args(inline=True)
    def skills_override_section(self, key, title_or_items, items=None):
        title: str | None = None
        section_items = title_or_items
        if items is not None:
            title = title_or_items
            section_items = items
        return model.OverrideSkillsSection(
            key=key,
            title=title,
            items=tuple(section_items),
        )

    @v_args(inline=True)
    def io_string(self, value):
        return value

    @v_args(inline=True)
    def io_body_line(self, value):
        return value

    def io_body(self, items):
        preamble: list[model.ProseLine] = []
        io_items: list[model.IoItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                if io_items:
                    raise TransformParseFailure(
                        "Inputs and outputs prose lines must appear before keyed entries.",
                        hints=(
                            "Move prose lines to the top of the inputs or outputs body or put them inside a titled section.",
                        ),
                    )
                preamble.append(item)
                continue
            io_items.append(item)
        return IoBodyParts(preamble=tuple(preamble), items=tuple(io_items))

    @v_args(inline=True)
    def io_section(self, key, title, items):
        return model.RecordSection(key=key, title=title, items=tuple(items))

    @v_args(inline=True)
    def io_inherit(self, key):
        return model.InheritItem(key=key)

    @v_args(inline=True)
    def io_override_section(self, key, title_or_items, items=None):
        title: str | None = None
        section_items = title_or_items
        if items is not None:
            title = title_or_items
            section_items = items
        return model.OverrideIoSection(
            key=key,
            title=title,
            items=tuple(section_items),
        )

    def record_body(self, items):
        return tuple(items)

    @v_args(inline=True)
    def record_text(self, value):
        return value

    def record_item_body(self, items):
        return tuple(items[0])

    @v_args(inline=True)
    def record_keyed_item(self, key, head, body=None):
        if isinstance(head, str) and body is not None:
            return model.RecordSection(key=key, title=head, items=tuple(body))
        return model.RecordScalar(key=key, value=head, body=None if body is None else tuple(body))

    @v_args(inline=True)
    def record_ref_item(self, ref, body=None):
        return model.RecordRef(ref=ref, body=None if body is None else tuple(body))

    def skills_body(self, items):
        preamble: list[model.ProseLine] = []
        skills_items: list[model.SkillsItem] = []
        for item in items:
            if isinstance(item, (str, model.EmphasizedLine)):
                if skills_items:
                    raise TransformParseFailure(
                        "Skills prose lines must appear before keyed skills entries.",
                        hints=(
                            "Move prose lines to the top of the skills body or put them inside a titled skills section.",
                        ),
                    )
                preamble.append(item)
                continue
            skills_items.append(item)
        return SkillsBodyParts(preamble=tuple(preamble), items=tuple(skills_items))

    def skills_section_body(self, items):
        return tuple(items)

    def skill_entry_body(self, items):
        return tuple(items[0])

    def ref_list(self, items):
        return tuple(items)

    @v_args(inline=True)
    def ref_item(self, ref):
        return ref

    @v_args(inline=True)
    def route_stmt(self, label, target):
        return model.RouteLine(label=label, target=target)

    def block_lines(self, items):
        return tuple(items)


@lru_cache(maxsize=1)
def build_lark_parser() -> Lark:
    return Lark.open(
        "grammars/doctrine.lark",
        rel_to=__file__,
        parser="lalr",
        lexer="contextual",
        postlex=DoctrineIndenter(),
        strict=True,
        maybe_placeholders=False,
    )


def parse_text(source: str, *, source_path: str | Path | None = None) -> model.PromptFile:
    resolved_path = Path(source_path).resolve() if source_path is not None else None
    try:
        tree = build_lark_parser().parse(source)
    except UnexpectedInput as exc:
        raise ParseError.from_lark(source=source, path=resolved_path, exc=exc) from exc
    try:
        return ToAst().transform(tree)
    except VisitError as exc:
        if isinstance(exc.orig_exc, ValueError):
            raise ParseError.from_transform(source=source, path=resolved_path, exc=exc) from exc
        raise


def parse_file(path: str | Path) -> model.PromptFile:
    resolved_path = Path(path).resolve()
    prompt_file = parse_text(resolved_path.read_text(), source_path=resolved_path)
    return replace(prompt_file, source_path=resolved_path)


def _name_ref_from_dotted_name(dotted_name: str) -> model.NameRef:
    parts = tuple(dotted_name.split("."))
    return model.NameRef(module_parts=parts[:-1], declaration_name=parts[-1])
````

## File: examples/01_hello_world/ref/AGENTS.md
````markdown
You are the hello world agent.

## Instruction

Say hello world.
````

## File: examples/02_sections/ref/AGENTS.md
````markdown
You are the sections demonstration agent.

## Steps

Follow the steps below in order.

### Step One

Say hello.

### Step Two

Say world.
````

## File: examples/02_sections/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "sections demo renders headed steps and substeps"
status = "active"
kind = "render_contract"
agent = "SectionsDemo"
assertion = "exact_lines"
approx_ref = "ref/AGENTS.md"
expected_lines = [
  "You are the sections demonstration agent.",
  "",
  "## Steps",
  "",
  "Follow the steps below in order.",
  "",
  "### Step One",
  "",
  "Say hello.",
  "",
  "### Step Two",
  "",
  "Say world.",
]

[[cases]]
name = "duplicate local section keys fail in compile stage"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_DUPLICATE_SECTION_KEY.prompt"
agent = "DuplicateSectionKeysDemo"
exception_type = "CompileError"
error_code = "E261"
message_contains = [
  "Duplicate workflow item key",
  "step_one",
]
````

## File: examples/03_imports/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "python-like imports compose simple and chained workflows"
status = "active"
kind = "render_contract"
agent = "ImportsDemo"
assertion = "exact_lines"
approx_ref = "ref/AGENTS.md"
expected_lines = [
  "You are the imports demonstration agent.",
  "",
  "## Imported Steps",
  "",
  "Follow the imported instructions below.",
  "",
  "### Greeting",
  "",
  "Say hello.",
  "",
  "### Object",
  "",
  "Say world.",
  "",
  "### Polite Greeting",
  "",
  "Say hello politely and keep the tone warm.",
  "",
  "### Absolute Briefing",
  "",
  "This file composes sibling imports through dotted package paths.",
  "",
  "#### Opening",
  "",
  "State the topic.",
  "",
  "#### Closing",
  "",
  "End with one clear next step.",
  "",
  "### Relative Chain",
  "",
  "This file chains a sibling-relative import with a parent-relative import.",
  "",
  "#### Leaf Step",
  "",
  "This module reaches back to its parent package before following the path forward again.",
  "",
  "##### Shared Context",
  "",
  "Start with the shared context.",
  "",
  "#### Shared Wrap-Up",
  "",
  "Finish with a shared wrap-up.",
  "",
  "### Deep Relative Chain",
  "",
  "This file uses both a sibling-relative import and a multi-level parent-relative import.",
  "",
  "#### Deep Detail",
  "",
  "This file walks back up the package tree with `...` before following the path forward again.",
  "",
  "##### Root Topic",
  "",
  "Name the root topic once.",
  "",
  "#### Final Note",
  "",
  "End with the final shared note.",
]

[[cases]]
name = "missing imported module fails in compile stage"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_MISSING_MODULE.prompt"
agent = "MissingModuleDemo"
exception_type = "CompileError"
error_code = "E280"
message_contains = [
  "Missing import module",
  "simple.missing",
]

[[cases]]
name = "unresolved qualified symbol fails in compile stage"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_UNRESOLVED_SYMBOL.prompt"
agent = "UnresolvedImportedSymbolDemo"
exception_type = "CompileError"
error_code = "E281"
message_contains = [
  "Missing imported declaration",
  "simple.greeting.MissingGreeting",
]

[[cases]]
name = "duplicate declaration name in one imported module fails in compile stage"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_DUPLICATE_DECLARATION.prompt"
agent = "DuplicateDeclarationDemo"
exception_type = "CompileError"
error_code = "E288"
message_contains = [
  "Duplicate declaration name",
  "duplicate_names.DuplicateGreeting",
]

[[cases]]
name = "imported parse failure shows the imported module trace"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_IMPORTED_PARSE.prompt"
agent = "ImportedParseFailureDemo"
exception_type = "ParseError"
error_code = "E101"
message_contains = [
  "Unexpected newline",
  "load import module `broken.syntax`",
  "broken/syntax.prompt",
]
````

## File: examples/04_inheritance/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "hello world greeter inherits shared sections from abstract bases"
status = "active"
kind = "render_contract"
agent = "HelloWorldGreeter"
assertion = "exact_lines"
approx_ref = "ref/hello_world_greeter/AGENTS.md"
expected_lines = [
  "You are the hello world greeter.",
  "",
  "## Hello World Instructions",
  "",
  "### Greeting",
  "",
  "Say hello.",
  "",
  "### Courtesy",
  "",
  "Keep the tone warm and direct.",
  "",
  "### Object",
  "",
  "Say world.",
]

[[cases]]
name = "inheritance demo overrides one inherited section in place"
status = "active"
kind = "render_contract"
agent = "InheritanceDemo"
assertion = "exact_lines"
approx_ref = "ref/inheritance_demo/AGENTS.md"
expected_lines = [
  "You are the inheritance demonstration agent.",
  "",
  "## Inherited Steps",
  "",
  "Follow the inherited steps below.",
  "This child keeps the shared greeting and replaces the final step.",
  "",
  "### Greeting",
  "",
  "Say hello.",
  "",
  "### Courtesy",
  "",
  "Keep the tone warm and direct.",
  "",
  "### Object",
  "",
  "Say inherited world.",
]

[[cases]]
name = "abstract base agent does not render"
status = "active"
kind = "compile_fail"
agent = "ImportedBaseGreeter"
exception_type = "CompileError"
error_code = "E202"
message_contains = [
  "Abstract agent does not render",
  "ImportedBaseGreeter",
]

[[cases]]
name = "imported workflow inheritance works through a named workflow parent"
status = "active"
kind = "render_contract"
agent = "ImportedWorkflowGreeter"
assertion = "exact_lines"
approx_ref = "ref/imported_workflow_greeter/AGENTS.md"
expected_lines = [
  "You are the imported workflow greeter.",
  "",
  "## Imported Workflow Instructions",
  "",
  "This workflow inherits its structure from an imported parent.",
  "",
  "### Greeting",
  "",
  "Say hello.",
  "",
  "### Courtesy",
  "",
  "Keep the tone warm and direct.",
  "",
  "### Object",
  "",
  "Say imported world.",
]
````

## File: examples/07_handoffs/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "handoff routing renders authored slots and narrow routes"
status = "active"
kind = "render_contract"
agent = "ProjectLead"
assertion = "exact_lines"
expected_lines = [
  "Core job: start the work, route it to Research Specialist, and take it back after Writing Specialist finishes.",
  "",
  "## Your Job",
  "",
  "Start the issue with a clear route.",
  "Route the first owner change.",
  "Keep the issue on a truthful route when work is blocked or routing goes stale.",
  "Take the issue back after the final specialist return and close it out honestly.",
  "",
  "## Read First",
  "",
  "Start by reading Your Job.",
  "Then read Workflow Core.",
  "",
  "## Workflow Core",
  "",
  "This file is the runtime guide for a simple multi-agent routing pattern.",
  "",
  "### Same-Issue Workflow",
  "",
  "Keep the whole job on one issue from setup through final return.",
  "Keep one owner at a time on that issue.",
  "The normal order is Project Lead -> Research Specialist -> Writing Specialist -> Project Lead.",
  "Route the first owner change to Research Specialist.",
  "After Research Specialist, the next owner is Writing Specialist.",
  "After Writing Specialist, the next owner is Project Lead.",
  "If the route is broken or the work is blocked before specialist work begins, keep or return the work to Project Lead.",
  "",
  "### Next Owner",
  "",
  "When ready to start the work -> ResearchSpecialist",
  "If the route is broken or the work is blocked before specialist work begins -> ProjectLead",
  "",
  "### Owner Change Comment",
  "",
  "Every owner-change comment should say:",
  "- what this turn changed",
  "- the next owner when ownership is changing now",
  "- the exact blocker when the issue is blocked",
]

[[cases]]
name = "handoff routing builds the canonical agent-doc tree"
status = "active"
kind = "build_contract"
build_target = "example_07_handoffs"

[[cases]]
name = "referenced authored slots reject inline bodies in parse stage"
status = "active"
kind = "parse_fail"
prompt = "prompts/INVALID_REFERENCED_SLOT_WITH_INLINE_BODY.prompt"
exception_type = "ParseError"
error_code = "E105"
message_contains = [
  "Invalid authored slot body",
  "Authored workflow slot references cannot also define an inline body",
  "override read_first",
]
````

## File: examples/08_inputs/prompts/AGENTS.prompt
````
# This example shows shipped `input` and `input source` declarations.
# Each input separates:
# - `source`: how the agent gets the input
# - `shape`: what kind of thing it is once the agent has it
# - `requirement`: whether the turn should fail if it is missing
# `source` is typed, not string-based.
# Built-in sources in this shipped subset:
# - `Prompt`
# - `File` (requires `path`)
# - `EnvVar` (requires `env`)
# A custom source can define its own required and optional keys.

input CurrentIssue: "Current Issue"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required
    "This content is already present in the invocation prompt."


input SectionPlan: "Section Plan"
    source: File
        path: "section_root/_authoring/SECTION_PLAN.md"
    shape: MarkdownDocument
    requirement: Required
    "Read this file before changing section planning."


input PreviousSummary: "Previous Summary"
    source: File
        path: "section_root/_authoring/PREVIOUS_SUMMARY.md"
    shape: MarkdownDocument
    requirement: Advisory
    "Use this only if continuity with earlier work matters for the current turn."


input TrackerRoot: "Tracker Root"
    source: EnvVar
        env: "TRACKER_ROOT"
    shape: DirectoryPath
    requirement: Required
    "This environment variable points to the tracker checkout root."


# A custom source can define its own source-specific keys.
# This keeps `source` typed and extensible without making every input accept
# every possible source field.
input source FigmaDocument: "Figma Document"
    required: "Required Source Keys"
        url: "URL"

    optional: "Optional Source Keys"
        node: "Node"


input DesignSpec: "Design Spec"
    source: FigmaDocument
        url: "https://figma.com/design/abc123/Example-Design"
        node: "12:34"
    shape: DesignDocument
    requirement: Required
    "Use this design document when the turn depends on a specific Figma source."


# Model 1: input can be provided directly in the invocation prompt.
agent PromptInputAgent:
    role: "Core job: summarize the current issue from prompt-provided input."

    your_job: "Your Job"
        "Read the current issue from the prompt."
        "Summarize it clearly and briefly."

    inputs: "Inputs"
        CurrentIssue


# Model 2: input can be looked up from a named path.
# This also shows that requiredness is separate from source:
# both inputs come from a path, but one is required and the other is advisory.
agent PathInputAgent:
    role: "Core job: revise a section plan using path-based file input."

    your_job: "Your Job"
        "Read the required section plan from the named path."
        "Use the previous summary only if continuity matters for the current turn."
        "Fail if the required section plan is missing."

    inputs: "Inputs"
        SectionPlan
        PreviousSummary


# Model 3: input can be looked up from an environment variable.
agent EnvInputAgent:
    role: "Core job: locate the tracker checkout from an environment variable before doing any tracker work."

    your_job: "Your Job"
        "Look up the tracker root from the environment variable."
        "Fail if the environment variable is missing."

    inputs: "Inputs"
        TrackerRoot


# Model 4: input can come from a declared custom source.
agent CustomSourceInputAgent:
    role: "Core job: use a design spec from a custom typed input source."

    your_job: "Your Job"
        "Use the custom source configuration to find the design document."
        "Fail if the required design source data is missing."

    inputs: "Inputs"
        DesignSpec
````

## File: examples/11_skills_and_tools/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "skill-first capability modeling renders required and advisory references"
status = "active"
kind = "render_contract"
agent = "LessonCopywriter"
assertion = "exact_lines"
expected_lines = [
  "Core job: turn an approved lesson manifest into grounded reader copy without changing lesson structure or authority scope.",
  "",
  "## Your Job",
  "",
  "Read the whole lesson before you rewrite isolated strings.",
  "Use grounded domain wording without changing the approved structure or authority scope.",
  "If no named task skill fits cleanly, discover the right one before you guess.",
  "",
  "## Skills",
  "",
  "### Can Run",
  "",
  "#### domain-grounding-kb",
  "",
  "##### Purpose",
  "",
  "Ground reader-facing domain wording against current source truth.",
  "",
  "This skill is required for this role. If you cannot locate it, stop and escalate instead of guessing.",
  "",
  "##### Use When",
  "",
  "Use this when the lane needs primary-source receipts for reader-facing copy.",
  "",
  "##### Requires",
  "",
  "A wording surface or claim that needs domain grounding.",
  "",
  "##### Provides",
  "",
  "The normal repo workflow for grounding domain wording against current source truth.",
  "A clear route for collecting the receipts this lane needs.",
  "",
  "##### Does Not",
  "",
  "Does not change the approved structure.",
  "Does not establish final expert authority.",
  "",
  "#### domain-copy-rewrite",
  "",
  "##### Purpose",
  "",
  "Rewrite reader-facing domain copy in the repo's expected voice.",
  "",
  "##### Use When",
  "",
  "Use this when the job is reader-facing domain wording such as titles, hints, coach text, explanations, and feedback.",
  "",
  "### Discover With",
  "",
  "#### find-skills",
  "",
  "##### Purpose",
  "",
  "Find the best matching repo skill for the current job.",
  "",
  "### Not For This Role",
  "",
  "#### device-runtime-check",
  "",
  "##### Purpose",
  "",
  "Drive a simulator or device for runtime investigation.",
  "",
  "##### Reason",
  "",
  "This role is baseline copy work, not simulator or device investigation.",
  "",
  "#### dev-loop-restore",
  "",
  "##### Purpose",
  "",
  "Restore a live development loop.",
  "",
  "##### Use When",
  "",
  "Use this only when the job is restoring a live development loop.",
  "",
  "##### Reason",
  "",
  "This role is baseline copy work, not development environment repair.",
]
````

## File: examples/14_handoff_truth/prompts/AGENTS.prompt
````
# This example keeps the same handoff-truth idea but uses the `03_imports`
# pattern so the source reads by concern instead of as one long file.
# - `contracts.inputs` holds the turn inputs
# - `contracts.outputs` holds the produced contracts
# - `roles.*` holds the role-local job text
#
# This still does not add a new primitive.
# It is the same example, just split into files that are easier to scan.
import contracts.inputs
import contracts.outputs
import roles.project_lead
import roles.acceptance_critic
import roles.section_author


agent ProjectLead:
    role: "Core job: take the issue back when the route is unclear or the current brief is missing."

    your_job: roles.project_lead.ProjectLeadJob


agent AcceptanceCritic:
    role: "Core job: review the exact current dossier and validation record named in the handoff."

    your_job: roles.acceptance_critic.AcceptanceCriticJob


agent SectionAuthor:
    role: "Core job: turn the current brief into the current dossier, leave one honest handoff, and route the same issue truthfully."

    your_job: roles.section_author.SectionAuthorJob

    inputs: "Inputs"
        contracts.inputs.CurrentIssuePlan
        contracts.inputs.SectionBrief
        contracts.inputs.PriorReviewNotes

    outputs: "Outputs"
        contracts.outputs.SectionDossierOutput
        contracts.outputs.SectionAuthorHandoff

    handoff_routing: "Handoff Routing"
        next_owner_if_ready: "Next Owner If Ready"
            route "If the dossier is ready for review" -> AcceptanceCritic

        if_the_work_is_not_ready: "If The Work Is Not Ready"
            route "If the route is unclear or the current brief is missing" -> ProjectLead

    when_to_stop: "When To Stop"
        stop_here_if: "Stop Here If"
            "Stop when the handoff comment names the exact files to use now and the next owner is clear."

        hard_stop_rule: "Hard Stop Rule"
            "If the current brief is missing, stop and escalate."
            "Do not point the next owner at stale notes, old copies, or a folder name instead of exact files."
````

## File: examples/14_handoff_truth/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "split-by-concern imports preserve handoff truth surfaces"
status = "active"
kind = "render_contract"
agent = "SectionAuthor"
assertion = "exact_lines"
expected_lines = [
  "Core job: turn the current brief into the current dossier, leave one honest handoff, and route the same issue truthfully.",
  "",
  "## Your Job",
  "",
  "Read the current issue plan and current brief before you write.",
  "Use prior review notes only as continuity help, not as proof.",
  "Write the current dossier and current validation record.",
  "Leave one handoff comment that names the exact files to use now.",
  "Say plainly whether current review files apply yet.",
  "Route the issue to the honest next owner.",
  "",
  "## Inputs",
  "",
  "### Current Issue Plan",
  "",
  "- Source: Prompt",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "Use the current issue plan to understand the intended lane and current scope.",
  "",
  "### Section Brief",
  "",
  "- Source: File",
  "- Path: `section_root/_authoring/BRIEF.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "Use the current brief as the upstream scope for this turn.",
  "",
  "### Prior Review Notes",
  "",
  "- Source: File",
  "- Path: `section_root/_authoring/PRIOR_REVIEW_NOTES.md`",
  "- Shape: Markdown Document",
  "- Requirement: Advisory",
  "",
  "Use this only for continuity when it exists.",
  "Do not treat it as proof of the current turn.",
  "",
  "## Outputs",
  "",
  "### Section Dossier Output",
  "",
  "- Current Dossier: `section_root/_authoring/SECTION_DOSSIER.md`",
  "- Current Dossier Shape: Markdown Document",
  "- Validation Record: `section_root/_authoring/DOSSIER_VALIDATION.md`",
  "- Validation Record Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "#### Must Include",
  "",
  "##### Current Dossier",
  "",
  "SECTION_DOSSIER.md must reflect the current section proposal for this turn.",
  "",
  "##### Validation Record",
  "",
  "DOSSIER_VALIDATION.md must say what checks ran, what passed or failed, or what did not run yet.",
  "",
  "#### Standalone Read",
  "",
  "A downstream reader should be able to read SECTION_DOSSIER.md and DOSSIER_VALIDATION.md and understand the current proposal and its validation basis.",
  "",
  "### Section Author Handoff",
  "",
  "- Target: Issue Comment",
  "- Issue: `CURRENT_ISSUE`",
  "- Shape: Handoff Comment Text",
  "- Requirement: Required",
  "",
  "#### Must Include",
  "",
  "##### What Changed",
  "",
  "Say what changed in this turn.",
  "",
  "##### Use Now",
  "",
  "Name the exact current files the next owner should read now.",
  "",
  "##### Review Files",
  "",
  "Either name the current review files explicitly or say plainly that no current review files apply yet.",
  "",
  "##### Next Owner",
  "",
  "Name the honest next owner.",
  "",
  "#### Standalone Read",
  "",
  "A downstream reader should be able to read this comment alone and understand what changed, which files are current now, whether review files apply, and who owns next.",
  "",
  "#### Example",
  "",
  "- changed: rewrote the dossier scope and added the validation record",
  "- use now: SECTION_DOSSIER.md and DOSSIER_VALIDATION.md",
  "- review files: no current review files apply yet",
  "- next owner: AcceptanceCritic",
  "",
  "## Handoff Routing",
  "",
  "### Next Owner If Ready",
  "",
  "If the dossier is ready for review -> AcceptanceCritic",
  "",
  "### If The Work Is Not Ready",
  "",
  "If the route is unclear or the current brief is missing -> ProjectLead",
  "",
  "## When To Stop",
  "",
  "### Stop Here If",
  "",
  "Stop when the handoff comment names the exact files to use now and the next owner is clear.",
  "",
  "### Hard Stop Rule",
  "",
  "If the current brief is missing, stop and escalate.",
  "Do not point the next owner at stale notes, old copies, or a folder name instead of exact files.",
]

[[cases]]
name = "split-by-concern imports build the canonical agent-doc tree"
status = "active"
kind = "build_contract"
build_target = "example_14_handoff_truth"
````

## File: examples/22_skills_block_inheritance/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "named skills blocks inherit and patch explicitly"
status = "active"
kind = "render_contract"
agent = "SkillsInheritanceDemo"
assertion = "exact_lines"
expected_lines = [
  "Use the inherited skills block for this role.",
  "",
  "## Skills",
  "",
  "### How To Use",
  "",
  "Start with the skill that directly matches the current job.",
  "",
  "### Copy Rewrite Skill",
  "",
  "#### Purpose",
  "",
  "Rewrite reader-facing text without changing the underlying guide job.",
  "",
  "This skill is required for this role. If you cannot locate it, stop and escalate instead of guessing.",
  "",
  "#### Reason",
  "",
  "For this role, rewriting is the lead capability.",
  "",
  "### Support",
  "",
  "#### Find Skills",
  "",
  "##### Purpose",
  "",
  "Find the right repo skill before you guess.",
  "",
  "#### Grounding Skill",
  "",
  "##### Purpose",
  "",
  "Ground the current claim before you write.",
]

[[cases]]
name = "cyclic skills inheritance fails with a dedicated skills code"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_CYCLIC_SKILLS_INHERITANCE.prompt"
agent = "InvalidSkillsCycleDemo"
exception_type = "CompileError"
error_code = "E250"
message_contains = [
  "Skills inheritance cycle",
  "CycleA -> CycleB -> CycleA",
]
````

## File: examples/31_currentness_and_trust_surface/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "current truth can be carried from an input artifact"
status = "active"
kind = "render_contract"
agent = "CurrentApprovedPlanDemo"
assertion = "exact_lines"
approx_ref = "ref/current_approved_plan_demo/AGENTS.md"
expected_lines = [
  "Carry one portable current artifact through a declared handoff field.",
  "",
  "## Carry Current Truth",
  "",
  "Keep one current artifact explicit and portable.",
  "",
  "Current artifact: Approved Plan.",
  "",
  "## Inputs",
  "",
  "### Approved Plan",
  "",
  "- Source: File",
  "- Path: `unit_root/_authoring/APPROVED_PLAN.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "## Outputs",
  "",
  "### Coordination Handoff",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
  "",
  "#### Current Artifact",
  "",
  "Name the one artifact that is current now.",
  "",
  "#### Trust Surface",
  "",
  "- Current Artifact",
  "",
  "#### Standalone Read",
  "",
  "A downstream owner must be able to read this output alone and know which artifact is current now.",
]

[[cases]]
name = "current truth can be carried from a newly produced artifact"
status = "active"
kind = "render_contract"
agent = "CurrentSectionMetadataDemo"
assertion = "exact_lines"
approx_ref = "ref/current_section_metadata_demo/AGENTS.md"
expected_lines = [
  "Carry a newly produced artifact as the current downstream truth.",
  "",
  "## Carry Current Truth",
  "",
  "Keep one current artifact explicit and portable.",
  "",
  "Current artifact: Section Metadata.",
  "",
  "## Outputs",
  "",
  "### Section Metadata",
  "",
  "- Target: File",
  "- Path: `unit_root/_authoring/section_metadata.json`",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "### Coordination Handoff",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
  "",
  "#### Current Artifact",
  "",
  "Name the one artifact that is current now.",
  "",
  "#### Trust Surface",
  "",
  "- Current Artifact",
  "",
  "#### Standalone Read",
  "",
  "A downstream owner must be able to read this output alone and know which artifact is current now.",
]

[[cases]]
name = "current artifact bindings require via carriers"
status = "active"
kind = "parse_fail"
prompt = "prompts/INVALID_CURRENT_ARTIFACT_WITHOUT_VIA.prompt"
exception_type = "ParseError"
error_code = "E133"
message_contains = [
  "Missing `via` carrier",
]

[[cases]]
name = "carrier refs reject unknown output fields"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_VIA_UNKNOWN_OUTPUT_FIELD.prompt"
agent = "InvalidViaUnknownOutputField"
exception_type = "CompileError"
error_code = "E337"
message_contains = [
  "Unknown current carrier field",
  "CoordinationHandoff.current_artifact",
]

[[cases]]
name = "carrier fields must be listed in the trust surface"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_VIA_FIELD_NOT_IN_TRUST_SURFACE.prompt"
agent = "InvalidViaFieldNotInTrustSurface"
exception_type = "CompileError"
error_code = "E336"
message_contains = [
  "Current carrier field missing from trust surface",
  "current_artifact",
]

[[cases]]
name = "workflows that carry current truth must emit the carrier output"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_CARRIER_OUTPUT_NOT_EMITTED.prompt"
agent = "InvalidCarrierOutputNotEmitted"
exception_type = "CompileError"
error_code = "E333"
message_contains = [
  "Current carrier output not emitted",
  "CoordinationHandoff",
]

[[cases]]
name = "current output artifacts must be emitted by the concrete turn"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_CURRENT_OUTPUT_NOT_EMITTED.prompt"
agent = "InvalidCurrentOutputNotEmitted"
exception_type = "CompileError"
error_code = "E334"
message_contains = [
  "Current output not emitted",
  "SectionMetadata",
]

[[cases]]
name = "current artifact targets must stay rooted in declared inputs or outputs"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_CURRENT_TARGET_WRONG_KIND.prompt"
agent = "InvalidCurrentTargetWrongKind"
exception_type = "CompileError"
error_code = "E335"
message_contains = [
  "Current artifact target has wrong kind",
  "input or output",
]
````

## File: examples/32_modes_and_match/ref/mode_aware_edit_demo/AGENTS.md
````markdown
Edit in exactly one typed mode and carry that mode through the handoff.

## Mode-Aware Edit

Edit in exactly one typed mode and carry that mode through the handoff.

This pass runs only when edit is owed now.

Work in exactly one mode:
- manifest-title
- section-summary

If mode is manifest-title:
- Current artifact: Approved Plan.
- Must CurrentHandoff.preserve_basis == ApprovedPlan.

If mode is section-summary:
- Current artifact: Approved Structure.
- Must CurrentHandoff.preserve_basis == ApprovedStructure.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether edit work is owed, which mode is active, and which preserve basis stays authoritative.

### Approved Plan

- Source: File
- Path: `unit_root/_authoring/APPROVED_PLAN.md`
- Shape: Markdown Document
- Requirement: Required

### Approved Structure

- Source: File
- Path: `unit_root/_authoring/APPROVED_STRUCTURE.md`
- Shape: Markdown Document
- Requirement: Required

## Outputs

### Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Active Mode

Name the active mode for this pass.

#### Trust Surface

- Current Artifact
- Active Mode

#### Standalone Read

A downstream owner must be able to read this output alone and know which artifact is current now and which mode is active.
````

## File: examples/32_modes_and_match/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "typed modes can select one current artifact per branch"
status = "active"
kind = "render_contract"
agent = "ModeAwareEditDemo"
assertion = "exact_lines"
approx_ref = "ref/mode_aware_edit_demo/AGENTS.md"
expected_lines = [
  "Edit in exactly one typed mode and carry that mode through the handoff.",
  "",
  "## Mode-Aware Edit",
  "",
  "Edit in exactly one typed mode and carry that mode through the handoff.",
  "",
  "This pass runs only when edit is owed now.",
  "",
  "Work in exactly one mode:",
  "- manifest-title",
  "- section-summary",
  "",
  "If mode is manifest-title:",
  "- Current artifact: Approved Plan.",
  "- Must CurrentHandoff.preserve_basis == ApprovedPlan.",
  "",
  "If mode is section-summary:",
  "- Current artifact: Approved Structure.",
  "- Must CurrentHandoff.preserve_basis == ApprovedStructure.",
  "",
  "## Inputs",
  "",
  "### Current Handoff",
  "",
  "- Source: Prompt",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "Use the host-provided handoff facts that say whether edit work is owed, which mode is active, and which preserve basis stays authoritative.",
  "",
  "### Approved Plan",
  "",
  "- Source: File",
  "- Path: `unit_root/_authoring/APPROVED_PLAN.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "### Approved Structure",
  "",
  "- Source: File",
  "- Path: `unit_root/_authoring/APPROVED_STRUCTURE.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "## Outputs",
  "",
  "### Coordination Handoff",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
  "",
  "#### Current Artifact",
  "",
  "Name the one artifact that is current now.",
  "",
  "#### Active Mode",
  "",
  "Name the active mode for this pass.",
  "",
  "#### Trust Surface",
  "",
  "- Current Artifact",
  "- Active Mode",
  "",
  "#### Standalone Read",
  "",
  "A downstream owner must be able to read this output alone and know which artifact is current now and which mode is active.",
]

[[cases]]
name = "typed matches must cover every mode or include else"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_NONEXHAUSTIVE_MODE_MATCH.prompt"
agent = "InvalidNonexhaustiveModeMatch"
exception_type = "CompileError"
error_code = "E342"
message_contains = [
  "Non-exhaustive mode match",
  "EditMode",
]

[[cases]]
name = "mode values must stay inside the referenced enum"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_MODE_VALUE_OUTSIDE_ENUM.prompt"
agent = "InvalidModeValueOutsideEnum"
exception_type = "CompileError"
error_code = "E341"
message_contains = [
  "Mode value outside enum",
  "taxonomy",
]

[[cases]]
name = "match arms cannot bind multiple current artifacts"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_DUPLICATE_CURRENT_IN_MATCH_ARM.prompt"
agent = "InvalidDuplicateCurrentInMatchArm"
exception_type = "CompileError"
error_code = "E332"
message_contains = [
  "Multiple current-subject forms",
  "current artifact",
]

[[cases]]
name = "every active match arm still needs one current subject"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_ACTIVE_BRANCH_WITHOUT_CURRENT_AFTER_MATCH.prompt"
agent = "InvalidActiveBranchWithoutCurrentAfterMatch"
exception_type = "CompileError"
error_code = "E331"
message_contains = [
  "Missing current-subject form",
]
````

## File: examples/33_scope_and_exact_preservation/prompts/INVALID_OWN_PATH_NOT_ADDRESSABLE.prompt
````
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
        own only MissingArtifact.title


agent InvalidOwnPathNotAddressable:
    role: "Trigger an unaddressable own path."
    workflow: InvalidNarrowMetadataEdit
    outputs: "Outputs"
        SectionMetadata
        CoordinationHandoff
````

## File: examples/33_scope_and_exact_preservation/prompts/INVALID_OWN_PATH_NOT_ROOTED_IN_CURRENT_ARTIFACT.prompt
````
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


agent InvalidOwnPathNotRootedInCurrentArtifact:
    role: "Trigger an own path outside the current artifact."
    workflow: InvalidNarrowMetadataEdit
    outputs: "Outputs"
        SectionMetadata
        CoordinationHandoff
````

## File: examples/33_scope_and_exact_preservation/ref/narrow_metadata_edit_demo/AGENTS.md
````markdown
Keep narrow ownership explicit and preserve every unowned field.

## Narrow Metadata Edit

Keep narrow ownership explicit and preserve every unowned field.

Work in exactly one mode:
- name-only
- summary-refresh

If mode is name-only:
- Current artifact: Section Metadata.
- Own only `SectionMetadata.name`.
- Preserve exact `SectionMetadata.*` except `SectionMetadata.name`.
- Preserve decisions `ApprovedPlan`.

If mode is summary-refresh:
- Current artifact: Section Metadata.
- Own only {`SectionMetadata.name`, `SectionMetadata.description`}.
- Preserve exact `SectionMetadata.*` except `SectionMetadata.name`, `SectionMetadata.description`.
- Preserve decisions `ApprovedStructure`.
- Do not modify {`SectionMetadata.taxonomy`, `SectionMetadata.flags`}.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say which metadata edit mode is active.

### Approved Plan

- Source: File
- Path: `unit_root/_authoring/APPROVED_PLAN.md`
- Shape: Markdown Document
- Requirement: Required

### Approved Structure

- Source: File
- Path: `unit_root/_authoring/APPROVED_STRUCTURE.md`
- Shape: Markdown Document
- Requirement: Required

## Outputs

### Section Metadata

- Target: File
- Path: `unit_root/_authoring/section_metadata.json`
- Shape: Json Object
- Requirement: Required

### Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Trust Surface

- Current Artifact

#### Standalone Read

A downstream owner must be able to read this output alone and know which artifact is current now.
````

## File: examples/33_scope_and_exact_preservation/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "own only and preserve exact keep narrow edits honest"
status = "active"
kind = "render_contract"
agent = "NarrowMetadataEditDemo"
assertion = "exact_lines"
approx_ref = "ref/narrow_metadata_edit_demo/AGENTS.md"
expected_lines = [
  "Keep narrow ownership explicit and preserve every unowned field.",
  "",
  "## Narrow Metadata Edit",
  "",
  "Keep narrow ownership explicit and preserve every unowned field.",
  "",
  "Work in exactly one mode:",
  "- name-only",
  "- summary-refresh",
  "",
  "If mode is name-only:",
  "- Current artifact: Section Metadata.",
  "- Own only `SectionMetadata.name`.",
  "- Preserve exact `SectionMetadata.*` except `SectionMetadata.name`.",
  "- Preserve decisions `ApprovedPlan`.",
  "",
  "If mode is summary-refresh:",
  "- Current artifact: Section Metadata.",
  "- Own only {`SectionMetadata.name`, `SectionMetadata.description`}.",
  "- Preserve exact `SectionMetadata.*` except `SectionMetadata.name`, `SectionMetadata.description`.",
  "- Preserve decisions `ApprovedStructure`.",
  "- Do not modify {`SectionMetadata.taxonomy`, `SectionMetadata.flags`}.",
  "",
  "## Inputs",
  "",
  "### Current Handoff",
  "",
  "- Source: Prompt",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "Use the host-provided handoff facts that say which metadata edit mode is active.",
  "",
  "### Approved Plan",
  "",
  "- Source: File",
  "- Path: `unit_root/_authoring/APPROVED_PLAN.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "### Approved Structure",
  "",
  "- Source: File",
  "- Path: `unit_root/_authoring/APPROVED_STRUCTURE.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "## Outputs",
  "",
  "### Section Metadata",
  "",
  "- Target: File",
  "- Path: `unit_root/_authoring/section_metadata.json`",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "### Coordination Handoff",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
  "",
  "#### Current Artifact",
  "",
  "Name the one artifact that is current now.",
  "",
  "#### Trust Surface",
  "",
  "- Current Artifact",
  "",
  "#### Standalone Read",
  "",
  "A downstream owner must be able to read this output alone and know which artifact is current now.",
]

[[cases]]
name = "owned paths must stay addressable"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_OWN_PATH_NOT_ADDRESSABLE.prompt"
agent = "InvalidOwnPathNotAddressable"
exception_type = "CompileError"
error_code = "E352"
message_contains = [
  "Owned scope target is unknown",
  "MissingArtifact",
]

[[cases]]
name = "owned paths must stay rooted in the current artifact"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_OWN_PATH_NOT_ROOTED_IN_CURRENT_ARTIFACT.prompt"
agent = "InvalidOwnPathNotRootedInCurrentArtifact"
exception_type = "CompileError"
error_code = "E351"
message_contains = [
  "Owned scope is outside the current artifact",
  "PrimaryManifest.title",
]

[[cases]]
name = "exact preservation cannot overlap owned scope without an explicit except"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_OWN_AND_EXACT_PRESERVE_OVERLAP.prompt"
agent = "InvalidOwnAndExactPreserveOverlap"
exception_type = "CompileError"
error_code = "E353"
message_contains = [
  "Owned scope overlaps exact preservation",
]

[[cases]]
name = "owned and forbidden scope cannot overlap"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_OWN_AND_FORBID_OVERLAP.prompt"
agent = "InvalidOwnAndForbidOverlap"
exception_type = "CompileError"
error_code = "E354"
message_contains = [
  "Owned scope overlaps forbidden scope",
]
````

## File: examples/36_invalidation_and_rebuild/build_ref/blocked_section_review_demo/AGENTS.md
````markdown
Do not keep reviewing against invalidated downstream truth.

## Blocked Section Review

This pass runs only when section review invalidated.

There is no current artifact for this turn.

Stop: Section Review is invalidated until rebuild work completes.

Route the same issue back to RoutingOwner until review is rebuilt.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether structure changed, whether Section Review is invalidated, and whether rebuild work is requested.

## Outputs

### Blocked Review Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Invalidations

Name any artifacts that are still no longer current.

#### Trust Surface

- Invalidations

#### Standalone Read

A downstream owner must be able to read this output alone and know what is no longer current.
````

## File: examples/36_invalidation_and_rebuild/build_ref/rebuild_section_review_demo/AGENTS.md
````markdown
Rebuild invalidated review work and reissue it as current truth.

## Rebuild Section Review

This pass runs only when rebuild requested.

Current artifact: Section Review.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether structure changed, whether Section Review is invalidated, and whether rebuild work is requested.

## Outputs

### Section Review

- Target: File
- Path: `unit_root/_authoring/SECTION_REVIEW.md`
- Shape: Markdown Document
- Requirement: Required

### Rebuild Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Trust Surface

- Current Artifact

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now.
````

## File: examples/36_invalidation_and_rebuild/build_ref/structure_change_demo/AGENTS.md
````markdown
Invalidate downstream review when structure changes.

## Structure Change

This pass runs only when structure changed.

Current artifact: Section Metadata.

Section Review is no longer current.

Stop: Structure moved; downstream review is no longer current.

Route the same issue back to RoutingOwner for rebuild.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether structure changed, whether Section Review is invalidated, and whether rebuild work is requested.

## Outputs

### Section Metadata

- Target: File
- Path: `unit_root/_authoring/section_metadata.json`
- Shape: Json Object
- Requirement: Required

### Invalidation Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Invalidations

Name any artifacts that are no longer current.

#### Trust Surface

- Current Artifact
- Invalidations

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now and what is no longer current.
````

## File: examples/36_invalidation_and_rebuild/ref/blocked_section_review_demo/AGENTS.md
````markdown
Do not keep reviewing against invalidated downstream truth.

## Blocked Section Review

This pass runs only when section review invalidated.

There is no current artifact for this turn.

Stop: Section Review is invalidated until rebuild work completes.

Route the same issue back to RoutingOwner until review is rebuilt.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether structure changed, whether Section Review is invalidated, and whether rebuild work is requested.

## Outputs

### Blocked Review Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Invalidations

Name any artifacts that are still no longer current.

#### Trust Surface

- Invalidations

#### Standalone Read

A downstream owner must be able to read this output alone and know what is no longer current.
````

## File: examples/36_invalidation_and_rebuild/ref/rebuild_section_review_demo/AGENTS.md
````markdown
Rebuild invalidated review work and reissue it as current truth.

## Rebuild Section Review

This pass runs only when rebuild requested.

Current artifact: Section Review.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether structure changed, whether Section Review is invalidated, and whether rebuild work is requested.

## Outputs

### Section Review

- Target: File
- Path: `unit_root/_authoring/SECTION_REVIEW.md`
- Shape: Markdown Document
- Requirement: Required

### Rebuild Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Trust Surface

- Current Artifact

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now.
````

## File: examples/36_invalidation_and_rebuild/ref/structure_change_demo/AGENTS.md
````markdown
Invalidate downstream review when structure changes.

## Structure Change

This pass runs only when structure changed.

Current artifact: Section Metadata.

Section Review is no longer current.

Stop: Structure moved; downstream review is no longer current.

Route the same issue back to RoutingOwner for rebuild.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether structure changed, whether Section Review is invalidated, and whether rebuild work is requested.

## Outputs

### Section Metadata

- Target: File
- Path: `unit_root/_authoring/section_metadata.json`
- Shape: Json Object
- Requirement: Required

### Invalidation Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Invalidations

Name any artifacts that are no longer current.

#### Trust Surface

- Current Artifact
- Invalidations

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now and what is no longer current.
````

## File: examples/36_invalidation_and_rebuild/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "invalidation can revoke portable currentness after structure changes"
status = "active"
kind = "render_contract"
agent = "StructureChangeDemo"
assertion = "exact_lines"
approx_ref = "ref/structure_change_demo/AGENTS.md"
expected_lines = [
  "Invalidate downstream review when structure changes.",
  "",
  "## Structure Change",
  "",
  "This pass runs only when structure changed.",
  "",
  "Current artifact: Section Metadata.",
  "",
  "Section Review is no longer current.",
  "",
  "Stop: Structure moved; downstream review is no longer current.",
  "",
  "Route the same issue back to RoutingOwner for rebuild.",
  "",
  "## Inputs",
  "",
  "### Current Handoff",
  "",
  "- Source: Prompt",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "Use the host-provided handoff facts that say whether structure changed, whether Section Review is invalidated, and whether rebuild work is requested.",
  "",
  "## Outputs",
  "",
  "### Section Metadata",
  "",
  "- Target: File",
  "- Path: `unit_root/_authoring/section_metadata.json`",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "### Invalidation Handoff",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
  "",
  "#### Current Artifact",
  "",
  "Name the one artifact that is current now.",
  "",
  "#### Invalidations",
  "",
  "Name any artifacts that are no longer current.",
  "",
  "#### Trust Surface",
  "",
  "- Current Artifact",
  "- Invalidations",
  "",
  "#### Standalone Read",
  "",
  "A downstream owner must be able to read this output alone and know what is current now and what is no longer current.",
]

[[cases]]
name = "downstream review stays blocked after invalidation"
status = "active"
kind = "render_contract"
agent = "BlockedSectionReviewDemo"
assertion = "exact_lines"
approx_ref = "ref/blocked_section_review_demo/AGENTS.md"
expected_lines = [
  "Do not keep reviewing against invalidated downstream truth.",
  "",
  "## Blocked Section Review",
  "",
  "This pass runs only when section review invalidated.",
  "",
  "There is no current artifact for this turn.",
  "",
  "Stop: Section Review is invalidated until rebuild work completes.",
  "",
  "Route the same issue back to RoutingOwner until review is rebuilt.",
  "",
  "## Inputs",
  "",
  "### Current Handoff",
  "",
  "- Source: Prompt",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "Use the host-provided handoff facts that say whether structure changed, whether Section Review is invalidated, and whether rebuild work is requested.",
  "",
  "## Outputs",
  "",
  "### Blocked Review Handoff",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
  "",
  "#### Invalidations",
  "",
  "Name any artifacts that are still no longer current.",
  "",
  "#### Trust Surface",
  "",
  "- Invalidations",
  "",
  "#### Standalone Read",
  "",
  "A downstream owner must be able to read this output alone and know what is no longer current.",
]

[[cases]]
name = "rebuild can reissue currentness after invalidation"
status = "active"
kind = "render_contract"
agent = "RebuildSectionReviewDemo"
assertion = "exact_lines"
approx_ref = "ref/rebuild_section_review_demo/AGENTS.md"
expected_lines = [
  "Rebuild invalidated review work and reissue it as current truth.",
  "",
  "## Rebuild Section Review",
  "",
  "This pass runs only when rebuild requested.",
  "",
  "Current artifact: Section Review.",
  "",
  "## Inputs",
  "",
  "### Current Handoff",
  "",
  "- Source: Prompt",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "Use the host-provided handoff facts that say whether structure changed, whether Section Review is invalidated, and whether rebuild work is requested.",
  "",
  "## Outputs",
  "",
  "### Section Review",
  "",
  "- Target: File",
  "- Path: `unit_root/_authoring/SECTION_REVIEW.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "### Rebuild Handoff",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
  "",
  "#### Current Artifact",
  "",
  "Name the one artifact that is current now.",
  "",
  "#### Trust Surface",
  "",
  "- Current Artifact",
  "",
  "#### Standalone Read",
  "",
  "A downstream owner must be able to read this output alone and know what is current now.",
]

[[cases]]
name = "invalidation and rebuild build-contract proof stays checked in"
status = "active"
kind = "build_contract"
build_target = "example_36_invalidation_and_rebuild"

[[cases]]
name = "invalidate statements require explicit carriers"
status = "active"
kind = "parse_fail"
prompt = "prompts/INVALID_INVALIDATION_WITHOUT_VIA.prompt"
exception_type = "ParseError"
error_code = "E133"
message_contains = [
  "Missing `via` carrier",
]

[[cases]]
name = "invalidation carriers must be trusted downstream"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_INVALIDATION_FIELD_NOT_IN_TRUST_SURFACE.prompt"
agent = "InvalidInvalidationFieldNotInTrustSurface"
exception_type = "CompileError"
error_code = "E372"
message_contains = [
  "Invalidation carrier field missing from trust surface",
  "invalidations",
]

[[cases]]
name = "the current artifact cannot be invalidated in the same active branch"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_CURRENT_ARTIFACT_AND_INVALIDATION_SAME_TARGET.prompt"
agent = "InvalidCurrentArtifactAndInvalidationSameTarget"
exception_type = "CompileError"
error_code = "E371"
message_contains = [
  "Current artifact invalidated in same branch",
]
````

## File: examples/37_law_reuse_and_patching/ref/base_metadata_polish_demo/AGENTS.md
````markdown
Keep reusable law subsections explicit in the base workflow.

## Base Metadata Polish

Current artifact: Section Metadata.

Accepted Peer Set is comparison-only support.

If unclear(CurrentHandoff.preserve_basis):
- Stop: Preserve basis is unclear.
- Route the same issue back to RoutingOwner.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether the preserve basis remains clear, whether this pass is a rewrite, and whether structure changed.

### Accepted Peer Set

- Source: File
- Path: `catalog/accepted_peers.json`
- Shape: Json Object
- Requirement: Advisory

## Outputs

### Section Metadata

- Target: File
- Path: `unit_root/_authoring/section_metadata.json`
- Shape: Json Object
- Requirement: Required

### Base Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Comparison Basis

Name any comparison-only artifacts used in this pass.

#### Trust Surface

- Current Artifact
- Comparison Basis

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now and what was comparison-only.
````

## File: examples/37_law_reuse_and_patching/ref/rewrite_aware_metadata_polish_demo/AGENTS.md
````markdown
Patch inherited law explicitly and add rewrite-only evidence rules.

## Rewrite-Aware Metadata Polish

If unclear(CurrentHandoff.preserve_basis):
- Stop: Preserve basis is unclear.
- Route the same issue back to RoutingOwner.

Current artifact: Section Metadata.

Accepted Peer Set is comparison-only support.

When CurrentHandoff.rewrite_regime is rewrite, ignore `SectionMetadata.description` for rewrite evidence.

If structure changed:
- Section Review is no longer current.
- Stop: Structure changed; downstream review is no longer current.
- Route the same issue back to RoutingOwner.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether the preserve basis remains clear, whether this pass is a rewrite, and whether structure changed.

### Accepted Peer Set

- Source: File
- Path: `catalog/accepted_peers.json`
- Shape: Json Object
- Requirement: Advisory

## Outputs

### Section Metadata

- Target: File
- Path: `unit_root/_authoring/section_metadata.json`
- Shape: Json Object
- Requirement: Required

### Rewrite-Aware Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Comparison Basis

Name any comparison-only artifacts used in this pass.

#### Rewrite Evidence Exclusions

Name any fields whose old values do not count as rewrite evidence.

#### Invalidations

Name any artifacts that are no longer current.

#### Trust Surface

- Current Artifact
- Comparison Basis
- Rewrite Evidence Exclusions on rewrite passes
- Invalidations when structure changed

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now, what was comparison-only, what old wording does not count as rewrite evidence on rewrite passes, and what is no longer current when structure changed.
````

## File: examples/37_law_reuse_and_patching/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "base workflows can name reusable law subsections"
status = "active"
kind = "render_contract"
agent = "BaseMetadataPolishDemo"
assertion = "exact_lines"
approx_ref = "ref/base_metadata_polish_demo/AGENTS.md"
expected_lines = [
  "Keep reusable law subsections explicit in the base workflow.",
  "",
  "## Base Metadata Polish",
  "",
  "Current artifact: Section Metadata.",
  "",
  "Accepted Peer Set is comparison-only support.",
  "",
  "If unclear(CurrentHandoff.preserve_basis):",
  "- Stop: Preserve basis is unclear.",
  "- Route the same issue back to RoutingOwner.",
  "",
  "## Inputs",
  "",
  "### Current Handoff",
  "",
  "- Source: Prompt",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "Use the host-provided handoff facts that say whether the preserve basis remains clear, whether this pass is a rewrite, and whether structure changed.",
  "",
  "### Accepted Peer Set",
  "",
  "- Source: File",
  "- Path: `catalog/accepted_peers.json`",
  "- Shape: Json Object",
  "- Requirement: Advisory",
  "",
  "## Outputs",
  "",
  "### Section Metadata",
  "",
  "- Target: File",
  "- Path: `unit_root/_authoring/section_metadata.json`",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "### Base Coordination Handoff",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
  "",
  "#### Current Artifact",
  "",
  "Name the one artifact that is current now.",
  "",
  "#### Comparison Basis",
  "",
  "Name any comparison-only artifacts used in this pass.",
  "",
  "#### Trust Surface",
  "",
  "- Current Artifact",
  "- Comparison Basis",
  "",
  "#### Standalone Read",
  "",
  "A downstream owner must be able to read this output alone and know what is current now and what was comparison-only.",
]

[[cases]]
name = "child workflows can inherit and override named law subsections"
status = "active"
kind = "render_contract"
agent = "RewriteAwareMetadataPolishDemo"
assertion = "exact_lines"
approx_ref = "ref/rewrite_aware_metadata_polish_demo/AGENTS.md"
expected_lines = [
  "Patch inherited law explicitly and add rewrite-only evidence rules.",
  "",
  "## Rewrite-Aware Metadata Polish",
  "",
  "If unclear(CurrentHandoff.preserve_basis):",
  "- Stop: Preserve basis is unclear.",
  "- Route the same issue back to RoutingOwner.",
  "",
  "Current artifact: Section Metadata.",
  "",
  "Accepted Peer Set is comparison-only support.",
  "",
  "When CurrentHandoff.rewrite_regime is rewrite, ignore `SectionMetadata.description` for rewrite evidence.",
  "",
  "If structure changed:",
  "- Section Review is no longer current.",
  "- Stop: Structure changed; downstream review is no longer current.",
  "- Route the same issue back to RoutingOwner.",
  "",
  "## Inputs",
  "",
  "### Current Handoff",
  "",
  "- Source: Prompt",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "Use the host-provided handoff facts that say whether the preserve basis remains clear, whether this pass is a rewrite, and whether structure changed.",
  "",
  "### Accepted Peer Set",
  "",
  "- Source: File",
  "- Path: `catalog/accepted_peers.json`",
  "- Shape: Json Object",
  "- Requirement: Advisory",
  "",
  "## Outputs",
  "",
  "### Section Metadata",
  "",
  "- Target: File",
  "- Path: `unit_root/_authoring/section_metadata.json`",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "### Rewrite-Aware Coordination Handoff",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
  "",
  "#### Current Artifact",
  "",
  "Name the one artifact that is current now.",
  "",
  "#### Comparison Basis",
  "",
  "Name any comparison-only artifacts used in this pass.",
  "",
  "#### Rewrite Evidence Exclusions",
  "",
  "Name any fields whose old values do not count as rewrite evidence.",
  "",
  "#### Invalidations",
  "",
  "Name any artifacts that are no longer current.",
  "",
  "#### Trust Surface",
  "",
  "- Current Artifact",
  "- Comparison Basis",
  "- Rewrite Evidence Exclusions on rewrite passes",
  "- Invalidations when structure changed",
  "",
  "#### Standalone Read",
  "",
  "A downstream owner must be able to read this output alone and know what is current now, what was comparison-only, what old wording does not count as rewrite evidence on rewrite passes, and what is no longer current when structure changed.",
]

[[cases]]
name = "inherited law blocks must account for every named parent subsection"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_MISSING_INHERITED_LAW_SECTION.prompt"
agent = "InvalidMissingInheritedLawSection"
exception_type = "CompileError"
error_code = "E383"
message_contains = [
  "Missing inherited law subsection",
  "currentness",
]

[[cases]]
name = "inherited law blocks cannot account for one subsection twice"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_DUPLICATE_INHERITED_LAW_SECTION.prompt"
agent = "InvalidDuplicateInheritedLawSection"
exception_type = "CompileError"
error_code = "E382"
message_contains = [
  "Duplicate inherited law subsection",
  "currentness",
]

[[cases]]
name = "override cannot target unknown law subsections"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_OVERRIDE_UNKNOWN_LAW_SECTION.prompt"
agent = "InvalidOverrideUnknownLawSection"
exception_type = "CompileError"
error_code = "E384"
message_contains = [
  "Cannot override undefined law subsection",
  "missing_section",
]

[[cases]]
name = "inherited law blocks cannot mix bare statements with patch entries"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_BARE_LAW_STATEMENT_IN_INHERITED_CHILD.prompt"
agent = "InvalidBareLawStatementInInheritedChild"
exception_type = "CompileError"
error_code = "E381"
message_contains = [
  "Inherited law requires named sections",
]
````

## File: examples/38_metadata_polish_capstone/ref/metadata_polish_capstone_demo/AGENTS.md
````markdown
Handle the last narrow wording pass after structure is already locked.

## Metadata Polish

This pass runs only when metadata polish is owed now.

Active mode: manifest-title.

Current artifact: Primary Manifest.

Must CurrentHandoff.preserve_basis == ApprovedPlan.

Own only `PrimaryManifest.title`.

Preserve exact `PrimaryManifest.*` except `PrimaryManifest.title`.

Preserve decisions `ApprovedPlan`.

Accepted Peer Set is comparison-only support.

If unclear(pass_mode, CurrentHandoff.preserve_basis):
- Stop: Mode or preserve basis is unclear.
- Route the same issue back to RoutingOwner.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether metadata polish is owed, which mode is active, which preserve basis remains authoritative, whether peer comparison is in play, whether this pass is a rewrite, and whether structure changed.

### Approved Plan

- Source: File
- Path: `unit_root/_authoring/APPROVED_PLAN.md`
- Shape: Markdown Document
- Requirement: Required

### Approved Structure

- Source: File
- Path: `unit_root/_authoring/APPROVED_STRUCTURE.md`
- Shape: Markdown Document
- Requirement: Required

### Accepted Peer Set

- Source: File
- Path: `catalog/accepted_peers.json`
- Shape: Json Object
- Requirement: Advisory

## Outputs

### Primary Manifest

- Target: File
- Path: `unit_root/_authoring/primary_manifest.json`
- Shape: Json Object
- Requirement: Required

### Base Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Active Mode

Name the one active mode for this pass.

#### Preserve Basis

Name the upstream declaration whose decisions remain authoritative.

#### Comparison Basis

Name any comparison-only artifacts used in this pass.

#### Trust Surface

- Current Artifact
- Active Mode
- Preserve Basis
- Comparison Basis when peer comparison is used

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now, which mode is active, and why that preserve basis remains authoritative.
````

## File: examples/38_metadata_polish_capstone/ref/rewrite_aware_metadata_polish_capstone_demo/AGENTS.md
````markdown
Handle the last narrow wording pass after structure is already locked.

## Metadata Polish

This pass runs only when metadata polish is owed now.

Active mode: section-summary.

Current artifact: Section Metadata.

Must CurrentHandoff.preserve_basis == ApprovedStructure.

Own only {`SectionMetadata.name`, `SectionMetadata.description`}.

Preserve exact `SectionMetadata.*` except `SectionMetadata.name`, `SectionMetadata.description`.

Preserve decisions `ApprovedStructure`.

Do not modify {`SectionMetadata.taxonomy`, `SectionMetadata.flags`}.

Accepted Peer Set is comparison-only support.

When pass_mode is manifest-title and CurrentHandoff.rewrite_regime is rewrite, ignore `PrimaryManifest.title` for rewrite evidence.

When pass_mode is section-summary and CurrentHandoff.rewrite_regime is rewrite, ignore {`SectionMetadata.name`, `SectionMetadata.description`} for rewrite evidence.

If structure changed:
- Section Review is no longer current.
- Stop: Structure moved; downstream review is no longer current.
- Route the same issue back to RoutingOwner for rebuild.

If unclear(pass_mode, CurrentHandoff.preserve_basis):
- Stop: Mode or preserve basis is unclear.
- Route the same issue back to RoutingOwner.

## Inputs

### Current Handoff

- Source: Prompt
- Shape: Json Object
- Requirement: Required

Use the host-provided handoff facts that say whether metadata polish is owed, which mode is active, which preserve basis remains authoritative, whether peer comparison is in play, whether this pass is a rewrite, and whether structure changed.

### Approved Plan

- Source: File
- Path: `unit_root/_authoring/APPROVED_PLAN.md`
- Shape: Markdown Document
- Requirement: Required

### Approved Structure

- Source: File
- Path: `unit_root/_authoring/APPROVED_STRUCTURE.md`
- Shape: Markdown Document
- Requirement: Required

### Accepted Peer Set

- Source: File
- Path: `catalog/accepted_peers.json`
- Shape: Json Object
- Requirement: Advisory

## Outputs

### Section Metadata

- Target: File
- Path: `unit_root/_authoring/section_metadata.json`
- Shape: Json Object
- Requirement: Required

### Rewrite-Aware Coordination Handoff

- Target: Turn Response
- Shape: Comment
- Requirement: Required

#### Current Artifact

Name the one artifact that is current now.

#### Active Mode

Name the one active mode for this pass.

#### Preserve Basis

Name the upstream declaration whose decisions remain authoritative.

#### Comparison Basis

Name any comparison-only artifacts used in this pass.

#### Rewrite Evidence Exclusions

Name any fields whose old values do not count as rewrite evidence.

#### Invalidations

Name any artifacts that are no longer current.

#### Trust Surface

- Current Artifact
- Active Mode
- Preserve Basis
- Comparison Basis when peer comparison is used
- Rewrite Evidence Exclusions on rewrite passes
- Invalidations when structure changed

#### Standalone Read

A downstream owner must be able to read this output alone and know what is current now, which mode is active, why that preserve basis remains authoritative, what old wording does not count as rewrite evidence on rewrite passes, and what is no longer current when structure changed.
````

## File: examples/38_metadata_polish_capstone/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "metadata polish capstone integrates currentness scope preservation and trust carriers"
status = "active"
kind = "render_contract"
agent = "MetadataPolishCapstoneDemo"
assertion = "exact_lines"
approx_ref = "ref/metadata_polish_capstone_demo/AGENTS.md"
expected_lines = [
  "Handle the last narrow wording pass after structure is already locked.",
  "",
  "## Metadata Polish",
  "",
  "This pass runs only when metadata polish is owed now.",
  "",
  "Active mode: manifest-title.",
  "",
  "Current artifact: Primary Manifest.",
  "",
  "Must CurrentHandoff.preserve_basis == ApprovedPlan.",
  "",
  "Own only `PrimaryManifest.title`.",
  "",
  "Preserve exact `PrimaryManifest.*` except `PrimaryManifest.title`.",
  "",
  "Preserve decisions `ApprovedPlan`.",
  "",
  "Accepted Peer Set is comparison-only support.",
  "",
  "If unclear(pass_mode, CurrentHandoff.preserve_basis):",
  "- Stop: Mode or preserve basis is unclear.",
  "- Route the same issue back to RoutingOwner.",
  "",
  "## Inputs",
  "",
  "### Current Handoff",
  "",
  "- Source: Prompt",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "Use the host-provided handoff facts that say whether metadata polish is owed, which mode is active, which preserve basis remains authoritative, whether peer comparison is in play, whether this pass is a rewrite, and whether structure changed.",
  "",
  "### Approved Plan",
  "",
  "- Source: File",
  "- Path: `unit_root/_authoring/APPROVED_PLAN.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "### Approved Structure",
  "",
  "- Source: File",
  "- Path: `unit_root/_authoring/APPROVED_STRUCTURE.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "### Accepted Peer Set",
  "",
  "- Source: File",
  "- Path: `catalog/accepted_peers.json`",
  "- Shape: Json Object",
  "- Requirement: Advisory",
  "",
  "## Outputs",
  "",
  "### Primary Manifest",
  "",
  "- Target: File",
  "- Path: `unit_root/_authoring/primary_manifest.json`",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "### Base Coordination Handoff",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
  "",
  "#### Current Artifact",
  "",
  "Name the one artifact that is current now.",
  "",
  "#### Active Mode",
  "",
  "Name the one active mode for this pass.",
  "",
  "#### Preserve Basis",
  "",
  "Name the upstream declaration whose decisions remain authoritative.",
  "",
  "#### Comparison Basis",
  "",
  "Name any comparison-only artifacts used in this pass.",
  "",
  "#### Trust Surface",
  "",
  "- Current Artifact",
  "- Active Mode",
  "- Preserve Basis",
  "- Comparison Basis when peer comparison is used",
  "",
  "#### Standalone Read",
  "",
  "A downstream owner must be able to read this output alone and know what is current now, which mode is active, and why that preserve basis remains authoritative.",
]

[[cases]]
name = "rewrite-aware metadata polish capstone adds rewrite exclusions invalidation and reroute"
status = "active"
kind = "render_contract"
agent = "RewriteAwareMetadataPolishCapstoneDemo"
assertion = "exact_lines"
approx_ref = "ref/rewrite_aware_metadata_polish_capstone_demo/AGENTS.md"
expected_lines = [
  "Handle the last narrow wording pass after structure is already locked.",
  "",
  "## Metadata Polish",
  "",
  "This pass runs only when metadata polish is owed now.",
  "",
  "Active mode: section-summary.",
  "",
  "Current artifact: Section Metadata.",
  "",
  "Must CurrentHandoff.preserve_basis == ApprovedStructure.",
  "",
  "Own only {`SectionMetadata.name`, `SectionMetadata.description`}.",
  "",
  "Preserve exact `SectionMetadata.*` except `SectionMetadata.name`, `SectionMetadata.description`.",
  "",
  "Preserve decisions `ApprovedStructure`.",
  "",
  "Do not modify {`SectionMetadata.taxonomy`, `SectionMetadata.flags`}.",
  "",
  "Accepted Peer Set is comparison-only support.",
  "",
  "When pass_mode is manifest-title and CurrentHandoff.rewrite_regime is rewrite, ignore `PrimaryManifest.title` for rewrite evidence.",
  "",
  "When pass_mode is section-summary and CurrentHandoff.rewrite_regime is rewrite, ignore {`SectionMetadata.name`, `SectionMetadata.description`} for rewrite evidence.",
  "",
  "If structure changed:",
  "- Section Review is no longer current.",
  "- Stop: Structure moved; downstream review is no longer current.",
  "- Route the same issue back to RoutingOwner for rebuild.",
  "",
  "If unclear(pass_mode, CurrentHandoff.preserve_basis):",
  "- Stop: Mode or preserve basis is unclear.",
  "- Route the same issue back to RoutingOwner.",
  "",
  "## Inputs",
  "",
  "### Current Handoff",
  "",
  "- Source: Prompt",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "Use the host-provided handoff facts that say whether metadata polish is owed, which mode is active, which preserve basis remains authoritative, whether peer comparison is in play, whether this pass is a rewrite, and whether structure changed.",
  "",
  "### Approved Plan",
  "",
  "- Source: File",
  "- Path: `unit_root/_authoring/APPROVED_PLAN.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "### Approved Structure",
  "",
  "- Source: File",
  "- Path: `unit_root/_authoring/APPROVED_STRUCTURE.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "### Accepted Peer Set",
  "",
  "- Source: File",
  "- Path: `catalog/accepted_peers.json`",
  "- Shape: Json Object",
  "- Requirement: Advisory",
  "",
  "## Outputs",
  "",
  "### Section Metadata",
  "",
  "- Target: File",
  "- Path: `unit_root/_authoring/section_metadata.json`",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "### Rewrite-Aware Coordination Handoff",
  "",
  "- Target: Turn Response",
  "- Shape: Comment",
  "- Requirement: Required",
  "",
  "#### Current Artifact",
  "",
  "Name the one artifact that is current now.",
  "",
  "#### Active Mode",
  "",
  "Name the one active mode for this pass.",
  "",
  "#### Preserve Basis",
  "",
  "Name the upstream declaration whose decisions remain authoritative.",
  "",
  "#### Comparison Basis",
  "",
  "Name any comparison-only artifacts used in this pass.",
  "",
  "#### Rewrite Evidence Exclusions",
  "",
  "Name any fields whose old values do not count as rewrite evidence.",
  "",
  "#### Invalidations",
  "",
  "Name any artifacts that are no longer current.",
  "",
  "#### Trust Surface",
  "",
  "- Current Artifact",
  "- Active Mode",
  "- Preserve Basis",
  "- Comparison Basis when peer comparison is used",
  "- Rewrite Evidence Exclusions on rewrite passes",
  "- Invalidations when structure changed",
  "",
  "#### Standalone Read",
  "",
  "A downstream owner must be able to read this output alone and know what is current now, which mode is active, why that preserve basis remains authoritative, what old wording does not count as rewrite evidence on rewrite passes, and what is no longer current when structure changed.",
]
````

## File: doctrine/diagnostics.py
````python
from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable

from lark import Token, Tree
from lark.exceptions import (
    UnexpectedCharacters,
    UnexpectedEOF,
    UnexpectedInput,
    UnexpectedToken,
    VisitError,
)


@dataclass(slots=True, frozen=True)
class DiagnosticLocation:
    path: Path | None = None
    line: int | None = None
    column: int | None = None


@dataclass(slots=True, frozen=True)
class DiagnosticExcerptLine:
    number: int
    text: str


@dataclass(slots=True, frozen=True)
class DiagnosticTraceFrame:
    label: str
    location: DiagnosticLocation | None = None


@dataclass(slots=True, frozen=True)
class DoctrineDiagnostic:
    code: str
    stage: str
    summary: str
    detail: str | None = None
    location: DiagnosticLocation | None = None
    excerpt: tuple[DiagnosticExcerptLine, ...] = ()
    caret_column: int | None = None
    hints: tuple[str, ...] = ()
    trace: tuple[DiagnosticTraceFrame, ...] = ()
    cause: str | None = None


class TransformParseFailure(ValueError):
    def __init__(
        self,
        detail: str,
        *,
        code: str = "E199",
        summary: str = "Parse failure",
        hints: tuple[str, ...] = (),
    ) -> None:
        super().__init__(detail)
        self.code = code
        self.summary = summary
        self.hints = hints


def diagnostic_to_dict(error_or_diagnostic: DoctrineError | DoctrineDiagnostic) -> dict[str, Any]:
    diagnostic = _coerce_diagnostic(error_or_diagnostic)
    return _json_safe_value(diagnostic)


def format_diagnostic(error_or_diagnostic: DoctrineError | DoctrineDiagnostic) -> str:
    diagnostic = _coerce_diagnostic(error_or_diagnostic)
    lines = [f"{diagnostic.code} {diagnostic.stage} error: {diagnostic.summary}"]

    if diagnostic.location is not None:
        lines.extend(["", "Location:", f"- {_format_location(diagnostic.location)}"])

    if diagnostic.detail:
        lines.extend(["", "Detail:"])
        lines.extend(_format_block(diagnostic.detail))

    if diagnostic.excerpt:
        lines.extend(["", "Source:"])
        lines.extend(
            _format_excerpt(
                diagnostic.excerpt,
                highlight_line=diagnostic.location.line if diagnostic.location is not None else None,
                caret_column=diagnostic.caret_column,
            )
        )

    if diagnostic.trace:
        lines.extend(["", "Trace:"])
        for frame in diagnostic.trace:
            location = ""
            if frame.location is not None:
                location = f" ({_format_location(frame.location)})"
            lines.append(f"- {frame.label}{location}")

    if diagnostic.hints:
        label = "Hint:" if len(diagnostic.hints) == 1 else "Hints:"
        lines.extend(["", label])
        for hint in diagnostic.hints:
            lines.extend(_format_block(hint))

    if diagnostic.cause:
        lines.extend(["", "Cause:"])
        lines.extend(_format_block(diagnostic.cause))

    return "\n".join(lines)


class DoctrineError(RuntimeError):
    stage = "runtime"
    fallback_code = "E999"
    fallback_summary = "Unexpected Doctrine error"

    def __init__(
        self,
        message: str | None = None,
        *,
        diagnostic: DoctrineDiagnostic | None = None,
    ) -> None:
        if diagnostic is None:
            diagnostic = self._diagnostic_from_message(message or self.fallback_summary)
        self.diagnostic = diagnostic
        super().__init__(format_diagnostic(diagnostic))

    @property
    def code(self) -> str:
        return self.diagnostic.code

    @property
    def location(self) -> DiagnosticLocation | None:
        return self.diagnostic.location

    def __str__(self) -> str:
        return format_diagnostic(self.diagnostic)

    @classmethod
    def from_parts(
        cls,
        *,
        code: str,
        summary: str,
        detail: str | None = None,
        location: DiagnosticLocation | None = None,
        excerpt: tuple[DiagnosticExcerptLine, ...] = (),
        caret_column: int | None = None,
        hints: tuple[str, ...] = (),
        trace: tuple[DiagnosticTraceFrame, ...] = (),
        cause: str | None = None,
    ) -> DoctrineError:
        return cls(
            diagnostic=DoctrineDiagnostic(
                code=code,
                stage=cls.stage,
                summary=summary,
                detail=detail,
                location=location,
                excerpt=excerpt,
                caret_column=caret_column,
                hints=hints,
                trace=trace,
                cause=cause,
            )
        )

    def prepend_trace(
        self,
        label: str,
        *,
        location: DiagnosticLocation | None = None,
    ) -> DoctrineError:
        self.diagnostic = replace(
            self.diagnostic,
            trace=(DiagnosticTraceFrame(label=label, location=location), *self.diagnostic.trace),
        )
        self.args = (format_diagnostic(self.diagnostic),)
        return self

    def ensure_location(
        self,
        *,
        path: Path | None = None,
        line: int | None = None,
        column: int | None = None,
    ) -> DoctrineError:
        if self.diagnostic.location is not None:
            return self
        self.diagnostic = replace(
            self.diagnostic,
            location=DiagnosticLocation(path=path, line=line, column=column),
        )
        self.args = (format_diagnostic(self.diagnostic),)
        return self

    def _diagnostic_from_message(self, message: str) -> DoctrineDiagnostic:
        return DoctrineDiagnostic(
            code=self.fallback_code,
            stage=self.stage,
            summary=self.fallback_summary,
            detail=message,
        )


class ParseError(DoctrineError):
    stage = "parse"
    fallback_code = "E199"
    fallback_summary = "Parse failure"

    @classmethod
    def from_lark(
        cls,
        *,
        source: str,
        path: Path | None,
        exc: UnexpectedInput,
    ) -> ParseError:
        line = getattr(exc, "line", None)
        column = getattr(exc, "column", None)
        location = DiagnosticLocation(path=path, line=line, column=column)
        excerpt, caret_column = _build_excerpt(source, line=line, column=column)

        if isinstance(exc, UnexpectedCharacters):
            summary = "Unexpected character"
            code = "E102"
            hints = (
                f"Remove or replace the unsupported character near column {column}.",
            )
            cause = f"Unexpected character {exc.char!r}."
        elif isinstance(exc, UnexpectedEOF):
            summary = "Unexpected end of file"
            code = "E103"
            hints = ("Finish the current declaration or block before the file ends.",)
            cause = _format_expected_tokens(getattr(exc, "expected", None))
        elif isinstance(exc, UnexpectedToken):
            code, summary, hints = _classify_unexpected_token(exc)
            cause = _format_unexpected_token_cause(exc)
        else:
            summary = "Unexpected parser input"
            code = "E199"
            hints = ("Check the surrounding syntax and indentation.",)
            cause = str(exc)

        return cls.from_parts(
            code=code,
            summary=summary,
            detail=_format_parse_detail(exc),
            location=location,
            excerpt=excerpt,
            caret_column=caret_column,
            hints=hints,
            cause=cause,
        )

    @classmethod
    def from_transform(
        cls,
        *,
        source: str,
        path: Path | None,
        exc: VisitError,
    ) -> ParseError:
        line, column = _extract_tree_position(exc.obj)
        location = DiagnosticLocation(path=path, line=line, column=column)
        excerpt, caret_column = _build_excerpt(source, line=line, column=column)
        detail = str(exc.orig_exc)
        code = "E105"
        summary = "Invalid authored slot body"
        hints = (
            "Do not attach an inline body to a referenced authored workflow slot.",
        )
        if isinstance(exc.orig_exc, TransformParseFailure):
            code = exc.orig_exc.code
            summary = exc.orig_exc.summary
            hints = exc.orig_exc.hints
        return cls.from_parts(
            code=code,
            summary=summary,
            detail=detail,
            location=location,
            excerpt=excerpt,
            caret_column=caret_column,
            hints=hints,
            cause=f"{type(exc.orig_exc).__name__}: {detail}",
        )


class CompileError(DoctrineError):
    stage = "compile"
    fallback_code = "E299"
    fallback_summary = "Compile failure"

    def _diagnostic_from_message(self, message: str) -> DoctrineDiagnostic:
        return _compile_diagnostic_from_message(message)


class EmitError(DoctrineError):
    stage = "emit"
    fallback_code = "E599"
    fallback_summary = "Emit failure"

    def _diagnostic_from_message(self, message: str) -> DoctrineDiagnostic:
        return _emit_diagnostic_from_message(message)

    @classmethod
    def from_toml_decode(
        cls,
        *,
        path: Path,
        exc: tomllib.TOMLDecodeError,
    ) -> EmitError:
        line = getattr(exc, "lineno", None)
        column = getattr(exc, "colno", None)
        if line is None or column is None:
            line, column = _extract_toml_decode_position(
                getattr(exc, "doc", ""),
                getattr(exc, "pos", None),
            )
        location = DiagnosticLocation(path=path.resolve(), line=line, column=column)
        excerpt, caret_column = _build_excerpt(getattr(exc, "doc", ""), line=line, column=column)
        return cls.from_parts(
            code="E506",
            summary="Invalid emit config TOML",
            detail="The emit config file is not valid TOML.",
            location=location,
            excerpt=excerpt,
            caret_column=caret_column,
            hints=("Fix the TOML syntax before running `emit_docs` again.",),
            cause=getattr(exc, "msg", str(exc)),
        )


def _coerce_diagnostic(error_or_diagnostic: DoctrineError | DoctrineDiagnostic) -> DoctrineDiagnostic:
    if isinstance(error_or_diagnostic, DoctrineError):
        return error_or_diagnostic.diagnostic
    return error_or_diagnostic


def _json_safe_value(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, tuple):
        return [_json_safe_value(item) for item in value]
    if isinstance(value, list):
        return [_json_safe_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_safe_value(item) for key, item in value.items()}
    if isinstance(value, DiagnosticLocation):
        return {
            "path": _json_safe_value(value.path),
            "line": value.line,
            "column": value.column,
        }
    if isinstance(value, DiagnosticExcerptLine):
        return {
            "number": value.number,
            "text": value.text,
        }
    if isinstance(value, DiagnosticTraceFrame):
        return {
            "label": value.label,
            "location": _json_safe_value(value.location),
        }
    if isinstance(value, DoctrineDiagnostic):
        return {
            "code": value.code,
            "stage": value.stage,
            "summary": value.summary,
            "detail": value.detail,
            "location": _json_safe_value(value.location),
            "excerpt": _json_safe_value(value.excerpt),
            "caret_column": value.caret_column,
            "hints": _json_safe_value(value.hints),
            "trace": _json_safe_value(value.trace),
            "cause": value.cause,
        }
    return value


def _format_location(location: DiagnosticLocation) -> str:
    path = location.path
    if path is None:
        return "<unknown>"
    rendered = _display_path(path)
    if location.line is None:
        return rendered
    if location.column is None:
        return f"{rendered}:{location.line}"
    return f"{rendered}:{location.line}:{location.column}"


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    cwd = Path.cwd().resolve()
    try:
        return str(resolved.relative_to(cwd))
    except ValueError:
        return str(resolved)


def _format_block(text: str) -> list[str]:
    return [f"- {line}" if index == 0 else f"  {line}" for index, line in enumerate(text.splitlines())]


def _format_excerpt(
    excerpt: tuple[DiagnosticExcerptLine, ...],
    *,
    highlight_line: int | None = None,
    caret_column: int | None,
) -> list[str]:
    number_width = max(len(str(line.number)) for line in excerpt)
    lines: list[str] = []
    for entry in excerpt:
        lines.append(f"  {entry.number:>{number_width}} | {entry.text}")
        if caret_column is not None and highlight_line is not None and entry.number == highlight_line:
            padding = " " * (number_width + 5 + max(caret_column - 1, 0))
            lines.append(f"{padding}^")
    return lines


def _build_excerpt(
    source: str,
    *,
    line: int | None,
    column: int | None,
) -> tuple[tuple[DiagnosticExcerptLine, ...], int | None]:
    if line is None:
        return (), None
    all_lines = source.splitlines()
    if not all_lines:
        return (), column
    start = max(line - 2, 1)
    end = min(line + 1, len(all_lines))
    excerpt = tuple(
        DiagnosticExcerptLine(number=index, text=all_lines[index - 1])
        for index in range(start, end + 1)
    )
    return excerpt, column


def _extract_tree_position(obj: object) -> tuple[int | None, int | None]:
    if isinstance(obj, Token):
        return getattr(obj, "line", None), getattr(obj, "column", None)
    if isinstance(obj, Tree):
        for child in obj.children:
            line, column = _extract_tree_position(child)
            if line is not None:
                return line, column
    return None, None


def _extract_toml_decode_position(
    source: str,
    pos: int | None,
) -> tuple[int | None, int | None]:
    if pos is None:
        return None, None
    bounded_pos = max(0, min(pos, len(source)))
    prefix = source[:bounded_pos]
    line = prefix.count("\n") + 1
    last_newline = prefix.rfind("\n")
    if last_newline == -1:
        column = bounded_pos + 1
    else:
        column = bounded_pos - last_newline
    return line, column


def _classify_unexpected_token(
    exc: UnexpectedToken,
) -> tuple[str, str, tuple[str, ...]]:
    previous = exc.token_history[-1] if exc.token_history else None
    expected = set(exc.expected or ())
    if previous is not None and previous.type == "ROUTE" and exc.token.value == "->":
        return (
            "E131",
            "Missing route label",
            ("Add a quoted route label before `->`.",),
        )
    if "CNAME" in expected and exc.token.type == "_NL":
        return (
            "E132",
            "Missing route target",
            ("Add an explicit agent target after `->`.",),
        )
    if "VIA" in expected:
        return (
            "E133",
            "Missing `via` carrier",
            ("Add `via Output.field` after the current artifact or invalidation target.",),
        )
    token_type = exc.token.type
    if token_type == "_INDENT":
        return (
            "E104",
            "Unexpected indented block",
            ("Indent this block only after a declaration line that opens a nested body.",),
        )
    if token_type == "_DEDENT":
        return (
            "E104",
            "Unexpected dedent",
            ("Keep indentation aligned with the current block structure.",),
        )
    if token_type == "_NL":
        return (
            "E101",
            "Unexpected newline",
            ("Finish the current declaration before starting a new line.",),
        )
    return (
        "E101",
        "Unexpected token",
        ("Check the expected token list and the surrounding punctuation.",),
    )


def _format_unexpected_token_cause(exc: UnexpectedToken) -> str:
    token = exc.token
    token_value = token.value.replace("\n", "\\n")
    parts = [f"Unexpected token `{token.type}` with value `{token_value}`."]
    expected = _format_expected_tokens(exc.expected)
    if expected:
        parts.append(expected)
    return " ".join(parts)


def _format_expected_tokens(expected: set[str] | list[str] | None) -> str | None:
    if not expected:
        return None
    normalized = ", ".join(f"`{token}`" for token in sorted(expected))
    return f"Expected one of: {normalized}."


def _format_parse_detail(exc: UnexpectedInput) -> str:
    if isinstance(exc, UnexpectedToken):
        token_type = exc.token.type
        if token_type == "_NL":
            return "The parser hit a line break where the current grammar still expected more input."
        if token_type == "_INDENT":
            return "The parser entered an indented block that is not valid at this point in the grammar."
        if token_type == "_DEDENT":
            return "The parser left an indented block before the current declaration was complete."
    if isinstance(exc, UnexpectedCharacters):
        return "The parser hit a character that does not belong to any token on this surface."
    if isinstance(exc, UnexpectedEOF):
        return "The file ended before the current declaration or block was complete."
    return "The parser could not match the current source against the shipped grammar."


_COMPILE_PATTERN_BUILDERS: tuple[
    tuple[re.Pattern[str], str, str, Callable[[re.Match[str]], str | None], tuple[str, ...]],
    ...,
] = (
    (
        re.compile(r"^E001 (?P<detail>.+)$"),
        "E001",
        "Cannot override undefined inherited entry",
        lambda match: match.group("detail"),
        (
            "If this entry is new, define it directly instead of using `override`.",
        ),
    ),
    (
        re.compile(r"^E003 (?P<detail>.+)$"),
        "E003",
        "Missing inherited entry",
        lambda match: match.group("detail"),
        (
            "Account for every inherited entry explicitly with `inherit` or `override`.",
        ),
    ),
    (
        re.compile(r"^Missing target agent: (?P<agent>.+)$"),
        "E201",
        "Missing target agent",
        lambda match: f"Target agent `{match.group('agent')}` does not exist in the root prompt file.",
        (),
    ),
    (
        re.compile(r"^Abstract agent does not render: (?P<agent>.+)$"),
        "E202",
        "Abstract agent does not render",
        lambda match: f"Agent `{match.group('agent')}` is marked abstract and cannot render output directly.",
        ("Render a concrete child agent instead.",),
    ),
    (
        re.compile(r"^Duplicate role field in agent (?P<agent>.+)$"),
        "E203",
        "Duplicate role field",
        lambda match: f"Agent `{match.group('agent')}` defines `role` more than once.",
        (),
    ),
    (
        re.compile(r"^Duplicate typed field in agent (?P<agent>[^:]+): (?P<field>.+)$"),
        "E204",
        "Duplicate typed field",
        lambda match: (
            f"Agent `{match.group('agent')}` defines typed field `{match.group('field')}` more than once."
        ),
        (),
    ),
    (
        re.compile(r"^Agent (?P<agent>.+) is outside the shipped subset: (?P<detail>.+)$"),
        "E206",
        "Unsupported agent field order",
        lambda match: (
            f"Agent `{match.group('agent')}` is outside the shipped subset. {match.group('detail')}"
        ),
        (),
    ),
    (
        re.compile(r"^Concrete agent is missing role field: (?P<agent>.+)$"),
        "E205",
        "Concrete agent is missing role field",
        lambda match: f"Concrete agent `{match.group('agent')}` is missing its required `role` field.",
        ("Add a `role` field before the rest of the authored workflow surface.",),
    ),
    (
        re.compile(r"^Unsupported agent field in (?P<agent>[^:]+): (?P<field>.+)$"),
        "E208",
        "Unsupported agent field",
        lambda match: f"Agent `{match.group('agent')}` uses unsupported field type `{match.group('field')}`.",
        (),
    ),
    (
        re.compile(
            r"^E209 Concrete agent is missing abstract authored slots in agent (?P<agent>[^:]+): (?P<slots>.+)$"
        ),
        "E209",
        "Concrete agent is missing abstract authored slots",
        lambda match: (
            f"Concrete agent `{match.group('agent')}` must define abstract authored slots: "
            f"{', '.join(f'`{slot.strip()}`' for slot in match.group('slots').split(','))}."
        ),
        ("Define each missing slot directly with `slot_key: ...`.",),
    ),
    (
        re.compile(
            r"^E210 Abstract authored slot in (?P<label>[^:]+) must be defined directly in agent (?P<agent>[^:]+): (?P<slot>.+)$"
        ),
        "E210",
        "Abstract authored slot must be defined directly",
        lambda match: (
            f"Agent `{match.group('agent')}` cannot satisfy abstract authored slot "
            f"`{match.group('slot')}` from {match.group('label')} with `inherit` or `override`."
        ),
        ("Define the slot directly with `slot_key: ...`.",),
    ),
    (
        re.compile(r"^Cyclic agent inheritance: (?P<detail>.+)$"),
        "E207",
        "Cyclic agent inheritance",
        lambda match: f"Agent inheritance cycle: {match.group('detail')}.",
        (),
    ),
    (
        re.compile(r"^Skill is missing string purpose: (?P<name>.+)$"),
        "E220",
        "Skill is missing string purpose",
        lambda match: f"Skill `{match.group('name')}` is missing a string `purpose` field.",
        (),
    ),
    (
        re.compile(r"^Input is missing typed source: (?P<name>.+)$"),
        "E221",
        "Input is missing typed source",
        lambda match: f"Input `{match.group('name')}` is missing a typed `source` field.",
        (),
    ),
    (
        re.compile(r"^Input is missing shape: (?P<name>.+)$"),
        "E222",
        "Input is missing shape",
        lambda match: f"Input `{match.group('name')}` is missing a `shape` field.",
        (),
    ),
    (
        re.compile(r"^Input is missing requirement: (?P<name>.+)$"),
        "E223",
        "Input is missing requirement",
        lambda match: f"Input `{match.group('name')}` is missing a `requirement` field.",
        (),
    ),
    (
        re.compile(r"^Output mixes `files` with `target` or `shape`: (?P<name>.+)$"),
        "E224",
        "Output mixes files with target or shape",
        lambda match: f"Output `{match.group('name')}` mixes `files` with `target` or `shape`.",
        (),
    ),
    (
        re.compile(r"^Output must define either `files` or both `target` and `shape`: (?P<name>.+)$"),
        "E224",
        "Output declaration is incomplete",
        lambda match: f"Output `{match.group('name')}` must define either `files` or both `target` and `shape`.",
        (),
    ),
    (
        re.compile(r"^Output target must be typed: (?P<name>.+)$"),
        "E225",
        "Output target must be typed",
        lambda match: f"Output `{match.group('name')}` must use a typed `target` reference.",
        (),
    ),
    (
        re.compile(r"^Unsupported record item: (?P<kind>.+)$"),
        "E226",
        "Unsupported record item",
        lambda match: f"Unsupported record item `{match.group('kind')}`.",
        (),
    ),
    (
        re.compile(r"^Config entries must be scalar key/value lines in (?P<owner>.+)$"),
        "E230",
        "Config entries must be scalar key/value lines",
        lambda match: f"Config entries must be scalar key/value lines in `{match.group('owner')}`.",
        (),
    ),
    (
        re.compile(r"^Duplicate config key in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E231",
        "Duplicate config key",
        lambda match: f"Config owner `{match.group('owner')}` repeats key `{match.group('key')}`.",
        (),
    ),
    (
        re.compile(r"^Unknown config key in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E232",
        "Unknown config key",
        lambda match: f"Config owner `{match.group('owner')}` uses unknown key `{match.group('key')}`.",
        (),
    ),
    (
        re.compile(r"^Missing required config key in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E233",
        "Missing required config key",
        lambda match: f"Config owner `{match.group('owner')}` is missing required key `{match.group('key')}`.",
        (),
    ),
    (
        re.compile(r"^Config key declarations must be simple titled scalars in (?P<owner>.+)$"),
        "E234",
        "Config key declarations must be simple titled scalars",
        lambda match: f"Config key declarations must be simple titled scalars in `{match.group('owner')}`.",
        (),
    ),
    (
        re.compile(r"^Config key declarations must use string labels in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E234",
        "Config key declarations must use string labels",
        lambda match: f"Config key declaration `{match.group('key')}` in `{match.group('owner')}` must use a string label.",
        (),
    ),
    (
        re.compile(r"^Duplicate config key declaration in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E235",
        "Duplicate config key declaration",
        lambda match: f"Config owner `{match.group('owner')}` repeats config key declaration `{match.group('key')}`.",
        (),
    ),
    (
        re.compile(r"^Cyclic workflow inheritance: (?P<detail>.+)$"),
        "E240",
        "Cyclic workflow inheritance",
        lambda match: f"Workflow inheritance cycle: {match.group('detail')}.",
        (),
    ),
    (
        re.compile(r"^Cyclic skills inheritance: (?P<detail>.+)$"),
        "E250",
        "Cyclic skills inheritance",
        lambda match: f"Skills inheritance cycle: {match.group('detail')}.",
        (),
    ),
    (
        re.compile(r"^Duplicate workflow item key in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E261",
        "Duplicate workflow item key",
        lambda match: f"Workflow owner `{match.group('owner')}` repeats key `{match.group('key')}`.",
        (),
    ),
    (
        re.compile(r"^Cannot inherit undefined workflow entry in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E241",
        "Cannot inherit undefined workflow entry",
        lambda match: f"Workflow owner `{match.group('owner')}` cannot inherit undefined key `{match.group('key')}`.",
        (),
    ),
    (
        re.compile(r"^Override kind mismatch for workflow entry in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E242",
        "Override kind mismatch",
        lambda match: f"Workflow owner `{match.group('owner')}` overrides `{match.group('key')}` with the wrong kind.",
        (),
    ),
    (
        re.compile(r"^(?P<kind>inherit|override) requires an inherited workflow in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E243",
        "Workflow patch requires an inherited workflow",
        lambda match: (
            f"`{match.group('kind')}` for key `{match.group('key')}` requires an inherited workflow in `{match.group('owner')}`."
        ),
        (),
    ),
    (
        re.compile(r"^Cyclic (?P<kind>inputs|outputs) inheritance: (?P<detail>.+)$"),
        "E244",
        "Cyclic IO block inheritance",
        lambda match: (
            f"{match.group('kind').title()} inheritance cycle: {match.group('detail')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Cannot inherit undefined (?P<kind>inputs|outputs) entry in (?P<owner>[^:]+): (?P<key>.+)$"
        ),
        "E245",
        "Cannot inherit undefined IO block entry",
        lambda match: (
            f"{match.group('kind').title()} block `{match.group('owner')}` cannot inherit undefined key `{match.group('key')}`."
        ),
        (),
    ),
    (
        re.compile(
            r"^(?P<action>inherit|override) requires an inherited (?P<kind>inputs|outputs) block in (?P<owner>[^:]+): (?P<key>.+)$"
        ),
        "E246",
        "IO block patch requires an inherited IO block",
        lambda match: (
            f"`{match.group('action')}` for key `{match.group('key')}` requires an inherited "
            f"{match.group('kind')} block in `{match.group('owner')}`."
        ),
        (),
    ),
    (
        re.compile(
            r"^Cannot inherit (?P<kind>inputs|outputs) block with unkeyed top-level refs in (?P<owner>[^:]+): (?P<detail>.+)$"
        ),
        "E247",
        "Inherited IO block needs keyed top-level entries",
        lambda match: (
            f"{match.group('kind').title()} block `{match.group('owner')}` contains unkeyed top-level refs: {match.group('detail')}."
        ),
        (
            "Give inherited inputs and outputs blocks stable keyed sections before patching them.",
        ),
    ),
    (
        re.compile(
            r"^(?P<field>Inputs|Outputs) fields must resolve to (?P<expected>inputs|outputs) blocks, not (?P<actual>inputs|outputs) blocks: (?P<ref>.+)$"
        ),
        "E248",
        "IO field ref kind mismatch",
        lambda match: (
            f"`{match.group('field').lower()}` field ref `{match.group('ref')}` must resolve to "
            f"a {match.group('expected')} block, not a {match.group('actual')} block."
        ),
        (),
    ),
    (
        re.compile(
            r"^(?P<field>Inputs|Outputs) patch fields must inherit from (?P<expected>inputs|outputs) blocks, not (?P<actual>inputs|outputs) blocks: (?P<ref>.+)$"
        ),
        "E249",
        "IO patch base kind mismatch",
        lambda match: (
            f"`{match.group('field').lower()}` patch base `{match.group('ref')}` must inherit from "
            f"a {match.group('expected')} block, not a {match.group('actual')} block."
        ),
        (),
    ),
    (
        re.compile(r"^Ambiguous (?P<surface>.+) in (?P<owner>[^:]+): (?P<detail>.+)$"),
        "E270",
        "Ambiguous declaration reference",
        lambda match: f"In `{match.group('owner')}`, `{match.group('detail')}` is ambiguous on the {match.group('surface')} surface.",
        (),
    ),
    (
        re.compile(r"^Workflow refs are not allowed in (?P<surface>.+); (?P<detail>.+)$"),
        "E271",
        "Workflow ref is not allowed here",
        lambda match: f"Workflow refs are not allowed in {match.group('surface')}; {match.group('detail')}",
        (),
    ),
    (
        re.compile(r"^Abstract agent refs are not allowed in (?P<surface>.+); (?P<detail>.+)$"),
        "E272",
        "Abstract agent ref is not allowed here",
        lambda match: f"Abstract agent refs are not allowed in {match.group('surface')}; {match.group('detail')}",
        ("Mention a concrete agent instead of an abstract base agent.",),
    ),
    (
        re.compile(
            r"^Unknown (?:interpolation field|addressable path) on (?P<surface>.+) in (?P<owner>[^:]+): (?P<detail>.+)$"
        ),
        "E273",
        "Unknown addressable path",
        lambda match: (
            f"In `{match.group('owner')}`, `{match.group('detail')}` does not resolve "
            f"to a known addressable item on the {match.group('surface')} surface."
        ),
        (),
    ),
    (
        re.compile(
            r"^(?:Interpolation field must resolve to a scalar|Addressable path must stay addressable) on (?P<surface>.+) in (?P<owner>[^:]+): (?P<detail>.+)$"
        ),
        "E274",
        "Addressable path must stay addressable",
        lambda match: (
            f"In `{match.group('owner')}`, `{match.group('detail')}` resolves "
            f"through a non-addressable surface on the {match.group('surface')} surface."
        ),
        (),
    ),
    (
        re.compile(r"^Missing local declaration ref in (?P<label>.+) (?P<owner>[^:]+): (?P<name>.+)$"),
        "E276",
        "Missing local declaration reference",
        lambda match: (
            f"Missing local declaration ref `{match.group('name')}` in {match.group('label')} `{match.group('owner')}`."
        ),
        (),
    ),
    (
        re.compile(r"^Missing import module: (?P<module>.+)$"),
        "E280",
        "Missing import module",
        lambda match: f"Import module `{match.group('module')}` could not be found under the current prompts root.",
        (),
    ),
    (
        re.compile(r"^Missing imported declaration: (?P<decl>.+)$"),
        "E281",
        "Missing imported declaration",
        lambda match: f"Imported declaration `{match.group('decl')}` does not exist in the resolved module.",
        (),
    ),
    (
        re.compile(r"^Route target must be a concrete agent: (?P<agent>.+)$"),
        "E282",
        "Route target must be a concrete agent",
        lambda match: f"Route target `{match.group('agent')}` is not a concrete agent.",
        (),
    ),
    (
        re.compile(r"^Cyclic workflow composition: (?P<detail>.+)$"),
        "E283",
        "Cyclic workflow composition",
        lambda match: f"Workflow composition cycle: {match.group('detail')}.",
        (),
    ),
    (
        re.compile(r"^Duplicate record key in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E284",
        "Duplicate record key",
        lambda match: f"Record owner `{match.group('owner')}` repeats key `{match.group('key')}`.",
        (),
    ),
    (
        re.compile(r"^Duplicate declaration name: (?P<decl>.+)$"),
        "E288",
        "Duplicate declaration name",
        lambda match: f"Declaration `{match.group('decl')}` is defined more than once in the same module.",
        (),
    ),
    (
        re.compile(r"^Duplicate enum member key in (?P<owner>[^:]+): (?P<key>.+)$"),
        "E293",
        "Duplicate enum member key",
        lambda match: f"Enum `{match.group('owner')}` repeats member key `{match.group('key')}`.",
        (),
    ),
    (
        re.compile(r"^Cyclic import module: (?P<detail>.+)$"),
        "E289",
        "Cyclic import module",
        lambda match: f"Import cycle: {match.group('detail')}.",
        (),
    ),
    (
        re.compile(r"^Relative import walks above prompts root: (?P<detail>.+)$"),
        "E290",
        "Relative import walks above prompts root",
        lambda match: f"Import `{match.group('detail')}` walks above the prompts root.",
        (),
    ),
    (
        re.compile(r"^Input source must stay typed(?:(?: in interpolation))?: (?P<name>.+)$"),
        "E275",
        "Input source must stay typed",
        lambda match: f"Input `{match.group('name')}` must keep a typed `source`.",
        (),
    ),
    (
        re.compile(r"^Output target must stay typed(?:(?: in interpolation))?: (?P<name>.+)$"),
        "E275",
        "Output target must stay typed",
        lambda match: f"Output `{match.group('name')}` must keep a typed `target`.",
        (),
    ),
    (
        re.compile(r"^Output shape must stay typed: (?P<name>.+)$"),
        "E275",
        "Output shape must stay typed",
        lambda match: f"Output `{match.group('name')}` must keep a typed `shape`.",
        (),
    ),
    (
        re.compile(r"^Prompt source path is required for compilation\.$"),
        "E291",
        "Prompt source path is required for compilation",
        lambda _match: "Prompt source path is required for compilation.",
        (),
    ),
    (
        re.compile(
            r"^Active leaf branch must resolve exactly one current-subject form in (?P<owner>.+)$"
        ),
        "E331",
        "Missing current-subject form",
        lambda match: (
            "Each active workflow-law leaf branch must declare exactly one current subject "
            f"in {match.group('owner')}."
        ),
        ("Add either `current artifact ... via ...` or `current none` in each active branch.",),
    ),
    (
        re.compile(
            r"^Active leaf branch resolves more than one current-subject form \((?P<detail>.+)\) in (?P<owner>.+)$"
        ),
        "E332",
        "Multiple current-subject forms",
        lambda match: (
            f"One active workflow-law leaf branch declares multiple current-subject forms "
            f"({match.group('detail')}) in {match.group('owner')}."
        ),
        ("Keep exactly one `current artifact` or `current none` in each active branch.",),
    ),
    (
        re.compile(
            r"^current artifact carrier output must be emitted by the concrete turn in (?P<owner>.+): (?P<name>.+)$"
        ),
        "E333",
        "Current carrier output not emitted",
        lambda match: (
            f"Current-artifact carrier output `{match.group('name')}` is not emitted by "
            f"{match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^current artifact output must be emitted by the concrete turn in (?P<owner>.+): (?P<name>.+)$"
        ),
        "E334",
        "Current output not emitted",
        lambda match: (
            f"Current-artifact output `{match.group('name')}` is not emitted by "
            f"{match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^current artifact target must resolve to a declared input or output in (?P<owner>.+): (?P<name>.+)$"
        ),
        "E335",
        "Current artifact target has wrong kind",
        lambda match: (
            f"Current-artifact target `{match.group('name')}` must resolve to a declared input "
            f"or output in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^current artifact carrier field must be listed in trust_surface in (?P<owner>.+): (?P<name>.+)$"
        ),
        "E336",
        "Current carrier field missing from trust surface",
        lambda match: (
            f"Current-artifact carrier field `{match.group('name')}` is not listed in "
            f"`trust_surface` in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Unknown output field on current artifact via in (?P<owner>.+): (?P<path>.+)$"
        ),
        "E337",
        "Unknown current carrier field",
        lambda match: (
            f"Current-artifact carrier field `{match.group('path')}` does not exist in "
            f"{match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^Mode value is outside enum (?P<enum>.+) in (?P<owner>.+): (?P<value>.+)$"),
        "E341",
        "Mode value outside enum",
        lambda match: (
            f"Mode value `{match.group('value')}` is outside enum `{match.group('enum')}` "
            f"in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^match on (?P<enum>.+) must be exhaustive or include else in (?P<owner>.+)$"),
        "E342",
        "Non-exhaustive mode match",
        lambda match: (
            f"`match` on `{match.group('enum')}` must cover every enum member or include `else` "
            f"in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^own only must stay rooted in the current artifact in (?P<owner>.+): (?P<path>.+)$"),
        "E351",
        "Owned scope is outside the current artifact",
        lambda match: (
            f"Owned scope `{match.group('path')}` is not rooted in the current artifact in "
            f"{match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^own only target must resolve to a declared input or output in (?P<owner>.+): (?P<path>.+)$"
        ),
        "E352",
        "Owned scope target is unknown",
        lambda match: (
            f"Owned scope target `{match.group('path')}` must resolve to a declared input or output "
            f"in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^Owned scope overlaps exact-preserved scope in (?P<owner>.+)$"),
        "E353",
        "Owned scope overlaps exact preservation",
        lambda match: (
            f"Owned scope overlaps exact-preserved scope in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^Owned and forbidden scope overlap in (?P<owner>.+)$"),
        "E354",
        "Owned scope overlaps forbidden scope",
        lambda match: (
            f"Owned scope overlaps forbidden scope in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^preserve (?P<kind>structure|mapping|vocabulary) target must resolve to a declared (?P<label>input or output|enum) in (?P<owner>.+): (?P<path>.+)$"
        ),
        "E355",
        "Preserve target is unknown",
        lambda match: (
            f"`preserve {match.group('kind')}` target `{match.group('path')}` must resolve to a "
            f"declared {match.group('label')} in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^The current artifact cannot be ignored for truth in (?P<owner>.+)$"),
        "E361",
        "Current artifact ignored for truth",
        lambda match: (
            f"The current artifact is being ignored for truth in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^support_only and ignore for comparison contradict in (?P<owner>.+)$"),
        "E362",
        "Comparison-only basis contradiction",
        lambda match: (
            f"`support_only` and `ignore ... for comparison` contradict in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^The current artifact cannot be invalidated in the same active branch in (?P<owner>.+)$"
        ),
        "E371",
        "Current artifact invalidated in same branch",
        lambda match: (
            f"The current artifact is invalidated in the same active branch in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^invalidate carrier field must be listed in trust_surface in (?P<owner>.+): (?P<name>.+)$"
        ),
        "E372",
        "Invalidation carrier field missing from trust surface",
        lambda match: (
            f"Invalidation carrier field `{match.group('name')}` is not listed in `trust_surface` "
            f"in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^Inherited law blocks must use named sections only in (?P<owner>.+)$"),
        "E381",
        "Inherited law requires named sections",
        lambda match: (
            f"Inherited law blocks must use named sections only in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Inherited law block accounts for the same parent subsection more than once in (?P<owner>.+): (?P<key>.+)$"
        ),
        "E382",
        "Duplicate inherited law subsection",
        lambda match: (
            f"Inherited law block accounts for subsection `{match.group('key')}` more than once "
            f"in {match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Inherited law block omits parent subsection\(s\) in (?P<owner>.+): (?P<keys>.+)$"
        ),
        "E383",
        "Missing inherited law subsection",
        lambda match: (
            f"Inherited law block omits parent subsection(s) `{match.group('keys')}` in "
            f"{match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(
            r"^Cannot override undefined law section in (?P<owner>.+): (?P<key>.+)$"
        ),
        "E384",
        "Cannot override undefined law subsection",
        lambda match: (
            f"Cannot override undefined law subsection `{match.group('key')}` in "
            f"{match.group('owner')}."
        ),
        (),
    ),
    (
        re.compile(r"^Could not resolve prompts/ root for (?P<path>.+)\.$"),
        "E292",
        "Could not resolve prompts root",
        lambda match: f"Could not resolve `prompts/` root for `{match.group('path')}`.",
        (),
    ),
    (
        re.compile(r"^Internal compiler error: (?P<detail>.+)$"),
        "E901",
        "Internal compiler error",
        lambda match: match.group("detail"),
        ("This is a compiler bug, not a prompt authoring error.",),
    ),
)


def _compile_diagnostic_from_message(message: str) -> DoctrineDiagnostic:
    for pattern, code, summary, detail_builder, hints in _COMPILE_PATTERN_BUILDERS:
        match = pattern.match(message)
        if match is None:
            continue
        return DoctrineDiagnostic(
            code=code,
            stage="compile",
            summary=summary,
            detail=detail_builder(match),
            hints=hints,
            cause=message if message != detail_builder(match) else None,
        )
    return DoctrineDiagnostic(
        code="E299",
        stage="compile",
        summary="Compile failure",
        detail=message,
    )


_EMIT_PATTERN_BUILDERS: tuple[
    tuple[re.Pattern[str], str, str, Callable[[re.Match[str]], str | None], tuple[str, ...]],
    ...,
] = (
    (
        re.compile(r"^Unknown emit target: (?P<target>.+)$"),
        "E501",
        "Unknown emit target",
        lambda match: f"Emit target `{match.group('target')}` is not defined in `pyproject.toml`.",
        (),
    ),
    (
        re.compile(r"^Emit target (?P<target>.+) has no concrete agents in (?P<path>.+)$"),
        "E502",
        "Emit target has no concrete agents",
        lambda match: f"Emit target `{match.group('target')}` points at `{match.group('path')}`, which has no concrete agents.",
        (),
    ),
    (
        re.compile(r"^pyproject\.toml does not define any \[tool\.doctrine\.emit\.targets\]\.$"),
        "E503",
        "Missing emit targets",
        lambda _match: "The current `pyproject.toml` does not define any emit targets.",
        (),
    ),
    (
        re.compile(r"^Could not find pyproject\.toml in (?P<detail>.+)\.$"),
        "E504",
        "Missing pyproject.toml",
        lambda match: f"Could not find `pyproject.toml` in {match.group('detail')}.",
        (),
    ),
    (
        re.compile(r"^Emit target (?P<target>.+) maps both (?P<a>.+) and (?P<b>.+) to (?P<path>.+)$"),
        "E505",
        "Emit target path collision",
        lambda match: (
            f"Emit target `{match.group('target')}` maps `{match.group('a')}` and `{match.group('b')}` to the same path `{match.group('path')}`."
        ),
        (),
    ),
    (
        re.compile(r"^Emit config must point at pyproject\.toml: (?P<path>.+)$"),
        "E507",
        "Emit config path must point at pyproject.toml",
        lambda match: f"Emit config path must point at `pyproject.toml`, got `{match.group('path')}`.",
        (),
    ),
    (
        re.compile(r"^Missing pyproject\.toml: (?P<path>.+)$"),
        "E504",
        "Missing pyproject.toml",
        lambda match: f"Missing `pyproject.toml`: `{match.group('path')}`.",
        (),
    ),
    (
        re.compile(r"^Emit target #(?P<index>.+) must be a TOML table\.$"),
        "E508",
        "Emit target must be a TOML table",
        lambda match: f"Emit target #{match.group('index')} must be a TOML table.",
        (),
    ),
    (
        re.compile(r"^Duplicate emit target name: (?P<name>.+)$"),
        "E509",
        "Duplicate emit target name",
        lambda match: f"Emit target `{match.group('name')}` is defined more than once.",
        (),
    ),
    (
        re.compile(
            r"^Emit target (?P<name>.+) must point at an AGENTS\.prompt or SOUL\.prompt entrypoint, got (?P<entrypoint>.+)$"
        ),
        "E510",
        "Emit target entrypoint must be AGENTS.prompt or SOUL.prompt",
        lambda match: (
            f"Emit target `{match.group('name')}` must point at an `AGENTS.prompt` or `SOUL.prompt` entrypoint, got `{match.group('entrypoint')}`."
        ),
        (),
    ),
    (
        re.compile(r"^Emit target (?P<name>.+) output_dir is a file: (?P<path>.+)$"),
        "E511",
        "Emit target output_dir is a file",
        lambda match: f"Emit target `{match.group('name')}` output_dir is a file: `{match.group('path')}`.",
        (),
    ),
    (
        re.compile(r"^(?P<label>.+) does not exist: (?P<value>.+)$"),
        "E512",
        "Emit config path does not exist",
        lambda match: f"{match.group('label')} does not exist: {match.group('value')}",
        (),
    ),
    (
        re.compile(r"^(?P<label>.+)\.(?P<key>.+) must be a string\.$"),
        "E513",
        "Emit config value must be a string",
        lambda match: f"{match.group('label')}.{match.group('key')} must be a string.",
        (),
    ),
    (
        re.compile(r"^Could not resolve prompts/ root for (?P<path>.+)$"),
        "E514",
        "Could not resolve prompts root",
        lambda match: f"Could not resolve `prompts/` root for `{match.group('path')}`.",
        (),
    ),
)


def _emit_diagnostic_from_message(message: str) -> DoctrineDiagnostic:
    for pattern, code, summary, detail_builder, hints in _EMIT_PATTERN_BUILDERS:
        match = pattern.match(message)
        if match is None:
            continue
        return DoctrineDiagnostic(
            code=code,
            stage="emit",
            summary=summary,
            detail=detail_builder(match),
            hints=hints,
            cause=message if message != detail_builder(match) else None,
        )
    return DoctrineDiagnostic(
        code="E599",
        stage="emit",
        summary="Emit failure",
        detail=message,
    )
````

## File: examples/01_hello_world/prompts/AGENTS.prompt
````
agent HelloWorld:
    # When there is no body beneath the key: heading it renders as plain text
    role: "You are the hello world agent."

    workflow: "Instruction"
        "Say hello world."

agent HelloWorld2:
    # This renders a "Role" markdown heading
    role: "Role"
        "You are the hello world agent."

    workflow: "Instruction"
        "Say hello world."
````

## File: examples/02_sections/prompts/AGENTS.prompt
````
agent SectionsDemo:
    role: "You are the sections demonstration agent."

    workflow: "Steps"
        "Follow the steps below in order."

        step_one: "Step One"
            "Say hello."

        step_two: "Step Two"
            "Say world."
````

## File: examples/03_imports/ref/AGENTS.md
````markdown
You are the imports demonstration agent.

## Imported Steps

Follow the imported instructions below.

### Greeting

Say hello.

### Object

Say world.

### Polite Greeting

Say hello politely and keep the tone warm.

### Absolute Briefing

This file composes sibling imports through dotted package paths.

#### Opening

State the topic.

#### Closing

End with one clear next step.

### Relative Chain

This file chains a sibling-relative import with a parent-relative import.

#### Leaf Step

This module reaches back to its parent package before following the path forward again.

##### Shared Context

Start with the shared context.

#### Shared Wrap-Up

Finish with a shared wrap-up.

### Deep Relative Chain

This file uses both a sibling-relative import and a multi-level parent-relative import.

#### Deep Detail

This file walks back up the package tree with `...` before following the path forward again.

##### Root Topic

Name the root topic once.

#### Final Note

End with the final shared note.
````

## File: examples/07_handoffs/ref/project_lead/AGENTS.md
````markdown
# Project Lead

Core job: start the work, route it to Research Specialist, and take it back after Writing Specialist finishes.

## Your Job

- Start the issue with a clear route.
- Route the first owner change.
- Keep the issue on a truthful route when work is blocked or routing goes stale.
- Take the issue back after the final specialist return and close it out honestly.

## Read First

Start by reading Your Job.
Then read Workflow Core.

## Workflow Core

This file is the runtime guide for a simple multi-agent routing pattern.

### Same-Issue Workflow

- Keep the whole job on one issue from setup through final return.
- Keep one owner at a time on that issue.
- The normal order is `Project Lead` -> `Research Specialist` -> `Writing Specialist` -> `Project Lead`.
- Route the first owner change to `Research Specialist`.
- After `Research Specialist`, the next owner is `Writing Specialist`.
- After `Writing Specialist`, the next owner is `Project Lead`.
- If the route is broken or the work is blocked before specialist work begins, keep or return the work to `Project Lead`.

### Next Owner

- When ready to start the work -> `Research Specialist`
- If the route is broken or the work is blocked before specialist work begins -> `Project Lead`

### Owner Change Comment

Every owner-change comment should say:

- what this turn changed
- the next owner when ownership is changing now
- the exact blocker when the issue is blocked
````

## File: examples/07_handoffs/ref/research_specialist/AGENTS.md
````markdown
# Research Specialist

Core job: do the research lane's work and route it to Writing Specialist.

## Your Job

- Take the work only when `Project Lead` routes it to you.
- Do the research lane's work.
- Keep the work ready for the next lane.
- Do not route the work anywhere except `Writing Specialist` or `Project Lead`.

## Read First

Read Your Job first. Then read Workflow Core.

## Workflow Core

### Same-Issue Workflow

- Keep the work on the same issue.
- Do only this lane's job.
- Route to the next owner only when the current lane is honestly ready.
- If the work is blocked or the route is unclear, return it to `Project Lead`.

### Next Owner

- When ready -> `Writing Specialist`
- If blocked or the route is unclear -> `Project Lead`

### Owner Change Comment

Every owner-change comment should say:

- what changed
- what the next owner should use now
- the next owner when ownership is changing now
````

## File: examples/07_handoffs/ref/writing_specialist/AGENTS.md
````markdown
# Writing Specialist

Core job: do the writing lane's work and route it back to Project Lead.

## Your Job

- Take the work only when `Research Specialist` hands it to you.
- Do the writing lane's work.
- Keep the work within the scope already set upstream.
- Route the work back to `Project Lead` when the lane is complete or blocked.

## Read First

Read Your Job first. Then read Workflow Core.

## Workflow Core

### Same-Issue Workflow

- Keep the work on the same issue.
- Do only this lane's job.
- Route to the next owner only when the current lane is honestly ready.
- If the work is blocked or the route is unclear, return it to `Project Lead`.

### Next Owner

- When ready -> `Project Lead`
- If blocked or the route is unclear -> `Project Lead`

### Owner Change Comment

Every owner-change comment should say:

- what changed
- what the next owner should use now
- the next owner when ownership is changing now
````

## File: examples/09_outputs/ref/custom_target_output_agent/AGENTS.md
````markdown
# Custom Target Output Agent

Core job: leave an owner update on the project tracker.

## Your Job

- Write the owner update using the custom tracker comment target.

## Outputs

### Project Tracker Update

- Target: Tracker Comment
- Issue: `CURRENT_ISSUE`
- Shape: Owner Update Comment
- Requirement: Required

#### Must Include

- What Changed: say what changed.
- Current Source Of Truth: name the current source of truth.
- Next Owner: name the next owner.

#### Owns

This output owns the owner-change summary and the current source of truth for the next owner.

#### Standalone Read

A downstream reader should be able to read this comment alone and understand what changed, what to trust now, and who owns next.

#### Example

```text
- changed: updated the section plan
- use now: SECTION_PLAN.md
- next owner: Writing Specialist
```
````

## File: examples/12_role_home_composition/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "role-home composition renders authored slots plus typed fields"
status = "active"
kind = "render_contract"
agent = "LessonsProjectLead"
assertion = "exact_lines"
expected_lines = [
  "Core job: open, route, and finish Lessons issues while keeping publish and follow-up honest on the same issue.",
  "",
  "## Your Job",
  "",
  "Keep one owner and one obvious next step on the same issue.",
  "Keep the issue plan current on routing-only or process-repair turns.",
  "Own publish and follow-up state when those are the live jobs.",
  "",
  "## Read First",
  "",
  "### Read Order",
  "",
  "Read Your Job first.",
  "Then read Workflow Core and How To Take A Turn.",
  "Then read Inputs, Outputs, Routing, When To Stop, Skills, When To Use This Role, and Standards And Support.",
  "",
  "### Immediate Local Read",
  "",
  "Read the active issue plan, the latest issue comment that names the current files, and any current PR or QR state before you route or publish.",
  "",
  "## Workflow Core",
  "",
  "### Read Current Work State",
  "",
  "Start with the active issue, the current plan, and the named current files.",
  "Use the attached checkout for product truth only.",
  "",
  "### Same-Issue Workflow",
  "",
  "Keep normal Lessons work on one issue from routing through follow-up.",
  "Keep one owner at a time on that issue.",
  "Route work to the earliest honest specialist lane.",
  "When copy work is ready, route it to Lessons Copywriter.",
  "",
  "### Handoff Comment",
  "",
  "Every handoff comment should say what changed, what the next owner should trust now, and who owns next.",
  "",
  "### Publish Return",
  "",
  "Keep PR, QR, and follow-up state on the same issue.",
  "Do not call the work done until the current publish state is explicit.",
  "",
  "## How To Take A Turn",
  "",
  "### Turn Sequence",
  "",
  "Read the active issue, the current files, and the upstream contracts your lane depends on.",
  "Do only this lane's job.",
  "Update the current outputs that now matter.",
  "Leave one clear handoff and stop.",
  "",
  "### Guardrails",
  "",
  "Do not let routing drift away from the active issue.",
  "Do not hand off weak work.",
  "",
  "## Inputs",
  "",
  "### Current Issue Plan",
  "",
  "- Source: Prompt",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "Use the current issue plan to understand the intended owner and next step.",
  "",
  "### Current Issue State",
  "",
  "- Source: File",
  "- Path: `track_root/_authoring/CURRENT_ISSUE_STATE.md`",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "Use the current issue state to understand the named current files and publish state.",
  "",
  "## Outputs",
  "",
  "### Project Lead Update",
  "",
  "- Target: Tracker Comment",
  "- Issue: `CURRENT_ISSUE`",
  "- Shape: Owner Update Comment",
  "- Requirement: Required",
  "",
  "#### Must Include",
  "",
  "##### What Changed",
  "",
  "Say what changed on this routing or publish turn.",
  "",
  "##### Current Source Of Truth",
  "",
  "Name the current source of truth for the next owner.",
  "",
  "##### Next Owner",
  "",
  "Name the honest next owner.",
  "",
  "## Routing",
  "",
  "### Next Owner If Accepted",
  "",
  "If the issue is ready for copy work -> LessonsCopywriter",
  "",
  "### If The Work Is Not Ready",
  "",
  "If the route is still unclear -> LessonsProjectLead",
  "",
  "## When To Stop",
  "",
  "### Stop Here If",
  "",
  "Stop when one honest owner, one honest next step, and the current source of truth are explicit.",
  "",
  "## Skills",
  "",
  "### Can Run",
  "",
  "#### release-followthrough",
  "",
  "##### Purpose",
  "",
  "Handle PR follow-up, QR updates, publish proof, and same-issue closeout.",
  "",
  "##### Use When",
  "",
  "Use this when publish or follow-up is the live job.",
  "",
  "## When To Use This Role",
  "",
  "Use this role when new Lessons work needs routing.",
  "Use this role when publish or follow-up is the live job.",
  "",
  "## Standards And Support",
  "",
  "### Publish And Follow-Up",
  "",
  "Keep the issue explicit about publish intent: ship or prototype.",
  "Do not use publish as a shortcut around current output or review rules.",
  "",
  "### GitHub Helpers",
  "",
  "Use repo-owned GitHub helpers when the live job needs remote GitHub access.",
  "",
  "### Staging QR Helpers",
  "",
  "Use repo-owned QR helpers when publish proof depends on current QR state.",
  "",
  "### Attached Checkout",
  "",
  "Use the attached checkout for product truth only. It does not decide workflow, ownership, or the next step.",
]
````

## File: examples/13_critic_protocol/ref/acceptance_critic/AGENTS.md
````markdown
# Acceptance Critic

Core job: review the current dossier, issue an explicit verdict, and route the same issue honestly.

## Your Job

- Review the current dossier against the current issue plan.
- Return one explicit verdict.
- Write the gate log that supports that verdict.
- Route the issue to the honest next owner.
- Stop and escalate instead of guessing when required review inputs are missing.

## Read First

### Read Order

Read Your Job first.
Then read Workflow Core and How To Take A Turn.
Then read Inputs, Outputs, Review Routing, When To Stop, Skills, and Standards And Support.

### Current Review Scope

Read the current issue plan, the current dossier, and the current validation record before you issue a verdict.

## Workflow Core

### Same-Issue Review

Keep review on the same issue as the producer turn.
Judge the current named files, not stale copies or remembered context.

### Verdict Rule

Return one explicit verdict: `accept` or `changes requested`.
Name the honest next owner for that verdict.

### Handoff Rule

If the work is accepted, route the issue forward.
If the work is not ready, route it back to the honest producer.
If the route is unclear, send it to Project Lead instead of guessing.

## How To Take A Turn

### Turn Sequence

Read the required review inputs.
Check the work against the current issue plan and the named validation record.
Write the verdict and gate log.
Route the issue to the honest next owner and stop.

### Guardrails

Do not approve work you cannot support from the current review inputs.
Do not bounce the work for vague reasons.
Do not guess when required review inputs are missing.

## Inputs

### Current Issue Plan

- Source: Prompt
- Shape: Markdown document
- Requirement: Required

Use the current issue plan to understand the intended acceptance bar and next normal owner.

### Section Dossier

- Source: File
- Path: `section_root/_authoring/SECTION_DOSSIER.md`
- Shape: Markdown document
- Requirement: Required

Review the current dossier as the main artifact under review.

### Dossier Validation Record

- Source: File
- Path: `section_root/_authoring/DOSSIER_VALIDATION.md`
- Shape: Markdown document
- Requirement: Required

Use the current validation record to understand what checks ran and what passed or failed.

## Outputs

### Critic Review Output

- Review Verdict: `section_root/_authoring/REVIEW_VERDICT.md`
- Review Verdict Shape: MarkdownDocument
- Run Gate Log: `section_root/_authoring/RUN_GATE_LOG.md`
- Run Gate Log Shape: MarkdownDocument

#### Must Include

- Verdict: `REVIEW_VERDICT.md` must state `accept` or `changes requested` explicitly.
- Next Owner: `REVIEW_VERDICT.md` must name the honest next owner.
- Reason: `REVIEW_VERDICT.md` must give the short reason for the verdict and route.
- Gate Results: `RUN_GATE_LOG.md` must list every failed gate or say that all named gates passed.
- Evidence Used: `RUN_GATE_LOG.md` must record the validation evidence the critic actually relied on.

#### Owns

This output owns the current verdict, the honest next owner, and the gate-by-gate review record for this turn.

#### Standalone Read

A downstream reader should be able to read `REVIEW_VERDICT.md` and `RUN_GATE_LOG.md` and understand the verdict, route, and review basis.

## Review Routing

### Next Owner If Accepted

- If accepted -> ProjectLead

### If The Work Is Not Ready

- If changes are required -> SectionAuthor
- If the route is unclear -> ProjectLead

## When To Stop

### Stop Here If

Stop when the verdict is explicit, the next owner is clear, and the gate log matches the actual review basis.

### Hard Stop Rule

- If a required review input is missing, stop and escalate.
- Do not approve from memory, stale notes, or old copies.

## Skills

### Can Run

#### lesson-review-checklist

##### Purpose

Run the repo's current checklist for critic review of a section dossier.

##### Use When

Use this when the role needs a repeatable review pass against the current dossier contract.

## Standards And Support

### Review Rules

Judge only the work that is currently in scope for this issue.
A failed gate should name the actual missing or incorrect thing.

### Evidence Rule

Record the evidence you actually relied on in the gate log.
If the validation record is missing or stale, do not pretend the work was validated.

### Diff Tools

Use repo-owned diff tools when you need to isolate what changed in the current dossier.

### Validator Runner

Use the named dossier validator when the validation record depends on a rerun.
Record the exact command and result in `RUN_GATE_LOG.md`.
````

## File: examples/16_workflow_string_interpolation/cases.toml
````toml
schema_version = 1
default_prompt = "prompts/AGENTS.prompt"

[[cases]]
name = "workflow strings interpolate local and imported declaration contract data inline"
status = "active"
kind = "render_contract"
agent = "WorkflowStringInterpolationDemo"
assertion = "exact_lines"
approx_ref = "ref/workflow_string_interpolation_demo/AGENTS.md"
expected_lines = [
  "Keep one workflow sentence readable while still pulling the typed contract truth from named declarations.",
  "",
  "## Immediate Local Read",
  "",
  "### Read Now",
  "",
  "Read the current issue, the current Issue Plan And Route, the latest issue comment that names the current files, track.meta.json at `track_root/track.meta.json`, any current CONCEPTS.md at `section_root/_authoring/CONCEPTS.md`, and nearby section context only as support evidence to re-earn.",
  "",
  "### Handoff Shape",
  "",
  "When you stop, leave one Final Handoff Comment through Turn Response.",
  "",
  "## Inputs",
  "",
  "### Current Issue Plan",
  "",
  "- Source: Prompt",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "Use the current issue plan to confirm the intended owner and next step.",
  "",
  "### Track Metadata",
  "",
  "- Source: File",
  "- Path: `track_root/track.meta.json`",
  "- Shape: Json Object",
  "- Requirement: Required",
  "",
  "Use this file as the current track metadata truth.",
  "",
  "### Current Concepts",
  "",
  "- Source: File",
  "- Path: `section_root/_authoring/CONCEPTS.md`",
  "- Shape: Markdown Document",
  "- Requirement: Advisory",
  "",
  "Use this only when the section already has live concepts to preserve.",
  "",
  "## Outputs",
  "",
  "### Final Handoff Comment",
  "",
  "- Target: Turn Response",
  "- Shape: Markdown Document",
  "- Requirement: Required",
  "",
  "Use this output contract when you leave the next owner one clear update.",
]

[[cases]]
name = "workflow refs are rejected in workflow string interpolation"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_WORKFLOW_INTERPOLATION.prompt"
agent = "InvalidWorkflowStringInterpolationAgent"
exception_type = "CompileError"
error_code = "E271"
message_contains = [
  "Workflow refs are not allowed in workflow strings",
  "use `use` for workflow composition",
  "SharedRead",
]

[[cases]]
name = "unknown workflow string interpolation fields fail loud"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_FIELD_PATH.prompt"
agent = "InvalidFieldPathInterpolationAgent"
exception_type = "CompileError"
error_code = "E273"
message_contains = [
  "Unknown addressable path on workflow strings",
  "shared.contracts.TrackMetadata:source.missing",
]

[[cases]]
name = "ambiguous workflow string interpolation refs fail loud"
status = "active"
kind = "compile_fail"
prompt = "prompts/INVALID_AMBIGUOUS_INTERPOLATION.prompt"
agent = "InvalidAmbiguousInterpolationAgent"
exception_type = "CompileError"
error_code = "E270"
message_contains = [
  "Ambiguous workflow string interpolation ref",
  "SharedThing",
  "input declaration",
  "skill declaration",
]
````

## File: examples/09_outputs/ref/file_output_agent/AGENTS.md
````markdown
# File Output Agent

Core job: write the section plan to a markdown file.

## Your Job

- Write the section plan to the required file.

## Outputs

### Section Plan Output

- Target: File
- Path: `section_root/_authoring/SECTION_PLAN.md`
- Shape: Section Plan Document
- Requirement: Required

#### Must Include

- Summary: start with a short summary.
- Planned Sections: list the planned sections in order.
- Unresolved Risks Or Decisions: list unresolved risks or decisions.

#### Support Files

- `SECTION_FLOW_AUDIT.md` at `section_root/_authoring/SECTION_FLOW_AUDIT.md` when section sizing or ordering constraints matter.

#### Owns

This output owns the current section plan and the unresolved decisions that still matter.

#### Standalone Read

The next role should be able to read `SECTION_PLAN.md` alone and understand the current plan.

#### Path Notes

Interpret `section_root/...` from the current work context and surrounding instructions.
This example keeps that interpretation as explained guidance, not as a separate root primitive.

#### Example

```md
# Section Plan
## Summary
...
```
````

## File: examples/README.md
````markdown
# Examples

The examples are both the language teaching surface and the verification corpus.

Each numbered example may contain:

- `prompts/`: authored `.prompt` source
- `cases.toml`: manifest-backed proof used by `doctrine.verify_corpus`
- `ref/`: checked-in expected render or error output
- `build_ref/`: checked-in emitted tree output when the emit pipeline matters

Read the examples in numeric order. The sequence is intentional.

For the shipped workflow-law model behind examples `30` through `38`, start
with [../docs/WORKFLOW_LAW.md](../docs/WORKFLOW_LAW.md).

## Reading Order

- `01` through `06`: core agent and workflow syntax, imports, inheritance, and
  explicit patching
- `07` through `14`: authored slots, routing, typed inputs and outputs, skills,
  role-home composition, and handoff truth
- `15` through `20`: readable refs, interpolation, and richer authored prose
  surfaces
- `21` through `26`: first-class block reuse, inheritance, and abstract
  authored-slot requirements
- `27` through `29`: addressable nested items, recursive workflow paths, and
  enums for closed vocabularies
- `30` through `38`: active workflow-law proof for route-only turns, portable
  currentness, trust carriers, scope and preservation law, basis roles,
  invalidation, law reuse, and the metadata-polish capstone

## Workflow Law Ladder

- `30_law_route_only_turns`: route-only work with `current none`, `stop`, and
  explicit reroute
- `31_currentness_and_trust_surface`: one current artifact plus emitted trust
  carriers
- `32_modes_and_match`: enum-backed modes, exhaustive `match`, and one current
  subject per branch
- `33_scope_and_exact_preservation`: narrow ownership with exact preservation
  and overlap checks
- `34_structure_mapping_and_vocabulary_preservation`: preserve non-exact truth
  such as structure, mapping, and vocabulary
- `35_basis_roles_and_rewrite_evidence`: comparison-only support and rewrite-
  evidence exclusions
- `36_invalidation_and_rebuild`: invalidation as a truth transition plus the
  rebuild pattern
- `37_law_reuse_and_patching`: named law subsections with explicit inheritance
  and override rules
- `38_metadata_polish_capstone`: the full integrated portable-truth model

## Important Rules

- A checked-in ref file is not proof on its own. The manifest is the proof
  surface.
- If docs and examples disagree, trust `doctrine/` and the manifest-backed
  cases.
- Keep new examples narrow: one new idea at a time.
- Do not add a new language primitive just to paper over a bad example.
- Keep the corpus single-surface: shipped manifests should stay active proof,
  not advisory review lanes.

## Useful Commands

Verify the whole active corpus:

```bash
make verify-examples
```

Verify one example manifest:

```bash
uv run --locked python -m doctrine.verify_corpus --manifest examples/01_hello_world/cases.toml
```

Emit configured example trees:

```bash
uv run --locked python -m doctrine.emit_docs --target example_07_handoffs
uv run --locked python -m doctrine.emit_docs --target example_14_handoff_truth
```
````

## File: examples/03_imports/prompts/AGENTS.prompt
````
# This example now pressure-tests Python-like import resolution for prompt files.
# - `import package.module` resolves from this example's `prompts/` root
# - `import .sibling.module` resolves from the current file's package
# - `import ..shared.module` walks to the parent package first
# - any number of leading dots is allowed; the import walks up one package
#   level fewer than the dot count before following the remaining module path
# - imported declarations are composed through keyed `use` entries:
#   `use local_key: package.module.WorkflowName`
# - the local key is the outer composition identity if a later phase needs to
#   patch, reorder, or replace this composed piece
# The first three imports are intentionally simple.
# The later imports are intentionally more complex transitive chains.
import simple.greeting
import simple.object
import simple.nested.polite
import chains.absolute.briefing
import chains.relative.entry
import chains.deep.levels.one.two.entry


agent ImportsDemo:
    role: "You are the imports demonstration agent."

    workflow: "Imported Steps"
        "Follow the imported instructions below."

        use greeting: simple.greeting.Greeting
        use object: simple.object.Object
        use polite_greeting: simple.nested.polite.PoliteGreeting
        use absolute_briefing: chains.absolute.briefing.AbsoluteBriefing
        use relative_chain: chains.relative.entry.RelativeChain
        use deep_relative_chain: chains.deep.levels.one.two.entry.DeepRelativeChain
````

## File: examples/05_workflow_merge/prompts/AGENTS.prompt
````
# This base is abstract because concrete leaf agents inherit from it.
abstract agent BaseBriefingAgent:
    role: "You are the base briefing agent."

    workflow: "Briefing"
        "Deliver the briefing in the base order."
        "Keep the framing brief and direct."

        opening: "Opening"
            "State the topic."

        main_point: "Main Point"
            "Give the original main point."

        supporting_point: "Supporting Point"
            "Add one supporting detail."

        closing: "Closing"
            "Wrap up the briefing."

# Inherited workflows are always explicit and exhaustive.
# Concrete leaf agents inherit from this abstract base.
# A child must account for every inherited section exactly once.
# - `inherit key` keeps the inherited section and places it exactly here
# - `override key:` replaces the inherited section and keeps the inherited title
# - `override key: "New Title"` replaces the inherited section and its title
# - `key: "Title"` creates a new section exactly where it is written
# There is no implicit merge or append behavior.
agent OrderedBriefingAgent[BaseBriefingAgent]:
    role: "You are the ordered briefing agent."

    workflow: "Ordered Briefing"
        "Deliver the revised briefing in the explicit order below."
        "This child places inherited, overridden, and new sections on purpose."

        inherit opening

        context_note: "Context Note"
            "Add the missing context before the main point."

        override main_point:
            "Give the revised main point."

        inherit supporting_point
        inherit closing

        follow_up: "Follow Up"
            "Invite one follow-up question."

# This child demonstrates a valid title override on an inherited section.
# The key identity stays the same, but the rendered section title changes.
agent RetitledBriefingAgent[BaseBriefingAgent]:
    role: "You are the retitled briefing agent."

    workflow: "Revised Briefing"
        "Deliver the revised briefing below."
        "This child keeps the structure but changes one section title on purpose."

        inherit opening

        override main_point: "Revised Main Point"
            "Give the revised main point."

        inherit supporting_point
        inherit closing

# This child demonstrates the compiler error rule for `override`.
# It is still a concrete leaf agent, so it would render if compilation succeeded.
# The inherited order is still accounted for explicitly.
# `override key:` only works when the parent already defines that key.
# If the intent is to add something new, drop `override` and define a new key with a title.
agent InvalidOverrideBriefingAgent[BaseBriefingAgent]:
    role: "You are the invalid override briefing agent."

    workflow: "Briefing"
        "This example should fail before rendering."

        inherit opening

        override context_note: "Context Note"
            "Add the missing context before the main point."

        override main_point: "Overridden Main Point Title"
            "Give the revised main point."

        inherit supporting_point
        inherit closing
````

## File: examples/05_workflow_merge/ref/invalid_override_briefing_agent/COMPILER_ERROR.md
````markdown
`InvalidOverrideBriefingAgent` does not render an `AGENTS.md`.

Canonical compiler error:

```text
E001 compile error: Cannot override undefined inherited entry

Location:
- examples/05_workflow_merge/prompts/AGENTS.prompt

Detail:
- Cannot override undefined workflow entry in agent BaseBriefingAgent slot workflow: context_note

Trace:
- compile agent `InvalidOverrideBriefingAgent` (examples/05_workflow_merge/prompts/AGENTS.prompt)

Hint:
- If this entry is new, define it directly instead of using `override`.

Cause:
- E001 Cannot override undefined workflow entry in agent BaseBriefingAgent slot workflow: context_note
```

Canonical reference:

- [docs/COMPILER_ERRORS.md](../../../docs/COMPILER_ERRORS.md)
````

## File: examples/11_skills_and_tools/ref/lesson_copywriter/AGENTS.md
````markdown
# Lesson Copywriter

Core job: turn an approved lesson manifest into grounded reader copy without changing lesson structure or authority scope.

## Your Job

- Read the whole lesson before you rewrite isolated strings.
- Use grounded domain wording without changing the approved structure or authority scope.
- If no named task skill fits cleanly, discover the right one before you guess.

## Skills

### Can Run

#### domain-grounding-kb

##### Purpose

Ground reader-facing domain wording against current source truth.

This skill is required for this role. If you cannot locate it, stop and escalate instead of guessing.

##### Use When

Use this when the lane needs primary-source receipts for reader-facing copy.

##### Requires

A wording surface or claim that needs domain grounding.

##### Provides

- The normal repo workflow for grounding domain wording against current source truth.
- A clear route for collecting the receipts this lane needs.

##### Does Not

- Does not change the approved structure.
- Does not establish final expert authority.

#### domain-copy-rewrite

##### Purpose

Rewrite reader-facing domain copy in the repo's expected voice.

##### Use When

Use this when the job is reader-facing domain wording such as titles, hints, coach text, explanations, and feedback.

### Discover With

#### find-skills

##### Purpose

Find the best matching repo skill for the current job.

### Not For This Role

#### device-runtime-check

##### Purpose

Drive a simulator or device for runtime investigation.

##### Reason

This role is baseline copy work, not simulator or device investigation.

#### dev-loop-restore

##### Purpose

Restore a live development loop.

##### Use When

Use this only when the job is restoring a live development loop.

##### Reason

This role is baseline copy work, not development environment repair.
````

## File: examples/12_role_home_composition/ref/lessons_copywriter/AGENTS.md
````markdown
# Lessons Copywriter

Core job: turn the approved manifest into grounded reader-facing copy without changing lesson structure or authority scope.

## Your Job

Read the whole lesson before you rewrite isolated strings.
Use grounded domain wording without changing the approved structure or authority scope.
Record post-copy validation in the current outputs.

## Read First

### Read Order

Read Your Job first.
Then read Workflow Core and How To Take A Turn.
Then read Inputs, Outputs, Routing, When To Stop, Skills, When To Use This Role, and Standards And Support.

### Immediate Local Read

Read SECTION_CONCEPTS_AND_TERMS.md, LESSON_PLAN.md, LESSON_SITUATIONS.md, and lesson_manifest.json before you touch reader-facing text.

## Workflow Core

### Read Current Work State

Start with the active issue, the current plan, and the named current files.
Use the attached checkout for product truth only.

### Same-Issue Workflow

Keep normal Lessons work on one issue from routing through follow-up.
Keep one owner at a time on that issue.
After the copy lane, return the same issue to Lessons Project Lead.

### Handoff Comment

Every handoff comment should say what changed, what the next owner should trust now, and who owns next.

## How To Take A Turn

### Turn Sequence

Read the active issue, the current files, and the upstream contracts your lane depends on.
Do only this lane's job.
Update the current outputs that now matter.
Leave one clear handoff and stop.

### Guardrails

Do not let routing drift away from the active issue.
Do not hand off weak work.

## Inputs

### Section Concepts And Terms

- Source: File
- Path: `section_root/_authoring/SECTION_CONCEPTS_AND_TERMS.md`
- Shape: Markdown document
- Requirement: Required

Use the locked section language before rewriting reader-facing text.

### Lesson Plan

- Source: File
- Path: `lesson_root/_authoring/LESSON_PLAN.md`
- Shape: Markdown document
- Requirement: Required

Use the approved lesson plan to preserve the lesson's teaching job.

### Lesson Situations

- Source: File
- Path: `lesson_root/_authoring/LESSON_SITUATIONS.md`
- Shape: Markdown document
- Requirement: Required

Use the approved lesson situations to preserve concrete rep choices.

### Lesson Manifest

- Source: File
- Path: `lesson_root/_authoring/lesson_manifest.json`
- Shape: JsonObject
- Requirement: Required

Use the current lesson manifest as the editable reader-facing surface.

## Outputs

### Copy Pass Output

- Copy Grounding: `lesson_root/_authoring/COPY_GROUNDING.md`
- Copy Grounding Shape: MarkdownDocument
- Updated Manifest: `lesson_root/_authoring/lesson_manifest.json`
- Updated Manifest Shape: JsonObject

#### Must Include

- Grounding: `COPY_GROUNDING.md` should show the grounding that shaped the final wording.
- Preserved Terms: `COPY_GROUNDING.md` should name the locked terms that had to survive.
- Validation: `COPY_GROUNDING.md` should record what validation ran after the copy pass.

#### Standalone Read

A downstream reader should be able to read `COPY_GROUNDING.md` and `lesson_manifest.json` and understand what changed and what was validated.

## Routing

### Next Owner If Accepted

- If copy and validation are ready -> LessonsProjectLead

### If The Work Is Not Ready

- If grounding is missing or routing is unclear -> LessonsProjectLead

## When To Stop

### Stop Here If

Stop when reader-facing copy and post-copy validation are explicit enough for return to Project Lead.

## Skills

### Can Run

#### domain-grounding-kb

##### Purpose

Ground reader-facing domain wording against current source truth.

This skill is required for this role. If you cannot locate it, stop and escalate instead of guessing.

##### Use When

Use this when the lane needs primary-source receipts for reader-facing copy.

##### Does Not

- Does not change the approved structure.
- Does not establish final expert authority.

#### domain-copy-rewrite

##### Purpose

Rewrite reader-facing domain copy in the repo's expected voice.

##### Use When

Use this when the job is reader-facing domain wording such as titles, hints, coach text, explanations, and feedback.

## When To Use This Role

Use this role when the manifest already exists and the next job is final reader-facing copy.
Expect this lane to stop with current copy outputs ready for return to Project Lead.

## Standards And Support

### Domain Grounding

Use reference notes to ground meaning and reviewed examples to ground natural wording.
If the grounding is missing, stop and say it is missing.

### Copy Standards

Keep locked concepts and terms intact.
Do not sharpen exact-action claims in copy.

### Reference KB

Use it for definitions, grounded claim checks, terminology, and domain wording.
Do not use it as final expert authority.

### Step JSON Validator

Use it after copy changes to validate the changed lesson manifest surfaces.
Record the command and result in `COPY_GROUNDING.md`.

### Attached Checkout

Use the attached checkout for product truth only. It does not decide workflow, ownership, or the next step.
````

## File: examples/12_role_home_composition/ref/lessons_project_lead/AGENTS.md
````markdown
# Lessons Project Lead

Core job: open, route, and finish Lessons issues while keeping publish and follow-up honest on the same issue.

## Your Job

Keep one owner and one obvious next step on the same issue.
Keep the issue plan current on routing-only or process-repair turns.
Own publish and follow-up state when those are the live jobs.

## Read First

### Read Order

Read Your Job first.
Then read Workflow Core and How To Take A Turn.
Then read Inputs, Outputs, Routing, When To Stop, Skills, When To Use This Role, and Standards And Support.

### Immediate Local Read

Read the active issue plan, the latest issue comment that names the current files, and any current PR or QR state before you route or publish.

## Workflow Core

### Read Current Work State

Start with the active issue, the current plan, and the named current files.
Use the attached checkout for product truth only.

### Same-Issue Workflow

Keep normal Lessons work on one issue from routing through follow-up.
Keep one owner at a time on that issue.
Route work to the earliest honest specialist lane.
When copy work is ready, route it to Lessons Copywriter.

### Handoff Comment

Every handoff comment should say what changed, what the next owner should trust now, and who owns next.

### Publish Return

Keep PR, QR, and follow-up state on the same issue.
Do not call the work done until the current publish state is explicit.

## How To Take A Turn

### Turn Sequence

Read the active issue, the current files, and the upstream contracts your lane depends on.
Do only this lane's job.
Update the current outputs that now matter.
Leave one clear handoff and stop.

### Guardrails

Do not let routing drift away from the active issue.
Do not hand off weak work.

## Inputs

### Current Issue Plan

- Source: Prompt
- Shape: Markdown document
- Requirement: Required

Use the current issue plan to understand the intended owner and next step.

### Current Issue State

- Source: File
- Path: `track_root/_authoring/CURRENT_ISSUE_STATE.md`
- Shape: Markdown document
- Requirement: Required

Use the current issue state to understand the named current files and publish state.

## Outputs

### Project Lead Update

- Target: Tracker Comment
- Issue: `CURRENT_ISSUE`
- Shape: Owner Update Comment
- Requirement: Required

#### Must Include

- What Changed: say what changed on this routing or publish turn.
- Current Source Of Truth: name the current source of truth for the next owner.
- Next Owner: name the honest next owner.

## Routing

### Next Owner If Accepted

- If the issue is ready for copy work -> LessonsCopywriter

### If The Work Is Not Ready

- If the route is still unclear -> LessonsProjectLead

## When To Stop

### Stop Here If

Stop when one honest owner, one honest next step, and the current source of truth are explicit.

## Skills

### Can Run

#### release-followthrough

##### Purpose

Handle PR follow-up, QR updates, publish proof, and same-issue closeout.

##### Use When

Use this when publish or follow-up is the live job.

## When To Use This Role

Use this role when new Lessons work needs routing.
Use this role when publish or follow-up is the live job.

## Standards And Support

### Publish And Follow-Up

Keep the issue explicit about publish intent: ship or prototype.
Do not use publish as a shortcut around current output or review rules.

### GitHub Helpers

Use repo-owned GitHub helpers when the live job needs remote GitHub access.

### Staging QR Helpers

Use repo-owned QR helpers when publish proof depends on current QR state.

### Attached Checkout

Use the attached checkout for product truth only. It does not decide workflow, ownership, or the next step.
````

## File: examples/13_critic_protocol/prompts/AGENTS.prompt
````
# This example asks a narrow question:
# can a minimal critic protocol be expressed cleanly with the language earned in
# `01` through `12`?
#
# This example does not add a critic-specific primitive.
# It models the protocol with:
# - required review inputs
# - one review output that owns both the verdict and the gate log
# - explicit review routes for accepted, changes requested, and escalate
# - optional skills and support guidance
#
# If this reads cleanly, then critic protocol is already expressible with the
# current language surface.


workflow CriticReadFirst: "Read First"
    read_order: "Read Order"
        "Read Your Job first."
        "Then read Workflow Core and How To Take A Turn."
        "Then read Inputs, Outputs, Review Routing, When To Stop, Skills, and Standards And Support."

    current_review_scope: "Current Review Scope"
        "Read the current issue plan, the current dossier, and the current validation record before you issue a verdict."


workflow CriticWorkflowCore: "Workflow Core"
    same_issue_review: "Same-Issue Review"
        "Keep review on the same issue as the producer turn."
        "Judge the current named files, not stale copies or remembered context."

    verdict_rule: "Verdict Rule"
        "Return one explicit verdict: `accept` or `changes requested`."
        "Name the honest next owner for that verdict."

    handoff_rule: "Handoff Rule"
        "If the work is accepted, route the issue forward."
        "If the work is not ready, route it back to the honest producer."
        "If the route is unclear, send it to Project Lead instead of guessing."


workflow CriticHowToTakeATurn: "How To Take A Turn"
    turn_sequence: "Turn Sequence"
        "Read the required review inputs."
        "Check the work against the current issue plan and the named validation record."
        "Write the verdict and gate log."
        "Route the issue to the honest next owner and stop."

    guardrails: "Guardrails"
        "Do not approve work you cannot support from the current review inputs."
        "Do not bounce the work for vague reasons."
        "Do not guess when required review inputs are missing."


workflow CriticStandardsAndSupport: "Standards And Support"
    review_rules: "Review Rules"
        "Judge only the work that is currently in scope for this issue."
        "A failed gate should name the actual missing or incorrect thing."

    evidence_rule: "Evidence Rule"
        "Record the evidence you actually relied on in the gate log."
        "If the validation record is missing or stale, do not pretend the work was validated."

    diff_tools: "Diff Tools"
        "Use repo-owned diff tools when you need to isolate what changed in the current dossier."

    validator_runner: "Validator Runner"
        "Use the named dossier validator when the validation record depends on a rerun."
        "Record the exact command and result in RUN_GATE_LOG.md."


input CurrentIssuePlan: "Current Issue Plan"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required
    "Use the current issue plan to understand the intended acceptance bar and next normal owner."


input SectionDossier: "Section Dossier"
    source: File
        path: "section_root/_authoring/SECTION_DOSSIER.md"
    shape: MarkdownDocument
    requirement: Required
    "Review the current dossier as the main artifact under review."


input DossierValidationRecord: "Dossier Validation Record"
    source: File
        path: "section_root/_authoring/DOSSIER_VALIDATION.md"
    shape: MarkdownDocument
    requirement: Required
    "Use the current validation record to understand what checks ran and what passed or failed."


skill ReviewChecklistSkill: "lesson-review-checklist"
    purpose: "Run the repo's current checklist for critic review of a section dossier."

    use_when: "Use When"
        "Use this when the role needs a repeatable review pass against the current dossier contract."


output CriticReviewOutput: "Critic Review Output"
    files: "Files"
        review_verdict: "Review Verdict"
            path: "section_root/_authoring/REVIEW_VERDICT.md"
            shape: MarkdownDocument

        run_gate_log: "Run Gate Log"
            path: "section_root/_authoring/RUN_GATE_LOG.md"
            shape: MarkdownDocument

    must_include: "Must Include"
        verdict: "Verdict"
            "REVIEW_VERDICT.md must state `accept` or `changes requested` explicitly."

        next_owner: "Next Owner"
            "REVIEW_VERDICT.md must name the honest next owner."

        reason: "Reason"
            "REVIEW_VERDICT.md must give the short reason for the verdict and route."

        gate_results: "Gate Results"
            "RUN_GATE_LOG.md must list every failed gate or say that all named gates passed."

        evidence_used: "Evidence Used"
            "RUN_GATE_LOG.md must record the validation evidence the critic actually relied on."

    standalone_read: "Standalone Read"
        "A downstream reader should be able to read REVIEW_VERDICT.md and RUN_GATE_LOG.md and understand the verdict, route, and review basis."


agent ProjectLead:
    role: "Core job: take the issue back when routing is unclear or when accepted work needs the next normal owner."

    your_job: "Your Job"
        "Take the issue back when the critic says the route is unclear."
        "Own the next normal lane after accepted review."


agent SectionAuthor:
    role: "Core job: revise the dossier when critic review sends the work back."

    your_job: "Your Job"
        "Revise the dossier and validation record when the critic requests changes."


agent AcceptanceCritic:
    role: "Core job: review the current dossier, issue an explicit verdict, and route the same issue honestly."

    your_job: "Your Job"
        "Review the current dossier against the current issue plan."
        "Return one explicit verdict."
        "Write the gate log that supports that verdict."
        "Route the issue to the honest next owner."
        "Stop and escalate instead of guessing when required review inputs are missing."

    read_first: CriticReadFirst
    workflow_core: CriticWorkflowCore
    how_to_take_a_turn: CriticHowToTakeATurn

    inputs: "Inputs"
        CurrentIssuePlan
        SectionDossier
        DossierValidationRecord

    outputs: "Outputs"
        CriticReviewOutput

    review_routing: "Review Routing"
        next_owner_if_accepted: "Next Owner If Accepted"
            route "If accepted" -> ProjectLead

        if_the_work_is_not_ready: "If The Work Is Not Ready"
            route "If changes are required" -> SectionAuthor
            route "If the route is unclear" -> ProjectLead

    when_to_stop: "When To Stop"
        stop_here_if: "Stop Here If"
            "Stop when the verdict is explicit, the next owner is clear, and the gate log matches the actual review basis."

        hard_stop_rule: "Hard Stop Rule"
            "If a required review input is missing, stop and escalate."
            "Do not approve from memory, stale notes, or old copies."

    skills: "Skills"
        can_run: "Can Run"
            skill review_checklist: ReviewChecklistSkill
                requirement: Advisory

    standards_and_support: CriticStandardsAndSupport
````

## File: examples/04_inheritance/prompts/AGENTS.prompt
````
import shared.greeters
import shared.workflows


# This abstract agent lives in the root file so the compile-fail contract can
# still prove that abstract agents do not render, even when the parent is
# imported from another module.
abstract agent ImportedBaseGreeter[shared.greeters.PoliteGreeter]:
    role: "You are the imported base greeter."

    workflow: "Shared Instructions"
        inherit greeting
        inherit courtesy
        inherit object


# These concrete agents inherit from abstract parents defined in imported
# modules. The inheritance model is unchanged; the parent can now be a dotted
# declaration ref instead of only a local name.
agent HelloWorldGreeter[shared.greeters.PoliteGreeter]:
    role: "You are the hello world greeter."

    workflow: "Hello World Instructions"
        inherit greeting
        inherit courtesy
        inherit object


# This is also a concrete leaf agent, and it keeps the shared doctrine from the
# imported parent while replacing the final inherited step.
agent InheritanceDemo[shared.greeters.PoliteGreeter]:
    role: "You are the inheritance demonstration agent."

    workflow: "Inherited Steps"
        "Follow the inherited steps below."
        "This child keeps the shared greeting and replaces the final step."

        inherit greeting
        inherit courtesy

        override object:
            "Say inherited world."


# Imported parents work for named workflow declarations too.
workflow ImportedWorkflowInstructions[shared.workflows.BaseGreeting]: "Imported Workflow Instructions"
    "This workflow inherits its structure from an imported parent."

    inherit greeting

    courtesy: "Courtesy"
        "Keep the tone warm and direct."

    override object:
        "Say imported world."


agent ImportedWorkflowGreeter:
    role: "You are the imported workflow greeter."

    workflow: ImportedWorkflowInstructions
````

## File: examples/07_handoffs/prompts/AGENTS.prompt
````
# Handoff example for next-owner routing.
# This example stays aligned with `05_workflow_merge`:
# - inherited named structure uses explicit patching
# - `inherit key` keeps inherited content in place
# - `override key:` replaces inherited content in place
# - authored workflow slots on agents follow the same explicit patching rule
#
# This shipped example is intentionally narrower than the earlier draft:
# - no critic lane
# - no review-specific routing
# - no routing DSL keywords like `review`, `when_ready`, or `on_reject`
# - the arrow is preserved, but only inside an explicit `route` statement
#
# This example still follows the `06_nested_workflows` rule:
# - simple local workflow structure can stay inline
# - nested, reusable, or inherited structure should live in named workflows
# - agent inheritance should carry named section slots, not anonymous deep trees

workflow ReadFirst: "Read First"
    "Read Your Job first. Then read Workflow Core."


workflow ProjectLeadReadFirst[ReadFirst]: "Read First"
    "Start by reading Your Job."
    "Then read Workflow Core."


workflow SameIssueWorkflowCoreBase: "Workflow Core"
    same_issue_workflow: "Same-Issue Workflow"
        "Keep the work on the same issue."
        "Do only this lane's job."
        "Route to the next owner only when the current lane is honestly ready."
        "If the work is blocked or the route is unclear, return it to Project Lead."

    owner_change_comment: "Owner Change Comment"
        "Every owner-change comment should say:"
        "- what changed"
        "- what the next owner should use now"
        "- the next owner when ownership is changing now"


workflow ResearchSpecialistWorkflowCore[SameIssueWorkflowCoreBase]: "Workflow Core"
    inherit same_issue_workflow

    next_owner: "Next Owner"
        route "When ready" -> WritingSpecialist
        route "If blocked or the route is unclear" -> ProjectLead

    inherit owner_change_comment


workflow WritingSpecialistWorkflowCore[SameIssueWorkflowCoreBase]: "Workflow Core"
    inherit same_issue_workflow

    next_owner: "Next Owner"
        route "When ready" -> ProjectLead
        route "If blocked or the route is unclear" -> ProjectLead

    inherit owner_change_comment


workflow ProjectLeadWorkflowCore[SameIssueWorkflowCoreBase]: "Workflow Core"
    "This file is the runtime guide for a simple multi-agent routing pattern."

    override same_issue_workflow:
        "Keep the whole job on one issue from setup through final return."
        "Keep one owner at a time on that issue."
        "The normal order is Project Lead -> Research Specialist -> Writing Specialist -> Project Lead."
        "Route the first owner change to Research Specialist."
        "After Research Specialist, the next owner is Writing Specialist."
        "After Writing Specialist, the next owner is Project Lead."
        "If the route is broken or the work is blocked before specialist work begins, keep or return the work to Project Lead."

    next_owner: "Next Owner"
        route "When ready to start the work" -> ResearchSpecialist
        route "If the route is broken or the work is blocked before specialist work begins" -> ProjectLead

    override owner_change_comment:
        "Every owner-change comment should say:"
        "- what this turn changed"
        "- the next owner when ownership is changing now"
        "- the exact blocker when the issue is blocked"


workflow ProjectLeadJob: "Your Job"
    "Start the issue with a clear route."
    "Route the first owner change."
    "Keep the issue on a truthful route when work is blocked or routing goes stale."
    "Take the issue back after the final specialist return and close it out honestly."


workflow ResearchSpecialistJob: "Your Job"
    "Take the work only when Project Lead routes it to you."
    "Do the research lane's work."
    "Keep the work ready for the next lane."
    "Do not route the work anywhere except Writing Specialist or Project Lead."


workflow WritingSpecialistJob: "Your Job"
    "Take the work only when Research Specialist hands it to you."
    "Do the writing lane's work."
    "Keep the work within the scope already set upstream."
    "Route the work back to Project Lead when the lane is complete or blocked."


abstract agent SameIssueRole:
    read_first: ReadFirst


# Agent-level authored workflow slots stay explicit.
# - `inherit read_first` keeps the inherited slot unchanged
# - `override read_first: ...` replaces the inherited slot
# - new slots such as `workflow_core` and `your_job` are introduced directly
agent ProjectLead[SameIssueRole]:
    role: "Core job: start the work, route it to Research Specialist, and take it back after Writing Specialist finishes."

    your_job: ProjectLeadJob
    override read_first: ProjectLeadReadFirst
    workflow_core: ProjectLeadWorkflowCore


agent ResearchSpecialist[SameIssueRole]:
    role: "Core job: do the research lane's work and route it to Writing Specialist."

    your_job: ResearchSpecialistJob
    inherit read_first
    workflow_core: ResearchSpecialistWorkflowCore


agent WritingSpecialist[SameIssueRole]:
    role: "Core job: do the writing lane's work and route it back to Project Lead."

    your_job: WritingSpecialistJob
    inherit read_first
    workflow_core: WritingSpecialistWorkflowCore
````

## File: examples/09_outputs/ref/json_file_output_agent/AGENTS.md
````markdown
# JSON File Output Agent

Core job: write the lesson manifest as structured JSON.

## Your Job

- Write the lesson manifest JSON to the required file.

## Outputs

### Lesson Manifest Output

- Built Lesson: `lesson_root/_authoring/lesson_manifest.json`
- Built Lesson Shape: Lesson Manifest JSON
- Validation File: `lesson_root/_authoring/MANIFEST_VALIDATION.md`
- Validation File Shape: MarkdownDocument
- Schema: Lesson Manifest Schema
- Schema Profile: `OpenAIStructuredOutput`
- Schema File: `schemas/lesson_manifest.schema.json`
- Example File: `examples/lesson_manifest.example.json`
- Requirement: Required

#### Must Include

- Built Lesson: the built lesson in `lesson_manifest.json`.
- Route Choice: in `MANIFEST_VALIDATION.md`, name the route chosen for each step.
- Validation Record: in `MANIFEST_VALIDATION.md`, name the exact validation command or commands that ran and what passed or failed.
- Placeholder Copy Status: in `MANIFEST_VALIDATION.md`, say whether placeholder copy is still present.

#### Support Files

- `GUIDED_WALKTHROUGH_LENGTH_REPORT.md` at `lesson_root/GUIDED_WALKTHROUGH_LENGTH_REPORT.md` when guided-walkthrough pacing is in scope.

#### Owns

This output owns the built learner-facing lesson structure, the chosen route for each step, and the validation proof.

#### Standalone Read

A downstream role should be able to read `lesson_manifest.json` and `MANIFEST_VALIDATION.md` and understand what was built and what was validated.

#### Notes

Interpret `lesson_root/...` from the current work context and surrounding instructions.
This example keeps that interpretation as explained guidance, not as a separate root primitive.

Keep validator command details, validator output, and placeholder-copy status in `MANIFEST_VALIDATION.md` unless a modeled support file truly owns them.

#### JSON Schema

See `schemas/lesson_manifest.schema.json`.

#### Field Notes

- `title` is the learner-facing title.
- `steps` is the ordered list of step identifiers.

#### Example

See `examples/lesson_manifest.example.json`.
````

## File: examples/12_role_home_composition/prompts/AGENTS.prompt
````
# This example pressure-tests role-home composition using only current primitives.
#
# It does not introduce a new declaration kind.
# Shared rendered role-home sections are still `workflow` declarations assigned
# to named agent fields such as `read_first` and `workflow_core`.
#
# The role home then mixes those shared workflow slots with the typed agent
# fields introduced in earlier examples:
# - `inputs`
# - `outputs`
# - `skills`
#
# Tool-specific helper guidance stays in support prose. It does not require a
# separate tools field.
#
# When an agent references a skill, point directly at the declared skill and
# attach agent-local metadata there. Do not add an extra wrapper key unless it
# carries real meaning the compiler or renderer actually needs.


workflow LessonsReadFirst: "Read First"
    read_order: "Read Order"
        "Read Your Job first."
        "Then read Workflow Core and How To Take A Turn."
        "Then read Inputs, Outputs, Routing, When To Stop, Skills, When To Use This Role, and Standards And Support."


workflow ProjectLeadReadFirst[LessonsReadFirst]: "Read First"
    inherit read_order

    immediate_local_read: "Immediate Local Read"
        "Read the active issue plan, the latest issue comment that names the current files, and any current PR or QR state before you route or publish."


workflow CopywriterReadFirst[LessonsReadFirst]: "Read First"
    inherit read_order

    immediate_local_read: "Immediate Local Read"
        "Read SECTION_CONCEPTS_AND_TERMS.md, LESSON_PLAN.md, LESSON_SITUATIONS.md, and lesson_manifest.json before you touch reader-facing text."


workflow LessonsWorkflowCore: "Workflow Core"
    read_current_work_state: "Read Current Work State"
        "Start with the active issue, the current plan, and the named current files."
        "Use the attached checkout for product truth only."

    same_issue_workflow: "Same-Issue Workflow"
        "Keep normal Lessons work on one issue from routing through follow-up."
        "Keep one owner at a time on that issue."

    handoff_comment: "Handoff Comment"
        "Every handoff comment should say what changed, what the next owner should trust now, and who owns next."


workflow ProjectLeadWorkflowCore[LessonsWorkflowCore]: "Workflow Core"
    inherit read_current_work_state

    override same_issue_workflow:
        "Keep normal Lessons work on one issue from routing through follow-up."
        "Keep one owner at a time on that issue."
        "Route work to the earliest honest specialist lane."
        "When copy work is ready, route it to Lessons Copywriter."

    inherit handoff_comment

    publish_return: "Publish Return"
        "Keep PR, QR, and follow-up state on the same issue."
        "Do not call the work done until the current publish state is explicit."


workflow CopywriterWorkflowCore[LessonsWorkflowCore]: "Workflow Core"
    inherit read_current_work_state

    override same_issue_workflow:
        "Keep normal Lessons work on one issue from routing through follow-up."
        "Keep one owner at a time on that issue."
        "After the copy lane, return the same issue to Lessons Project Lead."

    inherit handoff_comment


workflow LessonsHowToTakeATurn: "How To Take A Turn"
    turn_sequence: "Turn Sequence"
        "Read the active issue, the current files, and the upstream contracts your lane depends on."
        "Do only this lane's job."
        "Update the current outputs that now matter."
        "Leave one clear handoff and stop."

    guardrails: "Guardrails"
        "Do not let routing drift away from the active issue."
        "Do not hand off weak work."


workflow LessonsStandardsAndSupport: "Standards And Support"
    attached_checkout: "Attached Checkout"
        "Use the attached checkout for product truth only. It does not decide workflow, ownership, or the next step."


workflow ProjectLeadStandardsAndSupport[LessonsStandardsAndSupport]: "Standards And Support"
    publish_and_follow_up: "Publish And Follow-Up"
        "Keep the issue explicit about publish intent: ship or prototype."
        "Do not use publish as a shortcut around current output or review rules."

    github_helpers: "GitHub Helpers"
        "Use repo-owned GitHub helpers when the live job needs remote GitHub access."

    staging_qr_helpers: "Staging QR Helpers"
        "Use repo-owned QR helpers when publish proof depends on current QR state."

    inherit attached_checkout


workflow CopywriterStandardsAndSupport[LessonsStandardsAndSupport]: "Standards And Support"
    domain_grounding: "Domain Grounding"
        "Use reference notes to ground meaning and reviewed examples to ground natural wording."
        "If the grounding is missing, stop and say it is missing."

    copy_standards: "Copy Standards"
        "Keep locked concepts and terms intact."
        "Do not sharpen exact-action claims in copy."

    reference_kb: "Reference KB"
        "Use it for definitions, grounded claim checks, terminology, and domain wording."
        "Do not use it as final expert authority."

    step_json_validator: "Step JSON Validator"
        "Use it after copy changes to validate the changed lesson manifest surfaces."
        "Record the command and result in COPY_GROUNDING.md."

    inherit attached_checkout


workflow ProjectLeadJob: "Your Job"
    "Keep one owner and one obvious next step on the same issue."
    "Keep the issue plan current on routing-only or process-repair turns."
    "Own publish and follow-up state when those are the live jobs."


workflow CopywriterJob: "Your Job"
    "Read the whole lesson before you rewrite isolated strings."
    "Use grounded domain wording without changing the approved structure or authority scope."
    "Record post-copy validation in the current outputs."


workflow ProjectLeadWhenToUse: "When To Use This Role"
    "Use this role when new Lessons work needs routing."
    "Use this role when publish or follow-up is the live job."


workflow CopywriterWhenToUse: "When To Use This Role"
    "Use this role when the manifest already exists and the next job is final reader-facing copy."
    "Expect this lane to stop with current copy outputs ready for return to Project Lead."


input CurrentIssuePlan: "Current Issue Plan"
    source: Prompt
    shape: MarkdownDocument
    requirement: Required
    "Use the current issue plan to understand the intended owner and next step."


input CurrentIssueState: "Current Issue State"
    source: File
        path: "track_root/_authoring/CURRENT_ISSUE_STATE.md"
    shape: MarkdownDocument
    requirement: Required
    "Use the current issue state to understand the named current files and publish state."


input SectionConceptsAndTerms: "Section Concepts And Terms"
    source: File
        path: "section_root/_authoring/SECTION_CONCEPTS_AND_TERMS.md"
    shape: MarkdownDocument
    requirement: Required
    "Use the locked section language before rewriting reader-facing text."


input LessonPlan: "Lesson Plan"
    source: File
        path: "lesson_root/_authoring/LESSON_PLAN.md"
    shape: MarkdownDocument
    requirement: Required
    "Use the approved lesson plan to preserve the lesson's teaching job."


input LessonSituations: "Lesson Situations"
    source: File
        path: "lesson_root/_authoring/LESSON_SITUATIONS.md"
    shape: MarkdownDocument
    requirement: Required
    "Use the approved lesson situations to preserve concrete rep choices."


input LessonManifest: "Lesson Manifest"
    source: File
        path: "lesson_root/_authoring/lesson_manifest.json"
    shape: JsonObject
    requirement: Required
    "Use the current lesson manifest as the editable reader-facing surface."


output shape OwnerUpdateComment: "Owner Update Comment"
    kind: CommentText


output target TrackerComment: "Tracker Comment"
    required: "Required Target Keys"
        issue: "Issue"


output ProjectLeadUpdate: "Project Lead Update"
    target: TrackerComment
        issue: "CURRENT_ISSUE"
    shape: OwnerUpdateComment
    requirement: Required

    must_include: "Must Include"
        what_changed: "What Changed"
            "Say what changed on this routing or publish turn."

        current_truth: "Current Source Of Truth"
            "Name the current source of truth for the next owner."

        next_owner: "Next Owner"
            "Name the honest next owner."


output CopyPassOutput: "Copy Pass Output"
    files: "Files"
        copy_grounding: "Copy Grounding"
            path: "lesson_root/_authoring/COPY_GROUNDING.md"
            shape: MarkdownDocument

        updated_manifest: "Updated Manifest"
            path: "lesson_root/_authoring/lesson_manifest.json"
            shape: JsonObject

    must_include: "Must Include"
        grounding: "Grounding"
            "COPY_GROUNDING.md should show the grounding that shaped the final wording."

        preserved_terms: "Preserved Terms"
            "COPY_GROUNDING.md should name the locked terms that had to survive."

        validation: "Validation"
            "COPY_GROUNDING.md should record what validation ran after the copy pass."

    standalone_read: "Standalone Read"
        "A downstream reader should be able to read COPY_GROUNDING.md and lesson_manifest.json and understand what changed and what was validated."


skill ReleaseFollowthroughSkill: "release-followthrough"
    purpose: "Handle PR follow-up, QR updates, publish proof, and same-issue closeout."

    use_when: "Use When"
        "Use this when publish or follow-up is the live job."


skill DomainGroundingSkill: "domain-grounding-kb"
    purpose: "Ground reader-facing domain wording against current source truth."

    use_when: "Use When"
        "Use this when the lane needs primary-source receipts for reader-facing copy."

    does_not: "Does Not"
        "Does not change the approved structure."
        "Does not establish final expert authority."


skill CopyRewriteSkill: "domain-copy-rewrite"
    purpose: "Rewrite reader-facing domain copy in the repo's expected voice."

    use_when: "Use When"
        "Use this when the job is reader-facing domain wording such as titles, hints, coach text, explanations, and feedback."


abstract agent LessonsRoleHome:
    read_first: LessonsReadFirst
    workflow_core: LessonsWorkflowCore
    how_to_take_a_turn: LessonsHowToTakeATurn
    standards_and_support: LessonsStandardsAndSupport


agent LessonsProjectLead[LessonsRoleHome]:
    role: "Core job: open, route, and finish Lessons issues while keeping publish and follow-up honest on the same issue."

    your_job: ProjectLeadJob
    override read_first: ProjectLeadReadFirst
    override workflow_core: ProjectLeadWorkflowCore
    inherit how_to_take_a_turn

    inputs: "Inputs"
        CurrentIssuePlan
        CurrentIssueState

    outputs: "Outputs"
        ProjectLeadUpdate

    routing: "Routing"
        next_owner_if_accepted: "Next Owner If Accepted"
            route "If the issue is ready for copy work" -> LessonsCopywriter

        if_the_work_is_not_ready: "If The Work Is Not Ready"
            route "If the route is still unclear" -> LessonsProjectLead

    when_to_stop: "When To Stop"
        stop_here_if: "Stop Here If"
            "Stop when one honest owner, one honest next step, and the current source of truth are explicit."

    skills: "Skills"
        can_run: "Can Run"
            skill release_followthrough: ReleaseFollowthroughSkill
                requirement: Advisory

    when_to_use_this_role: ProjectLeadWhenToUse
    override standards_and_support: ProjectLeadStandardsAndSupport


agent LessonsCopywriter[LessonsRoleHome]:
    role: "Core job: turn the approved manifest into grounded reader-facing copy without changing lesson structure or authority scope."

    your_job: CopywriterJob
    override read_first: CopywriterReadFirst
    override workflow_core: CopywriterWorkflowCore
    inherit how_to_take_a_turn

    inputs: "Inputs"
        SectionConceptsAndTerms
        LessonPlan
        LessonSituations
        LessonManifest

    outputs: "Outputs"
        CopyPassOutput

    routing: "Routing"
        next_owner_if_accepted: "Next Owner If Accepted"
            route "If copy and validation are ready" -> LessonsProjectLead

        if_the_work_is_not_ready: "If The Work Is Not Ready"
            route "If grounding is missing or routing is unclear" -> LessonsProjectLead

    when_to_stop: "When To Stop"
        stop_here_if: "Stop Here If"
            "Stop when reader-facing copy and post-copy validation are explicit enough for return to Project Lead."

    skills: "Skills"
        can_run: "Can Run"
            skill domain_grounding: DomainGroundingSkill
                requirement: Required

            skill copy_rewrite: CopyRewriteSkill
                requirement: Advisory

    when_to_use_this_role: CopywriterWhenToUse
    override standards_and_support: CopywriterStandardsAndSupport
````

## File: examples/09_outputs/prompts/AGENTS.prompt
````
# This example shows the shipped output contract surface with reusable supporting
# declarations:
# - `output` is the produced-contract primitive
# - `output target` is the destination kind
# - `output shape` is the structural form
# - `json schema` is the strict machine-readable structure when needed
#
# Simple outputs can stay small.
# Richer outputs can add more contract detail directly on `output`.
# Paths like `section_root/...` and `lesson_root/...` stay plain path strings
# in this example. The model assumes the surrounding turn guidance explains how
# to interpret those prefixes; they are not promoted to separate root
# declarations here.

json schema LessonManifestSchema: "Lesson Manifest Schema"
    profile: OpenAIStructuredOutput
    file: "schemas/lesson_manifest.schema.json"

output shape IssueSummaryText: "Issue Summary Text"
    kind: PlainText


output shape SectionPlanDocument: "Section Plan Document"
    kind: MarkdownDocument


output shape LessonManifestJson: "Lesson Manifest JSON"
    kind: JsonObject

    schema: LessonManifestSchema
    example_file: "examples/lesson_manifest.example.json"

    explanation: "Field Notes"
        "`title` is the learner-facing title."
        "`steps` is the ordered list of step identifiers."


output shape OwnerUpdateComment: "Owner Update Comment"
    kind: CommentText


# A custom target can define its own target-specific keys.
# This keeps the built-in set small while still letting projects define
# destinations like tracker comments.
output target TrackerComment: "Tracker Comment"
    required: "Required Target Keys"
        issue: "Issue"


output IssueSummaryResponse: "Issue Summary Response"
    target: TurnResponse
    shape: IssueSummaryText
    requirement: Required

    purpose: "Purpose"
        "Give a short human-readable summary back in the turn."

    structure: "Expected Structure"
        "State the issue in one or two sentences."
        "End with the main blocker or next step if one matters."


output SectionPlanOutput: "Section Plan Output"
    target: File
        path: "section_root/_authoring/SECTION_PLAN.md"
    shape: SectionPlanDocument
    requirement: Required

    must_include: "Must Include"
        summary: "Summary"
            "Start with a short summary."

        planned_sections: "Planned Sections"
            "List the planned sections in order."

        unresolved_risks: "Unresolved Risks Or Decisions"
            "List unresolved risks or decisions."

    support_files: "Support Files"
        section_flow_audit: "SECTION_FLOW_AUDIT.md"
            path: "section_root/_authoring/SECTION_FLOW_AUDIT.md"
            when: "Use when section sizing or ordering constraints matter."

    standalone_read: "Standalone Read"
        "The next role should be able to read SECTION_PLAN.md alone and understand the current plan."

    path_notes: "Path Notes"
        "Interpret `section_root/...` from the current work context and surrounding instructions."
        "This example keeps that interpretation as explained guidance, not as a separate root primitive."

    example: "Example"
        "# Section Plan"
        "## Summary"
        "..."


output LessonManifestOutput: "Lesson Manifest Output"
    files: "Files"
        manifest: "Built Lesson"
            path: "lesson_root/_authoring/lesson_manifest.json"
            shape: LessonManifestJson

        validation: "Validation File"
            path: "lesson_root/_authoring/MANIFEST_VALIDATION.md"
            shape: MarkdownDocument

    must_include: "Must Include"
        built_lesson: "Built Lesson"
            "The built lesson in lesson_manifest.json."

        route_choice: "Route Choice"
            "In MANIFEST_VALIDATION.md, name the route chosen for each step."

        validation_record: "Validation Record"
            "In MANIFEST_VALIDATION.md, name the exact validation command or commands that ran and what passed or failed."

        placeholder_copy_status: "Placeholder Copy Status"
            "In MANIFEST_VALIDATION.md, say whether placeholder copy is still present."

    support_files: "Support Files"
        guided_walkthrough_length_report: "GUIDED_WALKTHROUGH_LENGTH_REPORT.md"
            path: "lesson_root/GUIDED_WALKTHROUGH_LENGTH_REPORT.md"
            when: "Guided-walkthrough pacing is in scope."

    standalone_read: "Standalone Read"
        "A downstream role should be able to read lesson_manifest.json and MANIFEST_VALIDATION.md and understand what was built and what was validated."

    notes: "Notes"
        "Interpret `lesson_root/...` from the current work context and surrounding instructions."
        "This example keeps that interpretation as explained guidance, not as a separate root primitive."
        "Keep validator command details, validator output, and placeholder-copy status in MANIFEST_VALIDATION.md unless a modeled support file truly owns them."


output ProjectTrackerUpdate: "Project Tracker Update"
    target: TrackerComment
        issue: "CURRENT_ISSUE"
    shape: OwnerUpdateComment
    requirement: Required

    must_include: "Must Include"
        what_changed: "What Changed"
            "Say what changed."

        current_truth: "Current Source Of Truth"
            "Name the current source of truth."

        next_owner: "Next Owner"
            "Name the next owner."

    standalone_read: "Standalone Read"
        "A downstream reader should be able to read this comment alone and understand what changed, what to trust now, and who owns next."

    example: "Example"
        "- changed: updated the section plan"
        "- use now: SECTION_PLAN.md"
        "- next owner: Writing Specialist"


# Model 1: a built-in turn response target.
agent TurnResponseOutputAgent:
    role: "Core job: return a short issue summary in the turn response."

    your_job: "Your Job"
        "Return the issue summary in the turn response."

    outputs: "Outputs"
        IssueSummaryResponse


# Model 2: a built-in file target with a markdown document shape.
agent FileOutputAgent:
    role: "Core job: write the section plan to a markdown file."

    your_job: "Your Job"
        "Write the section plan to the required file."

    outputs: "Outputs"
        SectionPlanOutput


# Model 3: a built-in file target with a stricter JSON output shape.
agent JsonFileOutputAgent:
    role: "Core job: write the lesson manifest as structured JSON."

    your_job: "Your Job"
        "Write the lesson manifest JSON to the required file."

    outputs: "Outputs"
        LessonManifestOutput


# Model 4: a custom output target with target-specific configuration.
agent CustomTargetOutputAgent:
    role: "Core job: leave an owner update on the project tracker."

    your_job: "Your Job"
        "Write the owner update using the custom tracker comment target."

    outputs: "Outputs"
        ProjectTrackerUpdate
````

## File: examples/11_skills_and_tools/prompts/AGENTS.prompt
````
# This example shows top-level `skill` declarations with a small required
# contract.
#
# This direction is intentionally skill-first.
# Do not treat "tell the agent to run this Python script" as a parallel authoring
# pattern. That is a hack around the language, not the intended design.
# If a repeated capability matters enough to name, model it as a skill.
#
# In this direction, every skill must say:
# - `purpose`: the job it helps with
#
# Everything else is optional typed structure layered on top, such as:
# - `use_when`
# - `requires`
# - `provides`
# - `does_not`
#
# This file intentionally shows progressive disclosure:
# - `FindSkills` uses only the required `purpose`
# - `CopyRewriteSkill` adds one optional field
# - `DomainGroundingSkill` shows a fuller optional contract
# - agent-side skill references show `Required`, `Advisory`, and `reason`
#
# The agent then references skill objects by relationship:
# - `can_run`
# - `discover_with`
# - `not_for_this_role`
#
# This example does not model a separate `runtime_tools` section.
# If the role needs a reusable helper and no skill exists yet, the intended move
# is to build the skill, not to smuggle a raw script path into agent guidance.
#
# A `skills` block now gives each skill entry a stable local key:
# - `skill grounding: DomainGroundingSkill`
# - `skill copy_rewrite: CopyRewriteSkill`
# The key is not for display. It exists so shared `skills` blocks can inherit
# and override entries cleanly later.
#
# Requirement belongs on the agent-side reference, not on the skill object.
# - `Required` means the skill must resolve and the turn should fail if the
#   role cannot use it honestly here.
# - `Advisory` means use it when needed if it is available; absence alone is
#   not a turn failure.
# In rendered `AGENTS.md`, do not print schema-like lines such as
# `Requirement: Advisory`.
# - required references should render as fail-loud role guidance
# - advisory references should just render the skill normally

skill FindSkills: "find-skills"
    purpose: "Find the best matching repo skill for the current job."


skill DomainGroundingSkill: "domain-grounding-kb"
    purpose: "Ground reader-facing domain wording against current source truth."

    use_when: "Use When"
        "Use this when the lane needs primary-source receipts for reader-facing copy."

    requires: "Requires"
        "A wording surface or claim that needs domain grounding."

    provides: "Provides"
        "The normal repo workflow for grounding domain wording against current source truth."
        "A clear route for collecting the receipts this lane needs."

    does_not: "Does Not"
        "Does not change the approved structure."
        "Does not establish final expert authority."


skill CopyRewriteSkill: "domain-copy-rewrite"
    purpose: "Rewrite reader-facing domain copy in the repo's expected voice."

    use_when: "Use When"
        "Use this when the job is reader-facing domain wording such as titles, hints, coach text, explanations, and feedback."


skill DeviceRuntimeCheckSkill: "device-runtime-check"
    purpose: "Drive a simulator or device for runtime investigation."


skill DevLoopRestoreSkill: "dev-loop-restore"
    purpose: "Restore a live development loop."

    use_when: "Use When"
        "Use this only when the job is restoring a live development loop."


agent LessonCopywriter:
    role: "Core job: turn an approved lesson manifest into grounded reader copy without changing lesson structure or authority scope."

    your_job: "Your Job"
        "Read the whole lesson before you rewrite isolated strings."
        "Use grounded domain wording without changing the approved structure or authority scope."
        "If no named task skill fits cleanly, discover the right one before you guess."

    skills: "Skills"
        can_run: "Can Run"
            skill grounding: DomainGroundingSkill
                requirement: Required

            skill copy_rewrite: CopyRewriteSkill
                requirement: Advisory

        discover_with: "Discover With"
            skill find_skills: FindSkills
                requirement: Advisory

        not_for_this_role: "Not For This Role"
            skill mobile_sim: DeviceRuntimeCheckSkill
                reason: "This role is baseline copy work, not simulator or device investigation."

            skill dev_loop_restore: DevLoopRestoreSkill
                reason: "This role is baseline copy work, not development environment repair."
````
