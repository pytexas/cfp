# Lessons Learned

## Recent
<!-- 10 most recent lessons, newest first -->
- Django's `UniqueConstraint(nulls_distinct=False)` is PostgreSQL-only; enforce the rule in `clean()` for SQLite dev/test and vendor-guard the DB constraint migration (2026-07-04)
- Pass file storage paths, never file bytes, through Temporal workflow inputs — payload limits and history bloat (2026-07-04)
- Use update-with-start for the lifecycle transition service so seeded rows and completed workflows self-heal without special-casing (2026-07-04)
- When applying `/bpe:review` feedback, read comments on `ship` decisions too — reviewers resolve open questions there without changing the verdict (2026-07-04)
- Regenerate plan.md/todo.md in the same session as any spec change; the old plan had silently drifted from the hardened spec (transition undo paths, bulk semantics) (2026-07-04)
- `mktemp` pre-creates the file, so Claude Code's Write tool requires a Read of the empty temp file first (2026-07-04)

## Temporal
- Pass file storage paths, never file bytes, through Temporal workflow inputs — payload limits and history bloat (2026-07-04)
- Use update-with-start for the lifecycle transition service so seeded rows and completed workflows self-heal without special-casing (2026-07-04)
- Workflow Update validators are the right primitive for a normative transition table: rejected updates never enter history and the caller gets the error synchronously (2026-07-04)

## Django
- Django's `UniqueConstraint(nulls_distinct=False)` is PostgreSQL-only; enforce the rule in `clean()` for SQLite dev/test and vendor-guard the DB constraint migration (2026-07-04)

## Workflow
- When applying `/bpe:review` feedback, read comments on `ship` decisions too — reviewers resolve open questions there without changing the verdict (2026-07-04)
- Regenerate plan.md/todo.md in the same session as any spec change; the old plan had silently drifted from the hardened spec (2026-07-04)

## Tooling
- `mktemp` pre-creates the file, so Claude Code's Write tool requires a Read of the empty temp file first (2026-07-04)
