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
