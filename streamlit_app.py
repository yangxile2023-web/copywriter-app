# -*- coding: utf-8 -*-
"""
晓牧传媒文案助手 v9.0
Apple Design Style - 简洁、优雅、留白
"""
import streamlit as st
import re
from openai import OpenAI
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io

st.set_page_config(
    page_title="晓牧传媒文案助手",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apple Design CSS
st.markdown("""
<style>
    /* ===== Apple Design System ===== */
    :root {
        --apple-blue: #007AFF;
        --apple-blue-hover: #0056D6;
        --apple-bg: #F5F5F7;
        --apple-card: #FFFFFF;
        --apple-text: #1D1D1F;
        --apple-text-secondary: #6E6E73;
        --apple-border: rgba(0,0,0,0.08);
        --apple-green: #34C759;
        --apple-orange: #FF9500;
        --apple-red: #FF3B30;
        --apple-gray: #8E8E93;
    }
    
    /* ===== 全局样式 ===== */
    .stApp {
        background: var(--apple-bg) !important;
    }
    
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border-right: 1px solid var(--apple-border) !important;
    }
    
    #MainMenu, header, footer {
        display: none !important;
    }
    
    /* ===== 侧边栏 - 玻璃拟态 ===== */
    .sidebar-content {
        padding: 24px 16px;
    }
    
    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 0 12px 24px 12px;
        border-bottom: 1px solid var(--apple-border);
        margin-bottom: 16px;
    }
    
    .logo-icon {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #007AFF, #5856D6);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.25rem;
    }
    
    .logo-text h2 {
        color: var(--apple-text);
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .logo-text p {
        color: var(--apple-text-secondary);
        font-size: 0.75rem;
        margin: 2px 0 0 0;
    }
    
    /* 导航菜单 */
    .nav-menu {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    
    .nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        border-radius: 10px;
        color: var(--apple-text-secondary);
        font-size: 0.9375rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .nav-item:hover {
        background: rgba(0,0,0,0.04);
        color: var(--apple-text);
    }
    
    .nav-item.active {
        background: rgba(0, 122, 255, 0.1);
        color: var(--apple-blue);
    }
    
    /* ===== 主内容区 ===== */
    .main-content {
        padding: 40px 48px;
        max-width: 1000px;
        margin: 0 auto;
    }
    
    /* 页面标题 */
    .page-header {
        margin-bottom: 40px;
    }
    
    .page-title {
        color: var(--apple-text);
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 8px;
    }
    
    .page-subtitle {
        color: var(--apple-text-secondary);
        font-size: 1.125rem;
        font-weight: 400;
    }
    
    /* ===== Apple Card ===== */
    .apple-card {
        background: var(--apple-card);
        border-radius: 20px;
        padding: 32px;
        margin-bottom: 24px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.04);
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
    }
    
    .card-title {
        color: var(--apple-text);
        font-size: 1.25rem;
        font-weight: 600;
        letter-spacing: -0.01em;
    }
    
    /* ===== 统计卡片 - 玻璃拟态 ===== */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        margin-bottom: 40px;
    }
    
    .stat-box {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 24px;
        border: 1px solid rgba(255,255,255,0.5);
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .stat-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }
    
    .stat-icon {
        width: 48px;
        height: 48px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 16px;
    }
    
    .stat-icon.blue { background: linear-gradient(135deg, #007AFF, #5E5CE6); }
    .stat-icon.green { background: linear-gradient(135deg, #34C759, #30D158); }
    .stat-icon.orange { background: linear-gradient(135deg, #FF9500, #FFCC00); }
    .stat-icon.red { background: linear-gradient(135deg, #FF3B30, #FF6B6B); }
    
    .stat-value {
        color: var(--apple-text);
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 4px;
    }
    
    .stat-label {
        color: var(--apple-text-secondary);
        font-size: 0.9375rem;
        font-weight: 500;
    }
    
    /* ===== 表单组件 ===== */
    .form-group {
        margin-bottom: 24px;
    }
    
    .form-label {
        color: var(--apple-text);
        font-size: 0.9375rem;
        font-weight: 600;
        margin-bottom: 8px;
        display: block;
    }
    
    .form-hint {
        color: var(--apple-text-secondary);
        font-size: 0.8125rem;
        margin-top: 6px;
    }
    
    /* 文本域 - iOS风格 */
    .stTextArea textarea {
        background: #F5F5F7 !important;
        border: 1px solid transparent !important;
        border-radius: 12px !important;
        color: var(--apple-text) !important;
        padding: 16px !important;
        font-size: 1rem !important;
        line-height: 1.5 !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextArea textarea:focus {
        background: #FFFFFF !important;
        border-color: var(--apple-blue) !important;
        box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1) !important;
    }
    
    /* 选择器 - iOS风格 */
    .stSelectbox > div > div {
        background: #F5F5F7 !important;
        border: 1px solid transparent !important;
        border-radius: 10px !important;
        color: var(--apple-text) !important;
        padding: 4px !important;
    }
    
    .stSelectbox > div > div:hover {
        background: #FFFFFF !important;
        border-color: rgba(0,0,0,0.1) !important;
    }
    
    /* 单选 - iOS分段控制器风格 */
    .stRadio > div {
        background: #E5E5EA !important;
        border-radius: 10px !important;
        padding: 4px !important;
        display: flex !important;
        gap: 4px !important;
    }
    
    .stRadio label {
        color: var(--apple-text) !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        border-radius: 8px !important;
        margin: 0 !important;
        flex: 1 !important;
        text-align: center !important;
        transition: all 0.2s !important;
    }
    
    .stRadio label:hover {
        background: rgba(255,255,255,0.5) !important;
    }
    
    /* ===== Apple Button ===== */
    .stButton>button[kind="primary"] {
        background: var(--apple-blue) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 16px 32px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: white !important;
        letter-spacing: -0.01em !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3) !important;
    }
    
    .stButton>button[kind="primary"]:hover {
        background: var(--apple-blue-hover) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(0, 122, 255, 0.4) !important;
    }
    
    .stButton>button[kind="primary"]:active {
        transform: scale(0.98) !important;
    }
    
    /* ===== 文案列表 - Apple风格 ===== */
    .copy-list {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }
    
    .copy-item {
        background: var(--apple-card);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        border: 1px solid rgba(0,0,0,0.04);
        transition: all 0.3s ease;
    }
    
    .copy-item:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }
    
    .copy-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    
    .copy-number {
        color: var(--apple-blue);
        font-weight: 700;
        font-size: 0.9375rem;
    }
    
    .copy-type {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.8125rem;
        font-weight: 600;
    }
    
    .type-blue { background: rgba(0, 122, 255, 0.1); color: var(--apple-blue); }
    .type-purple { background: rgba(88, 86, 214, 0.1); color: #5856D6; }
    .type-orange { background: rgba(255, 149, 0, 0.1); color: var(--apple-orange); }
    .type-green { background: rgba(52, 199, 89, 0.1); color: var(--apple-green); }
    
    .copy-content {
        color: var(--apple-text);
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 16px;
    }
    
    .copy-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 16px;
        border-top: 1px solid var(--apple-border);
    }
    
    .copy-meta {
        color: var(--apple-text-secondary);
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .copy-status {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.8125rem;
        font-weight: 600;
    }
    
    .status-ok { background: rgba(52, 199, 89, 0.1); color: var(--apple-green); }
    .status-warn { background: rgba(255, 149, 0, 0.1); color: var(--apple-orange); }
    .status-err { background: rgba(255, 59, 48, 0.1); color: var(--apple-red); }
    
    /* ===== 空状态 ===== */
    .empty-state {
        text-align: center;
        padding: 80px 40px;
    }
    
    .empty-icon {
        width: 120px;
        height: 120px;
        background: linear-gradient(135deg, #F5F5F7, #E5E5EA);
        border-radius: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 24px auto;
        font-size: 3rem;
    }
    
    .empty-title {
        color: var(--apple-text);
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .empty-desc {
        color: var(--apple-text-secondary);
        font-size: 1rem;
    }
    
    /* ===== 响应式 ===== */
    @media (max-width: 1024px) {
        .stats-container {
            grid-template-columns: repeat(2, 1fr);
        }
        .main-content {
            padding: 24px;
        }
        .page-title {
            font-size: 2rem;
        }
    }
    
    @media (max-width: 768px) {
        .stats-container {
            grid-template-columns: 1fr;
        }
        .apple-card {
            padding: 24px;
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

# 安全初始化 - 防止 None
if 'items' not in st.session_state:
    st.session_state.items = []
elif st.session_state.items is None:
    st.session_state.items = []
elif not isinstance(st.session_state.items, list):
    st.session_state.items = []

# ========== 侧边栏 ==========
with st.sidebar:
    st.markdown("""
    <div class="sidebar-content">
        <div class="sidebar-logo">
            <div class="logo-icon">✨</div>
            <div class="logo-text">
                <h2>晓牧传媒</h2>
                <p>内容创作系统</p>
            </div>
        </div>
        <div class="nav-menu">
            <div class="nav-item active">✨ 生成文案</div>
            <div class="nav-item">🔍 违禁词扫描</div>
            <div class="nav-item">📄 Word导出</div>
            <div class="nav-item">📋 订单管理</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ========== 主内容 ==========
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# 标题
st.markdown("""
<div class="page-header">
    <h1 class="page-title">生成30条爆款文案</h1>
    <p class="page-subtitle">输入客户资料，AI自动生成高质量短视频文案</p>
</div>
""", unsafe_allow_html=True)

# 统计卡片（有数据时显示）
if isinstance(st.session_state.items, list) and len(st.session_state.items) > 0:
    items = st.session_state.items
    total = len(items)
    ok = sum(1 for i in items if i['ok'])
    fail = sum(1 for i in items if i['wc'] == 0)
    warn = total - ok - fail
    
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-box">
            <div class="stat-icon blue">📊</div>
            <div class="stat-value">{total}</div>
            <div class="stat-label">总数</div>
        </div>
        <div class="stat-box">
            <div class="stat-icon green">✓</div>
            <div class="stat-value">{ok}</div>
            <div class="stat-label">优质</div>
        </div>
        <div class="stat-box">
            <div class="stat-icon orange">!</div>
            <div class="stat-value">{warn}</div>
            <div class="stat-label">需优化</div>
        </div>
        <div class="stat-box">
            <div class="stat-icon red">✗</div>
            <div class="stat-value">{fail}</div>
            <div class="stat-label">失败</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 输入卡片
st.markdown('<div class="apple-card">', unsafe_allow_html=True)

st.markdown('<div class="card-header"><div class="card-title">配置参数</div></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<label class="form-label">行业类型</label>', unsafe_allow_html=True)
    industry = st.selectbox("行业", INDUSTRIES, label_visibility="collapsed")
with col2:
    st.markdown('<label class="form-label">文案长度</label>', unsafe_allow_html=True)
    length = st.radio("长度", ["短文案(150-180)", "长文案(200-300)"], horizontal=True, label_visibility="collapsed")

st.markdown('<div style="margin: 20px 0;"></div>', unsafe_allow_html=True)

st.markdown('<label class="form-label">客户资料</label>', unsafe_allow_html=True)
raw = st.text_area("资料", height=120, placeholder="请输入客户资料：出镜称呼、店铺名称、主营业务、真实故事...", label_visibility="collapsed")

st.markdown(f'<div class="form-hint">已输入 {len(raw)} 字</div>', unsafe_allow_html=True)

st.markdown('<div style="margin: 24px 0;"></div>', unsafe_allow_html=True)

if st.button("生成文案", type="primary", use_container_width=True):
    if len(raw) < 30:
        st.error("资料至少30字")
    else:
        with st.spinner("AI生成中..."):
            prog = st.progress(0)
            items = []
            for i in range(30):
                r = generate(raw, i+1, "short" if "短" in length else "long")
                items.append(r)
                prog.progress((i+1)/30)
            st.session_state.items = items
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# 结果列表
if isinstance(st.session_state.items, list) and len(st.session_state.items) > 0:
    st.markdown('<div class="apple-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header"><div class="card-title">生成结果</div></div>', unsafe_allow_html=True)
    
    for item in st.session_state.items:
        type_idx = (item['idx'] - 1) % 4
        type_class = f"type-{['blue', 'purple', 'orange', 'green'][type_idx]}"
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
    
    # Word 下载按钮
    st.markdown('<div style="margin-top: 24px;"></div>', unsafe_allow_html=True)
    
    # 生成 Word 文档
    doc = Document()
    
    # 标题
    title = doc.add_heading('晓牧传媒文案生成结果', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 统计信息
    doc.add_paragraph(f'生成总数: {len(st.session_state.items)} 条')
    doc.add_paragraph(f'优质文案: {sum(1 for i in st.session_state.items if i["ok"])} 条')
    doc.add_paragraph()
    
    # 添加每条文案
    for item in st.session_state.items:
        # 类型标题
        p = doc.add_paragraph()
        run = p.add_run(f'【{item["type"]}】文案 #{item["idx"]}')
        run.bold = True
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0, 122, 255)
        
        # 文案内容
        content_p = doc.add_paragraph(item['content'])
        content_p.paragraph_format.line_spacing = 1.5
        
        # 状态
        status = "优质" if item['ok'] else "失败" if item['wc'] == 0 else "需优化"
        status_p = doc.add_paragraph(f'状态: {status} | 字数: {item["wc"]} 字')
        status_p.runs[0].font.size = Pt(9)
        status_p.runs[0].font.color.rgb = RGBColor(142, 142, 147)
        
        # 分隔线
        doc.add_paragraph('_' * 50)
    
    # 保存到内存
    doc_io = io.BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.download_button(
            label='📄 下载 Word 文档',
            data=doc_io,
            file_name='晓牧传媒文案生成结果.docx',
            mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            use_container_width=True
        )
    with col2:
        if st.button('🗑️ 清空结果', use_container_width=True):
            st.session_state.items = []
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
