# Database status — 4 November 2026

Dedicated project: Restaurants Menu (`sewhqpwncbfbtaswejoy`). Owner account is confirmed and assigned to EMBER Kitchen. Menu foundation plus waiter, table, session, feedback and rate-limit tables are applied. All application tables have RLS enabled; private service tables deny browser roles and mutations are service-only.

Live SQL tests passed for tenant isolation, draft revision conflicts, 45-table creation, assignment, occupied-table conflict, role restrictions, reassignment, disabled waiter rejection, close/history retention and an empty new session. Fixtures were rolled back.

The restaurant-service Edge Function is ACTIVE (version 2). Direct HTTP end-to-end verification remains blocked by the execution environment network policy. Menu management Worker, media storage and public UI hosting are pending Cloudflare setup. No REX resources were touched.

Security advisor: private service tables intentionally have explicit deny policies. Supabase reported leaked-password protection disabled; enable it if supported by the chosen plan. Reference: https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection
