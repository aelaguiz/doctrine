# Skill Inventory

| Skill | Package | Purpose |
| --- | --- | --- |
| Author Skill | `author-package` | Own the first draft. |
| Review Skill | `review-package` | Review the draft. |

## Relations

| Source | Kind | Target | Why |
| --- | --- | --- | --- |
| `AuthorSkill` | `requires` | `ReviewSkill` | Review uses review-package. |
