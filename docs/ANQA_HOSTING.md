# ANQA stable hosted website

The live host is Sites: https://anqa-atelier-yassin.salehchat5.chatgpt.site . GitHub Pages activation was unavailable to the connected GitHub integration (HTTP 403); do not report a github.io URL as live.

- Persistent project ID: `appgprj_6af757df499c8191944011dcf750ab4d`.
- Checkout: `/workspace/sites/anqa-atelier`.
- Hosting manifest: `.openai/hosting.json`, static directory `dist`.
- Current audience: owner-private. Preserve it unless the user explicitly requests another audience.

To update the same hosted URL:

1. Build and test the latest local ANQA project.
2. Run `python scripts/publish_anqa.py --source /path/to/current/anqa-project`.
3. Synchronize `docs/anqa/` into the existing Site checkout's `dist/` directory, preserving hashed assets for already-open sessions.
4. Follow the Sites skill to push the exact source, package `.openai/hosting.json` plus `dist/`, save a new version, and deploy the same project ID. Do not create another Site or change its slug.
5. Confirm the native deployment status and return its literal production URL.

`boot.js` reads `version.json` without a browser cache on every visit. The manifest supplies the current body markup, scripts, styles and assets; content-hashed files allow unchanged assets to remain cached. No service worker pins an old application version. Downloadable ZIPs remain separate backups.
