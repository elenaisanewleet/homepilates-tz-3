/* Development QA. Run against a local HTTP server serving review/. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium, webkit, devices} = require('playwright');
const origin = process.env.REVIEW_ORIGIN || 'http://127.0.0.1:8444';
const root = path.resolve(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(root,'design/shared/content.json')));
const slugs = Object.keys(data.pages);
const widths = [320,360,390,430,768,1024,1440];
const address = slug => origin + '/site/' + (slug ? slug + '/' : '') + 'index.html';
const alpha = n => {n/=255; return n<=0.04045 ? n/12.92 : ((n+0.055)/1.055)**2.4};
function contrast(a,b) {
  const lum = rgb => rgb.match(/[\d.]+/g).slice(0,3).map(Number).map(alpha).reduce((sum,x,i)=>sum+x*[.2126,.7152,.0722][i],0);
  const l=[lum(a),lum(b)].sort((a,b)=>b-a);
  return +((l[0]+.05)/(l[1]+.05)).toFixed(2);
}
async function run(engine, name) {
 const browser = await engine.launch(name==='Chrome'?{channel:'chrome'}:{});
 const report={engine:name,version:browser.version(),layouts:[],menus:[],interactions:[],localTargets:0,contrast:{},errors:[]};
 try {
  const ctx = await browser.newContext({viewport:{width:390,height:844},hasTouch:true,reducedMotion:'reduce'});
  const page=await ctx.newPage();page.setDefaultTimeout(6500);
  page.on('pageerror',e=>report.errors.push(e.message));
  page.on('console',m=>{if(m.type()==='error')report.errors.push(m.text())});
  page.on('response',r=>{if(r.url().startsWith(origin)&&r.status()>=400)report.errors.push(r.status()+' '+r.url())});
  await page.goto(address(''));
  await page.locator('[name=essential]').click();
  const urls=new Set();
  for(const width of widths){
   await page.setViewportSize({width,height:width<=430?700:900});
   for(const slug of slugs){
    await page.goto(address(slug));await page.evaluate(()=>document.fonts.ready);
    const result=await page.evaluate(async()=>{
     if(document.querySelector('.tariff')) document.querySelectorAll('.tariff').forEach(el=>el.open=true);
     const rect=el=>el.getBoundingClientRect();
     const visible=el=>rect(el).width>0 && rect(el).height>0;
     const header=[...document.querySelectorAll('.bar .brand,.bar .nav a,.cab,.burger')].filter(visible).map(rect).sort((a,b)=>a.left-b.left);
     const overflow=[...document.querySelectorAll('header *, main *, footer *')].filter(e=>visible(e)&&!(e.closest('thead') && getComputedStyle(e.closest('thead')).clipPath!=='none') && rect(e).width>2 && (rect(e).left < -1||rect(e).right > innerWidth+1)).slice(0,8).map(e=>e.tagName+'.'+e.className);
     const images=[...document.images];images.forEach(i=>i.loading='eager'); await Promise.all(images.map(i=>i.decode()));
     const targets=[...document.querySelectorAll('.burger,.cab,.actions a,.gallery-controls button,main summary,.tariff-grid .action')].filter(visible);
     const undersized=targets.filter(e=>rect(e).width<43.99||rect(e).height<43.99).map(e=>e.className||e.tagName);
     const hero=document.querySelector('.hero'), h=hero && rect(hero.querySelector('h1')), cta=hero && rect(hero.querySelector('.actions')),photo=hero &&rect(hero.querySelector('.frames'));
     const lines=hero && [...hero.querySelectorAll('.hero-copy > *')].map(rect);
     return {width:innerWidth,scroll:document.documentElement.scrollWidth,overflow, undersized,
      overlaps:header.some((r,i)=>i&&header[i-1].right>r.left+.5)||(lines&&lines.some((r,i)=>i&&lines[i-1].bottom>r.top+.5))||false,
      hero:hero&&{ctaBottom:Math.round(cta.bottom),photoTop:Math.round(photo.top),h1:Math.round(h.height)},
      images:images.length, titles:document.querySelectorAll('h1').length,
      glyph:/[←→↗↘↙↖⬈➜☰✕]/u.test(document.body.textContent),
      urls:[...document.querySelectorAll('a[href],img[src],script[src],link[href]')].map(e=>e.href||e.src).filter(x=>x&&x.startsWith(location.origin))};
    });
    const label=name+' '+width+' /'+slug;
    assert.equal(result.width,width,label);assert.equal(result.scroll,width,label);assert.deepEqual(result.overflow,[],label);assert.equal(result.titles,1,label);assert.equal(result.overlaps,false,label);assert.deepEqual(result.undersized,[],label);assert.equal(result.glyph,false,label);
    if(!slug && width<768)assert(result.hero.ctaBottom<=result.hero.photoTop,label);
    result.urls.forEach(u=>urls.add(u));delete result.urls;report.layouts.push({slug:slug||'/',...result});
   }
   if(width<1024){
    await page.goto(address('stoimost'));
    const trigger=page.locator('.burger'),dialog=page.locator('.menu-drawer');await trigger.focus();await page.keyboard.press('Enter');
    assert(await dialog.evaluate(e=>e.matches(':modal')));assert.equal(await dialog.locator('a[aria-current]').textContent(),'Стоимость');
    assert.equal(await dialog.locator('.drawer-links a').count(),8);
    const nav=await dialog.locator('.drawer-links a').evaluateAll(as=>as.map(a=>({top:a.offsetTop,h:a.offsetHeight})));
    assert(nav.every((r,i)=>r.h>=44&&(!i||r.top>=nav[i-1].top+nav[i-1].h)));
    await page.locator('main a').first().evaluate(e=>e.focus());assert(await dialog.evaluate(e=>e.contains(document.activeElement)));
    await page.keyboard.press('Escape');await page.waitForFunction(()=>!document.querySelector('dialog').open);
    assert(await trigger.evaluate(e=>document.activeElement===e));
    await trigger.click();await dialog.locator('.drawer-close').click();assert(!(await dialog.isVisible()));
    await trigger.click();await dialog.locator('a[aria-label="FAQ"]').click();await page.waitForURL(address('faq'));assert(!(await dialog.isVisible()));
    report.menus.push({width,items:nav.length,active:'Стоимость',backgroundFocusBlocked:true,close:'Escape, кнопка и переход'});
   }
  }
  for(const u of urls){ const response=await ctx.request.get(u);assert.equal(response.status(),200,u);
   if(new URL(u).hash){await page.goto(u);assert.equal(await page.locator(new URL(u).hash).count(),1,u)} }
  report.localTargets=urls.size;
  await page.setViewportSize({width:320,height:420});await page.goto(address(''));await page.locator('.burger').click();
  await page.locator('.drawer-account').scrollIntoViewIfNeeded();
  assert(await page.locator('dialog').evaluate(e=>e.scrollHeight>e.clientHeight && e.scrollTop>0));
  await page.locator('.drawer-account').click();await page.waitForURL(address('')+'#cabinet');
  assert(!(await page.locator('dialog').isVisible()));report.interactions.push('Меню 320×420 прокручивается до кабинета и закрывается по ссылке');
  await page.goto(address(''));await page.locator('[data-next]').click();assert.match(await page.locator('[data-count]').innerText(),/02/);await page.locator('[data-prev]').click();assert.match(await page.locator('[data-count]').innerText(),/01/);
  const palette=await page.evaluate(()=>{const color=(sel,prop)=>getComputedStyle(document.querySelector(sel))[prop];return {cta:[color('.hero .action','color'),color('.hero .action','backgroundColor')],accent:[color('h1 em','color'),color('.hero','backgroundColor')],legend:[color('.plate figcaption b','color'),color('.plate','backgroundColor')]}});
  for(const [key,pair] of Object.entries(palette)){report.contrast[key]=contrast(...pair);assert(report.contrast[key]>=4.5,key)}
  await page.goto(address('stoimost'));
  const rows=await page.locator('.tariff').evaluateAll(groups=>groups.map(g=>[...g.querySelectorAll('tbody tr')].map(r=>[...r.cells].map(td=>td.textContent))));
  assert.deepEqual(rows,data.prices.groups.map(g=>g.rows));const second=page.locator('.tariff').nth(1);await second.locator('summary').focus();await page.keyboard.press('Space');assert(await second.evaluate(e=>e.open));
  await page.goto(address('faq'));const faq=page.locator('main details');assert.equal(await faq.count(),data.faq.items.length);await faq.first().locator('summary').click();assert(await faq.first().evaluate(e=>e.open));
  await page.goto(address('kontakty'));const f=page.locator('[data-feedback]');await f.locator('input[type=tel]').fill('0000000000');await f.locator('textarea').fill('Проверка');assert(!(await f.evaluate(e=>e.checkValidity())));await f.locator('[type=checkbox]').check();await f.locator('[type=submit]').click();assert.match(await f.locator('[role=status]').innerText(),/прототипе/);
  await page.locator('[data-cookie-open]').click();await page.locator('[name=essential]').click();assert(!(await page.locator('.cookie-box').isVisible()));
  report.interactions.push('Галерея вперёд и назад','33 тарифа, все ячейки совпадают с данными V3','Раскрытие категорий, FAQ','Валидация и локальный ответ формы','Повторное открытие и закрытие настроек cookie');
  if(name==='WebKit') {
   const iphone=await browser.newContext({...devices['iPhone 13'],reducedMotion:'reduce'});
   const touch=await iphone.newPage();await touch.goto(address(''));
   await touch.locator('[name=essential]').tap();await touch.locator('.burger').tap();
   assert(await touch.locator('dialog').evaluate(e=>e.matches(':modal')));
   await touch.locator('.drawer-links a[aria-label="Стоимость"]').tap();
   await touch.waitForURL(address('stoimost'));
   assert(await touch.locator('.cab svg').isVisible());
   report.iPhoneEmulation={preset:'iPhone 13',userAgent:await touch.evaluate(()=>navigator.userAgent),width:await touch.evaluate(()=>innerWidth),touchMenuAndNavigation:true};
   await iphone.close();
  }
  assert.deepEqual(report.errors,[]);return report;
 }finally{await browser.close()}
}
(async()=>{const out=path.join(root,'review/verification');
 const results=await Promise.all([run(chromium,'Chrome'),run(webkit,'WebKit')]);
 fs.writeFileSync(path.join(out,'v4-browser.json'),JSON.stringify(results,null,2)+'\n');
 console.log(results.map(x=>[x.engine,x.layouts.length,x.menus.length,x.contrast,x.errors.length]));
})().catch(e=>{console.error(e);process.exitCode=1});
