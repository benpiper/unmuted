## 2024-04-26 - Optimize timestamp parsing in React video playback
**Learning:** React components executing inside high-frequency event handlers (like `<video onTimeUpdate>`) can suffer significant overhead from redundant string processing (like parsing timestamps `.split(':')`).
**Action:** Use `React.useMemo` to pre-calculate and cache derived data (like parsed timestamps) so that high-frequency handlers only perform fast numerical lookups.

## 2024-04-29 - SQLite/SQLAlchemy foreign key indexing
**Learning:** SQLite/SQLAlchemy does not auto-index foreign keys by default. Without an explicit index, reverse lookups (e.g., finding all projects for a given user or all segments for a given project) will cause a full table scan, degrading from O(1) to O(N) performance.
**Action:** Always add `index=True` explicitly when defining `ForeignKey` columns in SQLAlchemy models to optimize relational queries and cascading deletes.

## 2024-05-15 - Optimize SQLAlchemy bulk inserts
**Learning:** In SQLAlchemy, iterating over a list and calling `db.add()` for each model instantiates individual ORM objects and tracks their state, which adds significant overhead and database round-trips.
**Action:** For performance-critical code inserting multiple records (like saving numerous transcript segments), use `await db.execute(insert(Model), list_of_mappings)` to perform a bulk insert, skipping ORM instantiation and executing a single query.

## 2024-05-20 - Cache external API clients across function calls
**Learning:** Instantiating new API clients (like `OpenAI()` or `ElevenLabs()`) inside frequently called functions (e.g., inside a loop during synthesis) destroys connection pooling. Each instantiation sets up a new HTTP session, adding significant overhead and slowing down requests.
**Action:** Cache API clients at the module level or within a singleton when they are designed for reuse, using lazy initialization to configure them only when needed.

## 2024-05-25 - Use binary search in high-frequency React event handlers
**Learning:** High-frequency event handlers (like `<video onTimeUpdate>`) that perform linear searches (O(N)) on large arrays can cause performance bottlenecks and block the main thread.
**Action:** Use binary search (O(log N)) when looking up values in large ordered arrays (like timestamps) within high-frequency event handlers.
