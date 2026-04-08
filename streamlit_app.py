import streamlit as st
import json
import re
import time
import hashlib
from datetime import datetime
from openai import OpenAI
from sensitive_words import check_sensitive_words

# 页面配置
st.set_page_config(
    page_title="晓牧传媒文案助手 v4.1",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 密码验证
def check_password():
    """返回 True 如果密码正确"""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    if st.session_state["password_correct"]:
        return True
    
    # 登录界面
    st.title("🔐 晓牧传媒文案助手")
    st.caption("v4.1 · 请先登录")
    
    with st.form("login_form"):
        password = st.text_input("请输入密码", type="password")
        submitted = st.form_submit_button("🔓 登录", use_container_width=True)
        
        if submitted:
            # 密码是 88886666 的 SHA256
            if hashlib.sha256(password.encode()).hexdigest() == \
               "8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ 密码错误，请重试")
    
    return False

# 样式
st.markdown("""
<style>
    .main { padding: 2rem; }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 0.75rem;
        font-weight: 600;
    }
    .copy-card {
        background: white;
        border-radius: 1rem;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    .copy-card.success { border-left-color: #10b981; }
    .copy-card.fail { border-left-color: #ef4444; background: #fef2f2; }
    .tag {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-right: 0.5rem;
    }
    .tag-purple { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
    .tag-blue { background: #e0e7ff; color: #4338ca; }
    .tag-orange { background: #fef3c7; color: #92400e; }
    .tag-green { background: #d1fae5; color: #065f46; }
</style>
""", unsafe_allow_html=True)

# 行业配置
INDUSTRIES = {
    "catering": {
        "name": "餐饮",
        "description": "突出食材新鲜、口味独特、环境卫生、顾客好评",
        "forbidden": ["减肥", "治疗", "疗效", "疗程"]
    },
    "woodwork": {
        "name": "木作定制",
        "description": "强调工艺精湛、材质环保、设计独特、服务周到",
        "forbidden": ["最环保", "零甲醛", "绝对", "完全"]
    },
    "factory": {
        "name": "工厂/制造",
        "description": "展现生产实力、质量把控、交货准时、客户信赖",
        "forbidden": ["第一", "最大", "最强", "垄断"]
    },
    "lottery": {
        "name": "彩票店",
        "description": "分享中奖故事、客户好运、经营趣事，不卖梦想只讲故事",
        "forbidden": ["必中", "稳赚", "包赢", "内部消息", "预测"]
    },
    "hotel": {
        "name": "酒店/民宿",
        "description": "描述温馨环境、贴心服务、独特体验、客人好评",
        "forbidden": ["最便宜", "最低价", "顶级", "奢华无比"]
    },
    "general": {
        "name": "通用",
        "description": "根据行业特点，突出核心优势和真实故事",
        "forbidden": []
    }
}

# 配置组合
STYLES = ["轻松", "温馨", "真诚", "励志", "接地气", "怀旧"]
ANGLES = [
    "个人故事", "顾客见证", "行业见解", "创业历程", 
    "日常趣事", "价值观分享", "对比反差", "情感共鸣"
]
HOOKS = [
    "悬念疑问", "惊人数据", "情感共鸣", "直接开场",
    "故事引入", "痛点直击", "反差对比", "热点借势"
]

# Kimi API
KIMI_API_KEY = "sk-IA6qyNJFSYC8UB9RHnGHsgz24VWSrKalSnd5nTTbJNiqQ2uu"

@st.cache_resource
def get_kimi_client():
    return OpenAI(
        api_key=KIMI_API_KEY,
        base_url="https://api.moonshot.cn/v1"
    )

def call_kimi(prompt, max_tokens=600, timeout=35):
    """调用 Kimi API"""
    try:
        client = get_kimi_client()
        response = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是短视频文案专家，擅长写150-180字的短文案。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.8
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"ERROR: {str(e)}"

def generate_single_copywrite(raw_data, config, industry="general", length="short", retries=3):
    """生成单条文案"""
    industry_info = INDUSTRIES.get(industry, INDUSTRIES["general"])
    
    # 提取称呼
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
6. 不要用任何夸张或绝对化词汇

