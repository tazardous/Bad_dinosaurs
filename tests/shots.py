import sys, asyncio
from playwright.sync_api import sync_playwright
CH='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
OUT=sys.argv[1] if len(sys.argv)>1 else '/tmp/shots'
import os; os.makedirs(OUT,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CH,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':800,'height':400})
    errs=[]
    pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
    pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.goto('file:///home/claude/bad_dinosaurs/index.html')
    pg.wait_for_timeout(800)
    pg.evaluate("window.__DDmanual=true")
    def frames(n):
        pg.evaluate(f"for(let i=0;i<{n};i++)__DD.step(); __DD.draw()")
    frames(5); pg.screenshot(path=f'{OUT}/title.png')
    pg.evaluate("__DD.state='select'"); frames(5); pg.screenshot(path=f'{OUT}/select.png')
    for L in range(5):
        pg.evaluate(f"__DD.startLevel({L})"); frames(30)
        pg.screenshot(path=f'{OUT}/level{L+1}.png')
    pg.evaluate("__DD.startLevel(0)"); frames(5)
    pg.evaluate("__DD.P.x=__DD.LV.gates[0].tx*16-10"); frames(10)
    print('state',pg.evaluate("__DD.state"))
    for name,gens in [('letters',['letterFind','startLetter','nextLetter']),('numbers',['count','add','nextNum']),('shapes',['shapeFind','shapeName','sides']),('colors',['colorFind','pattern','mix','colorName'])]:
        for d in (0,1):
            for gname in gens:
                pg.evaluate(f"__DD.setDiff({d}); __DD.state='play'; __DD.startLevel(0); __DD.P.x=__DD.LV.gates[0].tx*16-10; for(let i=0;i<4;i++)__DD.step();")
                pg.evaluate(f"(()=>{{const q=__DD.GEN.{gname}(); __DD.quiz&&Object.assign(__DD.quiz,{{q}}); __DD.draw();}})()")
                if d==1 or gname in('letterFind','count','shapeFind','colorFind'):
                    pg.screenshot(path=f'{OUT}/q_{gname}_{d}.png')
    print('errors',errs)
    b.close()
