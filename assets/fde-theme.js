/* ===== FDE 蓝皮书 · ECharts 统一主题 fdeTheme ===== */
(function(){
  if(!window.echarts) return;
  const C = {blue:'#1f6feb', red:'#e5484d', gold:'#b45309', green:'#16a34a', violet:'#7c3aed',
    ink:'#1a2233', ink2:'#3c465c', dim:'#5a6478', faint:'#98a1b3', line:'#e3e7ef'};
  echarts.registerTheme('fde', {
    color: [C.blue, C.green, C.gold, C.red, C.violet, '#0e9f8a', '#d97706', '#64748b'],
    textStyle: {fontFamily: "'PingFang SC','Microsoft YaHei','Segoe UI',system-ui,sans-serif", color: C.ink2},
    title: {textStyle: {color: C.ink, fontWeight: 700, fontSize: 15}},
    tooltip: {backgroundColor: '#ffffff', borderColor: C.line,
      textStyle: {color: C.ink2, fontSize: 13},
      extraCssText: 'box-shadow:0 6px 20px rgba(16,24,40,.12);border-radius:10px;padding:10px 14px;'},
    legend: {textStyle: {color: C.dim, fontSize: 12}, itemWidth: 14, itemHeight: 8},
    categoryAxis: {
      axisLine: {lineStyle: {color: '#d5dbe7'}}, axisTick: {show: false},
      axisLabel: {color: C.dim, fontSize: 12}, splitLine: {show: false}},
    valueAxis: {
      axisLine: {show: false}, axisTick: {show: false},
      axisLabel: {color: C.faint, fontSize: 11}, splitLine: {lineStyle: {color: '#eef1f6'}}},
    radar: {
      axisName: {color: C.dim, fontSize: 12},
      splitLine: {lineStyle: {color: '#e3e7ef'}},
      splitArea: {areaStyle: {color: ['#ffffff', '#f6f8fb']}},
      axisLine: {lineStyle: {color: '#d5dbe7'}}},
    animationDuration: 900,
    animationEasing: 'cubicOut'
  });
  window.FDE_C = C;
  /* 统一挂载：页面中带 data-echart 的容器由 app.js 或页面脚本初始化 */
  window.fdeChart = function(el, option){
    const ch = echarts.init(el, 'fde', {renderer: 'canvas'});
    ch.setOption(option);
    window.addEventListener('resize', () => ch.resize());
    return ch;
  };
})();
