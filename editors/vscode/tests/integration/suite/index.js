const assert = require("node:assert/strict");
const path = require("node:path");

const vscode = require("vscode");

const REPO_ROOT = path.resolve(__dirname, "../../../../../");

async function run() {
  await activateDoctrineExtension();
  await testImportLinks();
  await testDefinitionProvider();
  await testAddressableDefinitionProvider();
  await testWorkflowLawDefinitionProvider();
  await testReviewDefinitionProvider();
  await testFullClickableSurface();
}

async function activateDoctrineExtension() {
  const extension = vscode.extensions.getExtension("aelaguiz.doctrine-language");
  assert.ok(extension, "Doctrine extension should be available in the test host.");
  await extension.activate();
}

async function testImportLinks() {
  const document = await openPrompt("examples/03_imports/prompts/AGENTS.prompt");
  const links = await vscode.commands.executeCommand(
    "_executeLinkProvider",
    document.uri,
    100,
  );

  assert.ok(Array.isArray(links), "Document link provider should return an array.");

  assertLinkTarget(
    links,
    document,
    "simple.greeting",
    "examples/03_imports/prompts/simple/greeting.prompt",
  );
  assertLinkTarget(
    links,
    document,
    "chains.relative.entry",
    "examples/03_imports/prompts/chains/relative/entry.prompt",
  );
  assertLinkTarget(
    links,
    document,
    "chains.deep.levels.one.two.entry",
    "examples/03_imports/prompts/chains/deep/levels/one/two/entry.prompt",
  );

  await assertDefinitionTarget({
    declarationSnippet: "import .leaf",
    expectedRelativeTargetPath:
      "examples/03_imports/prompts/chains/relative/entry.prompt",
    relativePath: "examples/03_imports/prompts/AGENTS.prompt",
    sourceLineFragment: "import chains.relative.entry",
    sourceText: "chains.relative.entry",
  });
}

async function testDefinitionProvider() {
  await assertDefinitionTarget({
    declarationSnippet: "workflow RelativeChain",
    expectedRelativeTargetPath:
      "examples/03_imports/prompts/chains/relative/entry.prompt",
    relativePath: "examples/03_imports/prompts/AGENTS.prompt",
    sourceLineFragment: "use relative_chain: chains.relative.entry.RelativeChain",
    sourceText: "chains.relative.entry.RelativeChain",
  });

  await assertDefinitionTarget({
    declarationSnippet: "abstract agent PoliteGreeter",
    expectedRelativeTargetPath:
      "examples/04_inheritance/prompts/shared/greeters.prompt",
    relativePath: "examples/04_inheritance/prompts/AGENTS.prompt",
    sourceLineFragment: "abstract agent ImportedBaseGreeter[shared.greeters.PoliteGreeter]:",
    sourceText: "shared.greeters.PoliteGreeter",
  });

  await assertDefinitionTarget({
    declarationSnippet: "agent AcceptanceCritic",
    expectedRelativeTargetPath:
      "examples/17_agent_mentions/prompts/shared/roles.prompt",
    relativePath: "examples/17_agent_mentions/prompts/AGENTS.prompt",
    sourceLineFragment:
      'route "If the work is ready for review" -> shared.roles.AcceptanceCritic',
    sourceText: "shared.roles.AcceptanceCritic",
  });

  await assertDefinitionTarget({
    declarationSnippet: "inputs ReviewSectionInputs",
    expectedRelativeTargetPath:
      "examples/24_io_block_inheritance/prompts/AGENTS.prompt",
    relativePath: "examples/24_io_block_inheritance/prompts/AGENTS.prompt",
    sourceLineFragment: "inputs: ReviewSectionInputs",
    sourceText: "ReviewSectionInputs",
  });

  await assertDefinitionTarget({
    declarationSnippet: "skill DomainGroundingSkill",
    expectedRelativeTargetPath:
      "examples/11_skills_and_tools/prompts/AGENTS.prompt",
    relativePath: "examples/11_skills_and_tools/prompts/AGENTS.prompt",
    sourceLineFragment: "skill grounding: DomainGroundingSkill",
    sourceText: "DomainGroundingSkill",
  });

  await assertDefinitionTarget({
    declarationSnippet: "output shape IssueSummaryText",
    expectedRelativeTargetPath: "examples/09_outputs/prompts/AGENTS.prompt",
    relativePath: "examples/09_outputs/prompts/AGENTS.prompt",
    sourceLineFragment: "shape: IssueSummaryText",
    sourceText: "IssueSummaryText",
  });
}

