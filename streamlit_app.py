# -*- coding: utf-8 -*-
"""
晓牧传媒文案助手 v5.1 - Kimi风格
深色主题 · 极简设计 · 紫色主调
"""
import streamlit as st
import re
import time
from openai import OpenAI
from sensitive_words import check_sensitive_words

st.set_page_config(
    page_title="晓牧传媒文案助手",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Kimi风格CSS - 深色主题
st.markdown("""
<style>
    /* 基础深色背景 */
    .stApp {
        background: #0d0d0d !important;
    }
    
    /* 侧边栏 */
    .css-1d391kg {
        background: #171717 !important;
        border-right: 1px solid #262626 !important;
    }
    
    /* 主内容区 */
    .main .block-container {
        max-width: 1000px !important;
        padding: 2rem !important;
    }
    
    /* 隐藏默认元素 */
    #MainMenu, header, footer {
        display: none !important;
    }
    
    /* 侧边栏标题 */
    .sidebar-title {
        color: #fff;
        font-size: 1.25rem;
        font-weight: 600;
        padding: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* 新建对话按钮 */
    .new-chat-btn {
        background: #262626;
        border: 1px solid #404040;
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin: 0 1rem 1rem 1rem;
        color: #e5e5e5;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .new-chat-btn:hover {
        background: #333;
        border-color: #525252;
    }
    
    /* 导航项 */
    .nav-item {
        padding: 0.75rem 1rem;
        margin: 0 0.5rem;
        border-radius: 8px;
        color: #a3a3a3;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 0.9375rem;
        transition: all 0.2s;
    }
    
    .nav-item:hover {
        background: #262626;
        color: #e5e5e5;
    }
    
    .nav-item.active {
        background: #262626;
        color: #a78bfa;
    }
    
    /* 主标题 */
    .main-title {
        color: #fff;
        font-size: 1.75rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .main-subtitle {
        color: #737373;
        font-size: 0.9375rem;
        margin-bottom: 2rem;
    }
    
    /* 输入区域 */
    .input-container {
        background: #171717;
        border: 1px solid #262626;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .input-label {
        color: #a3a3a3;
        font-size: 0.875rem;
        margin-bottom: 0.75rem;
    }
    
    .stTextArea textarea {
        background: #0d0d0d !important;
        border: 1px solid #262626 !important;
        border-radius: 12px !important;
        color: #e5e5e5 !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #a78bfa !important;
        box-shadow: 0 0 0 2px rgba(167, 139, 250, 0.2) !important;
    }
    
    .stTextArea textarea::placeholder {
        color: #525252 !important;
    }
    
    /* 配置行 */
    .config-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    /* 选择器 */
    .stSelectbox > div > div {
        background: #0d0d0d !important;
        border: 1px solid #262626 !important;
        border-radius: 10px !important;
        color: #e5e5e5 !important;
    }
    
    /* 单选按钮 */
    .stRadio > div {
        background: #0d0d0d !important;
        border-radius: 10px !important;
        padding: 0.5rem !important;
    }
    
    .stRadio label {
        color: #a3a3a3 !important;
    }
    
    /* 发送按钮 */
    .stButton>button[kind="primary"] {
        background: #7c3aed !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.875rem 2rem !important;
        font-weight: 600 !important;
        color: white !important;
        transition: all 0.2s !important;
    }
    
    .stButton>button[kind="primary"]:hover {
        background: #6d28d9 !important;
        transform: translateY(-1px);
    }
    
    /* 消息卡片 */
    .message-card {
        background: #171717;
        border: 1px solid #262626;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.2s;
    }
    
    .message-card:hover {
        border-color: #404040;
    }
    
    /* AI头像 */
    .ai-avatar {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #7c3aed, #a78bfa);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 0.75rem;
    }
    
    /* 用户头像 */
    .user-avatar {
        width: 32px;
        height: 32px;
        background: #262626;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #a3a3a3;
        font-weight: 600;
        font-size: 0.75rem;
    }
    
    /* 消息头部 */
    .message-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }
    
    .message-author {
        color: #e5e5e5;
        font-weight: 500;
    }
    
    .message-meta {
        color: #737373;
        font-size: 0.75rem;
    }
    
    /* 消息内容 */
    .message-content {
        color: #d4d4d4;
        line-height: 1.8;
        font-size: 0.9375rem;
        padding-left: 2.75rem;
    }
    
    /* 代码块样式 */
    .stCode {
        background: #0d0d0d !important;
        border: 1px solid #262626 !important;
        border-radius: 10px !important;
    }
    
    /* 工具按钮 */
    .tool-btn {
        background: transparent;
        border: 1px solid #333;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        color: #a3a3a3;
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s;
        margin-right: 0.5rem;
    }
    
    .tool-btn:hover {
        background: #262626;
        color: #e5e5e5;
        border-color: #404040;
    }
    
    /* 类型标签 */
    .type-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.625rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-left: 0.5rem;
    }
    
    .badge-red { background: rgba(239, 68, 68, 0.15); color: #f87171; }
    .badge-purple { background: rgba(167, 139, 250, 0.15); color: #a78bfa; }
    .badge-yellow { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }
    .badge-green { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
    
    /* 统计栏 */
    .stats-bar {
        display: flex;
        gap: 2rem;
        padding: 1rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid #262626;
    }
    
    .stat-box {
        display: flex;
        flex-direction: column;
    }
    
    .stat-value {
        color: #e5e5e5;
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    .stat-label {
        color: #737373;
        font-size: 0.875rem;
    }
    
    /* 分隔线 */
    .dark-divider {
        height: 1px;
        background: #262626;
        margin: 2rem 0;
    }
    
    /* 加载动画 */
    .loading-text {
        color: #737373;
        font-size: 0.9375rem;
    }
    
    /* 滚动条 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0d0d0d;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #333;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #444;
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

CONTENT_TYPES = {
    "干货避坑": {"badge": "badge-red", "icon": "💡"},
    "人设故事": {"badge": "badge-purple", "icon": "👤"},
    "细节特写": {"badge": "badge-yellow", "icon": "🔍"},
    "认知反转": {"badge": "badge-green", "icon": "💫"}
}

KIMI_KEY = "sk-IA6qyNJFSYC8UB9RHnGHsgz24VWSrKalSnd5nTTbJNiqQ2uu"

@st.cache_resource
def get_client():
    return OpenAI(api_key=KIMI_KEY, base_url="https://api.moonshot.cn/v1")

def generate(raw_data, idx, length):
    name = re.search(r'出镜称呼[：:]\s*(\S+)', raw_data)
    name = name.group(1) if name else "老板"
    min_w, max_w = (150, 180) if length == "short" else (200, 300)
    ctypes = list(CONTENT_TYPES.keys())
    ctype = ctypes[(idx - 1) % 4]
    
    try:
        client = get_client()
        resp = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是短视频文案大师。黄金三秒：严禁自我介绍、店名、地址。语义降维：禁用匠心/高端/专业。"},
                {"role": "user", "content": f"创作第{idx}条{ctype}文案。\n称呼：{name}\n资料：{raw_data[:400]}\n\n要求:\n1.字数{min_w}-{max_w}\n2.禁止自我介绍\n3.包含1个具体数字\n\n直接输出:"""}
            ],
            max_tokens=400, temperature=0.85, timeout=30
        )
        content = resp.choices[0].message.content.strip().strip('"')
        wc = len(content.replace(' ', '').replace('\n', ''))
        ok = min_w <= wc <= max_w and not re.search(r'[路街道]\s*\d+[号]', content)
        return {'idx': idx, 'content': content, 'wc': wc, 'ok': ok, 'type': ctype}
    except Exception as e:
        return {'idx': idx, 'content': f"生成失败: {str(e)[:30]}", 'wc': 0, 'ok': False, 'type': ctype}

