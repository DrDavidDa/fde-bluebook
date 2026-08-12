/* ===== FDE 蓝皮书 · 交互引擎 ===== */

/* ---- 滚动显现（首屏即时可见，仅首屏以下做动画；?noanim 可关闭） ---- */
const NOANIM = /noanim/.test(location.search);
/* 调试验证用：?scrollto=N 加载后滚动到指定位置 */
const _st=location.search.match(/scrollto=(\d+)/);
if(_st) window.addEventListener('load',()=>setTimeout(()=>window.scrollTo(0,+_st[1]),80));
/* 调试截图用：?shift=N 将页面整体上移 N px（headless 截图总从原点开始） */
const _sh=location.search.match(/shift=(\d+)/);
if(_sh) document.body.style.transform='translateY(-'+_sh[1]+'px)';
if(NOANIM) document.documentElement.classList.add('noanim');
document.querySelectorAll('.reveal').forEach(el=>{
  if(!NOANIM && el.getBoundingClientRect().top > window.innerHeight*0.95) el.classList.add('pre');
});
function activate(el){
  el.classList.remove('pre');
  if(el.dataset.count) runCounter(el);
  if(el.classList.contains('vbars')) runBars(el);
  if(el.classList.contains('funnel')) runFunnel(el);
  if(el.classList.contains('hbars')) runHbars(el);
}
const io = new IntersectionObserver(es=>{
  es.forEach(e=>{ if(e.isIntersecting){ activate(e.target); io.unobserve(e.target); } });
},{threshold:.15});
document.querySelectorAll('.reveal').forEach(el=>io.observe(el));
/* 保险丝：2 秒后仍在视口内的隐藏元素强制显示并播动画；?noanim 时全部立即就位 */
setTimeout(()=>{ document.querySelectorAll('.reveal').forEach(el=>{
  if(NOANIM || (el.classList.contains('pre') && el.getBoundingClientRect().top < window.innerHeight)) activate(el);
}); },NOANIM ? 0 : 2000);

/* ---- 数字滚动 ---- */
function runCounter(el){
  const raw = el.dataset.count, target = parseFloat(raw);
  const fmt = el.dataset.fmt || (v=>Math.round(v).toLocaleString());
  const t0 = performance.now(), dur = 1800;
  (function tick(t){
    const p = Math.min((t-t0)/dur,1), e = 1-Math.pow(1-p,3);
    el.textContent = fmt(target*e);
    if(p<1) requestAnimationFrame(tick);
  })(t0);
}

/* ---- 对比柱 ---- */
function runBars(box){
  box.querySelectorAll('.fill').forEach(f=>{ f.style.height = f.dataset.h; });
}

/* ---- 漏斗 ---- */
function runFunnel(box){
  box.querySelectorAll('.fstage').forEach((s,i)=>{
    const apply=()=>{ s.style.width = s.dataset.w; s.style.opacity=1; };
    if(NOANIM) apply(); else setTimeout(apply, i*220);
  });
}

/* ---- KPI 前后对照条 ---- */
function runHbars(box){
  box.querySelectorAll('.after').forEach(a=>{ if(a.dataset.w) a.style.width = a.dataset.w; });
}

/* ---- RAG 管道节点 ---- */
document.querySelectorAll('.pipeline').forEach(pl=>{
  const detail = pl.parentElement.querySelector('.pdetail');
  pl.querySelectorAll('.pnode').forEach(n=>{
    n.addEventListener('click',()=>{
      pl.querySelectorAll('.pnode').forEach(x=>x.classList.remove('on'));
      n.classList.add('on');
      detail.innerHTML = '<b style="color:var(--red)">'+n.dataset.t+'</b><br>'+n.dataset.d;
      detail.classList.add('show');
    });
  });
});

/* ---- 架构层折叠 ---- */
document.querySelectorAll('.layer').forEach(l=>{
  l.addEventListener('click',()=>l.classList.toggle('open'));
});

/* ================= 测验引擎 ================= */
/* 题目数据在页面内 <script> 以 FDE_QUIZ 注入：
   {dims:[..], questions:[{t, opts:[{t, s:[d1,d2..]}]}], verdicts:[[min,label,advice]..]} */