async function testAddressableDefinitionProvider() {
  await assertDefinitionTarget({
    declarationSnippet: "output SectionConceptsTermsFileOutput",
    expectedRelativeTargetPath:
      "examples/27_addressable_record_paths/prompts/AGENTS.prompt",
    relativePath: "examples/27_addressable_record_paths/prompts/AGENTS.prompt",
    sourceLineFragment:
      "SectionConceptsTermsFileOutput:must_include.analysis.tables.concept_ladder_table",
    sourceText: "SectionConceptsTermsFileOutput",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'must_include: "Must Include"',
    expectedRelativeTargetPath:
      "examples/27_addressable_record_paths/prompts/AGENTS.prompt",
    relativePath: "examples/27_addressable_record_paths/prompts/AGENTS.prompt",
    sourceLineFragment:
      "SectionConceptsTermsFileOutput:must_include.analysis.tables.concept_ladder_table",
    sourceText: "must_include",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'analysis: "Analysis"',
    expectedRelativeTargetPath:
      "examples/27_addressable_record_paths/prompts/AGENTS.prompt",
    relativePath: "examples/27_addressable_record_paths/prompts/AGENTS.prompt",
    sourceLineFragment:
      "SectionConceptsTermsFileOutput:must_include.analysis.tables.concept_ladder_table",
    sourceText: "analysis",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'tables: "Tables"',
    expectedRelativeTargetPath:
      "examples/27_addressable_record_paths/prompts/AGENTS.prompt",
    relativePath: "examples/27_addressable_record_paths/prompts/AGENTS.prompt",
    sourceLineFragment:
      "SectionConceptsTermsFileOutput:must_include.analysis.tables.concept_ladder_table",
    sourceText: "tables",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'concept_ladder_table: "Concept Ladder Table"',
    expectedRelativeTargetPath:
      "examples/27_addressable_record_paths/prompts/AGENTS.prompt",
    relativePath: "examples/27_addressable_record_paths/prompts/AGENTS.prompt",
    sourceLineFragment:
      "SectionConceptsTermsFileOutput:must_include.analysis.tables.concept_ladder_table",
    sourceText: "concept_ladder_table",
  });

  await assertDefinitionTarget({
    declarationSnippet: "output SectionConceptsTermsFileOutput",
    expectedRelativeTargetPath:
      "examples/27_addressable_record_paths/prompts/AGENTS.prompt",
    relativePath: "examples/27_addressable_record_paths/prompts/AGENTS.prompt",
    sourceLineFragment: "SectionConceptsTermsFileOutput:title",
    sourceText: "title",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'concept_ladder_table: "Concept Ladder Table"',
    expectedRelativeTargetPath:
      "examples/27_addressable_record_paths/prompts/AGENTS.prompt",
    relativePath: "examples/27_addressable_record_paths/prompts/AGENTS.prompt",
    sourceLineFragment:
      "SectionConceptsTermsFileOutput:must_include.analysis.tables.concept_ladder_table.title",
    sourceText: "title",
  });

  await assertDefinitionTarget({
    declarationSnippet: "workflow ReviewRules",
    expectedRelativeTargetPath:
      "examples/28_addressable_workflow_paths/prompts/AGENTS.prompt",
    relativePath: "examples/28_addressable_workflow_paths/prompts/AGENTS.prompt",
    sourceLineFragment: "ReviewRules:gates.build.check_build_honesty",
    sourceText: "ReviewRules",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'gates: "Gates"',
    expectedRelativeTargetPath:
      "examples/28_addressable_workflow_paths/prompts/AGENTS.prompt",
    relativePath: "examples/28_addressable_workflow_paths/prompts/AGENTS.prompt",
    sourceLineFragment: "ReviewRules:gates.build.check_build_honesty",
    sourceText: "gates",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'build: "Build"',
    expectedRelativeTargetPath:
      "examples/28_addressable_workflow_paths/prompts/AGENTS.prompt",
    relativePath: "examples/28_addressable_workflow_paths/prompts/AGENTS.prompt",
    sourceLineFragment: "ReviewRules:gates.build.check_build_honesty",
    sourceText: "build",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'check_build_honesty: "Check Build Honesty"',
    expectedRelativeTargetPath:
      "examples/28_addressable_workflow_paths/prompts/AGENTS.prompt",
    relativePath: "examples/28_addressable_workflow_paths/prompts/AGENTS.prompt",
    sourceLineFragment: "ReviewRules:gates.build.check_build_honesty",
    sourceText: "check_build_honesty",
  });

  await assertDefinitionTarget({
    declarationSnippet: "enum CriticVerdict",
    expectedRelativeTargetPath: "examples/29_enums/prompts/AGENTS.prompt",
    relativePath: "examples/29_enums/prompts/AGENTS.prompt",
    sourceLineFragment:
      "Use the {{CriticVerdict}} vocabulary and return {{CriticVerdict:accept}} or {{CriticVerdict:changes_requested}}.",
    sourceText: "CriticVerdict",
    occurrence: 2,
  });

  await assertDefinitionTarget({
    declarationSnippet: 'accept: "accept"',
    expectedRelativeTargetPath: "examples/29_enums/prompts/AGENTS.prompt",
    relativePath: "examples/29_enums/prompts/AGENTS.prompt",
    sourceLineFragment:
      "Use the {{CriticVerdict}} vocabulary and return {{CriticVerdict:accept}} or {{CriticVerdict:changes_requested}}.",
    sourceText: "accept",
  });

  await assertDefinitionTarget({
    declarationSnippet: "skills SharedSkills",
    expectedRelativeTargetPath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    relativePath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    sourceLineFragment:
      '"Keep {{SharedSkills:can_run.grounding}} available before you act."',
    sourceText: "SharedSkills",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'can_run: "Can Run"',
    expectedRelativeTargetPath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    relativePath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    sourceLineFragment:
      '"Keep {{SharedSkills:can_run.grounding}} available before you act."',
    sourceText: "can_run",
  });

  await assertDefinitionTarget({
    declarationSnippet: "skill grounding: GroundingSkill",
    expectedRelativeTargetPath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    relativePath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    sourceLineFragment:
      '"Keep {{SharedSkills:can_run.grounding}} available before you act."',
    sourceText: "grounding",
  });

  await assertDefinitionTarget({
    declarationSnippet: "workflow ReviewRules",
    expectedRelativeTargetPath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    relativePath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    sourceLineFragment: "WorkflowRoot:shared.title",
    sourceText: "title",
  });

  await assertDefinitionTarget({
    declarationSnippet: "skills SharedSkills",
    expectedRelativeTargetPath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    relativePath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    sourceLineFragment: "WorkflowRoot:skills.title",
    sourceText: "title",
  });

  await assertDefinitionTarget({
    declarationSnippet: "workflow WorkflowRoot",
    expectedRelativeTargetPath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    relativePath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    sourceLineFragment: "WorkflowRoot:shared.gates.build.check_build_honesty",
    sourceText: "WorkflowRoot",
  });

  await assertDefinitionTarget({
    declarationSnippet: "use shared: ReviewRules",
    expectedRelativeTargetPath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    relativePath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    sourceLineFragment: "WorkflowRoot:shared.gates.build.check_build_honesty",
    sourceText: "shared",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'gates: "Gates"',
    expectedRelativeTargetPath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    relativePath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    sourceLineFragment: "WorkflowRoot:shared.gates.build.check_build_honesty",
    sourceText: "gates",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'build: "Build"',
    expectedRelativeTargetPath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    relativePath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    sourceLineFragment: "WorkflowRoot:shared.gates.build.check_build_honesty",
    sourceText: "build",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'check_build_honesty: "Check Build Honesty"',
    expectedRelativeTargetPath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    relativePath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    sourceLineFragment: "WorkflowRoot:shared.gates.build.check_build_honesty",
    sourceText: "check_build_honesty",
  });

  await assertDefinitionTarget({
    declarationSnippet: "skills: SharedSkills",
    expectedRelativeTargetPath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    relativePath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    sourceLineFragment: "WorkflowRoot:skills.can_run.grounding",
    sourceText: "skills",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'can_run: "Can Run"',
    expectedRelativeTargetPath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    relativePath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    sourceLineFragment: "WorkflowRoot:skills.can_run.grounding",
    sourceText: "can_run",
  });

  await assertDefinitionTarget({
    declarationSnippet: "skill grounding: GroundingSkill",
    expectedRelativeTargetPath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    relativePath:
      "examples/28_addressable_workflow_paths/prompts/SELF_AND_DESCENT.prompt",
    sourceLineFragment: "WorkflowRoot:skills.can_run.grounding",
    sourceText: "grounding",
  });
}

