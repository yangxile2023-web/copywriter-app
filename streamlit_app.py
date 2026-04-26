# -*- coding: utf-8 -*-
import streamlit as st
import re
from openai import OpenAI
from sensitive_words import check_sensitive_words

st.set_page_config(page_title="晓牧传媒文案助手", layout="wide")

# CSS
st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #1a1a2e 0%, #0f3460 100%); }
    .main { max-width: 1000px; margin: 0 auto; padding: 2rem; }
    h1 { color: white !important; font-size: 2.5rem !important; }
    h1 span { color: #ff8c42 !important; }
    .stButton>button[kind="primary"] { 
        background: linear-gradient(90deg, #ff6b35, #ff8c42) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        font-size: 1.1rem !important;
    }
    .stTextArea textarea {
        background: rgba(0,0,0,0.3) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: white !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# 配置
INDUSTRIES = {"catering": "餐饮", "woodwork": "木作定制", "factory": "工厂/制造", "lottery": "彩票店", "hotel": "酒店/民宿", "general": "通用"}
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

# 初始化
if 'items' not in st.session_state:
    st.session_state.items = []

# ====== 侧边栏 ======
with st.sidebar:
    st.markdown("<h2 style='color:#ff8c42; margin:0;'>晓牧传媒</h2>", unsafe_allow_html=True)
    st.caption("内容创作系统 · 内部专用")
    
    st.markdown("---")
    
    st.markdown("""
    **功能导航**
    - AI文案生成
    - 违禁词扫描  
    - Word导出
    - 订单管理
    """)

# ====== 主内容 ======
st.markdown("<h1>生成 <span>30个</span><br>爆款视频文案</h1>", unsafe_allow_html=True)
st.caption("10种风格方向 · 智能违禁词扫描 · 一键导出Word")

st.markdown("---")

# 配置选项
col1, col2 = st.columns(2)
with col1:
    st.markdown("**行业类型**")
    industry = st.selectbox("行业", list(INDUSTRIES.keys()), format_func=lambda x: INDUSTRIES[x], label_visibility="collapsed")
with col2:
    st.markdown("**文案长度**")
    length = st.radio("长度", ["short", "long"], format_func=lambda x: "短文案 (150-180字)" if x == "short" else "长文案 (200-300字)", horizontal=True, label_visibility="collapsed")

# 输入
st.markdown("**客户资料**")
raw = st.text_area("资料", height=150, placeholder="请输入客户资料：\n\n- 出镜称呼：王老板、李姐\n- 店铺/企业名称\n- 所在城市\n- 主营业务\n- 核心卖点/特色\n- 真实故事或经历", label_visibility="collapsed")

st.caption(f"已输入 {len(raw)} 字")

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
    st.markdown("---")
    st.subheader("生成结果")
    
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
        status = "✓" if item['ok'] else "✗" if item['wc'] == 0 else "!"
        with st.expander(f"文案 #{item['idx']} [{item['type']}] {status} ({item['wc']}字)"):
            st.write(item['content'])
            col_copy, _ = st.columns([1, 5])
            with col_copy:
                st.button("复制", key=f"cp{item['idx']}")
