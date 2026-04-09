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

# Kimi风格CSS
st.markdown("""
<style>
    /* 基础样式 */
    * { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif !important; }
    
    /* 浅色主题背景 */
    .stApp {
        background: #fafafa !important;
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background: #ffffff !important;
        border-right: 1px solid #e5e5e5 !important;
    }
    
    /* 主内容区 */
    .main .block-container {
        max-width: 900px !important;
        padding: 0 !important;
    }
    
    /* 隐藏默认元素 */
    #MainMenu, header, footer { display: none !important; }
    
    /* 顶部导航栏 */
    .top-nav {
        background: #ffffff;
        border-bottom: 1px solid #e5e5e5;
        padding: 1rem 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .logo-text {
        font-size: 1.25rem;
        font-weight: 600;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* 输入区域 */
    .input-area {
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        padding: 1.5rem;
        margin: 1.5rem;
    }
    
    /* 文本框样式 */
    .stTextArea textarea {
        background: #f5f5f5 !important;
        border: 1px solid transparent !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        min-height: 120px !important;
    }
    
    .stTextArea textarea:focus {
        background: #ffffff !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* 发送按钮 */
    .send-btn {
        background: #3b82f6 !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    
    .send-btn:hover {
        background: #2563eb !important;
    }
    
    /* 消息卡片 */
    .message-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
    }
    
    /* AI头像 */
    .ai-avatar {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 0.875rem;
    }
    
    /* 用户头像 */
    .user-avatar {
        width: 36px;
        height: 36px;
        background: #e5e7eb;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #6b7280;
        font-weight: 600;
        font-size: 0.875rem;
    }
    
    /* 内容样式 */
    .content-text {
        line-height: 1.8;
        color: #1f2937;
        font-size: 0.95rem;
    }
    
    /* 标签 */
    .tag {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-right: 0.5rem;
    }
    
    .tag-blue { background: #dbeafe; color: #1d4ed8; }
    .tag-purple { background: #f3e8ff; color: #7c3aed; }
    .tag-green { background: #dcfce7; color: #15803d; }
    .tag-orange { background: #ffedd5; color: #c2410c; }
    
    /* 工具栏 */
    .toolbar {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #f0f0f0;
    }
    
    .tool-btn {
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: 1px solid #e5e5e5;
        background: white;
        color: #4b5563;
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .tool-btn:hover {
        background: #f9fafb;
        border-color: #d1d5db;
    }
    
    /* 统计栏 */
    .stats-bar {
        display: flex;
        gap: 2rem;
        padding: 1rem 1.5rem;
        background: #ffffff;
        border-bottom: 1px solid #e5e5e5;
    }
    
    .stat-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
        color: #6b7280;
    }
    
    .stat-num {
        font-weight: 600;
        color: #1f2937;
    }
    
    /* 侧边栏菜单 */
    .nav-item {
        padding: 0.75rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        color: #4b5563;
        font-size: 0.875rem;
    }
    
    .nav-item:hover {
        background: #f3f4f6;
    }
    
    .nav-item.active {
        background: #eff6ff;
        color: #3b82f6;
    }
    
    /* 新对话按钮 */
    .new-chat-btn {
        background: #ffffff;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 1rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        color: #4b5563;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .new-chat-btn:hover {
        background: #f9fafb;
        border-color: #d1d5db;
    }
    
    /* 加载动画 */
    .loading-dots {
        display: flex;
        gap: 0.25rem;
        padding: 1rem;
    }
    
    .loading-dots span {
        width: 8px;
        height: 8px;
        background: #3b82f6;
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out both;
    }
    
    .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
    .loading-dots span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
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

CTYPE_ICONS = {
    "干货避坑": "💡",
    "人设故事": "👤",
    "细节特写": "🔍",
    "认知反转": "💫"
}

KIMI_KEY = "sk-IA6qyNJFSYC8UB9RHnGHsgz24VWSrKalSnd5nTTbJNiqQ2uu"

@st.cache_resource
def get_client():
    return OpenAI(api_key=KIMI_KEY, base_url="https://api.moonshot.cn/v1")

def generate(raw_data, idx, industry, length):
    name = re.search(r'出镜称呼[：:]\s*(\S+)', raw_data)
    name = name.group(1) if name else "老板"
    min_w, max_w = (150, 180) if length == "short" else (200, 300)
    
    ctypes = ["干货避坑", "人设故事", "细节特写", "认知反转"]
    ctype = ctypes[(idx - 1) % 4]
    
    try:
        client = get_client()
        resp = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是短视频文案大师。黄金三秒：严禁自我介绍、店名、地址。开头用利益/冲突/悬念/扎心。语义降维：禁用匠心/高端/专业，必须具象化。"},
                {"role": "user", "content": f"创作第{idx}条{ctype}类型的短视频文案。\n\n【称呼】{name}\n【资料】{raw_data[:400]}\n\n要求:\n1.字数{min_w}-{max_w}\n2.禁止自我介绍和店名\n3.\"{name}\"不超过2次\n4.包含1个具体数字或细节\n\n直接输出文案:"""}
            ],
            max_tokens=400,
            temperature=0.85,
            timeout=30
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
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "generate"

