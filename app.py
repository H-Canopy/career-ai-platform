"""
大学生AI职业规划平台 - Motionsites暗黑风格
"""
import streamlit as st
from llm import call_llm_with_system, call_llm_stream
from prompts_loader import build_prompt
from agent import PlannerAgent, ExecutorAgent
from rag.retrieval import resume_engine, job_engine, init_resume_engine, init_job_engine
import docx
import fitz  # PyMuPDF
import io

# ===================== 页面配置 =====================
st.set_page_config(
    page_title="大学生AI职业规划平台",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== Motionsites 暗黑 CSS =====================
st.markdown("""
<style>
/* ============================================================
 *  Dark Premium — Modern dark theme for AI Career Platform
 *  Inter + subtle indigo accent, layered depth
 * ============================================================ */
@import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600;14..32,700&display=swap');

/* -- Palette -- */
:root {
    --bg: #0B0B12;
    --surface: #14141F;
    --surface-alt: #1A1A28;
    --sidebar: #08080C;
    --text: #EDEDF0;
    --text-secondary: #9494A8;
    --text-muted: #5C5C70;
    --accent: #818CF8;
    --accent-hover: #6366F1;
    --accent-subtle: rgba(129, 140, 248, 0.10);
    --border: rgba(255, 255, 255, 0.06);
    --border-hover: rgba(255, 255, 255, 0.12);
    --success: #4ADE80;
    --radius: 10px;
}

/* -- Global -- */
.stApp { background: var(--bg); }
html, body, .stApp, #root, section, main, [data-testid="stAppViewContainer"] {
    scroll-behavior: smooth;
    color-scheme: dark !important;
}
/* 手机端：所有表单控件强制暗黑渲染（iOS Safari/Android Chrome） */
@media (hover: none) and (pointer: coarse) {
    *, *::before, *::after { color-scheme: dark !important; }
    input, select, textarea, button { color-scheme: dark !important; }
}

/* -- Typography -- */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', -apple-system, sans-serif !important;
    color: var(--text) !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em;
    line-height: 1.3;
}
h1 { font-size: 2.2rem !important; letter-spacing: -0.03em !important; }
h2 { font-size: 1.6rem !important; }
h3 { font-size: 1.2rem !important; }

/* -- Gradient Title (Full-Spectrum Rainbow) -- */
.gradient-title, .gradient-title * {
    background: linear-gradient(135deg,
        #FF6B6B 0%,    /* 珊瑚红 */
        #FECA57 12%,   /* 金黄 */
        #48DBFB 25%,   /* 天蓝 */
        #FF9FF3 37%,   /* 粉紫 */
        #54A0FF 50%,   /* 宝蓝 */
        #5F27CD 62%,   /* 深紫 */
        #FF6B6B 75%,   /* 回到珊瑚红 */
        #FECA57 87%,   /* 金黄 */
        #48DBFB 100%   /* 天蓝 */
    ) !important;
    -webkit-background-clip: text !important;
    background-clip: text !important;
    color: transparent !important;
    -webkit-text-fill-color: transparent !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    animation: rainbowFlow 4s linear infinite;
    background-size: 400% 400% !important;
}
@keyframes rainbowFlow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
p, div, span, li, label {
    color: var(--text) !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}
/* Material Icons 必须保留字体，否则图标文字会暴露为普通文字 */
span[data-testid="stIconMaterial"] {
    font-family: "Material Icons" !important;
    font-size: 24px !important;
    color: var(--text-muted) !important;
    line-height: 1 !important;
}

/* -- Sidebar -- */
section[data-testid="stSidebar"] {
    background: var(--sidebar) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] div {
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif !important;
}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    color: var(--text-secondary) !important;
    transition: all 0.2s ease;
    padding: 4px 8px !important;
    border-radius: 6px !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    color: var(--text) !important;
    background: rgba(255,255,255,0.03) !important;
}
section[data-testid="stSidebar"] hr {
    border-color: var(--border) !important;
}

/* -- Buttons -- */
button[kind="primary"], .stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.2s ease;
}
button[kind="primary"]:hover, .stButton > button:hover {
    background: var(--accent-hover) !important;
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3) !important;
    transform: translateY(-1px);
}
button[kind="secondary"], [data-testid="stBaseButton-secondary"] {
    background: transparent !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.2s ease;
}
button[kind="secondary"]:hover, [data-testid="stBaseButton-secondary"]:hover {
    border-color: var(--border-hover) !important;
    background: rgba(255,255,255,0.03) !important;
}

/* -- Cards / Containers -- */
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
    background: transparent !important;
    border: none !important;
}
[data-testid="column"] > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 0.5rem !important;
    transition: border-color 0.2s;
}
[data-testid="column"] > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:hover {
    border-color: var(--border-hover) !important;
}

/* -- Inputs -- */
input, textarea, select, .stTextInput input, .stTextArea textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 0.8rem !important;
    color: var(--text) !important;
    transition: border-color 0.2s;
}
input:focus, textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-subtle) !important;
    outline: none !important;
}

/* -- Select / MultiSelect（手机端全量修复） -- */
div[data-baseweb="select"] {
    background: #0F0F17 !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: var(--radius) !important;
}
/* 所有内层元素硬编码暗黑背景 */
div[data-baseweb="select"] * {
    background-color: transparent !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
div[data-baseweb="select"] > div {
    background: #0F0F17 !important;
}
/* 暴力去除所有 focus 黑框 */
div[data-baseweb="select"] *:focus,
div[data-baseweb="select"] *:focus-visible,
div[data-baseweb="select"]:focus-within,
div[data-baseweb="select"] [tabindex]:focus {
    outline: none !important;
    box-shadow: none !important;
}
div[data-baseweb="select"]:focus-within {
    border-color: var(--accent) !important;
}
/* selected value container */
div[data-baseweb="select"] div[class*="Value"],
div[data-baseweb="select"] div[class*="singleValue"] {
    background: #0F0F17 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
/* placeholder */
div[data-baseweb="select"] div[class*="placeholder"] {
    color: #888893 !important;
    -webkit-text-fill-color: #888893 !important;
}
/* 下拉箭头 */
div[data-baseweb="select"] svg { fill: #888893 !important; }
/* 移动端 select 盒子本身强制黑底 */
@media (hover: none) and (pointer: coarse) {
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] * {
        background-color: #0F0F17 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
}

/* -- Slider -- */
div[data-testid="stSlider"] * { color: var(--text) !important; }
div[data-testid="stSlider"] > div > div {
    background: var(--surface) !important;
}

/* -- Metrics -- */
[data-testid="stMetricValue"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: var(--text) !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}
[data-testid="stMetricDelta"] {
    color: var(--accent) !important;
}

/* -- Links -- */
a {
    color: var(--accent) !important;
    text-decoration: none;
    transition: opacity 0.2s;
}
a:hover { opacity: 0.8; text-decoration: underline; }

/* -- Code -- */
code {
    background: var(--surface-alt) !important;
    color: var(--accent) !important;
    border-radius: 4px !important;
    padding: 2px 6px;
    font-size: 0.85rem;
    border: 1px solid var(--border);
}
pre {
    background: var(--surface-alt) !important;
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
}

/* -- Tabs -- */
div[data-testid="stTabs"] button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    color: var(--text-muted) !important;
    border-radius: var(--radius) !important;
    transition: all 0.2s;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--text) !important;
    background: var(--surface) !important;
}

/* -- DataFrames / Tables -- */
[data-testid="stDataFrame"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

/* -- Expander -- */
.streamlit-expanderHeader {
    background: var(--surface) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    border: 1px solid var(--border) !important;
}

/* -- Info / Success / Warning / Error -- */
.stAlert {
    border-radius: var(--radius) !important;
    border: none !important;
}
div[data-testid="stNotification"] {
    border-radius: var(--radius) !important;
}

/* -- Scrollbar -- */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--border-hover); }

/* -- Cards custom class -- */
.glass-card {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1.5rem !important;
    margin-bottom: 1rem !important;
    transition: border-color 0.2s;
}
.glass-card:hover {
    border-color: var(--border-hover) !important;
}

/* -- Footer -- */
.footer {
    text-align: center;
    padding: 2rem 0;
    border-top: 1px solid var(--border);
    margin-top: 3rem;
}
.footer p {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.7rem !important;
    color: var(--text-muted) !important;
}

/* -- Button in container (card buttons) -- */
[data-testid="stVerticalBlock"] > [data-testid="element-container"] + [data-testid="element-container"] button {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: var(--radius) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.2s;
}
[data-testid="stVerticalBlock"] > [data-testid="element-container"] + [data-testid="element-container"] button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: var(--accent-subtle) !important;
}

/* -- Header -- */
header[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }

/* 隐藏 Deploy 按钮 */
button[data-testid="stBaseButton-header"],
button:has(> [data-testid="stBaseButton-header"]),
.stDeployButton, [data-testid="stHeaderActionElements"] {
    display: none !important;
}

/* 侧边栏折叠/展开按钮 → 隐藏 Material Icon，换成白色 «  */
/* 1) 折叠按钮 — 侧边栏开着时的收起按钮 */
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarHeader"] button,
button[data-testid="stBaseButton-headerNoPadding"] {
    font-size: 0 !important;
    position: relative;
}
[data-testid="stSidebarCollapseButton"] button > *,
[data-testid="stSidebarHeader"] button > *,
button[data-testid="stBaseButton-headerNoPadding"] > * {
    display: none !important;
}
/* 折叠按钮 ← 用 ::after 画白色 « */
[data-testid="stSidebarCollapseButton"] button::after,
[data-testid="stSidebarHeader"] button::after,
button[data-testid="stBaseButton-headerNoPadding"]::after {
    content: "«";
    font-size: 26px;
    font-weight: 300;
    color: #FFFFFF;
    font-family: 'Inter', -apple-system, sans-serif;
    line-height: 1;
    opacity: 1 !important;
    position: static;
}
/* 2) 展开按钮 — 侧边栏折叠后出现 */
button[data-testid="stExpandSidebarButton"] {
    font-size: 0 !important;
    width: 40px !important;
    height: 40px !important;
    position: relative;
    background: rgba(255,255,255,0.1) !important;
    border-radius: 6px !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    margin: 6px 8px !important;
    cursor: pointer;
}
button[data-testid="stExpandSidebarButton"] > * {
    display: none !important;
}
button[data-testid="stExpandSidebarButton"]::before {
    content: "«";
    font-size: 26px;
    font-weight: 300;
    color: #FFFFFF;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    line-height: 1;
    font-family: 'Inter', -apple-system, sans-serif;
    opacity: 1;
}
button[data-testid="stExpandSidebarButton"]:hover {
    background: rgba(255,255,255,0.18) !important;
    border-color: rgba(255,255,255,0.25) !important;
}

/* -- 下拉框防遮挡 + 手机端暗黑适配 -- */
[data-baseweb="select"] [role="listbox"],
[data-baseweb="popover"] {
    z-index: 999999 !important;
}
div[data-baseweb="select"] {
    margin-bottom: 8px;
}
/* 下拉选项：背景深色 + 文字纯白（硬编码，不走CSS变量） */
[data-baseweb="popover"] *,
[data-baseweb="popover"] li,
[data-baseweb="popover"] [role="option"],
[data-baseweb="select"] [role="listbox"] *,
ul[role="listbox"] *,
ul[role="listbox"] li {
    background: #1A1A24 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
/* 选中态 */
[data-baseweb="select"] [aria-selected="true"],
[data-baseweb="popover"] [aria-selected="true"] {
    background: rgba(129, 140, 248, 0.18) !important;
    color: #818CF8 !important;
}
/* 下拉框输入/显示的文字 */
div[data-baseweb="select"] input,
div[data-baseweb="select"] [data-testid="stSelectbox"] {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
/* MultiSelect 标签 */
div[data-baseweb="tag"] {
    background: var(--surface-alt) !important;
    color: #FFFFFF !important;
}
/* 下拉框 hover */
[data-baseweb="select"] [role="option"]:hover,
ul[role="listbox"] li:hover,
[data-baseweb="popover"] li:hover {
    background: rgba(129, 140, 248, 0.14) !important;
    color: #FFFFFF !important;
}

/* -- Reduced motion -- */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.2s !important;
    }
    html { scroll-behavior: auto; }
}

/* ==================================================
   🌅☀️🌙 日升日落 · 月升月落 循环（增强版）
   ================================================== */
/* 天空光晕层 — 随循环切换暖金↔冷银 */
.sky-glow {
    position: fixed; top: 0; left: 0;
    width: 100%; height: 55%;
    pointer-events: none; z-index: 0;
    animation: skyShift 90s ease-in-out infinite;
    opacity: 0.06;
}
@keyframes skyShift {
    0%, 100% { background: radial-gradient(ellipse 80% 60% at 50% 3%, #1a2744, transparent); }
    13%      { background: radial-gradient(ellipse 80% 60% at 20% 6%, #3a2412, transparent); }
    28%      { background: radial-gradient(ellipse 55% 45% at 48% 1%, #4d3018, transparent); }
    42%      { background: radial-gradient(ellipse 80% 60% at 60% 5%, #352214, transparent); }
    50%      { background: radial-gradient(ellipse 80% 60% at 65% 6%, #2a2538, transparent); }
    65%      { background: radial-gradient(ellipse 80% 60% at 50% 8%, #1d2a3c, transparent); }
}

/* ========== ☀️ 太阳 — 艺术光晕、光圈、呼吸辉光 ========== */
.sun-orb {
    position: fixed; z-index: 0; pointer-events: none;
    width: 50px; height: 50px;
    border-radius: 50%;
    /* 内核：从白到金到橙的暖渐变 */
    background: radial-gradient(circle at 40% 35%,
        #FFFDE8 0%, #FFE9A0 15%, #FDB833 40%, #E8781A 70%, #B8400C 100%);
    /* 三层辉光 */
    box-shadow:
        0 0 20px rgba(255,200,50,.65),
        0 0 60px rgba(255,150,30,.4),
        0 0 130px rgba(255,110,20,.15);
    filter: blur(0.4px);
    animation: orbArc 90s ease-in-out infinite;
}
/* 内光圈 — 呼吸缩放 */
.sun-orb::before {
    content: ""; position: absolute;
    inset: -18px; border-radius: 50%;
    border: 1.5px solid rgba(255,200,110,.28);
    animation: coronaBreath 4s ease-in-out infinite;
}
/* 外光晕 — 更大的辉光环 */
.sun-orb::after {
    content: ""; position: absolute;
    inset: -40px; border-radius: 50%;
    background: radial-gradient(circle, rgba(255,160,40,.12) 0%, transparent 65%);
    animation: haloBreath 6s ease-in-out infinite;
}
@keyframes coronaBreath {
    0%, 100% { transform: scale(1);    opacity: .25; }
    50%      { transform: scale(1.18); opacity: .55; }
}
@keyframes haloBreath {
    0%, 100% { transform: scale(0.92); opacity: .4; }
    50%      { transform: scale(1.12); opacity: 1; }
}

/* ========== 🌙 月亮 — 银白满月 + 光晕 ========== */
.moon-orb {
    position: fixed; z-index: 0; pointer-events: none;
    width: 42px; height: 42px;
    border-radius: 50%;
    background: radial-gradient(circle at 40% 35%,
        #FDFEFF 0%, #EAEEF6 30%, #C8D0E2 65%, #9EAAC4 100%);
    box-shadow:
        0 0 20px rgba(200,210,235,.45),
        0 0 50px rgba(180,195,225,.2),
        0 0 100px rgba(170,185,215,.08);
    animation: orbArc 90s ease-in-out infinite;
    animation-delay: 45s;
}
/* 环形山纹理 */
.moon-orb::before {
    content: ""; position: absolute;
    inset: 0; border-radius: 50%;
    background:
        radial-gradient(circle 4px at 28% 28%, rgba(120,135,160,.35) 100%, transparent),
        radial-gradient(circle 3px at 58% 38%, rgba(115,130,155,.25) 100%, transparent),
        radial-gradient(circle 5px at 42% 62%, rgba(125,140,165,.3) 100%, transparent),
        radial-gradient(circle 2px at 70% 55%, rgba(110,125,150,.2) 100%, transparent);
    pointer-events: none;
}

/* ========== 🚀 SpaceX 火箭 — 右方直飞上升 ========== */
.rocket {
    position: fixed; z-index: 0; pointer-events: none;
    animation: rocketLaunch 36s ease-in infinite;
}
/* 箭体 — 银白圆柱 */
.rocket-body {
    position: relative;
    width: 14px; height: 72px;
    background: linear-gradient(180deg,
        #F0F0F5 0%, #D8D8E2 20%, #C5C5D2 50%, #B0B0BE 80%, #9A9AA8 100%);
    border-radius: 7px 7px 3px 3px;
    box-shadow:
        0 0 15px rgba(210,210,230,.4),
        0 0 40px rgba(190,190,215,.15),
        inset -3px 0 8px rgba(0,0,0,.08);
}
/* 整流罩/鼻锥 */
.rocket-body::before {
    content: "";
    position: absolute;
    bottom: 100%;
    left: 50%; transform: translateX(-50%);
    width: 0; height: 0;
    border-left: 7px solid transparent;
    border-right: 7px solid transparent;
    border-bottom: 18px solid #DCDCE6;
    filter: drop-shadow(0 -1px 2px rgba(180,180,200,.3));
}
/* 尾翼 */
.rocket-body::after {
    content: "";
    position: absolute;
    top: 94%;
    left: 50%; transform: translateX(-50%);
    width: 24px; height: 10px;
    background: #9090A4;
    clip-path: polygon(0% 0%, 28% 100%, 50% 55%, 72% 100%, 100% 0%);
}
/* 舷窗 */
.rocket-window {
    position: absolute;
    top: 22px; left: 50%; transform: translateX(-50%);
    width: 6px; height: 6px;
    background: #60A5FA;
    border-radius: 50%;
    box-shadow: 0 0 6px #60A5FA, 0 0 14px rgba(96,165,250,.4);
    z-index: 1;
}
/* 引擎尾焰 — 双层 + 抖动 */
.rocket-flame {
    position: absolute;
    top: 100%; left: 50%; transform: translateX(-50%);
    width: 8px; height: 36px;
    border-radius: 4px;
    background: linear-gradient(to bottom,
        #FBBF24 0%, #F59E0B 25%, #EF4444 60%, rgba(239,68,68,0) 100%);
    box-shadow: 0 0 16px rgba(245,158,11,.6), 0 0 40px rgba(239,68,68,.3);
    animation: flameFlicker .12s ease-in-out infinite alternate;
}
@keyframes flameFlicker {
    0%   { height: 36px; opacity: .9; }
    100% { height: 42px; opacity: 1; }
}
/* 直飞轨迹 — 火箭先飞走，卫星才出现 */
@keyframes rocketLaunch {
    0%   { right: 6%; bottom: -18%; opacity: 0; }
    6%   { right: 6%; bottom: -4%;  opacity: 1; }
    35%  { right: 6%; bottom: 50%;  opacity: 1; }
    55%  { right: 6%; bottom: 85%;  opacity: .4; }
    65%  { right: 6%; bottom: 108%; opacity: 0; }
    100% { right: 6%; bottom: 108%; opacity: 0; }
}

/* ========== 🛰️ 旅行者一号 — 火箭飞走后才出现 + 自旋 ========== */
.voyager {
    position: fixed; z-index: 0; pointer-events: none;
    top: 5%; right: 6%;
    opacity: 0;
    animation: voyagerOrbit 36s ease-in-out infinite;
    animation-delay: 23s;  /* ← 火箭 65% 消失后（~23.4s）才登场 */
}
/* 高增益天线 — 大圆盘（旅行者标志） */
.voyager-dish {
    position: relative;
    width: 42px; height: 42px;
    border-radius: 50%;
    border: 2px solid rgba(180,195,220,.4);
    background: radial-gradient(circle at 38% 35%,
        rgba(210,220,240,.2) 0%, rgba(180,195,220,.08) 40%, transparent 65%);
    box-shadow: 0 0 20px rgba(170,185,215,.25), 0 0 50px rgba(160,175,205,.08);
}
/* 天线内部同心圆 */
.voyager-dish::before {
    content: "";
    position: absolute;
    inset: 8px; border-radius: 50%;
    border: 1px solid rgba(180,195,220,.25);
}
/* 天线馈源（中心小圆） */
.voyager-dish::after {
    content: "";
    position: absolute;
    top: 50%; left: 50%; transform: translate(-50%, -50%);
    width: 6px; height: 6px;
    background: rgba(200,210,230,.4);
    border-radius: 50%;
    box-shadow: 0 0 8px rgba(180,195,220,.3);
}
/* 探测器主体 — 十边形总线 */
.voyager-body {
    position: absolute;
    top: 42px; left: 50%; transform: translateX(-50%);
    width: 28px; height: 28px;
    background: linear-gradient(135deg, #B8C0D4, #8E98B0);
    clip-path: polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%);
    box-shadow: 0 0 12px rgba(150,160,185,.35);
}
/* 磁强计悬臂 — 向右延伸 */
.voyager-body::before {
    content: "";
    position: absolute;
    top: 50%; left: 100%; transform: translateY(-50%);
    width: 50px; height: 2px;
    background: linear-gradient(90deg, rgba(160,175,195,.6), rgba(160,175,195,.1));
}
/* RTG 同位素电池臂 — 向左 */
.voyager-body::after {
    content: "";
    position: absolute;
    top: 50%; right: 100%; transform: translateY(-50%);
    width: 30px; height: 5px;
    background: linear-gradient(270deg, #6B7280, #4B5563);
    border-radius: 2px;
}
/* 信号灯 */
.voyager-light {
    position: absolute;
    top: -14px; left: 50%; transform: translateX(-50%);
    width: 5px; height: 5px;
    background: #34D399;
    border-radius: 50%;
    box-shadow: 0 0 8px #34D399, 0 0 18px rgba(52,211,153,.4);
    animation: voyagerBlink 2s ease-in-out infinite;
}
@keyframes voyagerOrbit {
    0%   { opacity: 0; transform: translateX(30px) rotate(0deg); }
    15%  { opacity: 1; transform: translateX(0)   rotate(90deg); }
    50%  { opacity: 1; transform: translateX(0)   rotate(360deg); }
    80%  { opacity: 1; transform: translateX(0)   rotate(630deg); }
    100% { opacity: 0; transform: translateX(-20px) rotate(720deg); }
}
@keyframes voyagerBlink {
    0%, 100% { opacity: 1; }
    35%      { opacity: .25; }
    70%      { opacity: .7; }
}

/* ========== 共同的弧形轨迹 ========== */
@keyframes orbArc {
    0%   { left: -7%;  top: 22%; opacity: 0;   transform: scale(0.5); }
    6%   { left: 2%;   top: 15%; opacity: 0.7; transform: scale(1); }
    18%  { left: 20%;  top: 5%;  opacity: 1;   transform: scale(1.1); }
    35%  { left: 45%;  top: 2%;  opacity: 1;   transform: scale(1.05); }
    50%  { left: 55%;  top: 3%;  opacity: 0.4; transform: scale(0.82); }
    58%  { left: 70%;  top: 9%;  opacity: 0.12;transform: scale(0.5); }
    70%  { left: 92%;  top: 18%; opacity: 0;   transform: scale(0.4); }
    100% { left: 105%; top: 26%; opacity: 0;   transform: scale(0.3); }
}
</style>
""", unsafe_allow_html=True)

# 天空层：日升日落 + 月升月落 + SpaceX 火箭 + 旅行者一号 循环动画
st.markdown("""
<div class="sky-glow"></div>
<div class="sun-orb"></div>
<div class="moon-orb"></div>
<div class="rocket">
    <div class="rocket-body">
        <div class="rocket-window"></div>
    </div>
    <div class="rocket-flame"></div>
</div>
<div class="voyager">
    <div class="voyager-dish">
        <div class="voyager-light"></div>
    </div>
    <div class="voyager-body"></div>
</div>
""", unsafe_allow_html=True)


# ===================== 初始化 =====================
planner = PlannerAgent()
executor = ExecutorAgent()

if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 首页总览"

@st.cache_resource
def get_rag_engines():
    init_resume_engine()
    init_job_engine()
    return resume_engine, job_engine

def call_ai(prompt: str) -> str:
    try:
        with st.spinner("🤖 AI 分析中..."):
            return call_llm_with_system("", prompt)
    except Exception as e:
        st.error(f"❌ 调用失败：{str(e)}")
        return None

def stream_ai(prompt: str) -> str:
    """流式调用 AI，逐字输出，体验跟豆包一样快"""
    try:
        stream = call_llm_stream("", prompt)
        return st.write_stream(stream)
    except Exception as e:
        st.error(f"❌ 调用失败：{str(e)}")
        return None


# ===================== 侧边栏 =====================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:24px 0 16px 0;">
        <div style="font-size:42px; margin-bottom:8px;">🎓</div>
        <h2 style="margin:0; font-size:20px; font-weight:700;">大学生AI助手</h2>
        <p style="color:var(--text-muted); font-size:12px; margin:4px 0 0 0;">考研 · 就业 · 考公 · 创业</p>
    </div>
    <hr style="border-color:rgba(255,255,255,0.04); margin:0 0 16px 0;">
    """, unsafe_allow_html=True)

    def on_sidebar_change():
        st.session_state.current_page = st.session_state.sidebar_radio

    st.markdown('<p style="font-size:11px; color:var(--text-muted); margin:0 0 6px 0; letter-spacing:0.08em; text-transform:uppercase;">📋 导航</p>', unsafe_allow_html=True)
    menu = st.radio("", ["🏠 首页总览", "📊 决策辅助", "📝 简历诊断", "💼 岗位推荐", "🤖 智能体协同", "💡 形象分析", "📜 隐私协议"], label_visibility="collapsed", key="sidebar_radio", on_change=on_sidebar_change)

    st.markdown("<hr style='border-color:rgba(255,255,255,0.04); margin:16px 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(255,255,255,0.03); border-radius:14px; padding:14px;">
        <p style="margin:0; font-size:11px; color:var(--text-muted);">🔌 API 状态</p>
        <p style="margin:4px 0 0 0; font-size:13px; color:#4ade80;">✅ DeepSeek</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(255,255,255,0.03); border-radius:14px; padding:14px; margin-top:12px;">
        <p style="margin:0; font-size:11px; color:var(--text-muted);">📂 资源</p>
        <a href="https://github.com/H-Canopy/resume-template" target="_blank" style="font-size:13px; color:var(--accent); text-decoration:none; display:block; margin-top:6px;">📄 简历模板 →</a>
    </div>
    """, unsafe_allow_html=True)


