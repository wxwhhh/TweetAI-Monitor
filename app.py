from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime, timedelta
import threading
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
from twitter_ai_monitor import TwitterAIMonitor

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# 全局变量
monitor_instance = None
monitor_thread = None
monitoring_status = {
    "running": False, 
    "last_update": None,
    "current_status": "待机中",
    "processed_tweets": 0,
    "current_account": "",
    "next_check_time": None,
    "last_result": "暂无结果"
}

# 时间转换函数：UTC转北京时间
def utc_to_beijing(utc_time_str):
    """
    将UTC时间字符串转换为北京时间字符串
    :param utc_time_str: ISO格式的UTC时间字符串
    :return: 北京时间字符串
    """
    try:
        if not utc_time_str:
            return ""
        # 解析ISO格式时间字符串
        utc_time = datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
        # 加上8小时得到北京时间
        beijing_time = utc_time + timedelta(hours=8)
        # 返回格式化后的北京时间
        return beijing_time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"时间转换错误: {str(e)}")
        return utc_time_str

def parse_twitter_time(twitter_time_str):
    """
    解析Twitter时间格式并转换为北京时间
    :param twitter_time_str: Twitter时间格式字符串，如 "Wed Aug 20 14:05:10 +0000 2025"
    :return: 格式化的北京时间字符串
    """
    try:
        if not twitter_time_str:
            return ""
        from email.utils import parsedate_to_datetime
        utc_time = parsedate_to_datetime(twitter_time_str)
        beijing_time = utc_time + timedelta(hours=8)
        return beijing_time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Twitter时间解析错误: {str(e)}")
        try:
            if 'T' in twitter_time_str:
                return utc_to_beijing(twitter_time_str)
            else:
                return twitter_time_str
        except:
            return twitter_time_str

def send_dingtalk_message(webhook_url, secret, author, update_time, ai_title, ai_content):
    """
    发送钉钉机器人消息
    :param webhook_url: 钉钉机器人webhook地址
    :param secret: 钉钉机器人签名密钥
    :param author: 作者名称
    :param update_time: 推文的发帖时间 (已转换为北京时间)
    :param ai_title: AI生成的标题
    :param ai_content: AI翻译内容
    :return: 是否发送成功
    """
    try:
        # 检查AI处理是否成功，如果失败则使用原文
        ai_processing_failed = False
        if (ai_title and ("处理失败" in ai_title or "内容安全检查失败" in ai_title or "AI标题生成失败" in ai_title)):
            ai_processing_failed = True
        if (ai_content and ("处理失败" in ai_content or "内容安全检查失败" in ai_content)):
            ai_processing_failed = True
        
        # 如果AI处理失败，使用原文内容
        if ai_processing_failed:
            ai_title = "AI处理失败，显示原文"
            ai_content = f"**推文原文：**\n{ai_content}"
            print(f"⚠️ AI处理失败，钉钉推送将显示原文内容")
        
        # 构建消息内容
        message = f"""🤖 AI新闻推送

---

📝 **{author}** 更新了推文
⏰ **发帖时间：** {update_time}

🎯 **AI生成标题：** **{ai_title}**

🧠 **AI翻译内容：**
{ai_content}

---

💡 *由 Twitter(X) AI 监控系统 自动推送*"""
        
        # 计算签名
        timestamp = str(round(time.time() * 1000))
        string_to_sign = f'{timestamp}\n{secret}'
        hmac_code = hmac.new(
            secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        
        # 构建请求URL
        url = f"{webhook_url}&timestamp={timestamp}&sign={sign}"
        
        # 构建消息数据
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": f"🤖 AI新闻推送 - {author}",
                "text": message
            },
            "at": {
                "isAtAll": False
            }
        }
        
        # 发送请求
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('errcode') == 0:
                print(f"✅ 钉钉消息发送成功: {author}")
                return True
            else:
                print(f"❌ 钉钉消息发送失败: {result.get('errmsg')}")
                return False
        else:
            print(f"❌ 钉钉请求失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 钉钉消息发送异常: {str(e)}")
        return False