async function testWorkflowLawDefinitionProvider() {
  await assertDefinitionTarget({
    declarationSnippet: 'current_artifact: "Current Artifact"',
    expectedRelativeTargetPath:
      "examples/31_currentness_and_trust_surface/prompts/AGENTS.prompt",
    relativePath: "examples/31_currentness_and_trust_surface/prompts/AGENTS.prompt",
    sourceLineFragment:
      "current artifact ApprovedPlan via CoordinationHandoff.current_artifact",
    sourceText: "current_artifact",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'rewrite_exclusions: "Rewrite Evidence Exclusions"',
    expectedRelativeTargetPath:
      "examples/37_law_reuse_and_patching/prompts/AGENTS.prompt",
    relativePath: "examples/37_law_reuse_and_patching/prompts/AGENTS.prompt",
    sourceLineFragment:
      "rewrite_exclusions when CurrentHandoff.rewrite_regime == RewriteRegime.rewrite",
    sourceText: "rewrite_exclusions",
  });

  await assertDefinitionTarget({
    declarationSnippet: "enum EditMode",
    expectedRelativeTargetPath: "examples/32_modes_and_match/prompts/AGENTS.prompt",
    relativePath: "examples/32_modes_and_match/prompts/AGENTS.prompt",
    sourceLineFragment: "mode edit_mode = CurrentHandoff.active_mode as EditMode",
    sourceText: "EditMode",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'manifest_title: "manifest-title"',
    expectedRelativeTargetPath: "examples/32_modes_and_match/prompts/AGENTS.prompt",
    relativePath: "examples/32_modes_and_match/prompts/AGENTS.prompt",
    sourceLineFragment: "EditMode.manifest_title:",
    sourceText: "manifest_title",
  });

  await assertDefinitionTarget({
    declarationSnippet: "reroute_on_unclear:",
    expectedRelativeTargetPath:
      "examples/37_law_reuse_and_patching/prompts/AGENTS.prompt",
    relativePath: "examples/37_law_reuse_and_patching/prompts/AGENTS.prompt",
    sourceLineFragment: "inherit reroute_on_unclear",
    sourceText: "reroute_on_unclear",
  });

  await assertDefinitionTarget({
    declarationSnippet: "agent RoutingOwner",
    expectedRelativeTargetPath:
      "examples/37_law_reuse_and_patching/prompts/AGENTS.prompt",
    relativePath: "examples/37_law_reuse_and_patching/prompts/AGENTS.prompt",
    sourceLineFragment:
      'route "Route the same issue back to RoutingOwner." -> RoutingOwner',
    sourceText: "RoutingOwner",
    occurrence: 2,
  });

  await assertDefinitionTarget({
    declarationSnippet: 'rewrite_mode: "Rewrite Mode" when RouteFacts.section_status in {"new", "full_rewrite"}:',
    expectedRelativeTargetPath:
      "examples/39_guarded_output_sections/prompts/AGENTS.prompt",
    relativePath: "examples/39_guarded_output_sections/prompts/AGENTS.prompt",
    sourceLineFragment:
      "Read {{GuardedReadbackComment:rewrite_mode.title}} and {{GuardedReadbackComment:repeated_problem.title}} when the conditional readback matters for this turn.",
    sourceText: "rewrite_mode",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'rewrite_detail: "Rewrite Detail" when RouteFacts.section_status in {"new", "full_rewrite"}:',
    expectedRelativeTargetPath:
      "examples/39_guarded_output_sections/prompts/AGENTS.prompt",
    relativePath: "examples/39_guarded_output_sections/prompts/AGENTS.prompt",
    sourceLineFragment:
      "Read {{NestedGuardedReadbackComment:detail_panel.status_summary.title}} before {{NestedGuardedReadbackComment:detail_panel.rewrite_detail.title}} when nested conditional detail is in play.",
    sourceText: "rewrite_detail",
  });

  await assertDefinitionTarget({
    declarationSnippet: "agent RoutingOwner",
    expectedRelativeTargetPath:
      "examples/42_route_only_handoff_capstone/prompts/AGENTS.prompt",
    relativePath: "examples/42_route_only_handoff_capstone/prompts/AGENTS.prompt",
    sourceLineFragment:
      'route "Keep the issue on RoutingOwner until the next specialist owner is actually justified." -> RoutingOwner when RouteFacts.next_owner_unknown',
    sourceText: "RoutingOwner",
    occurrence: 2,
  });
}