# ===================== 装饰组件 =====================
def glass_card(content, extra_style=""):
    """毛玻璃卡片包裹器"""
    st.markdown(f'<div class="glass-card" style="{extra_style}">', unsafe_allow_html=True)
    content()
    st.markdown('</div>', unsafe_allow_html=True)

def section_banner(emoji, title, subtitle):
    st.markdown(f"""
    <div style="text-align:center; padding:16px 20px 12px 20px;">
        <div style="font-size:48px; margin-bottom:8px;">{emoji}</div>
        <h1 class="gradient-title" style="font-size:36px;">{title}</h1>
        <p style="color:var(--text-secondary); font-size:15px; margin-top:8px;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

def step_indicator(steps, current=0):
    html = '<div style="display:flex; align-items:center; justify-content:center; gap:0; margin-bottom:28px;">'
    for i, step in enumerate(steps):
        active = i == current
        dot_bg = 'var(--accent)' if active else 'var(--surface-alt)'
        dot_color = '#fff' if active else 'var(--text-muted)'
        html += f'<div style="display:flex; flex-direction:column; align-items:center; gap:6px;">'
        html += f'<div style="width:30px;height:30px;border-radius:50%;background:{dot_bg};color:{dot_color};display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px;">{i+1}</div>'
        html += f'<span style="font-size:12px;color:{dot_color};">{step}</span></div>'
        if i < len(steps) - 1:
            line_color = 'var(--accent)' if i < current else 'var(--border)'
            html += f'<div style="width:48px;height:1px;background:{line_color};margin:0 4px;margin-top:-18px;"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def result_card(result_text):
    st.markdown("---")
    st.markdown("""
    <div style="background:var(--surface); border:1px solid var(--border);
        border-radius:var(--radius); padding:32px; margin:16px 0; position:relative;">
        <div style="position:absolute; top:-14px; left:24px;
            background:var(--accent);
            color:white; padding:4px 18px; border-radius:20px; font-size:13px; font-weight:600;">
        ✨ AI 分析结果</div>
    """, unsafe_allow_html=True)
    if result_text:
        st.markdown(result_text)
    st.markdown("</div>", unsafe_allow_html=True)


# ===================== 简历文件解析 =====================
def parse_resume_file(uploaded_file) -> str:
    """解析上传的 Word/PDF 简历文件，返回文本内容"""
    filename = uploaded_file.name.lower()
    file_bytes = uploaded_file.read()

    if filename.endswith(".docx"):
        # Word 文档
        doc = docx.Document(io.BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return text

    elif filename.endswith(".pdf"):
        # PDF 文档
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text

    else:
        raise ValueError("仅支持 .docx 和 .pdf 格式")


# ===================== 首页 =====================
def show_home():
    st.markdown("""
    <div style="text-align:center; padding:12px 20px 8px 20px;">
        <h1 class="gradient-title">大学生AI职业规划平台</h1>
        <p style="color:var(--text-secondary); font-size:16px; margin-top:8px;">
        多智能体协同 · RAG检索增强 · 智能化职业决策
        </p>
    </div>
    """, unsafe_allow_html=True)

    # metric 行
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 决策分析", "考研/就业/考公/创业", "智能评估")
    c2.metric("📝 简历诊断", "AI 评分", "精准建议")
    c3.metric("💼 岗位推荐", "实时匹配", "千人千面")
    c4.metric("🤖 智能体", "协同工作", "Planner+Executor")

    st.markdown("<br>", unsafe_allow_html=True)

    # 功能卡片 - 整张卡片可点击跳转
    st.markdown('<h3 style="color:var(--text); margin-bottom:20px;">🚀 核心功能</h3>', unsafe_allow_html=True)

    cards_info = [
        ("📊", "考研 / 就业 / 考公 / 创业决策", "AI 结合专业、成绩、兴趣，量化评估发展方向（含创业路径）", "📊 决策辅助"),
        ("📝", "简历智能诊断", "逐项分析简历质量，格式+内容+关键词优化建议", "📝 简历诊断"),
        ("💼", "岗位精准推荐", "基于技能画像匹配岗位，附带行业分析和成长路径", "💼 岗位推荐"),
        ("🤖", "智能体协同模式", "Planner+Executor 双Agent，自然语言驱动任务执行", "🤖 智能体协同"),
    ]

    col1, col2 = st.columns(2)
    for idx, (icon, title, desc, target_page) in enumerate(cards_info):
        col = col1 if idx % 2 == 0 else col2
        with col:
            # 用 container 保持卡片外观，整张卡片就是按钮
            with st.container(border=True):
                st.markdown(f"""
                <div style="text-align:center; padding:8px 0 4px 0;">
                    <div style="font-size:36px; margin-bottom:8px;">{icon}</div>
                    <div style="font-size:16px; font-weight:700; color:var(--text); margin-bottom:4px;">{title}</div>
                    <div style="font-size:12px; color:var(--text-secondary); line-height:1.5;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🚀 进入 {target_page}", key=f"card_{idx}", use_container_width=True):
                    st.session_state.current_page = target_page
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # 技术架构
    st.markdown('<h3 style="color:var(--text); margin-bottom:16px;">⚙️ 技术架构</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="glass-card">
            <h4 style="color:var(--accent);">🧠 智能体层</h4>
            <p style="color:var(--text-secondary); font-size:13px;">Planner Agent · Executor Agent · 工具调用</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="glass-card">
            <h4 style="color:var(--accent);">🔍 RAG 检索层</h4>
            <p style="color:var(--text-secondary); font-size:13px;">Embedding 向量化 · 语义检索 · 知识库</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="glass-card">
            <h4 style="color:var(--accent);">🎯 提示词工程</h4>
            <p style="color:var(--text-secondary); font-size:13px;">YAML 配置化 · 变量注入 · 模块化设计</p>
        </div>
        """, unsafe_allow_html=True)


# ===================== 决策辅助（新版：8步问卷 + 四条路径评分 + 追问） =====================
def _score_career_paths(info):
    """基于用户信息的四条路径评分引擎（0-100）"""
    scores = {"💼 直接就业": 50, "🎓 考研深造": 50, "🏛️ 考公务员": 50, "🚀 自主创业": 50}

    # 成绩排名
    grade_map = {"前5%": 15, "前10%": 10, "前20%": 5, "前30%": 0, "前50%": -5, "其他": -10}
    g = grade_map.get(info.get("grade", ""), 0)
    scores["🎓 考研深造"] += g * 1.8
    scores["💼 直接就业"] += g * 1.2
    scores["🏛️ 考公务员"] += g * 0.5
    scores["🚀 自主创业"] += g * 0.5

    # 核心诉求
    focus = info.get("focus", "")
    if "赚钱" in focus:
        scores["💼 直接就业"] += 18
        scores["🚀 自主创业"] += 22
        scores["🏛️ 考公务员"] -= 15
    elif "稳定" in focus:
        scores["🏛️ 考公务员"] += 25
        scores["💼 直接就业"] += 5
        scores["🚀 自主创业"] -= 20
        scores["🎓 考研深造"] += 3
    elif "发展" in focus:
        scores["🎓 考研深造"] += 12
        scores["💼 直接就业"] += 10
        scores["🚀 自主创业"] += 10
    elif "成就" in focus:
        scores["🚀 自主创业"] += 15
        scores["💼 直接就业"] += 12
        scores["🎓 考研深造"] += 5

    # 风险承受
    try:
        risk = int(info.get("risk", 5))
    except (ValueError, TypeError):
        risk = 5
    scores["🚀 自主创业"] += (risk - 5) * 5
    scores["🏛️ 考公务员"] -= (risk - 5) * 3
    scores["💼 直接就业"] += (risk - 5) * 1
    scores["🎓 考研深造"] += (risk - 5) * 1

    # 家庭经济
    family = info.get("family", "")
    if "紧张" in family:
        scores["💼 直接就业"] += 12
        scores["🚀 自主创业"] -= 8
        scores["🎓 考研深造"] -= 5
    elif "宽松" in family:
        scores["🚀 自主创业"] += 10
        scores["🎓 考研深造"] += 8
        scores["🏛️ 考公务员"] -= 5

    # 经历
    exp = info.get("experience", "")
    if "有" in exp and "相关" in exp:
        scores["💼 直接就业"] += 12
        scores["🚀 自主创业"] += 10
    elif "有" in exp:
        scores["💼 直接就业"] += 5
        scores["🚀 自主创业"] += 3
    elif "没有" in exp or "还没" in exp:
        scores["🎓 考研深造"] += 8
        scores["🏛️ 考公务员"] += 5

    # 年级
    year = info.get("grade_year", "")
    if year in ("大四", "研三", "已毕业"):
        scores["💼 直接就业"] += 8
        scores["🏛️ 考公务员"] += 5
    elif year in ("大一", "大二"):
        scores["🎓 考研深造"] += 5
        scores["🚀 自主创业"] += 5

    # 学校水平
    school = info.get("school_level", "")
    if school in ("985/211/双一流"):
        scores["🎓 考研深造"] += 10
        scores["💼 直接就业"] += 8
        scores["🚀 自主创业"] += 3
    elif school in ("一本"):
        scores["🎓 考研深造"] += 6
        scores["💼 直接就业"] += 5
    elif school in ("二本", "专科/高职"):
        scores["🏛️ 考公务员"] += 8
        scores["💼 直接就业"] += 2
        scores["🚀 自主创业"] += 5

    # 所在城市
    city = info.get("city", "")
    tier1 = ["北京", "上海", "深圳", "广州", "杭州", "成都", "武汉", "南京", "苏州", "重庆"]
    if any(c in city for c in tier1):
        scores["💼 直接就业"] += 6
        scores["🚀 自主创业"] += 4
    elif city.strip():
        scores["💼 直接就业"] += 2
        scores["🏛️ 考公务员"] += 4

    # AI/创业兴趣加成
    interest = info.get("interest", "")
    if any(k in interest for k in ["AI", "人工智能", "创业", "产品", "商业", "独立开发"]):
        scores["🚀 自主创业"] += 5
        scores["💼 直接就业"] += 3

    # 技术类专业加成
    major = info.get("major", "")
    tech_keywords = ["计算机", "软件", "人工智能", "数据", "电子", "通信", "信息", "自动化", "工科"]
    if any(k in major for k in tech_keywords):
        scores["💼 直接就业"] += 5
        scores["🚀 自主创业"] += 8

    # 归一化到 5-100
    for k in scores:
        scores[k] = max(5, min(100, int(scores[k])))

    return scores


def career_advisor():
    # ===== 1. 初始化会话状态 =====
    if "ca_phase" not in st.session_state:
        st.session_state.ca_phase = "welcome"    # welcome | questions | result | chat
    if "ca_qidx" not in st.session_state:
        st.session_state.ca_qidx = 0
    if "ca_info" not in st.session_state:
        st.session_state.ca_info = {}
    if "ca_scores" not in st.session_state:
        st.session_state.ca_scores = None
    if "ca_result" not in st.session_state:
        st.session_state.ca_result = None
    if "ca_done" not in st.session_state:
        st.session_state.ca_done = False
    if "ca_chat" not in st.session_state:
        st.session_state.ca_chat = []

    # ===== 2. 问卷配置 =====
    QUESTIONS = [
        ("🎓", "你的专业是什么？", "major", "text", {"placeholder": "例如：计算机科学与技术"}),
        ("📚", "你现在读几年级？", "grade_year", "select", {"options": ["大一", "大二", "大三", "大四", "研一", "研二", "研三", "已毕业"]}),
        ("📈", "你的成绩排名大概在？", "grade", "select", {"options": ["前5%", "前10%", "前20%", "前30%", "前50%", "其他"]}),
        ("🏫", "你的学校属于什么水平？", "school_level", "select", {"options": ["985/211/双一流", "一本", "二本", "专科/高职", "海外高校", "其他"]}),
        ("📍", "你现在所在的城市是？", "city", "text", {"placeholder": "例如：广州、成都、武汉…"}),
        ("💡", "你对什么方向感兴趣？<br><span style='font-size:13px;color:var(--text-muted);'>AI、开发、产品、设计、数据分析、金融、教育…</span>", "interest", "textarea", {"placeholder": "描述你的兴趣方向，可以写多个"}),
        ("🎯", "现阶段你最看重什么？", "focus", "radio", {"options": ["💰 赚钱", "🛡 稳定", "📈 发展", "🚀 成就感", "🤔 不确定"]}),
        ("🏠", "你的家庭经济状况怎么样？", "family", "radio", {"options": ["比较宽松，支持我慢慢来", "一般，能供我读完书", "比较紧张，希望早点经济独立", "不方便说"]}),
        ("📝", "你有过项目、实习或创业经历吗？", "experience", "radio", {"options": ["有，且和兴趣相关", "有，但不太相关", "还没有", "正在找"]}),
        ("🎲", "你觉得自己能承受多大的风险？<br><span style='font-size:13px;color:var(--text-muted);'>1 = 一点风险都不想冒　10 = 为了梦想可以 all in</span>", "risk", "slider", {"min": 1, "max": 10, "value": 5}),
    ]

    # ===== 3. 阶段路由 =====
    phase = st.session_state.ca_phase

    # ---------- 3a. 欢迎阶段 ----------
    if phase == "welcome":
        section_banner("📊", "考研 / 就业 / 考公 / 创业 决策分析", "AI 量化评估最适合你的发展方向")

        st.markdown("""
        <div class="glass-card anim-1" style="text-align:center; padding:28px 24px;">
            <div style="font-size:40px; margin-bottom:12px;">👋</div>
            <h3 style="color:var(--text); margin-bottom:10px;">先了解你，才能给好建议</h3>
            <p style="color:var(--text-secondary); font-size:14px; max-width:500px; margin:0 auto 16px auto;">
            我会问你 <strong style="color:var(--accent);">10 个简单问题</strong>，然后从
            <strong style="color:var(--accent);">就业 · 考研 · 考公 · 创业</strong>
            四条路径为你做全面分析。整个过程只需 <strong>3 分钟</strong>。
            </p>
        </div>
        """, unsafe_allow_html=True)

        _, col, _ = st.columns([1, 2, 1])
        with col:
            if st.button("🚀 开始填写", use_container_width=True):
                st.session_state.ca_phase = "questions"
                st.session_state.ca_qidx = 0
                st.rerun()

    # ---------- 3b. 问卷阶段 ----------
    elif phase == "questions":
        section_banner("📊", "考研 / 就业 / 考公 / 创业 决策分析", "一步步了解你的情况")

        total_q = len(QUESTIONS)
        current = st.session_state.ca_qidx

        # 进度条
        st.progress(current / total_q, text=f"第 {current+1} / {total_q} 题")

        q_emoji, q_text, q_key, q_type, q_opts = QUESTIONS[current]

        st.markdown(f"""
        <div class="glass-card" style="padding:24px 24px 16px; margin-top:8px;">
            <div style="font-size:36px; text-align:center; margin-bottom:8px;">{q_emoji}</div>
            <h3 style="text-align:center; color:var(--text); margin:0 0 16px 0; line-height:1.4; font-size:17px;">{q_text}</h3>
        """, unsafe_allow_html=True)

        saved_value = st.session_state.ca_info.get(q_key, None)
        answer = None

        if q_type == "text":
            answer = st.text_input("", placeholder=q_opts.get("placeholder", ""),
                                   value=saved_value or "", key=f"ca_q_{q_key}")
        elif q_type == "select":
            opts = q_opts["options"]
            idx = opts.index(saved_value) if saved_value in opts else 0
            answer = st.selectbox("", opts, index=idx, key=f"ca_q_{q_key}")
        elif q_type == "textarea":
            answer = st.text_area("", placeholder=q_opts.get("placeholder", ""),
                                  value=saved_value or "", height=100, key=f"ca_q_{q_key}")
        elif q_type == "radio":
            opts = q_opts["options"]
            display_map = {opt: opt.split(" ")[-1] if " " in opt else opt for opt in opts}
            default_idx = 0
            for i, opt in enumerate(opts):
                if display_map[opt] == saved_value:
                    default_idx = i
                    break
            selected = st.radio("", opts, index=default_idx,
                                horizontal=len(opts) <= 4, key=f"ca_q_{q_key}")
            answer = display_map[selected]
        elif q_type == "slider":
            answer = st.select_slider(
                "",
                options=list(range(q_opts.get("min", 1), q_opts.get("max", 10) + 1)),
                value=saved_value if saved_value is not None else q_opts.get("value", 5),
                key=f"ca_q_{q_key}"
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # 导航按钮
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            if current > 0:
                if st.button("← 上一步", use_container_width=True):
                    st.session_state.ca_qidx -= 1
                    st.rerun()
        with col3:
            has_ans = answer is not None and str(answer).strip() != ""
            btn_text = "🎯 开始分析" if current == total_q - 1 else "下一步 →"
            if st.button(btn_text, use_container_width=True, disabled=not has_ans):
                if has_ans:
                    st.session_state.ca_info[q_key] = answer
                    if current < total_q - 1:
                        st.session_state.ca_qidx += 1
                        st.rerun()
                    else:
                        # 最后一步 → 进入结果页
                        st.session_state.ca_phase = "result"
                        st.session_state.ca_done = False
                        st.rerun()

    # ---------- 3c. 结果阶段 ----------
    elif phase == "result":
        section_banner("📊", "你的专属路径分析", "基于你的情况，AI 从四条路径综合评估")

        # 计算评分
        if st.session_state.ca_scores is None:
            st.session_state.ca_scores = _score_career_paths(st.session_state.ca_info)
        scores = st.session_state.ca_scores
        sorted_paths = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # ---- 评分卡片 ----
        st.markdown('<h4 style="color:var(--text); margin-bottom:16px;">📊 路径匹配度评分</h4>', unsafe_allow_html=True)
        path_colors = {"💼 直接就业": "#10b981", "🎓 考研深造": "#d0b2ff",
                       "🏛️ 考公务员": "#f59e0b", "🚀 自主创业": "#ef4444"}
        cols = st.columns(4)
        for i, (path, score) in enumerate(sorted_paths):
            color = path_colors.get(path, "#888")
            emoji = path.split(" ")[0]
            label = path.split(" ", 1)[1] if " " in path else path
            with cols[i]:
                st.markdown(f"""
                <div class="glass-card" style="text-align:center; padding:20px 8px;">
                    <div style="font-size:32px; margin-bottom:2px;">{emoji}</div>
                    <div style="font-size:13px; color:var(--text-secondary); margin-bottom:10px;">{label}</div>
                    <div style="font-size:40px; font-weight:900; color:{color};">{score}</div>
                    <div style="font-size:11px; color:var(--text-muted);">/ 100</div>
                </div>
                """, unsafe_allow_html=True)

        # ---- 进度条对比 ----
        st.markdown("<br>", unsafe_allow_html=True)
        for path, score in sorted_paths:
            color = "#10b981" if score >= 70 else "#d0b2ff" if score >= 50 else "#f59e0b" if score >= 30 else "#ef4444"
            st.markdown(f"""
            <div style="margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; font-size:14px; margin-bottom:3px;">
                    <span style="color:var(--text);">{path}</span>
                    <span style="color:{color}; font-weight:700;">{score}/100</span>
                </div>
                <div style="background:#1a1a20; border-radius:8px; height:10px; overflow:hidden;">
                    <div style="background:{color}; width:{score}%; height:100%; border-radius:8px; transition:width 0.8s ease;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---", unsafe_allow_html=True)

        # ---- AI 分析（流式输出） ----
        if not st.session_state.ca_done:
            params = {
                "major": st.session_state.ca_info.get("major", ""),
                "年级": st.session_state.ca_info.get("grade_year", ""),
                "成绩排名": st.session_state.ca_info.get("grade", ""),
                "学校水平": st.session_state.ca_info.get("school_level", ""),
                "所在城市": st.session_state.ca_info.get("city", ""),
                "兴趣方向": st.session_state.ca_info.get("interest", ""),
                "核心诉求": st.session_state.ca_info.get("focus", ""),
                "家庭经济": st.session_state.ca_info.get("family", ""),
                "项目经历": st.session_state.ca_info.get("experience", ""),
                "风险承受": f"{st.session_state.ca_info.get('risk', '5')}/10",
            }
            with st.chat_message("assistant", avatar="🎓"):
                stream = executor.stream_execute("career", params)
                if stream:
                    result = st.write_stream(stream)
                    st.session_state.ca_result = result
                    st.session_state.ca_done = True
                    st.rerun()
        else:
            # 显示缓存结果
            if st.session_state.ca_result:
                with st.chat_message("assistant", avatar="🎓"):
                    st.markdown(st.session_state.ca_result)

            # 操作按钮
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("🔄 重新分析", use_container_width=True):
                    for k in ["ca_phase", "ca_qidx", "ca_info", "ca_scores", "ca_result", "ca_done", "ca_chat"]:
                        st.session_state.pop(k, None)
                    st.rerun()
            with col2:
                if st.button("💬 继续追问", use_container_width=True, type="primary"):
                    st.session_state.ca_phase = "chat"
                    st.rerun()

    # ---------- 3d. 追问阶段 ----------
    elif phase == "chat":
        section_banner("💬", "继续追问", "对分析有疑问？或者想补充更多信息？")

        # 快捷提问
        quick_qs = [
            "我家经济压力大，这个建议需要调整吗？",
            "能具体说说创业适合做什么吗？",
            "我现在应该先准备什么？",
            "我这个专业好就业吗？",
            "考研的话要选什么方向？"
        ]
        st.markdown('<p style="font-size:13px; color:var(--text-muted); text-align:center; margin-bottom:8px;">💡 快捷提问</p>', unsafe_allow_html=True)
        qcols = st.columns(3)
        for i, q in enumerate(quick_qs):
            with qcols[i % 3]:
                if st.button(q, use_container_width=True, key=f"ca_qbtn_{i}"):
                    st.session_state.ca_chat.append({"role": "user", "content": q})
                    st.rerun()

        st.markdown("---")

        # 显示聊天历史
        for msg in st.session_state.ca_chat:
            with st.chat_message(msg["role"], avatar="🎓" if msg["role"] == "assistant" else None):
                st.markdown(msg["content"])

        # 如果有新的用户消息未回复，调用 AI
        if st.session_state.ca_chat and st.session_state.ca_chat[-1]["role"] == "user":
            last_q = st.session_state.ca_chat[-1]["content"]
            params = {
                "previous_analysis": st.session_state.ca_result or "",
                "user_question": last_q,
            }
            # 加入原始信息作为上下文
            for k, v in st.session_state.ca_info.items():
                params[k] = v

            with st.chat_message("assistant", avatar="🎓"):
                stream = executor.stream_execute("career_followup", params)
                if stream:
                    response = st.write_stream(stream)
                    st.session_state.ca_chat.append({"role": "assistant", "content": response})
                    st.rerun()

        # 聊天输入框
        question = st.chat_input("输入你的追问或补充信息...", key="ca_chat_input")
        if question:
            st.session_state.ca_chat.append({"role": "user", "content": question})
            st.rerun()

        # 返回
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← 返回分析结果", use_container_width=True):
            st.session_state.ca_phase = "result"
            st.rerun()


