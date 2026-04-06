# Building a VS Code syntax highlighter and formatter for a custom DSL

**Langium is almost certainly the fastest path** to a working VS Code extension with syntax highlighting, formatting, diagnostics, and completion for a custom indentation-sensitive DSL. It auto-generates TextMate grammars, a full LSP server, and TypeScript AST types from a single `.langium` grammar file — and since version 3.2, it natively supports indentation-sensitive (off-side rule) parsing via `IndentationAwareTokenBuilder`. A basic DSL with all IDE features can ship in **1–3 days** versus 4–12 weeks hand-writing everything. That said, each layer of the VS Code language stack has distinct tradeoffs worth understanding before committing to an approach. This report covers every major option comprehensively.

---

## TextMate grammars are the foundation — and the ceiling

VS Code uses TextMate grammars as its **primary tokenization engine**. Every built-in language (Python, JavaScript, YAML) ships a `.tmLanguage.json` file that the `vscode-textmate` library processes using Oniguruma regex compiled to WASM. Tokenization runs **line-by-line, top-to-bottom, in a single pass**, storing state at line boundaries for incremental re-tokenization on edits.

A TextMate grammar JSON file declares a `scopeName` (e.g., `source.mydsl`), top-level `patterns`, and a `repository` of reusable rules. Each rule is either a `match` pattern (single-line regex → scope name) or a `begin`/`end` pair (multi-line constructs like strings and block comments). Captures assign scopes to specific regex groups. For a DSL with key-value pairs, named blocks, and string literals, the grammar would look like this:

```json
{
  "scopeName": "source.mydsl",
  "patterns": [{ "include": "#expression" }],
  "repository": {
    "key-value": {
      "match": "(\\w+)(\\s*:\\s*)(.*)",
      "captures": {
        "1": { "name": "entity.name.tag.mydsl" },
        "2": { "name": "punctuation.separator.key-value.mydsl" },
        "3": { "patterns": [{ "include": "#values" }] }
      }
    },
    "strings": {
      "begin": "\"", "end": "\"",
      "name": "string.quoted.double.mydsl",
      "patterns": [{ "match": "\\\\.", "name": "constant.character.escape.mydsl" }]
    }
  }
}
```

Scope naming follows a well-established hierarchy: `keyword.control` for flow keywords, `string.quoted.double` for strings, `entity.name.function` for function names, `variable.other` for variables, and so on. Convention appends the language name as a suffix (e.g., `keyword.control.mydsl`). A minimal color theme only styles roughly 10 root scope groups, so distributing your grammar's scopes across these groups ensures good default appearance.

**The critical limitation for indentation-sensitive languages**: TextMate grammars **cannot natively handle off-side rule scoping**. Each regex matches within a single line only, and there is no mechanism to track indentation depth across lines. A `begin`/`end` pattern needs an explicit closing delimiter — you cannot end a block on dedentation. The Python, YAML, CoffeeScript, and Pug grammars in VS Code all work around this by **not attempting to scope indent-based blocks at all**. They tokenize keywords, strings, comments, and operators per-line without creating nested scopes based on indentation. TextMate 2's `begin`/`while` rules offer partial relief — a region continues while a pattern matches at each subsequent line start — but this remains fragile. For true indentation-aware scoping, you need semantic highlighting or a full parser.

Best practices for grammar authoring include: using the `repository` extensively for reusable rules (referenced via `{ "include": "#rulename" }`), using `{ "include": "$self" }` for recursive grammar embedding, writing grammars in YAML during development (for comments and readability) then converting to JSON for shipping, and debugging with VS Code's **Scope Inspector** (`Developer: Inspect Editor Tokens and Scopes`).

---

## Semantic highlighting layers intelligence on top of regex

Introduced in VS Code 1.43, semantic highlighting provides **project-aware, symbol-resolved** token information that overrides TextMate tokens where they exist. While TextMate colors all identifiers the same, a `DocumentSemanticTokensProvider` backed by a real parser can distinguish a parameter from a local variable from a class name — and it can understand indentation-level scoping that TextMate fundamentally cannot.

The API defines **22 standard token types** (including `namespace`, `class`, `function`, `variable`, `parameter`, `property`, `keyword`, `string`, `number`, `operator`, `decorator`) and **10 standard modifiers** (`declaration`, `definition`, `readonly`, `static`, `deprecated`, `abstract`, `async`, `modification`, `documentation`, `defaultLibrary`). Registration requires building a `SemanticTokensLegend` and implementing a provider:

