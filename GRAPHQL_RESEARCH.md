# GraphQL Adoption Research for Unmuted

## 1. Current Architecture Overview

The "Unmuted" application currently employs a client-server architecture:
- **Backend:** Python-based RESTful API using FastAPI, SQLAlchemy for database operations (SQLite/PostgreSQL), and background tasks for heavy processing.
- **Frontend:** React-based Single Page Application (SPA) utilizing Vite, interacting with the backend via standard `fetch` API calls (`apiFetch` wrapper).

The core workflows involve:
- **Authentication:** Standard JWT-based auth.
- **Video Uploads:** Handling large binary files (MP4/MKV) via `multipart/form-data`.
- **RPC/Action-Oriented Endpoints:** Many endpoints execute actions rather than standard CRUD operations. Examples include `/api/project/extract`, `/api/project/identify-tools`, `/api/project/plan`, `/api/project/frame_candidates`, and `/api/project/synthesize`.
- **Long-Running Jobs:** Operations like frame extraction and auto-finishing are asynchronous. The client polls `/api/jobs/{job_id}/status` for progress updates.
- **Data Model:** Relatively shallow. The main entities are `User`, `Project`, `TranscriptSegment`, and `JobRecord`.

## 2. Evaluating GraphQL for this Project

### Pros of Adopting GraphQL
1. **Precise Data Fetching:** GraphQL prevents over-fetching and under-fetching. A client can query exactly what it needs for a specific view (e.g., fetching a project along with its segments and job statuses in a single query).
2. **Strong Typing and Introspection:** The schema acts as a strongly typed contract between the frontend and backend, enabling auto-generated types (e.g., using GraphQL Code Generator for React/TypeScript) and excellent developer tooling.
3. **Single Endpoint:** Simplifies client logic as all requests route through a single `/graphql` endpoint, instead of managing multiple REST paths.

### Cons and Challenges for this Specific Project
1. **RPC-Heavy Workflow:** GraphQL is fundamentally designed around querying and mutating a graph of data (CRUD). However, "Unmuted" relies heavily on RPC (Remote Procedure Call) operations (e.g., `extract`, `identify_tools`, `generate_plan`). While these can be modeled as GraphQL `Mutations`, it often feels less natural and can lead to a bloated mutation schema compared to semantic REST endpoints.
2. **File Uploads:** Handling large video files is a core feature of this app. Standard GraphQL does not natively support file uploads. While extensions like the `graphql-multipart-request-spec` exist, they add complexity and are generally less efficient and harder to debug than native FastAPI `UploadFile` REST endpoints.
3. **Shallow Data Graph:** The benefits of GraphQL shine brightest when dealing with highly connected, nested data structures. The "Unmuted" data model is relatively flat (Projects -> Segments/Jobs). REST is perfectly adequate for retrieving this data without significant N+1 query problems.
4. **Migration Overhead:** Replacing the existing, well-functioning FastAPI REST implementation and React `fetch` hooks with a GraphQL server (e.g., Strawberry or Graphene) and client (e.g., Apollo Client, URQL) would require significant engineering effort for minimal functional gain.
5. **Streaming/Progress Tracking:** Long-running jobs currently use simple REST polling. While GraphQL offers Subscriptions (via WebSockets) for real-time updates, implementing subscriptions is considerably more complex than the current polling or Server-Sent Events (SSE) approaches.

## 3. Conclusion

**Recommendation: Do not adopt GraphQL at this time.**

While GraphQL provides excellent developer experience and efficient data loading for data-heavy, deeply nested applications, it is not the right tool for "Unmuted".

The application's core complexity lies in file handling, long-running vision-language model (VLM) tasks, and orchestration of external processes (ffmpeg). Its data querying needs are simple. FastAPI's current REST implementation provides native, straightforward support for video file uploads, excellent integration with standard HTTP tools, and automatic interactive documentation (Swagger UI/OpenAPI) which is already typed via Pydantic models.

Introducing GraphQL would add unnecessary complexity, especially regarding file uploads and modeling RPC-style actions as mutations, without providing significant benefits to the frontend data fetching layer.
