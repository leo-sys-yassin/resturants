# Staff workspace update

- Owner overview: current occupancy, closed account counts and recorded account
  value for the Syria calendar day, plus seven-day count/value/visit charts.
- Owner and waiter profiles: display name, username and role. Owner email is
  visible only to the owner. Waiter synthetic Auth email is never displayed.
- Waiter statistics are restricted to assigned sessions. Owner sees team totals.
- Closed account values use server snapshots, not current prices. These figures
  are neither confirmed payment receipts nor profit.
- Aggregate visit counts start after deployment. The public client reports a
  successful page load once per browser tab session/day, respects Do Not Track,
  and does not report editor iframe loads or offline HTML. Counts are not unique
  people and can undercount blocked requests. Public visit events are rate limited.
- Profiles and all aggregates are protected by verified Edge Auth + membership.
  The aggregate tables/RPC are unavailable to anon and authenticated directly.
- Owner opens Menu Studio within the workspace; same-origin postMessage passes
  the in-memory token only to the specific iframe. No token is stored in URLs,
  localStorage, sessionStorage or cookies. The server verifies the owner again.
- Save uses the authenticated user's existing RLS/CAS draft RPC. Waiters cannot
  read or save drafts. Updates refresh the catalog on return to workspace.
- Public publication is still pending R2/management-worker setup. Draft saves
  do not update the anonymous Firebase menu. The editor states this explicitly
  and hides its unavailable Publish action.
- Draft body is capped at 2.5 MB. Large media catalogs need the planned object
  storage integration rather than increasing database payload limits.

Applied database migration: staff_profiles_daily_dashboard.
Deployed Edge Function: restaurant-service v3 (table-service-v2 health marker).
Local verification: tests/profile-stats.sql (rolled back fixtures),
profile-workspace.py (mocked browser transport), service-api.test.mjs and
backend.test.mjs. Actual Firebase deployment and real-account browser acceptance
must follow the repository update; Cloudflare auto-build does not update Firebase.