# 配置文件路径
CONFIG_FILE = "config.json"

def load_config():
    """加载配置文件"""
    default_config = {
        "TWITTER_API_KEY": "",
        "LLM_URL": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "LLM_API_KEY": "",
        "TARGET_ACCOUNTS": ["OpenAI"],
        "CHECK_INTERVAL": 300,
        "INITIAL_HOURS": 2,
        "DINGTALK_WEBHOOK": "",
        "DINGTALK_SECRET": "",
        "ENABLE_DINGTALK": False,
        "AI_MAX_RETRIES": 3,
        "AI_TIMEOUT": 30,
        "AI_MAX_TOKENS": 1000
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 合并默认配置以确保所有键都存在
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except json.JSONDecodeError:
            return default_config
    return default_config

def save_config(config):
    """保存配置文件"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def start_monitoring():
    """启动监控"""
    global monitor_instance, monitoring_status
    
    config = load_config()
    
    if not all([config["TWITTER_API_KEY"], config["LLM_API_KEY"]]):
        return False, "请先配置API密钥"
    
    try:
        monitor_instance = TwitterAIMonitor(
            config["TWITTER_API_KEY"],
            config["LLM_URL"],
            config["LLM_API_KEY"],
            dingtalk_webhook=config.get("DINGTALK_WEBHOOK", ""),
            dingtalk_secret=config.get("DINGTALK_SECRET", ""),
            enable_dingtalk=config.get("ENABLE_DINGTALK", False),
            ai_max_retries=config.get("AI_MAX_RETRIES", 3),
            ai_timeout=config.get("AI_TIMEOUT", 30),
            ai_max_tokens=config.get("AI_MAX_TOKENS", 1000)
        )
        
        # 在新线程中启动监控
        def monitor_worker():
            # 获取是否排除回复的配置，默认为False
            exclude_replies = config.get("EXCLUDE_REPLIES", False)
            
            monitor_instance.monitor_and_process_with_status(
                config["TARGET_ACCOUNTS"],
                config["CHECK_INTERVAL"],
                config["INITIAL_HOURS"],
                monitoring_status,
                exclude_replies
            )
        
        global monitor_thread
        monitor_thread = threading.Thread(target=monitor_worker, daemon=True)
        monitor_thread.start()
        
        monitoring_status["running"] = True
        monitoring_status["last_update"] = datetime.now().isoformat()
        monitoring_status["current_status"] = "正在初始化..."
        monitoring_status["processed_tweets"] = 0
        
        return True, "🚀 Neural Network Activated"
        
    except Exception as e:
        return False, f"❌ Neural Network Error: {str(e)}"

def stop_monitoring():
    """停止监控"""
    global monitoring_status, monitor_instance, monitor_thread
    
    # 设置状态为停止
    monitoring_status["running"] = False
    monitoring_status["current_status"] = "Neural Network Offline"
    monitoring_status["current_account"] = ""
    monitoring_status["next_check_time"] = None
    
    # 等待线程结束（最多等待3秒）
    if monitor_thread and monitor_thread.is_alive():
        try:
            monitor_thread.join(timeout=3)
        except Exception as e:
            print(f"停止监控线程时出错: {str(e)}")
    
    # 重置监控实例
    monitor_instance = None
    monitor_thread = None
    
    return True, "🛑 Neural Network Deactivated"

@app.route('/')
def index():
    """首页"""
    # 获取筛选参数
    author_filter = request.args.get('author', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # 获取所有推文数据
    if monitor_instance:
        all_tweets = monitor_instance.get_all_tweets()
    else:
        # 如果没有监控实例，创建临时实例来读取数据
        temp_monitor = TwitterAIMonitor("", "", "")
        all_tweets = temp_monitor.get_all_tweets()
    
    # 应用筛选
    filtered_tweets = all_tweets
    
    if author_filter:
        filtered_tweets = [t for t in filtered_tweets if t.get('author', '').lower() == author_filter.lower()]
    
    # 日期范围筛选
    if start_date or end_date:
        filtered_tweets = [t for t in filtered_tweets if t.get('created_at')]
        if start_date:
            filtered_tweets = [t for t in filtered_tweets if parse_twitter_time(t['created_at'])[:10] >= start_date]
        if end_date:
            filtered_tweets = [t for t in filtered_tweets if parse_twitter_time(t['created_at'])[:10] <= end_date]
    
    # 转换时间为北京时间并添加格式化的创建时间
    for tweet in filtered_tweets:
        if 'timestamp' in tweet:
            tweet['beijing_time'] = utc_to_beijing(tweet['timestamp'])
        if 'created_at' in tweet:
            tweet['formatted_created_at'] = parse_twitter_time(tweet['created_at'])
    
    # 按创建时间排序（最新的在前）
    filtered_tweets.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    # 获取所有作者列表用于筛选
    authors = list(set([t.get('author', '') for t in all_tweets if t.get('author')]))
    
    # 更新监控状态中的时间为北京时间
    if monitoring_status.get('last_update'):
        monitoring_status['beijing_last_update'] = utc_to_beijing(monitoring_status['last_update'])
    
    if monitoring_status.get('next_check_time'):
        monitoring_status['beijing_next_check_time'] = utc_to_beijing(monitoring_status['next_check_time'])
    
    return render_template('index.html', 
                         tweets=filtered_tweets, 
                         authors=authors,
                         current_author=author_filter,
                         start_date=start_date,
                         end_date=end_date,
                         monitoring_status=monitoring_status)

@app.route('/tweet/<tweet_id>')
def tweet_detail(tweet_id):
    """推文详情页"""
    # 获取所有推文数据
    if monitor_instance:
        all_tweets = monitor_instance.get_all_tweets()
    else:
        temp_monitor = TwitterAIMonitor("", "", "")
        all_tweets = temp_monitor.get_all_tweets()
    
    # 查找指定ID的推文
    tweet = None
    for t in all_tweets:
        if t.get('id') == tweet_id:
            tweet = t
            break
    
    if not tweet:
        return "推文未找到", 404
    
    # 添加格式化的时间
    if 'timestamp' in tweet:
        tweet['beijing_time'] = utc_to_beijing(tweet['timestamp'])
    if 'created_at' in tweet:
        tweet['formatted_created_at'] = parse_twitter_time(tweet['created_at'])
    
    return render_template('tweet_detail.html', tweet=tweet, monitoring_status=monitoring_status)

@app.route('/settings')
def settings():
    """个人中心/设置页面"""
    config = load_config()
    return render_template('settings.html', config=config, monitoring_status=monitoring_status)

@app.route('/api/save_config', methods=['POST'])
def save_config_api():
    """保存配置API"""
    try:
        if request.content_type == 'application/json':
            config = request.json
        else:
            # 处理表单数据
            config = request.form.to_dict()
        
        if not config:
            return jsonify({"success": False, "message": "未接收到配置数据"})
        
        # 验证必要字段
        required_fields = ['TWITTER_API_KEY', 'LLM_URL', 'LLM_API_KEY']
        for field in required_fields:
            if not config.get(field):
                return jsonify({"success": False, "message": f"{field} 不能为空"})
        
        # 验证钉钉配置
        if config.get('ENABLE_DINGTALK') == 'true' or config.get('ENABLE_DINGTALK') is True:
            if not config.get('DINGTALK_WEBHOOK'):
                return jsonify({"success": False, "message": "启用钉钉推送时，钉钉Webhook地址不能为空"})
            if not config.get('DINGTALK_SECRET'):
                return jsonify({"success": False, "message": "启用钉钉推送时，钉钉签名密钥不能为空"})
        
        # 确保TARGET_ACCOUNTS是列表
        if isinstance(config.get('TARGET_ACCOUNTS'), str):
            config['TARGET_ACCOUNTS'] = [acc.strip() for acc in config['TARGET_ACCOUNTS'].split(',') if acc.strip()]
        
        # 转换数字字段
        if 'CHECK_INTERVAL' in config:
            config['CHECK_INTERVAL'] = int(config['CHECK_INTERVAL']) if config['CHECK_INTERVAL'] else 300
        if 'INITIAL_HOURS' in config:
            config['INITIAL_HOURS'] = int(config['INITIAL_HOURS']) if config['INITIAL_HOURS'] else 2
        
        # 转换布尔字段
        if 'ENABLE_DINGTALK' in config:
            config['ENABLE_DINGTALK'] = config['ENABLE_DINGTALK'] == 'true' if isinstance(config['ENABLE_DINGTALK'], str) else bool(config['ENABLE_DINGTALK'])
        
        save_config(config)
        return jsonify({"success": True, "message": "🧠 Neural configuration updated successfully"})
        
    except Exception as e:
        return jsonify({"success": False, "message": f"⚠️ Configuration sync failed: {str(e)}"})

@app.route('/api/start_monitoring', methods=['POST'])
def start_monitoring_api():
    """启动监控API"""
    success, message = start_monitoring()
    return jsonify({"success": success, "message": message})

@app.route('/api/stop_monitoring', methods=['POST'])
def stop_monitoring_api():
    """停止监控API"""
    success, message = stop_monitoring()
    return jsonify({"success": success, "message": message})

@app.route('/api/monitoring_status')
def monitoring_status_api():
    """获取监控状态API"""
    return jsonify(monitoring_status)

@app.route('/api/tweets')
def tweets_api():
    """推文数据API"""
    author_filter = request.args.get('author', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # 获取所有推文数据
    if monitor_instance:
        all_tweets = monitor_instance.get_all_tweets()
    else:
        temp_monitor = TwitterAIMonitor("", "", "")
        all_tweets = temp_monitor.get_all_tweets()
    
    # 应用筛选
    filtered_tweets = all_tweets
    
    if author_filter:
        filtered_tweets = [t for t in filtered_tweets if t.get('author', '').lower() == author_filter.lower()]
    
    # 日期范围筛选
    if start_date or end_date:
        filtered_tweets = [t for t in filtered_tweets if t.get('created_at')]
        if start_date:
            filtered_tweets = [t for t in filtered_tweets if parse_twitter_time(t['created_at'])[:10] >= start_date]
        if end_date:
            filtered_tweets = [t for t in filtered_tweets if parse_twitter_time(t['created_at'])[:10] <= end_date]
    
    # 转换时间为北京时间
    for tweet in filtered_tweets:
        if 'timestamp' in tweet:
            tweet['beijing_time'] = utc_to_beijing(tweet['timestamp'])
        if 'created_at' in tweet:
            tweet['formatted_created_at'] = parse_twitter_time(tweet['created_at'])
    
    # 按创建时间排序（最新的在前）
    filtered_tweets.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return jsonify({
        'tweets': filtered_tweets,
        'total': len(filtered_tweets),
        'filtered': len(filtered_tweets) != len(all_tweets)
    })

@app.route('/api/test_dingtalk', methods=['POST'])
def test_dingtalk_api():
    """测试钉钉推送API"""
    try:
        config = load_config()
        
        if not config.get("ENABLE_DINGTALK"):
            return jsonify({"success": False, "message": "钉钉推送未启用"})
        
        webhook = config.get("DINGTALK_WEBHOOK")
        secret = config.get("DINGTALK_SECRET")
        
        if not webhook or not secret:
            return jsonify({"success": False, "message": "钉钉配置不完整"})
        
        # 发送测试消息
        success = send_dingtalk_message(
            webhook, 
            secret, 
            "测试账号", 
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "这是一条测试消息的标题",
            "这是一条测试消息，用于验证钉钉机器人配置是否正确。如果收到此消息，说明配置成功！🎉"
        )
        
        if success:
            return jsonify({"success": True, "message": "✅ 钉钉测试消息发送成功！请检查钉钉群是否收到消息。"})
        else:
            return jsonify({"success": False, "message": "❌ 钉钉测试消息发送失败，请检查配置是否正确。"})
            
    except Exception as e:
        return jsonify({"success": False, "message": f"❌ 测试失败: {str(e)}"})

if __name__ == '__main__':
    # 确保必要的目录存在
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 