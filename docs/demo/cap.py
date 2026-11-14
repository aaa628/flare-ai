import asyncio
from playwright.async_api import async_playwright
SITE="file:///home/user/flare-ai/site/index.html"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={"width":1280,"height":720}, device_scale_factor=1.5)
        async def shot(route, name, scroll=None, click=None, wait=900):
            await pg.goto(SITE+route); await pg.wait_for_timeout(wait)
            if click: await pg.click(click); await pg.wait_for_timeout(700)
            if scroll: await pg.evaluate(f"document.querySelector('{scroll}').scrollIntoView({{block:'start'}}); window.scrollBy(0,-90)"); await pg.wait_for_timeout(400)
            await pg.screenshot(path=name+".png")
        await shot("#/", "s_overview")
        await shot("#/", "s_overview2", scroll=".card")
        await shot("#/investigations/moon", "s_moon")
        await shot("#/investigations/moon", "s_moon_chart", scroll="svg")
        await shot("#/investigations/mars", "s_mars")
        await shot("#/experiment/FLEX-114", "s_record")
        await shot("#/scenario", "s_scen", click="button:has-text('Moon base / rover (brief)')")
        await shot("#/scenario", "s_scen2", click="button:has-text('Moon base / rover (brief)')", scroll=".verdict, .abst, .card")
        await b.close()
asyncio.run(main())