async function testReviewDefinitionProvider() {
  await assertDefinitionTarget({
    declarationSnippet: "review DraftReview",
    expectedRelativeTargetPath:
      "examples/43_review_basic_verdict_and_route_coupling/prompts/AGENTS.prompt",
    relativePath:
      "examples/43_review_basic_verdict_and_route_coupling/prompts/AGENTS.prompt",
    sourceLineFragment: "review: DraftReview",
    sourceText: "DraftReview",
  });

  await assertDefinitionTarget({
    declarationSnippet: "workflow DraftReviewContract",
    expectedRelativeTargetPath:
      "examples/43_review_basic_verdict_and_route_coupling/prompts/AGENTS.prompt",
    relativePath:
      "examples/43_review_basic_verdict_and_route_coupling/prompts/AGENTS.prompt",
    sourceLineFragment:
      'accept "The shared draft review contract passes." when contract.passes',
    sourceText: "contract",
    occurrence: 2,
  });

  await assertDefinitionTarget({
    declarationSnippet: 'failure_detail: "Failure Detail" when verdict == ReviewVerdict.changes_requested:',
    expectedRelativeTargetPath:
      "examples/43_review_basic_verdict_and_route_coupling/prompts/AGENTS.prompt",
    relativePath:
      "examples/43_review_basic_verdict_and_route_coupling/prompts/AGENTS.prompt",
    sourceLineFragment: "failing_gates: failure_detail.failing_gates",
    sourceText: "failure_detail",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'clarity: "Clarity"',
    expectedRelativeTargetPath: "examples/49_review_capstone/prompts/AGENTS.prompt",
    relativePath: "examples/49_review_capstone/prompts/AGENTS.prompt",
    sourceLineFragment:
      '"Summarize the review analysis that led to the verdict, including how {{fields.reviewed_artifact}} did or did not satisfy {{contract.clarity}}, plus any preserved boundary, comparison-only help, and rewrite-evidence exclusions that mattered."',
    sourceText: "clarity",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'reviewed_artifact: "Reviewed Artifact"',
    expectedRelativeTargetPath: "examples/49_review_capstone/prompts/AGENTS.prompt",
    relativePath: "examples/49_review_capstone/prompts/AGENTS.prompt",
    sourceLineFragment:
      '"Summarize the review analysis that led to the verdict, including how {{fields.reviewed_artifact}} did or did not satisfy {{contract.clarity}}, plus any preserved boundary, comparison-only help, and rewrite-evidence exclusions that mattered."',
    sourceText: "reviewed_artifact",
  });
}

async function testFullClickableSurface() {
  await assertDefinitionTarget({
    declarationSnippet: "workflow ProjectLeadJob",
    expectedRelativeTargetPath: "examples/07_handoffs/prompts/AGENTS.prompt",
    relativePath: "examples/07_handoffs/prompts/AGENTS.prompt",
    sourceLineFragment: "your_job: ProjectLeadJob",
    sourceText: "ProjectLeadJob",
  });

  await assertDefinitionTarget({
    declarationSnippet: "workflow ProjectLeadReadFirst",
    expectedRelativeTargetPath: "examples/07_handoffs/prompts/AGENTS.prompt",
    relativePath: "examples/07_handoffs/prompts/AGENTS.prompt",
    sourceLineFragment: "override read_first: ProjectLeadReadFirst",
    sourceText: "ProjectLeadReadFirst",
  });

  await assertDefinitionTarget({
    declarationSnippet: "workflow RevisedDelivery",
    expectedRelativeTargetPath: "examples/06_nested_workflows/prompts/AGENTS.prompt",
    relativePath: "examples/06_nested_workflows/prompts/AGENTS.prompt",
    sourceLineFragment: "override delivery: RevisedDelivery",
    sourceText: "RevisedDelivery",
  });

  await assertDefinitionTarget({
    declarationSnippet: "skills SharedSkills",
    expectedRelativeTargetPath:
      "examples/21_first_class_skills_blocks/prompts/AGENTS.prompt",
    relativePath: "examples/21_first_class_skills_blocks/prompts/AGENTS.prompt",
    sourceLineFragment: "skills: SharedSkills",
    sourceText: "SharedSkills",
  });

  await assertDefinitionTarget({
    declarationSnippet: "inputs BaseSectionInputs",
    expectedRelativeTargetPath:
      "examples/25_abstract_agent_io_override/prompts/AGENTS.prompt",
    relativePath: "examples/25_abstract_agent_io_override/prompts/AGENTS.prompt",
    sourceLineFragment: 'inputs[BaseSectionInputs]: "Your Inputs"',
    sourceText: "BaseSectionInputs",
  });

  await assertDefinitionTarget({
    declarationSnippet: "json schema LessonManifestSchema",
    expectedRelativeTargetPath: "examples/09_outputs/prompts/AGENTS.prompt",
    relativePath: "examples/09_outputs/prompts/AGENTS.prompt",
    sourceLineFragment: "schema: LessonManifestSchema",
    sourceText: "LessonManifestSchema",
  });

  await assertDefinitionTarget({
    declarationSnippet: "input ScopedCatalogTruth",
    expectedRelativeTargetPath:
      "examples/24_io_block_inheritance/prompts/AGENTS.prompt",
    relativePath: "examples/24_io_block_inheritance/prompts/AGENTS.prompt",
    sourceLineFragment: "ScopedCatalogTruth",
    sourceText: "ScopedCatalogTruth",
    occurrence: 1,
  });

  await assertDefinitionTarget({
    declarationSnippet: "output CoordinationHandoff",
    expectedRelativeTargetPath:
      "examples/24_io_block_inheritance/prompts/AGENTS.prompt",
    relativePath: "examples/24_io_block_inheritance/prompts/AGENTS.prompt",
    sourceLineFragment: "CoordinationHandoff",
    sourceText: "CoordinationHandoff",
    occurrence: 1,
  });

  await assertDefinitionTarget({
    declarationSnippet: "input CurrentIssuePlan",
    expectedRelativeTargetPath:
      "examples/15_workflow_body_refs/prompts/shared/contracts.prompt",
    relativePath: "examples/15_workflow_body_refs/prompts/AGENTS.prompt",
    sourceLineFragment: "shared.contracts.CurrentIssuePlan",
    sourceText: "shared.contracts.CurrentIssuePlan",
  });

  await assertDefinitionTarget({
    declarationSnippet: "input TrackMetadata",
    expectedRelativeTargetPath:
      "examples/16_workflow_string_interpolation/prompts/shared/contracts.prompt",
    relativePath: "examples/16_workflow_string_interpolation/prompts/AGENTS.prompt",
    sourceLineFragment: "{{shared.contracts.TrackMetadata:source.path}}",
    sourceText: "shared.contracts.TrackMetadata",
  });

  await assertDefinitionTarget({
    declarationSnippet: "input CurrentPlan",
    expectedRelativeTargetPath:
      "examples/20_authored_prose_interpolation/prompts/AGENTS.prompt",
    relativePath: "examples/20_authored_prose_interpolation/prompts/AGENTS.prompt",
    sourceLineFragment: "{{CurrentPlan:source.path}}",
    sourceText: "CurrentPlan",
  });

  await assertDefinitionTarget({
    declarationSnippet: "agent ProjectLead",
    expectedRelativeTargetPath:
      "examples/20_authored_prose_interpolation/prompts/AGENTS.prompt",
    relativePath: "examples/20_authored_prose_interpolation/prompts/AGENTS.prompt",
    sourceLineFragment: 'route "If {{ProjectLead}} must step in" -> ProjectLead',
    sourceText: "ProjectLead",
  });

  await assertDefinitionTarget({
    declarationSnippet: "read_first: SharedReadFirst",
    expectedRelativeTargetPath:
      "examples/26_abstract_authored_slots/prompts/AGENTS.prompt",
    relativePath: "examples/26_abstract_authored_slots/prompts/AGENTS.prompt",
    sourceLineFragment: "inherit read_first",
    sourceText: "read_first",
  });

  await assertDefinitionTarget({
    declarationSnippet: "use preparation: Preparation",
    expectedRelativeTargetPath: "examples/06_nested_workflows/prompts/AGENTS.prompt",
    relativePath: "examples/06_nested_workflows/prompts/AGENTS.prompt",
    sourceLineFragment: "inherit preparation",
    sourceText: "preparation",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'support: "Support"',
    expectedRelativeTargetPath:
      "examples/22_skills_block_inheritance/prompts/AGENTS.prompt",
    relativePath: "examples/22_skills_block_inheritance/prompts/AGENTS.prompt",
    sourceLineFragment: 'override support: "Support"',
    sourceText: "support",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'coordination_handoff: "Coordination Handoff"',
    expectedRelativeTargetPath:
      "examples/24_io_block_inheritance/prompts/AGENTS.prompt",
    relativePath: "examples/24_io_block_inheritance/prompts/AGENTS.prompt",
    sourceLineFragment: 'override coordination_handoff: "Coordination Handoff"',
    sourceText: "coordination_handoff",
  });

  await assertDefinitionTarget({
    declarationSnippet: 'continuity_only: "Continuity Only"',
    expectedRelativeTargetPath:
      "examples/25_abstract_agent_io_override/prompts/AGENTS.prompt",
    relativePath: "examples/25_abstract_agent_io_override/prompts/AGENTS.prompt",
    sourceLineFragment: 'override continuity_only: "Continuity Only"',
    sourceText: "continuity_only",
  });
}

