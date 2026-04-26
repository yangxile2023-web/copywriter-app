import streamlit as st
import re
from openai import OpenAI

st.set_page_config(page_title="晓牧传媒文案助手", layout="wide")

# 最简化CSS
st.markdown("""
<style>
.stApp { background: #1a1a2e; }
</style>
""", unsafe_allow_html=True)

st.title("晓牧传媒文案助手")
st.caption("v6.0 - AI生成30条短视频文案")

KIMI_KEY = "sk-IA6qyNJFSYC8UB9RHnGHsgz24VWSrKalSnd5nTTbJNiqQ2uu"

@st.cache_resource
def get_client():
    return OpenAI(api_key=KIMI_KEY, base_url="https://api.moonshot.cn/v1")

if 'items' not in st.session_state:
    st.session_state.items = []

# 侧边栏
with st.sidebar:
    st.header("晓牧传媒")
    st.caption("内容创作系统")

# 主内容
st.subheader("配置")
col1, col2 = st.columns(2)
with col1:
    industry = st.selectbox("行业", ["餐饮", "木作", "工厂", "彩票", "酒店", "通用"])
with col2:
    length = st.radio("长度", ["短文案(150-180)", "长文案(200-300)"])

st.subheader("客户资料")
raw = st.text_area("输入资料", height=150, placeholder="粘贴客户资料...")

if st.button("生成30条文案", type="primary", use_container_width=True):
    if len(raw) < 30:
        st.error("至少30字")
    else:
        with st.spinner("生成中..."):
            prog = st.progress(0)
            st.session_state.items = []
            for i in range(30):
                try:
                    client = get_client()
                    resp = client.chat.completions.create(
                        model="moonshot-v1-8k",
                        messages=[
                            {"role": "system", "content": "你是短视频文案大师。"},
                            {"role": "user", "content": f"创作第{i+1}条文案。资料：{raw[:400]} 要求:150-180字"}
                        ],
                        max_tokens=400, temperature=0.85, timeout=30
                    )
                    content = resp.choices[0].message.content.strip()
                    wc = len(content.replace(' ', '').replace('\n', ''))
                    st.session_state.items.append({'idx': i+1, 'content': content, 'wc': wc})
                except Exception as e:
                    st.session_state.items.append({'idx': i+1, 'content': f"错误: {str(e)[:20]}", 'wc': 0})
                prog.progress((i+1)/30)
        st.rerun()

# 显示结果
if st.session_state.items:
    st.divider()
    st.subheader(f"生成结果 ({len(st.session_state.items)}条)")
    for item in st.session_state.items:
        with st.expander(f"文案 #{item['idx']} ({item['wc']}字)"):
            st.write(item['content'])
