# Candidate Tests

## Good Doctrine Pressures

| Source signal | Doctrine example or diagnostic idea | Why it matters |
| --- | --- | --- |
| Root catalog of many rule packs | Example of a root instruction file that points to scoped child rule files | Exercises scope hierarchy and repository-level instruction discovery |
| Explicit `globs` metadata on a child rule | Diagnostic or example for a rule that should only apply under a path boundary | Tests path scoping and prevents overbroad application |
| `alwaysApply` versus path-limited files | Example showing a universal rule and a directory-specific override | Pressures precedence and inheritance semantics |
| Unit test requirement in a narrow file scope | Example where a change must trigger tests before completion | Useful for command-first or quality-gate doctrine surfaces |
| Early-return and conditional-style guidance | Example that distinguishes a preference from a hard constraint | Helps Doctrine separate soft guidance from fail-loud rules |

## Proposed Doctrine Example Ideas

1. Root catalog plus scoped child rule.
   - Model the root README as a global index and the child `.mdc` file as the only active rule under a path prefix.

2. File-bound App Router rule.
   - Show a path-scoped instruction that applies only to `app/**` and rejects files outside that tree.

3. Quality-gate rule for tests.
   - Add a Doctrine example where a narrow rule requires unit tests for touched test files and emits a clear failure when omitted.

4. Style preference as a low-severity rule.
   - Capture early returns or conditional-class preference as a rule that should guide output without pretending to be a semantic contract.

5. Framework-specific package README as instruction packaging.
   - Use the package README to test whether Doctrine can separate stack description from the actual executable rule fragments.

## Keep Out

- Do not copy the repo's app-stack marketing language into Doctrine examples.
- Do not turn the catalog itself into a Doctrine truth source.
- Do not collapse scoped and global instructions into one generic rule unless the example is explicitly about precedence.
