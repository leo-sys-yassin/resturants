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

## Navigation follow-up

The editor document starts cloaked, and the parent keeps the iframe hidden behind
a loading status until the editor or sign-in surface is ready. A 20-second
loading fallback offers Retry and Return. View menu closes only the editor
dialog, previews the current saved draft in the same iframe, and retains the
owner session. Back to editor reopens it without a draft reload. Back to admin
workspace is a separate command and respects unsaved-change confirmation.
Browser regression covers delayed draft responses, loading visibility, edited
draft preview, editor reopen, rejected/accepted discard and workspace return.

## Sidebar, table menu and public feedback

The owner primary navigation is Edit menu / Team / Tables. Profile, settings,
history, feedback and sign out live in the account sidebar, which shows the
name, username and role. It is persistent at >=1100px and a native modal drawer
on smaller screens. Settings no longer repeat profile/team shortcuts.
Table ordering uses searchable category/product cards with images, prices,
quantity, modifiers and notes; a separate basket requires an explicit server
save. The first EMBER server draft was initialized with the adopted 61-item
menu using INSERT ON CONFLICT DO NOTHING (no draft overwrite). This is a demo
restaurant catalog, not imported real restaurant inventory.
The public customer menu has a Feedback dialog posting validated stars/comments
to restaurant-service /menu-feedback. Its new menu_feedback table has RLS and
no browser grants. Only the owner inbox reads it, alongside labeled per-table
feedback. Anonymous feedback uses per-client and IP rate gates.
restaurant-service v4 includes these endpoints (health table-service-v3).
Frontend regression covers slow editor initialization, draft preview/return,
discard confirmation, sidebar/mobile layouts, card search/category filters,
modifiers, saved table baskets, and customer feedback reaching the owner inbox
using shared mocked transport. Database insert/privilege checks use rolled-back
fixtures. Firebase still requires deployment through the authenticated user
Cloud Shell; repository pushes only auto-deploy Cloudflare.
