# Rexo — merged motion draft v2

66-second silent portrait video, 1080×1920, 30 fps. This combines the user's modern HTML concept with the earlier service animations.

From supplied HTML: idea/developer hook, staged conversation about fragmented implementation, bold kinetic typography, cream/dark/green scene palette, logo assembly, partner proposition, idea-to-launch journey and DM closing.
From previous video: responsive interface transformation, customized modules, order stages, automation and system integration demonstrations. Services are presented sequentially with their qualitative customer benefits.

The logo geometry and exact fills are extracted directly from the provided SVG path data (`logo-paths.json`). No generated logo is used. Interface drawings and chat are illustrative, not customer screenshots or testimonials. There are no quantified performance promises or unverified competitor rankings.

## Rebuild
Python with Pillow + libraqm, NumPy, CairoSVG and FFmpeg. Run `python render_v2.py --preview`, then `python render_v2.py`. `base.py` provides reusable composition helpers and the original service scenes. `reference.html` is the user's original unmodified reference file.

`delivery/Voiceover_AR_v2.txt` is the revised proposed narration. Timings are editorial estimates for silent review. Re-time the visuals to the user's future audio at natural speed.

Fonts: Cairo/Montserrat, OFL. Icons: Lucide, ISC. Licenses included. The original vector brand mark is supplied by the user.

QA: representative settled states and transitions inspected; full encode decoded; dimensions, frame count, duration and absence of audio checked. This is a review draft for creative feedback; platform UI safe areas are provisional.
