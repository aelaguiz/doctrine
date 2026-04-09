const path = require("node:path");

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
  `^\\s*(?:abstract\\s+)?agent\\s+${IDENTIFIER_PATTERN}\\s*\\[(${DOTTED_NAME_PATTERN})\\]\\s*:\\s*$`,
);
const INHERITED_BLOCK_RE = new RegExp(
  `^\\s*(workflow|skills|inputs|outputs)\\s+${IDENTIFIER_PATTERN}\\s*\\[(${DOTTED_NAME_PATTERN})\\]\\s*:`,
);
const PATCH_FIELD_RE = new RegExp(
  `^\\s*(inputs|outputs)\\s*\\[(${DOTTED_NAME_PATTERN})\\]\\s*:\\s*${STRING_PATTERN}\\s*$`,
);
const ROUTE_RE = new RegExp(
  `^(\\s*route\\s+\")((?:[^\"\\\\]|\\\\.)*)(\"\\s*->\\s*)(${DOTTED_NAME_PATTERN})\\s*$`,
);
const USE_RE = new RegExp(
  `^\\s*use\\s+(${IDENTIFIER_PATTERN})\\s*:\\s*(${DOTTED_NAME_PATTERN})\\s*$`,
);
const TOP_LEVEL_FIELD_REF_RE = new RegExp(
  `^\\s*(skills|inputs|outputs)\\s*:\\s*(${DOTTED_NAME_PATTERN})\\s*$`,
);
const KEYED_DECL_REF_RE = new RegExp(
  `^\\s*(source|target|shape|schema)\\s*:\\s*(${DOTTED_NAME_PATTERN})\\s*$`,
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

const PROSE_LINE_RE = /^\s*(?:(?:required|important|warning|note)\s+)?"(?:\\.|[^"\\])*"\s*$/;
const ROLE_INLINE_RE = new RegExp(`^\\s*role\\s*:\\s*${STRING_PATTERN}\\s*$`);
const PURPOSE_OR_REASON_RE = new RegExp(
  `^\\s*(purpose|reason)\\s*:\\s*${STRING_PATTERN}\\s*$`,
);

const RESERVED_AGENT_FIELD_KEYS = new Set(["role", "inputs", "outputs", "skills"]);
const READABLE_DECLARATION_KINDS = Object.freeze([
  "agent",
  "input",
  "input_source",
  "output",
  "output_target",
  "output_shape",
  "json_schema",
  "skill",
  "enum",
]);

const DECLARATION_KIND = Object.freeze({
  AGENT: "agent",
  WORKFLOW: "workflow",
  SKILLS_BLOCK: "skills",
  INPUTS_BLOCK: "inputs",
  INPUT: "input",
  INPUT_SOURCE: "input_source",
  OUTPUTS_BLOCK: "outputs",
  OUTPUT: "output",
  OUTPUT_TARGET: "output_target",
  OUTPUT_SHAPE: "output_shape",
  JSON_SCHEMA: "json_schema",
  SKILL: "skill",
  ENUM: "enum",
});

const ADDRESSABLE_DECLARATION_KINDS = Object.freeze([
  DECLARATION_KIND.AGENT,
  DECLARATION_KIND.WORKFLOW,
  DECLARATION_KIND.SKILLS_BLOCK,
  DECLARATION_KIND.INPUT,
  DECLARATION_KIND.INPUT_SOURCE,
  DECLARATION_KIND.OUTPUT,
  DECLARATION_KIND.OUTPUT_TARGET,
  DECLARATION_KIND.OUTPUT_SHAPE,
  DECLARATION_KIND.JSON_SCHEMA,
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
    kind: DECLARATION_KIND.WORKFLOW,
    regex: new RegExp(
      `^\\s*workflow\\s+(${IDENTIFIER_PATTERN})(?:\\s*\\[(${DOTTED_NAME_PATTERN})\\])?\\s*:`,
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
      `^\\s*output\\s+shape\\s+(${IDENTIFIER_PATTERN})\\s*:`,
    ),
    nameGroup: 1,
  },
  {
    kind: DECLARATION_KIND.OUTPUT,
    regex: new RegExp(`^\\s*output\\s+(${IDENTIFIER_PATTERN})\\s*:`),
    nameGroup: 1,
  },
  {
    kind: DECLARATION_KIND.JSON_SCHEMA,
    regex: new RegExp(
      `^\\s*json\\s+schema\\s+(${IDENTIFIER_PATTERN})\\s*:`,
    ),
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
    case "workflow_body":
      sites.push(...collectWorkflowBodySites(lineText, position.line));
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
        ...collectRecordBodySites(
          lineText,
          position.line,
          lineContext.container.fieldKind,
        ),
      );
      break;
    default:
      break;
  }

  for (const site of sites) {
    if (site.type === "structuralKeyRef") {
      site.lineContext = lineContext;
    }
  }

  return sites.find((site) => site.range.contains(position));
}

