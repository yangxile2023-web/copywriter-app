#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
晓牧传媒文案助手 v4.1 - 修复版
支持短文案默认，可切换长文案重新生成
"""

import os
import json
import re
import time
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
import requests

try:
    from banned_words import BANNED_WORDS
except ImportError:
    BANNED_WORDS = []

# 导入敏感词检测
try:
    from sensitive_words import check_sensitive_words, SENSITIVE_WORDS
except ImportError:
    SENSITIVE_WORDS = ["测试敏感词"]
    def check_sensitive_words(text):
        return [w for w in SENSITIVE_WORDS if w in text]

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', os.urandom(24))

KIMI_API_KEY = os.getenv('KIMI_API_KEY')
SECRET_PASSWORD = os.getenv('SECRET_PASSWORD', '88886666')
KIMI_API_URL = "https://api.moonshot.cn/v1/chat/completions"

# 行业配置
INDUSTRIES = {
    "catering": {"name": "餐饮美食", "description": "餐厅、小吃、烧烤、火锅", "directions": ["食材故事", "制作工艺", "创业经历", "顾客反馈", "店铺环境"]},
    "woodwork": {"name": "木作家装", "description": "全屋定制、家具、木作", "directions": ["选材故事", "安装工艺", "设计细节", "客户案例", "从业经历"]},
    "factory": {"name": "工厂制造", "description": "制造业、加工厂", "directions": ["选材品控", "工艺展示", "设备实力", "创业故事", "品质坚守"]},
    "lottery": {"name": "彩票站点", "description": "彩票店、体彩福彩", "directions": ["守店日常", "购彩知识", "节日氛围", "经营故事", "社区互动"]},
    "hotel": {"name": "酒店宴席", "description": "婚宴酒店、宴会厅", "directions": ["场地特色", "本地人情味", "服务细节", "宴席故事", "环境展示"]},
    "general": {"name": "通用行业", "description": "其他行业通用", "directions": ["产品特色", "服务优势", "创业故事", "客户见证", "专业分享"]}
}

# 文案长度配置
LENGTHS = {
    "short": {"name": "短文案", "min": 150, "max": 180, "desc": "适合快节奏，约1分钟"},
    "long": {"name": "长文案", "min": 200, "max": 300, "desc": "适合深度内容，1.5-2分钟"}
}


def get_copywrite_config(industry="general", length="short"):
    """获取文案配置"""
    industry_info = INDUSTRIES.get(industry, INDUSTRIES["general"])
    directions = industry_info["directions"]
    
    hooks = ["提问式", "数字型", "场景型", "冲突型", "悬念型", "身份型", "对比型", "故事型", "痛点型", "情感型"]
    styles = ["真诚走心", "产品介绍", "创业故事", "品质坚守", "顾客见证", "幕后揭秘", "场景展示", "情感共鸣", "专业分享", "日常记录"]
    
    configs = []
    angle_pool = directions * 6
    
    for i in range(30):
        configs.append({
            "idx": i + 1,
            "style": styles[i % len(styles)],
            "angle": angle_pool[i],
            "hook": hooks[i % len(hooks)]
        })
    
    return configs


def call_kimi(prompt, max_tokens=700, timeout=35):
    """调用Kimi API"""
    headers = {
        "Authorization": f"Bearer {KIMI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "moonshot-v1-8k",
        "messages": [
            {"role": "system", "content": "你是短视频文案专家，写自然真实的内容。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(KIMI_API_URL, headers=headers, json=data, timeout=timeout)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except:
        return None


def generate_single_copywrite(raw_data, config, industry="general", length="short", retries=2):
    """生成单条文案 - 严格控制在150-180字"""
    industry_info = INDUSTRIES.get(industry, INDUSTRIES["general"])
    length_info = LENGTHS.get(length, LENGTHS["short"])
    
    name_match = re.search(r'出镜称呼[：:]\s*(\S+)', raw_data)
    name = name_match.group(1) if name_match else "老板"
    
    min_words, max_words = length_info["min"], length_info["max"]
    
    for attempt in range(retries):
        prompt = f"""写第{config['idx']}条口播文案。字数必须严格控制在{min_words}-{max_words}字！

【字数要求 - 最重要】
• 总字数：{min_words}-{max_words}字（写完后数一下，必须在这个范围内）
• 开头：20-30字
• 中间：{min_words-50}-{max_words-60}字
• 结尾：15-25字

【内容要求】
行业：{industry_info['name']}
风格：{config['style']}
角度：{config['angle']}
开头方式：{config['hook']}

客户资料：
{raw_data[:300]}

写作要点：
1. {config['hook']}开头
2. 称呼"{name}"最多1次，多用"咱"
3. 不写具体门牌号地址
4. 包含具体时间、数字、对话
5. 口语化，自然真实

