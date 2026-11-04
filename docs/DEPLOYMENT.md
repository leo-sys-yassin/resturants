# Deployment checklist

## Current state
- Supabase project `Restaurants Menu`: schema, owner membership and table service applied.
- `restaurant-service` Edge Function deployed. Authentication is enforced in the handler; JWT gateway verification is off because `/login` and signed customer-feedback submissions are public endpoints.
- UI and Cloudflare management Worker are source files, not yet a verified public deployment.

## Frontend (Cloudflare Pages)
Connect this repository, select branch `main`, no build command, output directory `web`. The files are static. No GitHub Actions are required. `web/_redirects` supports `/r/<slug>`.

## Menu publishing (Cloudflare Worker + R2)
1. Enable R2 Standard and create a dedicated `restaurant-menu-assets` bucket. Included quotas are not a guaranteed spending cap; review billing before enabling.
2. Connect a production custom asset domain and configure CORS for the menu origin. The r2.dev testing URL is rate limited and is not the production target.
3. Deploy `backend/worker.mjs` with the example Wrangler settings. Set `SUPABASE_URL`, public `SUPABASE_PUBLISHABLE_KEY`, exact `ADMIN_ORIGIN`, and `ASSET_BASE`. Bind bucket as `MENU_ASSETS`. No service-role credential is needed in this Worker.
4. Fill `web/runtime-config.js` with `apiBase` (management Worker), `assetBase` (asset custom domain), existing public Supabase settings and restaurant ID. Never include service-role keys in this file.
5. Sign in to menu management, configure the restaurant, save the draft and publish. New customer restaurants start with an empty catalog; onboarding must create/assign their own restaurant and owner membership. Current demonstration content must not be auto-published to new tenants.
6. Verify anonymous QR reads, picture uploads, draft save, publish failure preserving old version, and all staff operations against real providers.

## Owner recovery email
Configure Supabase Auth Site URL and redirect allowlist for `https://YOUR-MENU-ORIGIN/reset.html`, disable unwanted public sign-ups/providers, and set custom SMTP before commercial use. Default Supabase mail is constrained and not a production delivery guarantee. Test a real recovery email and expired-token behavior. No password is provided in source files.

## Retention and quotas
Set tenant image/storage budgets and old-session retention/export policy, then measure database growth and R2 origin reads. 500 MB free database cannot retain unlimited session histories. Retention deletion is not automatic in this version; agree retention policy before deleting customer records. See FREE_TIER_CAPACITY.md.
