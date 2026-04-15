const fs = require("node:fs");
const path = require("node:path");
const TOML = require("@iarna/toml");

const vscode = require("vscode");

const IDENTIFIER_PATTERN = "[A-Za-z_][A-Za-z0-9_]*";
const DOTTED_NAME_PATTERN = `${IDENTIFIER_PATTERN}(?:\\.${IDENTIFIER_PATTERN})*`;
const IMPORT_PATH_PATTERN = `(?:\\.+)?${DOTTED_NAME_PATTERN}`;
const STRING_PATTERN = "\"(?:\\\\.|[^\"\\\\])*\"";
const STRING_OR_EMPTY_PATTERN = `(?:${STRING_PATTERN})?`;
const PATH_REF_PATTERN = `${DOTTED_NAME_PATTERN}:${DOTTED_NAME_PATTERN}`;
const NAME_REF_RE = new RegExp(`^${DOTTED_NAME_PATTERN}$`);
const INTERPOLATION_RE = /\{\{([^{}]+)\}\}/g;
const INTERPOLATION_EXPR_RE = new RegExp(
  `^\\s*(${DOTTED_NAME_PATTERN})(?:\\s*:\\s*(${DOTTED_NAME_PATTERN}))?\\s*$`,
);

const IMPORT_LINE_RE = new RegExp(
  `^\\s*import\\s+(${IMPORT_PATH_PATTERN})\\s*$`,
);
const INHERITED_AGENT_RE = new RegExp(
  `^\\s*(?:abstract\\s+)?agent\\s+${IDENTIFIER_PATTERN}\\s*\\[(${DOTTED_NAME_PATTERN})\\]\\s*:\\s*${STRING_OR_EMPTY_PATTERN}\\s*$`,
);
const ENUM_MEMBER_RE = new RegExp(
  `^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*(${STRING_PATTERN})\\s*$`,
);
const ENUM_MEMBER_WIRE_RE = new RegExp(
  `^\\s*wire\\s*:\\s*(${STRING_PATTERN})\\s*$`,
);
const INHERITED_BLOCK_RE = new RegExp(
  `^\\s*(review|analysis|schema|document|workflow|skills|inputs|outputs|output)\\s+${IDENTIFIER_PATTERN}\\s*\\[(${DOTTED_NAME_PATTERN})\\]\\s*:`,
);
const PATCH_FIELD_RE = new RegExp(
  `^\\s*(inputs|outputs)\\s*\\[(${DOTTED_NAME_PATTERN})\\]\\s*:\\s*${STRING_PATTERN}\\s*$`,
);
const ROUTE_RE = new RegExp(
  `^(\\s*route\\s+\")((?:[^\"\\\\]|\\\\.)*)(\"\\s*->\\s*)(${DOTTED_NAME_PATTERN})(?:\\s+when\\b.*)?\\s*$`,
);
const USE_RE = new RegExp(
  `^\\s*use\\s+(${IDENTIFIER_PATTERN})\\s*:\\s*(${DOTTED_NAME_PATTERN})\\s*$`,
);
const TOP_LEVEL_FIELD_REF_RE = new RegExp(
  `^\\s*(analysis|decision|skills|inputs|outputs|final_output)\\s*:\\s*(${DOTTED_NAME_PATTERN})\\s*$`,
);
const KEYED_DECL_REF_RE = new RegExp(
  `^\\s*(source|target|shape|schema|structure|render_profile)\\s*:\\s*(${DOTTED_NAME_PATTERN})\\s*$`,
);
const AGENT_SLOT_REF_RE = new RegExp(
  `^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*(${DOTTED_NAME_PATTERN})\\s*$`,
);
const OVERRIDE_REF_RE = new RegExp(
  `^\\s*override\\s+(${IDENTIFIER_PATTERN})\\s*:\\s*(${DOTTED_NAME_PATTERN})\\s*$`,
);
const SKILL_ENTRY_RE = new RegExp(
  `^\\s*skill\\s+(${IDENTIFIER_PATTERN})\\s*:\\s*(${DOTTED_NAME_PATTERN})\\s*$`,
);
const INHERIT_RE = new RegExp(`^\\s*inherit\\s+(${IDENTIFIER_PATTERN})\\s*$`);
const ABSTRACT_FIELD_RE = new RegExp(
  `^\\s*abstract\\s+(${IDENTIFIER_PATTERN})\\s*$`,
);
const STANDALONE_REF_RE = new RegExp(
  `^\\s+(${DOTTED_NAME_PATTERN})\\s*$`,
);
const STANDALONE_PATH_REF_RE = new RegExp(
  `^\\s*(${DOTTED_NAME_PATTERN}):(${DOTTED_NAME_PATTERN})\\s*$`,
);
const KEY_VALUE_PATH_REF_RE = new RegExp(
  `^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*(${DOTTED_NAME_PATTERN}):(${DOTTED_NAME_PATTERN})\\s*$`,
);
const WORKFLOW_SKILLS_REF_RE = new RegExp(
  `^\\s*skills\\s*:\\s*(${DOTTED_NAME_PATTERN})\\s*$`,
);
const OVERRIDE_BODY_RE = new RegExp(
  `^\\s*override\\s+(${IDENTIFIER_PATTERN})\\s*:\\s*${STRING_OR_EMPTY_PATTERN}\\s*$`,
);
const LAW_FIELD_RE = /^\s*law\s*:\s*$/;
const TRUST_SURFACE_FIELD_RE = /^\s*trust_surface\s*:\s*$/;
const REVIEW_FIELDS_FIELD_RE = /^\s*fields\s*:\s*$/;
const REVIEW_SUBJECT_MAP_FIELD_RE = /^\s*subject_map\s*:\s*$/;
const REVIEW_OUTCOME_HEADER_RE = /^\s*(on_accept|on_reject)\s*:\s*(?:"(?:\\.|[^"\\])*")?\s*$/;
const REVIEW_OVERRIDE_FIELDS_RE = /^\s*override\s+fields\s*:\s*$/;
const REVIEW_OVERRIDE_OUTCOME_RE = /^\s*override\s+(on_accept|on_reject)\s*:\s*(?:"(?:\\.|[^"\\])*")?\s*$/;
const REVIEW_CONFIG_REF_RE = new RegExp(
  `^\\s*(subject|contract|comment_output)\\s*:\\s*(${DOTTED_NAME_PATTERN})\\s*$`,
);
const REVIEW_FIELD_BINDING_RE = new RegExp(
  `^\\s*(verdict|reviewed_artifact|analysis|readback|current_artifact|failing_gates|blocked_gate|next_owner|active_mode|trigger_reason)\\s*:\\s*(${DOTTED_NAME_PATTERN})\\s*$`,
);
const REVIEW_SUBJECT_MAP_ENTRY_RE = new RegExp(
  `^\\s*(${DOTTED_NAME_PATTERN})\\s*:\\s*(${DOTTED_NAME_PATTERN})\\s*$`,
);
const REVIEW_SECTION_RE = new RegExp(
  `^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*${STRING_PATTERN}\\s*$`,
);
const REVIEW_OVERRIDE_SECTION_RE = new RegExp(
  `^\\s*override\\s+(${IDENTIFIER_PATTERN})\\s*:\\s*(?:${STRING_PATTERN})?\\s*$`,
);
const ANALYSIS_SECTION_RE = new RegExp(
  `^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*${STRING_PATTERN}\\s*$`,
);
const ANALYSIS_OVERRIDE_SECTION_RE = new RegExp(
  `^\\s*override\\s+(${IDENTIFIER_PATTERN})\\s*:\\s*(?:${STRING_PATTERN})?\\s*$`,
);
const ANALYSIS_CLASSIFY_RE = new RegExp(
  `^\\s*classify\\s+${STRING_PATTERN}\\s+as\\s+(${DOTTED_NAME_PATTERN})\\s*$`,
);
const SCHEMA_BLOCK_FIELD_RE = /^\s*(sections|gates|artifacts|groups)\s*:\s*$/;
const SCHEMA_INHERIT_BLOCK_RE = /^\s*inherit\s+(sections|gates|artifacts|groups)\s*$/;
const SCHEMA_OVERRIDE_BLOCK_RE = /^\s*override\s+(sections|gates|artifacts|groups)\s*:\s*$/;
const SCHEMA_ITEM_RE = new RegExp(
  `^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*(${STRING_PATTERN})\\s*$`,
);
const SCHEMA_ARTIFACT_REF_RE = new RegExp(
  `^\\s*ref\\s*:\\s*(${DOTTED_NAME_PATTERN})\\s*$`,
);
const SCHEMA_GROUP_MEMBER_RE = new RegExp(`^\\s*(${IDENTIFIER_PATTERN})\\s*$`);
const DOCUMENT_BLOCK_RE = new RegExp(
  `^\\s*(section|sequence|bullets|checklist|definitions|properties|table|guard|callout|code|markdown|html|footnotes|image|rule)\\s+(${IDENTIFIER_PATTERN})\\s*(?::\\s*${STRING_PATTERN})?(?:\\s+.+)?\\s*$`,
);
const DOCUMENT_OVERRIDE_BLOCK_RE = new RegExp(
  `^\\s*override\\s+(section|sequence|bullets|checklist|definitions|properties|table|guard|callout|code|markdown|html|footnotes|image|rule)\\s+(${IDENTIFIER_PATTERN})\\s*(?::\\s*(?:${STRING_PATTERN})?)?(?:\\s+.+)?\\s*$`,
);
const READABLE_KEYED_STRING_RE = new RegExp(
  `^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*${STRING_PATTERN}\\s*$`,
);
const READABLE_ITEM_SCHEMA_RE = /^\s*(item_schema)\s*:\s*$/;
const READABLE_ROW_SCHEMA_RE = /^\s*(row_schema)\s*:\s*$/;
const READABLE_TABLE_CONTAINER_RE = /^\s*(columns|rows)\s*:\s*$/;
const READABLE_TABLE_ROW_RE = new RegExp(`^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*$`);
const LAW_OVERRIDE_SECTION_RE = new RegExp(
  `^\\s*override\\s+(${IDENTIFIER_PATTERN})\\s*:\\s*$`,
);
const LAW_SECTION_RE = new RegExp(`^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*$`);
const LAW_WHEN_RE = /^\s*when\b.*:\s*$/;
const LAW_MATCH_RE = /^\s*match\b.*:\s*$/;
const LAW_ROUTE_FROM_RE = /^\s*route_from\b.*:\s*$/;
const LAW_MATCH_ARM_RE = new RegExp(`^\\s*(else|${DOTTED_NAME_PATTERN})\\s*:\\s*$`);
const TRUST_SURFACE_ITEM_RE = new RegExp(
  `^\\s*(${IDENTIFIER_PATTERN})(?:\\s+when\\b.*)?\\s*$`,
);
const GUARDED_OUTPUT_HEADER_RE = new RegExp(
  `^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*${STRING_PATTERN}\\s+when\\b.*:\\s*$`,
);
const GUARDED_RECORD_ITEM_RE = new RegExp(
  `^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*(?:${STRING_PATTERN}|${DOTTED_NAME_PATTERN}|${PATH_REF_PATTERN})\\s+when\\b.*(?::\\s*)?$`,
);
const BRACED_EXPR_RE = /\{([^{}]+)\}/g;
const BRACED_REF_TOKEN_RE = new RegExp(
  `\\b(${DOTTED_NAME_PATTERN})(?::(${DOTTED_NAME_PATTERN}))?\\b`,
  "g",
);
const DOTTED_TOKEN_RE = new RegExp(`\\b${DOTTED_NAME_PATTERN}\\b`, "g");
const UPPERCASE_DOTTED_TOKEN_RE = new RegExp(`\\b${DOTTED_NAME_PATTERN}\\b`, "g");
const REVIEW_SEMANTIC_REF_RE = /\b(contract|fields)\.([A-Za-z_][A-Za-z0-9_]*)\b/g;
const NON_BINDING_LAW_TOKENS = new Set([
  "accept",
  "active",
  "and",
  "artifact",
  "as",
  "block",
  "carry",
  "comparison",
  "current",
  "decisions",
  "else",
  "exact",
  "except",
  "failed",
  "false",
  "for",
  "forbid",
  "ignore",
  "in",
  "invalidate",
  "mapping",
  "match",
  "missing",
  "mode",
  "must",
  "none",
  "not",
  "only",
  "or",
  "own",
  "passed",
  "passes",
  "present",
  "preserve",
  "reject",
  "rewrite_evidence",
  "route",
  "route_from",
  "stop",
  "structure",
  "support_only",
  "true",
  "truth",
  "unclear",
  "via",
  "vocabulary",
  "when",
]);

const PROSE_LINE_RE = /^\s*(?:(?:required|important|warning|note)\s+)?"(?:\\.|[^"\\])*"\s*$/;
const ROLE_INLINE_RE = new RegExp(`^\\s*role\\s*:\\s*${STRING_PATTERN}\\s*$`);
const PURPOSE_OR_REASON_RE = new RegExp(
  `^\\s*(purpose|reason)\\s*:\\s*${STRING_PATTERN}\\s*$`,
);

const RESERVED_AGENT_FIELD_KEYS = new Set(["role", "inputs", "outputs", "analysis", "decision", "skills", "review", "final_output"]);
const READABLE_DECLARATION_KINDS = Object.freeze([
  "agent",
  "analysis",
  "decision",
  "schema_decl",
  "document",
  "input",
  "input_source",
  "output",
  "output_target",
  "output_shape",
  "output_schema",
  "skill",
  "enum",
]);

const DECLARATION_KIND = Object.freeze({
  AGENT: "agent",
  REVIEW: "review",
  ANALYSIS: "analysis",
  DECISION: "decision",
  SCHEMA_DECL: "schema_decl",
  DOCUMENT: "document",
  WORKFLOW: "workflow",
  SKILLS_BLOCK: "skills",
  INPUTS_BLOCK: "inputs",
  INPUT: "input",
  INPUT_SOURCE: "input_source",
  OUTPUTS_BLOCK: "outputs",
  OUTPUT: "output",
  OUTPUT_TARGET: "output_target",
  OUTPUT_SHAPE: "output_shape",
  OUTPUT_SCHEMA: "output_schema",
  SKILL_PACKAGE: "skill_package",
  SKILL: "skill",
  ENUM: "enum",
  RENDER_PROFILE: "render_profile",
});

const ADDRESSABLE_DECLARATION_KINDS = Object.freeze([
  DECLARATION_KIND.AGENT,
  DECLARATION_KIND.ANALYSIS,
  DECLARATION_KIND.DECISION,
  DECLARATION_KIND.SCHEMA_DECL,
  DECLARATION_KIND.DOCUMENT,
  DECLARATION_KIND.WORKFLOW,
  DECLARATION_KIND.SKILLS_BLOCK,
  DECLARATION_KIND.INPUT,
  DECLARATION_KIND.INPUT_SOURCE,
  DECLARATION_KIND.OUTPUT,
  DECLARATION_KIND.OUTPUT_TARGET,
  DECLARATION_KIND.OUTPUT_SHAPE,
  DECLARATION_KIND.OUTPUT_SCHEMA,
  DECLARATION_KIND.SKILL,
  DECLARATION_KIND.ENUM,
]);

const DECLARATION_DEFINITIONS = Object.freeze([
  {
    kind: DECLARATION_KIND.AGENT,
    regex: new RegExp(
      `^\\s*(abstract\\s+)?agent\\s+(${IDENTIFIER_PATTERN})(?:\\s*\\[(${DOTTED_NAME_PATTERN})\\])?\\s*:`,
    ),
    abstractGroup: 1,
    nameGroup: 2,
    parentGroup: 3,
  },
  {
    kind: DECLARATION_KIND.REVIEW,
    regex: new RegExp(
      `^\\s*review_family\\s+(${IDENTIFIER_PATTERN})(?:\\s*\\[(${DOTTED_NAME_PATTERN})\\])?\\s*:`,
    ),
    nameGroup: 1,
    parentGroup: 2,
  },
  {
    kind: DECLARATION_KIND.REVIEW,
    regex: new RegExp(
      `^\\s*(abstract\\s+)?review\\s+(${IDENTIFIER_PATTERN})(?:\\s*\\[(${DOTTED_NAME_PATTERN})\\])?\\s*:`,
    ),
    abstractGroup: 1,
    nameGroup: 2,
    parentGroup: 3,
  },
  {
    kind: DECLARATION_KIND.WORKFLOW,
    regex: new RegExp(
      `^\\s*route_only\\s+(${IDENTIFIER_PATTERN})\\s*:`,
    ),
    nameGroup: 1,
  },
  {
    kind: DECLARATION_KIND.WORKFLOW,
    regex: new RegExp(
      `^\\s*grounding\\s+(${IDENTIFIER_PATTERN})\\s*:`,
    ),
    nameGroup: 1,
  },
  {
    kind: DECLARATION_KIND.WORKFLOW,
    regex: new RegExp(
      `^\\s*workflow\\s+(${IDENTIFIER_PATTERN})(?:\\s*\\[(${DOTTED_NAME_PATTERN})\\])?\\s*:`,
    ),
    nameGroup: 1,
    parentGroup: 2,
  },
  {
    kind: DECLARATION_KIND.ANALYSIS,
    regex: new RegExp(
      `^\\s*analysis\\s+(${IDENTIFIER_PATTERN})(?:\\s*\\[(${DOTTED_NAME_PATTERN})\\])?\\s*:`,
    ),
    nameGroup: 1,
    parentGroup: 2,
  },
  {
    kind: DECLARATION_KIND.DECISION,
    regex: new RegExp(`^\\s*decision\\s+(${IDENTIFIER_PATTERN})\\s*:`),
    nameGroup: 1,
  },
  {
    kind: DECLARATION_KIND.SCHEMA_DECL,
    regex: new RegExp(
      `^\\s*schema\\s+(${IDENTIFIER_PATTERN})(?:\\s*\\[(${DOTTED_NAME_PATTERN})\\])?\\s*:`,
    ),
    nameGroup: 1,
    parentGroup: 2,
  },
  {
    kind: DECLARATION_KIND.DOCUMENT,
    regex: new RegExp(
      `^\\s*document\\s+(${IDENTIFIER_PATTERN})(?:\\s*\\[(${DOTTED_NAME_PATTERN})\\])?\\s*:`,
    ),
    nameGroup: 1,
    parentGroup: 2,
  },
  {
    kind: DECLARATION_KIND.SKILLS_BLOCK,
    regex: new RegExp(
      `^\\s*skills\\s+(${IDENTIFIER_PATTERN})(?:\\s*\\[(${DOTTED_NAME_PATTERN})\\])?\\s*:`,
    ),
    nameGroup: 1,
    parentGroup: 2,
  },
  {
    kind: DECLARATION_KIND.INPUTS_BLOCK,
    regex: new RegExp(
      `^\\s*inputs\\s+(${IDENTIFIER_PATTERN})(?:\\s*\\[(${DOTTED_NAME_PATTERN})\\])?\\s*:`,
    ),
    nameGroup: 1,
    parentGroup: 2,
  },
  {
    kind: DECLARATION_KIND.INPUT_SOURCE,
    regex: new RegExp(
      `^\\s*input\\s+source\\s+(${IDENTIFIER_PATTERN})\\s*:`,
    ),
    nameGroup: 1,
  },
  {
    kind: DECLARATION_KIND.INPUT,
    regex: new RegExp(`^\\s*input\\s+(${IDENTIFIER_PATTERN})\\s*:`),
    nameGroup: 1,
  },
  {
    kind: DECLARATION_KIND.OUTPUTS_BLOCK,
    regex: new RegExp(
      `^\\s*outputs\\s+(${IDENTIFIER_PATTERN})(?:\\s*\\[(${DOTTED_NAME_PATTERN})\\])?\\s*:`,
    ),
    nameGroup: 1,
    parentGroup: 2,
  },
  {
    kind: DECLARATION_KIND.OUTPUT_TARGET,
    regex: new RegExp(
      `^\\s*output\\s+target\\s+(${IDENTIFIER_PATTERN})\\s*:`,
    ),
    nameGroup: 1,
  },
  {
    kind: DECLARATION_KIND.OUTPUT_SHAPE,
    regex: new RegExp(
      `^\\s*output\\s+shape\\s+(${IDENTIFIER_PATTERN})(?:\\s*\\[(${DOTTED_NAME_PATTERN})\\])?\\s*:`,
    ),
    nameGroup: 1,
    parentGroup: 2,
  },
  {
    kind: DECLARATION_KIND.RENDER_PROFILE,
    regex: new RegExp(
      `^\\s*render_profile\\s+(${IDENTIFIER_PATTERN})(?:\\s*:)?\\s*$`,
    ),
    nameGroup: 1,
  },
  {
    kind: DECLARATION_KIND.OUTPUT,
    regex: new RegExp(
      `^\\s*output\\s+(${IDENTIFIER_PATTERN})(?:\\s*\\[(${DOTTED_NAME_PATTERN})\\])?\\s*:`,
    ),
    nameGroup: 1,
    parentGroup: 2,
  },
  {
    kind: DECLARATION_KIND.OUTPUT_SCHEMA,
    regex: new RegExp(
      `^\\s*output\\s+schema\\s+(${IDENTIFIER_PATTERN})(?:\\s*\\[(${DOTTED_NAME_PATTERN})\\])?\\s*:`,
    ),
    nameGroup: 1,
    parentGroup: 2,
  },
  {
    kind: DECLARATION_KIND.SKILL_PACKAGE,
    regex: new RegExp(`^\\s*skill\\s+package\\s+(${IDENTIFIER_PATTERN})\\s*:`),
    nameGroup: 1,
  },
  {
    kind: DECLARATION_KIND.SKILL,
    regex: new RegExp(`^\\s*skill\\s+(${IDENTIFIER_PATTERN})\\s*:`),
    nameGroup: 1,
  },
  {
    kind: DECLARATION_KIND.ENUM,
    regex: new RegExp(`^\\s*enum\\s+(${IDENTIFIER_PATTERN})\\s*:`),
    nameGroup: 1,
  },
]);

