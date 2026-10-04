"""Play-test bot for Dino Dinner Dash.
Plays every level at both difficulties (walks right, jumps pits/walls/critters, answers
every gate - the first one wrong on purpose), checks the level ends, checks falling
into a pit respawns, and runs a real-time (not stepped) session with the keyboard."""
import sys
from playwright.sync_api import sync_playwright
CH='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
URL='file://'+__file__.rsplit('/tests/',1)[0]+'/index.html'
BOT="""
window.bot=function(maxFrames,wrongFirst){
  const D=__DD,P=D.P,T=16; let frames=0,falls=0,quizzes=0,lastX=-1,stuck=0,maxStuck=0;
  const solid=c=>c==='#'||c==='G';
  while(frames<maxFrames&&D.state!=='levelEnd'){
    frames++;
    if(D.state==='quiz'){
      const q=D.quiz;
      if(!q.done){ if(wrongFirst&&quizzes%2===0){ const w=q.q.choices.findIndex((c,i)=>i!==q.q.ans); D.answer(w); } D.answer(q.q.ans); quizzes++; }
      D.hit.add('start'); D.step(); continue;
    }
    if(D.state!=='play') return {fail:'bad state '+D.state,frames};
    const LV=D.LV, tile=(tx,ty)=>(tx<0||tx>=LV.W)?'#':(ty<0||ty>=LV.H)?' ':LV.t[ty][tx];
    const px=P.x+P.w, feetRow=Math.floor((P.y+P.h-1)/T);
    D.down.right=true; let jump=false;
    const aheadTx=Math.floor((px+4)/T);
    for(let r=feetRow-1;r<=feetRow;r++) if(solid(tile(aheadTx,r))) jump=true;
    const gTx=Math.floor((px+6)/T); let ground=false; for(let r=LV.top;r<LV.H;r++) if(solid(tile(gTx,r))) ground=true;
    if(!ground) jump=true;
    for(const c of LV.crits) if(c.alive&&c.x>P.x&&c.x-P.x<34&&Math.abs(c.y-P.y)<24) jump=true;
    D.down.jump=false; if(jump&&P.ground){ D.hit.add('jump'); D.down.jump=true; }
    D.step();
    if(P.inv===90) falls++;
    if(Math.abs(P.x-lastX)<0.01){ stuck++; maxStuck=Math.max(maxStuck,stuck); } else stuck=0; lastX=P.x;
    if(stuck>400) return {fail:'stuck at x='+P.x+' tile '+Math.floor(P.x/T),frames};
  }
  D.down.right=false; D.down.jump=false;
  return {ok:D.state==='levelEnd',frames,falls,quizzes,stars:D.LV.stars,gates:D.LV.gates.length,berries:D.LV.got,maxStuck};
};
"""
fails=0
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CH,args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':800,'height':400})
    errs=[]
    pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.on('console',lambda m: errs.append(m.text) if m.type=='error' and 'Failed to load resource' not in m.text else None)
    pg.goto(URL); pg.wait_for_timeout(500)
    pg.evaluate("window.__DDmanual=true"); pg.evaluate(BOT+";0")
    for diff in (0,1):
        for L in range(5):
            pg.evaluate(f"__DD.setDiff({diff}); __DD.startLevel({L}); for(const k in __DD.down) __DD.down[k]=false;")
            r=pg.evaluate("bot(9000,true)")
            ok=r.get('ok') and r['quizzes']==r['gates']
            print(('PASS' if ok else 'FAIL'),f'diff={diff} level={L+1}',r)
            fails+=0 if ok else 1
    # fall recovery: drop the hero into the first pit and keep stepping
    pg.evaluate("__DD.startLevel(0)")
    r=pg.evaluate("""(()=>{const D=__DD,P=D.P; P.x=26*16+8; P.y=8*16; P.vy=0; let f=0; while(f<200){D.step(); f++; if(P.inv===90) break;} const ok=P.inv>0&&P.y<8*16&&D.state==='play'; 
       // after respawn the hero can walk and jump again
       D.down.right=true; const x0=P.x; for(let i=0;i<60;i++) D.step(); D.down.right=false; return {ok,moved:P.x-x0,y:P.y,frames:f}})()""")
    print('PASS' if r['ok'] and r['moved']>20 else 'FAIL','fall recovery',r); fails+=0 if r['ok'] and r['moved']>20 else 1
    # tap targets: tapping a choice card answers it
    pg.evaluate("__DD.startLevel(0); __DD.P.x=__DD.LV.gates[0].tx*16-10; for(let i=0;i<4;i++)__DD.step(); __DD.draw();")
    r=pg.evaluate("""(()=>{const D=__DD; const q=D.quiz; if(!q) return {ok:false}; D.draw(); const card=D.hot.find(h=>h.w>40&&h.h>40&&h.w<100); 
        const idx=q.q.ans; const hs=D.hot.filter(h=>h.w>40&&h.w<100&&h.h>40&&h.h<70); const h=hs[idx]; D.setTap(h.x+h.w/2,h.y+h.h/2); D.step(); return {ok:D.quiz.done,hotCards:hs.length}})()""")
    print('PASS' if r['ok'] else 'FAIL','tap answers',r); fails+=0 if r['ok'] else 1
    # real time: no manual stepping, keyboard only, hero walks off into the first pit and comes back
    pg.evaluate("window.__DDmanual=false; __DD.startLevel(0); __DD.P.x=24*16; for(const k in __DD.down) __DD.down[k]=false")
    pg.keyboard.down('ArrowRight'); pg.wait_for_timeout(2500); pg.keyboard.up('ArrowRight')
    pg.wait_for_timeout(1500)
    r=pg.evaluate("({state:__DD.state,x:__DD.P.x,y:__DD.P.y})"); print('real-time after pit:',r)
    ok=r['state']=='play' and r['y']<8*16+1
    pg.keyboard.down('ArrowRight'); pg.wait_for_timeout(600); pg.keyboard.up('ArrowRight')
    r2=pg.evaluate("({x:__DD.P.x})"); print('PASS' if ok and r2['x']>r['x'] else 'FAIL','real-time recovery, still controllable',r2); fails+=0 if ok and r2['x']>r['x'] else 1
    print('page errors:',errs); fails+=len(errs)
    b.close()
sys.exit(1 if fails else 0)