```typescript
const legend = new vscode.SemanticTokensLegend(tokenTypes, tokenModifiers);
const provider: vscode.DocumentSemanticTokensProvider = {
  provideDocumentSemanticTokens(document) {
    const builder = new vscode.SemanticTokensBuilder(legend);
    // Parse document, emit tokens
    builder.push(range, 'variable', ['readonly']);
    return builder.build();
  }
};
vscode.languages.registerDocumentSemanticTokensProvider(selector, provider, legend);
```

Semantic tokens are encoded as a **compact integer array** (5 integers per token: delta line, delta char, length, type index, modifier bitmask) to minimize memory overhead. The optional `provideDocumentSemanticTokensEdits` method supports delta updates — only changed tokens are retransmitted after the initial full response. For very large files, `DocumentRangeSemanticTokensProvider` computes tokens only for the visible range.

**The layering model** works as follows: TextMate provides the base layer (immediate, synchronous, per-keystroke), and semantic tokens are applied on top once the language server has analyzed the file. This creates a slight delay on file open, but thereafter semantic tokens override TextMate scopes for a richer experience. All built-in VS Code themes (Dark+, Light+, Monokai) have semantic highlighting enabled by default. When a theme lacks specific semantic rules, VS Code falls back to a mapping (e.g., semantic `function` → TextMate `entity.name.function`).

**The recommended strategy for an indentation-sensitive DSL** is two layers: a TextMate grammar for immediate highlighting of keywords, strings, comments, and operators, plus a semantic token provider backed by a parser that understands indentation levels and emits structure-aware tokens.

---

## Tree-sitter in VS Code is promising but not yet native

Tree-sitter is a battle-tested incremental parser generator (MIT licensed, **24k+ GitHub stars**) used natively by Neovim, Emacs 29+, Zed, Helix, and GitHub.com for code navigation. It produces concrete syntax trees with robust error recovery — exactly what editors need. However, **VS Code has no native Tree-sitter integration** as of early 2026.

Several community bridges exist. The **tree-sitter-vscode** extension (by AlecGhost) registers a semantic token provider using user-supplied WASM Tree-sitter parsers and `.scm` query files. The **Syntax Highlighter** extension (by EvgeniyPeshkov) similarly uses VS Code's Semantic Token API to override TextMate highlighting with Tree-sitter-based tokens. Microsoft's own **vscode-anycode** extension uses Tree-sitter under the hood for lightweight Outline/Breadcrumbs/Go to Symbol features in `vscode.dev`, but it **does not provide syntax highlighting** and appears to be in maintenance mode.

The common technical approach is: use `web-tree-sitter` (the WASM build, since native `node-tree-sitter` has Electron ABI compatibility issues) → parse source → run `.scm` highlight queries → feed results to VS Code's Semantic Token API. Tree-sitter's query language maps node patterns to highlight names like `@keyword`, `@function`, `@string` using S-expression syntax.

For indentation-sensitive languages, Tree-sitter requires an **external scanner** — a C function that emits synthetic INDENT/DEDENT tokens. The `tree-sitter-python` grammar uses this approach. Writing an external scanner requires C programming and is recognized as one of the more challenging aspects of Tree-sitter grammar authoring.

**The VS Code team has shown active interest** in native Tree-sitter support. Issue #50140 (from 2018) is a long-running feature request. An internal exploration (issue #210475, assigned to alexr00 in April 2024) is investigating Tree-sitter tokenization performance and a contribution model. The key blocker cited by VS Code team member alexdima is Tree-sitter's parser ABI versioning — periodic ABI changes could break extensions, conflicting with VS Code's stability guarantees. As of early 2026, this remains in exploration with no shipping timeline.

**Tradeoffs versus TextMate**: Tree-sitter offers context-aware, accurate parsing with proper nesting and error recovery, versus TextMate's fast but imprecise regex matching. But Tree-sitter requires extension-level workarounds for VS Code, lacks theme compatibility (TextMate scopes are what themes target), and has a less mature VS Code ecosystem. For a new custom DSL, building a Tree-sitter grammar mainly makes sense if you also plan to support Neovim/Zed/Emacs, or if you want to use Topiary for formatting.

---