# 侧边栏
with st.sidebar:
    st.markdown('<div style="padding: 1rem 0; text-align: center;"><span class="logo-text">📝 文案助手</span></div>', unsafe_allow_html=True)
    
    if st.button("➕ 新建对话", use_container_width=True):
        st.session_state.items = []
        st.rerun()
    
    st.divider()
    
    # 导航菜单
    nav_items = [
        ("generate", "✨", "生成文案"),
        ("history", "📚", "历史记录"),
        ("settings", "⚙️", "设置")
    ]
    
    for key, icon, label in nav_items:
        active = "active" if st.session_state.current_tab == key else ""
        st.markdown(f'<div class="nav-item {active}" onclick="">{icon} {label}</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # 配置选项
    st.markdown("**配置**")
    industry = st.selectbox("行业", list(INDUSTRIES.keys()), format_func=lambda x: INDUSTRIES[x], index=5, label_visibility="collapsed")
    length = st.radio("长度", ["short", "long"], format_func=lambda x: "短文案 (150-180字)" if x == "short" else "长文案 (200-300字)")

# 主内容区
# 顶部栏
st.markdown('<div class="top-nav"><div></div><div style="color: #9ca3af; font-size: 0.875rem;">晓牧传媒文案助手 v4.1</div></div>', unsafe_allow_html=True)

# 统计栏
if st.session_state.items:
    total = len(st.session_state.items)
    ok = sum(1 for i in st.session_state.items if i['ok'])
    stats_html = f'''
    <div class="stats-bar">
        <div class="stat-item">生成数量: <span class="stat-num">{total}</span></div>
        <div class="stat-item">优质文案: <span class="stat-num" style="color: #22c55e;">{ok}</span></div>
        <div class="stat-item">成功率: <span class="stat-num">{ok/total*100:.0f}%</span></div>
    </div>
    '''
    st.markdown(stats_html, unsafe_allow_html=True)

# 输入区域
st.markdown('<div class="input-area">', unsafe_allow_html=True)

raw = st.text_area(
    "输入",
    height=100,
    placeholder="请输入客户资料，例如：\n出镜称呼：王老板\n店铺：某某餐饮店\n主营业务：...\n（输入后点击下方生成按钮）",
    label_visibility="collapsed"
)

col1, col2 = st.columns([6, 1])
with col2:
    if st.button("生成", type="primary", use_container_width=True):
        if len(raw) < 30:
            st.error("资料至少30字")
        else:
            with st.spinner(""):
                prog = st.progress(0)
                st.session_state.items = []
                for i in range(30):
                    r = generate(raw, i+1, industry, length)
                    st.session_state.items.append(r)
                    prog.progress((i+1)/30)
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# 结果列表
for item in st.session_state.items:
    icon = CTYPE_ICONS.get(item['type'], '💬')
    
    st.markdown(f'<div class="message-card">', unsafe_allow_html=True)
    
    # 头部
    header = f'''
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div class="ai-avatar">AI</div>
            <div>
                <div style="font-weight: 600; color: #1f2937;">文案 #{item['idx']}</div>
                <div style="font-size: 0.75rem; color: #9ca3af;">{item['wc']} 字</div>
            </div>
        </div>
        <div>
            <span class="tag {'tag-green' if item['ok'] else 'tag-orange'}">{item['type']}</span>
            {'<span style="color: #22c55e; font-size: 0.875rem;">✓</span>' if item['ok'] else '<span style="color: #f59e0b; font-size: 0.875rem;">⚠</span>'}
        </div>
    </div>
    '''
    st.markdown(header, unsafe_allow_html=True)
    
    # 内容
    st.markdown(f'<div class="content-text">{item['content']}</div>', unsafe_allow_html=True)
    
    # 工具栏
    toolbar = f'''
    <div class="toolbar">
        <button class="tool-btn" onclick="">📋 复制</button>
        {'<button class="tool-btn" onclick="">🔄 重新生成</button>' if not item['ok'] else ''}
        {'<button class="tool-btn" onclick="">📖 转长文案</button>' if item['ok'] and item['len'] == 'short' else '<button class="tool-btn" onclick="">⚡ 转短文案</button>' if item['ok'] else ''}
    </div>
    '''
    
    # Streamlit按钮
    c1, c2, c3 = st.columns([1, 1, 3])
    with c1:
        if st.button("📋 复制", key=f"copy_{item['idx']}", use_container_width=True):
            st.toast("已复制到剪贴板")
    with c2:
        if not item['ok'] and st.button("🔄 重试", key=f"retry_{item['idx']}", use_container_width=True):
            with st.spinner("生成中..."):
                new = generate(raw, item['idx'], industry, length)
                st.session_state.items[item['idx']-1] = new
                st.rerun()
    with c3:
        if item['ok']:
            target = "long" if item['len'] == "short" else "short"
            label = "📖 转长文案" if target == "long" else "⚡ 转短文案"
            if st.button(label, key=f"switch_{item['idx']}", use_container_width=True):
                with st.spinner("生成中..."):
                    new = generate(raw, item['idx'], industry, target)
                    st.session_state.items[item['idx']-1] = new
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
