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
## 2024-06-28 - Optimize array lookups in high-frequency React event handlers
**Learning:** Even if data is pre-processed/memoized (like cached `parsedTimestamps`), performing an O(N) linear search on that array inside a high-frequency event handler (like `<video onTimeUpdate>`, which fires multiple times per second) can cause UI stuttering for large arrays.
**Action:** When searching sorted arrays (like ordered video timestamps) in high-frequency event loops, replace linear iteration loops with an O(log N) binary search to minimize main thread blocking and ensure smooth UI execution.

## 2024-05-24 - Replace blocking time.sleep with asyncio.sleep in async FastAPI routes
**Learning:** FastAPI async routes must not use blocking I/O calls like `time.sleep()`. This completely blocks the main event loop, causing the entire application to hang and fail to process other concurrent requests.
**Action:** Always use `await asyncio.sleep()` in `async def` route handlers when waiting or polling, so the event loop can process other tasks.