const INDEX_CACHE = new Map();
const REVIEW_CONTEXT_CACHE = new Map();
const AGENT_BINDING_CACHE = new Map();
const PROJECT_CONFIG_CACHE = new Map();

// Compiler semantics stay the policy owner. This file only adapts those
// shipped import, declaration, readable-ref, and inheritance rules to VS Code.
async function provideImportLinks(document, token) {
  const context = getDocumentContext(document);
  if (!context) {
    return [];
  }

  const links = [];
  for (const entry of collectImportEntries(document, context)) {
    if (token.isCancellationRequested) {
      return [];
    }

    if (!(await uriExists(entry.targetUri))) {
      continue;
    }

    links.push(new vscode.DocumentLink(entry.range, entry.targetUri));
  }

  return links;
}

async function provideDefinitionLinks(document, position, token) {
  const source = getIndexedDocumentState(document);
  if (!source.context) {
    return undefined;
  }

  const importTarget = source.importEntries.find((entry) => entry.range.contains(position));
  if (importTarget) {
    if (token.isCancellationRequested || !(await uriExists(importTarget.targetUri))) {
      return undefined;
    }

    const targetDocument = await vscode.workspace.openTextDocument(importTarget.targetUri);
    return [createFileLocationLink(importTarget.range, targetDocument)];
  }

  const site = classifyDefinitionSite(source, position);
  if (!site || token.isCancellationRequested) {
    return undefined;
  }

  if (site.type === "directDeclRef") {
    return resolveDirectDefinition(site, source);
  }
  if (site.type === "readableDeclRef") {
    return resolveReadableDefinition(site, source);
  }
  if (site.type === "addressableRef") {
    return resolveAddressableDefinition(site, source);
  }
  if (site.type === "reviewSemanticRef") {
    return resolveReviewSemanticDefinition(site, source);
  }
  if (site.type === "reviewBoundOutputPathRef") {
    return resolveReviewBoundOutputPathDefinition(site, source);
  }
  if (site.type === "boundLawPathRef") {
    return resolveBoundLawPathDefinition(site, source);
  }
  return resolveStructuralDefinition(site, source);
}

function classifyDefinitionSite(source, position) {
  const { document } = source;
  const lineText = document.lineAt(position.line).text;
  const sites = [];

  const inheritedAgent = lineText.match(INHERITED_AGENT_RE);
  if (inheritedAgent) {
    sites.push({
      type: "directDeclRef",
      declarationKind: DECLARATION_KIND.AGENT,
      range: createFirstMatchRange(lineText, position.line, inheritedAgent[1]),
      ref: parseNameRef(inheritedAgent[1]),
      requireConcrete: false,
    });
  }

  const inheritedBlock = lineText.match(INHERITED_BLOCK_RE);
  if (inheritedBlock) {
    sites.push({
      type: "directDeclRef",
      declarationKind: inheritanceKindToDeclarationKind(inheritedBlock[1]),
      range: createLastMatchRange(lineText, position.line, inheritedBlock[2]),
      ref: parseNameRef(inheritedBlock[2]),
      requireConcrete: false,
    });
  }

  const patchField = lineText.match(PATCH_FIELD_RE);
  if (patchField) {
    sites.push({
      type: "directDeclRef",
      declarationKind:
        patchField[1] === "inputs"
          ? DECLARATION_KIND.INPUTS_BLOCK
          : DECLARATION_KIND.OUTPUTS_BLOCK,
      range: createLastMatchRange(lineText, position.line, patchField[2]),
      ref: parseNameRef(patchField[2]),
      requireConcrete: false,
    });
  }

  const lineContext = getLineContext(source, position.line);

  if (allowsInterpolation(lineText)) {
    sites.push(...collectInterpolationSites(lineText, position.line));
  }

  switch (lineContext.container.type) {
    case "agent_body":
      sites.push(...collectAgentBodySites(lineText, position.line));
      break;
    case "review_body":
      sites.push(...collectReviewBodySites(lineText, position.line));
      break;
    case "review_fields_body":
      sites.push(...collectReviewFieldsBodySites(lineText, position.line));
      break;
    case "review_subject_map_body":
      sites.push(...collectReviewSubjectMapBodySites(lineText, position.line));
      break;
    case "review_pre_outcome_body":
      sites.push(...collectReviewPreOutcomeSites(lineText, position.line));
      break;
    case "review_outcome_body":
      sites.push(...collectReviewOutcomeSites(lineText, position.line));
      break;
    case "review_match_body":
      sites.push(
        ...(
          lineContext.container.owner === "review_outcome"
            ? collectReviewOutcomeSites(lineText, position.line)
            : collectReviewPreOutcomeSites(lineText, position.line)
        ),
      );
      break;
    case "analysis_body":
      sites.push(...collectAnalysisBodySites(lineText, position.line));
      break;
    case "schema_body":
      sites.push(...collectSchemaBodySites(lineText, position.line));
      break;
    case "document_body":
      sites.push(...collectDocumentBodySites(lineText, position.line));
      break;
    case "workflow_body":
      sites.push(...collectWorkflowBodySites(lineText, position.line));
      break;
    case "law_body":
      sites.push(...collectLawBodySites(lineText, position.line, true));
      break;
    case "law_statement_body":
      sites.push(...collectLawBodySites(lineText, position.line, false));
      break;
    case "law_match_body":
      sites.push(...collectLawMatchBodySites(lineText, position.line));
      break;
    case "workflow_section_body":
      sites.push(...collectWorkflowSectionSites(lineText, position.line));
      break;
    case "skills_body":
      sites.push(...collectSkillsBodySites(lineText, position.line, true));
      break;
    case "skills_section_body":
      sites.push(...collectSkillsBodySites(lineText, position.line, false));
      break;
    case "io_body":
      sites.push(
        ...collectIoBodySites(lineText, position.line, lineContext.container.fieldKind),
      );
      break;
    case "record_body":
      sites.push(
        ...collectRecordBodySites(lineText, position.line, lineContext.container),
      );
      break;
    case "trust_surface_body":
      sites.push(...collectTrustSurfaceBodySites(lineText, position.line));
      break;
    default:
      break;
  }

  for (const site of sites) {
    if (
      site.type === "structuralKeyRef"
      || site.type === "reviewSemanticRef"
      || site.type === "reviewBoundOutputPathRef"
      || site.type === "boundLawPathRef"
    ) {
      site.lineContext = lineContext;
    }
  }

  return sites.find((site) => site.range.contains(position));
}

function collectAgentBodySites(lineText, lineNumber) {
  const sites = [];

  const reviewField = lineText.match(
    new RegExp(`^\\s*review\\s*:\\s*(${DOTTED_NAME_PATTERN})\\s*$`),
  );
  if (reviewField) {
    sites.push({
      type: "directDeclRef",
      declarationKind: DECLARATION_KIND.REVIEW,
      range: createLastMatchRange(lineText, lineNumber, reviewField[1]),
      ref: parseNameRef(reviewField[1]),
      requireConcrete: false,
    });
    return sites;
  }

  const abstractField = lineText.match(ABSTRACT_FIELD_RE);
  if (abstractField) {
    const key = abstractField[1];
    if (!RESERVED_AGENT_FIELD_KEYS.has(key)) {
      sites.push(createStructuralSite(lineText, lineNumber, key));
    }
  }

  const inheritItem = lineText.match(INHERIT_RE);
  if (inheritItem) {
    sites.push(createStructuralSite(lineText, lineNumber, inheritItem[1]));
  }

  const overrideRef = lineText.match(OVERRIDE_REF_RE);
  if (overrideRef) {
    const key = overrideRef[1];
    sites.push(createStructuralSite(lineText, lineNumber, key));
    sites.push({
      type: "directDeclRef",
      declarationKind: DECLARATION_KIND.WORKFLOW,
      range: createLastMatchRange(lineText, lineNumber, overrideRef[2]),
      ref: parseNameRef(overrideRef[2]),
      requireConcrete: false,
    });
    return sites;
  }

  const overrideBody = lineText.match(OVERRIDE_BODY_RE);
  if (overrideBody && !RESERVED_AGENT_FIELD_KEYS.has(overrideBody[1])) {
    sites.push(createStructuralSite(lineText, lineNumber, overrideBody[1]));
  }

  const topLevelFieldRef = lineText.match(TOP_LEVEL_FIELD_REF_RE);
  if (topLevelFieldRef) {
    if (topLevelFieldRef[1] === "review") {
      sites.push({
        type: "directDeclRef",
        declarationKind: DECLARATION_KIND.REVIEW,
        range: createLastMatchRange(lineText, lineNumber, topLevelFieldRef[2]),
        ref: parseNameRef(topLevelFieldRef[2]),
        requireConcrete: false,
      });
      return sites;
    }
    sites.push({
      type: "directDeclRef",
      declarationKind: keyedFieldToDeclarationKind(topLevelFieldRef[1]),
      range: createLastMatchRange(lineText, lineNumber, topLevelFieldRef[2]),
      ref: parseNameRef(topLevelFieldRef[2]),
      requireConcrete: false,
    });
    return sites;
  }

  const slotRef = lineText.match(AGENT_SLOT_REF_RE);
  if (slotRef && !RESERVED_AGENT_FIELD_KEYS.has(slotRef[1])) {
    sites.push({
      type: "directDeclRef",
      declarationKind: DECLARATION_KIND.WORKFLOW,
      range: createLastMatchRange(lineText, lineNumber, slotRef[2]),
      ref: parseNameRef(slotRef[2]),
      requireConcrete: false,
    });
  }

  return sites;
}

function collectReviewBodySites(lineText, lineNumber) {
  const sites = [];

  const inheritItem = lineText.match(INHERIT_RE);
  if (inheritItem) {
    sites.push(createStructuralSite(lineText, lineNumber, inheritItem[1]));
    return sites;
  }

  const overrideFields = lineText.match(REVIEW_OVERRIDE_FIELDS_RE);
  if (overrideFields) {
    sites.push(createStructuralSite(lineText, lineNumber, "fields"));
    return sites;
  }

  const overrideOutcome = lineText.match(REVIEW_OVERRIDE_OUTCOME_RE);
  if (overrideOutcome) {
    sites.push(createStructuralSite(lineText, lineNumber, overrideOutcome[1]));
    return sites;
  }

  const overrideSection = lineText.match(REVIEW_OVERRIDE_SECTION_RE);
  if (overrideSection) {
    sites.push(createStructuralSite(lineText, lineNumber, overrideSection[1]));
    return sites;
  }

  if (REVIEW_FIELDS_FIELD_RE.test(lineText)) {
    sites.push(createStructuralSite(lineText, lineNumber, "fields"));
    return sites;
  }

  if (REVIEW_OUTCOME_HEADER_RE.test(lineText)) {
    const key = lineText.trim().split(":")[0].trim();
    sites.push(createStructuralSite(lineText, lineNumber, key));
    return sites;
  }

  const configRef = lineText.match(REVIEW_CONFIG_REF_RE);
  if (configRef) {
    if (configRef[1] === "comment_output") {
      sites.push({
        type: "directDeclRef",
        declarationKind: DECLARATION_KIND.OUTPUT,
        range: createLastMatchRange(lineText, lineNumber, configRef[2]),
        ref: parseNameRef(configRef[2]),
        requireConcrete: false,
      });
      return sites;
    }
    sites.push({
      type: "readableDeclRef",
      range: createLastMatchRange(lineText, lineNumber, configRef[2]),
      ref: parseNameRef(configRef[2]),
    });
    return sites;
  }

  if (REVIEW_SUBJECT_MAP_FIELD_RE.test(lineText)) {
    sites.push(createStructuralSite(lineText, lineNumber, "subject_map"));
    return sites;
  }

  const localSection = lineText.match(REVIEW_SECTION_RE);
  if (localSection) {
    sites.push(createStructuralSite(lineText, lineNumber, localSection[1]));
    return sites;
  }

  sites.push(...collectShippedLawRefSites(lineText, lineNumber));
  return sites;
}

function collectReviewFieldsBodySites(lineText, lineNumber) {
  const binding = lineText.match(REVIEW_FIELD_BINDING_RE);
  if (!binding) {
    return [];
  }

  return createReviewBoundOutputPathSites({
    lineNumber,
    pathText: binding[2],
    startCharacter: lineText.lastIndexOf(binding[2]),
  });
}

function collectReviewSubjectMapBodySites(lineText, lineNumber) {
  const sites = [];
  const entry = lineText.match(REVIEW_SUBJECT_MAP_ENTRY_RE);
  if (!entry) {
    return sites;
  }

  const leftText = entry[1];
  const leftDot = leftText.indexOf(".");
  if (leftDot !== -1) {
    sites.push(
      ...createAddressableRefSites({
        lineNumber,
        pathText: leftText.slice(leftDot + 1),
        pathStartCharacter: lineText.indexOf(leftText) + leftDot + 1,
        rootText: leftText.slice(0, leftDot),
        startCharacter: lineText.indexOf(leftText),
      }),
    );
  }

  sites.push({
    type: "readableDeclRef",
    range: createLastMatchRange(lineText, lineNumber, entry[2]),
    ref: parseNameRef(entry[2]),
  });

  return sites;
}

function collectReviewPreOutcomeSites(lineText, lineNumber) {
  const sites = [];
  sites.push(...collectReviewSemanticSites(lineText, lineNumber));
  sites.push(...collectShippedLawRefSites(lineText, lineNumber));
  sites.push(...collectBoundLawPathSites(lineText, lineNumber));
  return sites;
}

function collectReviewOutcomeSites(lineText, lineNumber) {
  const sites = [];
  const routeTarget = lineText.match(ROUTE_RE);
  if (routeTarget) {
    sites.push({
      type: "directDeclRef",
      declarationKind: DECLARATION_KIND.AGENT,
      range: createLastMatchRange(lineText, lineNumber, routeTarget[4]),
      ref: parseNameRef(routeTarget[4]),
      requireConcrete: true,
    });
  }
  sites.push(...collectReviewSemanticSites(lineText, lineNumber));
  sites.push(...collectShippedLawRefSites(lineText, lineNumber));
  sites.push(...collectBoundLawPathSites(lineText, lineNumber));
  return sites;
}

function collectAnalysisBodySites(lineText, lineNumber) {
  const sites = [];

  const inheritItem = lineText.match(INHERIT_RE);
  if (inheritItem) {
    sites.push(createStructuralSite(lineText, lineNumber, inheritItem[1]));
    return sites;
  }

  const overrideSection = lineText.match(ANALYSIS_OVERRIDE_SECTION_RE);
  if (overrideSection) {
    sites.push(createStructuralSite(lineText, lineNumber, overrideSection[1]));
    return sites;
  }

  const localSection = lineText.match(ANALYSIS_SECTION_RE);
  if (localSection) {
    sites.push(createStructuralSite(lineText, lineNumber, localSection[1]));
    return sites;
  }

  const classifyTarget = lineText.match(ANALYSIS_CLASSIFY_RE);
  if (classifyTarget) {
    sites.push({
      type: "directDeclRef",
      declarationKind: DECLARATION_KIND.ENUM,
      range: createLastMatchRange(lineText, lineNumber, classifyTarget[1]),
      ref: parseNameRef(classifyTarget[1]),
      requireConcrete: false,
    });
  }

  const keyedRef = lineText.match(KEYED_DECL_REF_RE);
  if (keyedRef && keyedRef[1] === "render_profile") {
    sites.push({
      type: "directDeclRef",
      declarationKind: DECLARATION_KIND.RENDER_PROFILE,
      range: createLastMatchRange(lineText, lineNumber, keyedRef[2]),
      ref: parseNameRef(keyedRef[2]),
      requireConcrete: false,
    });
  }

  sites.push(...collectBraceReferenceSites(lineText, lineNumber));
  return sites;
}

function collectSchemaBodySites(lineText, lineNumber) {
  const sites = [];

  const inheritBlock = lineText.match(SCHEMA_INHERIT_BLOCK_RE);
  if (inheritBlock) {
    sites.push(createStructuralSite(lineText, lineNumber, inheritBlock[1]));
    return sites;
  }

  const overrideBlock = lineText.match(SCHEMA_OVERRIDE_BLOCK_RE);
  if (overrideBlock) {
    sites.push(createStructuralSite(lineText, lineNumber, overrideBlock[1]));
    return sites;
  }

  const blockField = lineText.match(SCHEMA_BLOCK_FIELD_RE);
  if (blockField) {
    sites.push(createStructuralSite(lineText, lineNumber, blockField[1]));
    return sites;
  }

  const schemaItem = lineText.match(SCHEMA_ITEM_RE);
  if (schemaItem) {
    sites.push(createStructuralSite(lineText, lineNumber, schemaItem[1]));
    return sites;
  }

  const artifactRef = lineText.match(SCHEMA_ARTIFACT_REF_RE);
  if (artifactRef) {
    sites.push({
      type: "readableDeclRef",
      range: createLastMatchRange(lineText, lineNumber, artifactRef[1]),
      ref: parseNameRef(artifactRef[1]),
    });
    return sites;
  }

  const groupMember = lineText.match(SCHEMA_GROUP_MEMBER_RE);
  if (groupMember) {
    sites.push(createStructuralSite(lineText, lineNumber, groupMember[1]));
  }

  const keyedRef = lineText.match(KEYED_DECL_REF_RE);
  if (keyedRef && keyedRef[1] === "render_profile") {
    sites.push({
      type: "directDeclRef",
      declarationKind: DECLARATION_KIND.RENDER_PROFILE,
      range: createLastMatchRange(lineText, lineNumber, keyedRef[2]),
      ref: parseNameRef(keyedRef[2]),
      requireConcrete: false,
    });
  }

  return sites;
}

function collectDocumentBodySites(lineText, lineNumber) {
  const sites = [];

  const inheritItem = lineText.match(INHERIT_RE);
  if (inheritItem) {
    sites.push(createStructuralSite(lineText, lineNumber, inheritItem[1]));
    return sites;
  }

  const overrideBlock = lineText.match(DOCUMENT_OVERRIDE_BLOCK_RE);
  if (overrideBlock) {
    sites.push(createStructuralSite(lineText, lineNumber, overrideBlock[2]));
    return sites;
  }

  const localBlock = lineText.match(DOCUMENT_BLOCK_RE);
  if (localBlock) {
    sites.push(createStructuralSite(lineText, lineNumber, localBlock[2]));
  }

  const keyedRef = lineText.match(KEYED_DECL_REF_RE);
  if (keyedRef && keyedRef[1] === "render_profile") {
    sites.push({
      type: "directDeclRef",
      declarationKind: DECLARATION_KIND.RENDER_PROFILE,
      range: createLastMatchRange(lineText, lineNumber, keyedRef[2]),
      ref: parseNameRef(keyedRef[2]),
      requireConcrete: false,
    });
  }

  return sites;
}

function collectWorkflowBodySites(lineText, lineNumber) {
  const sites = [];

  const inheritItem = lineText.match(INHERIT_RE);
  if (inheritItem) {
    sites.push(createStructuralSite(lineText, lineNumber, inheritItem[1]));
  }

  const workflowUse = lineText.match(USE_RE);
  if (workflowUse) {
    sites.push({
      type: "directDeclRef",
      declarationKind: DECLARATION_KIND.WORKFLOW,
      range: createLastMatchRange(lineText, lineNumber, workflowUse[2]),
      ref: parseNameRef(workflowUse[2]),
      requireConcrete: false,
    });
    return sites;
  }

  const skillsRef = lineText.match(WORKFLOW_SKILLS_REF_RE);
  if (skillsRef) {
    sites.push({
      type: "directDeclRef",
      declarationKind: DECLARATION_KIND.SKILLS_BLOCK,
      range: createLastMatchRange(lineText, lineNumber, skillsRef[1]),
      ref: parseNameRef(skillsRef[1]),
      requireConcrete: false,
    });
    return sites;
  }

  const overrideRef = lineText.match(OVERRIDE_REF_RE);
  if (overrideRef) {
    const key = overrideRef[1];
    sites.push(createStructuralSite(lineText, lineNumber, key));
    sites.push({
      type: "directDeclRef",
      declarationKind:
        key === "skills"
          ? DECLARATION_KIND.SKILLS_BLOCK
          : DECLARATION_KIND.WORKFLOW,
      range: createLastMatchRange(lineText, lineNumber, overrideRef[2]),
      ref: parseNameRef(overrideRef[2]),
      requireConcrete: false,
    });
  }

  const overrideBody = lineText.match(OVERRIDE_BODY_RE);
  if (overrideBody && !OVERRIDE_REF_RE.test(lineText)) {
    sites.push(createStructuralSite(lineText, lineNumber, overrideBody[1]));
  }

  return sites;
}

function collectLawBodySites(lineText, lineNumber, allowStructural) {
  const sites = [];

  if (allowStructural) {
    const inheritItem = lineText.match(INHERIT_RE);
    if (inheritItem) {
      sites.push(createStructuralSite(lineText, lineNumber, inheritItem[1]));
    }

    const overrideSection = lineText.match(LAW_OVERRIDE_SECTION_RE);
    if (overrideSection) {
      sites.push(createStructuralSite(lineText, lineNumber, overrideSection[1]));
    }
  }

  const routeTarget = lineText.match(ROUTE_RE);
  if (routeTarget) {
    sites.push({
      type: "directDeclRef",
      declarationKind: DECLARATION_KIND.AGENT,
      range: createLastMatchRange(lineText, lineNumber, routeTarget[4]),
      ref: parseNameRef(routeTarget[4]),
      requireConcrete: true,
    });
    return sites;
  }

  sites.push(...collectShippedLawRefSites(lineText, lineNumber));
  sites.push(...collectBoundLawPathSites(lineText, lineNumber));
  return sites;
}

