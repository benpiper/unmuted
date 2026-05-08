## 2024-04-26 - Optimize timestamp parsing in React video playback
**Learning:** React components executing inside high-frequency event handlers (like `<video onTimeUpdate>`) can suffer significant overhead from redundant string processing (like parsing timestamps `.split(':')`).
**Action:** Use `React.useMemo` to pre-calculate and cache derived data (like parsed timestamps) so that high-frequency handlers only perform fast numerical lookups.

## 2024-04-29 - SQLite/SQLAlchemy foreign key indexing
**Learning:** SQLite/SQLAlchemy does not auto-index foreign keys by default. Without an explicit index, reverse lookups (e.g., finding all projects for a given user or all segments for a given project) will cause a full table scan, degrading from O(1) to O(N) performance.
**Action:** Always add `index=True` explicitly when defining `ForeignKey` columns in SQLAlchemy models to optimize relational queries and cascading deletes.

## 2024-05-15 - Optimize SQLAlchemy bulk insertions
**Learning:** In SQLAlchemy, repeated `Session.add()` calls inside a loop introduce significant ORM overhead and generate individual `INSERT` statements when committed, degrading performance for large payloads (e.g., long transcript segments). `Session.add_all()` is just a wrapper for `Session.add()` and suffers from the same issue.
**Action:** Use `await db.execute(insert(Model), list_of_mappings)` for true bulk insertions to bypass the ORM's per-object overhead and reduce database round-trips to a single query.
