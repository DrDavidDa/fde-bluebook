# -*- coding: utf-8 -*-
"""FDE 蓝皮书站点构建：md 章节 -> HTML 页面"""
import os, re, html, json

SRC = r"E:/KimiCode/FDE蓝皮书"
OUT = os.path.join(SRC, "site")

CHAPTERS = [
    ("ch01", "第1章_Palantir藏了15年的岗位.md", "第一幕 · 新物种", "Palantir 藏了 15 年的岗位"),
    ("ch02", "第2章_OpenAI为什么一年扩了26倍.md", "第一幕 · 新物种", "OpenAI 为什么一年把这个团队扩了 26 倍"),
    ("ch03", "第3章_尸体解剖五种死法.md", "第二幕 · 避坑", "失败复盘：五种死法"),
    ("ch04", "第4章_影子AI.md", "第二幕 · 避坑", "影子 AI：你公司 90% 的员工已经在用了"),
    ("ch05", "第5章_进场72小时.md", "第三幕 · 作战链", "进场 72 小时"),
    ("ch06", "第6章_把大概能提效写成契约.md", "第三幕 · 作战链", "把“大概能提效”写成契约"),
    ("ch07", "第7章_RAG不是银弹evals才是命门.md", "第三幕 · 作战链", "建造：RAG 不是银弹，evals 才是命门"),
    ("ch08", "第8章_最后100米从Demo到生产.md", "第三幕 · 作战链", "最后 100 米：从 Demo 到生产"),
    ("ch09", "第9章_砾石路原理.md", "第三幕 · 作战链", "砾石路原理：别把天赋浪费成高薪外包"),
    ("ch10", "第10章_前线复盘1保险项目.md", "第四幕 · 前线与身价", "前线复盘①：让 FCR 冲到 90% 的保险项目"),
    ("ch11", "第11章_前线复盘2新前线.md", "第四幕 · 前线与身价", "前线复盘②：2026 的新前线"),
    ("ch12", "第12章_年薪210K的新物种.md", "第四幕 · 前线与身价", "年薪 $210K 的新物种：能力解剖"),
    ("ch13", "第13章_拿下offer.md", "第四幕 · 前线与身价", "拿下 offer：面试官真正想看到的"),
    ("toolbox", "工具箱_FDE的八件装备.md", "独立导航", "工具箱：FDE 的八件装备"),
]

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    t = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    return t

