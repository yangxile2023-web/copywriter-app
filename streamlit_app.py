# -*- coding: utf-8 -*-
import streamlit as st
import re
from openai import OpenAI

st.set_page_config(page_title="晓牧传媒文案助手", layout="wide")

# 现代深色主题CSS
st.markdown("""
<style>
    /* 全局深色背景 */
    .stApp {
        background: #0f0f1a !important;
    }
    
    /* 侧边栏 */
    .css-1d391kg {
        background: #1a1a2e !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }
    
    /* 隐藏默认元素 */
    #MainMenu, header, footer {
        display: none !important;
    }
    
    /* 侧边栏样式 */
    .sidebar-brand {
        padding: 1.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    
    .sidebar-brand h2 {
        color: #6366f1;
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0;
    }
    
    .sidebar-brand p {
        color: rgba(255,255,255,0.4);
        font-size: 0.75rem;
        margin: 0.25rem 0 0 0;
    }
    
    /* 导航菜单 */
    .nav-menu {
        padding: 1rem 0;
    }
    
    .nav-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.875rem 1.5rem;
        margin: 0.25rem 1rem;
        border-radius: 8px;
        color: rgba(255,255,255,0.6);
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .nav-item:hover {
        background: rgba(255,255,255,0.05);
        color: white;
    }
    
    .nav-item.active {
        background: rgba(99, 102, 241, 0.15);
        color: #6366f1;
    }
    
    /* 主内容区 */
    .main-content {
        padding: 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* 顶部栏 */
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }
    
    .page-title {
        color: white;
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    .user-menu {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    /* 统计卡片网格 */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .stat-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.3s;
    }
    
    .stat-card:hover {
        background: rgba(255,255,255,0.05);
        border-color: rgba(255,255,255,0.1);
    }
    
    .stat-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        margin-bottom: 1rem;
    }
    
    .stat-icon.blue { background: rgba(99, 102, 241, 0.15); }
    .stat-icon.green { background: rgba(34, 197, 94, 0.15); }
    .stat-icon.orange { background: rgba(251, 191, 36, 0.15); }
    .stat-icon.red { background: rgba(239, 68, 68, 0.15); }
    
    .stat-value {
        color: white;
        font-size: 1.75rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    
    .stat-label {
        color: rgba(255,255,255,0.4);
        font-size: 0.875rem;
    }
    
    /* 内容卡片 */
    .content-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .card-title {
        color: white;
        font-size: 1.125rem;
        font-weight: 600;
    }
    
    /* 输入框样式 */
    .stTextArea textarea {
        background: rgba(0,0,0,0.2) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        color: white !important;
        padding: 1rem !important;
        font-size: 0.9375rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }
    
    /* 选择器 */
    .stSelectbox > div > div, .stRadio > div {
        background: rgba(0,0,0,0.2) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    /* 按钮 */
    .stButton>button[kind="primary"] {
        background: #6366f1 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.875rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    
    .stButton>button[kind="primary"]:hover {
        background: #4f46e5 !important;
        transform: translateY(-1px);
    }
    
    /* 文案列表 */
    .copy-list {
        display: grid;
        gap: 1rem;
    }
    
    .copy-item {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 1.25rem;
        transition: all 0.2s;
    }
    
    .copy-item:hover {
        background: rgba(255,255,255,0.05);
        border-color: rgba(255,255,255,0.1);
    }
    
    .copy-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    
    .copy-number {
        color: #6366f1;
        font-weight: 600;
        font-size: 0.875rem;
    }
    
    .copy-type {
        padding: 0.25rem 0.625rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .type-1 { background: rgba(99, 102, 241, 0.15); color: #818cf8; }
    .type-2 { background: rgba(168, 85, 247, 0.15); color: #c084fc; }
    .type-3 { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }
    .type-4 { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
    
    .copy-content {
        color: rgba(255,255,255,0.85);
        line-height: 1.7;
        font-size: 0.9375rem;
        margin-bottom: 0.75rem;
    }
    
    .copy-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: rgba(255,255,255,0.4);
        font-size: 0.75rem;
    }
    
    .copy-status {
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-weight: 500;
    }
    
    .status-ok { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
    .status-warn { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }
    .status-err { background: rgba(239, 68, 68, 0.15); color: #f87171; }
    
    /* 空状态 */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: rgba(255,255,255,0.3);
    }
    
    /* 进度条 */
    .stProgress > div > div {
        background: #6366f1 !important;
    }
    
    /* 响应式 */
    @media (max-width: 1200px) {
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 768px) {
        .stats-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# 配置
INDUSTRIES = {"餐饮", "木作定制", "工厂/制造", "彩票店", "酒店/民宿", "通用"}
CONTENT_TYPES = ["干货避坑", "人设故事", "细节特写", "认知反转"]
KIMI_KEY = "sk-IA6qyNJFSYC8UB9RHnGHsgz24VWSrKalSnd5nTTbJNiqQ2uu"

@st.cache_resource
def get_client():
    return OpenAI(api_key=KIMI_KEY, base_url="https://api.moonshot.cn/v1")

def generate(raw_data, idx, length):
    name = re.search(r'出镜称呼[：:]\s*(\S+)', raw_data)
    name = name.group(1) if name else "老板"
    min_w, max_w = (150, 180) if length == "short" else (200, 300)
    ctype = CONTENT_TYPES[(idx - 1) % 4]
    
    try:
        client = get_client()
        resp = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是短视频文案大师。黄金三秒：严禁自我介绍、店名、地址。"},
                {"role": "user", "content": f"创作第{idx}条{ctype}文案。称呼：{name} 资料：{raw_data[:400]}"}
            ],
            max_tokens=400, temperature=0.85, timeout=30
        )
        content = resp.choices[0].message.content.strip().strip('"')
        wc = len(content.replace(' ', '').replace('\n', ''))
        ok = min_w <= wc <= max_w
        return {'idx': idx, 'content': content, 'wc': wc, 'ok': ok, 'type': ctype}
    except Exception as e:
        return {'idx': idx, 'content': f"失败:{str(e)[:30]}", 'wc': 0, 'ok': False, 'type': ctype}

# 初始化
if 'items' not in st.session_state or st.session_state.items is None:
    st.session_state.items = []
if not isinstance(st.session_state.items, list):
    st.session_state.items = []

# ========== 侧边栏 ==========
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2>晓牧传媒</h2>
        <p>内容创作系统 · 内部专用</p>
    </div>
    <div class="nav-menu">
        <div class="nav-item active">📊 数据概览</div>
        <div class="nav-item">✨ 生成文案</div>
        <div class="nav-item">🔍 违禁词扫描</div>
        <div class="nav-item">📄 Word导出</div>
        <div class="nav-item">📋 订单管理</div>
    </div>
    """, unsafe_allow_html=True)