async function openPrompt(relativePath) {
  const promptPath = path.join(REPO_ROOT, relativePath);
  const document = await vscode.workspace.openTextDocument(promptPath);
  await vscode.window.showTextDocument(document);
  return document;
}

function assertLinkTarget(links, document, linkText, expectedRelativeTargetPath) {
  const position = positionForText(document, linkText);
  const link = links.find((candidate) => rangeContains(candidate.range, position));
  assert.ok(link, `Expected a link for ${linkText}.`);

  const linkTarget = link.url || link.target;
  const linkTargetPath =
    typeof linkTarget === "string"
      ? vscode.Uri.parse(linkTarget).fsPath
      : linkTarget.fsPath;

  assert.equal(
    linkTargetPath,
    path.join(REPO_ROOT, expectedRelativeTargetPath),
    `Expected ${linkText} to resolve to ${expectedRelativeTargetPath}.`,
  );
}

async function assertDefinitionTarget({
  declarationSnippet,
  expectedRelativeTargetPath,
  occurrence = 1,
  relativePath,
  sourceLineFragment,
  sourceText,
}) {
  const document = await openPrompt(relativePath);
  const definitions = await vscode.commands.executeCommand(
    "vscode.executeDefinitionProvider",
    document.uri,
    sourceLineFragment
      ? positionForLineText(document, sourceLineFragment, sourceText, occurrence)
      : positionForText(document, sourceText),
  );

  assert.ok(
    Array.isArray(definitions) && definitions.length > 0,
    `Expected a definition for ${sourceText}.`,
  );

  const definition = definitions[0];
  const targetUri = definition.targetUri || definition.uri;
  const targetSelectionRange =
    definition.targetSelectionRange || definition.range;
  const targetDocument = await vscode.workspace.openTextDocument(targetUri);
  const targetLine = targetDocument.lineAt(targetSelectionRange.start.line).text;

  assert.equal(
    targetUri.fsPath,
    path.join(REPO_ROOT, expectedRelativeTargetPath),
    `Expected ${sourceText} to resolve to ${expectedRelativeTargetPath}.`,
  );
  assert.ok(
    targetLine.includes(declarationSnippet),
    `Expected ${sourceText} to land on ${declarationSnippet}, but got: ${targetLine}`,
  );
}

