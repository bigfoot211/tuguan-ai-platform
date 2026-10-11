# -*- coding: utf-8 -*-
"""
土管AI实训平台 · Streamlit 公网版
==================================
土地资源管理专业课余自主学习系统（与本地 Flask 版同源数据）。
整合土地管理学、地籍管理、土地利用规划、不动产估价、GIS与遥感应用
五门核心课程：68 个知识点（全部配套示意图）+ 904 条智能问答（答案配图）。

部署：Streamlit Community Cloud（https://streamlit.io/cloud）
运行：streamlit run streamlit_app.py
"""
import json
import os
import re

import streamlit as st
import base64

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


# ---------------------------------------------------------------- 数据加载
@st.cache_data(show_spinner=False)
def load_courses():
    with open(os.path.join(DATA_DIR, "courses.json"), "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_faq():
    with open(os.path.join(DATA_DIR, "faq.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def img_path(rel):
    """把 JSON 中的 /static/img/... 相对路径转为本地绝对路径。"""
    return os.path.join(BASE_DIR, rel.lstrip("/"))


def get_courses():
    return load_courses()["courses"]


def get_knowledge_points():
    points = []
    for c in get_courses():
        for kp in c["knowledge_points"]:
            kp = dict(kp)
            kp["_course_id"] = c["id"]
            kp["_course_name"] = c["name"]
            points.append(kp)
    return points


# ---------------------------------------------------------------- 检索引擎（与 Flask 版一致）
def normalize(text):
    text = re.sub(r"[\s\u3000，。！？、；：,.!?;:\"“”‘’（）()【】\[\]]+", "", text)
    return text.lower()


def search_knowledge(query, limit=8):
    q = normalize(query)
    if not q:
        return []
    scored = []
    for kp in get_knowledge_points():
        score = 0.0
        title = normalize(kp["title"])
        summary = normalize(kp["summary"])
        points_text = normalize("".join(kp["points"]))
        kw_text = normalize("|".join(kp["keywords"]))
        if q in title:
            score += 10.0
        for kw in kp["keywords"]:
            nkw = normalize(kw)
            if nkw and nkw in q:
                score += 6.0
        if q in kw_text:
            score += 5.0
        if q in summary:
            score += 3.0
        if q in points_text:
            score += 2.0
        for unit in [q[i:i + 2] for i in range(max(0, len(q) - 1))]:
            if len(unit) == 2 and unit in title:
                score += 0.5
            if len(unit) == 2 and unit in kw_text:
                score += 0.2
        if score > 0:
            scored.append((score, kp))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [kp for _, kp in scored[:limit]]


def search_faq(query):
    q = normalize(query)
    if not q:
        return None
    best = None
    best_score = 0.0
    for faq in load_faq()["faqs"]:
        score = 0.0
        hit_words = []
        for kw in faq["keywords"]:
            nkw = normalize(kw)
            if not nkw:
                continue
            if nkw in q:
                score += len(nkw)
                hit_words.append(kw)
            else:
                matched = sum(1 for i in range(len(nkw) - 1)
                              if nkw[i:i + 2] and nkw[i:i + 2] in q)
                score += matched * 0.3
        nq = normalize(faq["question"])
        if nq in q:
            score += 20.0
        if score > best_score:
            best_score = score
            best = {"faq": faq, "score": score, "hits": hit_words}
    if best is not None and best["score"] >= 2.0:
        return best
    return None


# ---------------------------------------------------------------- 页面组件
def show_image(rel, caption="", width=520):
    if rel:
        p = img_path(rel)
        if os.path.exists(p):
            st.image(p, caption=caption, use_container_width=True)
        else:
            st.warning(f"配图缺失：{rel}")
    return


def render_kp(kp, full=False):
    """渲染单个知识点（标题/概述/要点/关键词/配图）。"""
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown(f"##### {kp['id']} · {kp['title']}")
        st.markdown(kp["summary"])
        for p in (kp["points"] if full else kp["points"][:3]):
            st.markdown(f"- {p}")
        st.markdown("**关键词：** " + "、".join(kp["keywords"]))
    with c2:
        show_image(kp.get("image"), kp.get("image_caption", ""))
    st.divider()


# ---------------------------------------------------------------- 犇犇正能量组件
# 湖南农业大学吉祥物“犇犇”：表情丰富、定时说一句土管专业正能量话（学习/就业/社会地位），
# 说话对话框显示 5 秒后关闭，休息片刻再继续说下一句。
BENBEN_MESSAGES = [
    # 学习类
    {"t": "土地是财富之母。学土管，就是读懂大地这本最厚的书！📖", "e": "happy"},
    {"t": "今天多记一个地类编码，明天就多一双看懂国土的眼睛。🔍", "e": "wink"},
    {"t": "知识就像土壤肥力，勤学善用，终会迎来丰收季！🌾", "e": "happy"},
    {"t": "看懂一张土地利用现状图，就多一分把论文写在大地上的底气。🗺️", "e": "cheer"},
    {"t": "学习也要讲“占补平衡”——输入的努力足够，输出的成长自然平衡！⚖️", "e": "happy"},
    {"t": "测绘精度来自一次次校准，专业底气来自一遍遍复习。🎯", "e": "cheer"},
    {"t": "把每个专业概念，都变成你认知世界的坐标系吧！🧭", "e": "wink"},
    {"t": "深夜啃教材的你，正在为未来的国土事业积蓄能量。💪", "e": "star"},
    # 就业类
    {"t": "自然资源、住建、农业农村——土管人的舞台，比国土还要辽阔！🗺️", "e": "star"},
    {"t": "不动产登记、国土空间规划、土地估价，行行都有土管人的C位！🎯", "e": "cheer"},
    {"t": "土地估价师、规划师、测绘工程师——总有一款职业认证在等你拿下！📜", "e": "star"},
    {"t": "国土空间规划师是热门新职业，土管专业正踩在时代风口上！🚀", "e": "star"},
    {"t": "把 GIS 技能练熟，信息化岗位你就能一马当先！💻", "e": "cheer"},
    {"t": "今天的实训报告，就是你明天递给用人单位的“地籍档案”！📋", "e": "wink"},
    {"t": "从课堂到自然资源局，你差的只是一份漂亮的实习履历。🌟", "e": "happy"},
    {"t": "别小看每门专业课——面试官问的，正是你平时记的那些要点。✍️", "e": "wink"},
    # 社会地位与价值类
    {"t": "守护耕地红线，就是守护十四亿人的饭碗，土管人使命光荣！🍚", "e": "star"},
    {"t": "国土空间规划，绘的是山河，谋的是千秋，这份职业自带分量！⛰️", "e": "star"},
    {"t": "让每一寸土地都用得其所，土管人就是大地的“首席管家”！🏡", "e": "happy"},
    {"t": "参与土地征收与补偿、维护群众权益，土管工作有温度更有担当！🤝", "e": "happy"},
    {"t": "从宗地到国土，你经手的每个数据，都在服务国家治理。🏛️", "e": "cheer"},
    {"t": "第三次全国国土调查里有无数土管人的身影——你也可以成为其中一员！📊", "e": "star"},
    {"t": "土地是稀缺资源，管好用好它，就是为国家守住最宝贵的家底。🔐", "e": "happy"},
    {"t": "测绘人的足迹丈量山河，土管人的智慧规划未来，都值得尊敬！👏", "e": "cheer"},
]
BENBEN_EMOJI = {"学习": "📚", "就业": "💼", "价值": "🌟"}


@st.cache_data(show_spinner=False)
def benben_images_b64():
    """读取犇犇表情变体并转 base64 data URI（供前端组件使用）。"""
    faces = ["happy", "star", "wink", "cheer"]
    out = {}
    for f in faces:
        p = os.path.join(BASE_DIR, "static", "img", "benben", f"benben_{f}.png")
        with open(p, "rb") as fh:
            out[f] = "data:image/png;base64," + base64.b64encode(fh.read()).decode("ascii")
    return out


def benben_component():
    """在侧边栏嵌入犇犇吉祥物：多表情 + 弹跳/浮动/眨眼动画，
    定时轮播正能量话语，说话对话框显示 5 秒后关闭，休息后再说下一句。"""
    imgs = benben_images_b64()
    msgs = []
    for m in BENBEN_MESSAGES:
        msgs.append({"t": m["t"], "img": imgs[m["e"]]})
    msgs_json = json.dumps(msgs, ensure_ascii=False)
    html_code = """
<style>
body { background: transparent !important; margin: 0; padding: 0; }
@keyframes bb_bounce { 0%,100%{transform:translateY(0)} 30%{transform:translateY(-14px)} 60%{transform:translateY(-6px)} }
@keyframes bb_float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-5px)} }
#bb_img { width:auto; height:132px; transform-origin:bottom center; }
.bb-speak { animation: bb_bounce .9s ease-in-out infinite; }
.bb-idle { animation: bb_float 3.2s ease-in-out infinite; }
</style>
<div style="position:relative; width:100%; min-height:240px; font-family:'Microsoft YaHei',sans-serif;">
  <div id="bb_bubble" style="position:absolute; top:0; left:0; right:0;
       background:#ffffff; border:2px solid #2e7d32; border-radius:14px;
       box-shadow:0 4px 14px rgba(0,0,0,.15); padding:10px 12px;
       opacity:0; transition:opacity .45s; z-index:3;">
    <div style="display:flex; align-items:center; gap:6px;">
      <span style="background:#2e7d32; color:#fff; border-radius:9px;
            padding:1px 8px; font-size:12px; font-weight:bold; white-space:nowrap;">犇犇说</span>
      <span id="bb_txt" style="font-size:13px; line-height:1.5; color:#1b3a1b;"></span>
    </div>
    <div style="position:absolute; left:50%; bottom:-9px; margin-left:-8px; width:0; height:0;
         border-left:8px solid transparent; border-right:8px solid transparent;
         border-top:9px solid #2e7d32;"></div>
  </div>
  <img id="bb_img" src="__IMG0__" class="bb-idle"
       style="position:absolute; bottom:0; left:50%; transform:translateX(-50%);
       filter:drop-shadow(0 5px 9px rgba(0,0,0,.18)); z-index:2;"/>
</div>
<script>
(function(){
  const MSGS = __MSGS__;
  const bubble = document.getElementById('bb_bubble');
  const txt = document.getElementById('bb_txt');
  const img = document.getElementById('bb_img');
  const WINK = "__WINK__";
  let idx = 0;
  let cur = MSGS[0].img;
  const SHOW_MS = 5000;
  const REST_MS = 8000;
  function blink(){
    if (img.src !== WINK) { const t = img.src; img.src = WINK; setTimeout(()=>{ img.src = t; }, 180); }
  }
  setInterval(blink, 3600);
  function tick(){
    const m = MSGS[idx % MSGS.length];
    cur = m.img;
    txt.textContent = m.t;
    img.src = m.img;
    img.classList.remove('bb-idle');
    img.classList.add('bb-speak');
    bubble.style.opacity = 1;
    setTimeout(() => {
      bubble.style.opacity = 0;
      img.classList.remove('bb-speak');
      img.classList.add('bb-idle');
      setTimeout(() => { idx++; tick(); }, REST_MS);
    }, SHOW_MS);
  }
  setTimeout(tick, 800);
})();
</script>
"""
    html_code = html_code.replace("__IMG0__", imgs["happy"]).replace("__MSGS__", msgs_json).replace("__WINK__", imgs["wink"])
    st.components.v1.html(html_code, height=250, scrolling=False)


# ---------------------------------------------------------------- 页面：首页
def page_home():
    data = load_courses()
    meta = data["meta"]
    st.markdown(f"# {meta['title']}")
    st.markdown("> 培养德智体美劳全面发展，具备现代管理学、经济学、资源学与地理信息科学基本理论，"
                "掌握土地资源调查与评价、地籍管理、土地利用规划、土地估价、国土空间规划与治理等专业知识与技能，"
                "能在自然资源、农业农村、住房城乡建设、房地产等领域从事土地管理、规划、估价、调查与信息化管理等工作的"
                "复合应用型高级专门人才。")

    c1, c2, c3 = st.columns(3)
    c1.metric("核心课程", len(get_courses()))
    c2.metric("知识点", len(get_knowledge_points()))
    c3.metric("智能问答", len(load_faq()["faqs"]))

    st.markdown("## 课程群概览")
    st.markdown("五门课程对应人才培养目标的五大能力维度，形成"
                "“制度认知 → 业务技能 → 规划能力 → 估价实务 → 信息化素养”的递进式课程体系。")
    cols = st.columns(2)
    for i, c in enumerate(get_courses()):
        with cols[i % 2]:
            with st.container(border=True):
                show_image(f"/static/img/course/course-{c['id']}.png", "", width=1000)
                st.markdown(f"### {c['code']} · {c['name']}")
                st.caption(c["english_name"])
                st.markdown(c["brief"])
                for t in c["train_targets"]:
                    st.markdown(f"- ✓ {t}")
                st.markdown(f"知识点数：**{len(c['knowledge_points'])}**")

    st.markdown("## 能力培养矩阵")
    matrix = [
        ("理论素养与政策认知", "土地管理学", "土地制度、法规与政策运用能力", "自然资源行政管理岗"),
        ("地籍业务技能", "地籍管理", "地籍调查、登记、测量操作能力", "不动产登记、调查测绘岗"),
        ("规划编制与实施", "土地利用规划", "国土空间规划编制与管理能力", "规划编制、用途管制岗"),
        ("估价实务能力", "不动产估价", "估价方法运用与报告撰写能力", "土地评估、房地产估价机构"),
        ("信息化与空间分析", "GIS与遥感应用", "空间数据处理与遥感监测能力", "自然资源信息化、国土监测岗"),
    ]
    st.table(matrix)


# ---------------------------------------------------------------- 页面：课程学习
def page_course():
    st.markdown("# 课程知识库")
    st.markdown(f"覆盖 {len(get_courses())} 门课程、{len(get_knowledge_points())} 个核心知识点，"
                "每个知识点均配套示意图，点击图片可放大查看。")

    course_ids = [f"{c['code']} · {c['name']}" for c in get_courses()]
    sel = st.selectbox("选择课程", course_ids)
    course = get_courses()[course_ids.index(sel)]

    st.markdown(f"## {course['code']} · {course['name']}")
    st.caption(course["english_name"])
    st.markdown(course["brief"])
    st.markdown("**对应培养能力：**")
    for t in course["train_targets"]:
        st.markdown(f"- ✓ {t}")

    show_image(f"/static/img/course/course-{course['id']}.png", "", width=1000)

    st.markdown(f"### 核心知识点（{len(course['knowledge_points'])}）")
    for i, kp in enumerate(course["knowledge_points"]):
        with st.expander(f"{kp['id']} · {kp['title']}", expanded=(i < 2)):
            render_kp(kp, full=True)


# ---------------------------------------------------------------- 页面：知识检索
def page_search():
    st.markdown("# 知识点检索")
    q = st.text_input("输入关键词（如：占补平衡、界址、资本化率、卫片执法…）")
    if q:
        results = search_knowledge(q)
        st.markdown(f"### 检索结果：共 {len(results)} 条")
        if results:
            for kp in results:
                render_kp(kp, full=False)
        else:
            st.info("未找到相关知识点，建议尝试更短的关键词。")
    st.markdown("---")
    st.markdown("## 按课程浏览全部知识点")
    for c in get_courses():
        st.markdown(f"**{c['code']} · {c['name']}**（{len(c['knowledge_points'])} 个）")
        st.markdown("、".join(f"{kp['id']} {kp['title']}" for kp in c["knowledge_points"]))
        st.markdown("")


# ---------------------------------------------------------------- 页面：智能问答
def page_qa():
    st.markdown("# 智能问答")
    st.markdown("基于内置 900+ 条问答库的规则式智能答疑，无需联网。以自然语言提问，系统即时给出专业解答并配套示意图。")

    data = load_faq()
    suggested = data["suggested_questions"]
    st.markdown("**试试这样问：**")
    chips = "　·　".join(suggested[:8])
    st.caption(chips)

    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []

    q = st.text_input("请输入你的问题", key="qa_input")
    ask_btn = st.button("提问", type="primary", use_container_width=True)

    if ask_btn and q.strip():
        hit = search_faq(q)
        with st.container(border=True):
            if hit:
                faq = hit["faq"]
                st.markdown(f"**[{faq['category']}]** {faq['question']}")
                c1, c2 = st.columns([3, 2])
                with c1:
                    st.markdown(faq["answer"])
                with c2:
                    show_image(faq.get("image"), faq.get("image_caption", ""))
                related = [f for f in data["faqs"]
                           if f["id"] != faq["id"] and f["category"] == faq["category"]][:3]
                if related:
                    st.markdown("**相关提问：** " + "　·　".join(r["question"] for r in related))
            else:
                related_kps = search_knowledge(q, limit=3)
                if related_kps:
                    st.markdown("未在问答库中找到直接匹配，以下是最相关的知识点：")
                    c1, c2 = st.columns([3, 2])
                    with c1:
                        for kp in related_kps:
                            st.markdown(f"**{kp['id']} · {kp['title']}**（{kp['_course_name']}）")
                            st.markdown(kp["summary"])
                    with c2:
                        show_image(related_kps[0].get("image"), related_kps[0].get("image_caption", ""))
                else:
                    st.markdown(data["fallback_tip"])
                    st.markdown("**可以试试：** " + "　·　".join(data["suggested_questions"][:5]))

    if st.session_state.qa_history:
        st.markdown("---")
        st.markdown("### 最近提问")
        for h in st.session_state.qa_history[-5:]:
            st.caption(h)


# ---------------------------------------------------------------- 主入口
st.set_page_config(page_title="土管AI实训平台", page_icon="🌏", layout="wide")
st.sidebar.markdown("## 🌏 土管AI实训平台")
st.sidebar.markdown("土地资源管理专业课余自主学习系统")
st.sidebar.markdown("综合人才培养目标与五门核心课程：土地管理学、地籍管理、土地利用规划、不动产估价、GIS与遥感应用。")
st.sidebar.divider()

page = st.sidebar.radio("功能导航", ["首页", "课程学习", "知识检索", "智能问答"])
st.sidebar.divider()
st.sidebar.caption("知识点 68 个 · 智能问答 904 条 · 全部配图")
with st.sidebar:
    benben_component()

if page == "首页":
    page_home()
elif page == "课程学习":
    page_course()
elif page == "知识检索":
    page_search()
else:
    page_qa()
