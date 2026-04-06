# Parser libraries for indentation-sensitive DSLs

**Lark (Python), Chevrotain/Langium (JS/TS), and chumsky (Rust) are the strongest choices** for building your Python-like DSL with off-side rule indentation, each offering native or well-documented indentation support in their respective ecosystems. The fundamental technique across all ecosystems remains the same: convert indentation into explicit INDENT/DEDENT tokens at the lexer stage, then feed a standard context-free grammar. However, these three libraries minimize the manual work required. Below is a detailed analysis of every major option, organized by ecosystem, with concrete guidance on tradeoffs.

## The universal pattern: why indentation is a lexer problem

Every successful indentation-sensitive language—Python, Haskell, CoffeeScript, F#—solves parsing the same way. A lexer maintains a stack of indentation levels, initialized at `[0]`. At each new line, it compares leading whitespace against the stack top: greater indentation emits an `INDENT` token and pushes; equal indentation emits `NEWLINE`; lesser indentation pops until a matching level is found, emitting one `DEDENT` per pop. At EOF, remaining levels emit final `DEDENT` tokens. This transforms the context-sensitive indentation problem into a context-free one any parser can handle, treating `INDENT`/`DEDENT` exactly like `{`/`}`.

The key differentiator between libraries is **how much of this machinery they provide out of the box** versus requiring you to hand-write it. Common pitfalls include forgetting EOF dedents, mishandling blank lines (which should be ignored), mixing tabs and spaces, and multi-line strings triggering false indentation changes.

## Python ecosystem: Lark dominates with built-in indentation