function collectLawMatchBodySites(lineText, lineNumber) {
  return [
    ...collectShippedLawRefSites(lineText, lineNumber),
    ...collectBoundLawPathSites(lineText, lineNumber),
  ];
}

function collectWorkflowSectionSites(lineText, lineNumber) {
  const sites = [];
  const routeTarget = lineText.match(ROUTE_RE);
  if (routeTarget) {
    sites.push({
      type: "directDeclRef",
      declarationKind: DECLARATION_KIND.AGENT,
      range: createLastMatchRange(lineText, lineNumber, routeTarget[4]),
      ref: parseNameRef(routeTarget[4]),
      requireConcrete: true,
    });
  }

  const addressable = lineText.match(STANDALONE_PATH_REF_RE);
  if (addressable) {
    sites.push(
      ...createAddressableRefSites({
        lineNumber,
        pathText: addressable[2],
        pathStartCharacter: lineText.indexOf(addressable[2], lineText.indexOf(addressable[1]) + addressable[1].length),
        rootText: addressable[1],
        startCharacter: lineText.indexOf(addressable[1]),
      }),
    );
    return sites;
  }

  const standalone = lineText.match(STANDALONE_REF_RE);
  if (standalone) {
    sites.push({
      type: "readableDeclRef",
      range: createFirstMatchRange(lineText, lineNumber, standalone[1]),
      ref: parseNameRef(standalone[1]),
    });
  }

  return sites;
}

function collectTrustSurfaceBodySites(lineText, lineNumber) {
  const sites = [];
  const trustSurfaceItem = lineText.match(TRUST_SURFACE_ITEM_RE);
  if (trustSurfaceItem) {
    sites.push(createStructuralSite(lineText, lineNumber, trustSurfaceItem[1]));
  }
  sites.push(...collectShippedLawRefSites(lineText, lineNumber));
  sites.push(...collectBoundLawPathSites(lineText, lineNumber));
  return sites;
}

function collectSkillsBodySites(lineText, lineNumber, allowStructural) {
  const sites = [];

  if (allowStructural) {
    const inheritItem = lineText.match(INHERIT_RE);
    if (inheritItem) {
      sites.push(createStructuralSite(lineText, lineNumber, inheritItem[1]));
    }
  }

  const skillEntry = lineText.match(SKILL_ENTRY_RE);
  if (skillEntry) {
    sites.push({
      type: "directDeclRef",
      declarationKind: DECLARATION_KIND.SKILL,
      range: createLastMatchRange(lineText, lineNumber, skillEntry[2]),
      ref: parseNameRef(skillEntry[2]),
      requireConcrete: false,
    });
    return sites;
  }

  if (allowStructural) {
    const overrideRef = lineText.match(OVERRIDE_REF_RE);
    if (overrideRef) {
      sites.push(createStructuralSite(lineText, lineNumber, overrideRef[1]));
      sites.push({
        type: "directDeclRef",
        declarationKind: DECLARATION_KIND.SKILL,
        range: createLastMatchRange(lineText, lineNumber, overrideRef[2]),
        ref: parseNameRef(overrideRef[2]),
        requireConcrete: false,
      });
    }

    const overrideBody = lineText.match(OVERRIDE_BODY_RE);
    if (overrideBody && !OVERRIDE_REF_RE.test(lineText)) {
      sites.push(createStructuralSite(lineText, lineNumber, overrideBody[1]));
    }
  }

  return sites;
}

function collectIoBodySites(lineText, lineNumber, fieldKind) {
  const sites = [];

  const inheritItem = lineText.match(INHERIT_RE);
  if (inheritItem) {
    sites.push(createStructuralSite(lineText, lineNumber, inheritItem[1]));
  }

  const overrideBody = lineText.match(OVERRIDE_BODY_RE);
  if (overrideBody) {
    sites.push(createStructuralSite(lineText, lineNumber, overrideBody[1]));
  }

  const standalone = lineText.match(STANDALONE_REF_RE);
  if (standalone) {
    sites.push({
      type: "directDeclRef",
      declarationKind:
        fieldKind === "inputs"
          ? DECLARATION_KIND.INPUT
          : DECLARATION_KIND.OUTPUT,
      range: createFirstMatchRange(lineText, lineNumber, standalone[1]),
      ref: parseNameRef(standalone[1]),
      requireConcrete: false,
    });
  }

  return sites;
}

function collectRecordBodySites(lineText, lineNumber, container) {
  const sites = [];
  const fieldKind = container?.fieldKind;
  const declarationKind = container?.declarationKind;
  const isGuardedOutputItem = GUARDED_RECORD_ITEM_RE.test(lineText);

  const keyedPathRef = lineText.match(KEY_VALUE_PATH_REF_RE);
  if (keyedPathRef) {
    sites.push(
      ...createAddressableRefSites({
        lineNumber,
        pathText: keyedPathRef[3],
        pathStartCharacter: lineText.indexOf(
          keyedPathRef[3],
          lineText.lastIndexOf(keyedPathRef[2]) + keyedPathRef[2].length,
        ),
        rootText: keyedPathRef[2],
        startCharacter: lineText.lastIndexOf(keyedPathRef[2]),
      }),
    );
    return sites;
  }

  const inheritItem = lineText.match(INHERIT_RE);
  if (inheritItem) {
    sites.push(createStructuralSite(lineText, lineNumber, inheritItem[1]));
    return sites;
  }

  const overrideRef = lineText.match(OVERRIDE_REF_RE);
  if (overrideRef) {
    const key = overrideRef[1];
    const targetKind = keyedRecordFieldToDeclarationKind(key, {
      declarationKind,
      fieldKind,
    });
    sites.push(createStructuralSite(lineText, lineNumber, key));
    if (targetKind) {
      sites.push({
        type: "directDeclRef",
        declarationKind: targetKind,
        range: createLastMatchRange(lineText, lineNumber, overrideRef[2]),
        ref: parseNameRef(overrideRef[2]),
        requireConcrete: false,
      });
    }
    return sites;
  }

  const overrideBody = lineText.match(OVERRIDE_BODY_RE);
  if (overrideBody) {
    sites.push(createStructuralSite(lineText, lineNumber, overrideBody[1]));
    return sites;
  }

  const keyedRef = lineText.match(KEYED_DECL_REF_RE);
  if (keyedRef) {
    const targetKind = keyedRecordFieldToDeclarationKind(keyedRef[1], {
      declarationKind,
      fieldKind,
    });
    if (targetKind) {
      sites.push({
        type: "directDeclRef",
        declarationKind: targetKind,
        range: createLastMatchRange(lineText, lineNumber, keyedRef[2]),
        ref: parseNameRef(keyedRef[2]),
        requireConcrete: false,
      });
    }
  }

  if (fieldKind === "inputs" || fieldKind === "outputs") {
    const standalone = lineText.match(STANDALONE_REF_RE);
    if (standalone) {
      sites.push({
        type: "directDeclRef",
        declarationKind:
          fieldKind === "inputs"
            ? DECLARATION_KIND.INPUT
            : DECLARATION_KIND.OUTPUT,
        range: createFirstMatchRange(lineText, lineNumber, standalone[1]),
        ref: parseNameRef(standalone[1]),
        requireConcrete: false,
      });
    }
  }

  if (isGuardedOutputItem) {
    sites.push(...collectReviewSemanticSites(lineText, lineNumber));
    sites.push(...collectShippedLawRefSites(lineText, lineNumber));
  }

  return sites;
}

function collectInterpolationSites(lineText, lineNumber) {
  const sites = [];

  for (const match of lineText.matchAll(INTERPOLATION_RE)) {
    const expression = match[1];
    const expressionMatch = expression.match(INTERPOLATION_EXPR_RE);
    if (!expressionMatch) {
      continue;
    }

    const rootText = expressionMatch[1];
    const pathText = expressionMatch[2];
    const expressionOffset = expression.indexOf(rootText);
    const rootStart = (match.index ?? 0) + 2 + expressionOffset;
    const semanticMatch = rootText.match(/^(contract|fields)\.([A-Za-z_][A-Za-z0-9_]*)$/);
    if (semanticMatch) {
      sites.push({
        type: "reviewSemanticRef",
        lineContext: undefined,
        memberName: semanticMatch[2],
        range: new vscode.Range(
          lineNumber,
          rootStart,
          lineNumber,
          rootStart + semanticMatch[1].length,
        ),
        segmentIndex: -1,
        semanticRoot: semanticMatch[1],
      });
      sites.push({
        type: "reviewSemanticRef",
        lineContext: undefined,
        memberName: semanticMatch[2],
        range: new vscode.Range(
          lineNumber,
          rootStart + semanticMatch[1].length + 1,
          lineNumber,
          rootStart + rootText.length,
        ),
        segmentIndex: 0,
        semanticRoot: semanticMatch[1],
      });
      continue;
    }
    if (pathText) {
      const pathOffset = expression.indexOf(pathText, expressionOffset + rootText.length);
      sites.push(
        ...createAddressableRefSites({
          lineNumber,
          pathText,
          pathStartCharacter: (match.index ?? 0) + 2 + pathOffset,
          rootText,
          startCharacter: rootStart,
        }),
      );
      continue;
    }

    const ref = parseNameRef(rootText);
    if (!ref) {
      continue;
    }

    sites.push({
      type: "readableDeclRef",
      range: new vscode.Range(
        lineNumber,
        rootStart,
        lineNumber,
        rootStart + rootText.length,
      ),
      ref,
    });
  }

  return sites;
}

function collectBraceReferenceSites(lineText, lineNumber) {
  const sites = [];

  for (const braceMatch of lineText.matchAll(BRACED_EXPR_RE)) {
    const expression = braceMatch[1];
    for (const token of expression.matchAll(BRACED_REF_TOKEN_RE)) {
      const rootText = token[1];
      const pathText = token[2];
      const tokenOffset = token.index ?? 0;
      const rootStart = (braceMatch.index ?? 0) + 1 + tokenOffset;

      if (pathText) {
        const pathOffset = token[0].indexOf(pathText);
        sites.push(
          ...createAddressableRefSites({
            lineNumber,
            pathText,
            pathStartCharacter: rootStart + pathOffset,
            rootText,
            startCharacter: rootStart,
          }),
        );
        continue;
      }

      const ref = parseNameRef(rootText);
      if (!ref) {
        continue;
      }

      sites.push({
        type: "readableDeclRef",
        range: new vscode.Range(
          lineNumber,
          rootStart,
          lineNumber,
          rootStart + rootText.length,
        ),
        ref,
      });
    }
  }

  return sites;
}

async function resolveDirectDefinition(site, source) {
  const target = await resolveReferenceTarget(
    site.ref,
    source,
    site.declarationKind,
    site.requireConcrete,
  );
  if (!target) {
    return undefined;
  }

  return [
    createDeclarationLocationLink(
      site.range,
      target.document,
      target.declaration.nameRange,
    ),
  ];
}

async function resolveReadableDefinition(site, source) {
  const targetSource = await openReferencedDocument(site.ref, source);
  if (!targetSource) {
    return undefined;
  }

  const readable = findReadableDeclaration(
    targetSource.index,
    site.ref.declarationName,
  );
  if (!readable || (readable.kind === DECLARATION_KIND.AGENT && readable.abstract)) {
    return undefined;
  }

  return [
    createDeclarationLocationLink(
      site.range,
      targetSource.document,
      readable.nameRange,
    ),
  ];
}

async function resolveAddressableDefinition(site, source) {
  const targetSource = await openReferencedDocument(site.ref, source);
  if (!targetSource) {
    return undefined;
  }

  const declaration = findAddressableDeclaration(
    targetSource.index,
    site.ref.declarationName,
  );
  if (!declaration || (declaration.kind === DECLARATION_KIND.AGENT && declaration.abstract)) {
    return undefined;
  }

  if (site.segmentIndex === -1) {
    return [
      createDeclarationLocationLink(
        site.range,
        targetSource.document,
        declaration.nameRange,
      ),
    ];
  }

  const target = await findAddressablePathTarget({
    declaration,
    pathSegments: site.pathSegments.slice(0, site.segmentIndex + 1),
    source: targetSource,
  });
  if (!target) {
    return undefined;
  }

  return [
    {
      originSelectionRange: site.range,
      targetUri: target.document.uri,
      targetRange: new vscode.Range(
        target.lineNumber,
        0,
        target.lineNumber,
        target.document.lineAt(target.lineNumber).text.length,
      ),
      targetSelectionRange: target.selectionRange,
    },
  ];
}

async function resolveStructuralDefinition(site, source) {
  const parentBody = await resolveImmediateParentBody(site, source);
  if (!parentBody) {
    return undefined;
  }

  const target = findStructuralKeyTarget(parentBody, site.key);
  if (!target) {
    return undefined;
  }

  return [
    {
      originSelectionRange: site.range,
      targetUri: parentBody.document.uri,
      targetRange: new vscode.Range(
        target.lineNumber,
        0,
        target.lineNumber,
        parentBody.document.lineAt(target.lineNumber).text.length,
      ),
      targetSelectionRange: target.keyRange,
    },
  ];
}

async function resolveReviewSemanticDefinition(site, source) {
  const context = await resolveReviewSemanticContext(site.lineContext, source);
  if (!context) {
    return undefined;
  }

  if (site.semanticRoot === "contract") {
    if (!context.contractTarget) {
      return undefined;
    }
    if (site.segmentIndex === -1) {
      return [
        createDeclarationLocationLink(
          site.range,
          context.contractTarget.source.document,
          context.contractTarget.declaration.nameRange,
        ),
      ];
    }
    if (!context.contractGateKeys.has(site.memberName)) {
      return undefined;
    }
    const target = await findAddressablePathTarget({
      declaration: context.contractTarget.declaration,
      pathSegments: [site.memberName],
      source: context.contractTarget.source,
    });
    if (!target) {
      return undefined;
    }
    return [
      {
        originSelectionRange: site.range,
        targetUri: target.document.uri,
        targetRange: new vscode.Range(
          target.lineNumber,
          0,
          target.lineNumber,
          target.document.lineAt(target.lineNumber).text.length,
        ),
        targetSelectionRange: target.selectionRange,
      },
    ];
  }

  if (site.semanticRoot === "fields") {
    if (site.segmentIndex === -1) {
      if (context.fieldsLineNumber === undefined || !context.fieldsSource) {
        return undefined;
      }
      const targetDocument = context.fieldsSource.document;
      const targetLine = targetDocument.lineAt(context.fieldsLineNumber).text;
      return [
        {
          originSelectionRange: site.range,
          targetUri: targetDocument.uri,
          targetRange: new vscode.Range(
            context.fieldsLineNumber,
            0,
            context.fieldsLineNumber,
            targetLine.text.length,
          ),
          targetSelectionRange: createFirstMatchRange(
            targetLine,
            context.fieldsLineNumber,
            "fields",
          ),
        },
      ];
    }

    const pathSegments = context.fieldBindings.get(site.memberName);
    if (!pathSegments || !context.outputTarget) {
      return undefined;
    }
    const target = await findAddressablePathTarget({
      declaration: context.outputTarget.declaration,
      pathSegments,
      source: context.outputTarget.source,
    });
    if (!target) {
      return undefined;
    }
    return [
      {
        originSelectionRange: site.range,
        targetUri: target.document.uri,
        targetRange: new vscode.Range(
          target.lineNumber,
          0,
          target.lineNumber,
          target.document.lineAt(target.lineNumber).text.length,
        ),
        targetSelectionRange: target.selectionRange,
      },
    ];
  }

  return undefined;
}

async function resolveReviewBoundOutputPathDefinition(site, source) {
  const context = await resolveReviewSemanticContext(site.lineContext, source);
  if (!context || !context.outputTarget) {
    return undefined;
  }

  const target = await findAddressablePathTarget({
    declaration: context.outputTarget.declaration,
    pathSegments: site.pathSegments.slice(0, site.segmentIndex + 1),
    source: context.outputTarget.source,
  });
  if (!target) {
    return undefined;
  }

  return [
    {
      originSelectionRange: site.range,
      targetUri: target.document.uri,
      targetRange: new vscode.Range(
        target.lineNumber,
        0,
        target.lineNumber,
        target.document.lineAt(target.lineNumber).text.length,
      ),
      targetSelectionRange: target.selectionRange,
    },
  ];
}

function createResolvedTargetLink(originRange, target) {
  return {
    originSelectionRange: originRange,
    targetUri: target.document.uri,
    targetRange: new vscode.Range(
      target.lineNumber,
      0,
      target.lineNumber,
      target.document.lineAt(target.lineNumber).text.length,
    ),
    targetSelectionRange: target.selectionRange,
  };
}

function sameDeclarationIdentity(leftSource, leftDeclaration, rightSource, rightDeclaration) {
  return (
    leftSource.document.uri.toString() === rightSource.document.uri.toString()
    && leftDeclaration.kind === rightDeclaration.kind
    && leftDeclaration.name === rightDeclaration.name
  );
}

function bindingPathKey(pathSegments) {
  return pathSegments.join(".");
}

function pathStartsWith(pathSegments, prefixSegments) {
  if (prefixSegments.length > pathSegments.length) {
    return false;
  }
  for (let index = 0; index < prefixSegments.length; index += 1) {
    if (pathSegments[index] !== prefixSegments[index]) {
      return false;
    }
  }
  return true;
}

function removeBindingSubtree(bindings, prefixSegments) {
  for (const key of [...bindings.keys()]) {
    const binding = bindings.get(key);
    if (binding && pathStartsWith(binding.bindingPath, prefixSegments)) {
      bindings.delete(key);
    }
  }
}

function copyBindingSubtree(sourceBindings, prefixSegments, targetBindings) {
  for (const [key, binding] of sourceBindings.entries()) {
    if (pathStartsWith(binding.bindingPath, prefixSegments)) {
      targetBindings.set(key, binding);
    }
  }
}

async function resolveBoundLawPathDefinition(site, source) {
  const context = await resolveBoundLawSiteContext(site.lineContext, source);
  if (!context) {
    return undefined;
  }

  const match = findLongestBoundBindingMatch(context.bindings, site.pathSegments);
  if (!match) {
    return undefined;
  }

  if (site.segmentIndex < match.binding.bindingPath.length) {
    const target = match.binding.prefixTargets[site.segmentIndex];
    return target ? [createResolvedTargetLink(site.range, target)] : undefined;
  }

  const target = await findAddressablePathTarget({
    declaration: match.binding.declaration,
    pathSegments: site.pathSegments.slice(
      match.binding.bindingPath.length,
      site.segmentIndex + 1,
    ),
    source: match.binding.source,
  });
  if (!target) {
    return undefined;
  }

  return [createResolvedTargetLink(site.range, target)];
}

function findLongestBoundBindingMatch(bindings, pathSegments) {
  let bestMatch;
  for (const binding of bindings.values()) {
    if (!pathStartsWith(pathSegments, binding.bindingPath)) {
      continue;
    }
    if (
      !bestMatch
      || binding.bindingPath.length > bestMatch.binding.bindingPath.length
    ) {
      bestMatch = { binding };
    }
  }
  return bestMatch;
}

async function resolveBoundLawSiteContext(lineContext, source) {
  if (!lineContext?.declaration) {
    return undefined;
  }

  const agentTarget = await resolveConcreteAgentOwner(lineContext.declaration, source);
  if (!agentTarget) {
    return undefined;
  }

  const agentSource = getIndexedDocumentState(agentTarget.document);
  const inputBindings = await getResolvedAgentBindings(
    agentSource,
    agentTarget.declaration,
    "inputs",
  );
  const outputBindings = await getResolvedAgentBindings(
    agentSource,
    agentTarget.declaration,
    "outputs",
  );
  const bindings = new Map();
  const ambiguous = new Set();

  for (const bindingMap of [inputBindings, outputBindings]) {
    for (const [key, binding] of bindingMap.entries()) {
      const existing = bindings.get(key);
      if (!existing) {
        bindings.set(key, binding);
        continue;
      }
      if (
        !sameDeclarationIdentity(
          existing.source,
          existing.declaration,
          binding.source,
          binding.declaration,
        )
      ) {
        ambiguous.add(key);
      }
    }
  }

  for (const key of ambiguous) {
    bindings.delete(key);
  }

  return bindings.size ? { bindings } : undefined;
}

async function resolveConcreteAgentOwner(declaration, source) {
  if (declaration.kind === DECLARATION_KIND.AGENT && !declaration.abstract) {
    return { declaration, document: source.document };
  }

  if (declaration.kind === DECLARATION_KIND.WORKFLOW) {
    return findUniqueConcreteAgentUsingWorkflow(source, declaration);
  }

  if (declaration.kind === DECLARATION_KIND.REVIEW) {
    return findUniqueConcreteAgentUsingReview(source, declaration);
  }

  if (declaration.kind === DECLARATION_KIND.OUTPUT) {
    return findUniqueConcreteAgentEmittingOutput(source, declaration);
  }

  return undefined;
}

function getConcreteAgents(source) {
  return [...(source.index.byKind.get(DECLARATION_KIND.AGENT)?.values() || [])].filter(
    (declaration) => !declaration.abstract,
  );
}

async function findUniqueConcreteAgentUsingWorkflow(source, workflowDeclaration) {
  const matches = [];
  for (const agentDeclaration of getConcreteAgents(source)) {
    const target = await resolveDeclaredWorkflowForAgent(source, agentDeclaration);
    if (
      target
      && sameDeclarationIdentity(
        getIndexedDocumentState(target.document),
        target.declaration,
        source,
        workflowDeclaration,
      )
    ) {
      matches.push(targetAgentReference(source, agentDeclaration));
    }
  }

  return matches.length === 1 ? matches[0] : undefined;
}

