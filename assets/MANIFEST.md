# Assets Manifest

`assets/` is version-controlled as of 2026-08. The 21 reference PNGs are hand-made
originals — they are the visual DNA of the whole series and are NOT recoverable if
lost. Fonts are Google Fonts (OFL) and re-downloadable.

## Expected files (validated by `AgentAlpha.check_environment()`)

### Reference images — 3 per page key, 7 keys (21 files) — STATUS: MISSING, restore from original workstation
For each key in `cover, page1, page2, page3, page4, page5, page50`:

| File | Role |
|---|---|
| `ref_{key}_01.png` | Master style reference ("Master Visual Target") |
| `ref_{key}_layout_wireframe_kdp.png` | Layout wireframe with R/G/B zone guides |
| `ref_{key}_structure_example.png` | Structure example (layering & density) |

### Fonts — `assets/fonts/` (5 files) — STATUS: PRESENT
| File | Registered as | Source |
|---|---|---|
| `TitanOne-Regular.ttf` | TitanOne | google/fonts ofl/titanone |
| `Fredoka-Regular.ttf` | FredokaOne | google/fonts ofl/fredoka (static instance wght=400) |
| `Quicksand-Bold.ttf` | Quicksand | google/fonts ofl/quicksand (static instance wght=700) |
| `PatrickHand-Regular.ttf` | PatrickHand | google/fonts ofl/patrickhand |
| `Sniglet-Regular.ttf` | Sniglet | google/fonts ofl/sniglet |

### Other — STATUS: PRESENT
| File | Role |
|---|---|
| `logo.png` | Series logo, composited onto cover Zone 8 |

## Restoring the reference PNGs
Copy them from the original workstation
(`~/gitprojects/knolling_adventure_book/assets/`) into this directory and commit.
The pipeline refuses to run with missing assets unless `ALLOW_DEGRADED_ASSETS=true`
is set (degraded runs generate without visual conditioning — for debugging only).