def parse_md(text):
    """极简 md 解析：h1/h2/h3/表格/代码块/引用(含金句海报)/列表/段落"""
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            i += 1; continue
        # 代码块
        if s.startswith("```"):
            buf, i = [], i + 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>")
            continue
        # 标题
        m = re.match(r"^(#{1,3})\s+(.*)", s)
        if m and not s.startswith("####"):
            lv = len(m.group(1)); txt = inline(m.group(2))
            out.append(("<h%d>%s</h%d>") % (lv, txt, lv))
            i += 1; continue
        # 表格
        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i+1]):
            heads = [c.strip() for c in s.strip("|").split("|")]
            i += 2; rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            h = "<table><thead><tr>" + "".join("<th>%s</th>" % inline(c) for c in heads) + "</tr></thead><tbody>"
            for r in rows:
                h += "<tr>" + "".join("<td>%s</td>" % inline(c) for c in r) + "</tr>"
            out.append(h + "</tbody></table>")
            continue
        # 引用块
        if s.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip()); i += 1
            inner = "\n".join(buf)
            if any(b.strip().startswith("#") for b in buf):
                # 金句海报
                parts = [re.sub(r"^#\s*", "", b) for b in buf if b.strip()]
                txt = "<br>".join(inline(p) for p in parts)
                out.append('<div class="poster reveal"><p>' + txt + '</p><div class="sig">FDE 工程师蓝皮书</div></div>')
            else:
                body = "<br>".join(inline(b) for b in buf if b)
                out.append("<blockquote><p>" + body + "</p></blockquote>")
            continue
        # 列表
        if re.match(r"^[-*]\s+", s):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[i])); i += 1
            out.append("<ul>" + "".join("<li>%s</li>" % inline(x) for x in items) + "</ul>")
            continue
        if re.match(r"^\d+\.\s+", s):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i])); i += 1
            out.append("<ol>" + "".join("<li>%s</li>" % inline(x) for x in items) + "</ol>")
            continue
        # 分隔线
        if s == "---":
            out.append("<hr>"); i += 1; continue
        # 段落
        buf = [s]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,3}\s|>|```|\||[-*]\s|\d+\.\s)", lines[i].strip()):
            buf.append(lines[i].strip()); i += 1
        out.append("<p>" + inline(" ".join(buf)) + "</p>")
    return "\n".join(out)

# ---------- 交互组件 ----------
def comp_timeline():
    items = [("2003","Palantir 成立，瞄准反恐数据",0),("2010 前后","Delta 诞生：工程师进驻客户现场",0),
             ("2016","FDE 人数反超产品工程师",1),("2020","纽交所上市，模式被写进财报",0),
             ("2024 末","OpenAI 组建 FDE 团队",0),("2025","岗位 +800% · Anthropic 设岗",1),
             ("2026","全球大厂跟进，中国讨论升温",1)]
    h = '<div class="component reveal"><div class="cap">编年史 · 滚动时间线</div><div class="timeline">'
    for yr, tx, hot in items:
        h += '<div class="tl-item%s"><div class="yr">%s</div><div class="tx">%s</div></div>' % (" hot" if hot else "", yr, tx)
    return h + "</div></div>"

TOMBS = [("⚙","技术死","Demo 惊艳，生产见光死：没有 evals 就没有发现问题的能力"),
         ("🗄","数据死","给法拉利加了一箱水：脏数据被 AI 高效放大"),
         ("💸","钱死","ROI 永远“下个季度能算出来”，直到预算被砍"),
         ("🧍","人死","一场静默罢工：没人破坏系统，只是不配合"),
         ("⚖","合规死","法务的那封邮件，冻结了八个月的项目")]

def comp_tombs():
    # 滚动场景：卡片堆叠翻页
    stage = '<div class="stackcards">'
    for i, (ic, nm, ds) in enumerate(TOMBS):
        stage += '<div class="stcard" style="--i:%d"><div class="ic">%s</div><div class="nm">%s</div></div>' % (i, ic, nm)
    stage += '</div>'
    steps = ""
    for i, (ic, nm, ds) in enumerate(TOMBS):
        steps += '<div class="sstep"><div class="card"><b>第 %d 种 · %s</b><br>%s</div></div>' % (i + 1, nm, ds)
    return ('<div class="scrolly" data-scene="tombs"><div class="stage"><div class="component">'
            '<div class="cap">失败地图 · 五种典型死法（滚动翻页）</div>' + stage + '</div></div>'
            '<div class="steps">' + steps + '</div></div>')

def comp_vbars():
    return ('<div class="component reveal"><div class="cap">官方许可 vs 影子使用</div>'
      '<div class="vbars reveal">'
      '<div class="vbar"><div class="num" style="color:var(--accent)">40%</div>'
      '<div class="fill" data-h="76px" style="background:linear-gradient(180deg,#1f6feb,#1558b0)"></div>'
      '<div class="lab">公司购买了官方 AI 许可</div></div>'
      '<div class="vbar"><div class="num" style="color:var(--red)">90%+</div>'
      '<div class="fill" data-h="180px" style="background:linear-gradient(180deg,#e5484d,#b32b38)"></div>'
      '<div class="lab">员工在用个人 AI 工具工作</div></div>'
      '</div><p style="text-align:center;color:var(--dim);font-size:13px">需求从未消失，只是流进了你看不见的管道。</p></div>')

def comp_funnel():
    # 滚动场景：ECharts 真漏斗，随步骤逐层塌陷
    txts = [("100 个立项","大多数死在娘胎里：痛点不真，跟风立项。"),
            ("60 个进 PoC","数据拿不到、权限卡住——四成项目直接流产。"),
            ("30 个 PoC“成功”","干净数据上的自嗨，离生产还隔着一片海。"),
            ("15 个试点上线","高并发崩、护栏缺失，Demo 魔咒在此显灵。"),
            ("8 个全员推广","员工抵制、流程不改，使用率阴跌。"),
            ("5 个产生 P&L 影响","终值：MIT NANDA 的 5%。无人运营，效果还会衰减。")]
    steps = "".join('<div class="sstep"><div class="card"><b>%s</b><br>%s</div></div>' % t for t in txts)
    return ('<div class="scrolly" data-scene="funnel"><div class="stage"><div class="component">'
            '<div class="cap">PoC → 生产 · 存活漏斗</div>'
            '<div class="echart" data-chart="funnel" style="height:460px"></div>'
            '<p style="text-align:center;color:var(--dim);font-size:13px">各层数字为示意模型，来源：MIT NANDA 5% 终值 + 行业经验外推。</p>'
            '</div></div><div class="steps">' + steps + '</div></div>')

def comp_pipeline():
    nodes = [("1","文档解析","症状：PDF 表格拆成乱码，数字对不上。<br>补救：专用解析器 + 表格结构化，解析结果人工抽检。"),
             ("2","切块策略","症状：答案被拦腰切断，检索到半句话。<br>补救：按语义块切、保留标题层级、重叠 10–15%。"),
             ("3","嵌入模型","症状：中文行业术语检索不到。<br>补救：换中文优化的 embedding，用真实 query 测召回。"),
             ("4","检索召回","症状：该命中的文档排在第 30 名。<br>补救：top-k 放大 + BM25 与向量混合检索。"),
             ("5","重排序","症状：召回了但排错序。<br>补救：加 reranker 层，重排后再截断。"),
             ("6","提示组装","症状：检索内容塞太多，模型注意力涣散。<br>补救：只留 top 3–5，标注来源编号。"),
             ("7","生成校验","症状：模型不看资料自由发挥。<br>补救：强制引用来源 ID，无来源不输出。")]
    h = '<div class="component reveal"><div class="cap">RAG 管道 · 7 个漏点（点击排查）</div><div class="pipeline">'
    for n, t, d in nodes:
        h += '<div class="pnode" data-t="漏点 %s · %s" data-d="%s"><span class="n">%s</span>%s</div>' % (n, t, d, n, t)
    return h + '</div><div class="pdetail"></div></div>'

def comp_loop():
    return ('<div class="component reveal"><div class="cap">砾石路 → 柏油路 · 复利循环</div><div class="loopwrap">'
      '<svg viewBox="0 0 420 300">'
      '<circle cx="210" cy="150" r="105" fill="none" stroke="#d5dbe7" stroke-width="2" stroke-dasharray="6 6" class="spin"/>'
      '<g font-family="sans-serif" font-size="13" fill="#1a2233" text-anchor="middle">'
      '<rect x="150" y="18" width="120" height="40" rx="10" fill="#ffffff" stroke="#1f6feb"/><text x="210" y="43">① 现场 hack</text>'
      '<rect x="288" y="130" width="120" height="40" rx="10" fill="#ffffff" stroke="#1f6feb"/><text x="348" y="155">② 泛化设计</text>'
      '<rect x="150" y="242" width="120" height="40" rx="10" fill="#ffffff" stroke="#16a34a"/><text x="210" y="267">④ 反哺现场</text>'
      '<rect x="12" y="130" width="120" height="40" rx="10" fill="#ffffff" stroke="#1f6feb"/><text x="72" y="155">③ 多客户验证</text>'
      '</g><text x="210" y="146" text-anchor="middle" fill="#b45309" font-size="15" font-weight="bold">每一圈</text>'
      '<text x="210" y="166" text-anchor="middle" fill="#b45309" font-size="15" font-weight="bold">平台更厚</text>'
      '</svg></div></div>')

def comp_layers():
    layers = [("接入层","App / 微信 / 网页 / 电话语音统一入口，全渠道一致体验","L1"),
              ("对话管理与 AI 编排层","意图识别、多轮状态机、转人工路由——系统大脑","L2"),
              ("AI 核心能力层","大模型服务 + RAG 检索 + 规则校验层，回答可溯源","L3"),
              ("知识管理与数据层","条款库 / FAQ / 工单语料分库治理，版本化更新","L4"),
              ("人机协作与运营层","坐席辅助、AI 训练师工作台、质检与回流","L5"),
              ("支撑与集成层","CRM、保单核心系统、权限审计、监控告警","L6")]
    h = '<div class="component reveal"><div class="cap">智能客服中枢 · 六层架构（点击展开）</div><div class="layers">'
    for t, d, tag in layers:
        h += '<div class="layer"><span class="tag">%s</span><div class="lt">%s</div><div class="ld">%s</div></div>' % (tag, t, d)
    return h + "</div></div>"

def comp_ruler():
    return ('<div class="component reveal"><div class="cap">FDE 薪酬刻度尺（美国市场总包）</div>'
      '<div class="echart" data-chart="salary" style="height:300px"></div>'
      '<p style="text-align:center;color:var(--dim);font-size:13px">同一个岗位，差五倍——差价在三维能力的均衡度。</p></div>')

def comp_battlefield():
    cards = [("Palantir","源头","Delta/Dev 双轨制的发明者，FDE 人数曾反超产品工程师"),
             ("OpenAI","模型厂","2 → 52 人，旗舰客户联合攻坚，前线反哺研究"),
             ("Anthropic","模型厂","FDE · Applied AI，$200K–300K"),
             ("YC 创业群","应用层","100+ 家：FDE 即商业模式，按结果定价"),
             ("中国市场","混合编队","私有化部署 + 国产底座 + 甲方教练")]
    h = '<div class="component reveal"><div class="cap">全球 FDE 战场</div><div class="chgrid">'
    for nm, tag, ds in cards:
        h += '<div class="chcard"><div class="act">%s</div><div class="t">%s</div><div class="d">%s</div></div>' % (tag, nm, ds)
    return h + "</div></div>"

# ---------- 视觉组件 v2 ----------
def svg_radar(dims, series, size=420, maxv=5):
    import math
    cx = cy = size / 2; R = size / 2 - 64; n = len(dims)
    s = ['<svg viewBox="0 0 %d %d" style="max-width:%dpx;width:100%%;display:block;margin:0 auto">' % (size, size, size)]
    rings = 5
    for ring in range(1, rings + 1):
        pts = []
        for i in range(n):
            a = -math.pi / 2 + i * 2 * math.pi / n; r = R * ring / rings
            pts.append("%.1f,%.1f" % (cx + r * math.cos(a), cy + r * math.sin(a)))
        s.append('<polygon points="%s" fill="none" stroke="#d5dbe7"/>' % " ".join(pts))
    for i, d in enumerate(dims):
        a = -math.pi / 2 + i * 2 * math.pi / n
        x = cx + R * math.cos(a); y = cy + R * math.sin(a)
        s.append('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="#d5dbe7"/>' % (cx, cy, x, y))
        lx = cx + (R + 30) * math.cos(a); ly = cy + (R + 30) * math.sin(a) + 4
        s.append('<text x="%g" y="%g" text-anchor="middle" font-size="13" fill="#3c465c">%s</text>' % (lx, ly, d))
    for ser in series:
        pts = []
        for i, v in enumerate(ser["values"]):
            a = -math.pi / 2 + i * 2 * math.pi / n; r = R * v / maxv
            pts.append("%.1f,%.1f" % (cx + r * math.cos(a), cy + r * math.sin(a)))
        s.append('<polygon points="%s" fill="%s" fill-opacity="0.15" stroke="%s" stroke-width="2"/>' % (" ".join(pts), ser["color"], ser["color"]))
    s.append('</svg>')
    leg = ''.join('<span style="margin:0 10px;font-size:13px;color:%s">● %s</span>' % (x["color"], x["name"]) for x in series)
    return "".join(s) + '<div style="text-align:center;margin-top:8px">' + leg + '</div>'

def comp_powermap():
    # 滚动场景：四类人逐个点亮
    txts = [("掏钱的人","高影响、支持——你的项目 Sponsor。但别只盯着他，他批了预算不代表项目能活。"),
            ("用的人","低影响、支持——你的种子用户和情报来源。先让一线爽，口碑会替你上楼。"),
            ("挡路的人","高影响、警惕——“先约他喝咖啡”。他成不了功臣，但握着你唯一的否决票。"),
            ("埋数据的人","低影响、中立——掌握数据钥匙的人。没有他开门，你寸步难行。")]
    steps = "".join('<div class="sstep"><div class="card"><b>%s</b><br>%s</div></div>' % t for t in txts)
    return ('<div class="scrolly" data-scene="powermap"><div class="stage"><div class="component">'
            '<div class="cap">权力地图 · 先画人，再谈技术</div>'
            '<div class="echart" data-chart="powermap" style="height:430px"></div>'
            '</div></div><div class="steps">' + steps + '</div></div>')

def comp_growth():
    return ('<div class="component reveal"><div class="cap">OpenAI FDE 团队 · 2025 年扩张曲线</div>'
      '<div class="echart" data-chart="growth" style="height:380px"></div>'
      '<p style="text-align:center;color:var(--dim);font-size:13px">2 → 52 人，×26。OpenAI 当年扩张最快的团队之一，不是研究院。来源：ZenML LLMOps Database</p></div>')

def comp_jdcards():
    cards = [("深入客户业务与数据","看懂客户靠什么赚钱，不只是用什么框架"),
             ("构建生产级 LLM 应用","扛流量、可运维的真系统，不是 demo"),
             ("与研究/产品团队反馈","你是前线传感器，痛点传回模型迭代"),
             ("设计评估体系","evals 是必选项，不是加分项"),
             ("模糊中自主推进","没有产品经理给你写 PRD")]
    h = '<div class="component reveal"><div class="cap">一份顶级 JD 的解剖（Anthropic · FDE Applied AI）</div><div class="chgrid">'
    for t, d in cards:
        h += '<div class="chcard"><div class="t">%s</div><div class="d">%s</div></div>' % (t, d)
    return h + '</div><p style="text-align:center;color:var(--dim);font-size:13px">薪酬带：$200K–300K（2026-03 官方招聘页）</p></div>'

def comp_spectrum():
    return ('<div class="component reveal"><div class="cap">落地方式光谱 · 选哪一段取决于三个变量</div><div class="spectrum">'
      '<div class="bar"><span class="seg">纯买 SaaS 标品</span><span class="seg">厂商 FDE 深度交付</span>'
      '<span class="seg">甲方自建类 FDE</span><span class="seg">纯自研造轮子</span></div>'
      '<div class="notes"><span class="nt">快但浅，通用场景</span><span class="nt">成功率 ~67%，成本可控</span>'
      '<span class="nt">懂业务，能力留下</span><span class="nt">成功率 ~22% 的豪赌</span></div></div></div>')

def comp_matrix():
    # 滚动场景：气泡按推荐顺序逐个落入象限
    txts = [("退换货自动应答","高 ROI + 基本型需求——第一期首选，先赢一场小的。"),
            ("工单自动路由","同样高 ROI：规则清晰、容错高、见效快。"),
            ("差评预警","价值中等：先补数据，别急着上模型。"),
            ("智能搭配推荐","期望型需求：留到二期，用第一期的信任换预算。"),
            ("虚拟试穿","兴奋型 + 低 ROI：战略探索，讲故事可以，排期免谈。")]
    steps = "".join('<div class="sstep"><div class="card"><b>%s</b><br>%s</div></div>' % t for t in txts)
    return ('<div class="scrolly" data-scene="matrix"><div class="stage"><div class="component">'
            '<div class="cap">ROI-KANO 矩阵 · 先做哪个场景，算出来</div>'
            '<div class="echart" data-chart="matrix" style="height:440px"></div>'
            '</div></div><div class="steps">' + steps + '</div></div>')

def dtree(q, opts):
    h = '<div class="dtree"><div class="dt-q">%s</div><div class="dt-arrow">↓</div><div class="dt-opts">' % q
    for t, d, go, stop in opts:
        h += '<div class="dt-opt%s"><b>%s</b>%s<br><span class="go">→ %s</span></div>' % (" stop" if stop else "", t, d, go)
    return h + "</div></div>"

def comp_dtree_ch07():
    return ('<div class="component reveal"><div class="cap">2026 选型决策树 · 微调是最后的选项</div>'
      + dtree("问题到底出在哪？", [
          ("不懂你们的知识","条款、产品、内部数据","RAG（+知识更新机制）",0),
          ("不懂格式与语气","报告体、客服口吻","提示工程 + few-shot",0),
          ("不懂判断逻辑","审单、风险分级","先写规则 prompt；500+ 标注样本后再谈微调",0),
          ("都试了还不行","","先怀疑评估集和数据，最后怀疑模型",1)])
      + '</div>')

def comp_evalsloop():
    return ('<div class="component reveal"><div class="cap">evals 最小闭环</div><div class="loopwrap">'
      '<svg viewBox="0 0 420 300">'
      '<circle cx="210" cy="150" r="105" fill="none" stroke="#d5dbe7" stroke-width="2" stroke-dasharray="6 6" class="spin"/>'
      '<g font-size="13" fill="#1a2233" text-anchor="middle">'
      '<rect x="145" y="18" width="130" height="40" rx="10" fill="#ffffff" stroke="#16a34a"/><text x="210" y="43">① 攒评估集</text>'
      '<rect x="288" y="130" width="120" height="40" rx="10" fill="#ffffff" stroke="#16a34a"/><text x="348" y="155">② 变更必跑分</text>'
      '<rect x="145" y="242" width="130" height="40" rx="10" fill="#ffffff" stroke="#16a34a"/><text x="210" y="267">④ 错题回流</text>'
      '<rect x="12" y="130" width="120" height="40" rx="10" fill="#ffffff" stroke="#16a34a"/><text x="72" y="155">③ 上线监控</text>'
      '</g><text x="210" y="146" text-anchor="middle" fill="#16a34a" font-size="14" font-weight="bold">跑分不过</text>'
      '<text x="210" y="166" text-anchor="middle" fill="#16a34a" font-size="14" font-weight="bold">不上线</text></svg></div></div>')

def comp_routing():
    return ('<div class="component reveal"><div class="cap">置信度路由 · 人工兜底设计图</div>'
      + dtree("用户提问 → 置信度评估", [
          ("高 ≥ 0.85","","AI 直接回答",0),
          ("中 0.6–0.85","","AI 回答 + 标注「建议人工复核」",0),
          ("低 < 0.6 或敏感话题","","热转人工：完整上下文 + 建议答复，处理结果回流评估集",1)])
      + '<p style="text-align:center;color:var(--dim);font-size:13px">敢转人工的系统，比假装什么都会的系统更值得信任。</p></div>')

def comp_gray():
    steps = [("5%","真实流量"),("20%","观察 48h"),("50%","四项指标达标"),("100%","全量 + 回滚待命")]
    h = '<div class="component reveal"><div class="cap">灰度发布节奏</div><div class="stepper">'
    for sn, sd in steps:
        h += '<div class="step"><div class="dot"></div><div class="sn">%s</div><div class="sd">%s</div></div>' % (sn, sd)
    return h + '</div><p style="text-align:center;color:var(--dim);font-size:13px">每级观察 48 小时：准确率 / 转人工率 / 延迟 / 投诉率，全达标才进下一级。</p></div>'

def comp_ladder():
    rungs = [("L1","Prompt","一次性指令，这次能用下次重写",26),("L2","任务卡","带输入/输出/验收，换人也能用",46),
             ("L3","SOP","多步骤流程+异常处理，跨项目能用",68),("L4","组件","代码封装+版本管理，全团队复用",92)]
    h = '<div class="component reveal"><div class="cap">个人资产化阶梯 · 每周五升级一件</div><div class="ladder">'
    for lv, nm, ds, ht in rungs:
        h += '<div class="rung" style="height:%d%%"><div class="lv">%s</div><div class="nm">%s</div><div class="ds">%s</div></div>' % (ht, lv, nm, ds)
    return h + '</div></div>'

def comp_kpi():
    return ('<div class="component reveal"><div class="cap">战果对照 · 改造前 vs 改造后</div>'
      '<div class="echart" data-chart="kpi" style="height:340px"></div>'
      '<p style="text-align:center;color:var(--dim);font-size:13px">口径：公开报道 + 行业推断</p></div>')

def comp_profiles():
    return ('<div class="component reveal"><div class="cap">三维能力雷达 · 面积即身价</div>'
      '<div class="echart" data-chart="profiles" style="height:420px"></div></div>')

def comp_rounds():
    steps = [("技术轮","你真能独立造出来吗？关键词：evals 思维"),("现场模拟轮","45 分钟进场计划：问题质量占 40%"),("客户沟通轮","压力题暗线：单独扔进客户现场，公司是增值还是减值")]
    h = '<div class="component reveal"><div class="cap">三轮面试 · 隐藏考纲</div><div class="stepper">'
    for sn, sd in steps:
        h += '<div class="step"><div class="dot"></div><div class="sn">%s</div><div class="sd">%s</div></div>' % (sn, sd)
    return h + '</div></div>'

# ---- 每章开场数据带 ----
STATBAND = {
  "ch01":[("+800%","2025.1–9 FDE 岗位发布量涨幅"),("2016","这一年 FDE 人数反超产品工程师"),("$210K","美国市场中位基本薪资")],
  "ch02":[("2→52","OpenAI FDE 团队 2025 年人数"),("$200–300K","Anthropic FDE 岗位年薪"),("100+","招聘 FDE 的 YC 公司")],
  "ch03":[("95%","无可衡量 P&L 影响的项目占比"),("5 种","全部失败可归入的死法"),("1 种","其中真正和技术有关的")],
  "ch04":[("40% vs 90%","官方许可率 vs 影子使用率"),("67% vs 22%","外购深度交付 vs 内部自建成功率"),("5 问","判断需求真假的探测器")],
  "ch05":[("72 小时","决定项目生死的进场窗口"),("6 维","AI 就绪度打分维度"),("20 问","本章速查卡尽调问题数")],
  "ch06":[("5 问","动手前必须回答的定标问题"),("1 页纸","验收契约的全部篇幅"),("18 个月","回本周期的生死红线")],
  "ch07":[("7 个","RAG 管道上会漏的地方"),("50 条","evals 评估集起步规模"),("3 道闸","输出端的结构/安全/来源")],
  "ch08":[("5 / 100","从立项走到产生 P&L 影响"),("4 类","必须转人工的触发条件"),("48 小时","每级灰度的最短观察期")],
  "ch09":[("2 次","每个项目该交付的次数"),("4 级","个人资产化阶梯"),("3 块","滑向咨询公司的警示牌")],
  "ch10":[("90%+","改造后的首次联系解决率"),("-80%","转人工服务量降幅"),("7×24","全天候服务可用性")],
  "ch11":[("3 种","FDE 打法的光谱形态"),("52 人","OpenAI 一年扩出的团队"),("混合编队","中国战场的胜率阵型")],
  "ch12":[("$210K","美国 FDE 中位基本薪资"),("3 维","技术×业务×交付能力模型"),("90 天","从零到可投递的入行路线")],
  "ch13":[("3 轮","面试的完整链路"),("30 题","本章备战题库"),("×5","同名岗位的真实差价")],
}

# ---- 场间视觉注入（锚点 h2 → 组件） ----
INSERTS = {
  "ch01": [("【场 1】", comp_powermap())],
  "ch02": [("【场 1】", comp_jdcards()), ("【场 2】", comp_growth())],
  "ch05": [("【场 2】", '<div class="component reveal"><div class="cap">就绪度雷达 · 健康样本 vs 失败样本</div>' +
            '<div class="echart" data-chart="readiness" style="height:440px"></div></div>')],
  "ch06": [("【场 3】", comp_matrix())],
  "ch07": [("【场 3】", comp_dtree_ch07()), ("【场 4】", comp_evalsloop())],
  "ch08": [("【场 2】", comp_routing()), ("【场 3】", comp_gray())],
  "ch09": [("【场 3】", comp_ladder())],
  "ch10": [("【场 4】", comp_kpi())],
  "ch12": [("【场 1】", comp_profiles())],
  "ch13": [("【场 1】", comp_rounds())],
  "ch04": [("【场 2】", comp_spectrum())],
}

READINESS = {
  "title":"AI 就绪度测评","btn":"生成就绪度雷达","max":5,
  "dims":["战略","数据","技术","组织","应用","合规"],
  "questions":[
    {"t":"谈到 AI，你们管理层最接近哪种状态？","opts":[
      {"t":"“老板很重视”，但说不清重视什么","s":[1,0,0,0,0,0]},
      {"t":"有年度方向，没写进考核","s":[3,0,0,0,0,0]},
      {"t":"KPI 里写明落地场景和指标","s":[5,0,0,0,0,0]}]},
    {"t":"AI 项目的预算形态是？","opts":[
      {"t":"还没影的事","s":[1,0,0,0,0,0]},
      {"t":"有创新基金，随报随批","s":[3,0,0,0,0,0]},
      {"t":"列入年度预算，有验收节点","s":[5,0,0,0,0,0]}]},
    {"t":"核心业务数据的真实状态？","opts":[
      {"t":"“都在系统里，导出来就行”","s":[0,1,0,0,0,0]},
      {"t":"有治理但欠账不少","s":[0,3,0,0,0,0]},
      {"t":"有专人、有口径、有更新机制","s":[0,5,0,0,0,0]}]},
    {"t":"知识库/文档的现状？","opts":[
      {"t":"最后更新是去年","s":[0,1,0,0,0,0]},
      {"t":"有人管但没流程","s":[0,3,0,0,0,0]},
      {"t":"版本化管理，定期更新","s":[0,5,0,0,0,0]}]},
    {"t":"核心系统的集成能力？","opts":[
      {"t":"十年前外包的黑盒","s":[0,0,1,0,0,0]},
      {"t":"有 API 但文档感人","s":[0,0,3,0,0,0]},
      {"t":"网关、日志、工程团队齐备","s":[0,0,5,0,0,0]}]},
    {"t":"上次系统故障，多久被发现？","opts":[
      {"t":"用户打电话来骂才知道","s":[0,0,1,0,0,0]},
      {"t":"有人盯，但不及时","s":[0,0,3,0,0,0]},
      {"t":"监控告警分钟级发现","s":[0,0,5,0,0,0]}]},
    {"t":"业务和技术提需求的方式？","opts":[
      {"t":"“先走个流程”，流程三个月","s":[0,0,0,1,0,0]},
      {"t":"能开会，但很难拍板","s":[0,0,0,3,0,0]},
      {"t":"同桌吵架，也能同桌拍板","s":[0,0,0,5,0,0]}]},
    {"t":"一线员工对 AI 项目的态度？","opts":[
      {"t":"没人告诉过他们","s":[0,0,0,1,0,0]},
      {"t":"听说过，观望中","s":[0,0,0,3,0,0]},
      {"t":"有种子用户主动参与","s":[0,0,0,5,0,0]}]},
    {"t":"让业务说出具体痛点场景？","opts":[
      {"t":"“先做个通用智能助手”","s":[0,0,0,0,1,0]},
      {"t":"有场景，没排序","s":[0,0,0,0,3,0]},
      {"t":"三个具体痛点脱口而出","s":[0,0,0,0,5,0]}]},
    {"t":"上一个数字化/AI 项目的结局？","opts":[
      {"t":"悄悄没人用了","s":[0,0,0,0,1,0]},
      {"t":"活着，但没人复盘","s":[0,0,0,0,3,0]},
      {"t":"有指标、有复盘、有迭代","s":[0,0,0,0,5,0]}]},
    {"t":"法务和信息安全什么时候参与？","opts":[
      {"t":"“先做出来，合规后面再说”","s":[0,0,0,0,0,1]},
      {"t":"听说过项目，没进组","s":[0,0,0,0,0,3]},
      {"t":"从第一天就在场","s":[0,0,0,0,0,5]}]},
    {"t":"数据出域和备案情况？","opts":[
      {"t":"没想过这个问题","s":[0,0,0,0,0,1]},
      {"t":"知道有限制，没评估","s":[0,0,0,0,0,3]},
      {"t":"红线清晰，手续路径明确","s":[0,0,0,0,0,5]}]}],
  "verdicts":[[2.4,"先补课","有维度亮红灯。先按第 5 章清单补短板，别急着进场——项目会准时在你最弱的那一关翻车。"],
              [3.9,"可以进场","基本盘及格，但有短板维度。带着补齐计划进场，把短板写进项目风险清单。"],
              [5.1,"绿灯全亮","就绪度罕见地好。别浪费——直接上 MVP，用第 6 章的验收契约锁定第一场胜利。"]]
}

TALENT = {
  "title":"FDE 天赋指数","btn":"生成天赋雷达","max":5,
  "dims":["技术力","业务力","交付力"],
  "questions":[
    {"t":"给你一个模糊需求，48 小时后你能交出什么？","opts":[
      {"t":"一份需求澄清文档","s":[1,0,0]},
      {"t":"能跑的 demo，界面很糙","s":[5,0,0]},
      {"t":"demo 加一页验证计划","s":[4,0,0]}]},
    {"t":"你的 RAG 系统线上答错了一个核心问题，第一步？","opts":[
      {"t":"换个更大的模型","s":[1,0,0]},
      {"t":"查检索：这条知识到底召回了没有","s":[5,0,0]},
      {"t":"先道歉，再看日志","s":[3,0,0]}]},
    {"t":"你怎么看“evals 评估集”？","opts":[
      {"t":"听说过，没建过","s":[1,0,0]},
      {"t":"建过，但更新不勤","s":[3,0,0]},
      {"t":"改任何东西都先跑一遍","s":[5,0,0]}]},
    {"t":"客户要“接入 ChatGPT 就行”，你的反应？","opts":[
      {"t":"行，API 调通很快","s":[1,0,0]},
      {"t":"先问数据出域和护栏要求","s":[5,0,0]},
      {"t":"建议先做 PoC 看看","s":[3,0,0]}]},
    {"t":"你能讲清一个行业的价值链吗？","opts":[
      {"t":"没仔细想过","s":[0,1,0]},
      {"t":"能讲大概，没算过账","s":[0,3,0]},
      {"t":"能讲，还知道哪一环最痛","s":[0,5,0]}]},
    {"t":"客户说“我们要 AI 转型”，你的第一反应？","opts":[
      {"t":"太好了，开始讲方案","s":[0,1,0]},
      {"t":"问：上一个项目怎么死的？","s":[0,5,0]},
      {"t":"问预算和 deadline","s":[0,3,0]}]},
    {"t":"和业务负责人聊 30 分钟后，对方的典型反应？","opts":[
      {"t":"客气但保持距离","s":[0,1,0]},
      {"t":"“你以前是干我们这行的吧”","s":[0,5,0]},
      {"t":"开始倒苦水","s":[0,4,0]}]},
    {"t":"你怎么判断一个需求是真是假？","opts":[
      {"t":"客户说是就是","s":[0,1,0]},
      {"t":"看有没有人已经在为它花钱/加班","s":[0,5,0]},
      {"t":"做个调研问卷","s":[0,2,0]}]},
    {"t":"项目验收会上 CFO 质疑收益，你怎么办？","opts":[
      {"t":"当场冒汗","s":[0,0,1]},
      {"t":"翻出立项时的验收契约逐项对","s":[0,0,5]},
      {"t":"承诺下个季度给数据","s":[0,0,2]}]},
    {"t":"客户提了一个明知做不了的需求，你？","opts":[
      {"t":"先答应，回头再说","s":[0,0,1]},
      {"t":"说不，并给出能做的替代方案","s":[0,0,5]},
      {"t":"转给领导决定","s":[0,0,2]}]},
    {"t":"系统上线后使用率诡异走低，你先查什么？","opts":[
      {"t":"系统有没有 bug","s":[0,0,2]},
      {"t":"坐席是不是在教用户绕过系统","s":[0,0,5]},
      {"t":"发个使用手册","s":[0,0,1]}]},
    {"t":"上一个项目，你“先斩后奏”解决问题是什么时候？","opts":[
      {"t":"想不起来","s":[0,0,1]},
      {"t":"上周","s":[0,0,5]},
      {"t":"有过几次，看情况","s":[0,0,3]}]}],
  "verdicts":[[2.4,"潜力股","底子有了，短板明显。按第 12 章 90 天路线图补课，先补最弱的那一维。"],
              [3.9,"原型快手","已经能上战场。投初级 FDE 岗位，面试时把“对结果负责”的叙事讲出来。"],
              [5.1,"领域反叛者","三维均衡的稀缺物种。直接投头部岗位，薪资往 75 分位谈。"]]
}

COMPONENTS = {
    "ch01": comp_timeline(),
    "ch03": comp_tombs(),
    "ch04": comp_vbars(),
    "ch05": '<div class="component reveal quiz" data-quiz="FDE_READINESS"><div class="cap">交互测评 · 你的公司 AI 就绪度有几分</div></div>',
    "ch06": '<div class="component reveal" data-calc="roi"><div class="cap">交互计算器 · 你的场景几个月回本</div></div>',
    "ch07": comp_pipeline(),
    "ch08": comp_funnel(),
    "ch09": comp_loop(),
    "ch10": comp_layers(),
    "ch11": comp_battlefield(),
    "ch12": comp_ruler() + '<div class="component reveal quiz" data-quiz="FDE_TALENT"><div class="cap">交互测评 · 你的 FDE 天赋指数</div></div>',
}

QUIZ_SCRIPTS = {
    "ch05": "window.FDE_READINESS=" + json.dumps(READINESS, ensure_ascii=False) + ";",
    "ch12": "window.FDE_TALENT=" + json.dumps(TALENT, ensure_ascii=False) + ";",
}

# 站点发布地址（GitHub Pages），canonical/og:url/sitemap 都用它
BASE_URL = "https://drdaviddda.github.io/fde-bluebook/"

# 顶导航短标签（三处同步：本表、index.html、finish.html）
NAV_LABELS = {
    "ch01": "Palantir", "ch02": "OpenAI ×26", "ch03": "失败复盘", "ch04": "影子 AI",
    "ch05": "进场 72h", "ch06": "验收契约", "ch07": "evals", "ch08": "最后 100 米",
    "ch09": "砾石路", "ch10": "复盘①", "ch11": "复盘②", "ch12": "$210K",
    "ch13": "拿下 offer", "toolbox": "工具箱",
}
NAV = [("index.html","序章","")] + [(c[0]+".html", NAV_LABELS[c[0]], c[0]) for c in CHAPTERS] + [("finish.html","卡册","finish")]

def build_nav(cur):
    links = "".join('<a href="%s" data-ch="%s">%s</a>' % (u, cid, t) for u, t, cid in NAV)
    return ('<nav class="topnav"><span class="brand">FDE<span> · 工程师蓝皮书</span></span>'
            '<div class="map-links">' + links + "</div></nav>")

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} ｜ FDE 工程师蓝皮书</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="FDE 工程师蓝皮书">
<meta property="og:locale" content="zh_CN">
<meta property="og:title" content="{title} ｜ FDE 工程师蓝皮书">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{ogimg}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title} ｜ FDE 工程师蓝皮书">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{ogimg}">
<meta name="theme-color" content="#1f6feb">
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<link rel="stylesheet" href="assets/style.css">
</head><body data-ch="{cid}" data-act="{actcls}">
<div id="readbar"></div><div id="readticks"></div>
{nav}
<main class="chapter">
<header class="chhero">
<div class="bignum-no">{chapnum}</div>
<div class="inner">
<div class="act-tag">{act}</div>
<h1>{title}</h1>
<div class="teaser">{teaser}</div>
<div class="scrollhint">滚动开始</div>
</div>
</header>
<div class="wrap">
{statband}
{body}
<div class="nextch">{prevnext}</div>
</div>
</main>
<footer class="footer">FDE 工程师蓝皮书 · 数据来源见「工具箱 · 装备 8」 · 站点为内容原型</footer>
{vendorjs}<script>{quizjs}</script>
<script src="assets/app.js"></script>
</body></html>"""

def build():
    metas = {}
    ECHARTS_PAGES = {"ch01","ch02","ch05","ch06","ch08","ch10","ch12"}
    ACTCLS = {"第一幕":"a1","第二幕":"a2","第三幕":"a3","第四幕":"a4"}
    # 预取每章悬念句（用于章末预告卡）
    teasers = {}
    for cid0, fname0, act0, title0 in CHAPTERS:
        try:
            t0 = open(os.path.join(SRC, fname0), encoding="utf-8").read()
            m0 = re.search(r"##\s*【开场】\s*(.+)", t0)
            teasers[cid0] = m0.group(1).strip() if m0 else "八件装备，拿走即用"
        except OSError:
            teasers[cid0] = ""
    for idx, (cid, fname, act, title) in enumerate(CHAPTERS):
        raw = open(os.path.join(SRC, fname), encoding="utf-8").read()
        # 去掉 h1（模板已含）
        raw = re.sub(r"^#\s+.*?\n", "", raw, count=1)
        # 章节封面悬念句：取【开场】标题
        mt = re.search(r"##\s*【开场】\s*(.+)", raw)
        teaser = mt.group(1).strip() if mt else "八件装备，拿走即用"
        # 头部元信息（首个引用块）提取后移除
        meta = ""
        m = re.search(r"((?:>.*\n)+)", raw)
        if m:
            meta = " ｜ ".join(re.sub(r"[*>`]", "", x).strip() for x in m.group(1).strip().split("\n") if "：" in x)
            raw = raw[:m.start()] + raw[m.end():]
        body = parse_md(raw)
        # 去掉作者批注（视觉锚点说明）
        body = re.sub(r"<blockquote><p>📌.*?</blockquote>", "", body, flags=re.S)
        # 场间视觉注入
        for anchor, comphtml in INSERTS.get(cid, []):
            pat = re.compile(r"(<h2>[^<]*" + re.escape(anchor) + r"[^<]*</h2>)")
            body = pat.sub(lambda m: m.group(1) + "\n" + comphtml, body, count=1)
        # 组件注入：替换「名场面」区块内容；无名场面则插到速查卡前
        comp = COMPONENTS.get(cid, "")
        if comp:
            m2 = re.search(r"(<h2>【名场面】.*?</h2>).*?(?=<h2>|<hr>|$)", body, flags=re.S)
            if m2:
                body = body[:m2.start()] + m2.group(1) + "\n" + comp + "\n" + body[m2.end():]
            else:
                m3 = re.search(r"<h2>【速查卡】", body)
                pos = m3.start() if m3 else len(body)
                body = body[:pos] + comp + "\n" + body[pos:]
        # 区块动画：每个 h2 前开 section
        body = re.sub(r"(<h2>)", r"</section><section class='reveal'>\1", body)
        body = "<section class='reveal'>" + body + "</section>"
        body = body.replace("<section class='reveal'></section>", "")
        # 去掉只含 hr 的空 section；首个内容 section 标记 firstsec（首字下沉用）
        body = re.sub(r"<section class='reveal'>\s*<hr>\s*</section>", "", body)
        body = body.replace("<section class='reveal'>", "<section class='reveal firstsec'>", 1)
        # 速查卡收藏按钮
        body = re.sub(r"(<h2>【速查卡】[^<]*</h2>)",
                      r'\1<button class="collect" data-card="' + cid + '">☆ 收进卡册</button>',
                      body, count=1)
        # 数据带
        sb = ""
        if cid in STATBAND:
            sb = '<div class="statband">' + "".join(
                '<div class="sb"><div class="n">%s</div><div class="d">%s</div></div>' % (n, d)
                for n, d in STATBAND[cid]) + "</div>"
        # 上/下一章（下一章为预告卡）
        prevnext = ""
        if idx > 0:
            prevnext += '<a class="btn ghost" href="%s.html">← %s</a>' % (CHAPTERS[idx-1][0], CHAPTERS[idx-1][3][:14]) if idx > 0 else ""
        else:
            prevnext += '<a class="btn ghost" href="index.html">← 序章</a>'
        if idx < len(CHAPTERS) - 1:
            nid, ntitle = CHAPTERS[idx+1][0], CHAPTERS[idx+1][3]
            prevnext += ('<a class="nextcard" href="%s.html"><span class="nc-k">下一章</span>'
                         '<b>%s</b><i>%s</i><span class="nc-go">继续 →</span></a>'
                         % (nid, ntitle, teasers.get(nid, "")))
        actcls = "a0"
        for k, v in ACTCLS.items():
            if act.startswith(k): actcls = v
        chapnum = cid[2:] if cid.startswith("ch") else "✦"
        vendorjs = ('<script src="assets/vendor/echarts.min.js"></script>'
                    '<script src="assets/fde-theme.js"></script>'
                    '<script src="assets/charts.js"></script>') if cid in ECHARTS_PAGES else ""
        desc = html.escape(teaser + " —— FDE 工程师蓝皮书 · " + act, quote=True)
        page = TEMPLATE.format(title=title, cid=cid, act=act, actcls=actcls, chapnum=chapnum,
                               teaser=teaser, vendorjs=vendorjs, statband=sb,
                               desc=desc, canonical=BASE_URL + cid + ".html",
                               ogimg=BASE_URL + "assets/og.png",
                               body=body, nav=build_nav(cid), prevnext=prevnext,
                               quizjs=QUIZ_SCRIPTS.get(cid, ""))
        open(os.path.join(OUT, cid + ".html"), "w", encoding="utf-8").write(page)
        metas[cid] = (act, title)
        print("built", cid)
    write_sitemap()
    return metas

def write_sitemap():
    pages = ["index.html"] + [c[0] + ".html" for c in CHAPTERS] + ["finish.html"]
    urls = "\n".join(
        '  <url><loc>%s%s</loc></url>' % (BASE_URL, "" if p == "index.html" else p)
        for p in pages)
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + urls + "\n</urlset>\n")
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(xml)
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(
        "User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n" % BASE_URL)
    print("built sitemap.xml + robots.txt")

if __name__ == "__main__":
    build()