直接写文案："""
        
        result = call_kimi(prompt, max_tokens=600, timeout=35)
        if not result.startswith("ERROR:"):
            content = result.strip()
            word_count = len(content.replace(' ', '').replace('\n', ''))
            name_count = content.count(name)
            has_address = bool(re.search(r'[路街道]\s*\d+[号]', content))
            
            # 质量检查
            issues = []
            if word_count < min_words:
                issues.append(f"字数不足({word_count}字)")
            elif word_count > max_words:
                issues.append(f"字数超标({word_count}字)")
            if has_address:
                issues.append("有具体地址")
            if name_count > 3:
                issues.append(f"称呼{name}出现{name_count}次")
            
            # 敏感词检查
            sensitive = check_sensitive_words(content)
            if sensitive:
                issues.append(f"敏感词: {', '.join(sensitive[:3])}")
            
            quality_pass = min_words <= word_count <= max_words and not has_address and len(sensitive) == 0
            
            return {
                'index': config['idx'],
                'content': content,
                'word_count': word_count,
                'name_count': name_count,
                'quality_pass': quality_pass,
                'length_type': length,
                'style': config['style'],
                'angle': config['angle'],
                'hook': config['hook'],
                'issues': issues
            }
    return None

def generate_all_copywrites(raw_data, industry="general", length="short"):
    """生成30条文案"""
    configs = []
    for i in range(30):
        configs.append({
            'idx': i + 1,
            'style': STYLES[i % len(STYLES)],
            'angle': ANGLES[i % len(ANGLES)],
            'hook': HOOKS[i % len(HOOKS)]
        })
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, config in enumerate(configs):
        status_text.text(f"生成第 {i+1}/30 条...")
        result = generate_single_copywrite(raw_data, config, industry, length)
        if result:
            results.append(result)
        else:
            results.append({
                'index': config['idx'],
                'content': "生成失败",
                'word_count': 0,
                'quality_pass': False,
                'length_type': length,
                'style': config['style'],
                'angle': config['angle'],
                'hook': config['hook'],
                'issues': ["API调用失败"]
            })
        progress_bar.progress((i + 1) / 30)
    
    progress_bar.empty()
    status_text.empty()
    return results

def main():
    if not check_password():
        st.stop()
    
    # 标题
    st.title("✍️ 晓牧传媒文案助手 v4.1")
    st.caption("短文案默认(150-180字) · 支持切换长度 · 敏感词检测")
    
    # 初始化
    if 'copywrites' not in st.session_state:
        st.session_state.copywrites = []
    if 'raw_data_cache' not in st.session_state:
        st.session_state.raw_data_cache = ""
    
    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 配置")
        industry = st.selectbox(
            "🏭 行业类型",
            options=list(INDUSTRIES.keys()),
            format_func=lambda x: INDUSTRIES[x]['name'],
            index=5  # 默认通用
        )
        st.caption(INDUSTRIES[industry]['description'])
        
        st.divider()
        st.markdown("**生成设置**")
        length = st.radio(
            "文案长度",
            ["short", "long"],
            format_func=lambda x: "短文案 (150-180字)" if x == "short" else "长文案 (200-300字)",
            index=0
        )
        
        st.divider()
        if st.session_state.copywrites:
            if st.button("🚨 检测敏感词", use_container_width=True):
                with st.spinner("检测中..."):
                    total_sensitive = 0
                    affected = 0
                    for cw in st.session_state.copywrites:
                        found = check_sensitive_words(cw.get('content', ''))
                        if found:
                            total_sensitive += len(found)
                            affected += 1
                    
                    if affected > 0:
                        st.error(f"发现 {total_sensitive} 个敏感词，涉及 {affected} 条文案")
                    else:
                        st.success("✅ 未检测到敏感词")
        
        if st.session_state.copywrites:
            if st.button("📋 复制全部", use_container_width=True):
                text = "\n\n".join([
                    f"【{cw['style']}·{cw['angle']}·{'长' if cw['length_type']=='long' else '短'}】\n{cw['content']}"
                    for cw in st.session_state.copywrites
                ])
                st.code(text, language=None)
                st.toast("已复制到剪贴板！")
    
    # 主界面 - 输入区
    with st.container():
        st.subheader("📝 客户资料")
        raw_data = st.text_area(
            "直接粘贴客户资料",
            height=200,
            placeholder="请粘贴客户资料，建议包含：\n• 出镜称呼\n• 店铺/企业名称\n• 城市（不需要具体门牌号）\n• 主营业务\n• 核心卖点\n• 真实故事/经历（100字以上）"
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
                        st.session_state.copywrites = generate_all_copywrites(
                            raw_data, industry, length
                        )
                    st.rerun()
    
    # 结果显示
    if st.session_state.copywrites:
        st.divider()
        st.subheader("📊 生成结果")
        
        # 统计
        total = len(st.session_state.copywrites)
        passed = sum(1 for c in st.session_state.copywrites if c['quality_pass'])
        failed = sum(1 for c in st.session_state.copywrites if c['word_count'] == 0)
        need_opt = total - passed - failed
        
        cols = st.columns(4)
        cols[0].metric("总数", total)
        cols[1].metric("✓ 达标", passed)
        cols[2].metric("⚠ 需优化", need_opt)
        cols[3].metric("✗ 失败", failed)
        
        st.divider()
        
        # 文案卡片
        for item in st.session_state.copywrites:
            is_fail = item['word_count'] == 0
            is_short_fail = item['word_count'] < 120 and not is_fail
            card_class = "fail" if is_fail else ("success" if item['quality_pass'] else "")
            len_class = "tag-green" if item['length_type'] == 'long' else "tag-orange"
            len_name = "长" if item['length_type'] == 'long' else "短"
            
            with st.container():
                st.markdown(f"""
                <div class="copy-card {card_class}">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                        <div>
                            <span style="font-size:1.5rem;font-weight:bold;color:#e5e7eb;margin-right:0.5rem;">#{item['index']}</span>
                            <span class="tag tag-purple">{item['style']}</span>
                            <span class="tag tag-blue">{item['angle']}</span>
                            <span class="tag {len_class}">{len_name} {item['word_count']}字</span>
                            {"<span style='color:#10b981;margin-left:0.5rem;'>✓ 合格</span>" if item['quality_pass'] else "<span style='color:#f59e0b;margin-left:0.5rem;'>⚠ 需优化</span>" if not is_fail else "<span style='color:#ef4444;margin-left:0.5rem;'>✗ 失败</span>"}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 文案内容
                content_key = f"content_{item['index']}"
                if content_key not in st.session_state:
                    st.session_state[content_key] = item['content']
                
                new_content = st.text_area(
                    f"文案 #{item['index']}",
                    value=st.session_state[content_key],
                    key=content_key,
                    height=100,
                    label_visibility="collapsed"
                )
                
                # 操作按钮
                btn_cols = st.columns([1, 1, 1, 4])
                with btn_cols[0]:
                    if st.button("📋 复制", key=f"copy_{item['index']}"):
                        st.toast(f"#{item['index']} 已复制！")
                
                with btn_cols[1]:
                    # 只有严重失败才显示重新生成
                    if is_fail or item['word_count'] < 120:
                        if st.button("🔄 重试", key=f"retry_{item['index']}"):
                            with st.spinner(f"重新生成 #{item['index']}..."):
                                new_item = generate_single_copywrite(
                                    st.session_state.raw_data_cache,
                                    {
                                        'idx': item['index'],
                                        'style': item['style'],
                                        'angle': item['angle'],
                                        'hook': item['hook']
                                    },
                                    industry,
                                    item['length_type']
                                )
                                if new_item:
                                    idx = item['index'] - 1
                                    st.session_state.copywrites[idx] = new_item
                                    st.rerun()
                
                with btn_cols[2]:
                    # 长度切换
                    if item['quality_pass']:
                        target_len = 'long' if item['length_type'] == 'short' else 'short'
                        btn_text = "📖 长文案" if target_len == 'long' else "⚡ 短文案"
                        if st.button(btn_text, key=f"switch_{item['index']}"):
                            with st.spinner(f"切换长度 #{item['index']}..."):
                                new_item = generate_single_copywrite(
                                    st.session_state.raw_data_cache,
                                    {
                                        'idx': item['index'],
                                        'style': item['style'],
                                        'angle': item['angle'],
                                        'hook': item['hook']
                                    },
                                    industry,
                                    target_len
                                )
                                if new_item:
                                    idx = item['index'] - 1
                                    st.session_state.copywrites[idx] = new_item
                                    st.rerun()
                
                # 显示问题
                if item.get('issues'):
                    st.warning("⚠️ " + "，".join(item['issues']))
                
                st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