document.querySelectorAll('.quiz').forEach(box=>{
  const spec = window[box.dataset.quiz];
  if(!spec) return;
  const form = document.createElement('div');
  spec.questions.forEach((q,qi)=>{
    const qd = document.createElement('div'); qd.className='q';
    qd.innerHTML = '<div class="qt"><span class="qn">'+String(qi+1).padStart(2,'0')+'</span>'+q.t+'</div>';
    q.opts.forEach((o,oi)=>{
      const lb = document.createElement('label');
      lb.innerHTML = '<input type="radio" name="q'+qi+'" value="'+oi+'">'+o.t;
      lb.addEventListener('click',()=>{
        qd.querySelectorAll('label').forEach(x=>x.classList.remove('sel'));
        lb.classList.add('sel');
      });
      qd.appendChild(lb);
    });
    form.appendChild(qd);
  });
  const btn = document.createElement('button');
  btn.className='btn gold'; btn.textContent=spec.btn||'生成我的报告';
  const out = document.createElement('div'); out.className='quiz-result';
  btn.addEventListener('click',()=>{
    const sums = spec.dims.map(()=>0), cnts = spec.dims.map(()=>0);
    let answered=0;
    spec.questions.forEach((q,qi)=>{
      const sel = form.querySelector('input[name=q'+qi+']:checked');
      if(!sel) return; answered++;
      const o = q.opts[+sel.value];
      o.s.forEach((v,di)=>{ sums[di]+=v; cnts[di]++; });
    });
    if(answered<spec.questions.length){ btn.textContent='还有题目没答完（'+answered+'/'+spec.questions.length+'）'; return; }
    const scores = sums.map((s,i)=>+(s/cnts[i]).toFixed(1));
    const total = +(scores.reduce((a,b)=>a+b,0)/scores.length).toFixed(1);
    let verdict = spec.verdicts[spec.verdicts.length-1];
    for(const v of spec.verdicts){ if(total<=v[0]){ verdict=v; break; } }
    drawPoster(out, spec, scores, total, verdict);
    try{ RS.data.quiz[box.dataset.quiz]={total:total,verdict:verdict[1],scores:scores}; RS.save(); }catch(e){}
  });
  box.appendChild(form); box.appendChild(btn); box.appendChild(out);
});

/* ---- 海报绘制（canvas 雷达图，可下载） ---- */
function drawPoster(out, spec, scores, total, verdict){
  out.innerHTML='';
  const W=760,H=920,cv=document.createElement('canvas');
  cv.width=W*2; cv.height=H*2; cv.style.width='100%';
  const c=cv.getContext('2d'); c.scale(2,2);
  // 背景
  const g=c.createLinearGradient(0,0,W,H);
  g.addColorStop(0,'#ffffff'); g.addColorStop(1,'#eef1f6');
  c.fillStyle=g; c.fillRect(0,0,W,H);
  c.fillStyle='#b45309'; c.font='700 20px monospace'; c.textAlign='center';
  c.fillText(spec.title, W/2, 54);
  c.fillStyle='#5a6478'; c.font='12px monospace';
  c.fillText('FDE 工程师蓝皮书 · '+location.hostname, W/2, 78);
  // 雷达图
  const cx=W/2, cy=430, R=210, n=spec.dims.length, max=spec.max||5;
  c.strokeStyle='#d5dbe7'; c.fillStyle='#5a6478'; c.font='13px sans-serif';
  for(let ring=1;ring<=max;ring++){
    c.beginPath();
    for(let i=0;i<=n;i++){
      const a=-Math.PI/2+i*2*Math.PI/n, r=R*ring/max;
      const x=cx+r*Math.cos(a), y=cy+r*Math.sin(a);
      i?c.lineTo(x,y):c.moveTo(x,y);
    }
    c.stroke();
  }
  for(let i=0;i<n;i++){
    const a=-Math.PI/2+i*2*Math.PI/n;
    c.beginPath(); c.moveTo(cx,cy); c.lineTo(cx+R*Math.cos(a),cy+R*Math.sin(a)); c.stroke();
    const lx=cx+(R+34)*Math.cos(a), ly=cy+(R+34)*Math.sin(a);
    c.fillStyle='#3c465c'; c.font='600 14px sans-serif';
    c.fillText(spec.dims[i]+' '+scores[i], lx, ly);
  }
  c.beginPath();
  for(let i=0;i<=n;i++){
    const a=-Math.PI/2+(i%n)*2*Math.PI/n, r=R*scores[i%n]/max;
    const x=cx+r*Math.cos(a), y=cy+r*Math.sin(a);
    i?c.lineTo(x,y):c.moveTo(x,y);
  }
  c.closePath();
  c.fillStyle='rgba(31,111,235,.18)'; c.fill();
  c.strokeStyle='#1f6feb'; c.lineWidth=2.5; c.stroke(); c.lineWidth=1;
  // 结论
  c.fillStyle='#b45309'; c.font='800 40px monospace';
  c.fillText(verdict[1], W/2, 750);
  c.fillStyle='#5a6478'; c.font='15px sans-serif';
  wrapText(c, verdict[2], W/2, 785, W-120, 24);
  c.fillStyle='#5a6478'; c.font='11px monospace';
  c.fillText('综合 '+total+' / '+(spec.max||5)+' · 长按或下载分享', W/2, 880);
  out.appendChild(cv);
  const dl=document.createElement('a');
  dl.className='btn'; dl.textContent='下载海报'; dl.style.marginTop='14px';
  dl.download=spec.title+'.png'; dl.href=cv.toDataURL('image/png');
  out.appendChild(dl);
}
function wrapText(c,text,x,y,maxW,lh){
  const words=text.split(''); let line='';
  for(const ch of words){
    if(c.measureText(line+ch).width>maxW){ c.fillText(line,x,y); line=ch; y+=lh; }
    else line+=ch;
  }
  c.fillText(line,x,y);
}