## Langium generates an entire language toolchain from one grammar

Langium is a TypeScript-based language engineering framework from TypeFox (the creators of Xtext), now an **Eclipse Foundation graduated project** (since late 2024, version 3.3). It uses Chevrotain under the hood for blazing-fast LL(k) parsing and generates a complete VS Code extension from a single `.langium` grammar definition.

What you get from `npm run langium:generate`: TypeScript AST interfaces, a full parser, an auto-generated `.tmLanguage.json` TextMate grammar, and a complete Language Server providing syntax error reporting, context-aware code completion, go-to-definition/find references, document symbols/outline, rename/refactoring, hover information, and semantic highlighting via `AbstractSemanticTokenProvider`.

**Indentation-sensitive language support** was added in Langium 3.2 through `IndentationAwareTokenBuilder` and `IndentationAwareLexer`. These generate synthetic INDENT/DEDENT tokens from whitespace, with configuration options for delimiter-aware indentation ignoring (like Python's behavior inside brackets/parentheses). Few competing frameworks handle this so cleanly.

**Formatting** is supported via the `AbstractFormatter` class with a node-based API:

```typescript
export class MyFormatter extends AbstractFormatter {
  protected format(node: AstNode): void {
    if (ast.isBlock(node)) {
      const formatter = this.getNodeFormatter(node);
      formatter.property("name").surround(Formatting.oneSpace());
      formatter.nodes(...node.children).prepend(Formatting.indent());
    }
  }
}
```

Options include `newLine()`, `indent()`, `oneSpace()`, `noSpace()`, and `spaces(n)`. Formatting is not auto-generated — you must write rules manually — but the API is clean and well-documented.

**Effort estimates** compared to alternatives:

- Hand-written TextMate + LSP from scratch: **4–12 weeks**
- Tree-sitter + custom LSP server: **3–8 weeks**
- ANTLR + custom LSP server: **3–8 weeks**
- **Langium: 1–3 days** for basic IDE features; **2–6 weeks** for production quality

**Limitations**: LL(k) parser cannot handle left-recursive grammars directly (requires left-factoring). The auto-generated TextMate grammar is sufficient for basic cases but may need manual refinement for complex languages. Community is growing but smaller than Xtext's (~400 GitHub stars, ~4,000 npm downloads/week). Documentation at langium.org is generally good, though it can lag behind rapid framework evolution. No built-in type system — type checking must be implemented manually.

---

## LSP and the VS Code formatting API work together or independently

The Language Server Protocol defines a JSON-RPC-based client-server architecture. The lifecycle begins with an `initialize` handshake where capabilities are negotiated — a server can support formatting but not completion. For formatting specifically, LSP defines three requests:

- **`textDocument/formatting`** — full document formatting
- **`textDocument/rangeFormatting`** — selection formatting
- **`textDocument/onTypeFormatting`** — triggered by specific characters (e.g., `;`, `}`, `\n`)

All three return `TextEdit[]` — arrays of range+replacement pairs applied to the original document. Ranges must never overlap, and edits are applied bottom-to-top.

The `FormattingOptions` object carries `tabSize`, `insertSpaces`, and since LSP 3.15, `trimTrailingWhitespace`, `insertFinalNewline`, and `trimFinalNewlines`.

Four major LSP server libraries compete across languages:

**vscode-languageserver-node** (Microsoft, Node.js) is the reference implementation and most mature option. Minimal boilerplate — `createConnection()`, register handlers, done. Best VS Code integration, largest community, most tutorials. Limited by Node.js single-threaded model for CPU-intensive parsing.

**tower-lsp** (Rust) builds on the Tower service abstraction and Tokio async runtime. Excellent performance, small binaries, no runtime dependency. Steeper learning curve (Rust + async). The community has forked into `tower-lsp` (original) and `tower-lsp-server` (community), creating some confusion. ~1K GitHub stars.

**pygls** (Python, maintained by Open Law Library) uses a decorator-based API that gets a working server in ~15 lines. Extremely Pythonic, ideal for prototyping. Limited by Python's GIL for parallelism and slower execution. ~200+ known implementations.

**lsp4j** (Java, Eclipse Foundation) is very mature but verbose. Best for JVM-based language tooling. JVM startup overhead (~500ms+) and larger distribution size are downsides.

On the VS Code Extension API side, you can register formatters directly without LSP:

```typescript
vscode.languages.registerDocumentFormattingEditProvider('mydsl', {
  provideDocumentFormattingEdits(document, options) {
    const formatted = formatMyDSL(document.getText(), options.tabSize);
    const fullRange = new vscode.Range(
      document.positionAt(0), document.positionAt(document.getText().length)
    );
    return [vscode.TextEdit.replace(fullRange, formatted)];
  }
});
```

The three provider interfaces — `DocumentFormattingEditProvider`, `DocumentRangeFormattingEditProvider`, and `OnTypeFormattingEditProvider` — map to Format Document, Format Selection, and format-on-type respectively. When multiple formatters register for the same language, VS Code either uses the user's `editor.defaultFormatter` setting or prompts for selection. **Only one formatter runs at a time** — no chaining.

**When to use LSP versus direct API**: Use the direct VS Code API for VS Code-only extensions with lightweight formatting logic and no persistent server state. Use LSP when you want editor-agnostic support, need persistent state (parsed AST, symbol tables) for intelligent formatting, or are building a complete language experience where formatting is one of many features. When using LSP, the `vscode-languageclient` library automatically bridges LSP formatting requests to VS Code's infrastructure — no separate `DocumentFormattingEditProvider` registration needed.

---

## Five approaches to building a formatter, from trivial to industrial

The universal formatter pipeline is: **source → parse → AST → pretty-print → output**. For indentation-sensitive languages, the parser must track indentation as syntax (encoding it in the tree structure), and the printer re-emits indentation proportional to nesting depth. Since the tree structure IS the semantic structure, normalizing indentation (e.g., always 4 spaces per level) preserves meaning.

**Approach 1: Template-based string emission.** Walk the AST, emit strings with manual indentation tracking using a depth counter. Under 50 lines of code for a simple DSL. No line-width intelligence, hard to maintain as the DSL grows. Best for DSLs with completely predictable structure that won't evolve.

**Approach 2: Wadler-Lindig pretty-printing algorithm.** Philip Wadler's 2003 paper "A Prettier Printer" describes an algebraic approach using six document combinators: `nil`, `text(s)`, `line`, `nest(i, doc)`, `concat`, and `group(doc)`. The `group` combinator encodes layout choices — try flat first, break at `line` positions if the flat version exceeds the print width. The algorithm is **greedy and O(n)**, resolving groups one line at a time. Implementations exist in every major language: the Rust `pretty` crate (502K+ monthly downloads), Python's `wadler_lindig` package (96 lines for the core algorithm), Haskell's `prettyprinter` library, and — notably — **Prettier's core engine is directly based on this algorithm**. For a custom DSL, you write a recursive `to_doc()` function converting each AST node to a Doc, then render with a target width. This is typically **100–200 lines of formatting code** for a small DSL.

**Approach 3: Prettier plugin.** Prettier's plugin API is the same API used by all its built-in language implementations. A plugin exports `languages`, `parsers` (with `parse`, `locStart`, `locEnd`), and `printers` (with a `print` function). The printer builds a **Doc IR** using commands like `group()`, `indent()`, `line`, `softline`, `hardline`, `fill()`, and `ifBreak()` — these map directly to Wadler's combinators. You get Prettier's battle-tested line-breaking, comment-handling infrastructure, and automatic editor integration for free. The downside: you must write the plugin in JavaScript/TypeScript, you're tied to Prettier's opinionated model, and **plugin composition is fragile** — multiple plugins targeting the same language can conflict. Roughly **2–5 days of effort**, and 30+ community plugins exist for reference (Solidity, PHP, Ruby, XML, Pug, SQL).

**Approach 4: Topiary (Tree-sitter query-based formatting).** A Rust-based universal formatter by Tweag where formatting rules are expressed as declarative Tree-sitter queries. You write patterns like `(infix_operator) @append_space` to add spaces after operators. Extremely fast development — a GDScript formatter was built in hours. However, Topiary's maintainers explicitly state it is **"not suitable for languages that employ semantic whitespace"** — ruling it out for indentation-sensitive DSLs.

**Approach 5: dprint (Rust + Wasm plugin platform).** A pluggable formatting platform where plugins are sandboxed Wasm modules. The `dprint-core` crate provides a Wadler-style IR with `PrintItems`. Medium-high effort (3–7 days) and smaller community, but fast execution and strong sandboxing. Best for Rust-based toolchains needing high performance.

For an indentation-sensitive DSL compiling to markdown, **Approach 2 (standalone Wadler-style) or Langium's AbstractFormatter** are the strongest choices. Both give full control over indentation-as-syntax preservation, and for a small DSL the implementation is very tractable.

---

## Scaffolding, configuration, and the practical details that matter

**The `yo generator-code` scaffolding tool** bootstraps a VS Code extension project. Install with `npm install -g yo generator-code`, run `yo code`, and select "New Language Support." It generates: a `syntaxes/` directory with a `.tmLanguage.json` stub, a `language-configuration.json` with basic bracket/comment definitions, a `package.json` with `contributes.languages` and `contributes.grammars` entries, and a `.vscode/launch.json` for debugging in the Extension Development Host. You must add grammar rules, formatting logic, and language server support manually.

For Langium-based projects, use `npm install -g yo generator-langium` followed by `yo langium` — this scaffolds a complete project with grammar file, language server, VS Code client, and optional CLI.

**The `language-configuration.json` file** controls bracket matching, auto-closing, commenting, folding, and indentation behavior. For an indentation-sensitive DSL, the most important settings are:

- **`onEnterRules`**: Define patterns that trigger auto-indent on Enter. For a DSL with keywords that open blocks: `{ "beforeText": "^\\s*(?:block|section|def).*:\\s*$", "action": { "indent": "indent" } }`
- **`editor.foldingStrategy": "indentation"`** in `configurationDefaults`: VS Code's built-in indentation-based folding is the default fallback and works perfectly for Python-like languages without any extra configuration
- **`indentationRules`**: Regex patterns for `increaseIndentPattern` and `decreaseIndentPattern`. For indentation-sensitive languages, the Python team found these **insufficient** alone (GitHub issue #8996) and supplemented with `onEnterRules` and programmatic `formatOnType` handlers

The `package.json` manifest registers everything: `contributes.languages` (id, aliases, file extensions, configuration path, icon), `contributes.grammars` (language, scopeName, path, embeddedLanguages), and `contributes.configurationDefaults` for per-language editor settings. Since VS Code 1.74, extensions that contribute a language are activated implicitly on `onLanguage` — no explicit activation event needed, though always include at least a minimal `language-configuration.json` to avoid activation issues.

**Testing tools**: Use `vscode-tmgrammar-test` (npm package) for TextMate grammar unit tests (inline `^` annotations asserting scopes) and snapshot tests (auto-generated `.snap` files detecting regressions). Use `@vscode/test-electron` for integration testing that launches a real VS Code instance. Both work in headless CI with `xvfb-run`. The **vscode-textmate-languageservice** library can generate folding, document symbols, and other features directly from TextMate grammars without writing a language server — useful for quickly bootstrapping basic structural features.

**Packaging and publishing**: Use `@vscode/vsce` to create `.vsix` files (`vsce package`) and publish to the marketplace (`vsce publish`). For open-source editors like VSCodium and Gitpod, also publish to Open VSX (`ovsx publish`). The `HaaLeo/publish-vscode-extension` GitHub Action handles both marketplaces.

---

## The Monarch tokenizer is Monaco-only, not VS Code

Monarch is Monaco Editor's built-in declarative tokenization system — a JSON-based, state-machine-driven tokenizer using JavaScript regex. It was created because TextMate grammars originally required native Oniguruma, which couldn't run in browsers. Monarch features explicit state management (`@push`/`@pop`), efficient keyword arrays with `cases` guards, and dynamic token classes via `$1` capture expansion.

**Monarch cannot be used in VS Code extensions.** VS Code Desktop uses TextMate grammars exclusively for syntax highlighting. Monarch is only accessible through `monaco.languages.setMonarchTokensProvider()` in standalone Monaco deployments (e.g., web-based code playgrounds). Since Oniguruma now compiles to WASM, the `monaco-tm` library also enables TextMate grammars in standalone Monaco, making Monarch less essential even in its native domain. For a VS Code extension, Monarch is irrelevant — use TextMate grammars plus optional semantic tokens.

---

## Real-world extensions for indentation-sensitive languages to study

The best reference implementations for indentation-sensitive VS Code language support:

- **Python** (built-in grammar at `microsoft/vscode/extensions/python/`; main extension at `microsoft/vscode-python`): TextMate grammar for basic syntax, Pylance adds semantic highlighting. Uses `onEnterRules` for indent-triggering keywords. Formatting delegated to external tools (Black, autopep8). The `vsc-python-indent` community extension by kbrose is an especially instructive reference — it parses Python code on Enter to determine correct indentation.

- **YAML** (`redhat-developer/vscode-yaml`): Built-in TextMate grammar plus a YAML Language Server for validation, completion, and formatting. Uses VS Code's built-in indentation-based folding.

- **Haskell** (`haskell/vscode-haskell`): TextMate grammar from `language-haskell` plus semantic tokens from HLS (Haskell Language Server). Formatting via HLS integration with Ormolu/Fourmolu/Stylish Haskell.

- **CoffeeScript** (built-in at `microsoft/vscode/tree/main/extensions/coffeescript`): Pure TextMate grammar, no semantic tokens or language server. Minimal `language-configuration.json`. Relies on indentation-based folding. A good minimal reference.

- **Pug** (built-in at `microsoft/vscode/tree/main/extensions/pug`): Purely indentation-based template language. TextMate grammar uses `begin`/`while` patterns with `^(\s*)` captures for partial indentation handling. Sets `diffEditor.ignoreTrimWhitespace: false` as a language default.

- **Nim** (`nim-lang/vscode-nim`): TextMate grammar with indentation-based folding. Formatting delegated to external `nimpretty` tool.

---

## Choosing the fastest path: a decision framework

For a custom indentation-sensitive DSL that compiles to markdown, three viable paths exist ranked by speed-to-working-extension:

**Path 1 — Langium (recommended fastest path)**. Define your grammar in a `.langium` file using `IndentationAwareTokenBuilder` for off-side rule support. Run `langium:generate` to get a TextMate grammar, parser, AST types, and LSP server. Write a formatter extending `AbstractFormatter`. Package with `vsce`. **Total effort: 1–5 days for a working extension with highlighting, formatting, validation, and completion.** Tradeoff: LL(k) parser limitations, smaller community than hand-rolled solutions, TypeScript-only stack.

**Path 2 — Hand-rolled TextMate + direct VS Code formatter**. Scaffold with `yo code`, write a TextMate grammar for basic syntax elements, add a `DocumentFormattingEditProvider` that parses your DSL and re-emits formatted output using Wadler-style pretty-printing (import `prettier.doc.builders` directly, or use a standalone implementation). **Total effort: 1–2 weeks for highlighting + formatting.** Tradeoff: no completion, diagnostics, or go-to-definition without additional LSP work; TextMate grammar can't scope indent blocks.

**Path 3 — TextMate + custom LSP server (Node.js or Rust)**. Use `vscode-languageserver-node` or `tower-lsp` to build a language server with a real parser, providing semantic tokens, formatting, diagnostics, and completion. Layer semantic highlighting on top of a TextMate grammar for immediate visual feedback. **Total effort: 3–8 weeks for a complete IDE experience.** Tradeoff: significantly more work, but maximum control and accuracy.

All three paths should set `"editor.foldingStrategy": "indentation"` in `configurationDefaults` to get correct code folding out of the box.

## Conclusion

The VS Code language extension ecosystem is layered by design: TextMate grammars provide instant regex-based tokenization, semantic tokens add parser-aware intelligence on top, LSP servers deliver formatting and diagnostics, and `language-configuration.json` handles the mechanical editor behaviors like bracket matching and indentation. For indentation-sensitive DSLs specifically, the key insight is that **TextMate grammars fundamentally cannot scope indent-based blocks** — every production indentation-sensitive extension (Python, YAML, Haskell) works around this by tokenizing per-line syntax elements and delegating structural understanding to semantic tokens or a language server.

Langium collapses the multi-week effort of hand-building each layer into a single generate step, with native off-side rule support since version 3.2 making it uniquely suited for Python-like DSLs. For formatting, the Wadler-Lindig algorithm (or its practical incarnation in Prettier's Doc IR) is the proven approach — it naturally handles indentation through `nest`/`indent` combinators and makes line-breaking decisions automatically. The strongest combination for a custom DSL that compiles to markdown: **Langium for the complete toolchain, supplemented by manual TextMate grammar refinements and a custom `AbstractFormatter` using Wadler-style indentation rules**, with `vscode-tmgrammar-test` ensuring grammar correctness and `vsce` for packaging.
