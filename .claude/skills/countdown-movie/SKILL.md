---
name: countdown-movie
description: Build a flashy self-contained HTML countdown/ranking reveal movie (vertical 9:16, kawaii/pop) from a data file, then export it to MP4 via Puppeteer + ffmpeg. Use when the user wants a ranking countdown video, a "TOP N reveal" movie, an awards/vote-result animation, a shorts-style data-driven reveal, or to record an HTML animation to MP4. Covers data→HTML build, image fetch+upscale, theming, sound effects (Web Audio), overlay video compositing, and silent-but-known recording caveats.
---

# Countdown / Ranking Reveal Movie Generator

A reusable pattern for **data-driven vertical reveal movies** (TOP-N countdowns, vote results, awards).
Reference implementation: BatoraRoom branch `claude/beautiful-brown-0065c1` (tag `sanrio-movie-v1`) —
`build_sanrio_movie.py`, `record_sanrio.mjs`, `make_overlay.mjs`. Read those for working code.

## When to use
Ranking countdowns, "TOP 20 reveal", vote/award result videos, shorts-style data reveals,
or any "record this HTML animation to MP4" task.

## Architecture (proven, recommended)
1. **Single Python builder** emits ONE self-contained HTML file: CSS + JS embedded as strings,
   data injected as JSON (`JS.replace("__DATA__", json.dumps(rows, ensure_ascii=False))`).
   Zero external deps → trivial to distribute, preview, and record. Image fallback to colored card.
2. **Step engine** in JS: `steps[]` = `op → (banner/char per rank) → ed`. Per-step weight `WT()`
   distributes runtime; RAF eases the headline number (vote count) with ease-out.
   A monotonic `gen` counter guards against seek/speed-change races (bump on every render;
   every deferred callback checks `if(myGen!==gen)return`).
3. **Suspense ("tame")**: silhouette the subject (`filter:brightness(0)` on a transparent PNG +
   a separate background layer — NOT darkening the whole card, which yields a black rectangle).
   Reveal hints one by one via CSS `animation-delay`; reveal the answer after the last hint + ~0.5s.
4. **Theming**: `#frame.theme-a/b/c` with CSS custom properties; switchable at runtime.
5. **Polish layers** (optional, all CSS/JS, no assets): radial burst on reveal, confetti,
   spotlight for top ranks, mascots/bokeh/shooting-stars environment, jelly-bounce typography.

## Build & preview
```bash
python3 build_<name>_movie.py                 # data(CSV) → <name>_movie.html
python3 -m http.server 8141                    # http://localhost:8141/<name>_movie.html
```

## Images (if subjects have art)
- Fetch → convert/upscale with macOS `sips`: `sips -s format png`, `sips -z H*2 W*2` for 2×.
- **Verify transparency**: a PNG's IHDR `color_type` (byte 25) must be `6` (RGBA) for silhouettes.
  `2` (RGB) has no alpha → silhouette becomes a filled box. Prefer the RGBA candidate.
- Keep a review page (current vs candidates A/B/C) with copy-paste replace commands.

## Sound (Web Audio, self-contained + free-asset override)
- Synthesize SE procedurally (oscillator + gain envelope): pop/ding/sparkle/fanfare/whoosh,
  a ticking roll during count, a heartbeat during suspense. Gate behind a user gesture
  (AudioContext starts suspended → `resume()` on first control click).
- File override: if `sounds/<name>.mp3` loads, play it instead of the synth
  (lets the user drop in 効果音ラボ / Pixabay / Mixkit clips). BGM via a looping `<audio>`.

## Overlay video (free-asset compositing)
- Overlay a `<video>` with `mix-blend-mode:screen`; black-background light footage shows only the light.
- Generate a license-clean default yourself: draw bokeh/sparkles on black in a canvas,
  record a short seamless loop, encode to mp4 (see `make_overlay.mjs`). Users swap in
  Pixabay/Mixkit/Pexels/Coverr clips by replacing `overlays/sparkle.(webm|mp4)`.

## Record to MP4 (Puppeteer + ffmpeg)
- **Why Puppeteer not Playwright**: on some macOS Python builds (3.12/3.14) `pyexpat` is broken,
  so `pip install playwright` fails. Node + Puppeteer sidesteps it. `ffmpeg` for encoding.
- **Match preview scale**: render at logical 540×960 with `deviceScaleFactor:2` → physical 1080×1920.
  This keeps container-query (`cqw`) sizing identical to the browser preview (otherwise content
  looks tiny in a 1080-wide viewport because px-capped cards shrink relatively).
- Capture via CDP `Page.startScreencast` (jpeg frames), build a concat list with per-frame
  `duration` (variable FPS), then `ffmpeg -f concat ... -vf fps=N -pix_fmt yuv420p`.
- Parameterize modes: speed (mult) × fps (30/60, via `everyNthFrame` 2/1). Hide controls/borders
  with an injected stylesheet; enable the overlay before recording so it lands in the MP4.
- **Caveat — screencast is video-only → the MP4 is SILENT.** SE/BGM are for live playback /
  screen capture. To bake audio in, mux a track afterward with ffmpeg (and align SE timings).

## Gotchas
- macOS `grep` mangles Japanese → use Python `str.count()`/`re` instead.
- Non-raw Python strings choke on `\u{...}` in the HTML template → write emoji literally.
- Overlay error handling: listen on the `<video>` element (no capture) — capture-phase catches
  per-`<source>` failures and misfires when the first source 404s before fallback.
- `.gitignore` the heavy recording outputs (`*_movie.mp4`, `node_modules/`, temp `.rec_*`/`.ov_*`),
  but DO commit the small generated overlay default so the build is reproducible.

## Copyright
If subjects use third-party IP (characters, logos), that art is copyrighted (fan use). Keeping the
surrounding SE/overlay assets license-clean does not change the image's status — flag it to the user.