/* ================= ROI 计算器 ================= */
document.querySelectorAll('[data-calc=roi]').forEach(box=>{
  const P = {cost:{l:'被替代人力月成本',u:' 元/月',min:10000,max:500000,step:5000,v:80000},
             vol:{l:'日处理任务量',u:' 件/天',min:50,max:10000,step:50,v:1000},
             auto:{l:'预期自动化率',u:'%',min:10,max:90,step:5,v:60},
             inv:{l:'项目总投入',u:' 元',min:100000,max:5000000,step:50000,v:800000}};
  const state={};
  const sl=document.createElement('div'); sl.className='sliders';
  Object.entries(P).forEach(([k,p])=>{
    state[k]=p.v;
    const d=document.createElement('div'); d.className='sld';
    d.innerHTML='<label>'+p.l+'<b id="roi-'+k+'">'+p.v.toLocaleString()+p.u+'</b></label>'+
      '<input type="range" min="'+p.min+'" max="'+p.max+'" step="'+p.step+'" value="'+p.v+'">';
    d.querySelector('input').addEventListener('input',e=>{
      state[k]=+e.target.value;
      d.querySelector('b').textContent=(+e.target.value).toLocaleString()+p.u;
      calc();
    });
    sl.appendChild(d);
  });
  const out=document.createElement('div'); out.className='roi-out';
  out.innerHTML='<div class="roi-box"><div class="v" id="roi-gain">—</div><div class="k">年净收益（估）</div></div>'+
    '<div class="roi-box"><div class="v" id="roi-pay">—</div><div class="k">回本周期（月）</div></div>'+
    '<div class="roi-box"><div class="v" id="roi-judge">—</div><div class="k">速判</div></div>';
  box.appendChild(sl); box.appendChild(out);
  function calc(){
    const gain = state.cost*12*(state.auto/100)*0.7 - state.inv/3; // 摊三年运营成本近似
    const pay = gain>0 ? (state.inv/(state.cost*12*(state.auto/100)*0.7))*12 : Infinity;
    document.getElementById('roi-gain').textContent = gain>0? '¥'+Math.round(gain/10000)+'万':'亏损';
    document.getElementById('roi-pay').textContent = isFinite(pay)? pay.toFixed(1):'>36';
    const j = document.getElementById('roi-judge');
    if(!isFinite(pay)||pay>18){ j.textContent='先别做'; j.style.color='var(--red)'; }
    else if(pay>9){ j.textContent='再算算'; j.style.color='var(--gold)'; }
    else { j.textContent='值得做'; j.style.color='var(--green)'; }
  }
  calc();
});

/* ---- 当前章节导航高亮 ---- */
(function(){
  const id = document.body.dataset.ch;
  if(!id) return;
  document.querySelectorAll('.map-links a').forEach(a=>{
    if(a.dataset.ch===id) a.classList.add('cur');
  });
})();

/* ---- 阅读进度条 ---- */
(function(){
  const bar = document.getElementById('readbar');
  if(!bar) return;
  const upd = ()=>{
    const h = document.documentElement;
    const p = h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight);
    bar.style.width = (p*100).toFixed(1) + '%';
  };
  window.addEventListener('scroll', upd, {passive:true});
  upd();
})();

/* ================= v4 · 滚动叙事引擎 =================
   结构：<div class="scrolly" data-scene="xxx"><div class="stage">…</div>
         <div class="steps"><div class="sstep">…</div>…</div></div>
   场景控制器注册在 window.FDE_SCENES[sceneName](stepIndex)。 */