# 初始化
if 'items' not in st.session_state:
    st.session_state.items = []
if 'current_view' not in st.session_state:
    st.session_state.current_view = "generate"

# ========== 侧边栏 ==========
with st.sidebar:
    # 标题
    st.markdown('<div class="sidebar-title">✨ 文案助手</div>', unsafe_allow_html=True)
    
    # 新建对话按钮
    if st.button("➕ 新建对话", use_container_width=True):
        st.session_state.items = []
        st.rerun()
    
    st.markdown("<div style='margin:1rem 0; border-top:1px solid #262626;'></div>", unsafe_allow_html=True)
    
    # 导航菜单
    nav_items = [
        ("generate", "✨", "生成文案"),
        ("batch", "📚", "批量管理"),
        ("settings", "⚙️", "设置")
    ]
    
    for key, icon, label in nav_items:
        active = "active" if st.session_state.current_view == key else ""
        if st.button(f"{icon} {label}", use_container_width=True, key=f"nav_{key}"):
            st.session_state.current_view = key
            st.rerun()

# ========== 主内容区 ==========
# 根据当前视图显示不同内容
if st.session_state.current_view == "generate":
    # 标题
    st.markdown('<div class="main-title">生成文案</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-subtitle">输入客户资料，AI生成30条高质量短视频文案</div>', unsafe_allow_html=True)
    
    # 输入区域
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    # 配置行
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="input-label">行业类型</div>', unsafe_allow_html=True)
        industry = st.selectbox("行业", list(INDUSTRIES.keys()), format_func=lambda x: INDUSTRIES[x], index=5, label_visibility="collapsed")
    with col2:
        st.markdown('<div class="input-label">文案长度</div>', unsafe_allow_html=True)
        length = st.radio("长度", ["short", "long"], format_func=lambda x: "短文案 (150-180字)" if x == "short" else "长文案 (200-300字)", horizontal=True, label_visibility="collapsed")
    
    # 输入框
    st.markdown('<div class="input-label">客户资料</div>', unsafe_allow_html=True)
    raw = st.text_area("资料", height=100, placeholder="请粘贴客户资料：出镜称呼、店铺名称、主营业务、真实故事...", label_visibility="collapsed")
    
    # 发送按钮
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        st.caption(f"已输入 {len(raw)} 字")
    with col_btn:
        if st.button("发送 →", type="primary", use_container_width=True):
            if len(raw) < 30:
                st.error("资料至少30字")
            else:
                with st.spinner("AI思考中..."):
                    prog = st.progress(0)
                    st.session_state.items = []
                    for i in range(30):
                        r = generate(raw, i+1, length)
                        st.session_state.items.append(r)
                        prog.progress((i+1)/30)
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 结果显示
    if st.session_state.items:
        # 统计栏
        items = st.session_state.items
        total = len(items)
        ok = sum(1 for i in items if i['ok'])
        fail = sum(1 for i in items if i['wc'] == 0)
        warn = total - ok - fail
        
        st.markdown(f"""
        <div class="stats-bar">
            <div class="stat-box">
                <span class="stat-value">{total}</span>
                <span class="stat-label">总数</span>
            </div>
            <div class="stat-box">
                <span class="stat-value" style="color:#4ade80">{ok}</span>
                <span class="stat-label">优质</span>
            </div>
            <div class="stat-box">
                <span class="stat-value" style="color:#fbbf24">{warn}</span>
                <span class="stat-label">需优化</span>
            </div>
            <div class="stat-box">
                <span class="stat-value" style="color:#f87171">{fail}</span>
                <span class="stat-label">失败</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 消息列表
        for item in items:
            ct_info = CONTENT_TYPES.get(item['type'], {})
            status_icon = "✓" if item['ok'] else "✗" if item['wc'] == 0 else "!"
            
            st.markdown(f"""
            <div class="message-card">
                <div class="message-header">
                    <div class="ai-avatar">AI</div>
                    <span class="message-author">文案 #{item['idx']}</span>
                    <span class="type-badge {ct_info.get('badge', '')}">{item['type']}</span>
                    <span class="message-meta">{item['wc']} 字 · {status_icon}</span>
                </div>
                <div class="message-content">{item['content']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # 操作按钮
            col_copy, col_retry = st.columns([1, 6])
            with col_copy:
                st.button("复制", key=f"cp{item['idx']}")

elif st.session_state.current_view == "batch":
    st.markdown('<div class="main-title">批量管理</div>', unsafe_allow_html=True)
    
    if st.session_state.items:
        if st.button("📋 复制全部文案", use_container_width=True):
            txt = "\n\n".join([f"【{i['type']}】\n{i['content']}" for i in st.session_state.items])
            st.code(txt, language=None)
        if st.button("🗑️ 清空结果", use_container_width=True):
            st.session_state.items = []
            st.rerun()
    else:
        st.info("暂无文案，请先在生成页面创建")

elif st.session_state.current_view == "settings":
    st.markdown('<div class="main-title">设置</div>', unsafe_allow_html=True)
    st.markdown("- 版本: v5.1 (Kimi风格)")
    st.markdown("- 主题: 深色模式")
    st.markdown("- API: Kimi (Moonshot)")
