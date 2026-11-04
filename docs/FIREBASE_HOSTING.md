# EMBER Hosting handoff

Requested public URL: https://ember.web.app/ (not reserved or verified yet).
Team URL after publishing: https://ember.web.app/staff.
Supabase project: sewhqpwncbfbtaswejoy. Existing restaurant ID and internal
slug stay intact; the public Hosting site name is independent of that slug.

## Before deployment

Connect the Firebase account, inspect its projects, and select/create a dedicated
restaurant project. Do not deploy to either REX project. Keep the free Spark plan;
this static site does not require App Hosting, Cloud Functions, Firestore or
Firebase Authentication. Check availability by creating Hosting site `ember` in
the intended project. If unavailable, ask for another site ID; do not claim it is
reserved based on a missing public page. Creating a new named site later does not
rename the original site or update printed QR codes.

From the repository root (public folder `web`; the authoring workspace uses
`dist`), after selecting the correct project and confirming the site is owned:

```sh
firebase hosting:sites:create ember --project RESTAURANT_PROJECT_ID
firebase target:apply hosting ember ember --project RESTAURANT_PROJECT_ID
firebase deploy --only hosting:ember --project RESTAURANT_PROJECT_ID
```

Skip site creation if the selected project already owns it. Never overwrite an
existing unrelated site. The explicit Hosting target prevents accidentally
publishing to a project's default site. No GitHub Actions are needed.

## Routes and verification

- `/`: customer menu, no authentication; basket is temporary.
- `/staff`: owner/waiter sign-in; real server permissions determine available actions.
- `/staff/`: directory alias; asset paths resolve from the root.
- `/service.html`: existing entry kept compatible.
- `/reset.html`: password recovery; add the exact deployed URL to Supabase Auth
  redirect allowlist and configure email delivery before claiming recovery works.
- Staff feedback links use `/staff?feedback=...#...`.

Verify both entry routes on the live Firebase URL, sign in with actual owner and
waiter test accounts, verify that a waiter cannot access owner APIs, and only then
generate the printable customer QR code. Browser flow checks in the repository
use mocked transport and do not replace this live verification.

## Remaining service limitations

Firebase Hosting publishes static assets only. Real table service uses the
existing Supabase Edge Function. The menu editor still runs locally until the
menu publishing Worker and public image/manifest storage are configured. A new
Hosting URL alone does not enable cross-device menu editing or waiter catalog
seeding. Do not advertise that synchronization as complete.

Firebase bandwidth quotas differ from the earlier Cloudflare/R2 plan. Recalculate
hosting usage before commercial rollout; no paid upgrade is authorized here.
