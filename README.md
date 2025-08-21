# 🤖 Twitter AI 监控系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个智能的Twitter(X)推文监控系统，结合AI技术自动翻译和生成中文摘要及AI分析，支持钉钉机器人推送，让您及时获取关注领域的最新动态。。

## ✨ 主要功能

- 🔍 **智能监控**: 自动监控指定Twitter账号的新推文
- 🤖 **AI处理**: 使用大语言模型自动翻译推文内容并生成中文标题，并对推文内容进行分析处理
- 📱 **钉钉推送**: 支持钉钉机器人实时推送重要信息
- 🌐 **Web界面**: 提供友好的Web管理界面，实时查看监控状态
- 📊 **数据管理**: 自动存储推文数据，支持去重和清理
- ⚡ **实时更新**: 可配置的检查间隔，确保信息及时性

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 网络连接（访问Twitter API和AI模型）

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/twitter-ai-monitor.git
cd twitter-ai-monitor
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置参数**
在设置中填入所需要的api_key等信息，保存后配置。

4. **启动系统**
```bash
python start.py
```

5. **访问Web界面**
打开浏览器访问 `http://localhost:5000`

## 📋 配置说明

### Twitter API
- 使用 [TwitterAPI.io](https://twitterapi.io/) 服务
- 支持高级搜索和实时监控

### AI模型
- 支持多种大语言模型接口
- 默认配置为阿里云通义千问
- 可自定义模型参数和重试策略

### 钉钉机器人
- 支持钉钉群机器人推送
- 自动签名验证
- 智能内容过滤

## 🎯 使用场景

- **AI研究者**: 监控OpenAI、Google、Meta等AI公司的官方动态
- **技术博主**: 获取最新AI技术资讯，生成中文内容
- **投资分析**: 跟踪AI行业重要新闻和产品发布
- **内容创作**: 自动翻译和摘要，提高内容创作效率

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Twitter API   │───▶│  AI Monitor     │───▶│  LLM Service    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Web Interface  │◀───│  Data Storage   │◀───│  AI Processing  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ DingTalk Bot    │    │  Data Cleaner   │    │  Status Monitor │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 项目结构

```
twitter-ai-monitor/
├── app.py                 # Flask主应用
├── twitter_ai_monitor.py  # 核心监控逻辑
├── llm.py                # AI模型接口
├── tweets.py             # 推文处理模块
├── clean_duplicates.py   # 数据清理脚本
├── start.py              # 启动脚本
├── config.json           # 配置文件
├── requirements.txt      # Python依赖
├── templates/            # Web模板
├── static/               # 静态资源
├── data/                 # 数据存储目录
└── README.md            # 项目说明
```

## 🔧 高级配置

### 自定义监控账号
在Web界面中添加或修改要监控的Twitter账号

### 调整检查间隔
修改监控检查频率，平衡实时性和API使用量

### AI处理参数
- 最大重试次数
- 超时时间
- Token数量限制

## 📊 监控效果

系统会自动：
1. 监控指定账号的新推文
2. 使用AI翻译推文内容
3. 生成中文标题和摘要
4. 推送到钉钉群
5. 存储到本地数据库

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

### v1.0.0
- 基础监控功能
- AI翻译和摘要生成
- 钉钉机器人推送
- Web管理界面

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [TwitterAPI.io](https://twitterapi.io/) - 提供Twitter数据访问
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [OpenAI](https://openai.com/) - AI模型接口标准

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！ 