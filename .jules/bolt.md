## 2024-04-26 - Optimize timestamp parsing in React video playback
**Learning:** React components executing inside high-frequency event handlers (like `<video onTimeUpdate>`) can suffer significant overhead from redundant string processing (like parsing timestamps `.split(':')`).
**Action:** Use `React.useMemo` to pre-calculate and cache derived data (like parsed timestamps) so that high-frequency handlers only perform fast numerical lookups.