async function findUniqueConcreteAgentUsingReview(source, reviewDeclaration) {
  const matches = [];
  for (const agentDeclaration of getConcreteAgents(source)) {
    const target = await resolveDeclaredReviewForAgent(source, agentDeclaration);
    if (
      target
      && sameDeclarationIdentity(
        getIndexedDocumentState(target.document),
        target.declaration,
        source,
        reviewDeclaration,
      )
    ) {
      matches.push(targetAgentReference(source, agentDeclaration));
    }
  }

  return matches.length === 1 ? matches[0] : undefined;
}

async function findUniqueConcreteAgentEmittingOutput(source, outputDeclaration) {
  const matches = [];
  for (const agentDeclaration of getConcreteAgents(source)) {
    const bindings = await getResolvedAgentBindings(source, agentDeclaration, "outputs");
    const usesOutput = [...bindings.values()].some((binding) =>
      sameDeclarationIdentity(binding.source, binding.declaration, source, outputDeclaration),
    );
    if (usesOutput) {
      matches.push(targetAgentReference(source, agentDeclaration));
    }
  }

  return matches.length === 1 ? matches[0] : undefined;
}

function targetAgentReference(source, declaration) {
  return { declaration, document: source.document };
}

async function resolveDeclaredWorkflowForAgent(source, declaration, seen = new Set()) {
  const cacheKey = `${source.document.uri.toString()}#${declaration.name}#workflow`;
  if (seen.has(cacheKey)) {
    return undefined;
  }
  seen.add(cacheKey);

  const field = findAgentReservedField(source.document, declaration, "workflow");
  if (field?.type === "ref") {
    return resolveReferenceTarget(field.ref, source, DECLARATION_KIND.WORKFLOW, false);
  }

  if (!field && declaration.parentRef) {
    const parent = await resolveReferenceTarget(
      declaration.parentRef,
      source,
      DECLARATION_KIND.AGENT,
      false,
    );
    if (!parent) {
      return undefined;
    }
    return resolveDeclaredWorkflowForAgent(
      getIndexedDocumentState(parent.document),
      parent.declaration,
      seen,
    );
  }

  return undefined;
}

async function resolveDeclaredReviewForAgent(source, declaration, seen = new Set()) {
  const cacheKey = `${source.document.uri.toString()}#${declaration.name}#review`;
  if (seen.has(cacheKey)) {
    return undefined;
  }
  seen.add(cacheKey);

  const field = findAgentReservedField(source.document, declaration, "review");
  if (field?.type === "ref") {
    return resolveReferenceTarget(field.ref, source, DECLARATION_KIND.REVIEW, false);
  }

  if (!field && declaration.parentRef) {
    const parent = await resolveReferenceTarget(
      declaration.parentRef,
      source,
      DECLARATION_KIND.AGENT,
      false,
    );
    if (!parent) {
      return undefined;
    }
    return resolveDeclaredReviewForAgent(
      getIndexedDocumentState(parent.document),
      parent.declaration,
      seen,
    );
  }

  return undefined;
}

function findAgentReservedField(document, declaration, fieldKey) {
  const bodySpec = getDeclarationBodySpec(declaration);
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return undefined;
  }

  for (
    let lineNumber = declaration.lineNumber + 1;
    lineNumber <= declaration.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    if (fieldKey === "workflow") {
      const refMatch = lineText.match(
        new RegExp(`^\\s*workflow\\s*:\\s*(${DOTTED_NAME_PATTERN})\\s*$`),
      );
      if (refMatch) {
        return { ref: parseNameRef(refMatch[1]), type: "ref" };
      }
      if (new RegExp(`^\\s*workflow\\s*:\\s*${STRING_PATTERN}\\s*$`).test(lineText)) {
        return { type: "inline" };
      }
      continue;
    }

    if (fieldKey === "review") {
      const refMatch = lineText.match(
        new RegExp(`^\\s*review\\s*:\\s*(${DOTTED_NAME_PATTERN})\\s*$`),
      );
      if (refMatch) {
        return { ref: parseNameRef(refMatch[1]), type: "ref" };
      }
      continue;
    }

    const directRef = lineText.match(
      new RegExp(`^\\s*(${fieldKey})\\s*:\\s*(${DOTTED_NAME_PATTERN})\\s*$`),
    );
    if (directRef) {
      return { ref: parseNameRef(directRef[2]), type: "ref" };
    }

    if (
      new RegExp(`^\\s*${fieldKey}\\s*:\\s*${STRING_PATTERN}\\s*$`).test(lineText)
    ) {
      return {
        bodySpec: {
          type: "record_body",
          fieldKind: fieldKey,
          indent: leadingSpaces(lineText),
          lineNumber,
          endLine: findBodyEndLine(document, lineNumber, declaration.endLine),
        },
        type: "inline",
      };
    }

    const patchMatch = lineText.match(PATCH_FIELD_RE);
    if (patchMatch && patchMatch[1] === fieldKey) {
      return {
        bodySpec: {
          type: "io_body",
          fieldKind: fieldKey,
          indent: leadingSpaces(lineText),
          lineNumber,
          endLine: findBodyEndLine(document, lineNumber, declaration.endLine),
          owner: "patch",
          parentRef: parseNameRef(patchMatch[2]),
        },
        type: "patch",
      };
    }
  }

  return undefined;
}

async function getResolvedAgentBindings(source, declaration, fieldKind, seen = new Set()) {
  const cacheKey = `${source.document.uri.toString()}#${declaration.name}#${fieldKind}`;
  if (AGENT_BINDING_CACHE.has(cacheKey)) {
    return AGENT_BINDING_CACHE.get(cacheKey);
  }
  if (seen.has(cacheKey)) {
    return new Map();
  }
  seen.add(cacheKey);

  const root = await resolveConcreteAgentIoRoot(source, declaration, fieldKind, seen);
  if (!root) {
    const emptyBindings = new Map();
    AGENT_BINDING_CACHE.set(cacheKey, emptyBindings);
    return emptyBindings;
  }

  const parentBindings = await resolveParentBindings(root, fieldKind, seen);
  const bindings = await resolveBindingsFromBody({
    bodySpec: root.bodySpec,
    declaration: root.declaration,
    fieldKind,
    parentBindings,
    pathPrefix: [],
    prefixTargets: [],
    source: root.source,
  });
  AGENT_BINDING_CACHE.set(cacheKey, bindings);
  return bindings;
}

async function resolveConcreteAgentIoRoot(source, declaration, fieldKind, seen) {
  const field = findAgentReservedField(source.document, declaration, fieldKind);
  if (field?.type === "ref") {
    const declarationKind =
      fieldKind === "inputs"
        ? DECLARATION_KIND.INPUTS_BLOCK
        : DECLARATION_KIND.OUTPUTS_BLOCK;
    const target = await resolveReferenceTarget(field.ref, source, declarationKind, false);
    if (!target) {
      return undefined;
    }
    return {
      bodySpec: getDeclarationBodySpec(target.declaration),
      declaration: target.declaration,
      source: getIndexedDocumentState(target.document),
    };
  }

  if (field?.bodySpec) {
    return {
      bodySpec: field.bodySpec,
      declaration,
      source,
    };
  }

  if (declaration.parentRef) {
    const parent = await resolveReferenceTarget(
      declaration.parentRef,
      source,
      DECLARATION_KIND.AGENT,
      false,
    );
    if (!parent) {
      return undefined;
    }
    return resolveConcreteAgentIoRoot(
      getIndexedDocumentState(parent.document),
      parent.declaration,
      fieldKind,
      seen,
    );
  }

  return undefined;
}

async function resolveParentBindings(root, fieldKind, seen) {
  let parentRef;
  if (root.bodySpec.owner === "patch") {
    parentRef = root.bodySpec.parentRef;
  } else if (
    (root.declaration.kind === DECLARATION_KIND.INPUTS_BLOCK
      || root.declaration.kind === DECLARATION_KIND.OUTPUTS_BLOCK)
    && root.declaration.parentRef
  ) {
    parentRef = root.declaration.parentRef;
  }

  if (!parentRef) {
    return new Map();
  }

  const declarationKind =
    fieldKind === "inputs"
      ? DECLARATION_KIND.INPUTS_BLOCK
      : DECLARATION_KIND.OUTPUTS_BLOCK;
  const parent = await resolveReferenceTarget(parentRef, root.source, declarationKind, false);
  if (!parent) {
    return new Map();
  }

  return resolveBindingsFromBlockDeclaration(
    getIndexedDocumentState(parent.document),
    parent.declaration,
    fieldKind,
    seen,
  );
}

async function resolveBindingsFromBlockDeclaration(source, declaration, fieldKind, seen) {
  const parentBindings = declaration.parentRef
    ? await resolveParentBindings(
      {
        bodySpec: getDeclarationBodySpec(declaration),
        declaration,
        source,
      },
      fieldKind,
      seen,
    )
    : new Map();

  return resolveBindingsFromBody({
    bodySpec: getDeclarationBodySpec(declaration),
    declaration,
    fieldKind,
    parentBindings,
    pathPrefix: [],
    prefixTargets: [],
    source,
  });
}

async function resolveBindingsFromBody({
  bodySpec,
  declaration,
  fieldKind,
  parentBindings,
  pathPrefix,
  prefixTargets,
  source,
}) {
  const bindings = new Map();
  const entries = scanBindingBodyEntries(source.document, bodySpec, fieldKind);

  for (const entry of entries) {
    if (entry.type === "inherit") {
      const inheritedPrefix = [...pathPrefix, entry.key];
      removeBindingSubtree(bindings, inheritedPrefix);
      copyBindingSubtree(parentBindings, inheritedPrefix, bindings);
      continue;
    }

    if (entry.type !== "section" || !entry.bodySpec) {
      continue;
    }

    const sectionPrefix = [...pathPrefix, entry.key];
    const sectionTargets = [
      ...prefixTargets,
      {
        document: source.document,
        lineNumber: entry.lineNumber,
        selectionRange: entry.keyRange,
      },
    ];

    removeBindingSubtree(bindings, sectionPrefix);

    const childEntries = scanBindingBodyEntries(
      source.document,
      entry.bodySpec,
      fieldKind,
    );
    if (childEntries.length === 1 && childEntries[0].type === "ref") {
      const resolved = await resolveBoundLeafDeclaration(
        childEntries[0].ref,
        source,
        fieldKind,
      );
      if (resolved) {
        bindings.set(bindingPathKey(sectionPrefix), {
          bindingPath: sectionPrefix,
          declaration: resolved.declaration,
          prefixTargets: sectionTargets,
          source: resolved.source,
        });
      }
      continue;
    }

    const childBindings = await resolveBindingsFromBody({
      bodySpec: entry.bodySpec,
      declaration,
      fieldKind,
      parentBindings,
      pathPrefix: sectionPrefix,
      prefixTargets: sectionTargets,
      source,
    });
    for (const [key, binding] of childBindings.entries()) {
      bindings.set(key, binding);
    }
  }

  return bindings;
}

function scanBindingBodyEntries(document, bodySpec, fieldKind) {
  const entries = [];
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return entries;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const inheritItem = lineText.match(INHERIT_RE);
    if (inheritItem) {
      entries.push({
        type: "inherit",
        key: inheritItem[1],
      });
      continue;
    }

    const overrideBody = lineText.match(OVERRIDE_BODY_RE);
    if (overrideBody && !OVERRIDE_REF_RE.test(lineText)) {
      entries.push({
        type: "section",
        bodySpec: createBindingChildBodySpec(
          document,
          bodySpec,
          lineNumber,
          lineText,
          fieldKind,
        ),
        key: overrideBody[1],
        keyRange: createFirstMatchRange(lineText, lineNumber, overrideBody[1]),
        lineNumber,
      });
      continue;
    }

    const sectionLine = lineText.match(
      new RegExp(`^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*${STRING_PATTERN}\\s*$`),
    );
    if (sectionLine) {
      entries.push({
        type: "section",
        bodySpec: createBindingChildBodySpec(
          document,
          bodySpec,
          lineNumber,
          lineText,
          fieldKind,
        ),
        key: sectionLine[1],
        keyRange: createFirstMatchRange(lineText, lineNumber, sectionLine[1]),
        lineNumber,
      });
      continue;
    }

    const standaloneRef = lineText.match(STANDALONE_REF_RE);
    if (standaloneRef) {
      entries.push({
        ref: parseNameRef(standaloneRef[1]),
        type: "ref",
      });
    }
  }

  return entries;
}

function createBindingChildBodySpec(document, bodySpec, lineNumber, lineText, fieldKind) {
  const rawBody =
    bodySpec.type === "io_body"
      ? getIoChildBodySpec(lineText, lineNumber, fieldKind)
      : getRecordChildBodySpec(
          lineText,
          lineNumber,
          fieldKind,
          bodySpec.declarationKind,
        );
  if (!rawBody) {
    return undefined;
  }

  return {
    ...rawBody,
    endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
  };
}

async function resolveBoundLeafDeclaration(ref, source, fieldKind) {
  if (!ref) {
    return undefined;
  }

  const declarationKind =
    fieldKind === "inputs" ? DECLARATION_KIND.INPUT : DECLARATION_KIND.OUTPUT;
  const target = await resolveReferenceTarget(ref, source, declarationKind, false);
  if (!target) {
    return undefined;
  }

  return {
    declaration: target.declaration,
    source: getIndexedDocumentState(target.document),
  };
}

async function resolveReviewSemanticContext(lineContext, source) {
  const { declaration } = lineContext;
  if (!declaration) {
    return undefined;
  }

  if (declaration.kind === DECLARATION_KIND.REVIEW) {
    return getResolvedReviewContext(source, declaration);
  }

  if (declaration.kind === DECLARATION_KIND.OUTPUT) {
    return findReviewContextForOutput(source, declaration);
  }

  return undefined;
}

async function resolveReferenceTarget(ref, source, declarationKind, requireConcrete) {
  const targetSource = await openReferencedDocument(ref, source);
  if (!targetSource) {
    return undefined;
  }

  const declaration = findDeclarationByKind(
    targetSource.index,
    declarationKind,
    ref.declarationName,
    { requireConcrete },
  );
  if (!declaration) {
    return undefined;
  }

  return { declaration, document: targetSource.document };
}

async function resolveWorkflowParentBody(site, source) {
  const { declaration, container } = site.lineContext;
  if (container.owner === "agent_slot") {
    return resolveInheritedWorkflowSlotBody(site, source);
  }

  if (declaration.kind !== DECLARATION_KIND.WORKFLOW || !declaration.parentRef) {
    return undefined;
  }

  const parent = await resolveReferenceTarget(
    declaration.parentRef,
    source,
    DECLARATION_KIND.WORKFLOW,
    false,
  );
  if (!parent) {
    return undefined;
  }

  return {
    document: parent.document,
    bodySpec: getDeclarationBodySpec(parent.declaration),
  };
}

async function resolveSameKindParentBody(site, source, declarationKind) {
  const { declaration } = site.lineContext;
  if (declaration.kind !== declarationKind || !declaration.parentRef) {
    return undefined;
  }

  const parent = await resolveReferenceTarget(
    declaration.parentRef,
    source,
    declarationKind,
    false,
  );
  if (!parent) {
    return undefined;
  }

  return {
    document: parent.document,
    bodySpec: getDeclarationBodySpec(parent.declaration),
  };
}

async function resolveReviewParentBody(site, source) {
  return resolveSameKindParentBody(site, source, DECLARATION_KIND.REVIEW);
}

async function resolveAnalysisParentBody(site, source) {
  return resolveSameKindParentBody(site, source, DECLARATION_KIND.ANALYSIS);
}

async function resolveSchemaParentBody(site, source) {
  return resolveSameKindParentBody(site, source, DECLARATION_KIND.SCHEMA_DECL);
}

async function resolveDocumentParentBody(site, source) {
  return resolveSameKindParentBody(site, source, DECLARATION_KIND.DOCUMENT);
}

async function resolveOutputRecordParentBody(site, source) {
  const { declaration, container } = site.lineContext;
  if (declaration.kind !== DECLARATION_KIND.OUTPUT || !declaration.parentRef) {
    return undefined;
  }

  const parent = await resolveReferenceTarget(
    declaration.parentRef,
    source,
    DECLARATION_KIND.OUTPUT,
    false,
  );
  if (!parent) {
    return undefined;
  }

  let parentBody = {
    document: parent.document,
    bodySpec: getDeclarationBodySpec(parent.declaration),
  };
  if (!parentBody.bodySpec) {
    return undefined;
  }

  for (const segment of container.segmentPath || []) {
    const target = findStructuralKeyTarget(parentBody, segment);
    if (!target || !target.bodySpec) {
      return undefined;
    }

    parentBody = {
      document: parentBody.document,
      bodySpec: target.bodySpec,
    };
  }

  return parentBody;
}

function findWorkflowLawBodySpec(document, workflowBodySpec) {
  const baseIndent = findBodyBaseIndent(document, workflowBodySpec);
  if (baseIndent === undefined) {
    return undefined;
  }

  for (
    let lineNumber = workflowBodySpec.lineNumber + 1;
    lineNumber <= workflowBodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    if (!LAW_FIELD_RE.test(lineText)) {
      continue;
    }

    return {
      type: "law_body",
      endLine: findBodyEndLine(document, lineNumber, workflowBodySpec.endLine),
      indent: leadingSpaces(lineText),
      lineNumber,
      owner: "workflow_law",
    };
  }

  return undefined;
}

async function resolveImmediateParentBody(site, source) {
  const { declaration, container } = site.lineContext;
  if (!declaration) {
    return undefined;
  }

  if (container.type === "agent_body") {
    if (declaration.kind !== DECLARATION_KIND.AGENT || !declaration.parentRef) {
      return undefined;
    }

    const parent = await resolveReferenceTarget(
      declaration.parentRef,
      source,
      DECLARATION_KIND.AGENT,
      false,
    );
    if (!parent) {
      return undefined;
    }

    return {
      document: parent.document,
      bodySpec: getDeclarationBodySpec(parent.declaration),
    };
  }

  if (container.type === "workflow_body") {
    return resolveWorkflowParentBody(site, source);
  }

  if (container.type === "review_body") {
    return resolveReviewParentBody(site, source);
  }

  if (container.type === "analysis_body") {
    return resolveAnalysisParentBody(site, source);
  }

  if (container.type === "schema_body") {
    return resolveSchemaParentBody(site, source);
  }

  if (container.type === "document_body") {
    return resolveDocumentParentBody(site, source);
  }

  if (
    container.type === "review_fields_body"
    || container.type === "review_pre_outcome_body"
    || container.type === "review_outcome_body"
  ) {
    const parentReviewBody = await resolveReviewParentBody(site, source);
    if (!parentReviewBody) {
      return undefined;
    }

    return {
      document: parentReviewBody.document,
      bodySpec: parentReviewBody.bodySpec,
    };
  }

  if (container.type === "law_body") {
    const parentWorkflowBody = await resolveWorkflowParentBody(site, source);
    if (!parentWorkflowBody) {
      return undefined;
    }

    const parentLawBody = findWorkflowLawBodySpec(
      parentWorkflowBody.document,
      parentWorkflowBody.bodySpec,
    );
    if (!parentLawBody) {
      return undefined;
    }

    return {
      document: parentWorkflowBody.document,
      bodySpec: parentLawBody,
    };
  }

  if (container.type === "trust_surface_body") {
    return {
      document: source.document,
      bodySpec: getDeclarationBodySpec(declaration),
    };
  }

  if (container.type === "skills_body") {
    if (
      container.owner !== "skills_decl" ||
      declaration.kind !== DECLARATION_KIND.SKILLS_BLOCK ||
      !declaration.parentRef
    ) {
      return undefined;
    }

    const parent = await resolveReferenceTarget(
      declaration.parentRef,
      source,
      DECLARATION_KIND.SKILLS_BLOCK,
      false,
    );
    if (!parent) {
      return undefined;
    }

    return {
      document: parent.document,
      bodySpec: getDeclarationBodySpec(parent.declaration),
    };
  }

  if (container.type === "io_body") {
    if (container.owner === "patch") {
      const declarationKind =
        container.fieldKind === "inputs"
          ? DECLARATION_KIND.INPUTS_BLOCK
          : DECLARATION_KIND.OUTPUTS_BLOCK;
      const parent = await resolveReferenceTarget(
        container.parentRef,
        source,
        declarationKind,
        false,
      );
      if (!parent) {
        return undefined;
      }

      return {
        document: parent.document,
        bodySpec: getDeclarationBodySpec(parent.declaration),
      };
    }

    if (declaration.kind === DECLARATION_KIND.INPUTS_BLOCK && declaration.parentRef) {
      const parent = await resolveReferenceTarget(
        declaration.parentRef,
        source,
        DECLARATION_KIND.INPUTS_BLOCK,
        false,
      );
      if (!parent) {
        return undefined;
      }

      return {
        document: parent.document,
        bodySpec: getDeclarationBodySpec(parent.declaration),
      };
    }

    if (declaration.kind === DECLARATION_KIND.OUTPUTS_BLOCK && declaration.parentRef) {
      const parent = await resolveReferenceTarget(
        declaration.parentRef,
        source,
        DECLARATION_KIND.OUTPUTS_BLOCK,
        false,
      );
      if (!parent) {
        return undefined;
      }

      return {
        document: parent.document,
        bodySpec: getDeclarationBodySpec(parent.declaration),
      };
    }
  }

  if (container.type === "record_body") {
    return resolveOutputRecordParentBody(site, source);
  }

  return undefined;
}

