# -*- coding: utf-8 -*-
import streamlit as st
import re
import io
from openai import OpenAI
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

st.set_page_config(page_title="晓牧传媒文案助手", page_icon="📝", layout="wide")

# CSS
st.markdown("""
<style>
    .main { max-width: 1200px; margin: 0 auto; padding: 2rem; }
    h1 { color: #1a1a2e !important; font-weight: 700 !important; }
    .header-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem; border-radius: 16px; margin-bottom: 2rem; color: white;
    }
    .copy-card {
        background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06); border-left: 4px solid #667eea;
    }
    .copy-card.success { border-left-color: #10b981; }
    .copy-card.warning { border-left-color: #f59e0b; }
    .copy-card.error { border-left-color: #ef4444; }
    .tag { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 20px;
           font-size: 0.75rem; font-weight: 600; margin-right: 0.5rem; }
    .tag-blue { background: #dbeafe; color: #1e40af; }
    .tag-purple { background: #f3e8ff; color: #7c3aed; }
    .tag-orange { background: #ffedd5; color: #9a3412; }
    .tag-green { background: #d1fae5; color: #065f46; }
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important; border-radius: 10px !important;
        padding: 1rem 2rem !important; font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# 配置
INDUSTRIES = ["餐饮", "木作定制", "工厂/制造", "彩票店", "酒店/民宿", "通用"]
CONTENT_TYPES = ["干货避坑", "人设故事", "细节特写", "认知反转"]
KIMI_KEY = "sk-IA6qyNJFSYC8UB9RHnGHsgz24VWSrKalSnd5nTTbJNiqQ2uu"

# 初始化
def init_state():
    if 'items' not in st.session_state:
        st.session_state.items = []
    if 'generating' not in st.session_state:
        st.session_state.generating = False

init_state()

@st.cache_resource
def get_client():
    return OpenAI(api_key=KIMI_KEY, base_url="https://api.moonshot.cn/v1")

def generate_copywrite(raw_data, idx, length):
    name_match = re.search(r'出镜称呼[：:]\s*(\S+)', raw_data)
    name = name_match.group(1) if name_match else "老板"
    min_w, max_w = (150, 180) if length == "short" else (200, 300)
    ctype = CONTENT_TYPES[(idx - 1) % 4]
    
    try:
        client = get_client()
        resp = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是短视频文案大师。黄金三秒：严禁自我介绍、店名、地址。语义降维：禁用匠心/高端/专业。"},
                {"role": "user", "content": f"创作第{idx}条{ctype}文案。称呼：{name} 资料：{raw_data[:400]} 要求:1.字数{min_w}-{max_w} 2.禁止自我介绍 3.包含1个具体数字"}
            ],
            max_tokens=400, temperature=0.85, timeout=30
        )
        content = resp.choices[0].message.content.strip().strip('"')
        wc = len(content.replace(' ', '').replace('\n', ''))
        ok = min_w <= wc <= max_w and not re.search(r'[路街道]\s*\d+[号]', content)
        return {'idx': idx, 'content': content, 'wc': wc, 'ok': ok, 'type': ctype}
    except Exception as e:
        return {'idx': idx, 'content': f"生成失败: {str(e)[:30]}", 'wc': 0, 'ok': False, 'type': ctype}

def create_word_doc(items):
    doc = Document()
    title = doc.add_heading('晓牧传媒文案生成结果', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    ok_count = sum(1 for i in items if i.get('ok'))
    doc.add_paragraph(f'生成总数: {len(items)} 条')
    doc.add_paragraph(f'优质文案: {ok_count} 条')
    doc.add_paragraph()
    
    for item in items:
        p = doc.add_paragraph()
        run = p.add_run(f"【{item['type']}】文案 #{item['idx']}")
        run.bold = True
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(102, 126, 234)
        
        doc.add_paragraph(item['content'])
        
        status = "优质" if item.get('ok') else "失败" if item.get('wc', 0) == 0 else "需优化"
        status_p = doc.add_paragraph(f'状态: {status} | 字数: {item.get("wc", 0)} 字')
        status_p.runs[0].font.size = Pt(9)
        status_p.runs[0].font.color.rgb = RGBColor(128, 128, 128)
        
        doc.add_paragraph('_' * 50)
    
    doc_io = io.BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)
    return doc_io.getvalue()

# 头部
st.markdown("""
<div class="header-section">
    <h1 style="color: white; margin: 0;">晓牧传媒文案助手</h1>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">AI驱动 · 30条爆款文案一键生成</p>
</div>
""", unsafe_allow_html=True)

# 配置
st.markdown("### 配置参数")
col1, col2 = st.columns(2)
with col1:
    industry = st.selectbox("行业类型", INDUSTRIES, index=5)
with col2:
    length = st.radio("文案长度", ["短文案(150-180字)", "长文案(200-300字)"], horizontal=True)

# 输入
st.markdown("### 客户资料")
raw_data = st.text_area(
    "输入",
    height=150,
    placeholder="请粘贴客户资料：出镜称呼、店铺名称、主营业务、真实故事...",
    label_visibility="collapsed"
)

word_count = len(raw_data.replace(' ', '').replace('\n', ''))
st.caption(f"已输入 {word_count} 字")

# 生成按钮
col_btn, col_info = st.columns([1, 4])
with col_btn:
    generate_clicked = st.button("生成30条文案", type="primary", use_container_width=True)

# 处理生成
if generate_clicked:
    if word_count < 30:
        st.error("资料至少30字")
    else:
        with st.spinner("AI生成中..."):
            progress_bar = st.progress(0)
            new_items = []
            length_type = "short" if "短" in length else "long"
            
            for i in range(30):
                result = generate_copywrite(raw_data, i + 1, length_type)
                new_items.append(result)
                progress_bar.progress((i + 1) / 30)
            
            st.session_state.items = new_items
            st.success(f"成功生成 {len(new_items)} 条文案！")

# 显示结果
if isinstance(st.session_state.get('items'), list) and len(st.session_state.items) > 0:
    st.markdown("---")
    st.markdown("### 生成结果")
    
    items = st.session_state.items or []
    total = len(items)
    ok_count = sum(1 for i in items if i.get('ok'))
    fail_count = sum(1 for i in items if i.get('wc', 0) == 0)
    warn_count = total - ok_count - fail_count
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("总数", total)
    c2.metric("优质", ok_count)
    c3.metric("需优化", warn_count)
    c4.metric("失败", fail_count)
    
    # 操作按钮
    col_download, col_clear = st.columns([1, 4])
    with col_download:
        word_bytes = create_word_doc(items)
        st.download_button(
            label="下载Word文档",
            data=word_bytes,
            file_name=f"文案_{industry}_{total}条.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    with col_clear:
        if st.button("清空结果", use_container_width=True):
            st.session_state.items = []
            st.rerun()
    
    # 文案列表
    st.markdown("#### 文案详情")
    
    for item in items:
        is_ok = item.get('ok', False)
        is_fail = item.get('wc', 0) == 0
        card_class = "success" if is_ok else "error" if is_fail else "warning"
        
        type_idx = (item.get('idx', 1) - 1) % 4
        tag_class = ["tag-blue", "tag-purple", "tag-orange", "tag-green"][type_idx]
        status_icon = "✅" if is_ok else "❌" if is_fail else "⚠️"
        
        st.markdown(f"""
        <div class="copy-card {card_class}">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                <div>
                    <span style="font-weight:700; color:#667eea; margin-right:0.5rem;">#{item.get('idx')}</span>
                    <span class="tag {tag_class}">{item.get('type')}</span>
                    <span style="color:#9ca3af; font-size:0.875rem;">{item.get('wc', 0)}字</span>
                </div>
                <span style="font-size:1.25rem;">{status_icon}</span>
            </div>
            <div style="line-height:1.7; color:#374151;">{item.get('content')}</div>
        </div>
        """, unsafe_allow_html=True)
