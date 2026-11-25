# CLAUDE.md: Dot Calendar

Context for continuing this project. Read this before changing anything.

## Who and what

- The client is **ola | CREATIVE**. The project owner speaks Turkish: reply in Turkish and keep code and comments in English.
- The product is a free, shareable **2027 calendar web app (PWA)** that people install on a phone or desktop and use for notes and reminders. It is meant to be spread quickly by sharing one link, so there are no accounts and no backend.

## Design decisions (agreed with the owner; do not change without asking)

- **Visual language:** It combines two references:
  1. A Dieter Rams-style minimal calendar: warm grey paper `#e8e6e1`, a huge date numeral, the month name in caps, the year in grey, the weekday on the right, and a dot grid where past days are filled ink, upcoming days are empty rings, and today is orange `#f26b21`.
     Past days stay **filled ink**: re-confirmed 25 Nov 2026 after the dots grew to 96px,
     when a mostly-past month reads much heavier. Softer grey and ring-only were shown as
     alternatives and declined.
  2. A bold "content calendar" sticker look: each note is a colour circle the same size as the day, offset about 22% down and right, with small uppercase text inside. The day under it turns into a thin outlined ring.
- **Animation:** A note sticker fully covers its day, hiding the number, until that day arrives. On load, today's sticker slides off with a small anticipation bounce (`@keyframes uncover`). Past notes stay slid off. Hovering a future note peeks at it.
- **Typography:** Archivo (Google Fonts, variable `wdth 62–125`) everywhere. Labels, buttons and headings use expanded caps (`font-stretch:125%`). Note text in the list and in the textarea stays at normal width for readability.
- **Weekday spelling:** `WD3` holds mixed case (`Sun`, `Paz`, `Dom`, `Dg`). The header takes
  it as written; the weekday row is uppercased in CSS, so one dictionary serves both.
- **Sticker text:** `max(6.5px, 8cqw)` — 8% of the dot, with the old 6.5px floor so small
  dots stay readable. Set to 8% on 25 Nov 2026 after 11% read too loud on a 121px dot; 11,
  9, 8 and 7 were rendered side by side and 8 chosen.
- **Long text is clipped, never shrunk (25 Nov 2026).** `fitStk()` used to drop the font for
  long words; it now returns nothing. Text past three lines is cut with an ellipsis, and a
  single long word breaks with a hyphen through `hyphens:auto`. Hyphenation depends on the
  browser having a dictionary for `<html lang>`: verified in Chromium for tr, es and ca,
  absent for en, where `overflow-wrap:anywhere` breaks the word without a hyphen rather than
  letting it spill.
- **Date numeral:** `20cqw`, at `17%/15%` of the day. It used to sit at `21%/19%` at `25cqw`,
  which left 14% of it under the sticker once that slid to `22%/22%`. Any change to either
  position has to be re-checked against the slid state.
- **Themes:** Light grey (default) and black. In black, the grid matches the content-calendar reference: upcoming days are white filled circles and past days are dark grey.
- **Palette (owner-supplied, exact hex):** `#ff5a00 #ff9700 #ffcc00 #563cf3 #2495ff #00dbee #f6042e #ff62d7 #febaff #038a6c #7ac841 #a6fe5a`. The owner also wants a free colour picker.
- **Category defaults:** work `#563cf3`, meeting `#2495ff`, birthday `#ff62d7`, holiday `#f6042e`. Holidays must be **red from the start**.
- **Calendar range:** Opens on December 2026 (before Dec 2026) and is the "2027 calendar". Navigation is unlimited, plus a month picker.
- **Layout:** One column at every width. On desktop (≥960px) the whole month must fit one
  screen without scrolling, measured to the lowest element on the page, not just the grid.
  Stickers show words wherever the **dot** is at least 56px, and are colour only below
  that — a container query on the day, not a viewport breakpoint. The old 699px cutoff
  hid text on 75px dots in a 600px window while a tablet showed it on 96px ones.
  Browsers without container queries keep the old viewport rule.
- **Header is stacked at every width (decided 25 Nov 2026).** Numeral above, month and year
  below, weekday or note count on the right — matching the owner's reference, and what the
  narrow layout always did. Offered as A/B/C against measurements; the owner chose **C**,
  accepting that it costs about 10px of dot diameter because the header and the grid share
  the same vertical space. Hence the larger reserve below.