function collectAgentBodySites(lineText, lineNumber) {
  const sites = [];

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

function collectRecordBodySites(lineText, lineNumber, fieldKind) {
  const sites = [];

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

  const keyedRef = lineText.match(KEYED_DECL_REF_RE);
  if (keyedRef) {
    sites.push({
      type: "directDeclRef",
      declarationKind: keyedFieldToDeclarationKind(keyedRef[1]),
      range: createLastMatchRange(lineText, lineNumber, keyedRef[2]),
      ref: parseNameRef(keyedRef[2]),
      requireConcrete: false,
    });
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
    case "workflow_body":
      return getWorkflowBodyItems(parentBody.document, parentBody.bodySpec).get(key);
    case "workflow_section_body":
      return getWorkflowSectionBodyItems(parentBody.document, parentBody.bodySpec).get(key);
    case "skills_body":
      return getSkillsBodyItems(parentBody.document, parentBody.bodySpec).get(key);
    case "io_body":
      return getIoBodyItems(parentBody.document, parentBody.bodySpec).get(key);
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
    case DECLARATION_KIND.JSON_SCHEMA:
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
    case "workflow_body":
      childBody = getWorkflowChildBodySpec(lineText, lineNumber);
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
      childBody = getRecordChildBodySpec(lineText, lineNumber, container.fieldKind);
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

function getWorkflowChildBodySpec(lineText, lineNumber) {
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

function getRecordChildBodySpec(lineText, lineNumber, fieldKind) {
  if (
    new RegExp(
      `^\\s*(?:${IDENTIFIER_PATTERN}\\s*:\\s*(?:${STRING_PATTERN}|${DOTTED_NAME_PATTERN}|${PATH_REF_PATTERN})|${DOTTED_NAME_PATTERN})\\s*$`,
    ).test(lineText)
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

    const enumMember = lineText.match(
      new RegExp(`^\\s*(${IDENTIFIER_PATTERN})\\s*:\\s*${STRING_PATTERN}\\s*$`),
    );
    if (!enumMember) {
      continue;
    }

    items.set(enumMember[1], {
      keyRange: createFirstMatchRange(lineText, lineNumber, enumMember[1]),
      lineNumber,
    });
  }

  return items;
}

function getAddressableBodyItems(document, bodySpec) {
  switch (bodySpec.type) {
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
    default:
      return new Map();
  }
}

async function findAddressablePathTarget({ declaration, pathSegments, source }) {
  if (declaration.kind === DECLARATION_KIND.AGENT) {
    if (pathSegments.length === 1 && pathSegments[0] === "name") {
      return {
        document: source.document,
        lineNumber: declaration.lineNumber,
        selectionRange: declaration.nameRange,
      };
    }
    return undefined;
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
    if (!target) {
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

  return {
    document: source.document,
    lineNumber: target.lineNumber,
    selectionRange: target.keyRange,
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

    entries.push({
      moduleParts: resolvedModuleParts,
      range: createLastMatchRange(lineText, lineNumber, match[1]),
      targetUri: modulePartsToPromptUri(context.promptRootUri, resolvedModuleParts),
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

  return { currentModuleParts, promptRootUri };
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
    case "workflow":
      return DECLARATION_KIND.WORKFLOW;
    case "skills":
      return DECLARATION_KIND.SKILLS_BLOCK;
    case "inputs":
      return DECLARATION_KIND.INPUTS_BLOCK;
    case "outputs":
      return DECLARATION_KIND.OUTPUTS_BLOCK;
    default:
      return undefined;
  }
}

function keyedFieldToDeclarationKind(fieldName) {
  switch (fieldName) {
    case "skills":
      return DECLARATION_KIND.SKILLS_BLOCK;
    case "inputs":
      return DECLARATION_KIND.INPUTS_BLOCK;
    case "outputs":
      return DECLARATION_KIND.OUTPUTS_BLOCK;
    case "source":
      return DECLARATION_KIND.INPUT_SOURCE;
    case "target":
      return DECLARATION_KIND.OUTPUT_TARGET;
    case "shape":
      return DECLARATION_KIND.OUTPUT_SHAPE;
    case "schema":
      return DECLARATION_KIND.JSON_SCHEMA;
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

module.exports = {
  provideDefinitionLinks,
  provideImportLinks,
};
