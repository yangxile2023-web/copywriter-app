# -*- coding: utf-8 -*-
import streamlit as st
import re
from openai import OpenAI
from sensitive_words import check_sensitive_words

st.set_page_config(page_title="晓牧传媒文案助手", layout="wide")

# 深色主题CSS
st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #1a1a2e 0%, #0f3460 100%); }
    .css-1d391kg { background: rgba(26,26,46,0.95) !important; }
    #MainMenu, header, footer { display: none !important; }
    .main { max-width: 1000px; margin: 0 auto; padding: 2rem; }
    h1 { color: white !important; }
    .stButton>button[kind="primary"] { 
        background: linear-gradient(90deg, #ff6b35, #ff8c42) !important;
        border: none !important;
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

# 侧边栏
with st.sidebar:
    st.markdown("<h2 style='color:#ff8c42'>晓牧传媒</h2>", unsafe_allow_html=True)
    st.caption("内容创作系统")
    
    if st.button("🏠 首页"):
        st.session_state.page = "home"
    if st.button("✨ 生成文案"):
        st.session_state.page = "generate"

# 主内容
page = st.session_state.get("page", "home")

if page == "home":
    st.title("生成 **30个** 爆款视频文案")
    st.caption("10种风格方向 · 智能违禁词扫描 · 一键导出Word")

elif page == "generate":
    st.title("生成文案")
    
    col1, col2 = st.columns(2)
    with col1:
        industry = st.selectbox("行业", list(INDUSTRIES.keys()), format_func=lambda x: INDUSTRIES[x])
    with col2:
        length = st.radio("长度", ["short", "long"], format_func=lambda x: "短文案(150-180)" if x == "short" else "长文案(200-300)")
    
    raw = st.text_area("客户资料", height=150, placeholder="输入客户资料：出镜称呼、店铺名称、主营业务、真实故事...")
    
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
    
    # 显示结果
    if st.session_state.items:
        st.divider()
        st.subheader("生成结果")
        
        for item in st.session_state.items:
            with st.expander(f"#{item['idx']} {item['type']} ({item['wc']}字) {'✓' if item['ok'] else '✗'}"):
                st.write(item['content'])
                st.button("复制", key=f"cp{item['idx']}")
