#!/usr/bin/env python3
"""
微博热搜产品创意分析脚本
使用 Anthropic API 分析微博热搜数据并生成 HTML 报告
"""

import os
import json
import requests
import time
from datetime import datetime

def get_weibo_hot_data(tianapi_key):
    """获取微博热搜数据"""
    url = f"https://apis.tianapi.com/weibohot/index?key={tianapi_key}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('code') == 200:
            return data.get('result', {}).get('list', [])
        else:
            print(f"API 返回错误: {data}")
            return None
    except Exception as e:
        print(f"获取微博热搜数据失败: {e}")
        return None

def analyze_with_claude(hot_data, api_key, base_url):
    """使用 Claude 分析热搜数据"""

    # 只取前 20 条热搜
    hot_data = hot_data[:20]

    # 读取 prompt
    with open('prompt.md', 'r', encoding='utf-8') as f:
        system_prompt = f.read()

    # 构建用户消息
    today = datetime.now().strftime('%Y年%m月%d日')
    hot_list_text = "\n".join([
        f"{i+1}. {item['hotword']} (热度: {item['hotwordnum']}, 标签: {item.get('hottag', '无')})"
        for i, item in enumerate(hot_data)
    ])

    user_message = f"""今天是 {today}，微博热搜数据如下：

{hot_list_text}

【重要】请直接输出完整的 HTML 代码，从 <!DOCTYPE html> 开始到 </html> 结束。不要输出任何分析过程、思考过程、markdown 格式或其他说明文字。只输出纯 HTML 代码。

报告中的生成时间请使用 {today}。"""

    # 构建请求 URL
    api_url = f"{base_url.rstrip('/')}/v1/messages"
    print(f"使用 API: {api_url}")
    print(f"模型: MiniMax-M2.1")

    # 构建请求
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }

    payload = {
        "model": "MiniMax-M2.1",
        "max_tokens": 16000,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_message}
        ]
    }

    # 添加重试机制
    max_retries = 2  # 减少重试次数
    for attempt in range(max_retries):
        try:
            print(f"尝试调用 API (第 {attempt + 1}/{max_retries} 次)...")
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=300  # 增加超时时间到 5 分钟
            )

            print(f"响应状态码: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print("API 调用成功！")

                # 提取内容（兼容不同的响应格式）
                content = result.get('content', [])
                if content:
                    # 只获取 text 类型的内容，忽略 thinking
                    text_content = None
                    for item in content:
                        if item.get('type') == 'text':
                            text_content = item.get('text', '')
                            break

                    if text_content:
                        # 确保返回的是 HTML 格式
                        text_content = text_content.strip()

                        # 如果被 markdown 代码块包裹，提取出来
                        if text_content.startswith('```html'):
                            start = text_content.find('```html') + 7
                            end = text_content.rfind('```')
                            if end > start:
                                text_content = text_content[start:end].strip()

                        # 如果不是 HTML，直接拒绝
                        if not (text_content.startswith('<!DOCTYPE html>') or text_content.startswith('<html')):
                            print("❌ 错误: AI 返回的不是 HTML 格式")
                            print(f"内容开头: {text_content[:100]}")

                            # 如果是思考过程，明确提示
                            if text_content.startswith('我来') or text_content.startswith('##'):
                                print("⚠️  检测到 AI 返回了思考过程而非 HTML")
                                print("这是 MiniMax API 的已知问题，请重试或联系 API 提供商")

                            return None

                        return text_content

                print("警告: 响应中没有找到 text 类型的内容")
                return None
            else:
                print(f"API 返回错误: {response.text}")

        except Exception as e:
            print(f"第 {attempt + 1} 次调用失败: {e}")

        if attempt < max_retries - 1:
            wait_time = (attempt + 1) * 5
            print(f"等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)

    print(f"Claude API 调用失败，已重试 {max_retries} 次")
    return None

def save_html_report(content, output_dir='docs'):
    """保存 HTML 报告"""
    os.makedirs(output_dir, exist_ok=True)

    today = datetime.now().strftime('%Y-%m-%d')
    filename = f"{output_dir}/微博热搜分析_{today}.html"

    # 从 Claude 的回复中提取 HTML 内容
    # Claude 可能会用 markdown 代码块包裹 HTML
    if '```html' in content:
        start = content.find('```html') + 7
        end = content.find('```', start)
        html_content = content[start:end].strip()
    elif '<!DOCTYPE html>' in content or '<html' in content:
        html_content = content
    else:
        # 如果没有找到 HTML，可能 Claude 直接返回了 HTML
        html_content = content

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"报告已保存到: {filename}")
    return filename

def main():
    """主函数"""
    # 获取环境变量
    tianapi_key = os.environ.get('TIANAPI_KEY')
    anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
    anthropic_base_url = os.environ.get('ANTHROPIC_API_BASE_URL', 'https://api.anthropic.com')

    if not tianapi_key:
        print("错误: 未设置 TIANAPI_KEY 环境变量")
        return 1

    if not anthropic_api_key:
        print("错误: 未设置 ANTHROPIC_API_KEY 环境变量")
        return 1

    print("Step 1: 获取微博热搜数据...")
    hot_data = get_weibo_hot_data(tianapi_key)

    if not hot_data:
        print("获取热搜数据失败")
        return 1

    print(f"成功获取 {len(hot_data)} 条热搜数据")

    print("\nStep 2-4: 使用 Claude 分析并生成报告...")
    analysis_result = analyze_with_claude(hot_data, anthropic_api_key, anthropic_base_url)

    if not analysis_result:
        print("分析失败")
        return 1

    print("\n保存 HTML 报告...")
    save_html_report(analysis_result)

    print("\n✅ 分析完成！")
    return 0

if __name__ == '__main__':
    exit(main())
