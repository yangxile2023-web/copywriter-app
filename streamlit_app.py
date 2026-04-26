# -*- coding: utf-8 -*-
"""
晓牧传媒文案助手 v6.0
完全重构 - 深色主题 + 橙色强调色
"""
import streamlit as st
import re
import time
from openai import OpenAI
from sensitive_words import check_sensitive_words

st.set_page_config(
    page_title="晓牧传媒文案助手",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 全新CSS - 深色主题 + 橙色强调
st.markdown("""
<style>
    /* 全局深色背景 */
    .stApp {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
        min-height: 100vh;
    }
    
    /* 侧边栏 */
    .css-1d391kg {
        background: rgba(26, 26, 46, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* 隐藏默认元素 */
    #MainMenu, header, footer {
        display: none !important;
    }
    
    /* 侧边栏品牌 */
    .brand-section {
        padding: 2rem 1.5rem;
    }
    
    .brand-name {
        background: linear-gradient(90deg, #ff6b35, #ff8c42);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.75rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .brand-tagline {
        color: rgba(255, 255, 255, 0.5);
        font-size: 0.875rem;
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
        border-radius: 10px;
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.9375rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .nav-item:hover {
        background: rgba(255, 255, 255, 0.05);
        color: rgba(255, 255, 255, 0.9);
    }
    
    .nav-item.active {
        background: rgba(255, 107, 53, 0.15);
        color: #ff8c42;
    }
    
    /* 主内容区 */
    .main-content {
        padding: 3rem 4rem;
        max-width: 900px;
        margin: 0 auto;
    }
    
    /* 主标题 */
    .hero-title {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 1.5rem;
    }
    
    .hero-title .highlight {
        background: linear-gradient(90deg, #ff6b35, #ff8c42);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* 副标题 */
    .hero-subtitle {
        color: rgba(255, 255, 255, 0.6);
        font-size: 1rem;
        line-height: 2;
        margin-bottom: 3rem;
    }
    
    /* 输入区域 */
    .input-section {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .input-label {
        color: rgba(255, 255, 255, 0.4);
        font-size: 0.875rem;
        margin-bottom: 0.75rem;
    }
    
    .stTextArea textarea {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }
    
    .stTextArea textarea::placeholder {
        color: rgba(255, 255, 255, 0.3) !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #ff8c42 !important;
        box-shadow: 0 0 0 3px rgba(255, 140, 66, 0.1) !important;
    }
    
    /* 配置选项 */
    .config-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .config-item {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
    }
    
    .config-label {
        color: rgba(255, 255, 255, 0.4);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
    }
    
    /* 选择器样式 */
    .stSelectbox > div > div {
        background: transparent !important;
        border: none !important;
        color: white !important;
    }
    
    .stRadio > div {
        display: flex;
        gap: 1rem;
        background: transparent !important;
    }
    
    .stRadio label {
        color: rgba(255, 255, 255, 0.6) !important;
    }
    
    /* 生成按钮 */
    .generate-btn {
        background: linear-gradient(90deg, #ff6b35, #ff8c42) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 2rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: white !important;
        width: 100% !important;
        box-shadow: 0 4px 20px rgba(255, 107, 53, 0.3) !important;
        transition: all 0.3s !important;
    }
    
    .generate-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 30px rgba(255, 107, 53, 0.4) !important;
    }
    
    /* 结果区域 */
    .results-section {
        margin-top: 3rem;
    }
    
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .section-title {
        color: white;
        font-size: 1.25rem;
        font-weight: 600;
    }
    
    /* 文案卡片 */
    .copy-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: all 0.2s;
    }
    
    .copy-card:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.15);
    }
    
    .copy-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    
    .copy-index {
        color: rgba(255, 255, 255, 0.3);
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .copy-type {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .type-1 { background: rgba(255, 107, 53, 0.2); color: #ff8c42; }
    .type-2 { background: rgba(139, 92, 246, 0.2); color: #a78bfa; }
    .type-3 { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
    .type-4 { background: rgba(34, 197, 94, 0.2); color: #4ade80; }
    
    .copy-content {
        color: rgba(255, 255, 255, 0.9);
        line-height: 1.8;
        font-size: 0.9375rem;
        margin-bottom: 1rem;
    }
    
    .copy-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: rgba(255, 255, 255, 0.4);
        font-size: 0.75rem;
    }
    
    /* 统计标签 */
    .stat-tag {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    
    .tag-success { background: rgba(34, 197, 94, 0.2); color: #4ade80; }
    .tag-warning { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
    .tag-error { background: rgba(239, 68, 68, 0.2); color: #f87171; }
    
    /* 工具按钮 */
    .tool-btn {
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        color: rgba(255, 255, 255, 0.6);
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .tool-btn:hover {
        border-color: #ff8c42;
        color: #ff8c42;
    }
    
    /* 空状态 */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: rgba(255, 255, 255, 0.3);
    }
    
    /* 加载动画 */
    .stProgress > div > div {
        background: linear-gradient(90deg, #ff6b35, #ff8c42) !important;
    }
    
    /* 滚动条 */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# 配置
INDUSTRIES = {
    "catering": "餐饮",
    "woodwork": "木作定制",
    "factory": "工厂/制造",
    "lottery": "彩票店",
    "hotel": "酒店/民宿",
    "general": "通用"
}

CONTENT_TYPES = [
    ("干货避坑", "type-1"),
    ("人设故事", "type-2"),
    ("细节特写", "type-3"),
    ("认知反转", "type-4")
]

KIMI_KEY = "sk-IA6qyNJFSYC8UB9RHnGHsgz24VWSrKalSnd5nTTbJNiqQ2uu"

@st.cache_resource
def get_client():
    return OpenAI(api_key=KIMI_KEY, base_url="https://api.moonshot.cn/v1")

def generate(raw_data, idx, length):
    name = re.search(r'出镜称呼[：:]\s*(\S+)', raw_data)
    name = name.group(1) if name else "老板"
    min_w, max_w = (150, 180) if length == "short" else (200, 300)
    ctype, type_class = CONTENT_TYPES[(idx - 1) % 4]
    
    try:
        client = get_client()
        resp = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是短视频文案大师。黄金三秒：严禁自我介绍、店名、地址。语义降维：禁用匠心/高端/专业，必须具象化。"},
                {"role": "user", "content": f"创作第{idx}条{ctype}文案。\n称呼：{name}\n资料：{raw_data[:400]}\n\n要求:\n1.字数{min_w}-{max_w}\n2.禁止自我介绍\n3.包含1个具体数字\n\n直接输出:"""}
            ],
            max_tokens=400, temperature=0.85, timeout=30
        )
        content = resp.choices[0].message.content.strip().strip('"')
        wc = len(content.replace(' ', '').replace('\n', ''))
        ok = min_w <= wc <= max_w and not re.search(r'[路街道]\s*\d+[号]', content)
        return {'idx': idx, 'content': content, 'wc': wc, 'ok': ok, 'type': ctype, 'type_class': type_class}
    except Exception as e:
        return {'idx': idx, 'content': f"生成失败: {str(e)[:30]}", 'wc': 0, 'ok': False, 'type': ctype, 'type_class': type_class}

