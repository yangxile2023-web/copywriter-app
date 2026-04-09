# -*- coding: utf-8 -*-
import streamlit as st
import re
import time
from openai import OpenAI
from sensitive_words import check_sensitive_words

# 页面配置
st.set_page_config(
    page_title="晓牧传媒文案助手",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .main .block-container { max-width: 1600px; padding: 1rem 2rem; }
    #MainMenu, header, footer { display: none !important; }
    
    .header-title {
        text-align: center;
        color: white;
        padding: 1rem 0 2rem 0;
    }
    .header-title h1 {
        color: white !important;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    .header-title p {
        color: rgba(255,255,255,0.85);
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
    }
    
    .panel {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .stat-item {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        line-height: 1;
    }
    .stat-label {
        font-size: 0.875rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
    
    .result-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .result-card.success { border-left-color: #22c55e; }
    .result-card.warning { border-left-color: #f59e0b; }
    .result-card.error { border-left-color: #ef4444; background: #fef2f2; }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .card-meta {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .idx-num {
        font-size: 1.5rem;
        font-weight: 800;
        color: #e2e8f0;
    }
    
    .badge {
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-primary { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
    .badge-secondary { background: #e0e7ff; color: #4338ca; }
    .badge-accent { background: #fef3c7; color: #92400e; }
    .badge-success { background: #d1fae5; color: #065f46; }
    
    .status-tag {
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .tag-ok { background: #d1fae5; color: #065f46; }
    .tag-warn { background: #fef3c7; color: #92400e; }
    .tag-err { background: #fee2e2; color: #991b1b; }
    
    .content-box {
        background: #f8fafc;
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
        line-height: 1.7;
        font-size: 0.95rem;
        color: #1e293b;
        margin-bottom: 0.75rem;
    }
    
    .issue-tag {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        color: #9a3412;
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        font-size: 0.8rem;
        margin-bottom: 0.75rem;
    }
    
    @media (max-width: 1200px) {
        .stat-grid { grid-template-columns: repeat(2, 1fr); }
    }
    
    @media (max-width: 768px) {
        .stat-grid { grid-template-columns: 1fr; }
        .header-title h1 { font-size: 1.75rem; }
    }
</style>
""", unsafe_allow_html=True)

# 配置
INDUSTRIES = {
    "catering": {"name": "餐饮", "desc": "突出食材新鲜、口味独特"},
    "woodwork": {"name": "木作定制", "desc": "强调工艺精湛、材质环保"},
    "factory": {"name": "工厂/制造", "desc": "展现生产实力、质量把控"},
    "lottery": {"name": "彩票店", "desc": "分享中奖故事、客户好运"},
    "hotel": {"name": "酒店/民宿", "desc": "描述温馨环境、贴心服务"},
    "general": {"name": "通用", "desc": "根据行业特点突出优势"}
}

CONTENT_TYPES = {
    "干货避坑": {"color": "#ef4444"},
    "人设故事": {"color": "#8b5cf6"},
    "细节特写": {"color": "#f59e0b"},
    "认知反转": {"color": "#10b981"}
}

STYLES = ["轻松", "温馨", "真诚", "励志", "接地气", "怀旧"]
ANGLES = ["个人故事", "顾客见证", "行业见解", "创业历程", "日常趣事", "价值观分享", "对比反差", "情感共鸣"]

KIMI_API_KEY = "sk-IA6qyNJFSYC8UB9RHnGHsgz24VWSrKalSnd5nTTbJNiqQ2uu"

@st.cache_resource
def get_client():
    return OpenAI(api_key=KIMI_API_KEY, base_url="https://api.moonshot.cn/v1")

SYSTEM_PROMPT = """你是短视频文案大师。

【黄金三秒】严禁前3秒出现自我介绍、店名、地址。开头必须用利益/冲突/悬念/扎心。
【语义降维】严禁:匠心/高端/专业/品质。必须具象化，如"食材新鲜"→"龙虾腮白肉肥"。"""

TEMPLATES = {
    "干货避坑": ["别再交这种智商税了", "今天说个得罪人的真相", "行业没人敢说的秘密"],
    "人设故事": ["做了15年，说说心里话", "从欠债到翻身就这一步", "那个决定改变了我一生"],
    "细节特写": ["你看这个细节没人注意", "花3天就为这1毫米", "有人笑我傻看完沉默了"],
    "认知反转": ["你以为的其实是错的", "打破常识这行不是这么做的", "这真相可能得罪同行"]
}

def generate(raw_data, config, industry, length, retries=3):
    name = re.search(r'出镜称呼[：:]\s*(\S+)', raw_data)
    name = name.group(1) if name else "老板"
    min_w, max_w = (150, 180) if length == "short" else (200, 300)
    
    ctypes = list(CONTENT_TYPES.keys())
    ctype = ctypes[(config['idx'] - 1) % 4]
    hook = TEMPLATES[ctype][(config['idx'] - 1) // 4 % 3]
    
    for attempt in range(retries):
        try:
            client = get_client()
            resp = client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"""创作第{config['idx']}条文案。

【类型】{ctype}
【开头】{hook}
【称呼】{name}
【资料】{raw_data[:500]}

要求:
1.字数{min_w}-{max_w}
2.必须用上述开头，禁止自我介绍
3."{name}"不超过2次
4.包含1个具体数字或细节

直接输出文案:"""}
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
            
            return {
                'idx': config['idx'], 'content': content, 'wc': wc,
                'ok': ok, 'len': length, 'type': ctype, 'hook': hook,
                'issues': issues, 'style': config['style'], 'angle': config['angle']
            }
        except Exception as e:
            if attempt == retries - 1:
                return {
                    'idx': config['idx'], 'content': f"生成失败: {str(e)[:30]}",
                    'wc': 0, 'ok': False, 'len': length, 'type': ctype,
                    'hook': hook, 'issues': ["API错误"],
                    'style': config['style'], 'angle': config['angle']
                }
            time.sleep(1)
    return None

def main():
    # 初始化
    for k, v in [('items', []), ('raw', ''), ('gen', False)]:
        if k not in st.session_state:
            st.session_state[k] = v
    
    # 头部
    st.markdown('<div class="header-title"><h1>晓牧传媒文案助手</h1><p>AI 驱动短视频文案生成工具 v4.1</p></div>', unsafe_allow_html=True)
    
    # 使用container控制宽度
    main_container = st.container()
    
    with main_container:
        # 第一行：配置 + 输入
        cfg_col, input_col = st.columns([1, 3])
        
        with cfg_col:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown("#### 配置")
            
            industry = st.selectbox("行业", list(INDUSTRIES.keys()), 
                                   format_func=lambda x: INDUSTRIES[x]['name'], index=5)
            st.caption(INDUSTRIES[industry]['desc'])
            
            st.divider()
            length = st.radio("长度", ["short", "long"],
                            format_func=lambda x: "短文案 (150-180字)" if x == "short" else "长文案 (200-300字)")
            
            with st.expander("内容类型"):
                for t in CONTENT_TYPES:
                    st.markdown(f"**{t}**: {t}")
            
            if st.session_state.items:
                st.divider()
                if st.button("检测敏感词", use_container_width=True):
                    n = sum(len(check_sensitive_words(i.get('content', ''))) for i in st.session_state.items)
                    st.error(f"发现 {n} 个敏感词") if n else st.success("无敏感词")
                if st.button("复制全部", use_container_width=True):
                    txt = "\n\n".join([f"【{i['type']}】\n{i['content']}" for i in st.session_state.items])
                    st.code(txt)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with input_col:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown("#### 客户资料")
            
            raw = st.text_area("资料", height=120,
                              placeholder="粘贴客户资料（建议100字以上）:\n\n- 出镜称呼\n- 店铺名称\n- 所在城市\n- 主营业务\n- 核心卖点\n- 真实故事",
                              label_visibility="collapsed")
            
            c1, c2 = st.columns([5, 1])
            with c1:
                st.caption(f"已输入 {len(raw)} 字")
            with c2:
                if st.button("生成30条", type="primary", disabled=st.session_state.gen, use_container_width=True):
                    if len(raw) < 30:
                        st.error("资料至少30字")
                    else:
                        st.session_state.gen = True
                        st.session_state.raw = raw
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 生成处理
        if st.session_state.gen and not st.session_state.items:
            with st.spinner("生成中..."):
                cfgs = [{'idx': i+1, 'style': STYLES[i%6], 'angle': ANGLES[i%8]} for i in range(30)]
                prog = st.progress(0)
                for i, cfg in enumerate(cfgs):
                    r = generate(st.session_state.raw, cfg, industry, length)
                    if r:
                        st.session_state.items.append(r)
                    prog.progress((i+1)/30, f"{i+1}/30")
                prog.empty()
            st.session_state.gen = False
            st.rerun()
        
        # 结果显示
        if st.session_state.items:
            # 统计
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            total = len(st.session_state.items)
            ok = sum(1 for i in st.session_state.items if i['ok'])
            fail = sum(1 for i in st.session_state.items if i['wc'] == 0)
            warn = total - ok - fail
            
            stats_html = f'''
            <div class="stat-grid">
                <div class="stat-item"><div class="stat-value">{total}</div><div class="stat-label">总数</div></div>
                <div class="stat-item"><div class="stat-value" style="color:#22c55e">{ok}</div><div class="stat-label">优质</div></div>
                <div class="stat-item"><div class="stat-value" style="color:#f59e0b">{warn}</div><div class="stat-label">需优化</div></div>
                <div class="stat-item"><div class="stat-value" style="color:#ef4444">{fail}</div><div class="stat-label">失败</div></div>
            </div>
            '''
            st.markdown(stats_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 文案列表 - 使用3列网格
            st.markdown('<div class="panel"><h4>生成结果</h4>', unsafe_allow_html=True)
            
            # 将30条分成每行3个
            items = st.session_state.items
            for row_idx in range(0, len(items), 3):
                cols = st.columns(3)
                for col_idx in range(3):
                    idx = row_idx + col_idx
                    if idx >= len(items):
                        break
                    
                    item = items[idx]
                    with cols[col_idx]:
                        is_fail = item['wc'] == 0
                        is_warn = not item['ok'] and not is_fail
                        card_cls = "error" if is_fail else ("warning" if is_warn else "success")
                        ctype_color = CONTENT_TYPES.get(item['type'], {}).get('color', '#667eea')
                        
                        status = ('<span class="status-tag tag-ok">优质</span>' if item['ok'] 
                                 else '<span class="status-tag tag-err">失败</span>' if is_fail 
                                 else '<span class="status-tag tag-warn">需优化</span>')
                        
                        len_badge = (f'<span class="badge badge-success">长 {item["wc"]}字</span>' if item['len'] == 'long'
                                    else f'<span class="badge badge-accent">短 {item["wc"]}字</span>')
                        
                        card = f'''
                        <div class="result-card {card_cls}">
                            <div class="card-header">
                                <div class="card-meta">
                                    <span class="idx-num">#{item['idx']}</span>
                                    <span class="badge" style="background:{ctype_color};color:white">{item['type']}</span>
                                    {len_badge}
                                </div>
                                {status}
                            </div>
                            <div class="content-box">{item['content']}</div>
                        '''
                        st.markdown(card, unsafe_allow_html=True)
                        
                        if item.get('issues'):
                            st.markdown(f'<div class="issue-tag">⚠ {" · ".join(item["issues"])}</div>', unsafe_allow_html=True)
                        
                        b1, b2, b3 = st.columns([1, 1, 1])
                        with b1:
                            if st.button("复制", key=f"cp{idx}", use_container_width=True):
                                st.toast(f"已复制 #{item['idx']}")
                        with b2:
                            if (is_fail or item['wc'] < 120) and st.button("重试", key=f"rt{idx}", use_container_width=True):
                                with st.spinner("重试..."):
                                    new = generate(st.session_state.raw, 
                                                  {'idx': item['idx'], 'style': item['style'], 'angle': item['angle']},
                                                  industry, item['len'])
                                    if new:
                                        st.session_state.items[idx] = new
                                        st.rerun()
                        with b3:
                            if item['ok']:
                                tgt = 'long' if item['len'] == 'short' else 'short'
                                lbl = "转长" if tgt == 'long' else "转短"
                                if st.button(lbl, key=f"sw{idx}", use_container_width=True):
                                    with st.spinner("切换..."):
                                        new = generate(st.session_state.raw,
                                                      {'idx': item['idx'], 'style': item['style'], 'angle': item['angle']},
                                                      industry, tgt)
                                        if new:
                                            st.session_state.items[idx] = new
                                            st.rerun()
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