# ===================== 简历诊断 =====================
def resume_doctor():
    section_banner("📝", "简历智能诊断", "AI 从格式、内容、关键词、排版四维度评分并给出建议")
    step_indicator(["上传/粘贴简历", "AI 诊断", "获取评分"])

    # 初始化 session state 存储解析后的文本
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""
    if "resume_filename" not in st.session_state:
        st.session_state.resume_filename = None

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    # 文件上传区
    uploaded = st.file_uploader(
        "📂 导入简历文件（Word / PDF）",
        type=["docx", "pdf"],
        key="resume_uploader",
        help="支持 .docx / .pdf 格式，上传后自动解析"
    )

    if uploaded is not None:
        # 检查是否是新文件
        if st.session_state.resume_filename != uploaded.name:
            try:
                with st.spinner("📄 解析文件中..."):
                    parsed = parse_resume_file(uploaded)
                st.session_state.resume_text = parsed
                st.session_state.resume_filename = uploaded.name
                st.toast(f"✅ 已解析「{uploaded.name}」（{len(parsed)} 字符）", icon="📄")
            except Exception as e:
                st.error(f"❌ 解析失败：{str(e)}")

    st.markdown("""
    <div style="font-size:13px; color:var(--text-muted); margin: 12px 0 6px 0;">
        📝 简历内容（可手动编辑）
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([3, 1])
    with c1:
        resume = st.text_area(
            "简历内容",
            value=st.session_state.resume_text,
            height=340,
            placeholder="将完整简历粘贴到这里，或上传 Word/PDF 文件自动解析...\n\n建议包含：个人信息 · 教育背景 · 实习经历 · 项目经验 · 技能证书 · 自我评价",
            key="resume_input",
            label_visibility="collapsed"
        )
        # 同步编辑后的文本回 session
        st.session_state.resume_text = resume
    with c2:
        st.markdown("""
        <div style="background:rgba(245,158,11,0.05); border:1px solid rgba(245,158,11,0.15); border-radius:14px; padding:20px 14px; height:340px; display:flex; flex-direction:column; justify-content:center;">
            <div style="font-size:28px; text-align:center; margin-bottom:12px;">🔍</div>
            <h4 style="text-align:center; color:#f59e0b; margin-bottom:16px;">AI 诊断维度</h4>
            <div style="font-size:12px; color:var(--text-secondary); line-height:2.4;">
                <div>📐 格式规范性</div><div>🎯 关键词覆盖度</div>
                <div>📝 经历描述质量</div><div>👁 排版视觉效果</div>
                <div>💡 针对性优化建议</div>
                <div style="margin-top:8px; font-weight:600; color:#f59e0b;">⭐ 综合评分</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    _, cc, _ = st.columns([1,2,1])
    with cc:
        if st.button("🔍 开始诊断", use_container_width=True):
            if not resume:
                st.warning("⚠️ 请粘贴简历或上传文件")
            else:
                re, _ = get_rag_engines()
                rag_r = re.search(resume, top_k=2)
                rag_ctx = "\n\n参考简历写法：\n" + "\n".join([f"- {r['text']}" for r in rag_r]) if rag_r else ""
                stream = executor.stream_execute("resume", {"resume": resume + rag_ctx})
                if stream:
                    with st.chat_message("assistant", avatar="🤖"):
                        st.write_stream(stream)

    # 简历模板资源链接
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <a href="https://github.com/H-Canopy/resume-template" target="_blank" style="text-decoration:none;">
    <div style="background:rgba(208,178,255,0.06); border:1px solid rgba(208,178,255,0.18);
        border-radius:16px; padding:20px; text-align:center;
        transition: all 0.3s ease; cursor:pointer;">
        <div style="font-size:32px; margin-bottom:8px;">📋</div>
        <div style="font-size:16px; font-weight:700; color:var(--accent); margin-bottom:4px;">
            需要一份优质简历模板？
        </div>
        <div style="font-size:13px; color:var(--text-secondary);">
            GitHub 开源模板 → 直接下载使用 · Word 格式 · 排版精美
        </div>
    </div>
    </a>
    """, unsafe_allow_html=True)


# ===================== 岗位推荐 =====================
def job_recommender():
    section_banner("💼", "岗位智能推荐", "基于技能画像和城市偏好，AI 精准匹配岗位方向")
    step_indicator(["输入画像", "智能匹配", "岗位推荐"])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="glass-card"><div style="font-size:28px;">🛠</div><h4 style="color:var(--text);">技能标签</h4><p style="font-size:12px;color:var(--text-muted);">逗号分隔</p>', unsafe_allow_html=True)
        skills = st.text_input("技能", placeholder="Python, SQL, 数据分析...", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="glass-card"><div style="font-size:28px;">📍</div><h4 style="color:var(--text);">目标城市</h4><p style="font-size:12px;color:var(--text-muted);">期望就业城市</p>', unsafe_allow_html=True)
        city = st.text_input("城市", placeholder="北京 / 上海 / 不限...", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="glass-card"><div style="font-size:28px;">💰</div><h4 style="color:var(--text);">薪资期望</h4><p style="font-size:12px;color:var(--text-muted);">拖动选择</p>', unsafe_allow_html=True)
        salary = st.select_slider("薪资", options=["3k以下","3k-5k","5k-8k","8k-12k","12k-18k","18k-25k","25k以上"], label_visibility="collapsed")
        st.markdown(f'<div style="text-align:center;font-size:20px;font-weight:700;color:#10b981;margin-top:8px;">{salary}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    _, cc, _ = st.columns([1,2,1])
    with cc:
        if st.button("🎯 智能推荐", use_container_width=True):
            if not skills or not city:
                st.warning("⚠️ 请填写技能和城市")
            else:
                _, je = get_rag_engines()
                rag_r = je.search(f"{skills} {city} {salary}", top_k=3)
                rag_ctx = "\n\n相关岗位参考：\n" + "\n".join([f"- {r['text']}" for r in rag_r]) if rag_r else ""
                stream = executor.stream_execute("job", {"skills": skills, "city": city, "salary": salary, "rag_context": rag_ctx})
                if stream:
                    with st.chat_message("assistant", avatar="🤖"):
                        st.write_stream(stream)


# ===================== 智能体协同 =====================
def agent_collab_mode():
    section_banner("🤖", "智能体协同模式", "Planner Agent 自动分析 → 拆解任务 → Executor Agent 执行")

    st.markdown("""
    <div style="display:flex; align-items:center; justify-content:center; gap:0; padding:20px; margin-bottom:28px;" class="glass-card">
        <div style="text-align:center; padding:12px 20px;">
            <div style="width:56px;height:56px;border-radius:16px;background:radial-gradient(circle at 30% 30%, #A78BFA, #6366F1);display:flex;align-items:center;justify-content:center;font-size:24px;margin:0 auto 8px;">🧠</div>
            <div style="font-weight:700;color:var(--text);font-size:14px;">Planner</div>
            <div style="font-size:11px;color:var(--text-muted);">意图识别 · 任务分解</div>
        </div>
        <div style="font-size:20px; color:var(--text); padding:0 8px;">→</div>
        <div style="text-align:center; padding:12px 20px;">
            <div style="width:56px;height:56px;border-radius:16px;background:radial-gradient(circle at 30% 30%, #FB923C, #F97316);display:flex;align-items:center;justify-content:center;font-size:24px;margin:0 auto 8px;">⚡</div>
            <div style="font-weight:700;color:var(--text);font-size:14px;">路由</div>
            <div style="font-size:11px;color:var(--text-muted);">career · resume · job</div>
        </div>
        <div style="font-size:20px; color:var(--text); padding:0 8px;">→</div>
        <div style="text-align:center; padding:12px 20px;">
            <div style="width:56px;height:56px;border-radius:16px;background:radial-gradient(circle at 30% 30%, #34D399, #10B981);display:flex;align-items:center;justify-content:center;font-size:24px;margin:0 auto 8px;">🤖</div>
            <div style="font-weight:700;color:var(--text);font-size:14px;">Executor</div>
            <div style="font-size:11px;color:var(--text-muted);">工具调用 · 返回结果</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="glass-card"><div style="font-size:15px; font-weight:600; color:var(--accent); margin-bottom:12px;">💬 自然语言输入</div>', unsafe_allow_html=True)
    user_input = st.text_area("需求", height=120, placeholder="例如：我是计算机专业，成绩前5%，对AI感兴趣，有2段实习，不知道该就业还是考研...", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    _, cc, _ = st.columns([1,2,1])
    with cc:
        if st.button("🤖 启动 Agent", use_container_width=True):
            if not user_input:
                st.warning("⚠️ 请描述需求")
            else:
                with st.status("🧠 Planner 分析中...", expanded=True) as s:
                    st.write("🔍 识别意图...")
                    st.write("📋 拆解任务...")
                    plan = planner.analyze(user_input)
                    if plan and plan.get("task_type"):
                        s.update(label=f"✅ Planner 完成 → {plan['task_type']}（置信度 {plan.get('confidence',0):.0%}）", state="complete")
                    else:
                        s.update(label="⚠️ 意图不明确", state="complete")

                if plan:
                    with st.expander("📋 Planner 详情", expanded=False):
                        ca, cb = st.columns(2)
                        ca.metric("任务类型", plan.get('task_type', '?'))
                        cb.metric("置信度", f"{plan.get('confidence',0):.0%}")
                        st.json(plan)

                if plan and plan.get("task_type"):
                    with st.status("🤖 Executor 执行中...", expanded=True) as s:
                        st.write("⚙️ 调用处理器...")
                        st.write("📡 连接 RAG...")
                        stream = executor.stream_execute(plan["task_type"], plan.get("key_info", {}))
                        if stream:
                            s.update(label="✅ 开始生成...", state="complete")
                            with st.chat_message("assistant", avatar="🤖"):
                                st.write_stream(stream)
                        else:
                            s.update(label="❌ 执行失败", state="error")


# ===================== 个人信息分析 =====================
def persona_analyzer():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np

    section_banner("💡", "个人形象分析", "填写信息，生成你的能力雷达图与人格画像")

    # ----- 初始化 -----
    if "pa_result" not in st.session_state:
        st.session_state.pa_result = None

    # ===== 表单 =====
    with st.form("persona_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("姓名 / 昵称", placeholder="你的名字")
            gender = st.radio("性别", ["男", "女", "其他"], horizontal=True)
            age = st.selectbox("年龄段", ["18岁以下", "18-22", "23-26", "27-30", "30以上"])
        with col2:
            mbti = st.selectbox("MBTI 类型（选填）",
                ["不确定", "INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
                 "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"])
            edu = st.selectbox("学历", ["高中", "本科在读", "本科", "硕士在读", "硕士", "博士及以上"])

        st.markdown("---")
        traits = st.multiselect(
            "性格标签（选 3-6 个）",
            ["外向开朗", "沉稳内敛", "理性分析", "感性直觉", "执行力强", "创意无限",
             "善于沟通", "独立思考", "团队协作", "领导力", "耐心细致", "冒险精神",
             "完美主义", "随性自由", "共情力强", "逻辑严密"],
            default=["理性分析", "独立思考"]
        )

        col3, col4 = st.columns(2)
        with col3:
            strengths = st.text_area("自我优势", placeholder="你擅长什么？", height=80)
        with col4:
            weaknesses = st.text_area("自我短板", placeholder="哪些方面需要提升？", height=80)

        goal = st.text_input("职业/人生目标", placeholder="你想成为什么样的人？")

        submitted = st.form_submit_button("🔍 生成形象分析", use_container_width=True)

    # ===== 生成结果 =====
    if submitted:
        if not name:
            st.warning("请至少填写姓名/昵称")
        else:
            # 构建 AI prompt
            trait_str = "、".join(traits) if traits else "未填写"
            prompt = f"""你是一位资深职业规划与人格分析专家。请根据以下个人信息，生成一份「个人形象分析报告」。

姓名：{name}
性别：{gender}
年龄段：{age}
学历：{edu}
MBTI：{mbti}
性格标签：{trait_str}
自我优势：{strengths or '未填写'}
自我短板：{weaknesses or '未填写'}
职业目标：{goal or '未填写'}

请用以下结构输出（纯文本，不要markdown）：
【人格画像】用一段话描绘这个人的性格特征和给人的印象。
【能力六维】分别评估以下6个维度（每项0-100分）并给一句话说明：
  学习能力：XX分 - 说明
  社交能力：XX分 - 说明
  创造力：XX分 - 说明
  执行力：XX分 - 说明
  抗压能力：XX分 - 说明
  领导潜力：XX分 - 说明
【适合方向】推荐3个适合的职业方向，每个一句话。
【发展建议】给3条具体的发展建议。
"""
            with st.spinner("🤖 AI 分析中..."):
                try:
                    result = call_llm_with_system("你是专业的职业规划与人格分析专家，回复精炼专业。", prompt)
                    st.session_state.pa_result = result
                except Exception as e:
                    st.session_state.pa_result = f"ERROR: {e}"

    # ===== 展示结果 =====
    if st.session_state.pa_result:
        raw = st.session_state.pa_result
        if raw.startswith("ERROR:"):
            st.error(raw)
            return

        # 提取六维分数
        import re
        dims = ["学习能力", "社交能力", "创造力", "执行力", "抗压能力", "领导潜力"]
        scores = {}
        for dim in dims:
            m = re.search(rf'{dim}[：:]\s*(\d+)', raw)
            scores[dim] = int(m.group(1)) if m else 50

        # 切分段落
        sections = re.split(r'【(.+?)】', raw)
        section_map = {}
        for i in range(1, len(sections), 2):
            key = sections[i].strip()
            val = sections[i+1].strip() if i+1 < len(sections) else ""
            section_map[key] = val

        # ---- 雷达图 ----
        labels = list(dims)
        values = [scores[d] for d in dims]
        values.append(values[0])  # 闭合

        angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(4.5, 4.5), subplot_kw=dict(polar=True))
        fig.patch.set_facecolor('#0B0B12')
        ax.set_facecolor('#0B0B12')

        ax.fill(angles, values, color='#818CF8', alpha=0.2)
        ax.plot(angles, values, color='#A5B4FC', linewidth=2.5)
        ax.scatter(angles[:-1], values[:-1], color='#C4B5FD', s=50, zorder=3)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, color='#C5CBD8', fontsize=10, fontfamily='sans-serif')
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], color='#666', fontsize=7)
        ax.spines['polar'].set_color('#2A2A3A')
        ax.grid(color='#2A2A3A', linewidth=0.5)
        ax.set_title(f'{name} · 能力六维', color='#EDEDF0', fontsize=14, fontweight='bold', pad=18)

        st.pyplot(fig, use_container_width=False)
        plt.close(fig)

        # ---- 人格画像 ----
        if "人格画像" in section_map:
            st.markdown("### 🎭 人格画像")
            st.markdown(f'<div class="glass-card" style="padding:20px 24px;"><p style="color:var(--text); line-height:1.8;">{section_map["人格画像"]}</p></div>', unsafe_allow_html=True)

        # ---- 六维详情 ----
        if "能力六维" in section_map:
            st.markdown("### 📊 六维详情")
            cols = st.columns(3)
            for i, dim in enumerate(dims):
                s = scores[dim]
                bar_color = "#4ade80" if s >= 75 else "#fbbf24" if s >= 50 else "#f87171"
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="glass-card" style="padding:14px; text-align:center; margin-bottom:10px;">
                        <p style="font-size:28px; font-weight:700; color:{bar_color}; margin:0;">{s}</p>
                        <p style="font-size:13px; color:var(--text); margin:4px 0;">{dim}</p>
                    </div>
                    """, unsafe_allow_html=True)

        # ---- 适合方向 ----
        if "适合方向" in section_map:
            st.markdown("### 🎯 适合方向")
            st.markdown(f'<div class="glass-card" style="padding:20px 24px;"><p style="color:var(--text); line-height:1.8; white-space:pre-line;">{section_map["适合方向"]}</p></div>', unsafe_allow_html=True)

        # ---- 发展建议 ----
        if "发展建议" in section_map:
            st.markdown("### 💡 发展建议")
            st.markdown(f'<div class="glass-card" style="padding:20px 24px;"><p style="color:var(--text); line-height:1.8; white-space:pre-line;">{section_map["发展建议"]}</p></div>', unsafe_allow_html=True)


# ===================== 隐私协议 =====================
def privacy_policy():
    section_banner("📜", "隐私协议与服务条款", "我们重视你的数据安全与隐私权利")

    st.markdown("""
    <div class="glass-card" style="padding:28px 32px;">

    <h3 style="margin-top:0;">🔒 隐私保护声明</h3>
    <p style="color:var(--text); line-height:1.8;">
    本平台（大学生AI职业规划平台）高度重视用户隐私。我们承诺：
    </p>
    <ul style="color:var(--text); line-height:2.0;">
    <li><strong>不存储个人信息</strong> — 你在决策辅助、简历诊断、形象分析中填写的信息仅用于本次AI分析，分析完成后不落盘、不保留。</li>
    <li><strong>不上传简历文件</strong> — 简历诊断中上传的 Word/PDF 文件仅在内存中解析文本，解析后立即丢弃，文件本身不会被存储或传输至第三方。</li>
    <li><strong>API 调用加密</strong> — 所有与 DeepSeek API 的通信均通过 HTTPS 加密传输，API 密钥存储于服务端安全环境变量中。</li>
    </ul>

    <h3>📋 信息收集说明</h3>
    <p style="color:var(--text); line-height:1.8;">
    本平台<strong>不收集</strong>以下信息：
    </p>
    <ul style="color:var(--text); line-height:2.0;">
    <li>真实姓名、身份证号、手机号等个人身份信息</li>
    <li>浏览器 Cookie、浏览记录、设备指纹</li>
    <li>地理位置（除你在问卷中主动填写的城市外）</li>
    </ul>
    <p style="color:var(--text); line-height:1.8;">
    平台仅在 Streamlit Cloud 框架层面记录基本的访问日志（IP、访问时间），用于服务监控，不会与你的个人数据关联。
    </p>

    <h3>⚖️ 服务条款</h3>
    <ol style="color:var(--text); line-height:2.0;">
    <li><strong>仅供参考</strong> — 本平台提供的AI分析结果仅作为职业规划的参考建议，不构成专业的职业咨询或法律建议。重大职业决策请结合实际情况并咨询专业人士。</li>
    <li><strong>合理使用</strong> — 请勿利用本平台进行任何违法、违规或滥用行为，包括但不限于批量自动化请求、注入恶意提示词等。</li>
    <li><strong>内容责任</strong> — 用户自行对输入的内容负责。AI生成的输出内容可能存在误差，平台不对输出的准确性、完整性做任何保证。</li>
    <li><strong>服务可用性</strong> — 本平台基于 Streamlit Cloud 免费托管，不保证7×24小时可用。如遇服务中断，敬请谅解。</li>
    <li><strong>条款变更</strong> — 我们保留随时更新本协议的权利，更新后的条款将在本页面公示。</li>
    </ol>

    <h3>📧 联系方式</h3>
    <p style="color:var(--text); line-height:1.8;">
    如对本隐私协议有任何疑问或建议，请通过 GitHub Issues 联系我们：
    <a href="https://github.com/H-Canopy/career-ai-platform/issues" target="_blank" style="color:var(--accent);">github.com/H-Canopy/career-ai-platform/issues</a>
    </p>

    <p style="color:var(--text-muted); font-size:12px; margin-top:24px; text-align:center;">
    最后更新：2026年5月29日
    </p>

    </div>
    """, unsafe_allow_html=True)

# ===================== 路由 =====================
page = st.session_state.current_page
if page == "🏠 首页总览":
    show_home()
elif page == "📊 决策辅助":
    career_advisor()
elif page == "📝 简历诊断":
    resume_doctor()
elif page == "💼 岗位推荐":
    job_recommender()
elif page == "🤖 智能体协同":
    agent_collab_mode()
elif page == "💡 形象分析":
    persona_analyzer()
elif page == "📜 隐私协议":
    privacy_policy()

st.markdown("""
<div class="footer">
    <p>大学生AI职业规划平台 | MiniMax · Streamlit · RAG | Agent: Planner + Executor</p>
</div>
""", unsafe_allow_html=True)
