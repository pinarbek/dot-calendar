# Dot Calendar — roadmap and checklist

Status board for the project. Tick items as they land; keep this file honest rather than
optimistic. "Finalised" means the checklist under *Before the custom domain* is complete.

## Done

- [x] App built as a single dependency-free `index.html` (no build step)
- [x] Four languages (EN / ES / CA / TR), light and black themes
- [x] Holidays computed on-device for TR, ES, CAT, GB, DE, US
- [x] Notes, categories, palette and free colour picker
- [x] Reminders: in-app pop-up, chime, `.ics` export
- [x] Backup and restore through localStorage
- [x] PWA shell: manifest, service worker, icons
- [x] Smoke test suite — `tests/smoke.py`, 28 checks, all passing (2026-11-25)
- [x] Git repository published: https://github.com/pinarbek/dot-calendar (public)
- [x] Live on GitHub Pages: https://pinarbek.github.io/dot-calendar/
- [x] Live deployment verified in a real browser: 35 day dots, service worker registered,
      manifest and icons served, no script errors
- [x] NAS backup at `/Volumes/PROJECTS/olaCreative/dot-calendar`
- [x] Desktop layout bounded by its own column, so a tall window no longer puts the grid
      on top of the side list
- [x] Sundays filled in the contour colour; hovering a note uncovers its date properly
- [x] Month list, note count and legend moved into a slide-in panel; calendar screen is
      now one column holding only the month, the grid and the logo
- [x] Header note count sized like the weekday row instead of the header
- [x] Dot size derived from the free height and the month's row count. Fixed a six-row
      overflow that predated this work, and one the panel change introduced on tall windows
- [x] **Header stays side by side (A).** Stacking it, as the reference showed, costs ~10px
      of dot diameter; the owner chose the larger dots
- [x] Smoke test hardened: measures the lowest element rather than the grid, covers
      four-, five- and six-row months across nine window sizes. 147 checks

## Before the custom domain

Device coverage is the gap. The owner's rule is iOS **and** Android, phone **and** tablet.

- [ ] Install and use on an iPhone (Safari → Add to Home Screen): layout, sticker reveal,
      reminder pop-up, offline after airplane mode
- [ ] Same on an Android phone (Chrome → Install app)
- [ ] **Tablet layout.** One breakpoint at 960px. An iPad in portrait (768–1024px) falls
      into the phone branch, where stickers hide their text. Dots measure 94px there, so the
      question is now about sticker text and touch targets, not space. Separate pass
- [ ] Decide the weekday spelling: the reference shows `Sun`, the app renders `SUN` because
      `WD3` holds uppercase strings. Changing it touches the weekday row too, in four
      languages
- [ ] Check the reminder flow survives a real overnight gap (fires at the right local time,
      `fired` state not replayed)
- [ ] Decide whether notifications need a permission prompt on first run or stay opt-in
- [ ] Re-run `tests/smoke.py` and bump `VERSION` in `sw.js` before the final push

## Custom domain (parked until finalised)

- [ ] Pick the hostname (`takvim.` / `cal.` / `dot.` under `olacreative.es`)
- [ ] Cloudflare → DNS → `CNAME <name> → pinarbek.github.io`, proxy **DNS only** (grey cloud)
- [ ] Add a `CNAME` file to the repo, set the custom domain in Settings → Pages
- [ ] Wait for the Let's Encrypt certificate, then enable Enforce HTTPS
- [ ] Re-run the live check against the new hostname

## Later, if the owner asks

- Sync across devices — needs a backend (Firebase) plus sign-in. Local-only was the choice.
- More countries, regions, or local town holidays.
- A compact "widget" window mode for the desktop app.
- Logo size or position tweaks.
