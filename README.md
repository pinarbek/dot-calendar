# Dot Calendar

A calm, minimal 2027 wall calendar that runs in the browser and installs like an app on a phone or computer. Days are dots that fill in as the month goes by. Notes and reminders sit on top of their day as bright colour stickers. When a note's day arrives, the sticker slides off and reveals the date.

By **ola | CREATIVE**.

## Features

- **Calendar:** Starts in December 2026 and covers all of 2027. You can go to any month with the arrows, swiping, the arrow keys, or the month picker (tap the month name).
- **Notes:** Tap a day to write a note. Notes save automatically on the device.
- **Categories:** Personal, Work, Meeting, Birthday, Holiday. Each category has its own colour, and the user can change it in Settings. Holidays are red by default.
- **Palette:** 12 colours plus a free colour picker. Personal notes rotate through the colours that no category is using.
- **Reminders:**
  - Set a time and choose on the day, 1 day before or 1 week before.
  - While the app is open, a reminder shows a pop-up and plays a short chime. Notifications also work when the app is installed outside Claude.
  - "Add to my phone's calendar" saves an `.ics` file so the phone's own calendar raises the alarm even when the app is closed.
- **Holidays (computed on the device, no internet needed):**
  - Türkiye, including the Ramadan and Sacrifice feasts from the Umm al-Qura calendar, with half-day eves.
  - Spain and Catalonia.
  - United Kingdom (with substitute days), Germany and United States.
  - Fun days such as Valentine's Day, Halloween and Sant Jordi.
- **Languages:** English, Español, Català, Türkçe. Picked automatically from the device language, and can be changed from the EN/ES/CA/TR button or Settings.
- **Themes:** Light grey or black, or follow the device.
- **Backup:** Download or copy a backup, then restore it on another device. Notes are never sent anywhere.
- **Layout:** On a computer screen the whole month fits without scrolling. Narrow windows and phones get a single-column layout.

## Project structure

```
index.html              The whole app: markup, styles and script in one file (no build step)
manifest.webmanifest    PWA manifest (name, icons, standalone display)
sw.js                   Service worker: offline shell + font caching. Bump VERSION on every release
icons/                  App icons (192, 512, maskable 512, apple-touch, favicon)
assets/                 ola | CREATIVE logo (trimmed white PNG + the original)
netlify.toml            Static hosting config for Netlify
tests/smoke.py          Playwright smoke test (renders 4 languages, both themes, reminders)
docs/                   Illustration prompts, and the costed sync options (sync-options.md)
archive/                Earlier design directions (illustrated, typographic poster), kept for reference
CLAUDE.md               Context and conventions for continuing the work with Claude Code
```

## Run locally

The app is a static site. Any static server works:

```bash
python3 -m http.server 8080
# open http://localhost:8080
```

Opening `index.html` directly from disk also works, but installing and the service worker need `http://localhost` or `https://`.

## Test

```bash
pip install playwright && playwright install chromium
python3 tests/smoke.py
```

The test writes screenshots to `tests/output/` and fails if the page throws a script error or a key check fails.

## Publish (free)

The site is live on GitHub Pages, served from the `main` branch, root folder:

**https://pinarbek.github.io/dot-calendar/**

Every push to `main` redeploys it, normally within a minute. HTTPS is enforced, so the
service worker and "Add to Home Screen" work as they do on any other host.

Repository: https://github.com/pinarbek/dot-calendar (public)

People open the link and choose Install (computer) or Add to Home Screen (phone).

### Custom domain (planned, not set up yet)

When the project is finalised it moves to a subdomain of `olacreative.es`. DNS for that
domain is on Cloudflare, and two steps are needed:

1. Cloudflare → DNS → add `CNAME  <name>  →  pinarbek.github.io`, with proxy set to
   **DNS only** (grey cloud). An orange cloud breaks GitHub's certificate check.
2. In this repo, add a `CNAME` file holding the full hostname, set the custom domain under
   Settings → Pages, wait for the Let's Encrypt certificate, then enable Enforce HTTPS.

`manifest.webmanifest` and `sw.js` use relative paths (`./`), so the app works both in the
`/dot-calendar/` subfolder and at a domain root. No path changes are needed for the move.

## Data

Everything is stored in the browser's `localStorage` under the key `desklife-cal-v1`:

```js
{
  notes: { "2027-01-14": { t: "Release review", c: -1, cat: "work", r: "15:00", w: 0, hex?: "#rrggbb" } },
  weekStart: 1, country: "TR", lang: "tr", theme: "light", sound: true,
  catCol: { work: "#563cf3", ... }, fired: { ... }
}
```

- `c`: index into the palette, or `-1` for automatic.
- `cat`: `""` (personal), `work`, `meeting`, `birthday` or `holiday`.
- `r`: the reminder time.
- `w`: how many days before to remind (0, 1 or 7).

Backups are this `notes` object wrapped as `{app, v, saved, notes}`.
