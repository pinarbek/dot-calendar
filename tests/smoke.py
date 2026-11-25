"""Smoke test for Dot Calendar.

Serves the project folder over http, renders it in Chromium in four languages and both
themes, checks key holiday dates and the reminder flow, and saves screenshots to
tests/output/. Exits with code 1 if anything fails.

    pip install playwright && playwright install chromium
    python3 tests/smoke.py
"""
import asyncio, datetime, functools, http.server, pathlib, sys, threading
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "output"
OUT.mkdir(parents=True, exist_ok=True)
failures = []

def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        failures.append(msg)

def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Quiet, directory=str(ROOT))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"

def seed(**extra):
    notes = {
        "2027-01-05": {"t": "Team meeting", "c": -1, "cat": "meeting", "r": "10:00"},
        "2027-01-14": {"t": "Release review", "c": -1, "cat": "work"},
        "2027-05-14": {"t": "Birthday", "c": -1, "cat": "birthday", "r": "09:00", "w": 1},
    }
    data = {"notes": notes, "weekStart": 1, "fired": {}, **extra}
    import json
    return f"localStorage.setItem('desklife-cal-v1', {json.dumps(json.dumps(data))})"

async def page_for(browser, base, w, h, store, hash_):
    ctx = await browser.new_context(viewport={"width": w, "height": h}, timezone_id="Europe/Madrid")
    pg = await ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    await pg.goto(base + "index.html")
    await pg.evaluate(store)
    await pg.goto(base + "index.html#" + hash_)
    await pg.reload()
    await pg.wait_for_timeout(900)
    return pg, errors

async def main():
    srv, base = serve()
    async with async_playwright() as p:
        b = await p.chromium.launch()

        print("Languages and holidays")
        cases = [
            ("en", "GB", "december-2026", "2026-12-28", "Boxing Day"),
            ("es", "ES", "january-2027", "2027-01-06", "Reyes"),
            ("ca", "CAT", "september-2027", "2027-09-11", "Diada"),
            ("tr", "TR", "march-2027", "2027-03-09", "Ramazan Bayramı"),
            ("tr", "TR", "may-2027", "2027-05-16", "Kurban Bayramı"),
        ]
        for lang, cc, h, day, expect in cases:
            pg, errs = await page_for(b, base, 1440, 900, seed(lang=lang, country=cc), h)
            label = await pg.get_attribute(f'[data-k="{day}"]', "aria-label") or ""
            check(expect in label, f"{lang}/{cc} {day} shows '{expect}'")
            check(await pg.evaluate("document.documentElement.lang") == lang, f"{lang} sets <html lang>")
            check(not errs, f"{lang} {h} has no script errors {errs}")
            await pg.screenshot(path=str(OUT / f"{lang}-{h}.png"))
            await pg.context.close()

        print("Themes and layout")
        for theme, w, h in [("light", 1440, 900), ("dark", 1440, 900), ("light", 390, 844), ("dark", 390, 844)]:
            pg, errs = await page_for(b, base, w, h, seed(lang="en", country="TR", theme=theme), "january-2027")
            check(await pg.evaluate("document.documentElement.dataset.theme") == theme, f"theme {theme} applied at {w}px")
            if w >= 960:
                bottom = await pg.evaluate("document.querySelector('#grid').getBoundingClientRect().bottom")
                check(bottom <= h, f"month fits one screen at {w}x{h} (grid bottom {bottom:.0f})")
            check(not errs, f"no script errors ({theme}, {w}px)")
            await pg.screenshot(path=str(OUT / f"theme-{theme}-{w}.png"), full_page=True)
            await pg.context.close()

        print("Notes and reminders")
        now = datetime.datetime.now()
        k = now.strftime("%Y-%m-%d")
        soon = (now - datetime.timedelta(minutes=1)).strftime("%H:%M")
        cur = now.strftime("%B").lower() + "-" + now.strftime("%Y")
        pg, errs = await page_for(b, base, 1280, 900, seed(lang="en", country="TR"), cur)
        await pg.evaluate(f"""(()=>{{const s=JSON.parse(localStorage.getItem('desklife-cal-v1'));s.notes['{k}']={{t:'Call mom',c:-1,r:'{soon}'}};localStorage.setItem('desklife-cal-v1',JSON.stringify(s))}})()""")
        await pg.reload()
        await pg.wait_for_timeout(900)
        check(await pg.is_visible("#ovRem"), "due reminder opens the reminder pop-up")
        await pg.click("#remOk")
        await pg.click(f'[data-k="{k}"]')
        await pg.fill("#nText", "Quarterly report")
        await pg.click('#cats [data-cat="work"]')
        await pg.click("#nDone")
        saved = await pg.evaluate(f"JSON.parse(localStorage.getItem('desklife-cal-v1')).notes['{k}']")
        check(saved.get("cat") == "work" and saved.get("t") == "Quarterly report", "editing a note saves text and category")
        check(not errs, f"no script errors in note flow {errs}")
        await pg.context.close()
        await b.close()
    srv.shutdown()
    print(f"\n{'PASS' if not failures else 'FAILED: ' + str(len(failures))} — screenshots in {OUT}")
    sys.exit(1 if failures else 0)

asyncio.run(main())
