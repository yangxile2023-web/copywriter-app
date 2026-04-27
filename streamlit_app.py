# -*- coding: utf-8 -*-
import streamlit as st
import re
import io
from openai import OpenAI
from docx import Document

# 页面配置
st.set_page_config(page_title="文案助手", layout="wide")

# 简单CSS
st.markdown("""
<style>
    .main { max-width: 1000px; margin: 0 auto; padding: 20px; }
    .stButton>button[kind="primary"] { 
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
        border: none !important; border-radius: 8px !important;
        padding: 12px 24px !important; font-weight: 600 !important;
    }
    .result-box {
        background: #f8fafc; border-radius: 8px; padding: 16px;
        margin: 8px 0; border-left: 3px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# 配置
INDUSTRIES = ["餐饮", "木作定制", "工厂/制造", "彩票店", "酒店/民宿", "通用"]
CONTENT_TYPES = ["干货避坑", "人设故事", "细节特写", "认知反转"]
KIMI_KEY = "sk-IA6qyNJFSYC8UB9RHnGHsgz24VWSrKalSnd5nTTbJNiqQ2uu"

# 确保session state初始化
for key in ['items', 'generating']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'items' else False

@st.cache_resource
def get_client():
    return OpenAI(api_key=KIMI_KEY, base_url="https://api.moonshot.cn/v1")

def generate_one(raw_data, idx, length):
    """生成单条文案"""
    try:
        name = re.search(r'出镜称呼[：:]\s*(\S+)', raw_data)
        name = name.group(1) if name else "老板"
        min_w, max_w = (150, 180) if length == "short" else (200, 300)
        ctype = CONTENT_TYPES[(idx - 1) % 4]
        
        client = get_client()
        resp = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[{
                "role": "user",
                "content": f"创作第{idx}条{ctype}文案。称呼：{name} 资料：{raw_data[:400]} 要求:字数{min_w}-{max_w} 禁止自我介绍"
            }],
            max_tokens=400, temperature=0.8, timeout=25
        )
        content = resp.choices[0].message.content.strip().strip('"')
        wc = len(content.replace(' ', '').replace('\n', ''))
        return {
            'idx': idx, 'content': content, 'wc': wc,
            'ok': min_w <= wc <= max_w, 'type': ctype
        }
    except Exception as e:
        return {'idx': idx, 'content': f"错误:{str(e)[:20]}", 'wc': 0, 'ok': False, 'type': CONTENT_TYPES[(idx-1)%4]}

def make_word(items, industry):
    """生成Word文档"""
    doc = Document()
    doc.add_heading('文案生成结果', 0)
    doc.add_paragraph(f'行业: {industry}')
    doc.add_paragraph(f'总数: {len(items)} 条')
    doc.add_paragraph()
    
    for item in items:
        doc.add_heading(f"【{item['type']}】文案 #{item['idx']}", level=2)
        doc.add_paragraph(item['content'])
        doc.add_paragraph(f"字数: {item['wc']} | 状态: {'优质' if item['ok'] else '需优化'}")
        doc.add_paragraph()
    
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

# ========== UI ==========
st.title("📝 晓牧传媒文案助手")
st.caption("AI生成30条短视频文案")

# 配置
st.subheader("配置")
c1, c2 = st.columns(2)
with c1:
    industry = st.selectbox("行业", INDUSTRIES, index=5)
with c2:
    length_opt = st.radio("长度", ["短文案(150-180)", "长文案(200-300)"], horizontal=True)

# 输入
st.subheader("客户资料")
raw = st.text_area("输入", height=120, placeholder="请输入客户资料：出镜称呼、店铺名称、主营业务、真实故事...")
count = len(raw.replace(' ', '').replace('\n', ''))
st.caption(f"已输入 {count} 字")

# 生成按钮
if st.button("🚀 生成30条文案", type="primary", disabled=st.session_state.generating):
    if count < 30:
        st.error("请至少输入30字")
    else:
        st.session_state.generating = True
        length = "short" if "短" in length_opt else "long"
        
        progress = st.progress(0)
        results = []
        
        for i in range(30):
            result = generate_one(raw, i + 1, length)
            results.append(result)
            progress.progress((i + 1) / 30)
        
        st.session_state.items = results
        st.session_state.generating = False
        st.success(f"✅ 生成完成！{sum(1 for r in results if r['ok'])} 条优质文案")
        st.rerun()

# 显示结果
items = st.session_state.get('items', [])
if isinstance(items, list) and len(items) > 0:
    st.divider()
    st.subheader(f"生成结果 ({len(items)}条)")
    
    # 统计
    ok_num = sum(1 for i in items if i.get('ok'))
    cols = st.columns(4)
    cols[0].metric("总数", len(items))
    cols[1].metric("优质", ok_num)
    cols[2].metric("需优化", len(items) - ok_num)
    
    # 下载按钮
    with cols[3]:
        try:
            word_data = make_word(items, industry)
            st.download_button(
                "📥 下载Word",
                word_data,
                file_name=f"文案_{industry}_{len(items)}条.docx",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Word生成失败: {e}")
    
    # 清空按钮
    if st.button("🗑️ 清空结果"):
        st.session_state.items = []
        st.rerun()
    
    # 文案列表
    st.subheader("文案详情")
    for item in items:
        status = "✅" if item.get('ok') else "⚠️"
        with st.expander(f"{status} 文案 #{item['idx']} [{item['type']}] - {item['wc']}字"):
            st.write(item['content'])
            st.button("复制", key=f"copy_{item['idx']}")
