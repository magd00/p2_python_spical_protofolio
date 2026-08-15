# Setup Notes

## 1. Styling — self-contained ✅

No download needed. `static/assets/css/main.css` and `static/assets/js/main.js` are a
custom dark theme (rounded cards, hover effects, mobile nav, scroll-to-top, working
portfolio category filters). Bootstrap 5 + Bootstrap Icons load from CDN in `base.html`.

## 2. Projects — 12 of the 15 are now seeded

`INITIAL_PROJECTS` near the top of `main.py` seeds automatically on first run (only when
the `Project` table is empty — delete `portfolio.db` to re-seed from scratch).

**Original 6:**
1. Morse Code Translator
2. Tic-Tac-Toe XO Game
3. Image Watermarking App
4. Typing Speed Test
5. Breakout Game
6. Cafe Management System

**Newly added 6 (from the links you sent):**
7. Ledger & Co. — Online Shop (`p15_online_shop`)
8. Beauty Color Extractor (`p10_butycolory_app...`)
9. Open Art Museum Explorer (`p14_API_search`)
10. Recipe Scraper (`p11_Recipe-Scraper`)
11. Dinosaur Game Automation (`p12_automation_for_dinosaur_game`)
12. Space Invaders — **"Space Turtle War Invaders"** (`p13_arcade_game_space_invaders.` —
    note the repo name literally ends with a period, that's not a typo). This one now uses
    your real code from `main.py` + `turtle_1.py`: a turtle-graphics ship shooter with
    lasers, falling stars, alien enemies, lives, levels, pause/restart. Since `turtle`
    needs a real display and keyboard, it can't run headlessly on a web server — so the
    "Run Code" demo reproduces the actual collision/scoring logic from
    `Game.check_collisions()` (distance < 25 = hit, +10 per star, +15 per enemy) using
    plain coordinates instead of turtle sprites. The real playable game is one click away
    via "View on GitHub" — download it and run `python main.py` locally to actually play it.

Still missing: a couple of projects to reach 15 (you sent 6 links, one of which — space
invaders — was duplicated in your message, and turned out to have a period at the end of
the actual repo name). Send any remaining repo links and I'll add them the same way.

### How each new project's "Run Code" demo works
For the 6 new projects I pulled the real README/description and, where possible, the real
`main.py` from each repo. For the **"Run Code"** button I wrote a short, self-contained
version of each project's core logic (no external packages like `scikit-learn`, `pygame`,
or `pyautogui` required) so it runs instantly via the site's `/run-code` sandbox without
needing anything extra installed:
- **Color Extractor** — same color-clustering idea, pure Python instead of scikit-learn's KMeans
- **Recipe Scraper** — parses a local HTML sample instead of hitting AllRecipes (which blocks scrapers)
- **API Search** — calls the real Art Institute of Chicago API, with an offline fallback if there's no network
- **Dino Automation** — simulates the same jump/duck decision logic without needing a real screen
- **Online Shop** — the actual server-side cart pricing/tax logic from the app
- **Space Invaders** — the real collision/scoring formula from `Game.check_collisions()`, run against plain coordinates instead of turtle sprites (turtle needs a real screen, so it can't run on a server)

The full, real implementations are always one click away via each project's **"View on
GitHub"** button.

Security note: the `/run-code` endpoint runs whatever Python string it's given with
`exec()`. That's fine for a personal site where only you control what's in the database,
but if you ever deploy this publicly with the "Add Project" form open to strangers,
someone could submit malicious code and have your server execute it. If you plan to make
`/add-project` public, either remove code execution from that form or run it in a properly
sandboxed subprocess/container instead of in-process `exec()`.

## 3. All 12 projects now have a "Run Code" browser and real cover art

Projects 1–6 (Morse Code, Tic-Tac-Toe, Watermarking, Typing Speed, Breakout, Cafe System)
previously had no demo and used generic placeholder photos. They now have custom SVG
cover art and a self-contained "Run Code" demo each, same as projects 7-12:
- **Morse Code Translator** — real text→Morse encoding
- **Tic-Tac-Toe** — simulated match with win detection
- **Image Watermarking** — actually blends semi-transparent text onto a generated
  image with Pillow (the real app is a Tkinter GUI, which needs a display, so the
  demo shows the same blending technique headlessly)
- **Typing Speed Test** — real WPM/accuracy scoring math
- **Breakout** — real ball/paddle bounce-angle physics (the real game needs Pygame's
  display, so this demo runs the same collision formulas without a screen)
- **Cafe Management System** — the real stats-dashboard calculation (total cafes,
  unique areas, average price) against sample records

Note: I didn't have fresh access to re-download projects 1-6's exact source this
session, so their demos are faithful re-implementations based on their documented
features rather than copy-pasted from the original files. If you'd like them to match
your actual code more precisely, send me the repo links again and I'll pull the real
files in, same as I did for projects 7-13.

## 4. Public "Add Project" / "Delete Project" removed — use manage.py instead

The website no longer has any way for a visitor to add, edit, or delete a project —
that button and its route (`/add-project`) are gone, and so is the old unauthenticated
`/delete-project/<id>` route that anyone could have hit directly by guessing the URL.

To add or remove your own projects now, use the new `manage.py` script:

```bash
python manage.py --list                          # see every project + its ID
python manage.py --delete 7                      # delete project #7
python manage.py                                 # interactive: add a project step by step
python manage.py --title "..." --description "..." --full-description "..." \
  --category web --technologies "Python, Flask" --github-link "https://github.com/..." \
  --image /path/to/cover.png --code-file /path/to/demo.py
```

Or import it directly in your own script:

```python
from manage import add_project, delete_project, list_projects
add_project(title=..., description=..., full_description=..., category="web",
            technologies=..., github_link=..., image_path=..., code_snippet_path=...)
```

`category` must be one of: `web`, `data`, `automation`, `api`, `game`, `desktop`.

## 5. Running it

```bash
pip install flask flask_sqlalchemy
python main.py
```

Delete `portfolio.db` if it exists before the first run — the app auto-creates it and
seeds all 12 projects above only when the `Project` table is empty.

## Deployment Notes (Render / PythonAnywhere / similar)

**Environment variables** — `main.py` now reads `SECRET_KEY` and `DATABASE_URL`
from the environment via `python-dotenv` instead of hardcoding them. Copy
`.env.example` to `.env` for local dev and fill in real values; on your host,
set the same variables in its dashboard/secrets manager instead of committing
a `.env` file (it's already in `.gitignore`).

**SQLite vs. PostgreSQL** — SQLite is fine for this site's traffic level. The
catch: on free tiers that restart/redeploy the container (e.g. Render's free
web services), anything written to local disk — including `portfolio.db` —
gets wiped unless it's on attached persistent storage. If that happens
repeatedly, switch `DATABASE_URL` to a free managed Postgres instance (Render
Postgres, Supabase, Neon, etc.) and uncomment `psycopg2-binary` in
`requirements.txt`. No code changes needed beyond that - `main.py` already
normalizes `postgres://` URLs to `postgresql://` automatically.

**Re-seeding the database** — if a fresh host/database ever comes up empty
(new Postgres instance, or a wiped SQLite file), run:

    python seed.py

to recreate the tables and repopulate the portfolio projects. Use
`python seed.py --reset` only if you want to wipe and start clean (it will
delete any projects added by hand via `manage.py`).