async function resolveInheritedWorkflowSlotBody(site, source) {
  const { declaration, container } = site.lineContext;
  if (
    declaration.kind !== DECLARATION_KIND.AGENT ||
    !declaration.parentRef ||
    container.slotKey !== "workflow" ||
    container.isOverride
  ) {
    return undefined;
  }

  const parentAgent = await resolveReferenceTarget(
    declaration.parentRef,
    source,
    DECLARATION_KIND.AGENT,
    false,
  );
  if (!parentAgent) {
    return undefined;
  }

  const parentBody = {
    document: parentAgent.document,
    bodySpec: getDeclarationBodySpec(parentAgent.declaration),
  };
  const parentSlot = findStructuralKeyTarget(parentBody, container.slotKey);
  if (!parentSlot) {
    return undefined;
  }

  if (parentSlot.bodySpec) {
    return {
      document: parentBody.document,
      bodySpec: parentSlot.bodySpec,
    };
  }

  if (parentSlot.valueRef) {
    const workflow = await resolveReferenceTarget(
      parentSlot.valueRef,
      getIndexedDocumentState(parentBody.document),
      DECLARATION_KIND.WORKFLOW,
      false,
    );
    if (!workflow) {
      return undefined;
    }

    return {
      document: workflow.document,
      bodySpec: getDeclarationBodySpec(workflow.declaration),
    };
  }

  return undefined;
}

function findStructuralKeyTarget(parentBody, key) {
  switch (parentBody.bodySpec.type) {
    case "agent_body":
      return getAgentBodyItems(parentBody.document, parentBody.bodySpec).get(key);
    case "review_body":
      return getReviewBodyItems(parentBody.document, parentBody.bodySpec).get(key);
    case "analysis_body":
      return getAnalysisBodyItems(parentBody.document, parentBody.bodySpec).get(key);
    case "schema_body":
      return getSchemaBodyItems(parentBody.document, parentBody.bodySpec).get(key);
    case "document_body":
      return getDocumentBodyItems(parentBody.document, parentBody.bodySpec).get(key);
    case "workflow_body":
      return getWorkflowBodyItems(parentBody.document, parentBody.bodySpec).get(key);
    case "law_body":
      return getLawBodyItems(parentBody.document, parentBody.bodySpec).get(key);
    case "workflow_section_body":
      return getWorkflowSectionBodyItems(parentBody.document, parentBody.bodySpec).get(key);
    case "skills_body":
      return getSkillsBodyItems(parentBody.document, parentBody.bodySpec).get(key);
    case "io_body":
      return getIoBodyItems(parentBody.document, parentBody.bodySpec).get(key);
    case "record_body":
      return getRecordBodyItems(parentBody.document, parentBody.bodySpec).get(key);
    default:
      return undefined;
  }
}

async function openReferencedDocument(ref, source) {
  const targetUri = resolveRefTargetUri(
    ref,
    source.document.uri,
    source.context,
    source.importEntries,
  );
  if (!targetUri || !(await uriExists(targetUri))) {
    return undefined;
  }

  if (targetUri.toString() === source.document.uri.toString()) {
    return source;
  }

  const document = await vscode.workspace.openTextDocument(targetUri);
  return getIndexedDocumentState(document);
}

function getIndexedDocumentState(document) {
  const index = getPromptIndex(document);
  const context = getDocumentContext(document);
  return {
    context,
    document,
    importEntries: context ? collectImportEntries(document, context) : [],
    index,
  };
}

async function getResolvedReviewContext(source, declaration, seen = new Set()) {
  const cacheKey = `${source.document.uri.toString()}#${declaration.name}`;
  if (REVIEW_CONTEXT_CACHE.has(cacheKey)) {
    return REVIEW_CONTEXT_CACHE.get(cacheKey);
  }
  if (seen.has(cacheKey)) {
    return undefined;
  }
  seen.add(cacheKey);

  const bodySpec = getDeclarationBodySpec(declaration);
  if (!bodySpec || bodySpec.type !== "review_body") {
    return undefined;
  }

  let inherited;
  if (declaration.parentRef) {
    const parent = await resolveReferenceTarget(
      declaration.parentRef,
      source,
      DECLARATION_KIND.REVIEW,
      false,
    );
    if (parent) {
      inherited = await getResolvedReviewContext(
        getIndexedDocumentState(parent.document),
        parent.declaration,
        seen,
      );
    }
  }

  const local = getLocalReviewConfig(source.document, bodySpec);
  let fieldBindings = inherited?.fieldBindings;
  let fieldsLineNumber = inherited?.fieldsLineNumber;
  let fieldsSource = inherited?.fieldsSource;

  if (local.fieldsMode === "set" || local.fieldsMode === "override") {
    fieldBindings = local.fieldBindings;
    fieldsLineNumber = local.fieldsLineNumber;
    fieldsSource = source;
  } else if (local.fieldsMode === "inherit" && inherited) {
    fieldBindings = inherited.fieldBindings;
    fieldsLineNumber = inherited.fieldsLineNumber;
    fieldsSource = inherited.fieldsSource;
  }

  const contractRef = local.contractRef || inherited?.contractRef;
  const commentOutputRef = local.commentOutputRef || inherited?.commentOutputRef;

  const contractTarget =
    contractRef
      ? await resolveReferenceTarget(contractRef, source, DECLARATION_KIND.WORKFLOW, false)
      : undefined;
  const outputTarget =
    commentOutputRef
      ? await resolveReferenceTarget(commentOutputRef, source, DECLARATION_KIND.OUTPUT, false)
      : undefined;

  const context = {
    contractGateKeys:
      contractTarget
        ? new Set([...getWorkflowBodyItems(
          contractTarget.document,
          getDeclarationBodySpec(contractTarget.declaration),
        ).keys()])
        : new Set(),
    contractRef,
    contractTarget: contractTarget
      ? {
          declaration: contractTarget.declaration,
          source: getIndexedDocumentState(contractTarget.document),
        }
      : undefined,
    fieldBindings: fieldBindings || new Map(),
    fieldsLineNumber,
    fieldsSource,
    outputTarget: outputTarget
      ? {
          declaration: outputTarget.declaration,
          source: getIndexedDocumentState(outputTarget.document),
        }
      : undefined,
    reviewDeclaration: declaration,
    source,
  };

  REVIEW_CONTEXT_CACHE.set(cacheKey, context);
  return context;
}

async function findReviewContextForOutput(source, declaration) {
  const reviews = source.index.byKind.get(DECLARATION_KIND.REVIEW);
  if (!reviews) {
    return undefined;
  }

  const matches = [];
  for (const review of reviews.values()) {
    const context = await getResolvedReviewContext(source, review);
    if (!context || !context.outputTarget) {
      continue;
    }
    if (
      context.outputTarget.declaration.name === declaration.name
      && context.outputTarget.source.document.uri.toString() === source.document.uri.toString()
    ) {
      matches.push(context);
    }
  }

  return matches.length === 1 ? matches[0] : undefined;
}

function getLocalReviewConfig(document, bodySpec) {
  const config = {
    commentOutputRef: undefined,
    contractRef: undefined,
    fieldBindings: new Map(),
    fieldsLineNumber: undefined,
    fieldsMode: undefined,
  };
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return config;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const configRef = lineText.match(REVIEW_CONFIG_REF_RE);
    if (configRef) {
      if (configRef[1] === "contract") {
        config.contractRef = parseNameRef(configRef[2]);
      } else if (configRef[1] === "comment_output") {
        config.commentOutputRef = parseNameRef(configRef[2]);
      }
      continue;
    }

    const inheritItem = lineText.match(INHERIT_RE);
    if (inheritItem && inheritItem[1] === "fields") {
      config.fieldsMode = "inherit";
      config.fieldsLineNumber = lineNumber;
      continue;
    }

    if (REVIEW_FIELDS_FIELD_RE.test(lineText) || REVIEW_OVERRIDE_FIELDS_RE.test(lineText)) {
      const childBody = getReviewChildBodySpec(lineText, lineNumber);
      config.fieldBindings = childBody
        ? getReviewFieldBindings(
          document,
          {
            ...childBody,
            endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
          },
        )
        : new Map();
      config.fieldsLineNumber = lineNumber;
      config.fieldsMode = REVIEW_OVERRIDE_FIELDS_RE.test(lineText) ? "override" : "set";
    }
  }

  return config;
}

function getReviewFieldBindings(document, bodySpec) {
  const bindings = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return bindings;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const binding = lineText.match(REVIEW_FIELD_BINDING_RE);
    if (!binding) {
      continue;
    }
    bindings.set(binding[1], binding[2].split("."));
  }

  return bindings;
}

function getPromptIndex(document) {
  const cacheKey = document.uri.toString();
  const cached = INDEX_CACHE.get(cacheKey);
  if (cached && cached.version === document.version) {
    return cached.index;
  }

  const declarations = [];
  let previousDeclaration;

  for (let lineNumber = 0; lineNumber < document.lineCount; lineNumber += 1) {
    const lineText = document.lineAt(lineNumber).text;
    if (leadingSpaces(lineText) !== 0) {
      continue;
    }

    const declaration = parseDeclarationLine(lineText, lineNumber);
    if (!declaration) {
      continue;
    }

    if (previousDeclaration) {
      previousDeclaration.endLine = lineNumber - 1;
    }

    declarations.push(declaration);
    previousDeclaration = declaration;
  }

  if (previousDeclaration) {
    previousDeclaration.endLine = document.lineCount - 1;
  }

  const byKind = new Map();
  for (const declaration of declarations) {
    if (!byKind.has(declaration.kind)) {
      byKind.set(declaration.kind, new Map());
    }
    byKind.get(declaration.kind).set(declaration.name, declaration);
  }

  const index = { byKind, declarations };
  INDEX_CACHE.set(cacheKey, { version: document.version, index });
  return index;
}

function parseDeclarationLine(lineText, lineNumber) {
  for (const definition of DECLARATION_DEFINITIONS) {
    const match = lineText.match(definition.regex);
    if (!match) {
      continue;
    }

    const name = match[definition.nameGroup];
    const parentRef =
      definition.parentGroup && match[definition.parentGroup]
        ? parseNameRef(match[definition.parentGroup])
        : undefined;
    return {
      abstract:
        definition.abstractGroup !== undefined
          ? Boolean(match[definition.abstractGroup])
          : false,
      endLine: lineNumber,
      kind: definition.kind,
      lineNumber,
      name,
      nameRange: createNameRange(lineText, lineNumber, name),
      parentRange:
        definition.parentGroup && match[definition.parentGroup]
          ? createLastMatchRange(
              lineText,
              lineNumber,
              match[definition.parentGroup],
            )
          : undefined,
      parentRef,
    };
  }

  return undefined;
}

function findDeclarationByKind(index, kind, name, options = {}) {
  const declaration = index.byKind.get(kind)?.get(name);
  if (!declaration) {
    return undefined;
  }

  if (options.requireConcrete && declaration.abstract) {
    return undefined;
  }

  return declaration;
}

function findReadableDeclaration(index, declarationName) {
  const matches = READABLE_DECLARATION_KINDS
    .map((kind) => findDeclarationByKind(index, kind, declarationName))
    .filter(Boolean);

  return matches.length === 1 ? matches[0] : undefined;
}

function findAddressableDeclaration(index, declarationName) {
  const matches = ADDRESSABLE_DECLARATION_KINDS
    .map((kind) => findDeclarationByKind(index, kind, declarationName))
    .filter(Boolean);

  return matches.length === 1 ? matches[0] : undefined;
}

function getLineContext(source, lineNumber) {
  const declaration = findDeclarationForLine(source.index, lineNumber);
  if (!declaration) {
    return {
      container: { type: "none" },
      declaration: undefined,
    };
  }

  const stack = [];
  const rootBody = getDeclarationBodySpec(declaration);
  if (rootBody) {
    rootBody.segmentPath = [];
    stack.push(rootBody);
  }

  for (
    let currentLine = declaration.lineNumber + 1;
    currentLine < lineNumber;
    currentLine += 1
  ) {
    const lineText = source.document.lineAt(currentLine).text;
    if (isIgnorableLine(lineText)) {
      continue;
    }

    const indent = leadingSpaces(lineText);
    while (stack.length > 1 && indent <= stack.at(-1).indent) {
      stack.pop();
    }

    const childBody = getChildBodySpecForLine(
      source.document,
      declaration,
      stack.at(-1),
      currentLine,
    );
    if (childBody) {
      const parentPath = stack.at(-1)?.segmentPath || [];
      const segmentKey = getChildBodySegmentKey(lineText, childBody);
      childBody.segmentPath = segmentKey
        ? [...parentPath, segmentKey]
        : [...parentPath];
      stack.push(childBody);
    }
  }

  const currentLineText = source.document.lineAt(lineNumber).text;
  const currentIndent = isIgnorableLine(currentLineText)
    ? Number.MAX_SAFE_INTEGER
    : leadingSpaces(currentLineText);
  while (stack.length > 1 && currentIndent <= stack.at(-1).indent) {
    stack.pop();
  }

  return {
    container: stack.at(-1) || { type: "none" },
    declaration,
  };
}

function getChildBodySegmentKey(lineText, childBody) {
  if (childBody.type !== "record_body") {
    return undefined;
  }

  const overrideBody = lineText.match(OVERRIDE_BODY_RE);
  if (overrideBody && !OVERRIDE_REF_RE.test(lineText)) {
    return overrideBody[1];
  }

  const keyedItem = lineText.match(
    new RegExp(`^\\s*(${IDENTIFIER_PATTERN})\\s*:`),
  );
  return keyedItem ? keyedItem[1] : undefined;
}

function getDeclarationBodySpec(declaration) {
  switch (declaration.kind) {
    case DECLARATION_KIND.AGENT:
      return {
        type: "agent_body",
        declarationKind: declaration.kind,
        declarationLine: declaration.lineNumber,
        endLine: declaration.endLine,
        indent: 0,
        lineNumber: declaration.lineNumber,
      };
    case DECLARATION_KIND.REVIEW:
      return {
        type: "review_body",
        declarationKind: declaration.kind,
        declarationLine: declaration.lineNumber,
        endLine: declaration.endLine,
        indent: 0,
        lineNumber: declaration.lineNumber,
        owner: "review_decl",
      };
    case DECLARATION_KIND.ANALYSIS:
      return {
        type: "analysis_body",
        declarationKind: declaration.kind,
        declarationLine: declaration.lineNumber,
        endLine: declaration.endLine,
        indent: 0,
        lineNumber: declaration.lineNumber,
        owner: "analysis_decl",
      };
    case DECLARATION_KIND.SCHEMA_DECL:
      return {
        type: "schema_body",
        declarationKind: declaration.kind,
        declarationLine: declaration.lineNumber,
        endLine: declaration.endLine,
        indent: 0,
        lineNumber: declaration.lineNumber,
        owner: "schema_decl",
      };
    case DECLARATION_KIND.DOCUMENT:
      return {
        type: "document_body",
        declarationKind: declaration.kind,
        declarationLine: declaration.lineNumber,
        endLine: declaration.endLine,
        indent: 0,
        lineNumber: declaration.lineNumber,
        owner: "document_decl",
      };
    case DECLARATION_KIND.WORKFLOW:
      return {
        type: "workflow_body",
        declarationKind: declaration.kind,
        declarationLine: declaration.lineNumber,
        endLine: declaration.endLine,
        indent: 0,
        lineNumber: declaration.lineNumber,
        owner: "workflow_decl",
      };
    case DECLARATION_KIND.SKILLS_BLOCK:
      return {
        type: "skills_body",
        declarationKind: declaration.kind,
        declarationLine: declaration.lineNumber,
        endLine: declaration.endLine,
        indent: 0,
        lineNumber: declaration.lineNumber,
        owner: "skills_decl",
      };
    case DECLARATION_KIND.INPUTS_BLOCK:
      return {
        type: "io_body",
        declarationKind: declaration.kind,
        declarationLine: declaration.lineNumber,
        endLine: declaration.endLine,
        fieldKind: "inputs",
        indent: 0,
        lineNumber: declaration.lineNumber,
        owner: "decl",
      };
    case DECLARATION_KIND.OUTPUTS_BLOCK:
      return {
        type: "io_body",
        declarationKind: declaration.kind,
        declarationLine: declaration.lineNumber,
        endLine: declaration.endLine,
        fieldKind: "outputs",
        indent: 0,
        lineNumber: declaration.lineNumber,
        owner: "decl",
      };
    case DECLARATION_KIND.INPUT:
    case DECLARATION_KIND.INPUT_SOURCE:
    case DECLARATION_KIND.OUTPUT:
    case DECLARATION_KIND.OUTPUT_TARGET:
    case DECLARATION_KIND.OUTPUT_SHAPE:
    case DECLARATION_KIND.OUTPUT_SCHEMA:
    case DECLARATION_KIND.SKILL:
      return {
        type: "record_body",
        declarationKind: declaration.kind,
        declarationLine: declaration.lineNumber,
        endLine: declaration.endLine,
        fieldKind: undefined,
        indent: 0,
        lineNumber: declaration.lineNumber,
      };
    case DECLARATION_KIND.ENUM:
      return {
        type: "enum_body",
        declarationKind: declaration.kind,
        declarationLine: declaration.lineNumber,
        endLine: declaration.endLine,
        indent: 0,
        lineNumber: declaration.lineNumber,
      };
    default:
      return undefined;
  }
}

function getChildBodySpecForLine(document, declaration, container, lineNumber) {
  const lineText = document.lineAt(lineNumber).text;
  const nextContent = findNextSignificantLine(document, lineNumber + 1, declaration.endLine);
  if (!nextContent || nextContent.indent <= leadingSpaces(lineText)) {
    return undefined;
  }

  let childBody;

  switch (container.type) {
    case "agent_body":
      childBody = getAgentChildBodySpec(lineText, lineNumber, declaration);
      break;
    case "review_body":
      childBody = getReviewChildBodySpec(lineText, lineNumber);
      break;
    case "review_pre_outcome_body":
      childBody = getReviewPreOutcomeChildBodySpec(lineText, lineNumber);
      break;
    case "review_outcome_body":
      childBody = getReviewOutcomeChildBodySpec(lineText, lineNumber);
      break;
    case "review_match_body":
      childBody = getReviewMatchBodyChildBodySpec(
        lineText,
        lineNumber,
        container.owner,
      );
      break;
    case "workflow_body":
      childBody = getWorkflowChildBodySpec(lineText, lineNumber);
      break;
    case "law_body":
      childBody = getLawBodyChildBodySpec(lineText, lineNumber, true);
      break;
    case "law_statement_body":
      childBody = getLawBodyChildBodySpec(lineText, lineNumber, false);
      break;
    case "law_match_body":
      childBody = getLawMatchBodyChildBodySpec(lineText, lineNumber);
      break;
    case "workflow_section_body":
      childBody = getWorkflowSectionChildBodySpec(lineText, lineNumber);
      break;
    case "skills_body":
      childBody = getSkillsChildBodySpec(
        lineText,
        lineNumber,
        true,
        container.fieldKind,
      );
      break;
    case "skills_section_body":
      childBody = getSkillsChildBodySpec(
        lineText,
        lineNumber,
        false,
        container.fieldKind,
      );
      break;
    case "io_body":
      childBody = getIoChildBodySpec(lineText, lineNumber, container.fieldKind);
      break;
    case "record_body":
      childBody = getRecordChildBodySpec(
        lineText,
        lineNumber,
        container.fieldKind,
        container.declarationKind,
      );
      break;
    default:
      childBody = undefined;
      break;
  }

  if (!childBody) {
    return undefined;
  }

  childBody.endLine = findBodyEndLine(document, lineNumber, declaration.endLine);
  return childBody;
}

function getReadableChildBodySpec(document, kind, lineText, lineNumber, endLine) {
  const indent = leadingSpaces(lineText);
  switch (kind) {
    case "section":
    case "guard":
      return {
        type: "readable_section_body",
        endLine: findBodyEndLine(document, lineNumber, endLine),
        indent,
        lineNumber,
      };
    case "sequence":
    case "bullets":
    case "checklist":
      return {
        type: "readable_list_body",
        endLine: findBodyEndLine(document, lineNumber, endLine),
        indent,
        lineNumber,
      };
    case "definitions":
    case "properties":
      return {
        type: kind === "properties" ? "readable_properties_body" : "readable_definitions_body",
        endLine: findBodyEndLine(document, lineNumber, endLine),
        indent,
        lineNumber,
      };
    case "table":
      return {
        type: "readable_table_body",
        endLine: findBodyEndLine(document, lineNumber, endLine),
        indent,
        lineNumber,
      };
    case "footnotes":
      return {
        type: "readable_footnotes_body",
        endLine: findBodyEndLine(document, lineNumber, endLine),
        indent,
        lineNumber,
      };
    default:
      return undefined;
  }
}

function getAgentChildBodySpec(lineText, lineNumber) {
  const inlineIoField = lineText.match(
    new RegExp(`^\\s*(inputs|outputs)\\s*:\\s*${STRING_PATTERN}\\s*$`),
  );
  if (inlineIoField) {
    return {
      type: "record_body",
      fieldKind: inlineIoField[1],
      indent: leadingSpaces(lineText),
      lineNumber,
    };
  }

  const patchField = lineText.match(PATCH_FIELD_RE);
  if (patchField) {
    return {
      type: "io_body",
      fieldKind: patchField[1],
      indent: leadingSpaces(lineText),
      lineNumber,
      owner: "patch",
      parentRef: parseNameRef(patchField[2]),
    };
  }

  if (
    new RegExp(`^\\s*skills\\s*:\\s*${STRING_PATTERN}\\s*$`).test(lineText)
  ) {
    return {
      type: "skills_body",
      indent: leadingSpaces(lineText),
      lineNumber,
      owner: "agent_skills",
    };
  }

  if (new RegExp(`^\\s*review\\s*:\\s*${DOTTED_NAME_PATTERN}\\s*$`).test(lineText)) {
    return undefined;
  }

  const overrideTitleMatch = lineText.match(
    new RegExp(
      `^\\s*override\\s+(${IDENTIFIER_PATTERN})\\s*:\\s*${STRING_PATTERN}\\s*$`,
    ),
  );
  if (overrideTitleMatch) {
    return {
      type: "workflow_body",
      indent: leadingSpaces(lineText),
      isOverride: true,
      lineNumber,
      owner: "agent_slot",
      slotKey: overrideTitleMatch[1],
    };
  }

  const slotTitleMatch = lineText.match(
    new RegExp(`^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*${STRING_PATTERN}\\s*$`),
  );
  if (slotTitleMatch && !RESERVED_AGENT_FIELD_KEYS.has(slotTitleMatch[1])) {
    return {
      type: "workflow_body",
      indent: leadingSpaces(lineText),
      isOverride: false,
      lineNumber,
      owner: "agent_slot",
      slotKey: slotTitleMatch[1],
    };
  }

  return undefined;
}