**Lark** (~5,800 GitHub stars, actively maintained, MIT license) is the clear winner for Python. It provides a built-in `Indenter` class as a post-lexer stage that automatically manufactures INDENT/DEDENT tokens. You subclass `Indenter` in roughly **10 lines of Python**, specifying token names for newlines, indents, and dedents, then pass it via `postlex=` to the parser. Lark ships a complete Python 3 grammar (`python.lark`) using its `PythonIndenter`—a battle-tested reference for indentation-sensitive parsing. Grammars use clean EBNF-like `.lark` files with `%import`, `%ignore`, and `%declare` directives. AST generation is automatic: Lark builds a `Tree` of `Token` objects from your grammar structure, and its powerful `Transformer` pattern enables bottom-up tree rewriting for converting parse trees into your target format. The `ast_utils` module can even map directly to Python dataclasses. For your DSL compiling to markdown, the workflow would be: define grammar rules for key-value pairs, named blocks, and string literals → use `Indenter` for nesting → transform the parse tree into your markdown structure. Known gotchas include interactions between comments and the Indenter (issue #863), the fact that indentation isn't purely declarative (requires a Python class alongside the grammar), and **~20x slower performance** than hand-written parsers for very large files in some benchmarks.

**pyparsing** (~2,300 stars, actively maintained) is a strong alternative with its built-in `IndentedBlock` class since v3.0, which handles indentation directly in grammar expressions with no separate lexer class needed. Its grammar-as-Python-code approach (using operator overloading like `+` and `|`) is excellent for rapid prototyping but less portable and harder to maintain than Lark's grammar files. It returns `ParseResults` objects rather than offering Lark's clean Transformer pipeline.

**ANTLR with Python target** (~17,000 stars for ANTLR overall) has no built-in indentation support and requires the community `antlr-denter` helper library (~200 stars), plus a Java dependency for code generation. Terence Parr himself noted that indentation handling in ANTLR can get "pretty ugly very quickly." For a DSL of this scope, ANTLR is overkill. **PLY** is officially abandoned by its author. **Parsimonious** has only experimental `TokenGrammar` support for pre-lexed token streams and appears effectively inactive. **textX** explicitly states it has no support for whitespace-sensitive languages.

## JavaScript/TypeScript ecosystem: Chevrotain and Langium lead

**No JS parser natively handles Python-style indentation**—all require the INDENT/DEDENT lexer pattern. Among available options, **Chevrotain** (~2,700 stars, ~2–3M weekly npm downloads, written in TypeScript) offers the best-documented approach. It provides custom token pattern matchers where you maintain an indentation stack and emit INDENT/DEDENT tokens, with a dedicated [Python indentation example](https://github.com/chevrotain/chevrotain/blob/master/examples/lexer/python_indentation/python_indentation.js) in the repository. Chevrotain auto-generates a CST and provides a visitor pattern (`BaseCstVisitor`) for building custom ASTs. Its grammar-as-TypeScript-code approach is more verbose than grammar files but extremely debuggable and flexible.

The real standout is **Langium** (~5,000 stars), Eclipse's language workbench built on Chevrotain, which shipped a production-ready **`IndentationAwareTokenBuilder`** in v3.2.0. This is the most turnkey indentation solution in the JS/TS ecosystem. Langium also auto-generates AST type definitions, LSP features (code completion, go-to-definition, diagnostics), and TextMate grammars—making it ideal if you ever want VS Code support for your DSL.

**Ohm.js** (~5,400 stars) deserves mention for prototyping. It offers an experimental `IndentationSensitive` supergrammar you can inherit from, providing `indent` and `dedent` as primitive rules. The separation of grammar from semantic actions is exceptionally clean, and the interactive Ohm Editor is superb for development. However, **the indentation feature is buggy for non-trivial grammars** (multiple open issues with nested blocks and multi-level dedents), making it risky for production.

**Peggy** (PEG.js successor, ~1,100 stars, actively maintained) fundamentally struggles with indentation because PEG parsing is context-free—you'd need stateful semantic predicate hacks that fight against PEG's backtracking. **nearley.js** (~3,700 stars) can work with the `moo-indentation-lexer` wrapper, but both nearley and the indentation lexer are effectively unmaintained (last releases ~2020). **Lezer** (CodeMirror's parser) has an elegant indentation approach using `ContextTracker` and external tokenizers, with excellent official documentation, but it's optimized for editor integration rather than standalone compilation. **Tree-sitter** requires writing the external scanner in C, making it impractical for pure JS/TS projects.

## Rust ecosystem: chumsky offers native context-sensitive parsing

**chumsky** (~4,500 stars, actively developed) is the standout in Rust. Its README explicitly states support for "context-sensitive grammars via a set of dedicated combinators... including Python-style semantic indentation." The v0.10 rewrite introduced `ConfigParser`, `ignore_with_ctx`, `then_with_ctx`, and `map_ctx` combinators that pass context (like current indentation level) to sub-parsers, making indentation handling significantly more natural than any other Rust library. Its flagship feature is **best-in-class error recovery**—critical for DSL users—with rich error types that integrate with the Ariadne crate for beautiful diagnostics. The caveat: the 0.10.x API is still stabilizing toward 1.0, and some documentation references the old 0.9 API.

The **logos + LALRPOP** combination is the most battle-tested approach, used by **RustPython** for actual Python parsing. You write a custom lexer wrapper around logos (~1,900 stars, very fast DFA-based tokenizer) that emits INDENT/DEDENT tokens, then write LALRPOP grammar rules (~3,000 stars) consuming those tokens. LALRPOP's `.lalrpop` grammar files are readable BNF with embedded Rust action code that directly constructs AST types. The upfront setup is more involved (custom lexer + grammar file + build.rs), but the result is extremely reliable.

**pest** (~5,000 stars, ~110M crates.io downloads) has a clever stack mechanism (`PUSH`, `PEEK_ALL`, `POP`, `DROP`) that can track indentation in PEG grammars, but this is a workaround rather than a first-class feature and is fragile for complex grammars. **nom** (~9,500 stars) and **winnow** (~600 stars but ~471M downloads, used by cargo/clap) are excellent parser combinator libraries but require fully manual indentation state management that fights their design. **ANTLR for Rust** is community-maintained, not an official target, with only ~340 stars and ~3,500 crates.io downloads—too immature for production use.

## Cross-ecosystem tools and when not to use a parser generator

**ANTLR** remains the most powerful cross-ecosystem option for complex languages, with 10 official targets and 200+ community grammars. But for indentation, you'll always need the target-specific DenterHelper pattern, and the Java build dependency adds friction. **Tree-sitter** (~24,200 stars) is exceptional for editor integration across Neovim, Helix, Zed, and GitHub.com, but its requirement for C external scanners and its design focus on incremental parsing make it wrong as a primary compilation parser.

For a DSL of your described complexity—key-value pairs, named blocks, string literals, compiling to markdown—a full parser generator may be overkill. A hand-written recursive descent parser with an indentation preprocessor would total **300–600 lines** in any language and gives maximum control over error messages. CoffeeScript and TypeScript both use hand-written parsers. That said, using a library like Lark or Chevrotain provides grammar-as-documentation, automatic AST construction, and easier maintenance as the DSL evolves.

One tempting shortcut to avoid: **using a YAML parser as a base**. While YAML is indentation-sensitive with native key-value support, its implicit type coercion (`yes`/`no` → booleans, version numbers → floats), 83-page spec complexity, and inability to represent custom block syntax (`agent Name:`) cleanly make it a poor foundation.

## Comparative overview across all ecosystems

| Library | Ecosystem | Indent support | Stars | AST generation | Best for |
|---|---|---|---|---|---|
| **Lark** | Python | Built-in Indenter class | ~5.8K | Automatic Tree + Transformer | ⭐ Python DSL projects |
| **pyparsing** | Python | Built-in IndentedBlock | ~2.3K | ParseResults (partial) | Rapid prototyping |
| **Chevrotain** | JS/TS | Custom token patterns (documented) | ~2.7K | Auto CST + Visitor | Production JS/TS DSLs |
| **Langium** | JS/TS | IndentationAwareTokenBuilder (v3.2+) | ~5K | Auto AST + LSP | ⭐ DSL + editor tooling |
| **Ohm.js** | JS/TS | Experimental IndentationSensitive | ~5.4K | Semantic actions | Prototyping only |
| **chumsky** | Rust | Native context-sensitive combinators | ~4.5K | Manual via .map() | ⭐ Rust DSL projects |
| **logos + LALRPOP** | Rust | Custom lexer wrapper | 1.9K + 3K | Semi-auto in grammar | Battle-tested (RustPython) |
| **pest** | Rust | Stack-based workaround | ~5K | Manual tree walking | Simple PEG grammars |
| **ANTLR** | Multi | antlr-denter helper (Java/Py/C#) | ~17K | Auto listeners/visitors | Complex multi-target langs |
| **Tree-sitter** | Multi | External scanner in C | ~24K | CST traversal | Editor/IDE integration |

## Conclusion

The right choice depends on your primary ecosystem and whether you need editor tooling. **In Python, Lark is the definitive answer**—its Indenter class, EBNF grammar files, and Transformer pipeline are purpose-built for exactly this use case. **In JavaScript/TypeScript, Langium's `IndentationAwareTokenBuilder`** offers the most turnkey solution with the bonus of automatic LSP generation; use raw Chevrotain if you want lower-level control. **In Rust, chumsky's context-sensitive combinators** provide the most natural indentation handling, though logos + LALRPOP offers a more battle-tested path if you're willing to write a custom lexer wrapper.

The most underappreciated insight from this research: for a DSL of this complexity, a hand-written parser (~500 lines) with an indentation preprocessor may outperform any library in terms of error message quality, debuggability, and zero dependencies. Libraries shine when your grammar is likely to evolve significantly or when you want the grammar definition to serve as living documentation. If the DSL's scope is well-defined and stable, the simplest tool that works is often the best tool.

---


# Parser and AST Toolkits for an Indentation-Sensitive, Python-Like Prompt DSL

## What your example implies about the language

Your sample looks like a whitespace-significant (indentation-scoped) DSL with:

Declarative blocks introduced by a header ending in `:` (e.g., `agent SectionsDemo:`), nested by indentation (Python-style). This implies you’ll want first-class support for emitting `INDENT`/`DEDENT` tokens (or an equivalent mechanism), because indentation is context-sensitive rather than purely context-free. citeturn8view0

Two “statement kinds” inside a block: key/value declarations like `role: "..."` and `workflow:` (mapping-like), plus “bare string statements” like `"Follow the steps below in order."` that behave like a docstring or a block description. That docstring-like pattern is extremely similar to how Python treats a leading string literal in a suite (module/class/function) as a docstring, which is relevant when considering “reuse Python’s parser” approaches. citeturn2search0

A likely need for a compiler pipeline that does more than parsing: after building a tree, you’ll want validation (e.g., required fields like `role`, uniqueness of step names, allowed nesting) and code generation (compile to Markdown prompts, compile to a normalized canonical format, or both).

Given those constraints, the best “don’t start from scratch” options tend to fall into two big strategies:

Use an existing mature language and parser (often Python itself), then compile from that AST/CST.

Use a proven parsing toolkit that already solved indentation and tree building (and then you only define the grammar + transformation).

## Fastest path: make it valid Python and reuse Python’s AST/CST ecosystem

If you’re willing to slightly adjust surface syntax (or add a lightweight preprocessor), you can make your DSL parseable by the standard Python toolchain and immediately inherit decades of battle-testing.

### Python `ast` for an automatically-tested parser front-end

Python’s standard library `ast` module exists specifically to parse Python source into an abstract syntax tree and to help applications process the Python abstract syntax grammar; it also notes that the AST may change with Python releases, but it provides programmatic access to the grammar and parse output. citeturn2search0

A practical pattern for your DSL is:

Represent blocks as `class` suites (nested classes are legal), represent key/value pairs as assignments, and represent your “bare string statement” as a docstring (a string literal expression at the top of a suite). Then you parse via `ast.parse` and compile by walking the AST.

For example, conceptually (not prescribing exact design), this is valid Python:

```python
class SectionsDemo:
    role = "You are the sections demonstration agent."

    class workflow:
        "Follow the steps below in order."

        class step_one:
            "Say hello."

        class step_two:
            "Say world."
```

Pros: extremely mature parser; excellent tooling; straightforward to get good errors; easy to distribute (stdlib). citeturn2search0  
Cons: you either change syntax (e.g., `agent` → `class`) or you write a very small syntactic desugaring step.

### LibCST when you need round-trip formatting or “pretty compile”

If “compiles to …” means you want stable formatting, preservation of comments/whitespace, or high-quality re-printing, a concrete syntax tree is often better than a lossy AST.

LibCST parses Python source into a CST that keeps formatting details like comments and whitespace, and it’s positioned for codemods/linters/refactoring. citeturn1search1turn1search5

This becomes attractive if you want:

A formatter / canonicalizer (“compile back to your DSL style”)

Auto-fixes (“rename step_two to stepTwo”, normalize quoting, etc.)

Precise source mapping for diagnostics

### Parso when you want error recovery and “editor-grade” parsing

Parso is a Python parser focused on error recovery and round-trip parsing across Python versions, and it’s described as battle-tested by Jedi. citeturn2search1turn2search5

This is useful if you expect users to write drafts of prompt DSL files and you want IDE-like handling: “show multiple syntax errors,” keep going after the first error, and support incremental editing workflows. citeturn2search1

## Best fit for your exact syntax: indentation-aware parsing toolkits in Python

If you want to keep your current surface syntax (including `agent Name:` and bare quoted-string statements), you’ll still need a grammar and a parser—but you can avoid reinventing lexing, indentation handling, parse tree building, and AST transformation.

### Lark for EBNF grammars + indentation tokens + automatic parse trees

Lark is a general-purpose Python parsing library that can parse context-free grammars and offers multiple parsing algorithms (Earley, LALR(1), CYK), with automatic tree construction inferred from your grammar. citeturn11search13turn0search8turn0search0

For indentation-sensitive languages, Lark has a documented approach: use an `Indenter` in a post-lexing stage to manufacture `INDENT`/`DEDENT` tokens—explicitly because indentation is context-sensitive. citeturn8view0

That maps very naturally to your DSL: every `header:` opens a suite; suite contents are either “docstring statements” or named sections/assignments.

Once you have a parse tree, Lark provides “Transformers & Visitors” as a standard way to process parse trees by implementing methods per grammar rule. citeturn11search1turn11search9

If you care about generating a normalized textual output, Lark even demonstrates reconstruction of code from a parse tree (noting it as experimental in their example), which is relevant if you want a canonical “compiled” format. citeturn11search0

Also, Lark can generate a standalone parser for distribution (useful if you don’t want to ship the full toolkit runtime everywhere). citeturn11search6turn11search2

When Lark tends to be the best choice: your syntax is custom, indentation is meaningful, and you want a well-documented Python-native toolkit with a clear grammar file and a predictable tree-to-AST transform.

### Pyparsing for grammar-in-Python + an explicit IndentedBlock

Pyparsing is a long-running Python library for building PEG parsers by composing grammar elements directly in Python code (rather than writing yacc/lex specs). citeturn1search2turn1search6turn4search5

Critically for your use case, pyparsing provides an `IndentedBlock` class meant for parsing texts where structure is implied by indentation, “like Python source code.” citeturn7view0

So you can model:

`agent NAME:` as a “headline” expression followed by `IndentedBlock(body_stmt)`

`body_stmt` as a choice between `assignment_stmt`, `section_stmt`, and `docstring_stmt`

If you already prefer writing grammars as Python objects and want tight control over parse actions that directly construct AST nodes, pyparsing is often ergonomic. citeturn4search5turn7view0

## Industrial-grade generators and DSL workbenches

These tools can be great if you want a more “compiler toolchain” feel, multi-language support, or an ecosystem around DSLs.

### ANTLR4 for a broad ecosystem and multi-language targets

ANTLR4 is a well-known parser generator: from a grammar definition, it generates a parser that can build parse trees, and also generates listener interfaces or visitors to process recognized phrases. citeturn14search2turn14search11

It supports multiple target languages (including Python3), which matters if you think your agent tooling may expand beyond Python later. citeturn14search2

For the Python target specifically, the official docs show the basic setup: write a `.g4` grammar, generate parser code via the `antlr4` tool, and use the Python runtime (`antlr4-python3-runtime`). They also emphasize that the tool version and the runtime version should match. citeturn9view0turn14search3

ANTLR also has a large public repository of grammars for many languages and formats (grammars-v4), which can help if you embed or reuse existing syntaxes. citeturn11search3

Tradeoff to understand up front: indentation-based languages typically require an indentation strategy (manufacturing indentation tokens and/or preprocessing), because indentation is context-sensitive. Lark’s documentation articulates this general issue clearly (the need to manufacture `INDENT`/`DEDENT` tokens). citeturn8view0

When ANTLR tends to be the best choice: you want a more “enterprise compiler” workflow (separate grammar → generated code), you might want non-Python tooling later, and you value the listener/visitor patterns and surrounding ecosystem. citeturn14search2turn9view0

### textX for “DSL as a product,” including meta-models and language tooling

textX is positioned as a meta-language for building DSLs in Python; from one grammar description, it builds both a parser and a meta-model (abstract syntax) for the language. citeturn0search2turn0search10turn12search4

Unlike many pure parsing libraries, textX emphasizes higher-level DSL ergonomics:

It can build a graph of Python objects corresponding to your meta-model. citeturn0search10turn12search4

It advertises features like automatic linking (resolving textual references to object references) and automatic parent/child relationships imposed by the grammar. citeturn12search0

It gives parser controls including whitespace handling configuration (skipws, redefining whitespace). citeturn12search1turn12search8

If you want editor support early, textX explicitly points to textX-LS (Language Server Protocol + VS Code support) and generators for syntax highlighting / VS Code extensions. citeturn15search8turn15search0

textX is built on Arpeggio, a PEG/packrat parser (recursive descent with memoization). citeturn12search2turn3search1turn12search14

When textX tends to be the best choice: you want a “language workbench” flavor—parser + object model + validation hooks + tooling—and your syntax is sufficiently regular that you can describe it cleanly in the textX grammar style. citeturn0search10turn12search0turn15search0

### TatSu for PEG grammars with AST generation and optional codegen

TatSu generates Python parsers from grammars and can compile a grammar into an object you use to parse inputs—also able to generate a Python module implementing the parser. citeturn0search7turn0search15turn0search3

It supports left-recursive rules in PEG grammars (with the expected left associativity in generated ASTs), which can matter if you add expression syntax later. citeturn0search3turn0search7

One practical consideration: current TatSu docs note compatibility expectations around newer Python versions (it expects a “maintained version” of Python >= 3.13, while tests run down to 3.12, and it points older users to TatSu-LTS). citeturn0search3turn0search11

When TatSu tends to be the best choice: you like PEG grammars and want a “grammar in, parser out” experience in Python, and your runtime Python version aligns with the project’s support policy. citeturn0search7turn0search11

### Pegen (CPython’s PEG generator) if you want “Python’s parser style,” but for your DSL

Pegen is described as the PEG parser generator used in CPython to produce the parser used by the Python interpreter, and it’s distributed as an installable package. citeturn10search1turn10search3turn10search10

If you like the idea of writing a PEG grammar in a toolchain closely aligned with Python’s own parsing evolution (see PEP 617’s switch to a PEG-based parser), Pegen can be appealing. citeturn10search2turn10search1

That said, compared to Lark/ANTLR/textX, Pegen is more niche as a general DSL ecosystem; it’s best viewed as “use Python’s own style of parser generation,” not as the most batteries-included DSL product. citeturn10search1turn10search3

## Incremental parsing and editor-first tooling

If you expect users to write these prompt DSL files interactively and you want great editor experiences (syntax highlighting, incremental reparse, structural queries), incremental parsers are worth considering—even if you still compile with a separate AST later.

### Tree-sitter for fast incremental concrete syntax trees + highlighting queries

Tree-sitter is both a parser generator and an incremental parsing library; it builds a concrete syntax tree and can efficiently update it as the source is edited. citeturn1search8turn1search0

It also provides a syntax highlighting system based on pattern-matching queries over the parsed syntax tree. citeturn15search2turn15search10

When Tree-sitter tends to be the best choice: you want editor integration (Neovim/Helix/etc.), incremental parsing for interactive experiences, and a CST you can query for structural tooling—then separate compilation for semantics. citeturn1search8turn15search2

### Lezer for a JavaScript/CodeMirror ecosystem

Lezer is a parser generator that outputs JavaScript modules and is described as especially well-suited for use in code editors (it produces a non-abstract syntax tree designed for tooling). citeturn3search3turn3search7

When Lezer tends to be the best choice: your authoring environment is CodeMirror/JS-first and you want a native editor parsing pipeline. citeturn3search3

## Supporting projects for “compile to Markdown prompts” and semantic validation

Even if you choose a parser toolkit, you’ll still benefit from proven libraries for the rest of the pipeline: schema validation, prompt rendering, and (optionally) Markdown parsing/inspection.

### Validation and schema: Pydantic

Pydantic is positioned around data validation using Python type hints, with schema validation and serialization controlled by type annotations. citeturn13search0

A common pattern is: parse → build a raw AST/object model → validate into a typed model (AgentSpec, WorkflowSpec, StepSpec) → compile/render. Pydantic helps you centralize constraints (required fields, field types, allowed unions, custom validators) and produce high-quality error messages. citeturn13search0

### Rendering: Jinja for Markdown generation

Jinja is a templating engine designed to render documents from templates with placeholder expressions and Python-like control structures. citeturn13search1

For compilation, this can give you a clean separation:

Your DSL AST is the “data model”

Your Markdown prompt structure is the “template”

That separation tends to keep your compiler simpler (fewer string concatenation edge cases). citeturn13search1

### Markdown parsing (optional): markdown-it-py or Mistune for output verification

If part of “compile” is guaranteeing that emitted prompts are valid Markdown (or extracting sections, headings, code blocks, etc.), it can help to parse the generated Markdown as a sanity check.

markdown-it-py follows the CommonMark spec for baseline parsing and is built to be configurable/pluggable. citeturn13search6turn13search2  
Mistune is a “fast yet powerful” Markdown parser with renderers and plugins. citeturn13search3turn13search7turn13search11

## Comparative shortlist of the most practical options

| Option | Best when | Indentation support | Tree type | Evidence of maturity / ecosystem |
|---|---|---|---|---|
| Python `ast` (+ small desugaring) | You can accept “Python as DSL” or rewrite `agent`→`class` | Native (Python syntax) | AST | Standard library AST tooling for Python grammar processing citeturn2search0 |
| LibCST (Python-syntax DSL) | You need formatting-preserving round-trip and codemods | Native (Python syntax) | CST | Parses Python while keeping formatting details citeturn1search1turn1search5 |
| Lark | Your current syntax stays; you want grammar files + indentation tokens | Yes via `Indenter` emitting INDENT/DEDENT citeturn8view0 | Parse tree → AST via Transformer/Visitor citeturn11search1 | Context-free grammars; multiple parsers; tree construction; standalone parser option citeturn11search13turn11search6turn11search2 |
| pyparsing | You want grammars as Python code + parse actions; moderate complexity syntax | Yes via `IndentedBlock` citeturn7view0 | Parse results → AST | PEG-based approach; long-lived project; explicit indentation construct citeturn1search2turn7view0 |
| ANTLR4 | You want industrial parser gen and multi-language targets | Not automatic; typically needs an indentation strategy (INDENT/DEDENT-like) citeturn8view0 | Parse tree + listeners/visitors citeturn14search2turn9view0 | Strong ecosystem; grammar repo; Python runtime; version-matching guidance citeturn11search3turn9view0turn14search3 |
| textX | You want DSL “workbench” features (meta-model, linking, LSP tooling) | Possible but not its core selling point; whitespace configurable citeturn12search1turn12search8 | Object graph model (“meta-model”) citeturn0search10turn12search0 | Language server + VS Code tooling explicitly supported citeturn15search8turn15search0 |
| Tree-sitter | Editor-grade incremental parsing + highlighting | Depends on grammar; good for tooling | CST (incremental) citeturn1search8turn1search0 | Highlighting via tree queries citeturn15search2 |

## Recommendations tailored to your DSL

If your priority is “ship something solid quickly, keep my syntax, don’t build indentation parsing from scratch,” start by looking hardest at **Lark** and **pyparsing**:

Lark is purpose-built for “define grammar → get parse tree → transform to AST,” and it has a documented `Indenter` approach that explicitly manufactures `INDENT`/`DEDENT` in a post-lex stage for whitespace-significant syntax. citeturn8view0turn11search13turn11search1

pyparsing is attractive if you prefer an all-Python embedded grammar and want to lean on parse actions; it directly documents `IndentedBlock` for indentation-implied structure like Python. citeturn7view0turn1search2

If you can tolerate a syntax shift (or preprocessor) and want maximum test coverage and long-term stability, strongly consider “Python-syntax DSL”:

Use Python `ast` as the front-end if you only need semantic compilation. citeturn2search0

Use LibCST if you need canonical formatting, source mapping, or refactoring/auto-fix workflows. citeturn1search1turn1search5

If you foresee needing a full DSL product experience (validation hooks, object graph, editor tooling), **textX** becomes compelling, especially since it explicitly points to LSP/VS Code support via textX-LS and generators. citeturn12search0turn15search8turn15search0

If you want a classic compiler-generator workflow with strong cross-language possibilities, **ANTLR4** is the heavyweight option—just go in expecting to implement an indentation strategy because indentation is context-sensitive. citeturn14search2turn8view0turn9view0
