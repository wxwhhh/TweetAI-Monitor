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
pip3 install -r requirements.txt
```

3. **启动系统**
```bash
python3 start.py
```
<img width="1707" height="779" alt="image" src="https://github.com/user-attachments/assets/94fc4672-8699-4e85-88c1-3d28b18ecfe4" />

4. **访问Web界面**
打开浏览器访问 `http://localhost:5000`

5. **配置参数**
在设置中填入所需要的api_key等信息，保存后配置。
<img width="1973" height="740" alt="image" src="https://github.com/user-attachments/assets/12a782b4-916e-4979-a995-6cfea57b5d55" />
<img width="1287" height="462" alt="image" src="https://github.com/user-attachments/assets/53926418-f6ec-4dbd-8182-4d51cb374673" />

6. **配置监控用户**
在监控账号这里写要监测账号的名字，例如特朗普和特朗普中文推特
<img width="762" height="100" alt="image" src="https://github.com/user-attachments/assets/459b3b00-d476-41e4-b64d-066212326093" />
<img width="942" height="134" alt="image" src="https://github.com/user-attachments/assets/be0f2a95-3f22-4670-9557-57fef4055444" />
配置如下，使用逗号隔开(英文逗号)
<img width="1288" height="418" alt="image" src="https://github.com/user-attachments/assets/02dbba64-afad-451b-82a0-2fbd256e1cfa" />

7. **开启监控**
一切配置好之后进行开启监控，内容就会进行实时更新
<img width="2000" height="399" alt="image" src="https://github.com/user-attachments/assets/595789e9-251a-493a-add2-4c63399be262" />

7. **页面和钉钉显示通知显示如下**
<img width="1859" height="1031" alt="image" src="https://github.com/user-attachments/assets/dd16eae7-0af3-45e9-b359-215d5d2c19c5" />
<img width="1740" height="565" alt="image" src="https://github.com/user-attachments/assets/97599969-e2f5-48e6-af0f-0fef4847becd" />

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
- **技术博主**: 获取最新技术资讯，生成中文内容
- **投资分析**: 跟踪重要新闻和产品发布
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

## 📊 监控效果

系统会自动：
1. 监控指定账号的新推文
2. 使用AI翻译推文内容
3. 生成中文标题和摘要
4. 推送到钉钉群
5. 存储到本地数据库

## 📝 更新日志

### v1.0.0
- 基础监控功能
- AI翻译和摘要生成
- 钉钉机器人推送
- Web管理界面

## 🙏 致谢
使用AI-News进行二开造轮子 感谢！
- [源项目](https://github.com/luoyongkai/AI-News)) - AI-News
  
⭐ 如果这个项目对您有帮助，请给我们一个星标！ 
