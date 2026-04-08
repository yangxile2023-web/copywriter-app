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

# ==================== 生成文案 ====================
def generate_single_copywrite(raw_data, config, industry="general", length="short", retries=3):
    """生成单条文案"""
    industry_info = INDUSTRIES.get(industry, INDUSTRIES["general"])
    name_match = re.search(r'出镜称呼[：:]\s*(\S+)', raw_data)
    name = name_match.group(1) if name_match else "老板"
    
    min_words, max_words = (150, 180) if length == "short" else (200, 300)
    
    for attempt in range(retries):
        prompt = f"""根据资料写第{config['idx']}条短视频文案。
【行业】{industry_info['name']}
【风格】{config['style']}【角度】{config['angle']}【开头】{config['hook']}
【客户资料】{raw_data[:400]}

【写作要求】
1. 字数：严格{min_words}-{max_words}字（必须遵守）
2. 开头：{config['hook']}方式
3. 称呼："{name}"最多3次，多用"咱"
4. 禁止具体地址如"XX路XX号"
5. 口语化，真实自然

直接写文案："""
        
        try:
            client = get_kimi_client()
            response = client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {"role": "system", "content": "你是短视频文案专家。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.8,
                timeout=30
            )
            content = response.choices[0].message.content.strip()
            word_count = len(content.replace(' ', '').replace('\n', ''))
            name_count = content.count(name)
            has_address = bool(re.search(r'[路街道]\s*\d+[号]', content))
            sensitive = check_sensitive_words(content)
            
            issues = []
            if word_count < min_words: issues.append(f"字数不足({word_count}字)")
            elif word_count > max_words: issues.append(f"字数超标({word_count}字)")
            if has_address: issues.append("有具体地址")
            if sensitive: issues.append(f"敏感词: {', '.join(sensitive[:2])}")
            
            quality_pass = min_words <= word_count <= max_words and not has_address and not sensitive
            
            return {
                'index': config['idx'], 'content': content, 'word_count': word_count,
                'name_count': name_count, 'quality_pass': quality_pass,
                'length_type': length, 'style': config['style'], 
                'angle': config['angle'], 'hook': config['hook'], 'issues': issues
            }
        except Exception as e:
            error_msg = str(e)
            if attempt == retries - 1:
                return {
                    'index': config['idx'], 
                    'content': f"❌ 生成失败: {error_msg[:40]}..." if len(error_msg) > 40 else f"❌ 生成失败: {error_msg}", 
                    'word_count': 0, 'quality_pass': False, 'length_type': length, 
                    'style': config['style'], 'angle': config['angle'], 'hook': config['hook'], 
                    'issues': [f"API错误"]
                }
            time.sleep(1)
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
                
                # 状态标识
                if item['quality_pass']:
                    status_html = '<span class="status-badge status-success">✓ 合格</span>'
                elif is_fail:
                    status_html = '<span class="status-badge status-error">✗ 失败</span>'
                else:
                    status_html = '<span class="status-badge status-warning">⚠ 需优化</span>'
                
                st.markdown(f"""
                <div class="copy-card {card_class}">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:12px;">
                        <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
                            <span style="font-size:28px; font-weight:800; color:#e2e8f0;">#{item['index']}</span>
                            <span class="tag tag-purple">{item['style']}</span>
                            <span class="tag tag-blue">{item['angle']}</span>
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
