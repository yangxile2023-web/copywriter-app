import streamlit as st
import re
import hashlib
import time
from openai import OpenAI
from sensitive_words import check_sensitive_words

# 页面配置
st.set_page_config(
    page_title="晓牧传媒文案助手 v4.1",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 简化的CSS样式
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main .block-container {
        max-width: 1400px;
        padding: 2rem;
    }
    #MainMenu, header, footer {display: none !important;}
    
    .glass-box {
        background: rgba(255,255,255,0.95);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    
    .app-title {
        text-align: center;
        color: white;
        padding: 20px 0 30px 0;
    }
    .app-title h1 {
        color: white !important;
        font-size: 36px;
        margin-bottom: 8px;
    }
    
    .stat-box {
        background: white;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .stat-num {
        font-size: 28px;
        font-weight: bold;
    }
    .stat-label {
        color: #666;
        font-size: 13px;
    }
    
    .copy-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .copy-card.success {border-left-color: #10b981;}
    .copy-card.warning {border-left-color: #f59e0b;}
    .copy-card.error {border-left-color: #ef4444; background: #fef2f2;}
    
    .tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 6px;
    }
    .tag-p {background: linear-gradient(135deg, #667eea, #764ba2); color: white;}
    .tag-b {background: #e0e7ff; color: #4338ca;}
    .tag-o {background: #fef3c7; color: #92400e;}
    .tag-g {background: #d1fae5; color: #065f46;}
    
    .status-b {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .status-ok {background: #d1fae5; color: #065f46;}
    .status-warn {background: #fef3c7; color: #92400e;}
    .status-err {background: #fee2e2; color: #991b1b;}
    
    .copy-text {
        background: #f8fafc;
        border-radius: 8px;
        padding: 12px;
        margin: 10px 0;
        border: 1px solid #e2e8f0;
        line-height: 1.6;
        font-size: 14px;
    }
    
    .issue-box {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 12px;
        color: #9a3412;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 密码验证
def check_password():
    return True

# 配置数据
INDUSTRIES = {
    "catering": {"name": "餐饮", "desc": "突出食材新鲜、口味独特"},
    "woodwork": {"name": "木作定制", "desc": "强调工艺精湛、材质环保"},
    "factory": {"name": "工厂/制造", "desc": "展现生产实力、质量把控"},
    "lottery": {"name": "彩票店", "desc": "分享中奖故事、客户好运"},
    "hotel": {"name": "酒店/民宿", "desc": "描述温馨环境、贴心服务"},
    "general": {"name": "通用", "desc": "根据行业特点突出优势"}
}

CONTENT_TYPES = {
    "干货避坑": {"color": "#ef4444", "desc": "揭露行业内幕、避坑指南"},
    "人设故事": {"color": "#8b5cf6", "desc": "老板个人经历、创业故事"},
    "细节特写": {"color": "#f59e0b", "desc": "产品/工艺的具体细节"},
    "认知反转": {"color": "#10b981", "desc": "颠覆常识、打破认知"}
}

STYLES = ["轻松", "温馨", "真诚", "励志", "接地气", "怀旧"]
ANGLES = ["个人故事", "顾客见证", "行业见解", "创业历程", "日常趣事", "价值观分享", "对比反差", "情感共鸣"]

KIMI_API_KEY = "sk-IA6qyNJFSYC8UB9RHnGHsgz24VWSrKalSnd5nTTbJNiqQ2uu"

@st.cache_resource
def get_kimi_client():
    return OpenAI(api_key=KIMI_API_KEY, base_url="https://api.moonshot.cn/v1")

SYSTEM_PROMPT = """你是一位短视频文案大师。

【黄金三秒原则】
1. 严禁前3秒出现：自我介绍("大家好我是XX")、店名、经营地址
2. 开头必须用"利益、冲突、悬念、扎心"四选一

【语义降维】
严禁使用：匠心、坚守、高端、高效、专业、品质
必须转化为具象描述，如"食材新鲜"→"龙虾在水里打架，腮白肉肥"""

CONTENT_TEMPLATES = {
    "干货避坑": {"hooks": ["别再交这种智商税了", "今天说个得罪人的真相", "这个行业没人敢说的秘密"]},
    "人设故事": {"hooks": ["做了15年，我想说说心里话", "从欠债到翻身，就这一步", "当年那个决定改变了我一生"]},
    "细节特写": {"hooks": ["你看这个细节一般人不会注意", "花了3天就为这1毫米", "有人笑我傻看完沉默了"]},
    "认知反转": {"hooks": ["你以为的其实是错的", "打破常识这行不是这么做的", "这个真相可能会得罪同行"]}
}

def generate_single_copywrite(raw_data, config, industry="general", length="short", retries=3):
    industry_info = INDUSTRIES.get(industry, INDUSTRIES["general"])
    name_match = re.search(r'出镜称呼[：:]\s*(\S+)', raw_data)
    name = name_match.group(1) if name_match else "老板"
    min_words, max_words = (150, 180) if length == "short" else (200, 300)
    
    content_types = list(CONTENT_TYPES.keys())
    content_type = content_types[(config['idx'] - 1) % 4]
    template = CONTENT_TEMPLATES[content_type]
    hook = template["hooks"][(config['idx'] - 1) // 4 % len(template["hooks"])]
    
    for attempt in range(retries):
        prompt = f"""创作第{config['idx']}条短视频文案。

【内容类型】{content_type}
【强制开头】{hook}
【出镜称呼】{name}
【客户资料】{raw_data[:500]}

【硬性要求】
1. 字数：{min_words}-{max_words}字
2. 开头必须用上述"强制开头"或类似钩子，禁止自我介绍
3. 称呼"{name}"不超过2次，多用"我""咱"
4. 必须包含至少1个具体数字或感官细节

直接输出文案："""
        
        try:
            client = get_kimi_client()
            response = client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=450,
                temperature=0.85,
                timeout=35
            )
            content = response.choices[0].message.content.strip()
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            
            word_count = len(content.replace(' ', '').replace('\n', ''))
            name_count = content.count(name)
            has_address = bool(re.search(r'[路街道]\s*\d+[号]', content))
            has_self_intro = bool(re.search(r'^(大家好|我是|我叫|我们店|我们这里是)', content))
            sensitive = check_sensitive_words(content)
            
            issues = []
            if word_count < min_words: issues.append("字数不足")
            elif word_count > max_words: issues.append("字数超标")
            if has_address: issues.append("有具体地址")
            if has_self_intro: issues.append("开头有自我介绍")
            if name_count > 2: issues.append("称呼过多")
            if sensitive: issues.append("敏感词")
            
            quality_pass = (min_words <= word_count <= max_words and 
                          not has_address and not has_self_intro and 
                          name_count <= 2 and len(sensitive) == 0)
            
            return {
                'index': config['idx'], 'content': content, 'word_count': word_count,
                'quality_pass': quality_pass, 'length_type': length, 
                'style': config['style'], 'angle': config['angle'],
                'content_type': content_type, 'hook': hook, 'issues': issues
            }
        except Exception as e:
            if attempt == retries - 1:
                return {
                    'index': config['idx'], 
                    'content': f"生成失败: {str(e)[:40]}", 
                    'word_count': 0, 'quality_pass': False, 
                    'length_type': length, 'style': config['style'], 
                    'angle': config['angle'], 'content_type': content_type,
                    'hook': hook, 'issues': ["API错误"]
                }
            time.sleep(1.5)
    return None

def main():
    if not check_password():
        st.stop()
    
    # 初始化
    for key in ['copywrites', 'raw_data_cache', 'is_generating']:
        if key not in st.session_state:
            st.session_state[key] = [] if key == 'copywrites' else ("" if key == 'raw_data_cache' else False)
    
    # 标题
    st.markdown('<div class="app-title"><h1>晓牧传媒文案助手</h1><p>AI 驱动的短视频文案生成工具 v4.1</p></div>', unsafe_allow_html=True)
    
    # 布局
    col_left, col_right = st.columns([300, 1])
    
    # 左侧控制面板
    with col_left:
        st.markdown('<div class="glass-box">', unsafe_allow_html=True)
        st.markdown("### 配置")
        
        industry = st.selectbox(
            "行业",
            options=list(INDUSTRIES.keys()),
            format_func=lambda x: f"{INDUSTRIES[x]['name']}",
            index=5,
            label_visibility="collapsed"
        )
        st.caption(INDUSTRIES[industry]['desc'])
        
        st.divider()
        st.markdown("**文案长度**")
        length = st.radio(
            "长度",
            ["short", "long"],
            format_func=lambda x: "短文案 (150-180字)" if x == "short" else "长文案 (200-300字)",
            index=0,
            label_visibility="collapsed"
        )
        
        with st.expander("内容类型说明"):
            for ctype, info in CONTENT_TYPES.items():
                st.markdown(f"**{ctype}**: {info['desc']}")
        
        if st.session_state.copywrites:
            st.divider()
            st.markdown("**工具**")
            if st.button("检测敏感词", use_container_width=True):
                total = sum(len(check_sensitive_words(c.get('content', ''))) for c in st.session_state.copywrites)
                if total:
                    st.error(f"发现 {total} 个敏感词")
                else:
                    st.success("未检测到敏感词")
            
            if st.button("复制全部", use_container_width=True):
                text = "\n\n".join([f"【{c['content_type']}】\n{c['content']}" for c in st.session_state.copywrites])
                st.code(text)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 右侧主内容
    with col_right:
        # 输入区
        st.markdown('<div class="glass-box">', unsafe_allow_html=True)
        st.markdown("### 客户资料")
        
        raw_data = st.text_area(
            "资料",
            height=140,
            placeholder="请粘贴客户资料（建议100字以上）：\n\n- 出镜称呼：王老板、李姐\n- 店铺/企业名称\n- 所在城市\n- 主营业务\n- 核心卖点/特色\n- 真实故事或经历",
            label_visibility="collapsed"
        )
        
        c1, c2 = st.columns([4, 1])
        with c1:
            st.caption(f"已输入 {len(raw_data)} 字")
        with c2:
            if st.button("生成30条", type="primary", use_container_width=True, disabled=st.session_state.is_generating):
                if len(raw_data) < 30:
                    st.error("请填写完整资料（至少30字）")
                else:
                    st.session_state.is_generating = True
                    st.session_state.raw_data_cache = raw_data
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 生成处理
        if st.session_state.is_generating and not st.session_state.copywrites:
            with st.spinner("正在生成文案..."):
                configs = [{'idx': i+1, 'style': STYLES[i%6], 'angle': ANGLES[i%8]} for i in range(30)]
                st.session_state.copywrites = []
                progress = st.progress(0)
                
                for i, config in enumerate(configs):
                    result = generate_single_copywrite(st.session_state.raw_data_cache, config, industry, length)
                    if result:
                        st.session_state.copywrites.append(result)
                    progress.progress((i + 1) / 30, text=f"生成中... {i+1}/30")
                
                progress.empty()
            
            st.session_state.is_generating = False
            st.rerun()
        
        # 结果显示
        if st.session_state.copywrites:
            # 统计
            total = len(st.session_state.copywrites)
            passed = sum(1 for c in st.session_state.copywrites if c['quality_pass'])
            failed = sum(1 for c in st.session_state.copywrites if c['word_count'] == 0)
            need_opt = total - passed - failed
            
            st.markdown('<div class="glass-box">', unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            stats = [
                (c1, "总数", total, "#667eea"),
                (c2, "优质", passed, "#10b981"),
                (c3, "需优化", need_opt, "#f59e0b"),
                (c4, "失败", failed, "#ef4444")
            ]
            for col, label, value, color in stats:
                with col:
                    st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:{color}">{value}</div><div class="stat-label">{label}</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 文案列表
            st.markdown('<div class="glass-box">', unsafe_allow_html=True)
            st.markdown("### 生成结果")
            
            for item in st.session_state.copywrites:
                is_fail = item['word_count'] == 0
                is_warning = not item['quality_pass'] and not is_fail
                card_class = "error" if is_fail else ("warning" if is_warning else "success")
                
                ct_color = CONTENT_TYPES.get(item['content_type'], {}).get('color', '#667eea')
                
                status_html = ('<span class="status-b status-ok">优质</span>' if item['quality_pass'] 
                              else '<span class="status-b status-err">失败</span>' if is_fail 
                              else '<span class="status-b status-warn">需优化</span>')
                
                len_html = (f'<span class="tag tag-g">长 {item["word_count"]}字</span>' if item['length_type'] == 'long' 
                           else f'<span class="tag tag-o">短 {item["word_count"]}字</span>')
                
                # 卡片头部
                header_html = f'''
                <div class="copy-card {card_class}">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; flex-wrap:wrap; gap:8px;">
                        <div>
                            <span style="font-size:20px; font-weight:bold; color:#cbd5e1; margin-right:8px;">#{item['index']}</span>
                            <span class="tag" style="background:{ct_color}; color:white;">{item['content_type']}</span>
                            {len_html}
                        </div>
                        {status_html}
                    </div>
                    <div class="copy-text">{item['content']}</div>
                '''
                st.markdown(header_html, unsafe_allow_html=True)
                
                # 问题提示
                if item.get('issues'):
                    st.markdown(f'<div class="issue-box">⚠ {" · ".join(item["issues"])}</div>', unsafe_allow_html=True)
                
                # 操作按钮
                bc1, bc2, bc3 = st.columns([1, 1, 2])
                with bc1:
                    if st.button("复制", key=f"cp_{item['index']}", use_container_width=True):
                        st.toast(f"已复制 #{item['index']}")
                
                with bc2:
                    if (is_fail or item['word_count'] < 120) and st.button("重试", key=f"rt_{item['index']}", use_container_width=True):
                        with st.spinner("重试中..."):
                            new_item = generate_single_copywrite(
                                st.session_state.raw_data_cache,
                                {'idx': item['index'], 'style': item['style'], 'angle': item['angle']},
                                industry, item['length_type']
                            )
                            if new_item:
                                st.session_state.copywrites[item['index']-1] = new_item
                                st.rerun()
                
                with bc3:
                    if item['quality_pass']:
                        target = 'long' if item['length_type'] == 'short' else 'short'
                        btn = "转长文案" if target == 'long' else "转短文案"
                        if st.button(btn, key=f"sw_{item['index']}", use_container_width=True):
                            with st.spinner("切换中..."):
                                new_item = generate_single_copywrite(
                                    st.session_state.raw_data_cache,
                                    {'idx': item['index'], 'style': item['style'], 'angle': item['angle']},
                                    industry, target
                                )
                                if new_item:
                                    st.session_state.copywrites[item['index']-1] = new_item
                                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
