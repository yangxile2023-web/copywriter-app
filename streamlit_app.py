import streamlit as st
import re
import hashlib
import time
from openai import OpenAI
from sensitive_words import check_sensitive_words

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="晓牧传媒文案助手 v4.1",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== 全局样式 ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap');
    
    * { 
        font-family: 'Inter', 'Noto Sans SC', sans-serif !important;
        box-sizing: border-box;
    }
    
    /* 隐藏 Streamlit 默认元素 */
    #MainMenu, header, footer, .stDeployButton { display: none !important; }
    
    /* 主背景 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%) !important;
        background-attachment: fixed !important;
    }
    
    /* 限制最大宽度，居中显示 */
    .main .block-container {
        max-width: 1400px !important;
        padding: 2rem 3rem !important;
    }
    
    /* 玻璃态容器 */
    .glass-container {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25) !important;
        padding: 28px !important;
        margin-bottom: 24px !important;
    }
    
    /* 主按钮 */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 28px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.5) !important;
    }
    
    /* 次要按钮 */
    .stButton>button[kind="secondary"] {
        background: white !important;
        color: #667eea !important;
        border: 2px solid #e0e7ff !important;
        border-radius: 10px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
        font-size: 13px !important;
    }
    
    .stButton>button[kind="secondary"]:hover {
        background: #f5f7ff !important;
        border-color: #667eea !important;
    }
    
    /* 输入框 */
    .stTextArea textarea {
        background: #f8fafc !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 14px !important;
        padding: 18px !important;
        font-size: 15px !important;
        line-height: 1.7 !important;
        transition: all 0.3s !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1) !important;
        background: white !important;
    }
    
    /* 选择器 */
    .stSelectbox > div > div {
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
    }
    
    /* 单选 */
    .stRadio > div {
        background: #f8fafc !important;
        border-radius: 10px !important;
        padding: 6px !important;
    }
    
    /* 折叠面板 */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f5f7ff 0%, #ffffff 100%) !important;
        border-radius: 10px !important;
        border: 1px solid #e0e7ff !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }
    
    /* 进度条 */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 8px !important;
        height: 8px !important;
    }
    
    /* 头部 */
    .app-header {
        text-align: center;
        padding: 30px 0 40px 0;
        color: white;
    }
    
    .app-header h1 {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 10px;
        text-shadow: 0 4px 20px rgba(0,0,0,0.2);
        color: white !important;
    }
    
    .app-header p {
        font-size: 16px;
        opacity: 0.9;
    }
    
    /* 左侧固定面板 */
    .sidebar-fixed {
        position: sticky;
        top: 20px;
    }
    
    /* 统计卡片 - 水平排列 */
    .stats-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        border: 1px solid rgba(0,0,0,0.04);
        transition: transform 0.2s;
    }
    
    .stat-card:hover {
        transform: translateY(-3px);
    }
    
    .stat-icon {
        font-size: 24px;
        margin-bottom: 6px;
    }
    
    .stat-number {
        font-size: 32px;
        font-weight: 700;
        line-height: 1;
        margin-bottom: 4px;
    }
    
    .stat-label {
        font-size: 13px;
        color: #64748b;
        font-weight: 500;
    }
    
    /* 文案卡片网格 */
    .copy-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
        gap: 20px;
    }
    
    .copy-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
    }
    
    .copy-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.12);
    }
    
    .copy-card.success { border-left-color: #10b981; }
    .copy-card.warning { border-left-color: #f59e0b; }
    .copy-card.error { border-left-color: #ef4444; background: #fef2f2; }
    
    .copy-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
        flex-wrap: wrap;
        gap: 8px;
    }
    
    .copy-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
    }
    
    .copy-number {
        font-size: 22px;
        font-weight: 800;
        color: #e2e8f0;
        line-height: 1;
    }
    
    /* 标签 */
    .tag {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .tag-purple { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
        color: white;
    }
    .tag-blue { background: #e0e7ff; color: #4338ca; }
    .tag-orange { background: #fef3c7; color: #92400e; }
    .tag-green { background: #d1fae5; color: #065f46; }
    .tag-red { background: #fee2e2; color: #991b1b; }
    .tag-yellow { background: #fef3c7; color: #92400e; }
    
    /* 状态标识 */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .status-success { background: #d1fae5; color: #065f46; }
    .status-warning { background: #fef3c7; color: #92400e; }
    .status-error { background: #fee2e2; color: #991b1b; }
    
    /* 文案内容 */
    .copy-content {
        background: #f8fafc;
        border-radius: 10px;
        padding: 14px;
        margin: 12px 0;
        border: 1px solid #e2e8f0;
        line-height: 1.8;
        font-size: 14px;
        color: #1e293b;
        flex: 1;
    }
    
    /* 操作栏 */
    .copy-actions {
        display: flex;
        gap: 8px;
        margin-top: 12px;
        flex-wrap: wrap;
    }
    
    .action-btn {
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        border: none;
    }
    
    /* 问题提示 */
    .issue-hint {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 12px;
        color: #9a3412;
        margin-top: 8px;
    }
    
    /* 分隔线 */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 20px 0;
    }
    
    /* 两栏布局优化 */
    .main-layout {
        display: grid;
        grid-template-columns: 320px 1fr;
        gap: 24px;
    }
    
    @media (max-width: 1024px) {
        .main-layout {
            grid-template-columns: 1fr;
        }
        .copy-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==================== 密码验证 ====================
def check_password():
    return True

# ==================== 配置数据 ====================
INDUSTRIES = {
    "catering": {"name": "🍽️ 餐饮", "description": "突出食材新鲜、口味独特"},
    "woodwork": {"name": "🪵 木作定制", "description": "强调工艺精湛、材质环保"},
    "factory": {"name": "🏭 工厂/制造", "description": "展现生产实力、质量把控"},
    "lottery": {"name": "🎰 彩票店", "description": "分享中奖故事、客户好运"},
    "hotel": {"name": "🏨 酒店/民宿", "description": "描述温馨环境、贴心服务"},
    "general": {"name": "📦 通用", "description": "根据行业特点突出优势"}
}

CONTENT_TYPES = {
    "干货避坑": {"color": "#ef4444", "icon": "🔴", "desc": "揭露行业内幕、避坑指南"},
    "人设故事": {"color": "#8b5cf6", "icon": "🟣", "desc": "老板个人经历、创业故事"},
    "细节特写": {"color": "#f59e0b", "icon": "🟡", "desc": "产品/工艺的具体细节"},
    "认知反转": {"color": "#10b981", "icon": "🟢", "desc": "颠覆常识、打破认知"}
}

STYLES = ["轻松", "温馨", "真诚", "励志", "接地气", "怀旧"]
ANGLES = ["个人故事", "顾客见证", "行业见解", "创业历程", "日常趣事", "价值观分享", "对比反差", "情感共鸣"]

KIMI_API_KEY = "sk-IA6qyNJFSYC8UB9RHnGHsgz24VWSrKalSnd5nTTbJNiqQ2uu"

# ==================== API 客户端 ====================
@st.cache_resource
def get_kimi_client():
    return OpenAI(api_key=KIMI_API_KEY, base_url="https://api.moonshot.cn/v1")

# ==================== 专业调教指令 ====================
SYSTEM_PROMPT = """你是一位短视频文案大师，专为实体店主创作高转化短视频文案。

【黄金三秒原则】
1. 严禁前3秒出现：自我介绍("大家好我是XX")、店名、经营地址
2. 开头必须用"利益、冲突、悬念、扎心"四选一

【语义降维】
严禁使用：匠心、坚守、高端、高效、实战、回味无穷、专业、品质
必须转化为具象描述，如"食材新鲜"→"龙虾在水里打架，腮白肉肥"

【拍摄约束】
- 只有一人出镜，不出现客户
- 禁止最、绝对、第一等违禁词
- 禁止具体地址"""

CONTENT_TEMPLATES = {
    "干货避坑": {"hooks": ["别再交这种智商税了", "今天说个得罪人的真相", "这个行业没人敢说的秘密"]},
    "人设故事": {"hooks": ["做了15年，我想说说心里话", "从欠债到翻身，就这一步", "当年那个决定改变了我一生"]},
    "细节特写": {"hooks": ["你看这个细节一般人不会注意", "花了3天就为这1毫米", "有人笑我傻看完沉默了"]},
    "认知反转": {"hooks": ["你以为的其实是错的", "打破常识这行不是这么做的", "这个真相可能会得罪同行"]}
}

# ==================== 生成文案 ====================
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
5. 结尾自然引导互动

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
            if word_count < min_words: issues.append(f"字数不足")
            elif word_count > max_words: issues.append(f"字数超标")
            if has_address: issues.append("有具体地址")
            if has_self_intro: issues.append("开头有自我介绍")
            if name_count > 2: issues.append(f"称呼过多")
            if sensitive: issues.append(f"敏感词")
            
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
                    'content': f"❌ 生成失败: {str(e)[:40]}...", 
                    'word_count': 0, 'quality_pass': False, 
                    'length_type': length, 'style': config['style'], 
                    'angle': config['angle'], 'content_type': content_type,
                    'hook': hook, 'issues': ["API错误"]
                }
            time.sleep(1.5)
    return None

# ==================== 主程序 ====================
def main():
    if not check_password():
        st.stop()
    
    # 初始化
    for key in ['copywrites', 'raw_data_cache', 'is_generating']:
        if key not in st.session_state:
            st.session_state[key] = [] if key == 'copywrites' else ("" if key == 'raw_data_cache' else False)
    
    # 头部
    st.markdown("""
    <div class="app-header">
        <h1>✨ 晓牧传媒文案助手</h1>
        <p>AI 驱动的短视频文案生成工具 · v4.1</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 使用列布局（左侧固定宽度，右侧自适应）
    col_left, col_right = st.columns([280, 1])
    
    # ============ 左侧控制面板 ============
    with col_left:
        st.markdown('<div class="sidebar-fixed">', unsafe_allow_html=True)
        
        # 配置卡片
        st.markdown('<div class="glass-container" style="padding: 20px !important;">', unsafe_allow_html=True)
        st.markdown("### ⚙️ 配置")
        
        # 行业选择
        st.markdown("**🏭 行业**")
        industry = st.selectbox(
            "行业",
            options=list(INDUSTRIES.keys()),
            format_func=lambda x: INDUSTRIES[x]['name'],
            index=5,
            label_visibility="collapsed"
        )
        st.caption(INDUSTRIES[industry]['description'])
        
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        
        # 文案长度
        st.markdown("**📏 长度**")
        length = st.radio(
            "长度",
            ["short", "long"],
            format_func=lambda x: "短文案 (150-180字)" if x == "short" else "长文案 (200-300字)",
            index=0,
            label_visibility="collapsed"
        )
        
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        
        # 内容类型说明
        with st.expander("📚 内容类型分配"):
            for ctype, info in CONTENT_TYPES.items():
                st.markdown(f"**{info['icon']} {ctype}** - {info['desc']}")
        
        # 工具按钮
        if st.session_state.copywrites:
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            st.markdown("**🛠️ 工具**")
            
            if st.button("🚨 检测敏感词", use_container_width=True):
                total = sum(len(check_sensitive_words(c.get('content', ''))) for c in st.session_state.copywrites)
                st.error(f"发现 {total} 个敏感词") if total else st.success("✅ 未检测到敏感词")
            
            if st.button("📋 复制全部", use_container_width=True):
                text = "\n\n".join([f"【{c['content_type']}】\n{c['content']}" for c in st.session_state.copywrites])
                st.code(text)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ============ 右侧主内容区 ============
    with col_right:
        # 输入区域
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        st.markdown("### 📝 客户资料")
        
        raw_data = st.text_area(
            "资料",
            height=160,
            placeholder="请粘贴客户资料（建议100字以上）：\n\n• 出镜称呼：王老板、李姐\n• 店铺/企业名称\n• 所在城市\n• 主营业务\n• 核心卖点/特色\n• 真实故事或经历",
            label_visibility="collapsed"
        )
        
        # 生成按钮行
        col_gen1, col_gen2 = st.columns([4, 1])
        with col_gen1:
            st.caption(f"📊 已输入 {len(raw_data)} 字")
        with col_gen2:
            if st.button("✨ 生成30条", type="primary", use_container_width=True, disabled=st.session_state.is_generating):
                if len(raw_data) < 30:
                    st.error("⚠️ 请填写完整资料（至少30字）")
                else:
                    st.session_state.is_generating = True
                    st.session_state.raw_data_cache = raw_data
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 生成处理
        if st.session_state.is_generating and not st.session_state.copywrites:
            with st.spinner("🚀 正在生成文案..."):
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
            # 统计行
            total = len(st.session_state.copywrites)
            passed = sum(1 for c in st.session_state.copywrites if c['quality_pass'])
            failed = sum(1 for c in st.session_state.copywrites if c['word_count'] == 0)
            need_opt = total - passed - failed
            
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            
            stats_html = f"""
            <div class="stats-row">
                <div class="stat-card">
                    <div class="stat-icon">📊</div>
                    <div class="stat-number" style="color: #667eea;">{total}</div>
                    <div class="stat-label">总数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">✅</div>
                    <div class="stat-number" style="color: #10b981;">{passed}</div>
                    <div class="stat-label">优质</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">⚠️</div>
                    <div class="stat-number" style="color: #f59e0b;">{need_opt}</div>
                    <div class="stat-label">需优化</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">❌</div>
                    <div class="stat-number" style="color: #ef4444;">{failed}</div>
                    <div class="stat-label">失败</div>
                </div>
            </div>
            """
            st.markdown(stats_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 文案网格
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            st.markdown("### 📄 生成结果")
            
            # 开始网格布局
            st.markdown('<div class="copy-grid">', unsafe_allow_html=True)
            
            for item in st.session_state.copywrites:
                is_fail = item['word_count'] == 0
                is_warning = not item['quality_pass'] and not is_fail
                card_class = "error" if is_fail else ("warning" if is_warning else "success")
                
                ct_info = CONTENT_TYPES.get(item['content_type'], {})
                ct_color = ct_info.get('color', '#667eea')
                
                status_badge = ('<span class="status-badge status-success">✓ 优质</span>' if item['quality_pass'] 
                               else '<span class="status-badge status-error">✗ 失败</span>' if is_fail 
                               else '<span class="status-badge status-warning">⚠ 需优化</span>')
                
                len_badge = (f'<span class="tag tag-green">长 {item["word_count"]}字</span>' if item['length_type'] == 'long' 
                            else f'<span class="tag tag-orange">短 {item["word_count"]}字</span>')
                
                # 构建卡片 HTML
                card_html = f"""
                <div class="copy-card {card_class}">
                    <div class="copy-header">
                        <div class="copy-meta">
                            <span class="copy-number">#{item['index']}</span>
                            <span class="tag" style="background: {ct_color}; color: white;">{item['content_type']}</span>
                            {len_badge}
                        </div>
                        {status_badge}
                    </div>
                    <div class="copy-content">{item['content']}</div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                
                # 问题提示
                if item.get('issues'):
                    st.markdown(f'<div class="issue-hint">⚠️ {" · ".join(item["issues"])}</div>', unsafe_allow_html=True)
                
                # 操作按钮
                cols = st.columns([1, 1, 1, 2])
                with cols[0]:
                    if st.button("📋 复制", key=f"copy_{item['index']}", use_container_width=True):
                        st.toast(f"✅ 已复制 #{item['index']}")
                
                with cols[1]:
                    if (is_fail or item['word_count'] < 120) and st.button("🔄 重试", key=f"retry_{item['index']}", use_container_width=True):
                        with st.spinner(f"重试 #{item['index']}..."):
                            new_item = generate_single_copywrite(
                                st.session_state.raw_data_cache,
                                {'idx': item['index'], 'style': item['style'], 'angle': item['angle']},
                                industry, item['length_type']
                            )
                            if new_item:
                                st.session_state.copywrites[item['index']-1] = new_item
                                st.rerun()
                
                with cols[2]:
                    if item['quality_pass']:
                        target = 'long' if item['length_type'] == 'short' else 'short'
                        btn_text = "📖 长" if target == 'long' else "⚡ 短"
                        if st.button(btn_text, key=f"switch_{item['index']}", use_container_width=True):
                            with st.spinner(f"切换 #{item['index']}..."):
                                new_item = generate_single_copywrite(
                                    st.session_state.raw_data_cache,
                                    {'idx': item['index'], 'style': item['style'], 'angle': item['angle']},
                                    industry, target
                                )
                                if new_item:
                                    st.session_state.copywrites[item['index']-1] = new_item
                                    st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)  # 结束网格
            st.markdown('</div>', unsafe_allow_html=True)  # 结束玻璃容器

if __name__ == "__main__":
    main()