# 初始化
if 'items' not in st.session_state:
    st.session_state.items = []
if 'page' not in st.session_state:
    st.session_state.page = "home"

# ========== 侧边栏 ==========
with st.sidebar:
    # 品牌
    st.markdown("""
    <div class="brand-section">
        <div class="brand-name">晓牧传媒</div>
        <div class="brand-tagline">内容创作系统 · 内部专用</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 导航
    st.markdown("<div class='nav-menu'>", unsafe_allow_html=True)
    
    nav_items = [
        ("home", "🏠", "首页"),
        ("generate", "✨", "生成文案"),
        ("scan", "🔍", "违禁词扫描"),
        ("export", "📄", "Word导出")
    ]
    
    for key, icon, label in nav_items:
        active = "active" if st.session_state.page == key else ""
        if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ========== 主内容 ==========
if st.session_state.page == "home":
    st.markdown("""
    <div class="main-content">
        <h1 class="hero-title">生成<span class="highlight">30个</span><br>爆款视频文案</h1>
        <p class="hero-subtitle">
            10种风格方向 · 智能违禁词扫描<br>
            一键导出Word文档
        </p>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == "generate":
    st.markdown("""
    <div class="main-content">
        <h1 class="hero-title">生成<span class="highlight">30个</span><br>爆款视频文案</h1>
        <p class="hero-subtitle">
            输入客户资料，AI自动生成30条高质量短视频文案
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 配置
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="input-label">行业类型</div>', unsafe_allow_html=True)
        industry = st.selectbox("行业", list(INDUSTRIES.keys()), format_func=lambda x: INDUSTRIES[x], index=5, label_visibility="collapsed")
    with col2:
        st.markdown('<div class="input-label">文案长度</div>', unsafe_allow_html=True)
        length = st.radio("长度", ["short", "long"], format_func=lambda x: "短文案 (150-180字)" if x == "short" else "长文案 (200-300字)", horizontal=True, label_visibility="collapsed")
    
    # 输入
    st.markdown('<div class="input-label">客户资料</div>', unsafe_allow_html=True)
    raw = st.text_area("资料", height=150, placeholder="请输入客户资料，包含：出镜称呼、店铺名称、主营业务、真实故事...", label_visibility="collapsed")
    
    # 生成按钮
    if st.button("一键生成 →", type="primary", use_container_width=True):
        if len(raw) < 30:
            st.error("资料至少30字")
        else:
            with st.spinner("AI生成中..."):
                prog = st.progress(0)
                st.session_state.items = []
                for i in range(30):
                    r = generate(raw, i+1, length)
                    st.session_state.items.append(r)
                    prog.progress((i+1)/30)
            st.rerun()
    
    # 结果
    if st.session_state.items:
        st.markdown("<div class='results-section'>", unsafe_allow_html=True)
        
        # 头部
        col_title, col_copy = st.columns([6, 1])
        with col_title:
            st.markdown('<div class="section-title">生成结果</div>', unsafe_allow_html=True)
        with col_copy:
            if st.button("📋 复制全部", key="copy_all"):
                txt = "\n\n".join([f"【{i['type']}】\n{i['content']}" for i in st.session_state.items])
                st.code(txt)
        
        # 列表
        for item in st.session_state.items:
            status_class = "tag-success" if item['ok'] else "tag-error" if item['wc'] == 0 else "tag-warning"
            status_text = "优质" if item['ok'] else "失败" if item['wc'] == 0 else "需优化"
            
            st.markdown(f"""
            <div class="copy-card">
                <div class="copy-header">
                    <span class="copy-index">#{item['idx']}</span>
                    <span class="copy-type {item['type_class']}">{item['type']}</span>
                </div>
                <div class="copy-content">{item['content']}</div>
                <div class="copy-meta">
                    <span>{item['wc']} 字</span>
                    <span class="stat-tag {status_class}">{status_text}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.page == "scan":
    st.markdown('<div class="main-content"><h1 class="hero-title">违禁词<span class="highlight">扫描</span></h1></div>', unsafe_allow_html=True)
    if st.session_state.items:
        total_words = sum(len(check_sensitive_words(i['content'])) for i in st.session_state.items)
        if total_words > 0:
            st.error(f"发现 {total_words} 个敏感词")
        else:
            st.success("✅ 未检测到敏感词")
    else:
        st.info("请先生成文案")

elif st.session_state.page == "export":
    st.markdown('<div class="main-content"><h1 class="hero-title">Word<span class="highlight">导出</span></h1></div>', unsafe_allow_html=True)
    if st.session_state.items:
        txt = "\n\n".join([f"【{i['type']}】文案 #{i['idx']}\n{i['content']}" for i in st.session_state.items])
        st.code(txt)
        st.download_button("下载 Word 文档", txt, file_name="文案.docx")
    else:
        st.info("请先生成文案")
