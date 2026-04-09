# -*- coding: utf-8 -*-
import streamlit as st
import re
import time
from openai import OpenAI
from sensitive_words import check_sensitive_words

st.set_page_config(page_title="晓牧传媒文案助手", page_icon="✨", layout="wide")

# 深色主题CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', 'Noto Sans SC', sans-serif !important; }
    
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%) !important;
    }
    
    .main .block-container {
        max-width: 1400px;
        padding: 2rem;
    }
    
    #MainMenu, header, footer { display: none !important; }
    
    /* 头部 */
    .app-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
    }
    
    .app-header h1 {
        color: white !important;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .app-header p {
        color: rgba(255,255,255,0.6);
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    
    /* 玻璃态卡片 */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* 输入框样式 */
    .stTextArea textarea {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 16px !important;
        color: white !important;
        padding: 1.2rem !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }
    
    .stTextArea textarea::placeholder {
        color: rgba(255,255,255,0.4) !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* 选择器 */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    /* 按钮 */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 1rem 2rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: white !important;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s !important;
    }
    
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.5) !important;
    }
    
    /* 标签样式 */
    .content-tag {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 0.5rem;
        color: white;
    }
    
    .tag-red { background: linear-gradient(135deg, #ff6b6b, #ee5a5a); }
    .tag-purple { background: linear-gradient(135deg, #a855f7, #9333ea); }
    .tag-yellow { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #1a1a2e; }
    .tag-green { background: linear-gradient(135deg, #22c55e, #16a34a); }
    .tag-blue { background: linear-gradient(135deg, #3b82f6, #2563eb); }
    
    /* 统计卡片 */
    .stat-card {
        background: rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 1.25rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        color: rgba(255,255,255,0.6);
        font-size: 0.9rem;
        margin-top: 0.25rem;
    }
    
    /* 结果卡片 */
    .result-card {
        background: rgba(255,255,255,0.03);
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.08);
        transition: all 0.3s;
    }
    
    .result-card:hover {
        background: rgba(255,255,255,0.06);
        border-color: rgba(255,255,255,0.15);
        transform: translateY(-2px);
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    
    .card-meta {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    
    .idx-badge {
        width: 36px;
        height: 36px;
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: rgba(255,255,255,0.5);
        font-size: 0.9rem;
    }
    
    .content-text {
        background: rgba(0,0,0,0.2);
        border-radius: 12px;
        padding: 1rem;
        color: rgba(255,255,255,0.9);
        line-height: 1.8;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }
    
    .status-badge {
        padding: 0.35rem 0.75rem;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .status-ok { background: rgba(34, 197, 94, 0.2); color: #4ade80; }
    .status-warn { background: rgba(251, 191, 36, 0.2); color: #fbbf24; }
    .status-err { background: rgba(239, 68, 68, 0.2); color: #f87171; }
    
    .issue-tag {
        background: rgba(251, 191, 36, 0.1);
        border: 1px solid rgba(251, 191, 36, 0.3);
        color: #fbbf24;
        padding: 0.5rem 0.75rem;
        border-radius: 8px;
        font-size: 0.8rem;
        margin-bottom: 0.75rem;
    }
    
    .action-btn {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.85rem !important;
    }
    
    .action-btn:hover {
        background: rgba(255,255,255,0.15) !important;
    }
    
    /* 折叠面板 */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: white !important;
    }
    
    /* 分割线 */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        margin: 1.5rem 0;
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(255,255,255,0.05);
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: rgba(255,255,255,0.6) !important;
        border-radius: 8px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(102, 126, 234, 0.3) !important;
        color: white !important;
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
    "干货避坑": {"color": "#ff6b6b", "class": "tag-red"},
    "人设故事": {"color": "#a855f7", "class": "tag-purple"},
    "细节特写": {"color": "#fbbf24", "class": "tag-yellow"},
    "认知反转": {"color": "#22c55e", "class": "tag-green"}
}

TEMPLATES = {
    "干货避坑": ["别再交这种智商税了", "今天说个得罪人的真相", "行业没人敢说的秘密"],
    "人设故事": ["做了15年，说说心里话", "从欠债到翻身就这一步", "那个决定改变了我一生"],
    "细节特写": ["你看这个细节没人注意", "花3天就为这1毫米", "有人笑我傻看完沉默了"],
    "认知反转": ["你以为的其实是错的", "打破常识这行不是这么做的", "这真相可能得罪同行"]
}

KIMI_KEY = "sk-IA6qyNJFSYC8UB9RHnGHsgz24VWSrKalSnd5nTTbJNiqQ2uu"

@st.cache_resource
def get_client():
    return OpenAI(api_key=KIMI_KEY, base_url="https://api.moonshot.cn/v1")

def generate(raw_data, idx, industry, length, retries=3):
    name = re.search(r'出镜称呼[：:]\s*(\S+)', raw_data)
    name = name.group(1) if name else "老板"
    min_w, max_w = (150, 180) if length == "short" else (200, 300)
    
    ctypes = list(CONTENT_TYPES.keys())
    ctype = ctypes[(idx - 1) % 4]
    hook = TEMPLATES[ctype][(idx - 1) // 4 % 3]
    
    for _ in range(retries):
        try:
            client = get_client()
            resp = client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {"role": "system", "content": "你是短视频文案大师。黄金三秒：严禁自我介绍、店名、地址。语义降维：禁用匠心/高端/专业，必须具象化。"},
                    {"role": "user", "content": f"创作第{idx}条文案。\n\n【类型】{ctype}\n【开头】{hook}\n【称呼】{name}\n【资料】{raw_data[:500]}\n\n要求:\n1.字数{min_w}-{max_w}\n2.必须用上述开头，禁止自我介绍\n3.\"{name}\"不超过2次\n4.包含1个具体数字或细节\n\n直接输出文案:"""}
                ],
                max_tokens=400,
                temperature=0.85,
                timeout=30
            )
            content = resp.choices[0].message.content.strip().strip('"')
            wc = len(content.replace(' ', '').replace('\n', ''))
            nc = content.count(name)
            addr = bool(re.search(r'[路街道]\s*\d+[号]', content))
            intro = bool(re.search(r'^(大家好|我是|我叫|我们店)', content))
            sens = check_sensitive_words(content)
            
            issues = []
            if wc < min_w: issues.append("字数不足")
            elif wc > max_w: issues.append("字数超标")
            if addr: issues.append("有具体地址")
            if intro: issues.append("开头有自我介绍")
            if nc > 2: issues.append("称呼过多")
            if sens: issues.append("有敏感词")
            
            ok = min_w <= wc <= max_w and not addr and not intro and nc <= 2 and not sens
            return {'idx': idx, 'content': content, 'wc': wc, 'ok': ok, 'len': length, 'type': ctype, 'hook': hook, 'issues': issues}
        except Exception as e:
            if _ == retries - 1:
                return {'idx': idx, 'content': f"生成失败: {str(e)[:30]}", 'wc': 0, 'ok': False, 'len': length, 'type': ctype, 'hook': hook, 'issues': ["API错误"]}
            time.sleep(1)
    return None

def main():
    # 初始化
    if 'items' not in st.session_state:
        st.session_state.items = []
    if 'gen' not in st.session_state:
        st.session_state.gen = False
    
    # 头部
    st.markdown('<div class="app-header"><h1>晓牧传媒文案助手</h1><p>AI 驱动短视频文案生成工具</p></div>', unsafe_allow_html=True)
    
    # 使用tab组织界面
    tab1, tab2, tab3 = st.tabs(["生成文案", "批量管理", "设置"])
    
    with tab1:
        # 输入区
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("**行业类型**")
            industry = st.selectbox("行业", list(INDUSTRIES.keys()), format_func=lambda x: INDUSTRIES[x], index=5, label_visibility="collapsed")
            
            st.markdown("<div style='margin:1rem 0;'></div>", unsafe_allow_html=True)
            
            st.markdown("**文案长度**")
            length = st.radio("长度", ["short", "long"], format_func=lambda x: "短文案 150-180字" if x == "short" else "长文案 200-300字", label_visibility="collapsed")
        
        with col2:
            st.markdown("**客户资料**")
            raw = st.text_area("资料", height=140, placeholder="粘贴客户资料:\n\n- 出镜称呼: 王老板、李姐\n- 店铺名称、所在城市\n- 主营业务、核心卖点\n- 真实故事或经历", label_visibility="collapsed")
            
            c1, c2 = st.columns([4, 1])
            with c1:
                st.caption(f"已输入 {len(raw)} 字")
            with c2:
                if st.button("✨ 生成30条", type="primary", use_container_width=True, disabled=st.session_state.gen):
                    if len(raw) < 30:
                        st.error("资料至少30字")
                    else:
                        st.session_state.gen = True
                        st.session_state.raw_data = raw
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 生成
        if st.session_state.gen and not st.session_state.items:
            with st.spinner("正在生成..."):
                prog = st.progress(0)
                for i in range(30):
                    r = generate(st.session_state.raw_data, i+1, industry, length)
                    if r:
                        st.session_state.items.append(r)
                    prog.progress((i+1)/30, f"{i+1}/30")
                prog.empty()
            st.session_state.gen = False
            st.rerun()
        
        # 结果
        if st.session_state.items:
            # 统计
            total = len(st.session_state.items)
            ok = sum(1 for i in st.session_state.items if i['ok'])
            fail = sum(1 for i in st.session_state.items if i['wc'] == 0)
            warn = total - ok - fail
            
            cols = st.columns(4)
            stats = [(total, "总数", "#667eea"), (ok, "优质", "#22c55e"), (warn, "需优化", "#fbbf24"), (fail, "失败", "#ef4444")]
            for col, (val, lbl, clr) in zip(cols, stats):
                with col:
                    st.markdown(f'<div class="stat-card"><div class="stat-value" style="background: linear-gradient(135deg, {clr}, {clr}aa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{val}</div><div class="stat-label">{lbl}</div></div>', unsafe_allow_html=True)
            
            st.markdown("<div style='margin:1.5rem 0;'></div>", unsafe_allow_html=True)
            
            # 文案网格 3列
            items = st.session_state.items
            for row in range(0, len(items), 3):
                cols = st.columns(3)
                for cidx, col in enumerate(cols):
                    idx = row + cidx
                    if idx >= len(items):
                        break
                    
                    item = items[idx]
                    with col:
                        is_fail = item['wc'] == 0
                        is_warn = not item['ok'] and not is_fail
                        ct = CONTENT_TYPES.get(item['type'], {})
                        
                        status = f'<span class="status-badge {"status-ok" if item["ok"] else "status-err" if is_fail else "status-warn"}">{"优质" if item["ok"] else "失败" if is_fail else "需优化"}</span>'
                        
                        card = f'''
                        <div class="result-card">
                            <div class="card-header">
                                <div class="card-meta">
                                    <div class="idx-badge">{item['idx']}</div>
                                    <span class="content-tag {ct.get('class', 'tag-blue')}">{item['type']}</span>
                                    <span style="color:rgba(255,255,255,0.5);font-size:0.85rem;">{item['wc']}字</span>
                                </div>
                                {status}
                            </div>
                            <div class="content-text">{item['content']}</div>
                        '''
                        st.markdown(card, unsafe_allow_html=True)
                        
                        if item.get('issues'):
                            st.markdown(f'<div class="issue-tag">⚠ {" · ".join(item["issues"])}</div>', unsafe_allow_html=True)
                        
                        b1, b2, b3 = st.columns(3)
                        with b1:
                            if st.button("复制", key=f"cp{idx}", use_container_width=True):
                                st.toast(f"已复制 #{item['idx']}")
                        with b2:
                            if (is_fail or item['wc'] < 120) and st.button("重试", key=f"rt{idx}", use_container_width=True):
                                with st.spinner("重试..."):
                                    new = generate(st.session_state.raw_data, item['idx'], industry, item['len'])
                                    if new:
                                        st.session_state.items[idx] = new
                                        st.rerun()
                        with b3:
                            if item['ok'] and st.button("转长" if item['len']=='short' else "转短", key=f"sw{idx}", use_container_width=True):
                                with st.spinner("切换..."):
                                    new = generate(st.session_state.raw_data, item['idx'], industry, 'long' if item['len']=='short' else 'short')
                                    if new:
                                        st.session_state.items[idx] = new
                                        st.rerun()
                        
                        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 批量操作")
        if st.session_state.items:
            if st.button("检测全部敏感词"):
                n = sum(len(check_sensitive_words(i.get('content', ''))) for i in st.session_state.items)
                st.error(f"发现 {n} 个敏感词") if n else st.success("无敏感词")
            if st.button("复制全部文案"):
                txt = "\n\n".join([f"【{i['type']}】\n{i['content']}" for i in st.session_state.items])
                st.code(txt)
            if st.button("清空结果"):
                st.session_state.items = []
                st.rerun()
        else:
            st.info("先生成文案")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 关于")
        st.markdown("- **版本**: v4.1")
        st.markdown("- **功能**: AI生成30条短视频文案")
        st.markdown("- **特点**: 黄金三秒、语义降维、内容分类")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
