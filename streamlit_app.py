# -*- coding: utf-8 -*-
"""
晓牧传媒文案助手 v4.2
修复版 - 优化代码质量和UI设计
"""
import streamlit as st
import re
import time
from openai import OpenAI
from sensitive_words import check_sensitive_words

# ========== 页面配置 ==========
st.set_page_config(
    page_title="晓牧传媒文案助手",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 基础样式 ==========
st.markdown("""
<style>
    .stApp { background: #f8fafc; }
    .main { max-width: 1400px; margin: 0 auto; }
    h1 { color: #1e293b !important; font-size: 1.75rem !important; font-weight: 700 !important; }
    .stButton>button { border-radius: 8px; font-weight: 500; }
    .stButton>button[kind="primary"] { background: linear-gradient(135deg, #667eea, #764ba2); }
    div[data-testid="stMetricValue"] { font-size: 1.5rem !important; }
</style>
""", unsafe_allow_html=True)

# ========== 配置数据 ==========
INDUSTRIES = {
    "catering": "餐饮",
    "woodwork": "木作定制",
    "factory": "工厂/制造",
    "lottery": "彩票店",
    "hotel": "酒店/民宿",
    "general": "通用"
}

CONTENT_TYPES = {
    "干货避坑": {"emoji": "💡", "color": "🔴", "desc": "揭露行业内幕、避坑指南"},
    "人设故事": {"emoji": "👤", "color": "🟣", "desc": "老板个人经历、创业故事"},
    "细节特写": {"emoji": "🔍", "color": "🟡", "desc": "产品工艺的具体细节"},
    "认知反转": {"emoji": "💫", "color": "🟢", "desc": "颠覆常识、打破认知"}
}

KIMI_KEY = "sk-IA6qyNJFSYC8UB9RHnGHsgz24VWSrKalSnd5nTTbJNiqQ2uu"

# ========== API客户端 ==========
@st.cache_resource
def get_client():
    """获取Kimi API客户端（带缓存）"""
    return OpenAI(api_key=KIMI_KEY, base_url="https://api.moonshot.cn/v1")

# ========== 文案生成函数 ==========
def generate_single_copywrite(raw_data: str, idx: int, length: str = "short", retries: int = 2) -> dict:
    """
    生成单条文案
    
    Args:
        raw_data: 客户原始资料
        idx: 文案序号（1-30）
        length: 长度类型 short/long
        retries: 重试次数
    
    Returns:
        dict: 包含文案内容、字数、质量状态等
    """
    # 提取称呼
    name_match = re.search(r'出镜称呼[：:]\s*(\S+)', raw_data)
    name = name_match.group(1) if name_match else "老板"
    
    # 字数限制
    min_w, max_w = (150, 180) if length == "short" else (200, 300)
    
    # 内容类型循环分配
    ctypes = list(CONTENT_TYPES.keys())
    ctype = ctypes[(idx - 1) % 4]
    
    # Prompt构建
    prompt = f"""创作第{idx}条短视频文案（{ctype}类型）。

【出镜称呼】{name}
【客户资料】{raw_data[:500]}

【写作要求】
1. 字数严格控制在 {min_w}-{max_w} 字
2. 开头必须吸引人，禁止自我介绍和店名
3. "{name}" 出现不超过 2 次，多用"我""咱"
4. 必须包含 1 个具体数字或感官细节
5. 禁止具体地址如"XX路XX号"
6. 口语化，真实自然

直接输出文案内容："""

    system_msg = """你是短视频文案大师。严格遵循：
- 黄金三秒：严禁自我介绍、店名、经营地址
- 语义降维：禁用"匠心""高端""专业""品质"，必须具象化描述
- 开头用利益/冲突/悬念/扎心四选一"""

    for attempt in range(retries):
        try:
            client = get_client()
            resp = client.chat.completions.create(
                model="moonshot-v1-8k",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.85,
                timeout=30
            )
            
            content = resp.choices[0].message.content.strip().strip('"').strip("'")
            
            # 字数计算（去除空格和换行）
            word_count = len(content.replace(' ', '').replace('\n', ''))
            
            # 质量检查
            name_count = content.count(name)
            has_address = bool(re.search(r'[路街道]\s*\d+[号]', content))
            has_intro = bool(re.search(r'^(大家好|我是|我叫|我们店|我们这里是)', content))
            sensitive_words = check_sensitive_words(content)
            
            # 问题列表
            issues = []
            if word_count < min_w:
                issues.append(f"字数不足({word_count}字)")
            elif word_count > max_w:
                issues.append(f"字数超标({word_count}字)")
            if has_address:
                issues.append("含具体地址")
            if has_intro:
                issues.append("开头有自我介绍")
            if name_count > 2:
                issues.append(f"称呼出现{name_count}次")
            if sensitive_words:
                issues.append(f"敏感词:{','.join(sensitive_words[:2])}")
            
            # 质量通过标准
            quality_pass = (
                min_w <= word_count <= max_w and
                not has_address and
                not has_intro and
                name_count <= 2 and
                not sensitive_words
            )
            
            return {
                'idx': idx,
                'content': content,
                'word_count': word_count,
                'quality_pass': quality_pass,
                'content_type': ctype,
                'length_type': length,
                'issues': issues,
                'error': None
            }
            
        except Exception as e:
            error_msg = str(e)
            if attempt == retries - 1:  # 最后一次失败
                return {
                    'idx': idx,
                    'content': f"⚠️ 生成失败: {error_msg[:40]}{'...' if len(error_msg) > 40 else ''}",
                    'word_count': 0,
                    'quality_pass': False,
                    'content_type': ctype,
                    'length_type': length,
                    'issues': ["API调用失败，请检查网络或稍后重试"],
                    'error': error_msg
                }
            time.sleep(1)  # 重试前等待
    
    return None

# ========== 会话状态初始化 ==========
def init_session_state():
    """初始化所有会话状态变量"""
    defaults = {
        'items': [],
        'raw_data': '',
        'industry': 'general',
        'length': 'short',
        'is_generating': False,
        'generation_error': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state or st.session_state[key] is None:
            st.session_state[key] = value

# ========== 主应用 ==========
def main():
    # 初始化
    init_session_state()
    
    # ========== 顶部标题 ==========
    st.title("✨ 晓牧传媒文案助手")
    st.caption("AI驱动短视频文案生成工具 v4.2 | 30条文案一键生成")
    
    # ========== 布局：左侧配置 + 右侧主内容 ==========
    left_col, right_col = st.columns([280, 1])
    
    # ========== 左侧：配置面板 ==========
    with left_col:
        with st.container():
            st.markdown("#### ⚙️ 配置")
            
            # 行业选择
            industry = st.selectbox(
                "行业类型",
                options=list(INDUSTRIES.keys()),
                format_func=lambda x: f"{INDUSTRIES[x]}",
                index=5,
                key="industry_select"
            )
            st.session_state.industry = industry
            
            st.markdown("---")
            
            # 长度选择
            length = st.radio(
                "文案长度",
                options=["short", "long"],
                format_func=lambda x: "📄 短文案 (150-180字)" if x == "short" else "📖 长文案 (200-300字)",
                key="length_select"
            )
            st.session_state.length = length
            
            st.markdown("---")
            
            # 内容类型说明
            with st.expander("📚 内容类型说明"):
                for ctype, info in CONTENT_TYPES.items():
                    st.markdown(f"**{info['emoji']} {ctype}**")
                    st.caption(info['desc'])
            
            # 工具按钮（有结果时才显示）
            if isinstance(st.session_state.items, list) and len(st.session_state.items) > 0:
                st.markdown("---")
                st.markdown("#### 🛠️ 工具")
                
                # 复制全部
                if st.button("📋 复制全部文案", use_container_width=True):
                    all_text = "\n\n" + "\n\n".join([
                        f"【{item['content_type']}】文案 #{item['idx']}\n{item['content']}"
                        for item in st.session_state.items
                    ])
                    st.code(all_text, language=None)
                    st.toast("✅ 全部文案已生成，可复制上方文本")
                
                # 清空结果
                if st.button("🗑️ 清空结果", use_container_width=True):
                    st.session_state.items = []
                    st.session_state.raw_data = ''
                    st.rerun()
    
    # ========== 右侧：主内容区 ==========
    with right_col:
        # ----- 输入区 -----
        st.markdown("#### 📝 客户资料")
        
        raw_data = st.text_area(
            "客户资料输入",
            height=140,
            value=st.session_state.raw_data,
            placeholder="请粘贴客户资料（建议100字以上，内容越详细生成效果越好）：\n\n• 出镜称呼：如王老板、李姐\n• 店铺/企业名称\n• 所在城市（不需要具体门牌号）\n• 主营业务、核心卖点\n• 真实故事或经历",
            key="raw_data_input"
        )
        st.session_state.raw_data = raw_data
        
        # 输入统计和生成按钮
        col_stat, col_btn = st.columns([5, 1])
        with col_stat:
            word_count = len(raw_data.replace(' ', '').replace('\n', ''))
            st.caption(f"📊 已输入 {word_count} 字 {'✅' if word_count >= 30 else '⚠️ 至少30字'}")
        with col_btn:
            can_generate = word_count >= 30 and not st.session_state.is_generating
            if st.button(
                "✨ 生成30条" if not st.session_state.is_generating else "⏳ 生成中...",
                type="primary",
                disabled=not can_generate,
                use_container_width=True
            ):
                st.session_state.is_generating = True
                st.session_state.generation_error = None
                st.rerun()
        
        # ----- 生成处理 -----
        if st.session_state.is_generating:
            with st.spinner("🚀 AI正在生成文案，请稍候..."):
                progress_bar = st.progress(0, text="准备生成...")
                st.session_state.items = []
                
                try:
                    for i in range(30):
                        result = generate_single_copywrite(
                            raw_data=st.session_state.raw_data,
                            idx=i + 1,
                            length=st.session_state.length
                        )
                        if result:
                            st.session_state.items.append(result)
                        
                        # 更新进度
                        progress = (i + 1) / 30
                        progress_bar.progress(progress, text=f"生成中... {i+1}/30 ({int(progress*100)}%)")
                        
                    st.toast(f"✅ 成功生成 {len(st.session_state.items)} 条文案！")
                    
                except Exception as e:
                    st.session_state.generation_error = str(e)
                    st.error(f"❌ 生成过程中出错: {str(e)}")
                
                finally:
                    progress_bar.empty()
                    st.session_state.is_generating = False
                    st.rerun()
        
        # 显示错误信息
        if st.session_state.generation_error:
            st.error(f"❌ 错误详情: {st.session_state.generation_error}")
        
        # ----- 结果显示 -----
        if isinstance(st.session_state.items, list) and len(st.session_state.items) > 0:
            st.markdown("---")
            st.markdown("#### 📊 生成结果")
            
            # 统计概览
            items = st.session_state.items
            total = len(items)
            quality_ok = sum(1 for item in items if item.get('quality_pass', False))
            failed = sum(1 for item in items if item.get('word_count', 0) == 0)
            need_fix = total - quality_ok - failed
            
            stat_cols = st.columns(4)
            stats = [
                ("📊 总数", total, "#64748b"),
                ("✅ 优质", quality_ok, "#22c55e"),
                ("⚠️ 需优化", need_fix, "#f59e0b"),
                ("❌ 失败", failed, "#ef4444")
            ]
            
            for col, (label, value, color) in zip(stat_cols, stats):
                with col:
                    st.metric(label=label, value=value)
            
            st.markdown("---")
            st.markdown("#### 📝 文案列表")
            
            # 文案网格展示（每行3个）
            for row_idx in range(0, len(items), 3):
                cols = st.columns(3)
                for col_idx, col in enumerate(cols):
                    item_idx = row_idx + col_idx
                    if item_idx >= len(items):
                        break
                    
                    item = items[item_idx]
                    
                    with col:
                        # 判断状态
                        is_failed = item.get('word_count', 0) == 0
                        is_warning = not item.get('quality_pass', False) and not is_failed
                        
                        # 状态图标
                        if item.get('quality_pass', False):
                            status_icon = "✅"
                            status_color = "green"
                        elif is_failed:
                            status_icon = "❌"
                            status_color = "red"
                        else:
                            status_icon = "⚠️"
                            status_color = "orange"
                        
                        # 内容类型信息
                        ctype = item.get('content_type', '通用')
                        ctype_info = CONTENT_TYPES.get(ctype, {"emoji": "💬", "color": "⚪"})
                        
                        # 使用expander作为卡片
                        with st.expander(
                            f"{ctype_info['emoji']} #{item['idx']} {ctype} {status_icon} ({item.get('word_count', 0)}字)",
                            expanded=False
                        ):
                            # 文案内容
                            st.markdown("**文案内容：**")
                            st.info(item.get('content', '无内容'))
                            
                            # 问题提示
                            if item.get('issues'):
                                st.warning("⚠️ " + " | ".join(item['issues']))
                            
                            # 操作按钮
                            btn_cols = st.columns([1, 1, 1])
                            
                            with btn_cols[0]:
                                if st.button("📋 复制", key=f"copy_{item_idx}", use_container_width=True):
                                    st.toast(f"✅ 已复制文案 #{item['idx']}")
                            
                            with btn_cols[1]:
                                # 失败或字数不足时显示重试
                                if (is_failed or item.get('word_count', 0) < 120):
                                    if st.button("🔄 重试", key=f"retry_{item_idx}", use_container_width=True):
                                        with st.spinner(f"重新生成 #{item['idx']}..."):
                                            new_item = generate_single_copywrite(
                                                raw_data=st.session_state.raw_data,
                                                idx=item['idx'],
                                                length=item.get('length_type', 'short')
                                            )
                                            if new_item:
                                                st.session_state.items[item_idx] = new_item
                                                st.rerun()
                            
                            with btn_cols[2]:
                                # 质量合格时可以切换长度
                                if item.get('quality_pass', False):
                                    current_len = item.get('length_type', 'short')
                                    target_len = 'long' if current_len == 'short' else 'short'
                                    btn_label = "📖 转长" if target_len == 'long' else "⚡ 转短"
                                    
                                    if st.button(btn_label, key=f"switch_{item_idx}", use_container_width=True):
                                        with st.spinner(f"切换长度 #{item['idx']}..."):
                                            new_item = generate_single_copywrite(
                                                raw_data=st.session_state.raw_data,
                                                idx=item['idx'],
                                                length=target_len
                                            )
                                            if new_item:
                                                st.session_state.items[item_idx] = new_item
                                                st.rerun()

# ========== 运行应用 ==========
if __name__ == "__main__":
    main()
