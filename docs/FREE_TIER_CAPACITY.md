# Free tier capacity planning — verified 2026-11-04

Status: Supabase schema and owner membership exist. Public frontend, R2 bucket/domain and management Worker are not deployed/configured yet. This is a planning model, not a measured production capacity guarantee.

Architecture: public visitors read versioned JSON and images from CDN/R2. Supabase serves administrator authentication and drafts only. Never count anonymous menu visitors as Auth monthly active users. All included quotas are shared by their applicable account/project, not reset per restaurant.

Current provider limits:
- R2 Standard: 10 GB-month storage, 1 million Class A operations/month, 10 million Class B reads/month, no internet egress charge. Exceeding included usage can incur charges; this is not a hard free-only spending cap. Production should use a cached custom domain, not r2.dev.
- Workers Free: 100,000 dynamic requests/day, 10 ms CPU/invocation. Admin API only; do not proxy every public image through this Worker.
- Supabase Free: 500 MB database, 5 GB egress plus 5 GB cached egress, 1 GB Storage; 50,000 Auth MAU. Inactivity can pause a project after one week. Public cached reads do not keep the admin database active.

Planning example: 500 visits/day = 15,000 visits per 30-day month. At 40 uncached R2 object reads/visit, 600,000 reads/month. At 100 reads/visit, 1.5 million reads/month. Five such restaurants consume 3–7.5 million reads before retries/bots, above which headroom becomes material. Ten million / 40 = 250,000 visits is only a read-quota calculation, not promised capacity. Count CDN cache misses only where requests are actually served from cache; measure first.

Initial commercial target: one restaurant at 15,000 visits/month. Initially onboard 3–5 restaurants on the shared stack after load and usage verification; do not promise unlimited visits or sell all theoretical quota. Bursts, bot activity, devices and page weight require separate tests.

Content requirements: blank restaurant catalog at onboarding, arbitrary uploaded dish photos, no sample dishes automatically published. Target 100–300 KB optimized dish images, responsive/lazy delivery, 100 images roughly 10–30 MB before retained originals/versions. Current browser upload resizes to 1100 px but permits about 1.5 MB per image: it does NOT yet enforce this target or a tenant storage quota. Empty catalog/first-publish flow still needs verification (current API requires at least one category).

Before paid customers: implement tenant storage/item quotas, compressed-photo byte target, safe cleanup of unreferenced assets and old snapshots, usage thresholds (e.g. 60/80%), last-published offline/CDN fallback, custom SMTP and password recovery flow, backups, load tests and cost/overage policy. No guarantee that a provider's free service never pauses/fails.

Sources:
https://developers.cloudflare.com/r2/pricing/
https://developers.cloudflare.com/workers/platform/pricing/
https://supabase.com/pricing

## New waiter/table service scope

Public customer baskets remain entirely in-memory, so quantity changes create no database writes. Staff table sessions are different: an illustrative 500 parties/day × (one open + eight consolidated saves + one close) is 5,000 write operations/day, roughly 150,000/month, plus dashboard reads. This is only workload arithmetic, not throughput certification. Avoid persisting on every keystroke or every customer click; combine meaningful staff edits with explicit save and conflict checks.

If a retained closed-session snapshot averages 5 KB, 15,000 sessions/month occupy roughly 75 MB of payload, before row/index/TOAST overhead, backups and feedback. At 20 KB that becomes 300 MB/month. Therefore the 500 MB free database cannot retain unlimited order history. Define retention/export policy before rollout and measure actual pg_total_relation_size. Do not silently delete closed sessions or promise static-menu quotas cover this expanded system. Closed-table history, private feedback and staff access also require separate RLS and abuse tests.

Current code now has independent contactVisibility booleans. Empty contacts do not render. Hidden links remain in private drafts, while the publication projection clears their values so visitor JSON does not disclose them. This is independent of login/table-service quotas.

The implemented staff API now runs on Supabase Edge Functions, not the menu publishing Worker. Verify the project's included Edge invocation quota before onboarding customers. Count staff API requests separately; 5,000 saves/actions a day alone is 150,000 monthly function calls per restaurant, before logins/state/catalog/history reads. The earlier 3–5 restaurant static-menu target does not certify this new interactive workload.
