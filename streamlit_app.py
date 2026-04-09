import streamlit as st
import re
import time
from openai import OpenAI
from sensitive_words import check_sensitive_words

st.set_page_config(page_title="文案助手", layout="wide")

# 基础配置
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
                {"role": "system", "content": "你是短视频文案大师。黄金三秒：严禁自我介绍、店名、地址。语义降维：禁用匠心/高端/专业。"},
                {"role": "user", "content": f"创作第{idx}条{ctype}文案。\n【称呼】{name}\n【资料】{raw_data[:400]}\n\n要求:\n1.字数{min_w}-{max_w}\n2.禁止自我介绍\n3.包含1个具体数字\n\n直接输出:"""}
            ],
            max_tokens=400,
            temperature=0.85,
            timeout=30
        )
        content = resp.choices[0].message.content.strip().strip('"')
        wc = len(content.replace(' ', '').replace('\n', ''))
        ok = min_w <= wc <= max_w
        return {'idx': idx, 'content': content, 'wc': wc, 'ok': ok, 'type': ctype}
    except Exception as e:
        return {'idx': idx, 'content': f"失败:{str(e)[:20]}", 'wc': 0, 'ok': False, 'type': ctype}

# 初始化
if 'items' not in st.session_state:
    st.session_state.items = []

# 页面布局
st.title("晓牧传媒文案助手 v4.1")
st.caption("AI驱动短视频文案生成工具")

# 侧边栏配置
with st.sidebar:
    st.header("配置")
    industry = st.selectbox("行业", ["餐饮", "木作", "工厂", "彩票", "酒店", "通用"])
    length = st.radio("长度", ["short", "long"], format_func=lambda x: "短文案(150-180字)" if x == "short" else "长文案(200-300字)")
    
    if st.session_state.items:
        st.divider()
        if st.button("复制全部"):
            txt = "\n\n".join([f"【{i['type']}】\n{i['content']}" for i in st.session_state.items])
            st.code(txt)

# 主区域 - 输入
st.subheader("客户资料")
raw = st.text_area("", height=120, placeholder="粘贴客户资料：出镜称呼、店铺名称、主营业务、真实故事...")

if st.button("生成30条文案", type="primary"):
    if len(raw) < 30:
        st.error("资料至少30字")
    else:
        with st.spinner("生成中..."):
            prog = st.progress(0)
            st.session_state.items = []
            for i in range(30):
                r = generate(raw, i+1, industry, length)
                st.session_state.items.append(r)
                prog.progress((i+1)/30)
        st.rerun()

# 显示结果
if st.session_state.items:
    st.divider()
    
    # 统计
    total = len(st.session_state.items)
    ok = sum(1 for i in st.session_state.items if i['ok'])
    cols = st.columns(4)
    cols[0].metric("总数", total)
    cols[1].metric("优质", ok)
    cols[2].metric("需优化", total - ok)
    cols[3].metric("失败", sum(1 for i in st.session_state.items if i['wc'] == 0))
    
    st.divider()
    
    # 文案列表 - 用expander折叠
    for item in st.session_state.items:
        status = "✅" if item['ok'] else "❌" if item['wc'] == 0 else "⚠️"
        with st.expander(f"{status} 文案 #{item['idx']} [{item['type']}] - {item['wc']}字"):
            st.write(item['content'])
            col1, col2 = st.columns([1, 4])
            with col1:
                st.button("复制", key=f"cp{item['idx']}")
