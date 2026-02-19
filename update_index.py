#!/usr/bin/env python3
"""
自动更新 index.html 中的报告列表
"""

import os
import re
from datetime import datetime

def get_all_reports():
    """扫描 docs 目录获取所有报告文件"""
    reports = []
    docs_dir = 'docs'

    if not os.path.exists(docs_dir):
        return reports

    for filename in os.listdir(docs_dir):
        if filename.startswith('微博热搜分析_') and filename.endswith('.html'):
            # 提取日期
            match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
            if match:
                date = match.group(1)
                reports.append({
                    'date': date,
                    'file': filename
                })

    # 按日期倒序排列
    reports.sort(key=lambda x: x['date'], reverse=True)
    return reports

def update_index_html(reports):
    """更新 index.html 中的报告列表"""
    index_file = 'docs/index.html'

    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 构建新的报告列表
    reports_js = ',\n                '.join([
        f"{{ date: '{r['date']}', file: '{r['file']}' }}"
        for r in reports
    ])

    # 替换报告列表
    pattern = r'const reports = \[(.*?)\];'
    replacement = f"const reports = [\n                {reports_js}\n            ];"

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ 已更新 index.html，共 {len(reports)} 个报告")

def main():
    reports = get_all_reports()
    if reports:
        update_index_html(reports)
    else:
        print("未找到任何报告文件")

if __name__ == '__main__':
    main()
