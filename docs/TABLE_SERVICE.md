# Table service requirements — 2026-11-04

Customer QR menu: anonymous, temporary in-memory basket; reload/navigation clears it. No order or payment submission. Public browsing must never create table sessions or assign waiters.

Separate authenticated staff workspace: owner manages menu, photos, prices, members and numbered tables. Waiter role cannot write menu drafts, publish content, edit members or configure tables. Its workspace exposes only assigned/current table service operations. Existing editor/viewer roles are not a substitute for waiter authorization.

Owner may create numbered tables in ranges (e.g. 1–45), rename/disable tables, and see current occupancy. Assignments must be server checked within the same restaurant. Claiming/opening a table is atomic, with at most one active service session per table, so two waiters cannot claim the same table at once. Reassignment is an explicit owner action.

A service session records table, assigned waiter, guest count, opening timestamp, status and closing timestamp using server time. Its basket persists in the backend across reload/login and is private to the assigned waiter and owner. Each line stores the selected product/option names and prices as a snapshot so menu edits do not silently change an existing bill. Saves use expected revisions and are atomic/idempotent to prevent duplicate or lost orders. Customer basket is not copied to staff or sent to the server automatically.

Waiter enters the customer's choices after looking at their screen. An explicit "Close account" confirmation closes the active session. Table becomes available with an empty basket for the next party, but past service data is retained separately for owner reporting; never destroy history to clear a table. This action records staff-reported closure; it is not payment processing or proof of bank settlement.

Feedback defaults to owner-only. Waiters cannot read customer feedback unless a future explicit visibility setting is approved. Public feedback submission requires a scoped session token and rate/spam controls; never grant anonymous table/order reads. Do not infer QR scan alone proves occupancy or legitimate feedback.

The implementation and verification status is described below; production end-to-end acceptance remains pending hosting/network setup.

Capacity impact: public visits remain CDN reads, but staff assignments, saves and account closure add database/API traffic. Recalculate quotas/retention before production; previous static-menu estimate is not a measured guarantee for this new module.

## Implemented table-service revision

Database migration `backend/table-service.sql` is applied to the dedicated project. Service-only mutations use SECURITY INVOKER functions whose EXECUTE is revoked from PUBLIC/anon/authenticated. Browser roles have no direct access to private service tables; authenticated HTTP handlers derive actor ID from a validated Supabase Auth session and check current tenant membership on every call.

`backend/service/index.mjs` implements username/password waiter login, owner-managed Auth waiter accounts, activation/deactivation, code resets with token cutoff, table configuration/claim/save/close/reassign, owner history and feedback. Waiter aliases are internal non-deliverable addresses; waiters need no personal email. Codes require at least 12 characters and are stored by Supabase Auth. The service-role key is used only inside Edge environment variables.

Customer feedback uses per-session HMAC links (24-hour expiry), rate limiting and one-feedback-per-session uniqueness. Feedback reads are owner-only. These links establish possession, not verified customer identity.

The frontend `dist/service.html` works on phone/tablet/desktop. Staff tokens are memory-only; reload requires sign-in again but saved table baskets survive in the database. Writes happen explicitly, not on every click. Refresh is manual. Close retains historical basket data and frees the table. Owner can reassign disabled waiters' tables.

Verification: live transactional SQL tests passed (fixtures rolled back); four service handler tests and a browser scenario with mocked transport passed. Supabase deployment reported the service ACTIVE, but live HTTP verification was blocked by this execution environment's destination policy. No claim of a complete real-browser authenticated production test.

Menu publishing/media hosting remain separate Cloudflare/R2 components requiring provider access. The catalog reads the saved menu draft; without a draft, the staff picker is empty. Do not populate new customer restaurants with demo dishes automatically. Public commercial launch is pending media/publishing setup, mail recovery configuration, data-retention policy and live end-to-end acceptance.