# ========== 主内容 ==========
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# 顶部栏
st.markdown("""
<div class="top-bar">
    <div class="page-title">生成文案</div>
    <div class="user-menu">👤 Admin</div>
</div>
""", unsafe_allow_html=True)

# 输入区
st.markdown('<div class="content-card">', unsafe_allow_html=True)

st.markdown('<div class="card-header"><div class="card-title">配置参数</div></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    industry = st.selectbox("行业类型", list(INDUSTRIES), label_visibility="collapsed")
with col2:
    length = st.radio("文案长度", ["短文案(150-180)", "长文案(200-300)"], horizontal=True, label_visibility="collapsed")

st.markdown("**客户资料**")
raw = st.text_area("资料", height=120, placeholder="请输入客户资料...", label_visibility="collapsed")

if st.button("🚀 一键生成30条", type="primary", use_container_width=True):
    if len(raw) < 30:
        st.error("资料至少30字")
    else:
        with st.spinner("AI生成中..."):
            prog = st.progress(0)
            st.session_state.items = []
            for i in range(30):
                r = generate(raw, i+1, "short" if "短" in length else "long")
                st.session_state.items.append(r)
                prog.progress((i+1)/30)
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# 结果
if st.session_state.items and len(st.session_state.items) > 0:
    items = st.session_state.items
    total = len(items)
    ok = sum(1 for i in items if i['ok'])
    fail = sum(1 for i in items if i['wc'] == 0)
    warn = total - ok - fail
    
    # 统计卡片
    st.markdown(f"""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon blue">📊</div>
            <div class="stat-value">{total}</div>
            <div class="stat-label">总数</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon green">✓</div>
            <div class="stat-value">{ok}</div>
            <div class="stat-label">优质</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon orange">!</div>
            <div class="stat-value">{warn}</div>
            <div class="stat-label">需优化</div>
        </div>
        <div class="stat-card">
            <div class="stat-icon red">✗</div>
            <div class="stat-value">{fail}</div>
            <div class="stat-label">失败</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 文案列表
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header"><div class="card-title">生成结果</div></div>', unsafe_allow_html=True)
    
    for item in items:
        type_idx = (item['idx'] - 1) % 4
        type_class = f"type-{type_idx + 1}"
        status_class = "status-ok" if item['ok'] else "status-err" if item['wc'] == 0 else "status-warn"
        status_text = "优质" if item['ok'] else "失败" if item['wc'] == 0 else "需优化"
        
        st.markdown(f"""
        <div class="copy-item">
            <div class="copy-header">
                <span class="copy-number">#{item['idx']}</span>
                <span class="copy-type {type_class}">{item['type']}</span>
            </div>
            <div class="copy-content">{item['content']}</div>
            <div class="copy-meta">
                <span>{item['wc']} 字</span>
                <span class="copy-status {status_class}">{status_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