直接写文案（控制在{min_words}-{max_words}字）："""

        result = call_kimi(prompt, max_tokens=500, timeout=30)
        
        if result:
            content = result.strip()
            content = re.sub(r'^\d+[\.、\.\s]*', '', content)
            content = re.sub(r'【[^】]+】', '', content, count=1).strip()
            
            word_count = len(content.replace(' ', '').replace('\n', ''))
            name_count = content.count(name)
            has_address = bool(re.search(r'[路街道]\s*\d+[号]', content))
            
            # 严格字数控制，宽松其他检查
            quality_pass = min_words <= word_count <= max_words
            
            issues = []
            if word_count < min_words: 
                issues.append(f"不足{min_words}字")
            if word_count > max_words: 
                issues.append(f"超过{max_words}字")
            if name_count > 3: 
                issues.append(f"称呼多")
            if has_address: 
                issues.append(f"有门牌号")
            
            return {
                'index': config['idx'],
                'style': config['style'],
                'angle': config['angle'],
                'hook': config['hook'],
                'content': content,
                'word_count': word_count,
                'name_count': name_count,
                'length_type': length,
                'quality_pass': quality_pass,
                'issues': issues
            }
        
        if attempt < retries - 1:
            time.sleep(1)
    
    return None


def generate_all_copywrites(raw_data, industry="general", length="short"):
    """生成30条文案"""
    configs = get_copywrite_config(industry, length)
    all_copywrites = []
    failed_count = 0
    
    for config in configs:
        result = generate_single_copywrite(raw_data, config, industry, length)
        
        if result:
            all_copywrites.append(result)
        else:
            failed_count += 1
            all_copywrites.append({
                'index': config['idx'],
                'style': config['style'],
                'angle': config['angle'],
                'hook': config['hook'],
                'content': "【生成失败，请重新生成】",
                'word_count': 0,
                'length_type': length,
                'quality_pass': False,
                'issues': ['API失败']
            })
        
        if config['idx'] % 5 == 0:
            time.sleep(0.3)
    
    passed = sum(1 for c in all_copywrites if c.get('quality_pass'))
    
    return {
        "success": True,
        "copywrites": all_copywrites,
        "total": len(all_copywrites),
        "failed": failed_count,
        "passed": passed
    }


# ===== 路由 =====

@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('index.html')


@app.route('/config')
def get_config():
    """获取行业和长度配置"""
    return jsonify({
        'success': True,
        'industries': INDUSTRIES,
        'lengths': LENGTHS
    })


@app.route('/login', methods=['POST'])
def login():
    password = request.json.get('password', '')
    if password == SECRET_PASSWORD:
        session['logged_in'] = True
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': '密码错误'})


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return jsonify({'success': True})


@app.route('/generate', methods=['POST'])
def generate():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': '请先登录'})
    
    data = request.json
    raw_data = data.get('raw_data', '').strip()
    industry = data.get('industry', 'general')
    length = data.get('length', 'short')
    
    if not raw_data or len(raw_data) < 30:
        return jsonify({'success': False, 'error': '请填写完整资料'})
    
    result = generate_all_copywrites(raw_data, industry, length)
    
    return jsonify({
        'success': True,
        'copywrites': result["copywrites"],
        'total': result["total"],
        'failed': result.get("failed", 0),
        'passed': result.get("passed", 0),
        'industry': industry,
        'length': length
    })


@app.route('/regenerate', methods=['POST'])
def regenerate():
    """重新生成单条，可切换长度"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': '请先登录'})
    
    data = request.json
    raw_data = data.get('raw_data', '').strip()
    index = data.get('index', 0)
    industry = data.get('industry', 'general')
    length = data.get('length', 'short')  # 可以切换长度
    
    if not raw_data:
        return jsonify({'success': False, 'error': '没有资料'})
    
    configs = get_copywrite_config(industry, length)
    config = next((c for c in configs if c['idx'] == index), None)
    
    if not config:
        return jsonify({'success': False, 'error': '无效序号'})
    
    result = generate_single_copywrite(raw_data, config, industry, length, retries=3)
    
    if result:
        return jsonify({'success': True, 'copywrite': result})
    else:
        return jsonify({'success': False, 'error': '重新生成失败'})


@app.route('/check_sensitive', methods=['POST'])
def check_sensitive():
    """检测敏感词"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': '请先登录'})
    
    data = request.json
    content = data.get('content', '')
    
    if not content:
        return jsonify({'success': False, 'error': '没有内容'})
    
    found = check_sensitive_words(content)
    
    return jsonify({
        'success': True,
        'has_sensitive': len(found) > 0,
        'sensitive_words': found,
        'count': len(found)
    })


@app.route('/check_all_sensitive', methods=['POST'])
def check_all_sensitive():
    """批量检测敏感词"""
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': '请先登录'})
    
    data = request.json
    copywrites = data.get('copywrites', [])
    
    results = []
    total_sensitive = 0
    
    for cw in copywrites:
        found = check_sensitive_words(cw.get('content', ''))
        if found:
            total_sensitive += len(found)
        results.append({
            'index': cw.get('index'),
            'sensitive_words': found,
            'has_sensitive': len(found) > 0
        })
    
    return jsonify({
        'success': True,
        'results': results,
        'total_sensitive': total_sensitive,
        'affected_count': sum(1 for r in results if r['has_sensitive'])
    })


if __name__ == '__main__':
    print("=" * 60)
    print("📝 晓牧传媒文案助手 v4.1 - 修复版")
    print("=" * 60)
    print("访问地址: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