function positionForText(document, text, occurrence = 1) {
  const source = document.getText();
  let offset = -1;
  let searchFrom = 0;

  for (let index = 0; index < occurrence; index += 1) {
    offset = source.indexOf(text, searchFrom);
    assert.notEqual(
      offset,
      -1,
      `Expected to find occurrence ${occurrence} of ${text} in the test document.`,
    );
    searchFrom = offset + text.length;
  }

  return document.positionAt(offset + 1);
}

function positionForLineText(document, lineFragment, text, occurrence = 1) {
  let fallbackLineNumber = -1;

  for (let lineNumber = 0; lineNumber < document.lineCount; lineNumber += 1) {
    const lineText = document.lineAt(lineNumber).text;
    const exactMatch = lineText.trim() === lineFragment.trim();
    const partialMatch = lineText.includes(lineFragment);
    if (!exactMatch && !partialMatch) {
      continue;
    }

    if (!exactMatch) {
      if (fallbackLineNumber === -1) {
        fallbackLineNumber = lineNumber;
      }
      continue;
    }

    return positionForLineOccurrence(document, lineNumber, lineText, lineFragment, text, occurrence);
  }

  if (fallbackLineNumber !== -1) {
    const lineText = document.lineAt(fallbackLineNumber).text;
    return positionForLineOccurrence(
      document,
      fallbackLineNumber,
      lineText,
      lineFragment,
      text,
      occurrence,
    );
  }

  assert.fail(`Expected to find a line containing ${lineFragment}.`);
}

