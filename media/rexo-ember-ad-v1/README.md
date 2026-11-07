# Rexo × EMBER — silent motion ad v1

53-second portrait video, 1080 × 1920, 30 fps, with no audio. It follows the established Rexo green, beige and charcoal identity, with the actual EMBER interface and food assets from the user's repository. The original Rexo vector logo is retained. Narration is supplied separately in Arabic, with optional ElevenLabs performance tags and a clean speech-only version.

## Rebuild
Install Python 3, FFmpeg, Pillow with libraqm, NumPy, CairoSVG. Run `python render.py`. Assets and interface captures are included, so rebuilding the video requires no web service. Run `python render.py --preview` for a contact sheet. `base.py`, `render_v2.py` and `logo-paths.json` provide the existing Rexo typography helpers and original vector logo. Only their logo and drawing helpers are used by this renderer.

`capture.py` and `capture_extra.py` document capture provenance. To recapture, install Playwright, provide Chromium at `/usr/bin/chromium`, serve the restaurant repository at `http://127.0.0.1:8876`, then run them. Captures use the self-contained `offline-menu.html` last changed at commit `de6450b`. Product assets come from `web/assets/plated/`. Latest restaurant source at production time is `a204503`; the ad demonstrates customer-facing menu interactions shared with the standalone preview, not the newer staff dashboard.

## Story and timing
The opening establishes that food presentation shapes the first impression. Rexo introduces EMBER as a sample menu. Actual captures demonstrate scrolling, categories, details, available add-ons, quantity/total changes and Arabic/English switching. The close invites restaurant owners to contact @rexo.web.

`timeline.json` records estimated visual beats. These are provisional, not measured speech alignment. Final voice should be exported as one natural-speed recording; re-time graphics to the supplied audio rather than changing voice speed. The silent video is complete as a first review draft, not a final synchronized audio edition.

## Accuracy
The showcased menu is a demonstration. The cart is a local preview and does not submit an order or process payments. No fabricated dashboard, sales metric, guaranteed conversion improvement, or live ordering integration appears in the ad. Prices and images are examples from the supplied menu. Existing cart demo labels remain visible.

## Visual direction
Large Arabic kinetic typography, purposeful product reveals, original logo assembly and real interface captures. Cairo and Montserrat fonts, Rexo cream `#ece6d8`, green `#35564f` / `#1f7a68`, beige `#cbb5a0`, charcoal `#101516`. EMBER's orange is retained inside its actual product interface. Short decelerating entrances followed by readable holds; hard cuts for beat changes. No stock avatars, fabricated UI or generated food artwork. One claim leads per state. UI tap rings land on actual captured control positions.

## Review
Representative layouts, start/end states and UI interactions reviewed against original screenshots. Full encoded-file decoding and stream dimensions verified after export. Real-time audiovisual playback review unavailable; this version intentionally contains no audio. Font and icon licenses are in `assets/`.
