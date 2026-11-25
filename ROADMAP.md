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

## Before the custom domain

Device coverage is the gap. The owner's rule is iOS **and** Android, phone **and** tablet.

- [ ] Install and use on an iPhone (Safari → Add to Home Screen): layout, sticker reveal,
      reminder pop-up, offline after airplane mode
- [ ] Same on an Android phone (Chrome → Install app)
- [ ] **Tablet layout.** The CSS has one breakpoint at 960px: desktop one-screen above it,
      single column below. An iPad in portrait (768–1024px) falls into the phone branch and
      loses the side list, and phone stickers hide their text. Decide whether a tablet needs
      its own treatment, as a separate pass with alternatives shown in an HTML page
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