function positionForLineOccurrence(
  document,
  lineNumber,
  lineText,
  lineFragment,
  text,
  occurrence,
) {
  let startCharacter = -1;
  let searchFrom = 0;
  for (let index = 0; index < occurrence; index += 1) {
    startCharacter = lineText.indexOf(text, searchFrom);
    assert.notEqual(
      startCharacter,
      -1,
      `Expected occurrence ${occurrence} of ${text} on the line containing ${lineFragment}.`,
    );
    searchFrom = startCharacter + text.length;
  }
  assert.notEqual(
    startCharacter,
    -1,
    `Expected ${text} to appear on the line containing ${lineFragment}.`,
  );
  return new vscode.Position(lineNumber, startCharacter + 1);
}

function rangeContains(rangeLike, position) {
  const range =
    rangeLike.start && rangeLike.end
      ? new vscode.Range(
          new vscode.Position(
            rangeLike.start.line,
            rangeLike.start.character,
          ),
          new vscode.Position(rangeLike.end.line, rangeLike.end.character),
        )
      : new vscode.Range(
          new vscode.Position(
            rangeLike.startLineNumber - 1,
            rangeLike.startColumn - 1,
          ),
          new vscode.Position(
            rangeLike.endLineNumber - 1,
            rangeLike.endColumn - 1,
          ),
        );
  return range.contains(position);
}

module.exports = {
  run,
};
