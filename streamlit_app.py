import streamlit as st
import re
import time
from openai import OpenAI
from sensitive_words import check_sensitive_words

st.set_page_config(page_title="晓牧传媒文案助手", page_icon="✨", layout="wide")

# 基础样式 - 简单有效
st.markdown("""
<style>
    .stApp { background: #f8fafc; }
    .main { max-width: 1200px; margin: 0 auto; }
    h1 { color: #1e293b !important; font-size: 1.8rem !important; }
    .stButton>button { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# 配置
INDUSTRIES = {"catering": "餐饮", "woodwork": "木作定制", "factory": "工厂/制造", "lottery": "彩票店", "hotel": "酒店/民宿", "general": "通用"}
CTYPE_COLORS = {"干货避坑": "🔴", "人设故事": "🟣", "细节特写": "🟡", "认知反转": "🟢"}

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
                {"role": "system", "content": "你是短视频文案大师。黄金三秒：严禁自我介绍、店名、地址。语义降维：禁用匠心/高端/专业，必须具象化。"},
                {"role": "user", "content": f"创作第{idx}条{ctype}文案。\n【称呼】{name}\n【资料】{raw_data[:400]}\n\n要求:\n1.字数{min_w}-{max_w}\n2.禁止自我介绍\n3.包含1个具体数字\n\n直接输出:"""}
            ],
            max_tokens=400, temperature=0.85, timeout=30
        )
        content = resp.choices[0].message.content.strip().strip('"')
        wc = len(content.replace(' ', '').replace('\n', ''))
        ok = min_w <= wc <= max_w and not re.search(r'[路街道]\s*\d+[号]', content)
        return {'idx': idx, 'content': content, 'wc': wc, 'ok': ok, 'type': ctype}
    except Exception as e:
        return {'idx': idx, 'content': f"失败:{str(e)[:20]}", 'wc': 0, 'ok': False, 'type': ctype}

# 初始化 - 确保 items 是列表
if 'items' not in st.session_state or st.session_state.items is None:
    st.session_state.items = []

# ===== 顶部标题区 =====
col_title, col_info = st.columns([3, 1])
with col_title:
    st.title("✨ 晓牧传媒文案助手")
    st.caption("AI驱动短视频文案生成工具 v4.1")

# ===== 两栏布局 =====
left_col, right_col = st.columns([1, 3])

with left_col:
    # 配置面板
    st.markdown("### ⚙️ 配置")
    
    with st.container():
        st.markdown("**行业类型**")
        industry = st.selectbox("行业", list(INDUSTRIES.keys()), format_func=lambda x: INDUSTRIES[x], index=5, label_visibility="collapsed")
    
    with st.container():
        st.markdown("**文案长度**")
        length = st.radio("长度", ["short", "long"], format_func=lambda x: "短文案 (150-180字)" if x == "short" else "长文案 (200-300字)", label_visibility="collapsed")
    
    # 内容类型说明
    with st.expander("📚 内容类型"):
        st.markdown("🔴 **干货避坑** - 揭露行业内幕")
        st.markdown("🟣 **人设故事** - 老板个人经历")
        st.markdown("🟡 **细节特写** - 产品工艺细节")
        st.markdown("🟢 **认知反转** - 颠覆常识")
    
    # 工具按钮
    if st.session_state.items and len(st.session_state.items) > 0:
        st.divider()
        if st.button("📋 复制全部", use_container_width=True):
            txt = "\n\n".join([f"【{i['type']}】\n{i['content']}" for i in st.session_state.items])
            st.code(txt, language=None)
        if st.button("🗑️ 清空结果", use_container_width=True):
            st.session_state.items = []
            st.rerun()

with right_col:
    # 输入区
    st.markdown("### 📝 客户资料")
    
    with st.container():
        raw = st.text_area("资料", height=120, placeholder="请粘贴客户资料：\n\n- 出镜称呼：王老板、李姐\n- 店铺/企业名称\n- 所在城市\n- 主营业务\n- 核心卖点/特色\n- 真实故事或经历", label_visibility="collapsed")
        
        col_input, col_btn = st.columns([4, 1])
        with col_input:
            st.caption(f"已输入 {len(raw)} 字")
        with col_btn:
            if st.button("✨ 生成30条", type="primary", use_container_width=True):
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
    
    # 结果显示
    if st.session_state.items and len(st.session_state.items) > 0:
        st.divider()
        st.markdown("### 📊 生成结果")
        
        # 统计卡片
        total = len(st.session_state.items)
        ok = sum(1 for i in st.session_state.items if i['ok'])
        fail = sum(1 for i in st.session_state.items if i['wc'] == 0)
        warn = total - ok - fail
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📊 总数", total)
        c2.metric("✅ 优质", ok, f"{ok/total*100:.0f}%")
        c3.metric("⚠️ 需优化", warn)
        c4.metric("❌ 失败", fail)
        
        st.divider()
        
        # 文案列表 - 3列网格
        items = st.session_state.items
        for row in range(0, len(items), 3):
            cols = st.columns(3)
            for cidx, col in enumerate(cols):
                idx = row + cidx
                if idx >= len(items):
                    break
                
                item = items[idx]
                with col:
                    # 卡片容器
                    with st.container():
                        icon = CTYPE_COLORS.get(item['type'], '⚪')
                        status = "✅" if item['ok'] else "❌" if item['wc'] == 0 else "⚠️"
                        
                        # 头部
                        st.markdown(f"**{icon} #{item['idx']}** {item['type']} {status}")
                        st.caption(f"{item['wc']} 字")
                        
                        # 内容
                        st.info(item['content'])
                        
                        # 操作按钮
                        bcol1, bcol2 = st.columns(2)
                        with bcol1:
                            if st.button("📋 复制", key=f"cp{idx}", use_container_width=True):
                                st.toast(f"已复制 #{item['idx']}")
                        with bcol2:
                            if not item['ok'] and st.button("🔄 重试", key=f"rt{idx}", use_container_width=True):
                                with st.spinner("重试..."):
                                    new = generate(raw, item['idx'], industry, length)
                                    st.session_state.items[idx] = new
                                    st.rerun()
