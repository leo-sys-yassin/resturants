# ANQA stable website

The hosted showroom is published from `docs/anqa/` to the fixed `/resturants/anqa/` URL using GitHub Pages.

To update it from the latest verified local project:

1. Build and test the local project as usual.
2. Run `python scripts/publish_anqa.py --source /path/to/current/anqa-project`.
3. Commit the changed `docs/anqa/` files and push `main`.
4. Confirm the GitHub Pages deployment and test the stable URL.

`boot.js` reads `version.json` without a browser cache on each visit. Scripts, styles, fonts and assets have content-hashed filenames; unchanged binaries are reused by the browser. Old hashed assets are retained for already open sessions. This avoids shipping the monolithic downloadable HTML on the live site while keeping the existing scene and interactions.

The downloadable ZIP versions remain separate backups. Local cart storage remains under the same key for subsequent hosted updates. No service worker pins an old application version.