document.querySelectorAll('.scrolly').forEach(sc=>{
  const steps=[...sc.querySelectorAll('.sstep')];
  const name=sc.dataset.scene;
  if(!steps.length) return;
  const apply=i=>{
    steps.forEach((s,j)=>s.classList.toggle('on',j===i));
    if(name==='tombs'){
      sc.querySelectorAll('.stcard').forEach((c,j)=>c.classList.toggle('on',j===i));
    } else if(window.FDE_SCENES && window.FDE_SCENES[name]){
      window.FDE_SCENES[name](i);
    }
  };
  const sio=new IntersectionObserver(es=>{
    es.forEach(e=>{ if(e.isIntersecting) apply(steps.indexOf(e.target)); });
  },{rootMargin:'-42% 0px -42% 0px'});
  steps.forEach(s=>sio.observe(s));
  /* 初始：第一步点亮；noanim（截图/打印）直接呈现最后一步终态 */
  apply(NOANIM ? steps.length-1 : 0);
});

/* ---- 进度条锚点刻度（对应章内 h2 位置，随窗口尺寸重排） ---- */
(function(){
  const ticks=document.getElementById('readticks');
  if(!ticks) return;
  const hs=document.querySelectorAll('.chapter h2');
  if(!hs.length) return;
  const place=()=>{
    const h=document.documentElement;
    const total=Math.max(1,h.scrollHeight-h.clientHeight);
    ticks.innerHTML='';
    hs.forEach(h2=>{
      const i=document.createElement('i');
      i.style.left=Math.min(100,(h2.offsetTop/total*100)).toFixed(2)+'%';
      ticks.appendChild(i);
    });
  };
  window.addEventListener('load',place);
  window.addEventListener('resize',place);
  place();
})();

/* ================= v4 · 粘性体系 ReadingStore ================= */
const RS_KEY='fde-rs-v1';
const RS={
  data:null,
  load(){ try{ this.data=JSON.parse(localStorage.getItem(RS_KEY))||{}; }catch(e){ this.data={}; }
    this.data.ch=this.data.ch||{}; this.data.cards=this.data.cards||[]; this.data.quiz=this.data.quiz||{}; },
  save(){ try{ localStorage.setItem(RS_KEY,JSON.stringify(this.data)); }catch(e){} },
  progress(ch,p){ const d=this.data.ch[ch]||{p:0,done:false};
    if(p>d.p) d.p=Math.round(p); if(p>=92) d.done=true; this.data.ch[ch]=d; },
  collect(id){ if(this.data.cards.includes(id)) return false; this.data.cards.push(id); this.save(); return true; },
};
RS.load();

/* 滚动进度记录（防抖保存） */
(function(){
  const ch=document.body.dataset.ch;
  if(!ch || ch==='index') return;
  let dirty=false, tid=null;
  const upd=()=>{
    const h=document.documentElement;
    const p=h.scrollTop/Math.max(1,h.scrollHeight-h.clientHeight)*100;
    RS.progress(ch,p); dirty=true;
    if(!tid) tid=setTimeout(()=>{ if(dirty){RS.save();dirty=false;} tid=null; },800);
  };
  window.addEventListener('scroll',upd,{passive:true});
  window.addEventListener('pagehide',()=>{ if(dirty) RS.save(); });
  upd();
})();

/* 顶导航完成勾 */
(function(){
  document.querySelectorAll('.map-links a').forEach(a=>{
    const cid=a.dataset.ch;
    if(cid && RS.data.ch[cid] && RS.data.ch[cid].done) a.classList.add('done');
  });
})();

/* Toast */
function fdeToast(msg){
  let t=document.querySelector('.fdetoast');
  if(!t){ t=document.createElement('div'); t.className='fdetoast'; document.body.appendChild(t); }
  t.textContent=msg; t.classList.add('show');
  clearTimeout(t._tid); t._tid=setTimeout(()=>t.classList.remove('show'),2200);
}

/* 速查卡收藏 */
document.querySelectorAll('.collect').forEach(btn=>{
  const id=btn.dataset.card;
  if(RS.data.cards.includes(id)){ btn.textContent='✓ 已入卡册'; btn.classList.add('got'); }
  btn.addEventListener('click',()=>{
    if(RS.collect(id)){
      btn.textContent='✓ 已入卡册'; btn.classList.add('got');
      fdeToast('已收进卡册（'+RS.data.cards.length+' / 11）· 到「卡册」页查看收集进度');
    } else {
      fdeToast('这张卡已经在你的卡册里了');
    }
  });
});

/* ================= v4 · 决策树可点击 ================= */
document.querySelectorAll('.dt-opts').forEach(box=>{
  box.querySelectorAll('.dt-opt').forEach(opt=>{
    opt.addEventListener('click',()=>{
      const was=opt.classList.contains('on');
      box.querySelectorAll('.dt-opt').forEach(x=>x.classList.remove('on'));
      if(!was) opt.classList.add('on');
    });
  });
});
