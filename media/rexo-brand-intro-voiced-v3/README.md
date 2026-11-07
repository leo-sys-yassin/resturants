# Rexo — voice-synchronized edition v3

Portrait motion advertisement using the supplied ElevenLabs recording as the master clock. Audio remains complete at natural speed, with loudness normalization only. No music or synthesized replacement speech has been added.

The v2 art direction, original vector logo, service demonstrations and closing are retained. Scene starts and internal text reveals are tied to recognized speech cues. The opening chat is shortened to the three needs actually named by the narration. Authored graphics are retimed independently; the audio is not time-stretched.

## Rebuild
Python 3, Pillow with libraqm, NumPy, CairoSVG and FFmpeg. Run `python render_voiced.py`. Original `voice.mp3` and all required source assets are included. `render_v2.py` and `base.py` provide the previous silent visual scenes.

## Timing and review
`transcript.json` preserves automatic word alignment; `delivery/timeline.json` records the scene mapping. The SRT sidecar is for optional captions/editing, not burned into the video. Names and obvious ASR spelling errors are normalized against the supplied script. Technical checks cover full decoding, stream duration, audio offset/correlation and representative encoded frames. Direct listening review was unavailable.

Font and icon licenses are in assets. Logo paths come directly from the user-supplied HTML reference.
