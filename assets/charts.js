/* ===== FDE 蓝皮书 · ECharts 图表配置（依赖 echarts + fde-theme） =====
   每个配置函数接收容器 el，返回 chart 实例（存 el._chart）。
   滚动场景通过 window.FDE_SCENES 暴露分步控制器。 */
(function(){
if(!window.echarts) return;
const ANIM = !/noanim/.test(location.search);
const C = {blue:'#1f6feb',red:'#e5484d',gold:'#b45309',green:'#16a34a',violet:'#7c3aed',ink:'#1a2233',dim:'#5a6478',line:'#e3e7ef'};
window.FDE_SCENES = {};
function mk(el){ const ch = echarts.init(el,'fde',{renderer:'canvas'}); el._chart = ch;
  window.addEventListener('resize',()=>ch.resize()); return ch; }

/* ---- ch01 权力地图：散点 + 象限 ---- */
function powermap(el){
  const pts = [
    {name:'掏钱的人', v:[82,78], c:C.green, tag:'高影响 · 支持'},
    {name:'用的人',   v:[74,26], c:C.blue,  tag:'低影响 · 支持'},
    {name:'挡路的人', v:[22,80], c:C.red,   tag:'高影响 · 警惕'},
    {name:'埋数据的人',v:[45,28], c:C.gold, tag:'低影响 · 中立'}];
  const ch = mk(el);
  ch.setOption({
    grid:{left:60,right:40,top:30,bottom:56},
    xAxis:{name:'态度：警惕 → 支持',min:0,max:100,splitLine:{show:false}},
    yAxis:{name:'影响力 →',min:0,max:100,splitLine:{show:false}},
    tooltip:{formatter:p=>'<b>'+p.data.name+'</b><br>'+p.data.tag},
    series:[{type:'scatter',symbolSize:26,
      label:{show:true,position:'top',formatter:'{b}',fontWeight:700,color:C.ink,fontSize:13},
      data:pts.map(p=>({name:p.name,value:p.v,tag:p.tag,itemStyle:{color:p.c}})),
      markLine:{silent:true,symbol:'none',label:{show:false},
        lineStyle:{color:C.line,type:'dashed'},
        data:[{xAxis:50},{yAxis:50}]},
      animationDuration:ANIM?900:0}],
  });
  // 场景控制：点亮第 i 个人，其余压暗
  window.FDE_SCENES.powermap = function(i){
    ch.setOption({series:[{data:pts.map((p,j)=>({name:p.name,value:p.v,tag:p.tag,
      itemStyle:{color:p.c,opacity:(i==null||i===j)?1:.18},
      label:{opacity:(i==null||i===j)?1:.18}}))}]});
  };
}

/* ---- ch02 OpenAI 2→52 面积图 ---- */
function growth(el){
  const ch = mk(el);
  ch.setOption({
    grid:{left:56,right:36,top:40,bottom:44},
    xAxis:{type:'category',data:['2025-01','2025-04','2025-07','2025-10','2025-12'],boundaryGap:false},
    yAxis:{type:'value',name:'FDE 人数',max:60},
    tooltip:{trigger:'axis'},
    series:[{type:'line',smooth:true,symbol:'circle',symbolSize:9,
      data:[2,9,21,38,52],
      lineStyle:{width:3,color:C.blue},
      itemStyle:{color:C.blue},
      areaStyle:{color:{type:'linear',x:0,y:0,x2:0,y2:1,
        colorStops:[{offset:0,color:'rgba(31,111,235,.30)'},{offset:1,color:'rgba(31,111,235,.02)'}]}},
      markPoint:{data:[{coord:['2025-12',52],value:'×26',symbolSize:64,
        itemStyle:{color:C.red},label:{color:'#fff',fontWeight:800,fontSize:16}}]},
      animationDuration:ANIM?1600:0}],
    graphic:[]});
}

/* ---- ch05 就绪度雷达：健康 vs 失败样本 ---- */
function readiness(el){
  const ch = mk(el);
  ch.setOption({
    legend:{bottom:0,data:['健康样本','失败样本']},
    radar:{indicator:['战略','数据','技术','组织','应用','合规'].map(t=>({name:t,max:5})),
      radius:'62%',center:['50%','48%'],splitNumber:5,
      axisName:{color:C.dim,fontSize:13}},
    tooltip:{},
    series:[{type:'radar',
      data:[
        {name:'健康样本',value:[4,4,4,4,5,4],itemStyle:{color:C.green},
         areaStyle:{color:'rgba(22,163,74,.18)'},lineStyle:{width:2.5}},
        {name:'失败样本',value:[3,1,2,1,4,1],itemStyle:{color:C.red},
         areaStyle:{color:'rgba(229,72,77,.15)'},lineStyle:{width:2.5}}],
      animationDuration:ANIM?900:0}],
  });
}

/* ---- ch06 ROI-KANO 气泡矩阵 ---- */
function matrix(el){
  const pts = [
    {name:'退换货自动应答',v:[78,26],c:C.green,tag:'第一期'},
    {name:'工单自动路由',  v:[64,44],c:C.green,tag:'第一期'},
    {name:'差评预警',      v:[48,52],c:C.gold, tag:'补数据'},
    {name:'智能搭配推荐',  v:[30,74],c:C.violet,tag:'二期试点'},
    {name:'虚拟试穿',      v:[12,88],c:C.red,  tag:'战略探索'}];
  const ch = mk(el);
  ch.setOption({
    grid:{left:70,right:40,top:30,bottom:56},
    xAxis:{name:'ROI →',min:0,max:100,splitLine:{show:false}},
    yAxis:{name:'KANO：基本 → 兴奋 →',min:0,max:100,inverse:true,splitLine:{show:false}},
    tooltip:{formatter:p=>'<b>'+p.data.name+'</b><br>阶段：'+p.data.tag},
    series:[{type:'scatter',symbolSize:24,
      label:{show:true,position:'top',formatter:'{b}',color:C.ink,fontSize:12,fontWeight:600},
      data:pts.map(p=>({name:p.name,value:p.v,tag:p.tag,itemStyle:{color:p.c,opacity:.88}})),
      markLine:{silent:true,symbol:'none',label:{show:false},
        lineStyle:{color:C.line,type:'dashed'},data:[{xAxis:50},{yAxis:50}]},
      markArea:{silent:true,itemStyle:{color:'rgba(22,163,74,.05)'},
        label:{show:true,position:'insideBottomRight',color:C.green,fontSize:12,fontWeight:700},
        data:[[{name:'第一期 · 先赢一场小的',xAxis:50,yAxis:0},{xAxis:100,yAxis:50}]]},
      animationDuration:ANIM?1000:0}],
  });
  // 场景控制：气泡逐个落下
  window.FDE_SCENES.matrix = function(i){
    ch.setOption({series:[{data:pts.map((p,j)=>({name:p.name,value:p.v,tag:p.tag,
      itemStyle:{color:p.c,opacity:(i==null||i>=j)?.88:.12},
      label:{opacity:(i==null||i>=j)?1:.12}}))}]});
  };
}

/* ---- ch08 存活漏斗（真漏斗图） ---- */
function funnel(el){
  const all = [
    {name:'100 个立项',value:100,d:'跟风立项，痛点不真'},
    {name:'60 个进 PoC',value:60,d:'数据拿不到、权限卡住'},
    {name:'30 个 PoC“成功”',value:30,d:'干净数据自嗨'},
    {name:'15 个试点上线',value:15,d:'高并发崩、护栏缺'},
    {name:'8 个全员推广',value:8,d:'员工抵制、流程不改'},
    {name:'5 个产生 P&L 影响',value:5,d:'无人运营、效果衰减'}];
  const ch = mk(el);
  const opt = n => ({
    tooltip:{formatter:p=>'<b>'+p.name+'</b><br>'+all.find(a=>a.name===p.name).d},
    series:[{type:'funnel',left:'8%',right:'8%',top:10,bottom:10,
      min:0,max:100,sort:'descending',gap:4,
      label:{show:true,position:'inside',formatter:'{b}',fontSize:13,fontWeight:600,color:'#fff'},
      itemStyle:{borderColor:'#fff',borderWidth:2},
      color:['#3b5a8f','#46639b','#5a82c2','#7ba3e0','#9dbdec',C.green],
      data:all.slice(0,n),
      animationDuration:ANIM?800:0,animationDurationUpdate:600}],
  });
  ch.setOption(opt(6));
  // 场景控制：逐层塌陷
  window.FDE_SCENES.funnel = i => ch.setOption(opt(i==null?6:i+1));
}

/* ---- ch10 KPI 前后对照 ---- */
function kpi(el){
  const rows = [
    {n:'在线接通率',b:30,a:90,bl:'30%',al:'90%+'},
    {n:'首次联系解决率 FCR',b:65,a:90,bl:'~65%',al:'90%+'},
    {n:'转人工服务量',b:100,a:20,bl:'基线 100',al:'-80%'},
    {n:'服务可用时长',b:33,a:100,bl:'8h/工作日',al:'7×24'}];
  const ch = mk(el);
  ch.setOption({
    legend:{bottom:0,data:['改造前','改造后']},
    grid:{left:150,right:60,top:20,bottom:44},
    xAxis:{type:'value',max:100,splitLine:{lineStyle:{color:C.line}}},
    yAxis:{type:'category',inverse:true,data:rows.map(r=>r.n),
      axisLabel:{color:C.ink,fontSize:13}},
    tooltip:{trigger:'axis',axisPointer:{type:'shadow'},
      formatter:ps=>ps[0].name+'<br>'+ps.map(p=>p.marker+p.seriesName+'：'+rows[p.dataIndex][p.seriesName==='改造前'?'bl':'al']).join('<br>')},
    series:[
      {name:'改造前',type:'bar',barWidth:14,itemStyle:{color:'#b9c3d4',borderRadius:[0,4,4,0]},
       data:rows.map(r=>r.b),animationDuration:ANIM?700:0},
      {name:'改造后',type:'bar',barWidth:14,itemStyle:{color:C.green,borderRadius:[0,4,4,0]},
       data:rows.map(r=>r.a),animationDuration:ANIM?1100:0}],
  });
}

/* ---- ch12 三维能力雷达（三样本） ---- */
function profiles(el){
  const ch = mk(el);
  ch.setOption({
    legend:{bottom:0},
    radar:{indicator:[{name:'技术力',max:9},{name:'业务力',max:9},{name:'交付力',max:9}],
      radius:'62%',center:['50%','46%'],
      axisName:{color:C.dim,fontSize:13}},
    tooltip:{},
    series:[{type:'radar',
      data:[
        {name:'偏科工程师 (9/3/2)',value:[9,3,2],itemStyle:{color:C.red},
         areaStyle:{color:'rgba(229,72,77,.12)'},lineStyle:{width:2}},
        {name:'资深售前 (3/7/6)',value:[3,7,6],itemStyle:{color:C.gold},
         areaStyle:{color:'rgba(180,83,9,.12)'},lineStyle:{width:2}},
        {name:'合格 FDE (7/7/7)',value:[7,7,7],itemStyle:{color:C.green},
         areaStyle:{color:'rgba(22,163,74,.20)'},lineStyle:{width:3}}],
      animationDuration:ANIM?900:0}],
  });
}

/* ---- ch12 薪酬刻度（散点标尺） ---- */
function salary(el){
  const marks = [
    {name:'入门 · YC 初创',v:140},{name:'中位 base',v:210},
    {name:'Anthropic/OpenAI',v:300},{name:'资深 · Palantir+',v:415},{name:'顶级总包',v:600}];
  const ch = mk(el);
  ch.setOption({
    grid:{left:50,right:50,top:56,bottom:44},
    xAxis:{type:'value',min:100,max:660,name:'美元 / 年（总包）',
      splitLine:{lineStyle:{color:C.line}}},
    yAxis:{show:false,min:0,max:1},
    tooltip:{formatter:p=>'<b>$'+p.value[0]+'K</b><br>'+p.name},
    series:[{type:'scatter',symbolSize:20,
      data:marks.map((m,i)=>({name:m.name,value:[m.v,.5],
        itemStyle:{color:[C.dim,C.blue,C.violet,C.gold,C.red][i]}})),
      label:{show:true,position:'top',fontSize:12,fontWeight:700,color:C.ink,
        formatter:p=>'$'+p.value[0]+'K\n'+p.name},
      markLine:{silent:true,symbol:'none',
        lineStyle:{color:C.line,width:6,type:'solid',cap:'round'},
        label:{show:false},
        data:[[{coord:[140,.5]},{coord:[600,.5]}]]},
      animationDuration:ANIM?800:0}],
  });
}

window.FDE_CHARTS = {powermap,growth,readiness,matrix,funnel,kpi,profiles,salary};
document.querySelectorAll('.echart').forEach(el=>{
  const fn = window.FDE_CHARTS[el.dataset.chart];
  if(fn) fn(el);
});
})();
