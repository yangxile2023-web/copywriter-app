# -*- coding: utf-8 -*-
import streamlit as st
import re
import time
from openai import OpenAI
from sensitive_words import check_sensitive_words

st.set_page_config(page_title="文案助手", layout="wide")

# 配置
INDUSTRIES = {
    "catering": "餐饮",
    "woodwork": "木作定制", 
    "factory": "工厂/制造",
    "lottery": "彩票店",
    "hotel": "酒店/民宿",
    "general": "通用"
}

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

# 页面布局
st.title("晓牧传媒文案助手 v4.2")
st.caption("AI驱动短视频文案生成工具")

# 侧边栏
with st.sidebar:
    st.header("配置")
    industry = st.selectbox("行业", list(INDUSTRIES.keys()), format_func=lambda x: INDUSTRIES[x])
    length = st.radio("长度", ["short", "long"], format_func=lambda x: "短文案(150-180)" if x == "short" else "长文案(200-300)")
    
    if st.session_state.items:
        st.divider()
        if st.button("复制全部"):
            txt = "\n\n".join([f"【{i['type']}】\n{i['content']}" for i in st.session_state.items])
            st.code(txt)
        if st.button("清空"):
            st.session_state.items = []
            st.rerun()

# 主内容
st.subheader("客户资料")
raw = st.text_area("资料", height=120, placeholder="粘贴客户资料：出镜称呼、店铺名称、主营业务、真实故事...")

if st.button("生成30条文案", type="primary"):
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

# 显示结果
if st.session_state.items:
    st.divider()
    
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
    
    st.divider()
    
    # 文案列表
    for item in items:
        status = "优质" if item['ok'] else "失败" if item['wc'] == 0 else "需优化"
        with st.expander(f"文案 #{item['idx']} [{item['type']}] - {status} ({item['wc']}字)"):
            st.write(item['content'])
            col1, col2 = st.columns([1, 4])
            with col1:
                st.button("复制", key=f"cp{item['idx']}")
