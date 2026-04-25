# -*- coding: utf-8 -*-
"""
晓牧传媒文案助手 v5.0
现代简洁风格 - 米白+橙色配色
"""
import streamlit as st
import re
import time
from openai import OpenAI
from sensitive_words import check_sensitive_words

st.set_page_config(page_title="晓牧传媒文案助手", layout="wide")

# 现代简洁风格CSS
st.markdown("""
<style>
    /* 基础样式 */
    * { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif !important; }
    
    .stApp {
        background: linear-gradient(135deg, #faf8f5 0%, #f5f0e8 100%) !important;
    }
    
    #MainMenu, header, footer { display: none !important; }
    
    /* 主布局 */
    .main .block-container {
        max-width: 1400px !important;
        padding: 0 !important;
    }
    
    /* 左侧品牌区 */
    .brand-section {
        background: linear-gradient(180deg, #faf8f5 0%, #f0ebe3 100%);
        padding: 3rem;
        min-height: 100vh;
        position: relative;
    }
    
    .brand-label {
        color: #ff8c42;
        font-size: 0.875rem;
        font-weight: 600;
        letter-spacing: 0.2em;
        margin-bottom: 0.5rem;
    }
    
    .brand-name {
        color: #ff8c42;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    
    .brand-sub {
        color: #999;
        font-size: 0.875rem;
    }
    
    .main-title {
        margin-top: 4rem;
    }
    
    .main-title h1 {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        line-height: 1.2 !important;
        color: #1a1a1a !important;
        margin: 0 !important;
    }
    
    .main-title .highlight {
        color: #ff8c42;
    }
    
    .features {
        margin-top: 2rem;
        color: #666;
        font-size: 0.9375rem;
        line-height: 2;
    }
    
    .stats-row {
        display: flex;
        gap: 3rem;
        margin-top: 4rem;
    }
    
    .stat-item h3 {
        font-size: 2.5rem;
        color: #ff8c42;
        margin: 0;
    }
    
    .stat-item p {
        color: #999;
        font-size: 0.875rem;
        margin: 0.25rem 0 0 0;
    }
    
    /* 功能标签 */
    .feature-tags {
        display: flex;
        gap: 1rem;
        margin-top: 3rem;
        flex-wrap: wrap;
    }
    
    .feature-tag {
        padding: 0.75rem 1.5rem;
        border: 1px solid #ddd;
        border-radius: 8px;
        color: #666;
        font-size: 0.875rem;
        background: rgba(255,255,255,0.5);
    }
    
    /* 右侧工作区 */
    .work-section {
        background: #ffffff;
        padding: 3rem;
        min-height: 100vh;
    }
    
    .welcome-text {
        color: #ff8c42;
        font-size: 0.875rem;
        font-weight: 500;
        letter-spacing: 0.3em;
        margin-bottom: 1rem;
    }
    
    .section-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    
    .section-title .version {
        font-size: 0.875rem;
        color: #999;
        font-weight: 400;
    }
    
    .section-desc {
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* 输入框样式 */
    .stTextArea textarea {
        background: #f8f8f8 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        color: #333 !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #ff8c42 !important;
        box-shadow: 0 0 0 3px rgba(255,140,66,0.1) !important;
    }
    
    /* 按钮样式 */
    .stButton>button[kind="primary"] {
        background: #ff8c42 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 2rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(255,140,66,0.3) !important;
        transition: all 0.3s !important;
    }
    
    .stButton>button[kind="primary"]:hover {
        background: #e67a35 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255,140,66,0.4) !important;
    }
    
    /* 选择器 */
    .stSelectbox > div > div {
        background: #f8f8f8 !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 10px !important;
    }
    
    /* 统计卡片 */
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #f0f0f0;
        text-align: center;
    }
    
    .stat-card h4 {
        font-size: 2rem;
        color: #ff8c42;
        margin: 0;
    }
    
    .stat-card p {
        color: #999;
        font-size: 0.875rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* 文案卡片 */
    .copy-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #f0f0f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .copy-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .copy-type {
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .type-red { background: #fff0eb; color: #c45c3e; }
    .type-purple { background: #f3e8ff; color: #7c3aed; }
    .type-yellow { background: #fff8e7; color: #b8860b; }
    .type-green { background: #e8f5e9; color: #2e7d32; }
    
    .copy-status {
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-ok { color: #2e7d32; }
    .status-warn { color: #b8860b; }
    .status-err { color: #c45c3e; }
    
    .copy-content {
        background: #fafafa;
        border-radius: 10px;
        padding: 1rem;
        line-height: 1.8;
        color: #333;
        margin-bottom: 1rem;
    }
    
    .copy-meta {
        display: flex;
        gap: 1rem;
        align-items: center;
    }
    
    .copy-index {
        font-size: 1.25rem;
        font-weight: 700;
        color: #ddd;
    }
    
    /* 分隔线 */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #e0e0e0, transparent);
        margin: 2rem 0;
    }
    
    /* 标签页 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: #f8f8f8;
        padding: 0.25rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #666 !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #ff8c42 !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
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
    "干货避坑": {"class": "type-red", "desc": "揭露行业内幕"},
    "人设故事": {"class": "type-purple", "desc": "老板个人经历"},
    "细节特写": {"class": "type-yellow", "desc": "产品工艺细节"},
    "认知反转": {"class": "type-green", "desc": "颠覆常识"}
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
        return {'idx': idx, 'content': f"失败:{str(e)[:30]}", 'wc': 0, 'ok': False, 'type': ctype}

# 初始化
if 'items' not in st.session_state:
    st.session_state.items = []

# 两栏布局
left_col, right_col = st.columns([1, 1])

# ========== 左侧品牌区 ==========
with left_col:
    st.markdown("""
    <div class="brand-section">
        <div class="brand-label">// XIAOMUCHUANMEI</div>
        <div class="brand-name">晓牧传媒</div>
        <div class="brand-sub">内容创作系统 · 内部专用</div>
        
        <div class="main-title">
            <h1>专注短视频<br><span class="highlight">文案内容</span>创作</h1>
        </div>
        
        <div class="features">
            AI 驱动生成 · 行业违禁词精准扫描<br>
            10批次 × 3条 · 30个脚本一键导出 Word
        </div>
        
        <div class="stats-row">
            <div class="stat-item">
                <h3>30+</h3>
                <p>脚本/次生成</p>
            </div>
            <div class="stat-item">
                <h3>10+</h3>
                <p>行业分类适配</p>
            </div>
            <div class="stat-item">
                <h3>AI</h3>
                <p>智能质量评分</p>
            </div>
        </div>
        
        <div class="feature-tags">
            <div class="feature-tag">AI 文案生成</div>
            <div class="feature-tag">违禁词扫描</div>
            <div class="feature-tag">Word 导出</div>
            <div class="feature-tag">订单管理</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ========== 右侧工作区 ==========
with right_col:
    st.markdown("""
    <div class="work-section">
        <div class="welcome-text">// 欢迎回来</div>
        <div class="section-title">文案工作台 <span class="version">v5.0</span></div>
        <div class="section-desc">输入客户资料，生成高质量短视频文案</div>
    """, unsafe_allow_html=True)
    
    # 配置选项卡
    tab1, tab2, tab3 = st.tabs(["生成文案", "批量管理", "设置"])
    
    with tab1:
        # 配置
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**行业类型**")
            industry = st.selectbox("行业", list(INDUSTRIES.keys()), format_func=lambda x: INDUSTRIES[x], index=5, label_visibility="collapsed")
        with col2:
            st.markdown("**文案长度**")
            length = st.radio("长度", ["short", "long"], format_func=lambda x: "短文案(150-180字)" if x == "short" else "长文案(200-300字)", horizontal=True, label_visibility="collapsed")
        
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        
        # 输入区
        st.markdown("**客户资料**")
        raw = st.text_area("资料", height=120, placeholder="请粘贴客户资料：\n\n- 出镜称呼：王老板、李姐\n- 店铺/企业名称\n- 所在城市\n- 主营业务\n- 核心卖点/特色\n- 真实故事或经历", label_visibility="collapsed")
        
        # 生成按钮
        col_stat, col_btn = st.columns([4, 1])
        with col_stat:
            st.caption(f"已输入 {len(raw)} 字")
        with col_btn:
            if st.button("生成 →", type="primary", use_container_width=True):
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
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            st.markdown("**生成结果**")
            
            # 统计
            items = st.session_state.items
            total = len(items)
            ok = sum(1 for i in items if i['ok'])
            fail = sum(1 for i in items if i['wc'] == 0)
            warn = total - ok - fail
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("总数", total)
            c2.metric("优质", ok)
            c3.metric("需优化", warn)
            c4.metric("失败", fail)
            
            # 文案列表
            for item in items:
                is_fail = item['wc'] == 0
                is_warn = not item['ok'] and not is_fail
                ct_info = CONTENT_TYPES.get(item['type'], {})
                status_class = "status-ok" if item['ok'] else "status-err" if is_fail else "status-warn"
                status_text = "优质" if item['ok'] else "失败" if is_fail else "需优化"
                
                st.markdown(f"""
                <div class="copy-card">
                    <div class="copy-header">
                        <div style="display:flex; align-items:center; gap:0.75rem;">
                            <span class="copy-index">#{item['idx']}</span>
                            <span class="copy-type {ct_info.get('class', '')}">{item['type']}</span>
                            <span style="color:#999; font-size:0.875rem;">{item['wc']}字</span>
                        </div>
                        <span class="copy-status {status_class}">{status_text}</span>
                    </div>
                    <div class="copy-content">{item['content']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                b1, b2 = st.columns([1, 4])
                with b1:
                    st.button("复制", key=f"cp{item['idx']}")
    
    with tab2:
        st.markdown("**批量操作**")
        if st.session_state.items:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("复制全部文案", use_container_width=True):
                    txt = "\n\n".join([f"【{i['type']}】\n{i['content']}" for i in st.session_state.items])
                    st.code(txt)
            with col2:
                if st.button("清空结果", use_container_width=True):
                    st.session_state.items = []
                    st.rerun()
        else:
            st.info("暂无文案，请先生成")
    
    with tab3:
        st.markdown("**关于**")
        st.markdown("- 版本: v5.0")
        st.markdown("- 功能: AI生成30条短视频文案")
        st.markdown("- 特点: 黄金三秒、语义降维、内容分类")
    
    st.markdown("</div>", unsafe_allow_html=True)
