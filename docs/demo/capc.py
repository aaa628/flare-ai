import asyncio
from playwright.async_api import async_playwright
SITE="file:///home/user/flare-ai/site/index.html"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={"width":1280,"height":720}, device_scale_factor=1.5)
        for i,label in enumerate(["Three opposed-flow rods","FLEX: methanol droplets","Two different experiments"]):
            await pg.goto(SITE+"#/compare"); await pg.wait_for_timeout(800)
            await pg.click(f"main button:has-text('{label}')"); await pg.wait_for_timeout(900)
            n=await pg.evaluate("document.querySelectorAll('main svg').length")
            # scroll so the first chart sits near the top
            await pg.evaluate("var s=[...document.querySelectorAll('main svg')].filter(e=>e.getBoundingClientRect().width>200)[0]; if(s){s.closest('.card,section')?.scrollIntoView({block:'start'}); window.scrollBy(0,-175)}")
            await pg.wait_for_timeout(400); await pg.screenshot(path=f"cmp{i+1}.png"); print(label, n)
        await b.close()
asyncio.run(main())
