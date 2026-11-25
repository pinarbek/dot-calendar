# CLAUDE.md: Dot Calendar

Context for continuing this project. Read this before changing anything.

## Who and what

- The client is **ola | CREATIVE**. The project owner speaks Turkish: reply in Turkish and keep code and comments in English.
- The product is a free, shareable **2027 calendar web app (PWA)** that people install on a phone or desktop and use for notes and reminders. It is meant to be spread quickly by sharing one link, so there are no accounts and no backend.

## Design decisions (agreed with the owner; do not change without asking)

- **Visual language:** It combines two references:
  1. A Dieter Rams-style minimal calendar: warm grey paper `#e8e6e1`, a huge date numeral, the month name in caps, the year in grey, the weekday on the right, and a dot grid where past days are filled ink, upcoming days are empty rings, and today is orange `#f26b21`.
  2. A bold "content calendar" sticker look: each note is a colour circle the same size as the day, offset about 22% down and right, with small uppercase text inside. The day under it turns into a thin outlined ring.
- **Animation:** A note sticker fully covers its day, hiding the number, until that day arrives. On load, today's sticker slides off with a small anticipation bounce (`@keyframes uncover`). Past notes stay slid off. Hovering a future note peeks at it.
- **Typography:** Archivo (Google Fonts, variable `wdth 62–125`) everywhere. Labels, buttons and headings use expanded caps (`font-stretch:125%`). Note text in the list and in the textarea stays at normal width for readability.
- **Themes:** Light grey (default) and black. In black, the grid matches the content-calendar reference: upcoming days are white filled circles and past days are dark grey.
- **Palette (owner-supplied, exact hex):** `#ff5a00 #ff9700 #ffcc00 #563cf3 #2495ff #00dbee #f6042e #ff62d7 #febaff #038a6c #7ac841 #a6fe5a`. The owner also wants a free colour picker.
- **Category defaults:** work `#563cf3`, meeting `#2495ff`, birthday `#ff62d7`, holiday `#f6042e`. Holidays must be **red from the start**.
- **Calendar range:** Opens on December 2026 (before Dec 2026) and is the "2027 calendar". Navigation is unlimited, plus a month picker.
- **Layout:** On desktop (≥960px) the whole month must fit one screen without scrolling. The header sits side by side and the dot size is driven by the viewport height (`calc((100vh - 390px) * 1.18)`). Below 960px it is a single column. On phones the stickers show no text (too small), only colour.
- **Logo:** The ola | CREATIVE logo is a white PNG embedded as a CSS mask, so it takes `var(--ink)` and works in both themes. On desktop it sits bottom-left under the legend. On mobile it sits at the very bottom.
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
  - `holidays(year, cc)` returns `{ "YYYY-MM-DD": {ids:[...], kind:"off"|"half"|"fun"} }`, with a lazy `name` getter.
  - Country codes are `TR ES CAT GB DE US`.
  - Ids may carry `:n` (the feast day number) or `:sub` (a substitute day).
  - Easter uses an algorithm. Islamic feasts use `Intl` `islamic-umalqura`.
- **Rendering:** `render(anim)` builds the header, weekdays, grid and side list. `renderToday()` builds the "next 24 hours" box. `revealSoon()` renders and triggers the uncover animation (on load and at midnight).
- **Note editor:** `openNote(k)`, `commit()` (autosaves on every input), category chips `#cats`, colour dots `#dots`, `#nHex`.
- **Reminders:** `fireAt()`, `tick()` (every 20 s and on focus), `showRem()`/`chime()` (Web Audio), `icsFor()` (`.ics` export with VALARM).
- **Settings:** backup/restore, theme, language, category colours, week start, holiday country, sound, notifications, print.
- **Environment detection:** `inFrame` is true inside the claude.ai artifact viewer, where downloads go through `claude.use("downloads")`; print, Web Share and the service worker are off there. Standalone hosting uses normal browser APIs.

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

- Sync across devices. This would need a backend such as Firebase plus sign-in; the owner chose local-only for now.
- More countries or regions, or local town holidays.
- A compact "widget" window mode for the desktop app.
- Logo size or position tweaks.
