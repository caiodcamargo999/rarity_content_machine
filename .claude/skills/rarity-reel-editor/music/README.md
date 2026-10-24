# Music library for voiceover Reels

Source: Mixkit (mixkit.co/free-stock-music) — **Mixkit Stock Music Free License**: free for
commercial use and social media (Instagram, YouTube, ads), no attribution required (appreciated).
Not allowed: CDs/DVDs, games, TV/radio broadcast, or re-selling the track as music. Always keep the
track inside a finished video, never redistribute the raw mp3.

How these were chosen (2026-10): all 173 tracks from 12 Mixkit categories (corporate, technology,
hip-hop, tech-house, business, upbeat, motivational, electronica, chill, modern, beats, inspiring)
were downloaded and scored with librosa for voiceover suitability — tempo 100–120 BPM, low
loudness variance, warm-mid spectral centroid, moderate onset density, length ≥ 50 s, instrumental.

| File | Title / artist | Genre | BPM | Use for |
|---|---|---|---|---|
| `brainiac-167.mp3` | Brainiac — Alejandro Magaña | Electronica | ~117 | **Default.** Modern, pulsing, tech-forward; news/analysis/ecom data Reels. Start at ~4 s to skip the intro. |
| `infinity-440.mp3` | Infinity — Arulo | Corporate | ~112 | Clean, optimistic; client-win / how-to Reels. |
| `raising-me-higher-034.mp3` | Raising Me Higher — Ahjay Stelino | Corporate | ~112 | Building energy; motivational/founder story Reels. |
| `deep-house-196.mp3` | Deep House — Arulo | House (deep) | 123 | **Ads / talking-head edits when Caio asks for deep house.** Steady groove 18–50 s and 80–140 s, 157 s long; start at 18. |
| `deep-urban-623.mp3` | Deep Urban — Eugenio Mininni | House | ~123 | Faster, edgy; hot-take / contrarian Reels. 4:49 long — pick a `--music-start`. |

More candidates ranked in the same scan (all Mixkit): Spiritual Moment (525), Cyberpunk City (140),
Day Dreamin' with U (988), Kodama Night Town (114). To re-scan: download via
`https://assets.mixkit.co/music/<id>/<id>.mp3` (ids are in each category page's JSON-LD).

Mix levels live in `build_voiceover_reel.py` (`--music-lufs`, default -27 LUFS before ducking).

## Orchestral / epic (added 2026-10 — Caio: "the music is not nice, I want more orchestral, something that excites more; I can barely hear it")
All Mixkit (same free licence). Measured: share of energy at 300-3400 Hz (lower = more room for the voice).
| File | Title | Mid-band | Use for |
|---|---|---|---|
| `epical-drums-03-678.mp3` | Epical Drums 03 (183 s) | 0.17 | **Default for VSLs / long talking heads** — cinematic drums + orchestra, builds |
| `epical-drums-02-677.mp3` | Epical Drums 02 (123 s) | 0.10 | **Default for ads and Reels 60-150 s** |
| `epical-drums-01-676.mp3` | Epical Drums 01 (106 s) | 0.09 | Reels up to ~90 s, lowest voice conflict |
| `i-wont-surrender-846.mp3` | I Won't Surrender (114 s) | 0.33 | Emotional/epic alternative, steady loud level (6.6 dB under voice at -16) |
| `rising-sun-523.mp3` | Rising Sun (92 s) | 0.22 | Bright, loud, uplifting alternative |
| `lifes-a-movie-322.mp3` | Life's a Movie (121 s) | 0.58 | Cinematic, very dynamic; mid-heavy, so keep it quiet |
Not audible-tested by the agent (no ears) — Caio's ear decides; swap the file and re-run `finish_vsl.py` (5 min). IDs for
`fetch_music.py`: 678, 677, 676, 846, 523, 322. Build a bed to length with `scripts/music_bed.py <seconds> bed.wav --track <file>`.
**Level:** `--music-lufs -17 --duck-ratio 3` puts the ducked bed ≈ 8 dB under the voice during speech (measured with the
speech/pause split on the VSL); the old deep-house settings (-26, ratio 9) left it 14+ dB under = "barely audible".

## ELECTRONIC / motivational — the current default for every Caio talking-head video (2026-10, after deep house and orchestral were rejected)
Scanned 110 Mixkit tracks (electronica, tech-house, motivational, upbeat, hip-hop) with librosa: tempo, onset strength, key mode,
300-3400 Hz share, energy rise. Picked for drive + major key + low voice-band share.
| File | Title | BPM | Mode | Mid-band | Note |
|---|---|---|---|---|---|
| `kraft-twerk-115.mp3` | Kraft Twerk (130 s) | 117 | major | 0.09 | **Default.** Driving electronica |
| `motivating-mornings-033.mp3` | Motivating Mornings (96 s) | 123 | minor | 0.18 | Builds (+2 dB), more "motivational" |
| `tech-house-vibes-130.mp3` | Tech House vibes (102 s) | 123 | minor | 0.08 | Cleaner, less melodic |
Mixkit ids: 115, 33, 130. The `epical-drums-*`, `i-wont-surrender`, `rising-sun`, `lifes-a-movie` files above were tried and REJECTED by Caio.