- **Dot size:** derived from the height actually free, divided by the rows the month needs:
  `--avail: calc(100vh - 302px - 18.5vh)`, `--dot: (--avail - (--rows - 1) * --gap) / --rows`,
  sheet width `7 * --dot + 6 * --gap`. `--rows` is set by `render()`. The 235px + 18.5vh
  reserve was measured across eight windows (186px + 17.4vh), plus a margin and the 67px the
  stacked header adds. **Dots therefore differ month to month** — 99px on a six-row month
  against 121px on a five-row one at the same window. Queried by the owner on 25 Nov 2026
  and kept: both months already fill the screen, so matching them would mean either
  shrinking every month to the six-row size or letting six-row months scroll. Shrinking
  when a month needs six rows is the accepted behaviour. Dots land at 73-141px on four-row months, 57-138px on five-row and
  54-137px on six-row.
- **Month list, note count and legend live in a panel** (`#ovList`), opened by the Notes
  button, sliding in from the right, anchored to the right edge, scrolling on its own. The
  calendar screen keeps only the month, the grid and the logo.
- **Only the current month names a day (25 Nov 2026).** The header reads `25 KASIM 2026 ·
  Çar` in the month you are in. In any other month the numeral is hidden and the weekday
  slot is empty, leaving the month, the year and the orange back-to-today link. The numeral
  keeps its space (`visibility`, not `display`) so paging through months does not make the
  grid jump. The note count that used to sit in the weekday slot is gone; the panel carries
  it. `.cnt` and its styling are now unused.
- **Logo:** The ola | CREATIVE logo is a white PNG embedded as a CSS mask, so it takes `var(--ink)` and works in both themes. On the calendar screen it sits under the grid; the panel carries its own copy at the bottom.
- **A day can hold several notes, and the circle advances through the day (agreed 25 Nov
  2026).** One day is still one circle, one colour, one label — it just moves on. A day
  ahead of today opens on its first note; today shows the next note still to come, so once
  11:00 passes the 13:00 one takes the circle; once all have passed, and on any past day,
  the circle keeps the last note. Notes sort untimed first, then by time. No "+2 more" badge
  on the circle: the panel lists them. `shownNote()` holds this rule, and `tick()` re-renders
  when the signature of shown notes changes, so the circle turns over on its own.
  The editor carries a strip of the day's notes with a **+** to start another; tapping a chip
  switches to that note, Delete removes only that one and stays open while others remain.
  The panel lists every note, one row each, with the day number only on the first.
- **A note moves by dragging its sticker onto another day.** Mouse drags after 7px; a
  finger must hold still for 300ms first, so the month swipe and page scrolling still work
  (a finger that travels early is treated as a swipe). Dropping on a day that already has a
  note **swaps** the two, so nothing is ever lost. Reminder state (`fired`) travels with the
  note. Holiday stickers are not draggable. `skipClick` suppresses the click that follows a
  drop and expires after 350ms — a sticky flag swallowed the next real tap.
- **Reminders stay local; no push when the app is closed (decided 25 Nov 2026).** Asked
  directly whether notifications should arrive with the app fully closed, the owner said no.
  So the three paths stay as they are: a pop-up and chime while the app is open (`tick()`
  every 20s, with a 36-hour catch-up for reminders whose time passed while the device was
  off), a system notification when the app is installed and running or backgrounded, and
  `.ics` export with a VALARM for anything that must fire regardless. Do not add a service
  worker push path or a backend for this.
- **Desktop and mobile only; tablet is not a target (25 Nov 2026).** The one-screen layout
  starts at 960px and the phone layout runs below it. Lowering that to 700px so an iPad fits
  the month on one screen was tried and reverted at the owner's request, as was enlarging
  the month name to fill the header on months with no date. The design is not to be bent for
  tablet.
- **Rejected directions:** AI-illustrated monthly scenes, and a giant-month-word poster. Both are in `archive/` for reference only.
- **Never copy third-party artwork:** The owner once asked to feed other artists' images to an image model as references. That was declined: describe styles in words instead.

## Code map (`index.html`, single file, no build)

- **CSS (top):** Base tokens use `light-dark()` with `[data-theme]` overrides. Day/sticker states are `.day.past/.today/.has/.hol/.out` and `.stk`. Later blocks override earlier ones, in this order: unified typography, the desktop one-screen layout, the brand logo.
- **Palette and categories:** `NOTECOL`, `CATS`, `CATDEF`, `catCol()`, `personalPool()`, `colorOf(key, note)`.
- **i18n:**
  - Dictionaries: `LANGS`, `LOCALE`, `WD3`/`WD1` (weekday labels), `T` (all UI strings ×4), `HN` (holiday names ×4).
  - Functions: `t(key, vars)`, `monthName()`, `fmtLong()`, `holName()`.
  - Static elements use `data-i18n`, `data-i18n-ph` and `data-i18n-html`. `applyI18n()` refreshes everything.
  - **Every new UI string must be added to all four languages.**