function getReviewChildBodySpec(lineText, lineNumber) {
  if (REVIEW_FIELDS_FIELD_RE.test(lineText) || REVIEW_OVERRIDE_FIELDS_RE.test(lineText)) {
    return {
      type: "review_fields_body",
      indent: leadingSpaces(lineText),
      lineNumber,
      owner: "review_fields",
    };
  }

  if (REVIEW_SUBJECT_MAP_FIELD_RE.test(lineText)) {
    return {
      type: "review_subject_map_body",
      indent: leadingSpaces(lineText),
      lineNumber,
      owner: "review_subject_map",
    };
  }

  const outcomeHeader = lineText.match(REVIEW_OUTCOME_HEADER_RE);
  if (outcomeHeader) {
    return {
      type: "review_outcome_body",
      indent: leadingSpaces(lineText),
      lineNumber,
      owner: outcomeHeader[1],
    };
  }

  const overrideOutcome = lineText.match(REVIEW_OVERRIDE_OUTCOME_RE);
  if (overrideOutcome) {
    return {
      type: "review_outcome_body",
      indent: leadingSpaces(lineText),
      lineNumber,
      owner: overrideOutcome[1],
    };
  }

  if (
    (REVIEW_OVERRIDE_SECTION_RE.test(lineText) && !REVIEW_OVERRIDE_OUTCOME_RE.test(lineText))
    || REVIEW_SECTION_RE.test(lineText)
  ) {
    return {
      type: "review_pre_outcome_body",
      indent: leadingSpaces(lineText),
      lineNumber,
      owner: "review_section",
    };
  }

  return undefined;
}

function getReviewPreOutcomeChildBodySpec(lineText, lineNumber) {
  if (LAW_MATCH_RE.test(lineText)) {
    return {
      type: "review_match_body",
      indent: leadingSpaces(lineText),
      lineNumber,
      owner: "review_pre_outcome",
    };
  }

  if (LAW_WHEN_RE.test(lineText)) {
    return {
      type: "review_pre_outcome_body",
      indent: leadingSpaces(lineText),
      lineNumber,
      owner: "review_pre_outcome",
    };
  }

  return undefined;
}

function getReviewOutcomeChildBodySpec(lineText, lineNumber) {
  if (LAW_MATCH_RE.test(lineText)) {
    return {
      type: "review_match_body",
      indent: leadingSpaces(lineText),
      lineNumber,
      owner: "review_outcome",
    };
  }

  if (LAW_WHEN_RE.test(lineText)) {
    return {
      type: "review_outcome_body",
      indent: leadingSpaces(lineText),
      lineNumber,
      owner: "review_outcome",
    };
  }

  return undefined;
}

function getReviewMatchBodyChildBodySpec(lineText, lineNumber, owner) {
  if (!LAW_MATCH_ARM_RE.test(lineText)) {
    return undefined;
  }

  return {
    type: owner === "review_outcome" ? "review_outcome_body" : "review_pre_outcome_body",
    indent: leadingSpaces(lineText),
    lineNumber,
    owner,
  };
}

function getWorkflowChildBodySpec(lineText, lineNumber) {
  if (LAW_FIELD_RE.test(lineText)) {
    return {
      type: "law_body",
      indent: leadingSpaces(lineText),
      lineNumber,
      owner: "workflow_law",
    };
  }

  if (new RegExp(`^\\s*skills\\s*:\\s*${STRING_PATTERN}\\s*$`).test(lineText)) {
    return {
      type: "skills_body",
      indent: leadingSpaces(lineText),
      lineNumber,
      owner: "workflow_skills",
    };
  }

  if (
    new RegExp(`^\\s*override\\s+skills\\s*:\\s*${STRING_PATTERN}\\s*$`).test(
      lineText,
    )
  ) {
    return {
      type: "skills_body",
      indent: leadingSpaces(lineText),
      lineNumber,
      owner: "workflow_override_skills",
    };
  }

  if (
    OVERRIDE_BODY_RE.test(lineText) &&
    !OVERRIDE_REF_RE.test(lineText)
  ) {
    return {
      type: "workflow_section_body",
      indent: leadingSpaces(lineText),
      lineNumber,
    };
  }

  if (
    new RegExp(`^\\s*${IDENTIFIER_PATTERN}\\s*:\\s*${STRING_PATTERN}\\s*$`).test(
      lineText,
    )
  ) {
    return {
      type: "workflow_section_body",
      indent: leadingSpaces(lineText),
      lineNumber,
    };
  }

  return undefined;
}

function getWorkflowSectionChildBodySpec(lineText, lineNumber) {
  if (
    new RegExp(`^\\s*${IDENTIFIER_PATTERN}\\s*:\\s*${STRING_PATTERN}\\s*$`).test(
      lineText,
    )
  ) {
    return {
      type: "workflow_section_body",
      indent: leadingSpaces(lineText),
      lineNumber,
    };
  }

  return undefined;
}

function getLawBodyChildBodySpec(lineText, lineNumber, allowStructural) {
  if (LAW_MATCH_RE.test(lineText) || LAW_ROUTE_FROM_RE.test(lineText)) {
    return {
      type: "law_match_body",
      indent: leadingSpaces(lineText),
      lineNumber,
    };
  }

  if (LAW_WHEN_RE.test(lineText)) {
    return {
      type: "law_statement_body",
      indent: leadingSpaces(lineText),
      lineNumber,
    };
  }

  if (
    allowStructural &&
    (LAW_OVERRIDE_SECTION_RE.test(lineText) || LAW_SECTION_RE.test(lineText))
  ) {
    return {
      type: "law_statement_body",
      indent: leadingSpaces(lineText),
      lineNumber,
    };
  }

  return undefined;
}

function getLawMatchBodyChildBodySpec(lineText, lineNumber) {
  if (!LAW_MATCH_ARM_RE.test(lineText)) {
    return undefined;
  }

  return {
    type: "law_statement_body",
    indent: leadingSpaces(lineText),
    lineNumber,
  };
}

function getSkillsChildBodySpec(lineText, lineNumber, allowStructural, fieldKind) {
  if (
    allowStructural &&
    OVERRIDE_BODY_RE.test(lineText) &&
    !OVERRIDE_REF_RE.test(lineText)
  ) {
    return {
      type: "skills_section_body",
      fieldKind,
      indent: leadingSpaces(lineText),
      lineNumber,
    };
  }

  if (
    new RegExp(`^\\s*${IDENTIFIER_PATTERN}\\s*:\\s*${STRING_PATTERN}\\s*$`).test(
      lineText,
    )
  ) {
    return {
      type: "skills_section_body",
      fieldKind,
      indent: leadingSpaces(lineText),
      lineNumber,
    };
  }

  if (SKILL_ENTRY_RE.test(lineText) || (allowStructural && OVERRIDE_REF_RE.test(lineText))) {
    return {
      type: "record_body",
      fieldKind,
      indent: leadingSpaces(lineText),
      lineNumber,
    };
  }

  return undefined;
}

function getIoChildBodySpec(lineText, lineNumber, fieldKind) {
  if (
    OVERRIDE_BODY_RE.test(lineText) &&
    !OVERRIDE_REF_RE.test(lineText)
  ) {
    return {
      type: "record_body",
      fieldKind,
      indent: leadingSpaces(lineText),
      lineNumber,
    };
  }

  if (
    new RegExp(`^\\s*${IDENTIFIER_PATTERN}\\s*:\\s*${STRING_PATTERN}\\s*$`).test(
      lineText,
    ) ||
    STANDALONE_REF_RE.test(lineText)
  ) {
    return {
      type: "record_body",
      fieldKind,
      indent: leadingSpaces(lineText),
      lineNumber,
    };
  }

  return undefined;
}

function getRecordChildBodySpec(lineText, lineNumber, fieldKind, declarationKind) {
  if (
    OVERRIDE_BODY_RE.test(lineText) &&
    !OVERRIDE_REF_RE.test(lineText)
  ) {
    return {
      type: "record_body",
      declarationKind,
      fieldKind,
      indent: leadingSpaces(lineText),
      lineNumber,
    };
  }

  if (TRUST_SURFACE_FIELD_RE.test(lineText)) {
    return {
      type: "trust_surface_body",
      fieldKind,
      indent: leadingSpaces(lineText),
      lineNumber,
    };
  }

  if (GUARDED_OUTPUT_HEADER_RE.test(lineText)) {
    return {
      type: "record_body",
      declarationKind,
      fieldKind,
      indent: leadingSpaces(lineText),
      lineNumber,
    };
  }

  if (GUARDED_RECORD_ITEM_RE.test(lineText)) {
    return {
      type: "record_body",
      declarationKind,
      fieldKind,
      indent: leadingSpaces(lineText),
      lineNumber,
    };
  }

  if (
    new RegExp(
      `^\\s*(?:${IDENTIFIER_PATTERN}\\s*:\\s*(?:${STRING_PATTERN}|${DOTTED_NAME_PATTERN}|${PATH_REF_PATTERN})|${DOTTED_NAME_PATTERN})\\s*$`,
    ).test(lineText)
  ) {
    return {
      type: "record_body",
      declarationKind,
      fieldKind,
      indent: leadingSpaces(lineText),
      lineNumber,
    };
  }

  return undefined;
}

function getAgentBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.declarationLine + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const abstractField = lineText.match(ABSTRACT_FIELD_RE);
    if (abstractField && !RESERVED_AGENT_FIELD_KEYS.has(abstractField[1])) {
      items.set(abstractField[1], {
        bodySpec: undefined,
        keyRange: createFirstMatchRange(lineText, lineNumber, abstractField[1]),
        lineNumber,
      });
      continue;
    }

    const inheritItem = lineText.match(INHERIT_RE);
    if (inheritItem) {
      items.set(inheritItem[1], {
        bodySpec: undefined,
        keyRange: createFirstMatchRange(lineText, lineNumber, inheritItem[1]),
        lineNumber,
      });
      continue;
    }

    const overrideRef = lineText.match(OVERRIDE_REF_RE);
    if (overrideRef) {
      items.set(overrideRef[1], {
        bodySpec: undefined,
        keyRange: createFirstMatchRange(lineText, lineNumber, overrideRef[1]),
        lineNumber,
        valueRef: parseNameRef(overrideRef[2]),
      });
      continue;
    }

    const overrideTitle = lineText.match(
      new RegExp(
        `^\\s*override\\s+(${IDENTIFIER_PATTERN})\\s*:\\s*${STRING_PATTERN}\\s*$`,
      ),
    );
    if (overrideTitle && !RESERVED_AGENT_FIELD_KEYS.has(overrideTitle[1])) {
      items.set(overrideTitle[1], {
        bodySpec: {
          type: "workflow_body",
          endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
          indent: leadingSpaces(lineText),
          lineNumber,
          owner: "agent_slot",
          slotKey: overrideTitle[1],
        },
        keyRange: createFirstMatchRange(lineText, lineNumber, overrideTitle[1]),
        lineNumber,
      });
      continue;
    }

    const slotRef = lineText.match(AGENT_SLOT_REF_RE);
    if (slotRef && !RESERVED_AGENT_FIELD_KEYS.has(slotRef[1])) {
      items.set(slotRef[1], {
        bodySpec: undefined,
        keyRange: createFirstMatchRange(lineText, lineNumber, slotRef[1]),
        lineNumber,
        valueRef: parseNameRef(slotRef[2]),
      });
      continue;
    }

    const slotTitle = lineText.match(
      new RegExp(`^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*${STRING_PATTERN}\\s*$`),
    );
    if (slotTitle && !RESERVED_AGENT_FIELD_KEYS.has(slotTitle[1])) {
      items.set(slotTitle[1], {
        bodySpec: {
          type: "workflow_body",
          endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
          indent: leadingSpaces(lineText),
          lineNumber,
          owner: "agent_slot",
          slotKey: slotTitle[1],
        },
        keyRange: createFirstMatchRange(lineText, lineNumber, slotTitle[1]),
        lineNumber,
      });
    }
  }

  return items;
}

function getWorkflowBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const inheritItem = lineText.match(INHERIT_RE);
    if (inheritItem) {
      items.set(inheritItem[1], {
        keyRange: createFirstMatchRange(lineText, lineNumber, inheritItem[1]),
        lineNumber,
      });
      continue;
    }

    const workflowUse = lineText.match(USE_RE);
    if (workflowUse) {
      items.set(workflowUse[1], {
        declarationKind: DECLARATION_KIND.WORKFLOW,
        keyRange: createFirstMatchRange(lineText, lineNumber, workflowUse[1]),
        lineNumber,
        titleDeclarationKind: DECLARATION_KIND.WORKFLOW,
        titleRef: parseNameRef(workflowUse[2]),
        valueRef: parseNameRef(workflowUse[2]),
      });
      continue;
    }

    const skillsRef = lineText.match(WORKFLOW_SKILLS_REF_RE);
    if (skillsRef) {
      items.set("skills", {
        declarationKind: DECLARATION_KIND.SKILLS_BLOCK,
        keyRange: createFirstMatchRange(lineText, lineNumber, "skills"),
        lineNumber,
        titleDeclarationKind: DECLARATION_KIND.SKILLS_BLOCK,
        titleRef: parseNameRef(skillsRef[1]),
        valueRef: parseNameRef(skillsRef[1]),
      });
      continue;
    }

    const overrideRef = lineText.match(OVERRIDE_REF_RE);
    if (overrideRef) {
      const key = overrideRef[1];
      items.set(overrideRef[1], {
        declarationKind:
          key === "skills"
            ? DECLARATION_KIND.SKILLS_BLOCK
            : DECLARATION_KIND.WORKFLOW,
        keyRange: createFirstMatchRange(lineText, lineNumber, overrideRef[1]),
        lineNumber,
        titleDeclarationKind:
          key === "skills"
            ? DECLARATION_KIND.SKILLS_BLOCK
            : DECLARATION_KIND.WORKFLOW,
        titleRef: parseNameRef(overrideRef[2]),
        valueRef: parseNameRef(overrideRef[2]),
      });
      continue;
    }

    if (
      OVERRIDE_BODY_RE.test(lineText) &&
      !OVERRIDE_REF_RE.test(lineText)
    ) {
      const key = lineText.trim().split(/\s+/)[1].replace(":", "");
      const childBody = getWorkflowChildBodySpec(lineText, lineNumber);
      items.set(key, {
        bodySpec: childBody
          ? {
              ...childBody,
              endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
            }
          : undefined,
        keyRange: createFirstMatchRange(lineText, lineNumber, key),
        lineNumber,
      });
      continue;
    }

    const localSection = lineText.match(
      new RegExp(`^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*${STRING_PATTERN}\\s*$`),
    );
    if (localSection) {
      const childBody = getWorkflowChildBodySpec(lineText, lineNumber);
      items.set(localSection[1], {
        bodySpec: childBody
          ? {
              ...childBody,
              endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
            }
          : undefined,
        keyRange: createFirstMatchRange(lineText, lineNumber, localSection[1]),
        lineNumber,
      });
    }
  }

  return items;
}

function getLawBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const inheritItem = lineText.match(INHERIT_RE);
    if (inheritItem) {
      items.set(inheritItem[1], {
        keyRange: createFirstMatchRange(lineText, lineNumber, inheritItem[1]),
        lineNumber,
      });
      continue;
    }

    const overrideSection = lineText.match(LAW_OVERRIDE_SECTION_RE);
    if (overrideSection) {
      items.set(overrideSection[1], {
        keyRange: createFirstMatchRange(lineText, lineNumber, overrideSection[1]),
        lineNumber,
      });
      continue;
    }

    const lawSection = lineText.match(LAW_SECTION_RE);
    if (!lawSection) {
      continue;
    }

    items.set(lawSection[1], {
      keyRange: createFirstMatchRange(lineText, lineNumber, lawSection[1]),
      lineNumber,
    });
  }

  return items;
}

function getWorkflowSectionBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const readableBlock = lineText.match(DOCUMENT_BLOCK_RE);
    if (readableBlock) {
      items.set(readableBlock[2], {
        bodySpec: getReadableChildBodySpec(
          document,
          readableBlock[1],
          lineText,
          lineNumber,
          bodySpec.endLine,
        ),
        keyRange: createFirstMatchRange(lineText, lineNumber, readableBlock[2]),
        lineNumber,
      });
      continue;
    }

    const localSection = lineText.match(
      new RegExp(`^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*${STRING_PATTERN}\\s*$`),
    );
    if (!localSection) {
      continue;
    }

    items.set(localSection[1], {
      bodySpec: {
        type: "workflow_section_body",
        endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
        indent: leadingSpaces(lineText),
        lineNumber,
      },
      keyRange: createFirstMatchRange(lineText, lineNumber, localSection[1]),
      lineNumber,
    });
  }

  return items;
}

function getReviewBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const inheritItem = lineText.match(INHERIT_RE);
    if (inheritItem) {
      items.set(inheritItem[1], {
        keyRange: createFirstMatchRange(lineText, lineNumber, inheritItem[1]),
        lineNumber,
      });
      continue;
    }

    if (REVIEW_FIELDS_FIELD_RE.test(lineText) || REVIEW_OVERRIDE_FIELDS_RE.test(lineText)) {
      const childBody = getReviewChildBodySpec(lineText, lineNumber);
      items.set("fields", {
        bodySpec: childBody
          ? {
              ...childBody,
              endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
            }
          : undefined,
        keyRange: createFirstMatchRange(lineText, lineNumber, "fields"),
        lineNumber,
      });
      continue;
    }

    const outcomeHeader = lineText.match(REVIEW_OUTCOME_HEADER_RE);
    if (outcomeHeader) {
      const childBody = getReviewChildBodySpec(lineText, lineNumber);
      items.set(outcomeHeader[1], {
        bodySpec: childBody
          ? {
              ...childBody,
              endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
            }
          : undefined,
        keyRange: createFirstMatchRange(lineText, lineNumber, outcomeHeader[1]),
        lineNumber,
      });
      continue;
    }

    const overrideOutcome = lineText.match(REVIEW_OVERRIDE_OUTCOME_RE);
    if (overrideOutcome) {
      const childBody = getReviewChildBodySpec(lineText, lineNumber);
      items.set(overrideOutcome[1], {
        bodySpec: childBody
          ? {
              ...childBody,
              endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
            }
          : undefined,
        keyRange: createFirstMatchRange(lineText, lineNumber, overrideOutcome[1]),
        lineNumber,
      });
      continue;
    }

    const overrideSection = lineText.match(REVIEW_OVERRIDE_SECTION_RE);
    if (overrideSection && !REVIEW_OVERRIDE_OUTCOME_RE.test(lineText)) {
      const childBody = getReviewChildBodySpec(lineText, lineNumber);
      items.set(overrideSection[1], {
        bodySpec: childBody
          ? {
              ...childBody,
              endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
            }
          : undefined,
        keyRange: createFirstMatchRange(lineText, lineNumber, overrideSection[1]),
        lineNumber,
      });
      continue;
    }

    const localSection = lineText.match(REVIEW_SECTION_RE);
    if (localSection) {
      const childBody = getReviewChildBodySpec(lineText, lineNumber);
      items.set(localSection[1], {
        bodySpec: childBody
          ? {
              ...childBody,
              endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
            }
          : undefined,
        keyRange: createFirstMatchRange(lineText, lineNumber, localSection[1]),
        lineNumber,
      });
    }
  }

  return items;
}

function getSkillsBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const inheritItem = lineText.match(INHERIT_RE);
    if (inheritItem) {
      items.set(inheritItem[1], {
        keyRange: createFirstMatchRange(lineText, lineNumber, inheritItem[1]),
        lineNumber,
      });
      continue;
    }

    const skillEntry = lineText.match(SKILL_ENTRY_RE);
    if (skillEntry) {
      const childBody = getSkillsChildBodySpec(lineText, lineNumber, false);
      items.set(skillEntry[1], {
        declarationKind: DECLARATION_KIND.SKILL,
        bodySpec: childBody
          ? {
              ...childBody,
              endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
            }
          : undefined,
        keyRange: createFirstMatchRange(lineText, lineNumber, skillEntry[1]),
        lineNumber,
        titleDeclarationKind: DECLARATION_KIND.SKILL,
        titleRef: parseNameRef(skillEntry[2]),
        valueRef: parseNameRef(skillEntry[2]),
      });
      continue;
    }

    const overrideRef = lineText.match(OVERRIDE_REF_RE);
    if (overrideRef) {
      const childBody = getSkillsChildBodySpec(lineText, lineNumber, true);
      items.set(overrideRef[1], {
        declarationKind: DECLARATION_KIND.SKILL,
        bodySpec: childBody
          ? {
              ...childBody,
              endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
            }
          : undefined,
        keyRange: createFirstMatchRange(lineText, lineNumber, overrideRef[1]),
        lineNumber,
        titleDeclarationKind: DECLARATION_KIND.SKILL,
        titleRef: parseNameRef(overrideRef[2]),
        valueRef: parseNameRef(overrideRef[2]),
      });
      continue;
    }

    if (
      OVERRIDE_BODY_RE.test(lineText) &&
      !OVERRIDE_REF_RE.test(lineText)
    ) {
      const key = lineText.trim().split(/\s+/)[1].replace(":", "");
      const childBody = getSkillsChildBodySpec(lineText, lineNumber, true);
      items.set(key, {
        bodySpec: childBody
          ? {
              ...childBody,
              endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
            }
          : undefined,
        keyRange: createFirstMatchRange(lineText, lineNumber, key),
        lineNumber,
      });
      continue;
    }

    const skillsSection = lineText.match(
      new RegExp(`^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*${STRING_PATTERN}\\s*$`),
    );
    if (skillsSection) {
      const childBody = getSkillsChildBodySpec(lineText, lineNumber, false);
      items.set(skillsSection[1], {
        bodySpec: childBody
          ? {
              ...childBody,
              endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
            }
          : undefined,
        keyRange: createFirstMatchRange(lineText, lineNumber, skillsSection[1]),
        lineNumber,
      });
    }
  }

  return items;
}

function getSkillsSectionBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const skillEntry = lineText.match(SKILL_ENTRY_RE);
    if (!skillEntry) {
      continue;
    }

    const childBody = getSkillsChildBodySpec(lineText, lineNumber, false);
    items.set(skillEntry[1], {
      declarationKind: DECLARATION_KIND.SKILL,
      bodySpec: childBody
        ? {
            ...childBody,
            endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
          }
        : undefined,
      keyRange: createFirstMatchRange(lineText, lineNumber, skillEntry[1]),
      lineNumber,
      titleDeclarationKind: DECLARATION_KIND.SKILL,
      titleRef: parseNameRef(skillEntry[2]),
      valueRef: parseNameRef(skillEntry[2]),
    });
  }

  return items;
}

function getIoBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const inheritItem = lineText.match(INHERIT_RE);
    if (inheritItem) {
      items.set(inheritItem[1], {
        keyRange: createFirstMatchRange(lineText, lineNumber, inheritItem[1]),
        lineNumber,
      });
      continue;
    }

    if (
      OVERRIDE_BODY_RE.test(lineText)
    ) {
      const overrideKey = lineText.trim().split(/\s+/)[1].replace(":", "");
      items.set(overrideKey, {
        keyRange: createFirstMatchRange(lineText, lineNumber, overrideKey),
        lineNumber,
      });
      continue;
    }

    const ioSection = lineText.match(
      new RegExp(`^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*${STRING_PATTERN}\\s*$`),
    );
    if (ioSection) {
      items.set(ioSection[1], {
        keyRange: createFirstMatchRange(lineText, lineNumber, ioSection[1]),
        lineNumber,
      });
    }
  }

  return items;
}

function getRecordBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const inheritItem = lineText.match(INHERIT_RE);
    if (inheritItem) {
      items.set(inheritItem[1], {
        inherited: true,
        keyRange: createFirstMatchRange(lineText, lineNumber, inheritItem[1]),
        lineNumber,
      });
      continue;
    }

    const overrideRef = lineText.match(OVERRIDE_REF_RE);
    if (overrideRef) {
      const targetKind = keyedRecordFieldToDeclarationKind(overrideRef[1], {
        declarationKind: bodySpec.declarationKind,
        fieldKind: bodySpec.fieldKind,
      });
      items.set(overrideRef[1], {
        keyRange: createFirstMatchRange(lineText, lineNumber, overrideRef[1]),
        lineNumber,
        titleDeclarationKind: targetKind,
        titleRef: targetKind ? parseNameRef(overrideRef[2]) : undefined,
        valueRef: targetKind ? parseNameRef(overrideRef[2]) : undefined,
      });
      continue;
    }

    const overrideBody = lineText.match(OVERRIDE_BODY_RE);
    if (overrideBody && !OVERRIDE_REF_RE.test(lineText)) {
      const childBody = getRecordChildBodySpec(
        lineText,
        lineNumber,
        bodySpec.fieldKind,
        bodySpec.declarationKind,
      );
      items.set(overrideBody[1], {
        bodySpec: childBody
          ? {
              ...childBody,
              endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
            }
          : undefined,
        keyRange: createFirstMatchRange(lineText, lineNumber, overrideBody[1]),
        lineNumber,
      });
      continue;
    }

    const readableBlock = lineText.match(DOCUMENT_BLOCK_RE);
    if (readableBlock) {
      items.set(readableBlock[2], {
        bodySpec: getReadableChildBodySpec(
          document,
          readableBlock[1],
          lineText,
          lineNumber,
          bodySpec.endLine,
        ),
        keyRange: createFirstMatchRange(lineText, lineNumber, readableBlock[2]),
        lineNumber,
      });
      continue;
    }

    const keyedItem = lineText.match(
      new RegExp(`^\\s*(${IDENTIFIER_PATTERN})\\s*:`),
    );
    if (!keyedItem) {
      continue;
    }
    const keyedValueRef = lineText.match(
      new RegExp(`^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*(${DOTTED_NAME_PATTERN})\\s*$`),
    );
    const titleDeclarationKind = keyedFieldToDeclarationKind(keyedItem[1]);

    items.set(keyedItem[1], {
      bodySpec:
        findNextSignificantLine(document, lineNumber + 1, bodySpec.endLine)?.indent >
        leadingSpaces(lineText)
          ? {
              type: "record_body",
              declarationKind: bodySpec.declarationKind,
              fieldKind: bodySpec.fieldKind,
              endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
              indent: leadingSpaces(lineText),
              lineNumber,
            }
          : undefined,
      keyRange: createFirstMatchRange(lineText, lineNumber, keyedItem[1]),
      lineNumber,
      titleDeclarationKind,
      titleRef:
        titleDeclarationKind && keyedValueRef
          ? parseNameRef(keyedValueRef[2])
          : undefined,
    });
  }

  return items;
}

function getAnalysisBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const inheritItem = lineText.match(INHERIT_RE);
    if (inheritItem) {
      items.set(inheritItem[1], {
        keyRange: createFirstMatchRange(lineText, lineNumber, inheritItem[1]),
        lineNumber,
      });
      continue;
    }

    const overrideSection = lineText.match(ANALYSIS_OVERRIDE_SECTION_RE);
    if (overrideSection) {
      items.set(overrideSection[1], {
        keyRange: createFirstMatchRange(lineText, lineNumber, overrideSection[1]),
        lineNumber,
      });
      continue;
    }

    const localSection = lineText.match(ANALYSIS_SECTION_RE);
    if (!localSection) {
      continue;
    }

    items.set(localSection[1], {
      keyRange: createFirstMatchRange(lineText, lineNumber, localSection[1]),
      lineNumber,
    });
  }

  return items;
}

function getSchemaBlockItems(document, lineNumber, endLine) {
  const items = [];
  const baseIndent = findBodyBaseIndent(document, {
    endLine,
    lineNumber,
  });
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let childLineNumber = lineNumber + 1;
    childLineNumber <= endLine;
    childLineNumber += 1
  ) {
    const lineText = document.lineAt(childLineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const schemaItem = lineText.match(SCHEMA_ITEM_RE);
    if (!schemaItem) {
      continue;
    }

    items.push({
      key: schemaItem[1],
      keyRange: createFirstMatchRange(lineText, childLineNumber, schemaItem[1]),
      lineNumber: childLineNumber,
      titleRange: createLastMatchRange(lineText, childLineNumber, schemaItem[2]),
    });
  }

  return items;
}

function getSchemaBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const inheritBlock = lineText.match(SCHEMA_INHERIT_BLOCK_RE);
    if (inheritBlock) {
      items.set(inheritBlock[1], {
        keyRange: createFirstMatchRange(lineText, lineNumber, inheritBlock[1]),
        lineNumber,
      });
      continue;
    }

    const overrideBlock = lineText.match(SCHEMA_OVERRIDE_BLOCK_RE);
    const blockField = lineText.match(SCHEMA_BLOCK_FIELD_RE);
    const blockMatch = overrideBlock || blockField;
    if (blockMatch) {
      const blockKey = blockMatch[1];
      const blockEndLine = findBodyEndLine(document, lineNumber, bodySpec.endLine);
      items.set(blockKey, {
        keyRange: createFirstMatchRange(lineText, lineNumber, blockKey),
        lineNumber,
        bodySpec: {
          type: "schema_block_body",
          blockKey,
          indent: leadingSpaces(lineText),
          lineNumber,
          endLine: blockEndLine,
        },
      });
      for (const item of getSchemaBlockItems(document, lineNumber, blockEndLine)) {
        items.set(item.key, {
          keyRange: item.keyRange,
          lineNumber: item.lineNumber,
          titleRange: item.titleRange,
          nestedOnly: true,
        });
      }
      continue;
    }

    const schemaItem = lineText.match(SCHEMA_ITEM_RE);
    if (!schemaItem) {
      continue;
    }

    items.set(schemaItem[1], {
      keyRange: createFirstMatchRange(lineText, lineNumber, schemaItem[1]),
      lineNumber,
    });
  }

  return items;
}

function getDocumentBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const inheritItem = lineText.match(INHERIT_RE);
    if (inheritItem) {
      items.set(inheritItem[1], {
        inherited: true,
        keyRange: createFirstMatchRange(lineText, lineNumber, inheritItem[1]),
        lineNumber,
      });
      continue;
    }

    const overrideBlock = lineText.match(DOCUMENT_OVERRIDE_BLOCK_RE);
    if (overrideBlock) {
      items.set(overrideBlock[2], {
        bodySpec: getReadableChildBodySpec(
          document,
          overrideBlock[1],
          lineText,
          lineNumber,
          bodySpec.endLine,
        ),
        keyRange: createFirstMatchRange(lineText, lineNumber, overrideBlock[2]),
        lineNumber,
      });
      continue;
    }

    const localBlock = lineText.match(DOCUMENT_BLOCK_RE);
    if (localBlock) {
      items.set(localBlock[2], {
        bodySpec: getReadableChildBodySpec(
          document,
          localBlock[1],
          lineText,
          lineNumber,
          bodySpec.endLine,
        ),
        keyRange: createFirstMatchRange(lineText, lineNumber, localBlock[2]),
        lineNumber,
      });
      continue;
    }

    const localSection = lineText.match(READABLE_KEYED_STRING_RE);
    if (!localSection) {
      continue;
    }

    items.set(localSection[1], {
      bodySpec: {
        type: "readable_section_body",
        endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
        indent: leadingSpaces(lineText),
        lineNumber,
      },
      keyRange: createFirstMatchRange(lineText, lineNumber, localSection[1]),
      lineNumber,
    });
  }

  return items;
}

function getReadableSectionBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const readableBlock = lineText.match(DOCUMENT_BLOCK_RE);
    if (!readableBlock) {
      continue;
    }

    items.set(readableBlock[2], {
      bodySpec: getReadableChildBodySpec(
        document,
        readableBlock[1],
        lineText,
        lineNumber,
        bodySpec.endLine,
      ),
      keyRange: createFirstMatchRange(lineText, lineNumber, readableBlock[2]),
      lineNumber,
    });
  }

  return items;
}

function getReadableListBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const itemSchema = lineText.match(READABLE_ITEM_SCHEMA_RE);
    if (itemSchema) {
      items.set(itemSchema[1], {
        bodySpec: {
          type: "readable_inline_schema_body",
          endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
          indent: leadingSpaces(lineText),
          lineNumber,
        },
        keyRange: createFirstMatchRange(lineText, lineNumber, itemSchema[1]),
        lineNumber,
      });
      continue;
    }

    const keyedItem = lineText.match(READABLE_KEYED_STRING_RE);
    if (!keyedItem) {
      continue;
    }

    items.set(keyedItem[1], {
      keyRange: createFirstMatchRange(lineText, lineNumber, keyedItem[1]),
      lineNumber,
    });
  }

  return items;
}

function getReadableDefinitionsBodyItems(document, bodySpec) {
  return getReadableListBodyItems(document, bodySpec);
}

function getReadablePropertiesBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const propertyItem = lineText.match(SCHEMA_ITEM_RE);
    if (!propertyItem) {
      continue;
    }

    items.set(propertyItem[1], {
      keyRange: createFirstMatchRange(lineText, lineNumber, propertyItem[1]),
      lineNumber,
      titleRange: createLastMatchRange(lineText, lineNumber, propertyItem[2]),
    });
  }

  return items;
}

function getReadableInlineSchemaBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const schemaItem = lineText.match(SCHEMA_ITEM_RE);
    if (!schemaItem) {
      continue;
    }

    items.set(schemaItem[1], {
      keyRange: createFirstMatchRange(lineText, lineNumber, schemaItem[1]),
      lineNumber,
      titleRange: createLastMatchRange(lineText, lineNumber, schemaItem[2]),
    });
  }

  return items;
}

function getReadableFootnotesBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const footnoteItem = lineText.match(SCHEMA_ITEM_RE);
    if (!footnoteItem) {
      continue;
    }

    items.set(footnoteItem[1], {
      keyRange: createFirstMatchRange(lineText, lineNumber, footnoteItem[1]),
      lineNumber,
      titleRange: createLastMatchRange(lineText, lineNumber, footnoteItem[2]),
    });
  }

  return items;
}

function getReadableTableBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const rowSchema = lineText.match(READABLE_ROW_SCHEMA_RE);
    if (rowSchema) {
      items.set(rowSchema[1], {
        bodySpec: {
          type: "readable_inline_schema_body",
          endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
          indent: leadingSpaces(lineText),
          lineNumber,
        },
        keyRange: createFirstMatchRange(lineText, lineNumber, rowSchema[1]),
        lineNumber,
      });
      continue;
    }

    const container = lineText.match(READABLE_TABLE_CONTAINER_RE);
    if (!container) {
      continue;
    }

    items.set(container[1], {
      bodySpec: {
        type: container[1] === "columns" ? "readable_table_columns_body" : "readable_table_rows_body",
        endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
        indent: leadingSpaces(lineText),
        lineNumber,
      },
      keyRange: createFirstMatchRange(lineText, lineNumber, container[1]),
      lineNumber,
    });
  }

  return items;
}

function getReadableTableColumnsBodyItems(document, bodySpec) {
  return getReadableDefinitionsBodyItems(document, bodySpec);
}

function getReadableTableRowsBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const row = lineText.match(READABLE_TABLE_ROW_RE);
    if (!row) {
      continue;
    }

    items.set(row[1], {
      bodySpec: {
        type: "readable_table_row_body",
        endLine: findBodyEndLine(document, lineNumber, bodySpec.endLine),
        indent: leadingSpaces(lineText),
        lineNumber,
      },
      keyRange: createFirstMatchRange(lineText, lineNumber, row[1]),
      lineNumber,
    });
  }

  return items;
}

function getReadableTableRowBodyItems(document, bodySpec) {
  return getReadableDefinitionsBodyItems(document, bodySpec);
}

function getEnumBodyItems(document, bodySpec) {
  const items = new Map();
  const baseIndent = findBodyBaseIndent(document, bodySpec);
  if (baseIndent === undefined) {
    return items;
  }

  for (
    let lineNumber = bodySpec.lineNumber + 1;
    lineNumber <= bodySpec.endLine;
    lineNumber += 1
  ) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText) || leadingSpaces(lineText) !== baseIndent) {
      continue;
    }

    const enumMember = lineText.match(ENUM_MEMBER_RE);
    if (!enumMember) {
      continue;
    }

    const memberEndLine = findBodyEndLine(document, lineNumber, bodySpec.endLine);
    const item = {
      bodySpec: undefined,
      keyRange: createFirstMatchRange(lineText, lineNumber, enumMember[1]),
      lineNumber,
      titleRange: createLastMatchRange(lineText, lineNumber, enumMember[2]),
      wireLineNumber: lineNumber,
      wireRange: createLastMatchRange(lineText, lineNumber, enumMember[2]),
    };

    const nextContent = findNextSignificantLine(document, lineNumber + 1, memberEndLine);
    if (nextContent && nextContent.indent > leadingSpaces(lineText)) {
      item.bodySpec = {
        type: "enum_member_body",
        endLine: memberEndLine,
        indent: leadingSpaces(lineText),
        keyRange: item.keyRange,
        lineNumber,
        titleRange: item.titleRange,
        wireLineNumber: item.wireLineNumber,
        wireRange: item.wireRange,
      };

      for (
        let bodyLineNumber = lineNumber + 1;
        bodyLineNumber <= memberEndLine;
        bodyLineNumber += 1
      ) {
        const bodyLineText = document.lineAt(bodyLineNumber).text;
        if (isIgnorableLine(bodyLineText) || leadingSpaces(bodyLineText) !== nextContent.indent) {
          continue;
        }
        const wireMatch = bodyLineText.match(ENUM_MEMBER_WIRE_RE);
        if (!wireMatch) {
          continue;
        }
        item.wireLineNumber = bodyLineNumber;
        item.wireRange = createLastMatchRange(bodyLineText, bodyLineNumber, wireMatch[1]);
        item.bodySpec.wireLineNumber = item.wireLineNumber;
        item.bodySpec.wireRange = item.wireRange;
        break;
      }
    }

    items.set(enumMember[1], item);
  }

  return items;
}

function getEnumMemberBodyItems(_document, bodySpec) {
  return new Map([
    [
      "key",
      {
        keyRange: bodySpec.keyRange,
        lineNumber: bodySpec.lineNumber,
      },
    ],
    [
      "wire",
      {
        keyRange: bodySpec.wireRange,
        lineNumber: bodySpec.wireLineNumber,
      },
    ],
  ]);
}

function getAddressableBodyItems(document, bodySpec) {
  switch (bodySpec.type) {
    case "review_body":
      return getReviewBodyItems(document, bodySpec);
    case "analysis_body":
      return getAnalysisBodyItems(document, bodySpec);
    case "schema_body":
      return getSchemaBodyItems(document, bodySpec);
    case "schema_block_body":
      return new Map(
        getSchemaBlockItems(document, bodySpec.lineNumber, bodySpec.endLine).map((item) => [
          item.key,
          item,
        ]),
      );
    case "document_body":
      return getDocumentBodyItems(document, bodySpec);
    case "readable_section_body":
      return getReadableSectionBodyItems(document, bodySpec);
    case "readable_list_body":
      return getReadableListBodyItems(document, bodySpec);
    case "readable_definitions_body":
      return getReadableDefinitionsBodyItems(document, bodySpec);
    case "readable_properties_body":
      return getReadablePropertiesBodyItems(document, bodySpec);
    case "readable_inline_schema_body":
      return getReadableInlineSchemaBodyItems(document, bodySpec);
    case "readable_footnotes_body":
      return getReadableFootnotesBodyItems(document, bodySpec);
    case "readable_table_body":
      return getReadableTableBodyItems(document, bodySpec);
    case "readable_table_columns_body":
      return getReadableTableColumnsBodyItems(document, bodySpec);
    case "readable_table_rows_body":
      return getReadableTableRowsBodyItems(document, bodySpec);
    case "readable_table_row_body":
      return getReadableTableRowBodyItems(document, bodySpec);
    case "workflow_body":
      return getWorkflowBodyItems(document, bodySpec);
    case "workflow_section_body":
      return getWorkflowSectionBodyItems(document, bodySpec);
    case "skills_body":
      return getSkillsBodyItems(document, bodySpec);
    case "skills_section_body":
      return getSkillsSectionBodyItems(document, bodySpec);
    case "record_body":
      return getRecordBodyItems(document, bodySpec);
    case "enum_body":
      return getEnumBodyItems(document, bodySpec);
    case "enum_member_body":
      return getEnumMemberBodyItems(document, bodySpec);
    default:
      return new Map();
  }
}

async function findAddressablePathTarget({ declaration, pathSegments, source }) {
  if (declaration.kind === DECLARATION_KIND.AGENT) {
    return findAgentPathTarget(declaration, pathSegments, source);
  }

  let currentSource = source;
  let currentBody = getDeclarationBodySpec(declaration);
  if (!currentBody) {
    return undefined;
  }
  let currentTarget = {
    bodySpec: currentBody,
    keyRange: declaration.nameRange,
    lineNumber: declaration.lineNumber,
  };

  for (let index = 0; index < pathSegments.length; index += 1) {
    const segment = pathSegments[index];
    const isLast = index === pathSegments.length - 1;
    if (segment === "title") {
      if (!isLast) {
        return undefined;
      }
      return resolveAddressableTitleTarget({
        source: currentSource,
        target: currentTarget,
      });
    }

    const items = getAddressableBodyItems(currentSource.document, currentBody);
    const target = items.get(segment);
    if (!target || (currentBody.type === "schema_body" && target.nestedOnly)) {
      return undefined;
    }
    currentTarget = target;

    if (isLast) {
      return {
        document: currentSource.document,
        lineNumber: target.lineNumber,
        selectionRange: target.keyRange,
      };
    }

    if (!target.bodySpec) {
      if (
        target.inherited
        && currentBody.type === "document_body"
        && declaration.kind === DECLARATION_KIND.DOCUMENT
        && declaration.parentRef
      ) {
        const parentSource = await openReferencedDocument(declaration.parentRef, currentSource);
        if (!parentSource) {
          return undefined;
        }

        const parentDeclaration = findDeclarationByKind(
          parentSource.index,
          DECLARATION_KIND.DOCUMENT,
          declaration.parentRef.declarationName,
          { requireConcrete: false },
        );
        if (!parentDeclaration) {
          return undefined;
        }

        const parentBody = getDeclarationBodySpec(parentDeclaration);
        if (!parentBody) {
          return undefined;
        }

        const parentTarget = getDocumentBodyItems(parentSource.document, parentBody).get(segment);
        if (!parentTarget || !parentTarget.bodySpec) {
          return undefined;
        }

        currentSource = parentSource;
        currentBody = parentTarget.bodySpec;
        currentTarget = parentTarget;
        continue;
      }

      if (!target.valueRef || !target.declarationKind) {
        return undefined;
      }

      const nextSource = await openReferencedDocument(target.valueRef, currentSource);
      if (!nextSource) {
        return undefined;
      }

      const nextDeclaration = findDeclarationByKind(
        nextSource.index,
        target.declarationKind,
        target.valueRef.declarationName,
        { requireConcrete: false },
      );
      if (!nextDeclaration) {
        return undefined;
      }

      currentSource = nextSource;
      currentBody = getDeclarationBodySpec(nextDeclaration);
      if (!currentBody) {
        return undefined;
      }
      continue;
    }
    currentBody = target.bodySpec;
  }

  return undefined;
}

