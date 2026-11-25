"""Smoke test for Dot Calendar.

Serves the project folder over http, renders it in Chromium in four languages and both
themes, checks key holiday dates and the reminder flow, and saves screenshots to
tests/output/. Exits with code 1 if anything fails.

    pip install playwright && playwright install chromium
    python3 tests/smoke.py
"""
import asyncio, datetime, functools, http.server, json, pathlib, sys, threading
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

def first(notes, k):
    """The day's first note. Days hold a list now; old backups held a single object."""
    v = notes.get(k)
    if isinstance(v, list):
        return v[0] if v else {}
    return v or {}

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
    now_ = datetime.datetime.now()
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

        print("Desktop widths and heights")
        # Two bugs hid here before: measuring only #grid missed the logo below it, and testing
        # only short months missed six-row ones. Measure the lowest element, and include
        # August 2027, which needs six rows with a Monday week start.
        for w, h in [(1440, 900), (1366, 768), (1440, 1100), (1600, 1000), (1920, 1080),
                     (1000, 1100), (1280, 800), (2560, 1440), (1512, 982)]:
            for month, rows in [("january-2027", 5), ("august-2027", 6), ("february-2027", 4)]:
                pg, errs = await page_for(b, base, w, h, seed(lang="en", country="TR"), month)
                box = await pg.evaluate(
                    "(() => {const app = document.querySelector('.app'); let bottom = 0, what = '';"
                    " app.querySelectorAll('*').forEach(el => {const r = el.getBoundingClientRect();"
                    "   if (r.width && r.height && getComputedStyle(el).visibility !== 'hidden'"
                    "       && r.bottom > bottom) {bottom = r.bottom; what = el.className || el.tagName}});"
                    " return {bottom, what,"
                    "         dot: document.querySelector('.day').getBoundingClientRect().width,"
                    "         hscroll: document.documentElement.scrollWidth - document.documentElement.clientWidth}})()")
                check(box["hscroll"] <= 0, f"no horizontal scroll at {w}x{h} {month}")
                check(box["bottom"] <= h,
                      f"{rows}-row {month} fits one screen at {w}x{h} "
                      f"(lowest {box['what']} at {box['bottom']:.0f})")
                check(box["dot"] >= 50, f"dots stay legible at {w}x{h} {month} ({box['dot']:.0f}px)")
                check(not errs, f"no script errors at {w}x{h} {month}")
                await pg.context.close()

        print("Month panel")
        pg, errs = await page_for(b, base, 1440, 900, seed(lang="en", country="ES"), "january-2027")
        check(not await pg.is_visible("#ovList"), "panel starts closed")
        check(not await pg.is_visible("#legend"), "legend is not on the calendar screen")
        await pg.click("#bList")
        await pg.wait_for_timeout(500)
        check(await pg.is_visible("#ovList"), "Notes button opens the panel")
        for sel, what in [("#ul", "month list"), ("#lc", "note count"), ("#legend", "legend"),
                          ("#todaybar", "next 24 hours")]:
            check(await pg.is_visible(sel), f"panel holds the {what}")
        panel = await pg.evaluate(
            "(() => {const p = document.querySelector('.ov.pan .side');"
            " return {overflow: getComputedStyle(p).overflowY,"
            "         fromRight: Math.round(document.documentElement.clientWidth - p.getBoundingClientRect().right),"
            "         scrollable: p.scrollHeight >= p.clientHeight}})()")
        check(panel["overflow"] == "auto", "panel scrolls on its own")
        check(panel["fromRight"] == 0, "panel is anchored to the right edge")
        await pg.click("#lDone")
        await pg.wait_for_timeout(400)
        check(not await pg.is_visible("#ovList"), "close button dismisses the panel")
        check(not errs, f"no script errors in the panel {errs}")
        await pg.context.close()

        print("Long words in a sticker")
        # Long text is clipped with an ellipsis rather than shrunk, and a single long word
        # breaks with a hyphen where the browser has a dictionary for the page language.
        # Hyphens depend on the browser, so the check here is the invariant: nothing spills
        # out of the circle, and nothing is shrunk.
        long_notes = {"2027-01-11": [{"id": "w1", "t": "Konstantinopolis", "c": -1, "cat": "work"}],
                      "2027-01-12": [{"id": "w2", "t": "Short", "c": -1, "cat": "work"}],
                      "2027-01-13": [{"id": "w3", "c": -1, "cat": "work",
                                      "t": "Hazirlik toplantisi ve uzun bir aciklama metni daha"}]}
        store2 = ("localStorage.setItem('desklife-cal-v1', "
                  + json.dumps(json.dumps({"notes": long_notes, "weekStart": 1, "country": "ES",
                                           "lang": "tr", "fired": {}})) + ")")
        pg, errs = await page_for(b, base, 1216, 1100, store2, "january-2027")
        sizes = await pg.evaluate(
            "['2027-01-11','2027-01-12','2027-01-13'].map(k => {"
            " const stk = document.querySelector(`[data-k=\"${k}\"] .stk`),"
            "       sp = stk.querySelector('span:last-child'),"
            "       box = stk.getBoundingClientRect(), txt = sp.getBoundingClientRect();"
            " return {font: getComputedStyle(stk).fontSize,"
            "         spills: txt.width > box.width + 1 || sp.scrollWidth > sp.clientWidth + 1,"
            "         clipped: sp.scrollHeight > sp.clientHeight + 1}})")
        # dots differ by a fraction of a pixel, so compare to a tenth
        fonts = [round(float(s_["font"].rstrip("px")), 1) for s_ in sizes]
        check(len(set(fonts)) == 1,
              f"a long word is no longer shrunk; all stickers share one size ({fonts})")
        check(not any(s_["spills"] for s_ in sizes), "no sticker text spills out of its circle")
        check(sizes[2]["clipped"], "text too long for the circle is clipped, with an ellipsis")
        check(not sizes[1]["clipped"], "short text is left alone")
        check(not errs, f"no script errors with long words {errs}")
        await pg.context.close()

        print("Several notes on one day")
        pg, errs = await page_for(b, base, 1280, 950, seed(lang="en", country="ES"), "january-2027")
        await pg.click('[data-k="2027-01-14"]')
        await pg.wait_for_timeout(400)
        check(await pg.is_visible("#nTabs"), "the editor shows the day's notes")

        async def add_note(text, cat, when):
            await pg.click("#nAdd")
            await pg.wait_for_timeout(300)
            await pg.fill("#nText", text)
            await pg.click(f'#cats [data-cat="{cat}"]')
            await pg.check("#rOn")
            await pg.fill("#rTime", when)
            await pg.wait_for_timeout(200)

        await add_note("Lunch", "meeting", "13:00")
        await add_note("Birthday", "birthday", "20:00")
        await pg.wait_for_timeout(300)
        day = await pg.evaluate("JSON.parse(localStorage.getItem('desklife-cal-v1')).notes['2027-01-14']")
        check(len(day) == 3, f"the + button adds notes without replacing (got {len(day)})")
        # the seeded note carries no time, and untimed notes sort first
        check([n.get("r") for n in day] == [None, "13:00", "20:00"],
              f"each note keeps its own time, untimed first ({[n.get('r') for n in day]})")
        check([n.get("cat") for n in day] == ["work", "meeting", "birthday"], "each note keeps its own category and colour")
        check(len({n["id"] for n in day}) == 3, "each note has its own id")

        await pg.click('#nTabs button[data-id]')
        await pg.wait_for_timeout(300)
        await pg.click("#nDel")
        await pg.wait_for_timeout(500)
        left = await pg.evaluate("JSON.parse(localStorage.getItem('desklife-cal-v1')).notes['2027-01-14']")
        check(len(left) == 2, "deleting removes one note, not the day")
        check(await pg.is_visible("#ovNote"), "the editor stays open while notes remain")
        await pg.click("#nDone")
        await pg.wait_for_timeout(300)

        await pg.click("#bList")
        await pg.wait_for_timeout(600)
        listed = await pg.evaluate(
            "[...document.querySelectorAll('#ul li')].map(li => li.innerText.replace(/\\n/g, ' '))")
        on_day = [row for row in listed if "Lunch" in row or "Birthday" in row]
        check(len(on_day) == 2, f"the panel lists every note of the day, not just one ({len(on_day)})")
        check(not errs, f"no script errors with several notes {errs}")
        await pg.context.close()

        print("The circle advances through the day")
        # One circle per day still, but on today it shows the next note yet to come, so the
        # 13:00 one takes over once 11:00 has passed. Ahead of today a day opens on its
        # first note; once every note has passed, and on any past day, it keeps the last.
        # now + 90 minutes wraps past midnight late in the evening, which would reorder the
        # day and break the premise. Keep the middle note inside the same day.
        soon = min((now_ + datetime.timedelta(minutes=30)).strftime("%H:%M"), "23:58")
        three = [{"id": "a", "t": "Meeting", "c": -1, "cat": "meeting", "r": "00:01"},
                 {"id": "b", "t": "Lunch", "c": -1, "cat": "", "r": soon},
                 {"id": "c", "t": "Birthday", "c": -1, "cat": "birthday", "r": "23:59"}]
        days = {now_.strftime("%Y-%m-%d"): three,
                (now_ - datetime.timedelta(days=3)).strftime("%Y-%m-%d"): three,
                (now_ + datetime.timedelta(days=3)).strftime("%Y-%m-%d"): three}
        store = ("localStorage.setItem('desklife-cal-v1', "
                 + json.dumps(json.dumps({"notes": days, "weekStart": 1, "country": "ES",
                                          "lang": "en", "fired": {}})) + ")")
        pg, errs = await page_for(b, base, 1280, 900, store,
                                  now_.strftime("%B").lower() + "-" + now_.strftime("%Y"))
        while await pg.is_visible("#ovRem"):
            await pg.click("#remOk")
            await pg.wait_for_timeout(250)
        async def circle(day):
            return (await pg.inner_text(f'[data-k="{day}"] .stk')).upper()
        ahead = await circle((now_ + datetime.timedelta(days=3)).strftime("%Y-%m-%d"))
        check("MEETING" in ahead, f"a day still ahead opens on its first note ({ahead!r})")
        here = await circle(now_.strftime("%Y-%m-%d"))
        if now_.hour == 23 and now_.minute >= 55:
            print("  skip  today's next-note check: too close to midnight to stage it")
        else:
            check("LUNCH" in here, f"today shows the next note still to come ({here!r})")
        gone = await circle((now_ - datetime.timedelta(days=3)).strftime("%Y-%m-%d"))
        check("BIRTHDAY" in gone, f"a past day keeps its last note ({gone!r})")
        check(not errs, f"no script errors while the circle advances {errs}")
        await pg.context.close()

        print("Upgrading old data")
        # Every seed in this file is written in the pre-list shape, the one real backups on
        # the owner's devices hold. Loading has to convert it without losing anything.
        pg, errs = await page_for(b, base, 1280, 900, seed(lang="en", country="TR"), "january-2027")
        shape = await pg.evaluate("JSON.parse(localStorage.getItem('desklife-cal-v1')).notes")
        check(all(isinstance(v, list) for v in shape.values()), "every day became a list of notes")
        check(all(n.get("id") for v in shape.values() for n in v), "every note was given an id")
        check(first(shape, "2027-01-05").get("t") == "Team meeting"
              and first(shape, "2027-01-05").get("r") == "10:00", "the note itself came through intact")
        check(first(shape, "2027-05-14").get("w") == 1, "reminder settings came through")
        await pg.context.close()

        print("Moving notes by dragging")
        # A mouse drags straight away; a finger must hold still for 300ms first, so that the
        # month swipe and page scrolling keep working. Both paths are checked here.
        async def day_box(pg, k):
            return await (await pg.query_selector(f'[data-k="{k}"]')).bounding_box()

        pg, errs = await page_for(b, base, 1280, 900, seed(lang="en", country="ES"), "january-2027")
        src, dst = await day_box(pg, "2027-01-14"), await day_box(pg, "2027-01-21")
        await pg.mouse.move(src["x"] + src["width"] / 2, src["y"] + src["height"] / 2)
        await pg.mouse.down()
        await pg.mouse.move(src["x"] + src["width"] / 2 + 30, src["y"] + src["height"] / 2, steps=4)
        await pg.mouse.move(dst["x"] + dst["width"] / 2, dst["y"] + dst["height"] / 2, steps=10)
        await pg.mouse.up()
        await pg.wait_for_timeout(600)
        kept = await pg.evaluate("JSON.parse(localStorage.getItem('desklife-cal-v1')).notes")
        check("2027-01-14" not in kept, "dragging a note empties the day it left")
        check(first(kept, "2027-01-21").get("t") == "Release review", "the note lands on the new day")
        check(not await pg.is_visible("#ovNote"), "a drag does not open the note editor")

        src, dst = await day_box(pg, "2027-01-21"), await day_box(pg, "2027-01-05")
        await pg.mouse.move(src["x"] + src["width"] / 2, src["y"] + src["height"] / 2)
        await pg.mouse.down()
        await pg.mouse.move(src["x"] + src["width"] / 2 + 30, src["y"] + src["height"] / 2, steps=4)
        await pg.mouse.move(dst["x"] + dst["width"] / 2, dst["y"] + dst["height"] / 2, steps=10)
        await pg.mouse.up()
        await pg.wait_for_timeout(600)
        both = await pg.evaluate("JSON.parse(localStorage.getItem('desklife-cal-v1')).notes")
        check(first(both, "2027-01-05").get("t") == "Release review"
              and first(both, "2027-01-21").get("t") == "Team meeting",
              "dropping onto a day that already has a note swaps them, losing neither")

        await pg.click('[data-k="2027-01-05"]')
        await pg.wait_for_timeout(400)
        check(await pg.is_visible("#ovNote"), "a plain click still opens the note editor")
        check(not errs, f"no script errors while dragging {errs}")
        await pg.context.close()

        touch = await b.new_context(viewport={"width": 390, "height": 844}, has_touch=True,
                                    is_mobile=True, timezone_id="Europe/Madrid")
        tpg = await touch.new_page()
        terrs = []
        tpg.on("pageerror", lambda e: terrs.append(str(e)))
        await tpg.goto(base + "index.html")
        await tpg.evaluate(seed(lang="en", country="ES"))
        await tpg.goto(base + "index.html#january-2027")
        await tpg.reload()
        await tpg.wait_for_timeout(900)
        gesture = """([ax, ay, bx, by, hold, from]) => new Promise(done => {
          const sheet = document.getElementById('sheet');
          const src = document.querySelector(`[data-k="${from}"]`);
          const fire = (type, x, y, el) => (el || sheet).dispatchEvent(new PointerEvent(type,
            {bubbles: true, cancelable: true, pointerId: 7, pointerType: 'touch',
             isPrimary: true, clientX: x, clientY: y, button: 0}));
          fire('pointerdown', ax, ay, src);
          setTimeout(() => {
            let i = 0;
            const step = () => { i++;
              fire('pointermove', ax + (bx - ax) * i / 10, ay + (by - ay) * i / 10);
              if (i < 10) setTimeout(step, 16); else { fire('pointerup', bx, by); setTimeout(() => done(1), 400) }};
            step();
          }, hold);
        })"""
        for hold, should_move, what in [(420, True, "a 420ms hold then a drag moves the note"),
                                        (80, False, "a quick swipe does not move it, it changes month")]:
            await tpg.goto(base + "index.html#january-2027")
            await tpg.evaluate(seed(lang="en", country="ES"))
            await tpg.reload()
            await tpg.wait_for_timeout(900)
            a = await (await tpg.query_selector('[data-k="2027-01-14"]')).bounding_box()
            c = await (await tpg.query_selector('[data-k="2027-01-21"]')).bounding_box()
            await tpg.evaluate(gesture, [a["x"] + a["width"] / 2, a["y"] + a["height"] / 2,
                                         c["x"] + c["width"] / 2, c["y"] + c["height"] / 2,
                                         hold, "2027-01-14"])
            now = await tpg.evaluate("JSON.parse(localStorage.getItem('desklife-cal-v1')).notes")
            check(("2027-01-21" in now) == should_move, what)
        check(not terrs, f"no script errors on touch {terrs}")
        await touch.close()

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
        one = saved[0] if isinstance(saved, list) else saved
        check(one.get("cat") == "work" and one.get("t") == "Quarterly report", "editing a note saves text and category")
        check(not errs, f"no script errors in note flow {errs}")
        await pg.context.close()
        await b.close()
    srv.shutdown()
    print(f"\n{'PASS' if not failures else 'FAILED: ' + str(len(failures))} — screenshots in {OUT}")
    sys.exit(1 if failures else 0)

asyncio.run(main())