- **Holidays:**
  - `guessCC()` picks the country from the **timezone first**, language second. Someone
    living abroad keeps their own language, so language alone is the wrong signal; it only
    chooses between ES and CAT, and stands in when the timezone matches nothing.
  - `holidays(year, cc)` returns `{ "YYYY-MM-DD": {ids:[...], kind:"off"|"half"|"fun"} }`, with a lazy `name` getter.
  - Country codes are `TR ES CAT GB DE US`.
  - Ids may carry `:n` (the feast day number) or `:sub` (a substitute day).
  - Easter uses an algorithm. Islamic feasts use `Intl` `islamic-umalqura`.
- **Rendering:** `render(anim)` builds the header, weekdays, grid and side list. `renderToday()` builds the "next 24 hours" box. `revealSoon()` renders and triggers the uncover animation (on load and at midnight).
- **Note editor:** `openNote(k)`, `commit()` (autosaves on every input), category chips `#cats`, colour dots `#dots`, `#nHex`.
- **Reminders:** `fireAt()`, `tick()` (every 20 s and on focus), `showRem()`/`chime()` (Web Audio), `icsFor()` (`.ics` export with VALARM).
- **Settings:** backup/restore, theme, language, category colours, week start, holiday country, sound, notifications, print.
- **Environment detection:** `inFrame` is true inside the claude.ai artifact viewer, where downloads go through `claude.use("downloads")`; print, Web Share and the service worker are off there. Standalone hosting uses normal browser APIs.

## Where the project lives (keep all three in step)

- **Working copy:** `~/Desktop/Capcut_2026/dot-calendar`
- **GitHub:** https://github.com/pinarbek/dot-calendar (public, `main`)
- **NAS backup:** `/Volumes/PROJECTS/olaCreative/dot-calendar` (SMB forces mode 0755, so the
  backup has `core.fileMode false`; contents are identical)
- **Live site:** https://pinarbek.github.io/dot-calendar/ — GitHub Pages, `main` / root.
  A push to `main` redeploys it.

After any change: commit and push, then `rsync -a --delete --exclude .DS_Store
--exclude tests/output` the folder to the NAS. Three copies that disagree is worse than one.

## Tooling on this machine

- `gh` is installed at `~/.local/bin/gh` (not on PATH by default; add
  `export PATH="$HOME/.local/bin:$PATH"` to `~/.zshrc`). Logged in as `pinarbek`.
- Playwright is **not** installed system-wide. The smoke test needs a virtualenv:
  `python3 -m venv venv && venv/bin/pip install playwright && venv/bin/playwright install chromium`,
  then `venv/bin/python tests/smoke.py`.
- No Homebrew on this machine.

## Conventions

- Keep it a single dependency-free `index.html`. Only Google Fonts load from outside.
- Escape every user string with `esc()` before it goes into HTML. Notes are untrusted text.
- Never shadow `t` (the translate function) with a local variable. Use `nowT`, `tday` and similar names. This bug happened once.
- Bump `VERSION` in `sw.js` on every release.
- Run `python3 tests/smoke.py` after changes. It checks four languages, both themes, holiday dates and the reminder flow, and saves screenshots.

## Verified facts (2027)

- **Türkiye:**
  - Ramazan Bayramı is 9–11 March, with the eve on 8 March.
  - Kurban Bayramı is 16–19 May, with the eve on 15 May. Most sources say this; one says 17–20 May.
  - 19 May coincides with the 4th day of Kurban Bayramı.
- **Spain (BOE 13 Oct 2026):** nine common holidays. 15 Aug 2027 is a Sunday.
- **Catalonia (Ordre EMT/52/2026):**
  - 12 days, including Easter Monday 29 March, 24 June and 11 September.
  - Sant Esteve and 15 August fall on Sunday in 2027.
  - Vall d'Aran swaps Easter Monday for 17 June (not modelled).
  - Local town holidays (2 per town) are not modelled.

## Ideas the owner may ask for next

- Sync across devices. Local-only was the owner's choice at the start. Researched properly on
  25 Nov 2026 and written up in `docs/sync-options.md`: money is not the obstacle (free to
  10,000 users, under $5/month at 100,000; classic Firebase Auth has no user cap and no
  charge — the $0.0055/MAU figure belongs to Identity Platform, which this app does not
  need). Three routes are costed there, with a recommendation of **B, a sync code with no
  accounts**. **No decision has been taken.** Read that file before discussing it again.
- More countries or regions, or local town holidays.
- A compact "widget" window mode for the desktop app.
- Logo size or position tweaks.
