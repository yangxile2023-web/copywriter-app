# -*- coding: utf-8 -*-
"""
晓牧传媒文案助手 v4.3
现代简洁风格设计
"""
import streamlit as st
import re
import time
from openai import OpenAI
from sensitive_words import check_sensitive_words

# ========== 页面配置 ==========
st.set_page_config(
    page_title="晓牧传媒文案助手",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 现代化CSS样式 ==========
st.markdown("""
<style>
    /* 基础样式重置 */
    .stApp {
        background: linear-gradient(180deg, #fafafa 0%, #f5f5f5 100%);
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background: #ffffff !important;
        border-right: 1px solid #e5e5e5;
    }
    
    /* 主内容区 */
    .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
    }
    
    /* 隐藏默认元素 */
    #MainMenu, header, footer {
        display: none !important;
    }
    
    /* 顶部品牌栏 */
    .brand-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
    }
    
    .brand-title {
        color: white;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0;
    }
    
    .brand-subtitle {
        color: rgba(255,255,255,0.8);
        font-size: 0.875rem;
        margin: 0.25rem 0 0 0;
    }
    
    /* 卡片样式 */
    .modern-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
    }
    
    /* 输入框样式 */
    .stTextArea textarea {
        background: #fafafa !important;
        border: 2px solid #e8e8e8 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        transition: all 0.2s !important;
    }
    
    .stTextArea textarea:focus {
        background: white !important;
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* 按钮样式 */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.875rem 2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s !important;
    }
    
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton>button[kind="secondary"] {
        background: white !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 10px !important;
        color: #666 !important;
        transition: all 0.2s !important;
    }
    
    .stButton>button[kind="secondary"]:hover {
        background: #f8f8f8 !important;
        border-color: #667eea !important;
        color: #667eea !important;
    }
    
    /* 统计卡片 */
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        border: 1px solid #f0f0f0;
        transition: all 0.2s;
    }
    
    .stat-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        color: #888;
        font-size: 0.875rem;
        margin-top: 0.25rem;
    }
    
    /* 文案卡片 */
    .copy-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid #f0f0f0;
        transition: all 0.3s;
    }
    
    .copy-card:hover {
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-color: #e0e0e0;
    }
    
    .copy-card.success {
        border-left: 4px solid #22c55e;
    }
    
    .copy-card.warning {
        border-left: 4px solid #f59e0b;
    }
    
    .copy-card.error {
        border-left: 4px solid #ef4444;
        background: #fefafa;
    }
    
    /* 标签 */
    .type-tag {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .tag-tip { background: #fee2e2; color: #991b1b; }
    .tag-story { background: #f3e8ff; color: #7c3aed; }
    .tag-detail { background: #fef3c7; color: #b45309; }
    .tag-reverse { background: #d1fae5; color: #15803d; }
    
    /* 状态标签 */
    .status-tag {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .status-ok { background: #dcfce7; color: #166534; }
    .status-warn { background: #fef3c7; color: #92400e; }
    .status-err { background: #fee2e2; color: #991b1b; }
    
    /* 内容文本 */
    .content-text {
        background: #fafafa;
        border-radius: 10px;
        padding: 1rem;
        line-height: 1.8;
        color: #374151;
        margin: 0.75rem 0;
    }
    
    /* 分隔线 */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #e5e5e5, transparent);
        margin: 1.5rem 0;
    }
    
    /* 侧边栏菜单项 */
    .nav-item {
        padding: 0.75rem 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s;
        color: #4b5563;
        font-weight: 500;
    }
    
    .nav-item:hover {
        background: #f3f4f6;
        color: #667eea;
    }
    
    /* 进度条美化 */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
        border-radius: 10px !important;
    }
    
    /* 折叠面板 */
    .streamlit-expanderHeader {
        background: white !important;
        border: 1px solid #f0f0f0 !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
    }
    
    /* 代码块 */
    .stCode {
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== 配置数据 ==========
INDUSTRIES = {
    "catering": "餐饮",
    "woodwork": "木作定制",
    "factory": "工厂/制造",
    "lottery": "彩票店",
    "hotel": "酒店/民宿",
    "general": "通用"
}

CONTENT_TYPES = {
    "干货避坑": {"class": "tag-tip", "icon": "💡"},
    "人设故事": {"class": "tag-story", "icon": "👤"},
    "细节特写": {"class": "tag-detail", "icon": "🔍"},
    "认知反转": {"class": "tag-reverse", "icon": "💫"}
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
                {"role": "system", "content": "你是短视频文案大师。黄金三秒：严禁自我介绍、店名、地址。语义降维：禁用匠心/高端/专业，必须具象化。"},
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

# ========== 初始化 ==========
if 'items' not in st.session_state:
    st.session_state.items = []

# ========== 顶部品牌栏 ==========
st.markdown("""
<div class="brand-header">
    <h1 class="brand-title">晓牧传媒文案助手</h1>
    <p class="brand-subtitle">AI驱动短视频文案生成工具</p>
</div>
""", unsafe_allow_html=True)

# ========== 主布局 ==========
left_col, right_col = st.columns([300, 1])

with left_col:
    st.markdown("### 配置")
    
    with st.container():
        st.markdown("**行业类型**")
        industry = st.selectbox("行业", list(INDUSTRIES.keys()), format_func=lambda x: INDUSTRIES[x], index=5, label_visibility="collapsed")
    
    st.markdown("<div style='margin:1rem 0;'></div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("**文案长度**")
        length = st.radio("长度", ["short", "long"], format_func=lambda x: "短文案 (150-180字)" if x == "short" else "长文案 (200-300字)", label_visibility="collapsed")
    
    with st.expander("内容类型说明"):
        st.markdown("**💡 干货避坑** - 揭露行业内幕、避坑指南")
        st.markdown("**👤 人设故事** - 老板个人经历、创业故事")
        st.markdown("**🔍 细节特写** - 产品工艺的具体细节")
        st.markdown("**💫 认知反转** - 颠覆常识、打破认知")
    
    if st.session_state.items:
        st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
        st.markdown("### 工具")
        
        if st.button("📋 复制全部文案", use_container_width=True):
            txt = "\n\n".join([f"【{i['type']}】\n{i['content']}" for i in st.session_state.items])
            st.code(txt, language=None)
        
        if st.button("🗑️ 清空结果", use_container_width=True):
            st.session_state.items = []
            st.rerun()

with right_col:
    # 输入区
    st.markdown("### 客户资料")
    
    with st.container():
        raw = st.text_area("资料", height=120, placeholder="请粘贴客户资料：\n\n- 出镜称呼：王老板、李姐\n- 店铺/企业名称\n- 所在城市\n- 主营业务\n- 核心卖点/特色\n- 真实故事或经历", label_visibility="collapsed")
        
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            st.caption(f"已输入 {len(raw)} 字")
        with col_btn:
            if st.button("✨ 生成", type="primary", use_container_width=True):
                if len(raw) < 30:
                    st.error("资料至少30字")
                else:
                    with st.spinner("生成中..."):
                        prog = st.progress(0)
                        st.session_state.items = []
                        for i in range(30):
                            r = generate(raw, i+1, length)
                            st.session_state.items.append(r)
                            prog.progress((i+1)/30)
                    st.rerun()
    
    # 结果显示
    if st.session_state.items:
        st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
        st.markdown("### 生成结果")
        
        # 统计
        items = st.session_state.items
        total = len(items)
        ok = sum(1 for i in items if i['ok'])
        fail = sum(1 for i in items if i['wc'] == 0)
        warn = total - ok - fail
        
        cols = st.columns(4)
        stats = [
            (total, "总数", "#667eea"),
            (ok, "优质", "#22c55e"),
            (warn, "需优化", "#f59e0b"),
            (fail, "失败", "#ef4444")
        ]
        
        for col, (val, lbl, clr) in zip(cols, stats):
            with col:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-number" style="background: linear-gradient(135deg, {clr}, {clr}dd); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{val}</div>
                    <div class="stat-label">{lbl}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin:1.5rem 0;'></div>", unsafe_allow_html=True)
        
        # 文案列表
        for item in items:
            is_fail = item['wc'] == 0
            is_warn = not item['ok'] and not is_fail
            card_class = "error" if is_fail else ("warning" if is_warn else "success")
            
            ct_info = CONTENT_TYPES.get(item['type'], {})
            status_class = "status-ok" if item['ok'] else "status-err" if is_fail else "status-warn"
            status_text = "优质" if item['ok'] else "失败" if is_fail else "需优化"
            
            st.markdown(f"""
            <div class="copy-card {card_class}">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <span style="font-size:1.25rem; font-weight:700; color:#d1d5db;">#{item['idx']}</span>
                        <span class="type-tag {ct_info.get('class', '')}">{item['type']}</span>
                        <span style="color:#9ca3af; font-size:0.875rem;">{item['wc']}字</span>
                    </div>
                    <span class="status-tag {status_class}">{status_text}</span>
                </div>
                <div class="content-text">{item['content']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            b1, b2 = st.columns([1, 5])
            with b1:
                if st.button("📋 复制", key=f"cp{item['idx']}", use_container_width=True):
                    st.toast(f"已复制 #{item['idx']}")
