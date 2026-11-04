# Workspace latency changes

## Frontend

- Sign-in and Refresh use one `/bootstrap` request, not serial state/catalog/profile
  requests. The response is still scoped to the verified current member.
- Overview uses the bootstrap statistics immediately. Feedback and compact history
  are prefetched after owner sign-in without blocking the first render.
- Read-only section data is cached only in memory: feedback freshness is 3 seconds,
  statistics/history 10 seconds. Stale data remains visible while revalidation runs.
  Last-update/error status distinguishes saved data from a successful refresh.
- Concurrent duplicate reads are deduplicated. Mutations invalidate freshness and
  version pending reads. Logout, auth failures and account changes clear all private
  cache state; epoch guards reject responses belonging to previous sessions.
- Refresh disables only its own button, leaving navigation usable.
- The redundant read-only Profile page/navigation button is removed. Identity,
  role and day statistics are in the account sidebar; team statistics stay in Team.
- Customer feedback uses a CORS simple text/plain JSON body, preconnect and a stable
  submission UUID for retries. Editing a failed submission creates a new UUID.
  Inputs freeze while sending. Success still requires a server acknowledgement.

## Server and database

- Auth user verification and active tenant membership are checked on each request;
  no authorization decisions are cached. Membership and actor rate gates run in
  parallel; independent bootstrap/table/catalog/statistics reads run in parallel.
- Public menu and signed table feedback each use one service-only database RPC for
  validation, rate gates and the write, rather than multiple serial REST calls.
  Retry idempotency prevents duplicate entries; signed feedback still verifies the
  HMAC before calling the database and preserves its 24-hour expiry.
- The owner inbox combines bounded recent menu/table feedback in one SQL query.
- `/history-summary` returns per-account totals rather than all basket lines and
  notes. The legacy `/history` route keeps its shape for older deployed frontends.
- Daily statistics restrict the intermediate data to today's closed accounts and
  currently open tables. Existing recent-history indexes plus a new open-account
  index avoid scanning/copying old basket data for each daily summary.
- RPCs use SECURITY INVOKER, explicit service_role-only execution and tenant/owner
  checks. Browser roles retain no direct feedback table privileges.

Apply schema.sql, table-service.sql, profile-stats.sql, menu-feedback.sql, then
workspace-performance.sql when provisioning a new environment.

## Verification and deployment

- Backend tests: 15 checks including identity, role changes, rate limits, bootstrap
  parallelism, one-RPC feedback and backward-compatible history.
- SQL tests use rolled-back fixtures and verify idempotency, changed-content
  protection, rate limits, tenant/role scope, compact totals and browser denial.
- With artificial 900 ms network delays, cached section navigation took about
  40–65 ms locally. This is a controlled browser test, not a live Internet SLA.
- A simulated 100 ms database hop produced one-hop feedback completion in about
  101 ms; production mobile/network/cold-start latency can differ.
- Browser regressions cover stale-data errors, old responses after logout, editor
  navigation, table options/basket saves and feedback delivery/retries.
- Deployed Edge Function: restaurant-service version 5; health table-service-v4.
  Frontend build marker: workspace-speed-20261104-v15.
- GitHub pushes auto-deploy the existing Cloudflare preview. They do not update
  Firebase Hosting; the Firebase deployment must use its authenticated Cloud Shell.
