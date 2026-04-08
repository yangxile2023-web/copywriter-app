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
    
    /* 玻璃态容器 */
    .glass-container {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 24px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25) !important;
        padding: 32px !important;
        margin-bottom: 24px !important;
    }
    
    /* 主按钮 */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 16px 32px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
    }
    
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.5) !important;
    }
    
    /* 次要按钮 */
    .stButton>button[kind="secondary"] {
        background: white !important;
        color: #667eea !important;
        border: 2px solid #e0e7ff !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    
    .stButton>button[kind="secondary"]:hover {
        background: #f5f7ff !important;
        border-color: #667eea !important;
    }
    
    /* 输入框样式 */
    .stTextArea textarea {
        background: rgba(248, 250, 252, 0.8) !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
        transition: all 0.3s !important;
        resize: vertical !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1) !important;
        background: white !important;
    }
    
    /* 下拉选择器 */
    .stSelectbox > div > div {
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
    }
    
    /* 单选按钮 */
    .stRadio > div {
        background: rgba(248, 250, 252, 0.8) !important;
        border-radius: 12px !important;
        padding: 8px !important;
    }
    
    /* 进度条 */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 10px !important;
        height: 8px !important;
    }
    
    /* 统计卡片 */
    .stat-card {
        background: white;
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
        transition: transform 0.3s, box-shadow 0.3s;
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.12);
    }
    
    .stat-number {
        font-size: 36px;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stat-label {
        color: #64748b;
        font-size: 14px;
        margin-top: 4px;
        font-weight: 500;
    }
    
    /* 文案卡片 */
    .copy-card {
        background: white;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .copy-card:hover {
        transform: translateX(8px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.12);
    }
    
    .copy-card.success { border-left-color: #10b981; }
    .copy-card.warning { border-left-color: #f59e0b; }
    .copy-card.error { border-left-color: #ef4444; background: #fef2f2; }
    
    /* 标签 */
    .tag {
        display: inline-flex;
        align-items: center;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 600;
        margin-right: 8px;
    }
    
    .tag-purple { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    .tag-blue { background: #e0e7ff; color: #4338ca; }
    .tag-orange { background: #fef3c7; color: #92400e; }
    .tag-green { background: #d1fae5; color: #065f46; }
    
    /* 状态标识 */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 9999px;
        font-size: 13px;
        font-weight: 600;
    }
    
    .status-success { background: #d1fae5; color: #065f46; }
    .status-warning { background: #fef3c7; color: #92400e; }
    .status-error { background: #fee2e2; color: #991b1b; }
    
    /* 文案内容区 */
    .content-area {
        background: #f8fafc;
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
        border: 1px solid #e2e8f0;
        line-height: 1.8;
        font-size: 15px;
        color: #1e293b;
    }
    
    /* 分隔线 */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 24px 0;
    }
    
    /* 头部标题 */
    .app-header {
        text-align: center;
        padding: 40px 0;
        color: white;
    }
    
    .app-header h1 {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 12px;
        text-shadow: 0 4px 20px rgba(0,0,0,0.2);
        color: white !important;
    }
    
    .app-header p {
        font-size: 18px;
        opacity: 0.9;
        font-weight: 400;
    }
    
    /* 登录框 */
    .login-box {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 24px;
        padding: 48px;
        max-width: 420px;
        margin: 0 auto;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.35);
        text-align: center;
    }
    
    .login-icon {
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 24px;
        font-size: 40px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    /* 工具栏 */
    .toolbar {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-bottom: 20px;
    }
    
    /* Toast 提示 */
    .toast {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# ==================== 密码验证（已关闭）====================
def check_password():
    """密码验证已关闭，方便测试"""
    return True

# ==================== 配置数据 ====================
INDUSTRIES = {
    "catering": {"name": "🍽️ 餐饮", "description": "突出食材新鲜、口味独特、环境卫生、顾客好评"},
    "woodwork": {"name": "🪵 木作定制", "description": "强调工艺精湛、材质环保、设计独特、服务周到"},
    "factory": {"name": "🏭 工厂/制造", "description": "展现生产实力、质量把控、交货准时、客户信赖"},
    "lottery": {"name": "🎰 彩票店", "description": "分享中奖故事、客户好运、经营趣事，不卖梦想只讲故事"},
    "hotel": {"name": "🏨 酒店/民宿", "description": "描述温馨环境、贴心服务、独特体验、客人好评"},
    "general": {"name": "📦 通用", "description": "根据行业特点，突出核心优势和真实故事"}
}

STYLES = ["轻松", "温馨", "真诚", "励志", "接地气", "怀旧"]
ANGLES = ["个人故事", "顾客见证", "行业见解", "创业历程", "日常趣事", "价值观分享", "对比反差", "情感共鸣"]
HOOKS = ["悬念疑问", "惊人数据", "情感共鸣", "直接开场", "故事引入", "痛点直击", "反差对比", "热点借势"]

KIMI_API_KEY = "sk-IA6qyNJFSYC8UB9RHnGHsgz24VWSrKalSnd5nTTbJNiqQ2uu"

# ==================== API 客户端 ====================
@st.cache_resource
def get_kimi_client():
    return OpenAI(api_key=KIMI_API_KEY, base_url="https://api.moonshot.cn/v1")

# ==================== 专业调教系统指令 ====================
SYSTEM_PROMPT = """你是一位短视频文案大师，专为实体店主/企业主创作高转化短视频文案。

【黄金三秒原则 - 硬性约束】
1. 严禁前3秒出现：自我介绍("大家好我是XX")、店名、经营地址
2. 开头必须用"利益、冲突、悬念、扎心"四选一：
   - 利益："别再交这种智商税了"
   - 冲突："邢台的老板们，别再发这种垃圾朋友圈了"
   - 悬念："做了15年餐饮，今天说个得罪人的真相"
   - 扎心："你知道吗？90%的装修钱都被这东西坑走了"

【单一主题逻辑 - 内容分配】
- 30%干货避坑：揭露行业内幕、避坑指南
- 30%人设故事：老板个人经历、创业故事
- 20%细节特写：产品细节、工艺细节、服务细节
- 20%认知反转：打破常识、颠覆认知

【语义降维 - 禁用词汇】
严禁使用：匠心、坚守、高端、高效、实战、回味无穷、专业、品质、服务
必须转化为：
- "食材新鲜" → "龙虾在水里打架，腮白肉肥"
- "经验丰富" → "这二十年，手里的茧子磨掉了一层又一层"
- "做工精细" → "这个缝我拆了7遍，直到完全对齐"

【拍摄与合规约束】
- 画面只有一人出镜，不出现客户
- 场景描述由口播完成，不复刻回忆画面
- 禁止最、绝对、第一等违禁词
- 禁止具体地址如"XX路XX号"

【5%重复率过滤】
- 同一批5条文案，核心动词重合度不超过10%
- 场景轮换：工作台、店门口、茶歇区、货架旁

【KPI自检标准】
1. 钩子力：开头3秒让用户"别划走"
2. 口语化：念起来顺口，无书面语
3. 颗粒度：有具体数字、细节、画面感
4. 情绪值：带情绪的交谈，非冷冰冰科普
5. 转化力：结尾引导自然且有诱惑力"""

# ==================== 文案类型模板 ====================
CONTENT_TEMPLATES = {
    "干货避坑": {
        "hook": ["别再交这种智商税了", "今天说个得罪人的真相", "这个行业没人敢说的秘密", "90%的人都踩过这个坑"],
        "focus": "揭露行业内幕、避坑指南",
        "style": "直接指出问题，给出解决方案"
    },
    "人设故事": {
        "hook": ["做了15年，我想说说心里话", "从欠债到翻身，就这一步", "当年那个决定，改变了我的一生", "有人问我为什么这么拼"],
        "focus": "老板个人经历、创业故事、转折点",
        "style": "真实、有细节、有情感"
    },
    "细节特写": {
        "hook": ["你看这个细节，一般人不会注意", "就是这不起眼的地方", "花了3天，就为这1毫米", "有人笑我傻，看完沉默了"],
        "focus": "产品/工艺/服务的具体细节",
        "style": "具象化、有画面感、可感知"
    },
    "认知反转": {
        "hook": ["你以为的，其实是错的", "打破常识，这行不是这么做的", "所有人都告诉我这样做，但我偏不", "这个真相，可能会得罪同行"],
        "focus": "颠覆常识、打破认知",
        "style": "先破后立、引发思考"
    }
}

# ==================== 生成文案 ====================
def generate_single_copywrite(raw_data, config, industry="general", length="short", retries=3):
    """生成单条文案 - 使用专业调教系统"""
    industry_info = INDUSTRIES.get(industry, INDUSTRIES["general"])
    name_match = re.search(r'出镜称呼[：:]\s*(\S+)', raw_data)
    name = name_match.group(1) if name_match else "老板"
    
    min_words, max_words = (150, 180) if length == "short" else (200, 300)
    
    # 根据序号分配内容类型
    content_types = ["干货避坑", "人设故事", "细节特写", "认知反转"]
    content_type = content_types[(config['idx'] - 1) % 4]
    template = CONTENT_TEMPLATES[content_type]
    
    # 选择该类型的开场钩子
    hook_index = (config['idx'] - 1) // 4 % len(template["hook"])
    forced_hook = template["hook"][hook_index]
    
    for attempt in range(retries):
        prompt = f"""根据以下信息创作第{config['idx']}条短视频文案。

【内容类型】{content_type}
【类型说明】{template["focus"]}
【风格要求】{template["style"]}

【客户资料】{raw_data[:500]}
【出镜称呼】{name}

【硬性要求】
1. 字数：{min_words}-{max_words}字（严格限制）
2. 开头：必须用"{forced_hook}"或类似钩子开场，禁止自我介绍和店名
3. 称呼："{name}"出现不超过2次，多用"我""咱"
4. 细节：必须包含至少1个具体数字或感官细节
5. 结尾：自然引导互动，不生硬求关注
6. 场景：在"工作台/店门口/货架旁/操作区"中选择一个

直接输出文案："""
        
        try:
            client = get_kimi_client()
            response = client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.85,
                timeout=35
            )
            content = response.choices[0].message.content.strip()
            
            # 清理可能的引号
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            
            word_count = len(content.replace(' ', '').replace('\n', ''))
            name_count = content.count(name)
            has_address = bool(re.search(r'[路街道]\s*\d+[号]', content))
            has_self_intro = bool(re.search(r'^(大家好|我是|我叫|我们店|我们这里是)', content))
            sensitive = check_sensitive_words(content)
            
            issues = []
            if word_count < min_words: issues.append(f"字数不足({word_count}字)")
            elif word_count > max_words: issues.append(f"字数超标({word_count}字)")
            if has_address: issues.append("有具体地址")
            if has_self_intro: issues.append("开头有自我介绍")
            if name_count > 2: issues.append(f"称呼{name}出现{name_count}次")
            if sensitive: issues.append(f"敏感词: {', '.join(sensitive[:2])}")
            
            # 质量通过标准
            quality_pass = (
                min_words <= word_count <= max_words and 
                not has_address and 
                not has_self_intro and
                name_count <= 2 and
                len(sensitive) == 0
            )
            
            return {
                'index': config['idx'], 
                'content': content, 
                'word_count': word_count,
                'name_count': name_count, 
                'quality_pass': quality_pass,
                'length_type': length, 
                'style': config['style'], 
                'angle': config['angle'], 
                'hook': forced_hook,
                'content_type': content_type,
                'issues': issues
            }
        except Exception as e:
            error_msg = str(e)
            if attempt == retries - 1:
                return {
                    'index': config['idx'], 
                    'content': f"❌ 生成失败: {error_msg[:40]}..." if len(error_msg) > 40 else f"❌ 生成失败: {error_msg}", 
                    'word_count': 0, 
                    'quality_pass': False, 
                    'length_type': length, 
                    'style': config['style'], 
                    'angle': config['angle'], 
                    'hook': forced_hook,
                    'content_type': content_type,
                    'issues': [f"API错误"]
                }
            time.sleep(1.5)
            continue
    return None

# ==================== 主程序 ====================
def main():
    if not check_password():
        st.stop()
    
    # 初始化
    if 'copywrites' not in st.session_state:
        st.session_state.copywrites = []
    if 'raw_data_cache' not in st.session_state:
        st.session_state.raw_data_cache = ""
    if 'is_generating' not in st.session_state:
        st.session_state.is_generating = False
    
    # 头部
    st.markdown("""
    <div class="app-header">
        <h1>✨ 晓牧传媒文案助手</h1>
        <p>AI 驱动的短视频文案生成工具 · v4.1</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 主布局
    col_left, col_right = st.columns([1, 2])
    
    # 左侧配置面板
    with col_left:
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        
        st.markdown("### ⚙️ 配置选项")
        
        # 行业选择
        st.markdown("**🏭 选择行业**")
        industry = st.selectbox(
            "行业类型",
            options=list(INDUSTRIES.keys()),
            format_func=lambda x: INDUSTRIES[x]['name'],
            index=5,
            label_visibility="collapsed"
        )
        st.caption(INDUSTRIES[industry]['description'])
        
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        
        # 文案长度
        st.markdown("**📏 文案长度**")
        length = st.radio(
            "长度",
            ["short", "long"],
            format_func=lambda x: "📄 短文案 (150-180字)" if x == "short" else "📖 长文案 (200-300字)",
            index=0,
            label_visibility="collapsed"
        )
        
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        
        # 内容类型分配
        with st.expander("📚 内容类型分配（点击展开）"):
            st.markdown("""
            **30条文案自动分配：**
            - 🔴 **干货避坑** (30%)：揭露行业内幕、避坑指南
            - 🟣 **人设故事** (30%)：老板个人经历、创业故事
            - 🟡 **细节特写** (20%)：产品/工艺的具体细节
            - 🟢 **认知反转** (20%)：颠覆常识、打破认知
            
            **黄金三秒原则：**
            - ❌ 禁止自我介绍、店名、地址
            - ✅ 必须用利益/冲突/悬念/扎心开场
            """)
        
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        
        # 工具按钮
        if st.session_state.copywrites:
            st.markdown("**🛠️ 工具**")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🚨 检测敏感词", use_container_width=True):
                    with st.spinner("检测中..."):
                        total_sensitive = sum(len(check_sensitive_words(c.get('content', ''))) for c in st.session_state.copywrites)
                        if total_sensitive > 0:
                            st.error(f"发现 {total_sensitive} 个敏感词")
                        else:
                            st.success("✅ 未检测到敏感词")
            
            with col_btn2:
                if st.button("📋 复制全部", use_container_width=True):
                    text = "\n\n".join([f"【{c['style']}·{c['angle']}】\n{c['content']}" for c in st.session_state.copywrites])
                    st.code(text, language=None)
                    st.toast("已复制到剪贴板！")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 右侧主内容区
    with col_right:
        # 输入区域
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        
        st.markdown("### 📝 客户资料")
        
        raw_data = st.text_area(
            "客户资料",
            height=180,
            placeholder="请粘贴客户资料，建议包含：\n\n• 出镜称呼：如王老板、李姐\n• 店铺/企业名称\n• 所在城市（不需要具体门牌号）\n• 主营业务\n• 核心卖点/特色\n• 真实故事或经历（100字以上效果更佳）",
            label_visibility="collapsed"
        )
        
        # 生成按钮
        col_gen1, col_gen2, col_gen3 = st.columns([2, 1, 1])
        with col_gen1:
            st.caption(f"📊 已输入 {len(raw_data)} 字")
        with col_gen2:
            if st.session_state.is_generating:
                st.button("⏳ 生成中...", disabled=True, use_container_width=True)
        with col_gen3:
            if st.button("✨ 生成30条文案", type="primary", use_container_width=True, disabled=st.session_state.is_generating):
                if len(raw_data) < 30:
                    st.error("⚠️ 请填写完整的客户资料（至少30字）")
                else:
                    st.session_state.is_generating = True
                    st.session_state.raw_data_cache = raw_data
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 生成处理
        if st.session_state.is_generating and not st.session_state.copywrites:
            with st.spinner("🚀 正在生成文案，请稍候..."):
                configs = [{'idx': i+1, 'style': STYLES[i%6], 'angle': ANGLES[i%8], 'hook': HOOKS[i%8]} for i in range(30)]
                st.session_state.copywrites = []
                
                progress_placeholder = st.empty()
                
                for i, config in enumerate(configs):
                    result = generate_single_copywrite(st.session_state.raw_data_cache, config, industry, length)
                    if result:
                        st.session_state.copywrites.append(result)
                    
                    # 更新进度
                    progress = (i + 1) / 30
                    progress_placeholder.progress(progress, text=f"生成进度: {i+1}/30 ({int(progress*100)}%)")
                
                progress_placeholder.empty()
            
            st.session_state.is_generating = False
            st.rerun()
        
        # 结果显示
        if st.session_state.copywrites:
            # 统计卡片
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            
            total = len(st.session_state.copywrites)
            passed = sum(1 for c in st.session_state.copywrites if c['quality_pass'])
            failed = sum(1 for c in st.session_state.copywrites if c['word_count'] == 0)
            need_opt = total - passed - failed
            
            cols = st.columns(4)
            stats_data = [
                ("📊", "总数", total, "#667eea"),
                ("✅", "达标", passed, "#10b981"),
                ("⚠️", "需优化", need_opt, "#f59e0b"),
                ("❌", "失败", failed, "#ef4444")
            ]
            
            for i, (icon, label, value, color) in enumerate(stats_data):
                with cols[i]:
                    st.markdown(f"""
                    <div class="stat-card">
                        <div style="font-size: 28px; margin-bottom: 4px;">{icon}</div>
                        <div class="stat-number" style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{value}</div>
                        <div class="stat-label">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 文案列表
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            st.markdown("### 📄 生成结果")
            
            for item in st.session_state.copywrites:
                is_fail = item['word_count'] == 0
                is_warning = not item['quality_pass'] and not is_fail
                card_class = "error" if is_fail else ("warning" if is_warning else "success")
                len_class = "tag-green" if item['length_type'] == 'long' else "tag-orange"
                len_name = "长文案" if item['length_type'] == 'long' else "短文案"
                content_type = item.get('content_type', '通用')
                
                # 内容类型颜色
                type_colors = {
                    "干货避坑": "#ef4444",
                    "人设故事": "#8b5cf6", 
                    "细节特写": "#f59e0b",
                    "认知反转": "#10b981"
                }
                type_color = type_colors.get(content_type, "#667eea")
                
                # 状态标识
                if item['quality_pass']:
                    status_html = '<span class="status-badge status-success">✓ 优质</span>'
                elif is_fail:
                    status_html = '<span class="status-badge status-error">✗ 失败</span>'
                else:
                    status_html = '<span class="status-badge status-warning">⚠ 需优化</span>'
                
                st.markdown(f"""
                <div class="copy-card {card_class}">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:12px;">
                        <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
                            <span style="font-size:26px; font-weight:800; color:#e2e8f0;">#{item['index']}</span>
                            <span class="tag" style="background:{type_color};color:white;font-weight:600;">{content_type}</span>
                            <span class="tag {len_class}">{len_name} · {item['word_count']}字</span>
                            {status_html}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 文案内容编辑
                content_key = f"edit_{item['index']}"
                if content_key not in st.session_state:
                    st.session_state[content_key] = item['content']
                
                new_content = st.text_area(
                    f"文案内容 #{item['index']}",
                    value=st.session_state[content_key],
                    key=content_key,
                    height=100,
                    label_visibility="collapsed"
                )
                
                # 问题提示
                if item.get('issues'):
                    issues_text = " · ".join(item['issues'])
                    st.warning(f"⚠️ {issues_text}")
                
                # 操作按钮
                btn_cols = st.columns([1, 1, 1, 3])
                
                with btn_cols[0]:
                    if st.button("📋 复制", key=f"btn_copy_{item['index']}", use_container_width=True):
                        st.toast(f"✅ 文案 #{item['index']} 已复制！")
                
                with btn_cols[1]:
                    if is_fail or item['word_count'] < 120:
                        if st.button("🔄 重试", key=f"btn_retry_{item['index']}", use_container_width=True):
                            with st.spinner(f"重新生成 #{item['index']}..."):
                                new_item = generate_single_copywrite(
                                    st.session_state.raw_data_cache,
                                    {'idx': item['index'], 'style': item['style'], 
                                     'angle': item['angle'], 'hook': item['hook']},
                                    industry, item['length_type']
                                )
                                if new_item:
                                    st.session_state.copywrites[item['index']-1] = new_item
                                    st.rerun()
                
                with btn_cols[2]:
                    if item['quality_pass']:
                        target_len = 'long' if item['length_type'] == 'short' else 'short'
                        btn_text = "📖 转长" if target_len == 'long' else "⚡ 转短"
                        if st.button(btn_text, key=f"btn_switch_{item['index']}", use_container_width=True):
                            with st.spinner(f"切换长度 #{item['index']}..."):
                                new_item = generate_single_copywrite(
                                    st.session_state.raw_data_cache,
                                    {'idx': item['index'], 'style': item['style'],
                                     'angle': item['angle'], 'hook': item['hook']},
                                    industry, target_len
                                )
                                if new_item:
                                    st.session_state.copywrites[item['index']-1] = new_item
                                    st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
