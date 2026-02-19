# 微博热搜产品创意分析项目

## 项目简介

每天自动抓取微博热搜，使用 AI 分析挖掘产品创意，生成 HTML 报告并发布到 GitHub Pages。

**网站地址**: https://michelle-chenmj.github.io/weibo/

## 核心文件说明

### 1. 主要代码文件

- **analyze.py** - 核心分析脚本
  - 调用天行数据 API 获取微博热搜
  - 使用 MiniMax API (兼容 Anthropic 格式) 进行 AI 分析
  - 生成 HTML 报告到 `docs/` 目录
  - **重要**: 只提取 `text` 类型内容，忽略 `thinking` 类型

- **prompt.md** - AI 分析的 System Prompt
  - 定义分析流程：获取数据 → 分类归纳 → 筛选分析 → 生成报告
  - 控制报告的格式和风格
  - 可以调整这个文件来改变分析质量

- **update_index.py** - 自动更新首页报告列表
  - 扫描 `docs/` 目录下的所有报告
  - 自动更新 `index.html` 中的报告列表

### 2. 配置文件

- **.github/workflows/weibo-analysis.yml** - GitHub Actions 定时任务
  - 定时: 每天 UTC 01:00 (北京时间 09:00)
  - 流程: 安装依赖 → 运行分析 → 更新首页 → 提交推送 → 部署 Pages
  - 支持手动触发

- **requirements.txt** - Python 依赖
  ```
  requests
  ```

### 3. 输出文件

- **docs/** - GitHub Pages 发布目录
  - `index.html` - 首页，列出所有报告
  - `微博热搜分析_YYYY-MM-DD.html` - 每日报告

## 环境变量 (GitHub Secrets)

需要在 GitHub 仓库设置以下 Secrets:

1. **MINIMAX_API_KEY** - MiniMax API 密钥
2. **TIANAPI_KEY** - 天行数据 API 密钥

## 关键技术点

### 1. API 调用问题

**MiniMax API 返回格式**:
```json
{
  "content": [
    {"type": "thinking", "thinking": "思考过程..."},
    {"type": "text", "text": "最终HTML内容"}
  ]
}
```

**解决方案**: 只提取 `type == "text"` 的内容，忽略 `thinking`

### 2. 时间显示问题

**问题**: AI 生成的报告时间不准确

**解决方案**: 在用户消息中明确指定日期
```python
today = datetime.now().strftime('%Y年%m月%d日')
user_message = f"今天是 {today}，微博热搜数据如下：..."
```

### 3. GitHub Pages 配置

- **方式**: 使用 master 分支的 `/docs` 目录
- **部署**: 每次推送到 master 自动更新
- **延迟**: 1-2 分钟生效

### 4. 报告列表自动更新

使用 `update_index.py` 自动扫描并更新 `index.html` 中的报告列表，避免手动维护。

## 常见问题排查

### 1. 定时任务没运行
- 检查 GitHub Actions 是否启用
- 查看 Actions 标签的运行日志
- 确认 Secrets 配置正确

### 2. 报告显示思考过程而非 HTML
- 检查 `analyze.py` 是否只提取 `text` 类型
- 确认 API 返回格式

### 3. 报告时间错误
- 确认 `analyze.py` 中有传递日期给 AI
- 检查 prompt 中的时间格式要求

### 4. GitHub Pages 没更新
- 等待 1-2 分钟
- 检查 Settings → Pages 配置
- 确认选择了 master 分支的 /docs 目录

## 手动运行

本地测试:
```bash
# 设置环境变量
export TIANAPI_KEY="your_key"
export ANTHROPIC_API_KEY="your_minimax_key"
export ANTHROPIC_API_BASE_URL="https://api.minimaxi.com/anthropic"

# 运行分析
python analyze.py

# 更新首页
python update_index.py
```

GitHub 手动触发:
1. 进入 Actions 标签
2. 选择 "微博热搜产品创意分析"
3. 点击 "Run workflow"

## 优化建议

### 成本控制
- 改为每周 3 次 (修改 cron 表达式)
- 减少分析热搜数量 (修改 `analyze.py` 中的 `hot_data[:20]`)

### 功能扩展
- 添加 README.md 介绍项目
- 添加趋势统计功能
- 实现邮件订阅通知
- 存储历史数据为 JSON

### 报告质量
- 调整 `prompt.md` 优化分析深度
- 增加数据可视化图表
- 改进移动端显示效果

## 项目结构

```
weibo-hot-analysis/
├── .github/
│   └── workflows/
│       └── weibo-analysis.yml    # GitHub Actions 配置
├── docs/                          # GitHub Pages 目录
│   ├── index.html                 # 首页
│   └── 微博热搜分析_*.html        # 每日报告
├── analyze.py                     # 主分析脚本
├── update_index.py                # 更新首页脚本
├── prompt.md                      # AI 分析 Prompt
├── requirements.txt               # Python 依赖
└── PROJECT.md                     # 本文档
```

## 维护清单

**每周检查**:
- [ ] GitHub Actions 运行状态
- [ ] API 调用额度
- [ ] 报告生成质量

**每月检查**:
- [ ] API Key 是否需要续费
- [ ] 报告存储空间
- [ ] 用户反馈

## 联系方式

- GitHub 仓库: https://github.com/Michelle-chenMJ/weibo
- 问题反馈: 在 GitHub Issues 提交

---

**最后更新**: 2026-02-19
