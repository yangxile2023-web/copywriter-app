import streamlit as st
import json
import re
import hashlib
from datetime import datetime
from openai import OpenAI
from sensitive_words import check_sensitive_words

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="晓牧传媒文案助手 v4.1",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== 样式优化 ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
    
    * { font-family: 'Noto Sans SC', sans-serif !important; }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    /* 标题样式 */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
    }
    
    /* 按钮样式 */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5) !important;
    }
    
    /* 输入框样式 */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        border-radius: 12px !important;
        border: 2px solid #e5e7eb !important;
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(10px) !important;
    }
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* 卡片样式 */
    .copy-card {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        margin-bottom: 16px !important;
        border-left: 4px solid #667eea !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08) !important;
        backdrop-filter: blur(10px) !important;
    }
    .copy-card.success { border-left-color: #10b981 !important; }
    .copy-card.fail { border-left-color: #ef4444 !important; background: #fef2f2 !important; }
    
    /* 标签样式 */
    .tag {
        display: inline-flex;
        align-items: center;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        margin-right: 8px;
    }
    .tag-purple { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
    .tag-blue { background: #e0e7ff; color: #4338ca; }
    .tag-orange { background: #fef3c7; color: #92400e; }
    .tag-green { background: #d1fae5; color: #065f46; }
    
    /* 统计卡片 */
    .stat-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .stat-number {
        font-size: 28px;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* 隐藏默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 玻璃态卡片 */
    .glass-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        padding: 24px;
        margin-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 密码验证 ====================
def check_password():
    """密码验证已关闭，方便测试"""
    return True

# ==================== 配置数据 ====================
INDUSTRIES = {
    "catering": {"name": "餐饮", "description": "突出食材新鲜、口味独特、环境卫生"},
    "woodwork": {"name": "木作定制", "description": "强调工艺精湛、材质环保、设计独特"},
    "factory": {"name": "工厂/制造", "description": "展现生产实力、质量把控、交货准时"},
    "lottery": {"name": "彩票店", "description": "分享中奖故事、客户好运、经营趣事"},
    "hotel": {"name": "酒店/民宿", "description": "描述温馨环境、贴心服务、独特体验"},
    "general": {"name": "通用", "description": "根据行业特点，突出核心优势和真实故事"}
}

STYLES = ["轻松", "温馨", "真诚", "励志", "接地气", "怀旧"]
ANGLES = ["个人故事", "顾客见证", "行业见解", "创业历程", "日常趣事", "价值观分享", "对比反差", "情感共鸣"]
HOOKS = ["悬念疑问", "惊人数据", "情感共鸣", "直接开场", "故事引入", "痛点直击", "反差对比", "热点借势"]

KIMI_API_KEY = "sk-IA6qyNJFSYC8UB9RHnGHsgz24VWSrKalSnd5nTTbJNiqQ2uu"

# ==================== API 客户端（缓存）====================
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
                # 最后一次失败，返回带错误信息的失败项
                return {
                    'index': config['idx'], 
                    'content': f"生成失败: {error_msg[:50]}..." if len(error_msg) > 50 else f"生成失败: {error_msg}", 
                    'word_count': 0,
                    'quality_pass': False,
                    'length_type': length, 
                    'style': config['style'], 
                    'angle': config['angle'],
                    'hook': config['hook'], 
                    'issues': [f"API错误: {error_msg[:30]}..."]
                }
            # 等待一下再重试
            import time
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
    
    # 标题区
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 30px; border-radius: 20px; margin-bottom: 30px; color: white;">
        <h1 style="color: white; margin: 0; -webkit-text-fill-color: white;">✍️ 晓牧传媒文案助手</h1>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">v4.1 · 短文案默认(150-180字) · 支持切换长度 · 敏感词检测</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 两列布局
    col_left, col_right = st.columns([1, 3])
    
    # 侧边栏功能
    with col_left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("⚙️ 配置")
        
        industry = st.selectbox(
            "🏭 行业类型",
            options=list(INDUSTRIES.keys()),
            format_func=lambda x: INDUSTRIES[x]['name'],
            index=5
        )
        st.caption(INDUSTRIES[industry]['description'])
        
        st.divider()
        length = st.radio(
            "文案长度",
            ["short", "long"],
            format_func=lambda x: "📄 短文案 (150-180字)" if x == "short" else "📖 长文案 (200-300字)",
            index=0
        )
        
        st.divider()
        if st.session_state.copywrites:
            if st.button("🚨 检测敏感词", use_container_width=True):
                with st.spinner("检测中..."):
                    total_sensitive = sum(len(check_sensitive_words(c.get('content', ''))) for c in st.session_state.copywrites)
                    if total_sensitive > 0:
                        st.error(f"发现 {total_sensitive} 个敏感词")
                    else:
                        st.success("✅ 未检测到敏感词")
            
            if st.button("📋 复制全部", use_container_width=True):
                text = "\n\n".join([f"【{c['style']}·{c['angle']}】\n{c['content']}" for c in st.session_state.copywrites])
                st.code(text)
                st.toast("已生成全部文案文本！")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 主内容区
    with col_right:
        # 输入区域
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📝 客户资料")
        raw_data = st.text_area(
            "直接粘贴客户资料",
            height=180,
            placeholder="请粘贴客户资料，建议包含：\n• 出镜称呼\n• 店铺/企业名称\n• 城市（不需要具体门牌号）\n• 主营业务\n• 核心卖点\n• 真实故事/经历（100字以上）",
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.caption(f"已输入 {len(raw_data)} 字")
        with col2:
            if st.button("✨ 生成30条文案", use_container_width=True, type="primary"):
                if len(raw_data) < 30:
                    st.error("请填写完整的客户资料（至少30字）")
                else:
                    st.session_state.raw_data_cache = raw_data
                    with st.spinner("正在生成文案..."):
                        configs = [{'idx': i+1, 'style': STYLES[i%6], 'angle': ANGLES[i%8], 'hook': HOOKS[i%8]} for i in range(30)]
                        st.session_state.copywrites = []
                        progress_bar = st.progress(0)
                        
                        for i, config in enumerate(configs):
                            result = generate_single_copywrite(raw_data, config, industry, length)
                            if result:
                                st.session_state.copywrites.append(result)
                            else:
                                st.session_state.copywrites.append({
                                    'index': config['idx'], 'content': "生成失败", 'word_count': 0,
                                    'quality_pass': False, 'length_type': length,
                                    'style': config['style'], 'angle': config['angle'],
                                    'hook': config['hook'], 'issues': ["API调用失败"]
                                })
                            progress_bar.progress((i + 1) / 30)
                        
                        progress_bar.empty()
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 结果显示
        if st.session_state.copywrites:
            # 统计
            total = len(st.session_state.copywrites)
            passed = sum(1 for c in st.session_state.copywrites if c['quality_pass'])
            failed = sum(1 for c in st.session_state.copywrites if c['word_count'] == 0)
            need_opt = total - passed - failed
            
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            cols = st.columns(4)
            stats = [
                ("📊 总数", total, "#667eea"),
                ("✅ 达标", passed, "#10b981"),
                ("⚠️ 需优化", need_opt, "#f59e0b"),
                ("❌ 失败", failed, "#ef4444")
            ]
            for i, (label, value, color) in enumerate(stats):
                with cols[i]:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 15px; background: rgba({','.join(str(int(color.lstrip('#')[i:i+2], 16)) for i in (0, 2, 4))},0.1); border-radius: 12px;">
                        <div style="font-size: 32px; font-weight: 700; color: {color};">{value}</div>
                        <div style="font-size: 12px; color: #6b7280;">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 文案卡片
            for item in st.session_state.copywrites:
                is_fail = item['word_count'] == 0
                card_class = "fail" if is_fail else ("success" if item['quality_pass'] else "")
                len_class = "tag-green" if item['length_type'] == 'long' else "tag-orange"
                len_name = "长" if item['length_type'] == 'long' else "短"
                
                st.markdown(f"""
                <div class="copy-card {card_class}">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <div>
                            <span style="font-size:24px; font-weight:bold; color:#e5e7eb; margin-right:8px;">#{item['index']}</span>
                            <span class="tag tag-purple">{item['style']}</span>
                            <span class="tag tag-blue">{item['angle']}</span>
                            <span class="tag {len_class}">{len_name} {item['word_count']}字</span>
                            {"<span style='color:#10b981; margin-left:8px;'>✓ 合格</span>" if item['quality_pass'] else "<span style='color:#f59e0b; margin-left:8px;'>⚠ 需优化</span>" if not is_fail else "<span style='color:#ef4444; margin-left:8px;'>✗ 失败</span>"}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                content_key = f"content_{item['index']}"
                if content_key not in st.session_state:
                    st.session_state[content_key] = item['content']
                
                new_content = st.text_area(
                    f"文案 #{item['index']}",
                    value=st.session_state[content_key],
                    key=content_key,
                    height=80,
                    label_visibility="collapsed"
                )
                
                btn_cols = st.columns([1, 1, 1, 4])
                with btn_cols[0]:
                    if st.button("📋 复制", key=f"copy_{item['index']}"):
                        st.toast(f"#{item['index']} 已复制！")
                
                with btn_cols[1]:
                    if is_fail or item['word_count'] < 120:
                        if st.button("🔄 重试", key=f"retry_{item['index']}"):
                            with st.spinner(f"重新生成 #{item['index']}..."):
                                new_item = generate_single_copywrite(
                                    st.session_state.raw_data_cache,
                                    {'idx': item['index'], 'style': item['style'], 
                                     'angle': item['angle'], 'hook': item['hook']},
                                    industry, item['length_type']
                                )
                                if new_item:
                                    idx = item['index'] - 1
                                    st.session_state.copywrites[idx] = new_item
                                    st.rerun()
                
                with btn_cols[2]:
                    if item['quality_pass']:
                        target_len = 'long' if item['length_type'] == 'short' else 'short'
                        btn_text = "📖 长文案" if target_len == 'long' else "⚡ 短文案"
                        if st.button(btn_text, key=f"switch_{item['index']}"):
                            with st.spinner(f"切换长度 #{item['index']}..."):
                                new_item = generate_single_copywrite(
                                    st.session_state.raw_data_cache,
                                    {'idx': item['index'], 'style': item['style'],
                                     'angle': item['angle'], 'hook': item['hook']},
                                    industry, target_len
                                )
                                if new_item:
                                    idx = item['index'] - 1
                                    st.session_state.copywrites[idx] = new_item
                                    st.rerun()
                
                if item.get('issues'):
                    st.warning("⚠️ " + "，".join(item['issues']))
                
                st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