async function resolveAddressableTitleTarget({ source, target }) {
  if (target.titleRef && target.titleDeclarationKind) {
    const nextSource = await openReferencedDocument(target.titleRef, source);
    if (!nextSource) {
      return undefined;
    }

    const nextDeclaration = findDeclarationByKind(
      nextSource.index,
      target.titleDeclarationKind,
      target.titleRef.declarationName,
      { requireConcrete: false },
    );
    if (!nextDeclaration) {
      return undefined;
    }

    return {
      document: nextSource.document,
      lineNumber: nextDeclaration.lineNumber,
      selectionRange: nextDeclaration.nameRange,
    };
  }

  if (target.titleRange) {
    return {
      document: source.document,
      lineNumber: target.lineNumber,
      selectionRange: target.titleRange,
    };
  }

  return {
    document: source.document,
    lineNumber: target.lineNumber,
    selectionRange: target.keyRange,
  };
}

function findAgentPathTarget(declaration, pathSegments, source) {
  if (pathSegments.length !== 1) {
    return undefined;
  }

  const segment = pathSegments[0];
  if (segment === "name" || segment === "key") {
    return {
      document: source.document,
      lineNumber: declaration.lineNumber,
      selectionRange: declaration.nameRange,
    };
  }
  if (segment !== "title") {
    return undefined;
  }

  const lineText = source.document.lineAt(declaration.lineNumber).text;
  const match = lineText.match(
    new RegExp(
      `^\\s*agent\\s+${IDENTIFIER_PATTERN}(?:\\s*\\[${DOTTED_NAME_PATTERN}\\])?\\s*:\\s*(${STRING_PATTERN})\\s*$`,
    ),
  );
  if (!match) {
    return undefined;
  }

  return {
    document: source.document,
    lineNumber: declaration.lineNumber,
    selectionRange: createLastMatchRange(lineText, declaration.lineNumber, match[1]),
  };
}

function findDeclarationForLine(index, lineNumber) {
  return index.declarations.find(
    (declaration) =>
      declaration.lineNumber <= lineNumber && lineNumber <= declaration.endLine,
  );
}

function findBodyBaseIndent(document, bodySpec) {
  const startLine =
    bodySpec.declarationLine !== undefined
      ? bodySpec.declarationLine + 1
      : bodySpec.lineNumber + 1;
  const nextContent = findNextSignificantLine(document, startLine, bodySpec.endLine);
  return nextContent ? nextContent.indent : undefined;
}

function findBodyEndLine(document, lineNumber, maxEndLine) {
  const headerIndent = leadingSpaces(document.lineAt(lineNumber).text);
  let previousSignificantLine = lineNumber;

  for (
    let currentLine = lineNumber + 1;
    currentLine <= maxEndLine;
    currentLine += 1
  ) {
    const lineText = document.lineAt(currentLine).text;
    if (isIgnorableLine(lineText)) {
      continue;
    }

    if (leadingSpaces(lineText) <= headerIndent) {
      return previousSignificantLine;
    }

    previousSignificantLine = currentLine;
  }

  return maxEndLine;
}

function collectImportEntries(document, context) {
  const entries = [];

  for (let lineNumber = 0; lineNumber < document.lineCount; lineNumber += 1) {
    const lineText = document.lineAt(lineNumber).text;
    const match = lineText.match(IMPORT_LINE_RE);
    if (!match) {
      continue;
    }

    const parsed = parseImportPath(match[1]);
    if (!parsed) {
      continue;
    }

    const resolvedModuleParts = resolveImportModuleParts(
      parsed,
      context.currentModuleParts,
    );
    if (!resolvedModuleParts) {
      continue;
    }

    const targetUri = parsed.level === 0
      ? resolveAbsoluteImportTargetUri(context.importRootUris, resolvedModuleParts)
      : modulePartsToPromptUri(context.promptRootUri, resolvedModuleParts);
    if (!targetUri) {
      continue;
    }

    entries.push({
      moduleParts: resolvedModuleParts,
      range: createLastMatchRange(lineText, lineNumber, match[1]),
      targetUri,
    });
  }

  return entries;
}

function getDocumentContext(document) {
  const promptRootUri = resolvePromptRoot(document.uri);
  if (!promptRootUri) {
    return undefined;
  }

  const currentModuleParts = uriToModuleParts(document.uri, promptRootUri);
  if (!currentModuleParts) {
    return undefined;
  }

  return {
    currentModuleParts,
    importRootUris: resolveImportRootUris(document.uri, promptRootUri),
    promptRootUri,
  };
}

function resolveRefTargetUri(ref, documentUri, context, importEntries) {
  if (
    ref.moduleParts.length === 0 ||
    arraysEqual(ref.moduleParts, context.currentModuleParts)
  ) {
    return documentUri;
  }

  const dottedTargetModule = ref.moduleParts.join(".");
  const importedModule = importEntries.find(
    (entry) => entry.moduleParts.join(".") === dottedTargetModule,
  );
  return importedModule ? importedModule.targetUri : undefined;
}

function resolvePromptRoot(documentUri) {
  let currentUri = documentUri.with({
    path: path.posix.dirname(documentUri.path),
  });

  while (true) {
    if (path.posix.basename(currentUri.path) === "prompts") {
      return currentUri;
    }

    const parentPath = path.posix.dirname(currentUri.path);
    if (parentPath === currentUri.path) {
      return undefined;
    }

    currentUri = currentUri.with({ path: parentPath });
  }
}

function resolveImportRootUris(documentUri, promptRootUri) {
  const roots = [promptRootUri];
  const config = loadCompileProjectConfig(documentUri);
  for (const additionalRootUri of config.additionalPromptRootUris) {
    if (!roots.some((rootUri) => rootUri.toString() === additionalRootUri.toString())) {
      roots.push(additionalRootUri);
    }
  }
  return roots;
}

function uriToModuleParts(documentUri, promptRootUri) {
  const relativePath = path.posix.relative(promptRootUri.path, documentUri.path);
  if (
    relativePath.startsWith("../") ||
    relativePath === ".." ||
    !relativePath.endsWith(".prompt")
  ) {
    return undefined;
  }

  const withoutExtension = relativePath.slice(0, -".prompt".length);
  return withoutExtension.split("/").filter(Boolean);
}

function modulePartsToPromptUri(promptRootUri, moduleParts) {
  const fileName = `${moduleParts[moduleParts.length - 1]}.prompt`;
  return vscode.Uri.joinPath(promptRootUri, ...moduleParts.slice(0, -1), fileName);
}

function resolveAbsoluteImportTargetUri(importRootUris, moduleParts) {
  const candidates = importRootUris
    .map((promptRootUri) => modulePartsToPromptUri(promptRootUri, moduleParts))
    .filter((targetUri) => uriExistsSync(targetUri));
  if (candidates.length !== 1) {
    return undefined;
  }
  return candidates[0];
}

function parseImportPath(rawPath) {
  const match = rawPath.match(
    new RegExp(`^(\\.+)?(${DOTTED_NAME_PATTERN})$`),
  );
  if (!match) {
    return undefined;
  }

  return {
    level: match[1] ? match[1].length : 0,
    moduleParts: match[2].split("."),
  };
}

function resolveImportModuleParts(importPath, currentModuleParts) {
  if (importPath.level === 0) {
    return importPath.moduleParts;
  }

  const currentPackageParts = currentModuleParts.slice(0, -1);
  const parentWalk = importPath.level - 1;
  if (parentWalk > currentPackageParts.length) {
    return undefined;
  }

  const basePackageParts = parentWalk
    ? currentPackageParts.slice(0, currentPackageParts.length - parentWalk)
    : currentPackageParts;
  return [...basePackageParts, ...importPath.moduleParts];
}

function parseNameRef(rawRef) {
  if (!NAME_REF_RE.test(rawRef)) {
    return undefined;
  }

  const parts = rawRef.split(".");
  return {
    declarationName: parts[parts.length - 1],
    moduleParts: parts.slice(0, -1),
  };
}

function maskQuotedText(lineText) {
  return lineText.replace(/"(?:\\.|[^"\\])*"/g, (match) => " ".repeat(match.length));
}

function splitShippedLawToken(rawToken) {
  const segments = rawToken.split(".");
  const declarationIndex = segments.findIndex((segment) => /^[A-Z]/.test(segment));
  if (declarationIndex === -1) {
    return undefined;
  }

  const rootText = segments.slice(0, declarationIndex + 1).join(".");
  const pathSegments = segments.slice(declarationIndex + 1);
  return {
    pathText: pathSegments.length ? pathSegments.join(".") : undefined,
    rootText,
  };
}

function collectShippedLawRefSites(lineText, lineNumber) {
  // The compiler owns law semantics. The editor mirrors only the shipped
  // clickable declaration/path surface by scanning non-string law tokens that
  // still look like declaration roots.
  const maskedLine = maskQuotedText(lineText);
  const sites = [];

  for (const match of maskedLine.matchAll(UPPERCASE_DOTTED_TOKEN_RE)) {
    const rawToken = match[0];
    const tokenStart = match.index ?? -1;
    if (tokenStart < 0) {
      continue;
    }

    const split = splitShippedLawToken(rawToken);
    if (!split) {
      continue;
    }

    if (split.pathText) {
      sites.push(
        ...createAddressableRefSites({
          lineNumber,
          pathText: split.pathText,
          pathStartCharacter: tokenStart + split.rootText.length + 1,
          rootText: split.rootText,
          startCharacter: tokenStart,
        }),
      );
      continue;
    }

    const ref = parseNameRef(split.rootText);
    if (!ref) {
      continue;
    }

    sites.push({
      type: "readableDeclRef",
      range: createRangeFromStart(lineNumber, tokenStart, split.rootText.length),
      ref,
    });
  }

  return sites;
}

function createBoundLawPathSites({ lineNumber, pathText, startCharacter }) {
  const pathSegments = pathText.split(".");
  const sites = [];
  let cursor = startCharacter;
  for (let index = 0; index < pathSegments.length; index += 1) {
    const segment = pathSegments[index];
    sites.push({
      type: "boundLawPathRef",
      pathSegments,
      range: createRangeFromStart(lineNumber, cursor, segment.length),
      segmentIndex: index,
      lineContext: undefined,
    });
    cursor += segment.length + 1;
  }
  return sites;
}

function collectBoundLawPathSites(lineText, lineNumber) {
  const maskedLine = maskQuotedText(lineText);
  const sites = [];

  for (const match of maskedLine.matchAll(DOTTED_TOKEN_RE)) {
    const rawToken = match[0];
    const tokenStart = match.index ?? -1;
    if (tokenStart < 0) {
      continue;
    }

    const rootSegment = rawToken.split(".")[0];
    if (/^[A-Z]/.test(rootSegment) || NON_BINDING_LAW_TOKENS.has(rootSegment)) {
      continue;
    }

    sites.push(
      ...createBoundLawPathSites({
        lineNumber,
        pathText: rawToken,
        startCharacter: tokenStart,
      }),
    );
  }

  return sites;
}

function createAddressableRefSites({
  lineNumber,
  pathText,
  pathStartCharacter,
  rootText,
  startCharacter,
}) {
  const ref = parseNameRef(rootText);
  if (!ref) {
    return [];
  }

  const pathSegments = pathText.split(".");
  const sites = [
    {
      type: "addressableRef",
      pathSegments,
      range: createRangeFromStart(lineNumber, startCharacter, rootText.length),
      ref,
      segmentIndex: -1,
    },
  ];

  let cursor =
    pathStartCharacter !== undefined
      ? pathStartCharacter
      : startCharacter + rootText.length + 1;
  for (let index = 0; index < pathSegments.length; index += 1) {
    const segment = pathSegments[index];
    sites.push({
      type: "addressableRef",
      pathSegments,
      range: createRangeFromStart(lineNumber, cursor, segment.length),
      ref,
      segmentIndex: index,
    });
    cursor += segment.length + 1;
  }

  return sites;
}

function collectReviewSemanticSites(lineText, lineNumber) {
  const sites = [];
  const maskedLine = maskQuotedText(lineText);

  for (const match of maskedLine.matchAll(REVIEW_SEMANTIC_REF_RE)) {
    const rootText = match[1];
    const memberName = match[2];
    const rootStart = match.index ?? -1;
    if (rootStart < 0) {
      continue;
    }

    sites.push({
      type: "reviewSemanticRef",
      lineContext: undefined,
      memberName,
      range: createRangeFromStart(lineNumber, rootStart, rootText.length),
      segmentIndex: -1,
      semanticRoot: rootText,
    });
    sites.push({
      type: "reviewSemanticRef",
      lineContext: undefined,
      memberName,
      range: createRangeFromStart(
        lineNumber,
        rootStart + rootText.length + 1,
        memberName.length,
      ),
      segmentIndex: 0,
      semanticRoot: rootText,
    });
  }

  return sites;
}

function createReviewBoundOutputPathSites({ lineNumber, pathText, startCharacter }) {
  const pathSegments = pathText.split(".");
  const sites = [];
  let cursor = startCharacter;
  for (let index = 0; index < pathSegments.length; index += 1) {
    const segment = pathSegments[index];
    sites.push({
      type: "reviewBoundOutputPathRef",
      lineContext: undefined,
      pathSegments,
      range: createRangeFromStart(lineNumber, cursor, segment.length),
      segmentIndex: index,
    });
    cursor += segment.length + 1;
  }
  return sites;
}

function createStructuralSite(lineText, lineNumber, key) {
  return {
    type: "structuralKeyRef",
    key,
    lineContext: undefined,
    range: createFirstMatchRange(lineText, lineNumber, key),
  };
}

function createNameRange(lineText, lineNumber, name) {
  return createFirstMatchRange(lineText, lineNumber, name);
}

function createFirstMatchRange(lineText, lineNumber, rawValue) {
  return createRangeFromStart(lineNumber, lineText.indexOf(rawValue), rawValue.length);
}

function createLastMatchRange(lineText, lineNumber, rawValue) {
  return createRangeFromStart(lineNumber, lineText.lastIndexOf(rawValue), rawValue.length);
}

function createRangeFromStart(lineNumber, startCharacter, length) {
  return new vscode.Range(
    lineNumber,
    startCharacter,
    lineNumber,
    startCharacter + length,
  );
}

function createFileLocationLink(originRange, targetDocument) {
  const firstLine = targetDocument.lineAt(0);
  return {
    originSelectionRange: originRange,
    targetUri: targetDocument.uri,
    targetRange: new vscode.Range(0, 0, 0, firstLine.text.length),
    targetSelectionRange: new vscode.Range(0, 0, 0, 0),
  };
}

function createDeclarationLocationLink(originRange, targetDocument, targetSelectionRange) {
  const targetLine = targetDocument.lineAt(targetSelectionRange.start.line);
  return {
    originSelectionRange: originRange,
    targetUri: targetDocument.uri,
    targetRange: new vscode.Range(
      targetSelectionRange.start.line,
      0,
      targetSelectionRange.start.line,
      targetLine.text.length,
    ),
    targetSelectionRange,
  };
}

function leadingSpaces(lineText) {
  return lineText.length - lineText.trimStart().length;
}

function isIgnorableLine(lineText) {
  const trimmed = lineText.trim();
  return trimmed.length === 0 || trimmed.startsWith("#");
}

function findNextSignificantLine(document, startLine, endLine) {
  for (let lineNumber = startLine; lineNumber <= endLine; lineNumber += 1) {
    const lineText = document.lineAt(lineNumber).text;
    if (isIgnorableLine(lineText)) {
      continue;
    }

    return {
      indent: leadingSpaces(lineText),
      lineNumber,
      text: lineText,
    };
  }

  return undefined;
}

function allowsInterpolation(lineText) {
  return (
    PROSE_LINE_RE.test(lineText) ||
    ROLE_INLINE_RE.test(lineText) ||
    PURPOSE_OR_REASON_RE.test(lineText) ||
    ROUTE_RE.test(lineText)
  );
}

function inheritanceKindToDeclarationKind(kind) {
  switch (kind) {
    case "review":
      return DECLARATION_KIND.REVIEW;
    case "analysis":
      return DECLARATION_KIND.ANALYSIS;
    case "schema":
      return DECLARATION_KIND.SCHEMA_DECL;
    case "document":
      return DECLARATION_KIND.DOCUMENT;
    case "workflow":
      return DECLARATION_KIND.WORKFLOW;
    case "skills":
      return DECLARATION_KIND.SKILLS_BLOCK;
    case "inputs":
      return DECLARATION_KIND.INPUTS_BLOCK;
    case "outputs":
      return DECLARATION_KIND.OUTPUTS_BLOCK;
    case "output":
      return DECLARATION_KIND.OUTPUT;
    default:
      return undefined;
  }
}

function keyedFieldToDeclarationKind(fieldName) {
  switch (fieldName) {
    case "analysis":
      return DECLARATION_KIND.ANALYSIS;
    case "decision":
      return DECLARATION_KIND.DECISION;
    case "skills":
      return DECLARATION_KIND.SKILLS_BLOCK;
    case "inputs":
      return DECLARATION_KIND.INPUTS_BLOCK;
    case "outputs":
      return DECLARATION_KIND.OUTPUTS_BLOCK;
    case "final_output":
      return DECLARATION_KIND.OUTPUT;
    case "source":
      return DECLARATION_KIND.INPUT_SOURCE;
    case "target":
      return DECLARATION_KIND.OUTPUT_TARGET;
    case "shape":
      return DECLARATION_KIND.OUTPUT_SHAPE;
    case "schema":
      return DECLARATION_KIND.OUTPUT_SCHEMA;
    case "render_profile":
      return DECLARATION_KIND.RENDER_PROFILE;
    default:
      return undefined;
  }
}

function keyedRecordFieldToDeclarationKind(fieldName, context = {}) {
  const { declarationKind } = context;
  switch (fieldName) {
    case "source":
      return DECLARATION_KIND.INPUT_SOURCE;
    case "target":
      return DECLARATION_KIND.OUTPUT_TARGET;
    case "shape":
      return DECLARATION_KIND.OUTPUT_SHAPE;
    case "schema":
      if (declarationKind === DECLARATION_KIND.OUTPUT) {
        return DECLARATION_KIND.SCHEMA_DECL;
      }
      if (declarationKind === DECLARATION_KIND.OUTPUT_SHAPE) {
        return DECLARATION_KIND.OUTPUT_SCHEMA;
      }
      return DECLARATION_KIND.OUTPUT_SCHEMA;
    case "structure":
      if (
        declarationKind === DECLARATION_KIND.INPUT
        || declarationKind === DECLARATION_KIND.OUTPUT
      ) {
        return DECLARATION_KIND.DOCUMENT;
      }
      return undefined;
    case "render_profile":
      if (
        declarationKind === DECLARATION_KIND.ANALYSIS
        || declarationKind === DECLARATION_KIND.SCHEMA_DECL
        || declarationKind === DECLARATION_KIND.DOCUMENT
        || declarationKind === DECLARATION_KIND.OUTPUT
      ) {
        return DECLARATION_KIND.RENDER_PROFILE;
      }
      return undefined;
    default:
      return undefined;
  }
}

function arraysEqual(left, right) {
  if (left.length !== right.length) {
    return false;
  }

  return left.every((value, index) => value === right[index]);
}

async function uriExists(uri) {
  try {
    await vscode.workspace.fs.stat(uri);
    return true;
  } catch {
    return false;
  }
}

function uriExistsSync(uri) {
  try {
    fs.statSync(uri.fsPath);
    return true;
  } catch {
    return false;
  }
}

function loadCompileProjectConfig(documentUri) {
  const pyprojectPath = findNearestPyproject(documentUri);
  if (!pyprojectPath) {
    return { additionalPromptRootUris: [] };
  }

  const cacheKey = pyprojectPath.fsPath;
  const cached = PROJECT_CONFIG_CACHE.get(cacheKey);
  if (cached) {
    return cached;
  }

  let config = { additionalPromptRootUris: [] };
  try {
    const parsed = TOML.parse(fs.readFileSync(pyprojectPath.fsPath, "utf8"));
    const compile = parsed?.tool?.doctrine?.compile;
    const rawRoots = compile?.additional_prompt_roots;
    if (Array.isArray(rawRoots)) {
      const additionalPromptRootUris = rawRoots
        .filter((value) => typeof value === "string")
        .map((value) => resolveConfigPath(pyprojectPath, value))
        .filter((targetUri) => path.posix.basename(targetUri.path) === "prompts")
        .filter((targetUri) => uriExistsSync(targetUri));
      config = { additionalPromptRootUris };
    }
  } catch {
    config = { additionalPromptRootUris: [] };
  }

  PROJECT_CONFIG_CACHE.set(cacheKey, config);
  return config;
}

function findNearestPyproject(documentUri) {
  let currentPath = path.dirname(documentUri.fsPath);
  while (true) {
    const candidatePath = path.join(currentPath, "pyproject.toml");
    if (fs.existsSync(candidatePath)) {
      return vscode.Uri.file(candidatePath);
    }
    const parentPath = path.dirname(currentPath);
    if (parentPath === currentPath) {
      return undefined;
    }
    currentPath = parentPath;
  }
}

function resolveConfigPath(pyprojectUri, value) {
  const candidatePath = path.isAbsolute(value)
    ? value
    : path.join(path.dirname(pyprojectUri.fsPath), value);
  return vscode.Uri.file(path.resolve(candidatePath));
}

module.exports = {
  provideDefinitionLinks,
  provideImportLinks,
};
