# -*- coding: utf-8 -*-
"""
晓牧传媒文案助手 v8.0
基于UI Design Skill重构 - 专业深色主题
"""
import streamlit as st
import re
from openai import OpenAI

st.set_page_config(
    page_title="晓牧传媒文案助手",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 设计系统 CSS ==========
st.markdown("""
<style>
    /* ===== 色彩系统 ===== */
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --primary-light: #818cf8;
        --success: #22c55e;
        --warning: #f59e0b;
        --error: #ef4444;
        --bg-dark: #0f0f1a;
        --bg-card: #1a1a2e;
        --bg-hover: rgba(255,255,255,0.05);
        --text-primary: #ffffff;
        --text-secondary: rgba(255,255,255,0.7);
        --text-muted: rgba(255,255,255,0.4);
        --border: rgba(255,255,255,0.05);
    }
    
    /* ===== 全局样式 ===== */
    .stApp {
        background: var(--bg-dark) !important;
    }
    
    .css-1d391kg {
        background: var(--bg-card) !important;
        border-right: 1px solid var(--border) !important;
    }
    
    #MainMenu, header, footer {
        display: none !important;
    }
    
    /* ===== 侧边栏 ===== */
    .sidebar-brand {
        padding: 24px;
        border-bottom: 1px solid var(--border);
    }
    
    .sidebar-brand h2 {
        color: var(--primary);
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .sidebar-brand p {
        color: var(--text-muted);
        font-size: 0.75rem;
        margin: 4px 0 0 0;
    }
    
    /* 导航菜单 */
    .nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 24px;
        margin: 4px 16px;
        border-radius: 8px;
        color: var(--text-secondary);
        font-size: 0.875rem;
        transition: all 0.2s;
        cursor: pointer;
    }
    
    .nav-item:hover {
        background: var(--bg-hover);
        color: var(--text-primary);
    }
    
    .nav-item.active {
        background: rgba(99, 102, 241, 0.15);
        color: var(--primary-light);
    }
    
    /* ===== 主内容区 ===== */
    .main-content {
        padding: 32px;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* 页面标题 */
    .page-header {
        margin-bottom: 32px;
    }
    
    .page-title {
        color: var(--text-primary);
        font-size: 1.75rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    
    .page-subtitle {
        color: var(--text-muted);
        font-size: 0.875rem;
    }
    
    /* ===== 卡片组件 ===== */
    .card {
        background: rgba(255,255,255,0.03);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
    }
    
    .card:hover {
        background: rgba(255,255,255,0.05);
        border-color: rgba(255,255,255,0.1);
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .card-title {
        color: var(--text-primary);
        font-size: 1.125rem;
        font-weight: 600;
    }
    
    /* ===== 统计卡片网格 ===== */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 24px;
        margin-bottom: 32px;
    }
    
    .stat-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        transition: all 0.3s;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        background: rgba(255,255,255,0.05);
    }
    
    .stat-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        margin-bottom: 16px;
    }
    
    .stat-icon.blue { background: rgba(99, 102, 241, 0.15); }
    .stat-icon.green { background: rgba(34, 197, 94, 0.15); }
    .stat-icon.orange { background: rgba(245, 158, 11, 0.15); }
    .stat-icon.red { background: rgba(239, 68, 68, 0.15); }
    
    .stat-value {
        color: var(--text-primary);
        font-size: 1.75rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    
    .stat-label {
        color: var(--text-muted);
        font-size: 0.875rem;
    }
    
    /* ===== 表单组件 ===== */
    .form-label {
        color: var(--text-secondary);
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 8px;
    }
    
    .stTextArea textarea {
        background: rgba(0,0,0,0.2) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        padding: 16px !important;
        font-size: 0.9375rem !important;
        line-height: 1.6 !important;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }
    
    /* 选择器 */
    .stSelectbox > div > div {
        background: rgba(0,0,0,0.2) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }
    
    /* 单选 */
    .stRadio > div {
        background: transparent !important;
        display: flex;
        gap: 16px;
    }
    
    /* ===== 按钮 ===== */
    .stButton>button[kind="primary"] {
        background: var(--primary) !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 14px 28px !important;
        font-weight: 600 !important;
        color: white !important;
        transition: all 0.2s !important;
        width: 100% !important;
    }
    
    .stButton>button[kind="primary"]:hover {
        background: var(--primary-dark) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    /* ===== 文案列表 ===== */
    .copy-list {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }
    
    .copy-item {
        background: rgba(255,255,255,0.03);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 20px;
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
        margin-bottom: 12px;
    }
    
    .copy-number {
        color: var(--primary);
        font-weight: 600;
        font-size: 0.875rem;
    }
    
    .copy-type {
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .type-1 { background: rgba(99, 102, 241, 0.15); color: #818cf8; }
    .type-2 { background: rgba(168, 85, 247, 0.15); color: #c084fc; }
    .type-3 { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
    .type-4 { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
    
    .copy-content {
        color: var(--text-secondary);
        line-height: 1.8;
        font-size: 0.9375rem;
        margin-bottom: 16px;
    }
    
    .copy-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .copy-meta {
        color: var(--text-muted);
        font-size: 0.75rem;
    }
    
    .copy-status {
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .status-ok { background: rgba(34, 197, 94, 0.15); color: var(--success); }
    .status-warn { background: rgba(245, 158, 11, 0.15); color: var(--warning); }
    .status-err { background: rgba(239, 68, 68, 0.15); color: var(--error); }
    
    /* ===== 空状态 ===== */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: var(--text-muted);
    }
    
    .empty-icon {
        font-size: 3rem;
        margin-bottom: 16px;
    }
    
    /* ===== 进度条 ===== */
    .stProgress > div > div {
        background: var(--primary) !important;
    }
    
    /* ===== 响应式 ===== */
    @media (max-width: 1200px) {
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 768px) {
        .stats-grid {
            grid-template-columns: 1fr;
        }
        .main-content {
            padding: 16px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ========== 配置 ==========
INDUSTRIES = ["餐饮", "木作定制", "工厂/制造", "彩票店", "酒店/民宿", "通用"]
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
                {"role": "system", "content": "你是短视频文案大师。黄金三秒：严禁自我介绍、店名、地址。语义降维：禁用匠心/高端/专业。"},
                {"role": "user", "content": f"创作第{idx}条{ctype}文案。称呼：{name} 资料：{raw_data[:400]} 要求:1.字数{min_w}-{max_w} 2.禁止自我介绍 3.包含1个具体数字"}
            ],
            max_tokens=400, temperature=0.85, timeout=30
        )
        content = resp.choices[0].message.content.strip().strip('"')
        wc = len(content.replace(' ', '').replace('\n', ''))
        ok = min_w <= wc <= max_w
        return {'idx': idx, 'content': content, 'wc': wc, 'ok': ok, 'type': ctype}
    except Exception as e:
        return {'idx': idx, 'content': f"失败:{str(e)[:30]}", 'wc': 0, 'ok': False, 'type': ctype}

# 安全初始化
if 'items' not in st.session_state or not isinstance(st.session_state.items, list):
    st.session_state.items = []

# ========== 侧边栏 ==========
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2>晓牧传媒</h2>
        <p>内容创作系统 · 内部专用</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="nav-item active">📊 生成文案</div>
    <div class="nav-item">🔍 违禁词扫描</div>
    <div class="nav-item">📄 Word导出</div>
    <div class="nav-item">📋 订单管理</div>
    """, unsafe_allow_html=True)

# ========== 主内容 ==========
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# 页面标题
st.markdown("""
<div class="page-header">
    <div class="page-title">生成文案</div>
    <div class="page-subtitle">输入客户资料，AI自动生成30条高质量短视频文案</div>
</div>
""", unsafe_allow_html=True)

# 输入卡片
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="card-header"><div class="card-title">配置参数</div></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="form-label">行业类型</div>', unsafe_allow_html=True)
    industry = st.selectbox("行业", INDUSTRIES, label_visibility="collapsed")
with col2:
    st.markdown('<div class="form-label">文案长度</div>', unsafe_allow_html=True)
    length = st.radio("长度", ["短文案(150-180)", "长文案(200-300)"], horizontal=True, label_visibility="collapsed")

st.markdown('<div style="margin: 16px 0;"></div>', unsafe_allow_html=True)
st.markdown('<div class="form-label">客户资料</div>', unsafe_allow_html=True)
raw = st.text_area("资料", height=120, placeholder="请输入客户资料：出镜称呼、店铺名称、主营业务、真实故事...", label_visibility="collapsed")

st.caption(f"已输入 {len(raw)} 字")

if st.button("🚀 一键生成30条文案", type="primary"):
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
    
    # 结果列表
    st.markdown('<div class="card">', unsafe_allow_html=True)
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
            <div class="copy-footer">
                <span class="copy-meta">{item['wc']} 字</span>
                <span class="copy-status {status_class}">{status_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
