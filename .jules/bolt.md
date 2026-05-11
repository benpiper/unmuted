## 2024-04-26 - Optimize timestamp parsing in React video playback
**Learning:** React components executing inside high-frequency event handlers (like `<video onTimeUpdate>`) can suffer significant overhead from redundant string processing (like parsing timestamps `.split(':')`).
**Action:** Use `React.useMemo` to pre-calculate and cache derived data (like parsed timestamps) so that high-frequency handlers only perform fast numerical lookups.

## 2024-04-29 - SQLite/SQLAlchemy foreign key indexing
**Learning:** SQLite/SQLAlchemy does not auto-index foreign keys by default. Without an explicit index, reverse lookups (e.g., finding all projects for a given user or all segments for a given project) will cause a full table scan, degrading from O(1) to O(N) performance.
**Action:** Always add `index=True` explicitly when defining `ForeignKey` columns in SQLAlchemy models to optimize relational queries and cascading deletes.

## 2024-05-12 - SQLAlchemy bulk inserts over sequential adds
**Learning:** In SQLAlchemy, `Session.add_all()` and looped `Session.add()` incur significant ORM overhead and generate separate database operations.
**Action:** Always use `await db.execute(insert(Model), list_of_mappings)` for true bulk inserts to drastically reduce database round-trips and ORM overhead. Ensure the mapping list is not empty before executing.
