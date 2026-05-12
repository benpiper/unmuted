## 2024-04-26 - Optimize timestamp parsing in React video playback
**Learning:** React components executing inside high-frequency event handlers (like `<video onTimeUpdate>`) can suffer significant overhead from redundant string processing (like parsing timestamps `.split(':')`).
**Action:** Use `React.useMemo` to pre-calculate and cache derived data (like parsed timestamps) so that high-frequency handlers only perform fast numerical lookups.

## 2024-04-29 - SQLite/SQLAlchemy foreign key indexing
**Learning:** SQLite/SQLAlchemy does not auto-index foreign keys by default. Without an explicit index, reverse lookups (e.g., finding all projects for a given user or all segments for a given project) will cause a full table scan, degrading from O(1) to O(N) performance.
**Action:** Always add `index=True` explicitly when defining `ForeignKey` columns in SQLAlchemy models to optimize relational queries and cascading deletes.

## 2024-05-18 - SQLAlchemy bulk inserts via DB execution
**Learning:** In SQLAlchemy, sequential ORM insertions (like calling `db.add()` inside a loop for 1000s of items) is slow due to object instantiation and identity map overhead. `add_all()` is just a wrapper for `add()`.
**Action:** For performance-critical code inserting large amounts of records, bypass the ORM layer entirely and construct a list of mapping dictionaries, then use `await db.execute(insert(Model), list_of_dicts)` directly, ensuring the list is not empty first.
