import requests
import time
import json
import os
from datetime import datetime, timedelta
from openai import OpenAI


class TwitterAIMonitor:
    """Twitter推文监控和AI处理器"""
    
    def __init__(self, twitter_api_key: str, llm_url: str, llm_api_key: str, data_dir: str = "data", 
                 dingtalk_webhook: str = "", dingtalk_secret: str = "", enable_dingtalk: bool = False,
                 ai_max_retries: int = 3, ai_timeout: int = 30, ai_max_tokens: int = 1000):
        """
        初始化监控器
        
        :param twitter_api_key: TwitterAPI.io API Key
        :param llm_url: 大模型接口URL
        :param llm_api_key: 大模型API Key
        :param data_dir: 数据存储目录
        :param dingtalk_webhook: 钉钉机器人Webhook地址
        :param dingtalk_secret: 钉钉机器人签名密钥
        :param enable_dingtalk: 是否启用钉钉推送
        :param ai_max_retries: AI调用最大重试次数
        :param ai_timeout: AI调用超时时间（秒）
        :param ai_max_tokens: AI调用最大token数量
        """
        self.twitter_api_key = twitter_api_key
        self.llm_client = OpenAI(
            api_key=llm_api_key,
            base_url=llm_url,
        )
        self.data_dir = data_dir
        self.dingtalk_webhook = dingtalk_webhook
        self.dingtalk_secret = dingtalk_secret
        self.enable_dingtalk = enable_dingtalk
        self.ai_max_retries = ai_max_retries
        self.ai_timeout = ai_timeout
        self.ai_max_tokens = ai_max_tokens
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
    
    def get_ai_response(self, prompt: str, max_retries: int = None) -> str:
        """
        调用AI模型获取响应，支持重试机制
        
        :param prompt: 输入提示词
        :param max_retries: 最大重试次数，默认使用配置值
        :return: AI响应内容
        """
        if max_retries is None:
            max_retries = self.ai_max_retries
            
        for attempt in range(max_retries):
            try:
                print(f"🤖 AI调用尝试 {attempt + 1}/{max_retries}")
                
                completion = self.llm_client.chat.completions.create(
                    model="qwen-plus",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    timeout=self.ai_timeout,  # 使用配置的超时时间
                    max_tokens=self.ai_max_tokens  # 使用配置的token数量
                )
                
                response = completion.choices[0].message.content
                if response and response.strip():
                    print(f"✅ AI调用成功 (尝试 {attempt + 1})")
                    return response
                else:
                    print(f"⚠️ AI返回空响应 (尝试 {attempt + 1})")
                    if attempt < max_retries - 1:
                        time.sleep(2)  # 等待2秒后重试
                        continue
                    else:
                        return "AI返回空响应，请重试"
                        
            except Exception as e:
                error_msg = str(e)
                print(f"❌ AI调用出错 (尝试 {attempt + 1}): {error_msg}")
                
                # 根据错误类型决定是否重试
                if "rate limit" in error_msg.lower() or "429" in error_msg:
                    print("🚫 遇到频率限制，等待后重试...")
                    time.sleep(10)  # 频率限制等待10秒
                elif "timeout" in error_msg.lower() or "timed out" in error_msg:
                    print("⏰ 请求超时，等待后重试...")
                    time.sleep(5)  # 超时等待5秒
                elif "invalid api key" in error_msg.lower() or "401" in error_msg:
                    print("🔑 API密钥无效，停止重试")
                    return f"API密钥错误: {error_msg}"
                elif "quota exceeded" in error_msg.lower():
                    print("💳 API配额已用完，停止重试")
                    return f"API配额已用完: {error_msg}"
                elif "data_inspection_failed" in error_msg.lower() or "inappropriate content" in error_msg.lower():
                    print("🚫 内容安全检查失败，尝试内容清理后重试...")
                    # 对于内容安全检查失败，等待更长时间后重试
                    time.sleep(8)  # 内容安全检查失败等待8秒
                    if attempt < max_retries - 1:
                        continue
                    else:
                        return f"内容安全检查失败: 推文内容可能包含不当内容，已尝试清理但仍有问题"
                else:
                    print("❓ 未知错误，等待后重试...")
                    time.sleep(3)  # 其他错误等待3秒
                
                # 如果不是最后一次尝试，继续重试
                if attempt < max_retries - 1:
                    continue
                else:
                    return f"AI处理失败: {error_msg}"
        
        return "AI处理失败: 已达到最大重试次数"
    
    def process_tweet_with_ai(self, tweet_text: str) -> dict:
        """
        使用AI处理推文：翻译、解读、生成标题
        
        :param tweet_text: 推文内容
        :return: 包含AI处理结果的字典
        """
        # 验证推文内容
        if not tweet_text or not tweet_text.strip():
            print("⚠️ 推文内容为空，跳过AI处理")
            return {
                'title': '推文内容为空',
                'translation': '推文内容为空',
                'analysis': '推文内容为空，无法进行分析'
            }
        
        # 内容预处理，过滤可能导致内容安全检查失败的内容
        print("🧹 正在进行内容预处理...")
        cleaned_text = self.preprocess_tweet_content(tweet_text)
        
        # 限制推文长度，避免过长内容导致AI处理失败
        if len(cleaned_text) > 1000:
            print(f"⚠️ 推文内容过长 ({len(cleaned_text)} 字符)，截取前1000字符")
            cleaned_text = cleaned_text[:1000] + "..."
        
        print(f"📝 开始AI处理推文，原始长度: {len(tweet_text)}, 处理后长度: {len(cleaned_text)}")
        
        try:
            # 翻译推文
            print("🔄 正在翻译推文...")
            translate_prompt = f"""请将以下英文推文翻译成中文，保持原意和语气：

推文内容：{cleaned_text}

请只返回翻译结果，不要包含其他说明。"""
            
            translation = self.get_ai_response(translate_prompt)
            print(f"✅ 翻译完成: {translation[:50]}...")
            
            # 解读推文
            print("🔄 正在解读推文...")
            analysis_prompt = f"""请对以下推文进行深度解读分析，包括其含义、背景、可能的影响等,全文内容在160字左右：

推文内容：{cleaned_text}

请从以下角度进行分析：
1. 推文的主要信息和观点
2. 可能的背景和原因
3. 对相关领域的影响
4. 其他值得关注的要点

请用中文回答，内容要有深度和见解。"""
            
            analysis = self.get_ai_response(analysis_prompt)
            print(f"✅ 解读完成: {analysis[:50]}...")
            
            # 生成标题
            print("🔄 正在生成标题...")
            title_prompt = f"""请为以下推文生成一个简洁有力的中文标题，要求：
1. 控制在15-25个字以内
2. 能够准确概括推文的核心内容
3. 具有吸引力和新闻性

推文内容：{cleaned_text}

请只返回标题，不要包含其他内容。"""
            
            title = self.get_ai_response(title_prompt)
            print(f"✅ 标题生成完成: {title}")
            
            # 验证AI处理结果
            if "AI处理失败" in translation or "AI处理失败" in analysis or "AI处理失败" in title:
                print("❌ AI处理结果包含错误信息")
                return {
                    'title': f"处理异常: {title}",
                    'translation': f"翻译异常: {translation}",
                    'analysis': f"解读异常: {analysis}"
                }
            
            return {
                'title': title.strip(),
                'translation': translation.strip(),
                'analysis': analysis.strip()
            }
            
        except Exception as e:
            print(f"❌ AI处理过程出现异常: {str(e)}")
            return {
                'title': f"处理异常: {str(e)[:50]}",
                'translation': f"翻译异常: {str(e)[:50]}",
                'analysis': f"解读异常: {str(e)[:50]}"
            }
    
    def preprocess_tweet_content(self, tweet_text: str) -> str:
        """
        预处理推文内容，过滤可能导致内容安全检查失败的内容
        
        :param tweet_text: 原始推文内容
        :return: 预处理后的内容
        """
        if not tweet_text:
            return ""
        
        # 转换为小写进行检查
        text_lower = tweet_text.lower()
        
        # 定义可能导致内容安全检查失败的词汇模式
        problematic_patterns = [
            # 政治敏感词汇（英文）
            r'\b(trump|biden|politics|government|election|vote|democrat|republican)\b',
            # 暴力相关词汇
            r'\b(kill|death|murder|violence|attack|war|bomb|gun|weapon)\b',
            # 色情相关词汇
            r'\b(sex|porn|nude|naked|sexual|adult)\b',
            # 毒品相关词汇
            r'\b(drug|heroin|cocaine|marijuana|weed|addiction)\b',
            # 其他敏感词汇
            r'\b(hate|racist|discrimination|abuse|suicide)\b'
        ]
        
        import re
        
        # 检查是否包含问题词汇
        has_problematic_content = False
        for pattern in problematic_patterns:
            if re.search(pattern, text_lower):
                has_problematic_content = True
                print(f"⚠️ 检测到可能的问题内容: {pattern}")
                break
        
        if has_problematic_content:
            # 如果检测到问题内容，进行内容清理
            print("🧹 正在进行内容清理...")
            
            # 替换敏感词汇为中性词汇
            replacements = {
                r'\btrump\b': 'former president',
                r'\bbiden\b': 'current president',
                r'\bpolitics\b': 'public affairs',
                r'\bgovernment\b': 'administration',
                r'\belection\b': 'voting process',
                r'\bvote\b': 'participate',
                r'\bkill\b': 'eliminate',
                r'\bdeath\b': 'passing',
                r'\bmurder\b': 'incident',
                r'\bviolence\b': 'conflict',
                r'\battack\b': 'incident',
                r'\bwar\b': 'conflict',
                r'\bbomb\b': 'device',
                r'\bgun\b': 'weapon',
                r'\bweapon\b': 'tool',
                r'\bsex\b': 'relationship',
                r'\bporn\b': 'adult content',
                r'\bnude\b': 'unclothed',
                r'\bnaked\b': 'unclothed',
                r'\bsexual\b': 'intimate',
                r'\badult\b': 'mature',
                r'\bdrug\b': 'substance',
                r'\bheroin\b': 'illegal substance',
                r'\bcocaine\b': 'illegal substance',
                r'\bmarijuana\b': 'cannabis',
                r'\bweed\b': 'cannabis',
                r'\baddiction\b': 'dependency',
                r'\bhate\b': 'dislike',
                r'\bracist\b': 'discriminatory',
                r'\bdiscrimination\b': 'bias',
                r'\babuse\b': 'mistreatment',
                r'\bsuicide\b': 'self-harm'
            }
            
            cleaned_text = tweet_text
            for pattern, replacement in replacements.items():
                cleaned_text = re.sub(pattern, replacement, cleaned_text, flags=re.IGNORECASE)
            
            print(f"✅ 内容清理完成，原始长度: {len(tweet_text)}, 清理后长度: {len(cleaned_text)}")
            return cleaned_text
        
        return tweet_text
    
    def get_tweets_from_account(self, account: str, since_time: datetime, until_time: datetime, exclude_replies: bool = False) -> list:
        """
        获取指定账号在指定时间范围内的推文
        
        :param account: Twitter账号
        :param since_time: 开始时间
        :param until_time: 结束时间
        :param exclude_replies: 是否排除回复推文
        :return: 推文列表
        """
        since_str = since_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        until_str = until_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # 根据配置决定是否排除回复
        if exclude_replies:
            query = f"from:{account} -is:reply since:{since_str} until:{until_str} include:nativeretweets"
        else:
            query = f"from:{account} since:{since_str} until:{until_str} include:nativeretweets"
            
        url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
        params = {"query": query, "queryType": "Latest"}
        headers = {"X-API-Key": self.twitter_api_key}
        
        all_tweets = []
        next_cursor = None
        
        while True:
            if next_cursor:
                params["cursor"] = next_cursor
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                tweets = data.get("tweets", [])
                
                if tweets:
                    for t in tweets:
                        t['author'] = account  # 添加作者信息
                    all_tweets.extend(tweets)
                
                if data.get("has_next_page", False) and data.get("next_cursor", "") != "":
                    next_cursor = data.get("next_cursor")
                    continue
                else:
                    break
            else:
                print(f"获取推文出错: {response.status_code} - {response.text}")
                break
        
        return all_tweets
    
    def save_tweet_data(self, tweet_data: dict):
        """
        保存推文数据到JSON文件，按天存储
        
        :param tweet_data: 推文数据
        """
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(self.data_dir, f"tweets_{today}.json")
        
        # 读取现有数据
        existing_data = []
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
        
        # 检查是否重复 - 根据推文ID去重
        tweet_id = tweet_data.get('id')
        existing_ids = {item.get('id') for item in existing_data if item.get('id')}
        
        if tweet_id not in existing_ids:
            # 添加新数据（仅当ID不重复时）
            existing_data.append(tweet_data)
            print(f"保存新推文: {tweet_id} - {tweet_data.get('author', 'Unknown')}")
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            # 发送钉钉推送
            if self.enable_dingtalk and self.dingtalk_webhook and self.dingtalk_secret:
                try:
                    self.send_dingtalk_notification(tweet_data)
                except Exception as e:
                    print(f"钉钉推送失败: {str(e)}")
        else:
            print(f"跳过重复推文: {tweet_id} - {tweet_data.get('author', 'Unknown')}")
    
    def send_dingtalk_notification(self, tweet_data: dict):
        """
        发送钉钉机器人通知
        
        :param tweet_data: 推文数据
        """
        try:
            import hmac
            import hashlib
            import base64
            import urllib.parse
            import requests
            
            # 构建消息内容
            author = tweet_data.get('author', 'Unknown')
            original_created_at_str = tweet_data.get('created_at', '') # 获取原始推文创建时间字符串
            ai_title = tweet_data.get('ai_title', '')
            ai_content = tweet_data.get('ai_translation', '')
            original_text = tweet_data.get('original_text', '')
            
            # 检查AI处理是否成功，如果失败则使用原文
            ai_processing_failed = False
            if (ai_title and ("处理失败" in ai_title or "内容安全检查失败" in ai_title or "AI标题生成失败" in ai_title)):
                ai_processing_failed = True
            if (ai_content and ("处理失败" in ai_content or "内容安全检查失败" in ai_content)):
                ai_processing_failed = True
            
            # 如果AI处理失败，使用原文内容
            if ai_processing_failed:
                ai_title = "AI处理失败，显示原文"
                ai_content = f"**推文原文：**\n{original_text}"
                print(f"⚠️ AI处理失败，钉钉推送将显示原文内容")
            
            # 确保有内容显示
            if not ai_content:
                ai_content = f"**推文原文：**\n{original_text[:200]}{'...' if len(original_text) > 200 else ''}"
            
            if not ai_title:
                ai_title = 'AI标题生成失败，显示原文'
            
            # 格式化推文发帖时间为北京时间
            formatted_tweet_posting_time = "未知时间"
            try:
                if original_created_at_str:
                    from email.utils import parsedate_to_datetime
                    utc_time = parsedate_to_datetime(original_created_at_str)
                    beijing_time = utc_time + timedelta(hours=8)
                    formatted_tweet_posting_time = beijing_time.strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                print(f"❌ 钉钉通知时间解析错误: {str(e)}")
                formatted_tweet_posting_time = "未知时间"
            
            message = f"""# 🤖 AI新闻推送

---

## 📝 **作者：** {author}
⏰ **发帖时间：** {formatted_tweet_posting_time}

🎯 **AI生成标题：** **{ai_title}**

## 🧠 **AI翻译内容：**
{ai_content}

---

💡 *由 Twitter(X) AI 监控系统 自动推送*"""
            
            # 计算签名
            timestamp = str(int(time.time() * 1000))
            string_to_sign = f'{timestamp}\n{self.dingtalk_secret}'
            hmac_code = hmac.new(
                self.dingtalk_secret.encode('utf-8'),
                string_to_sign.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest()
            sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
            
            # 构建请求URL
            url = f"{self.dingtalk_webhook}&timestamp={timestamp}&sign={sign}"
            
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
                else:
                    print(f"❌ 钉钉消息发送失败: {result.get('errmsg')}")
            else:
                print(f"❌ 钉钉请求失败: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ 钉钉消息发送异常: {str(e)}")
    
    def load_tweets_by_date(self, date_str: str = None) -> list:
        """
        根据日期加载推文数据
        
        :param date_str: 日期字符串 (YYYY-MM-DD)，默认为今天
        :return: 推文数据列表
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        file_path = os.path.join(self.data_dir, f"tweets_{date_str}.json")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
    
    def get_all_tweets(self) -> list:
        """
        获取所有存储的推文数据
        
        :return: 所有推文数据列表
        """
        all_tweets = []
        
        # 遍历数据目录中的所有JSON文件
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.startswith("tweets_") and filename.endswith(".json"):
                    file_path = os.path.join(self.data_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            tweets = json.load(f)
                            all_tweets.extend(tweets)
                    except json.JSONDecodeError:
                        continue
        
        # 按时间排序（最新的在前）
        all_tweets.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return all_tweets
    
    def monitor_and_process(self, target_accounts: list, check_interval: int = 300, hours: int = 1, exclude_replies: bool = False):
        """
        监控Twitter账号并使用AI处理新推文
        
        :param target_accounts: 要监控的账号列表
        :param check_interval: 检查间隔（秒）
        :param hours: 初始回溯时间（小时）
        :param exclude_replies: 是否排除回复推文
        """
        last_checked_time = datetime.utcnow() - timedelta(hours=hours)
        
        def check_and_process_tweets():
            nonlocal last_checked_time
            until_time = datetime.utcnow()
            since_time = last_checked_time
            
            all_tweets = []
            
            for account in target_accounts:
                tweets = self.get_tweets_from_account(account, since_time, until_time, exclude_replies)
                all_tweets.extend(tweets)
                
                # 添加5秒延迟，避免API限制
                if account != target_accounts[-1]:  # 如果不是最后一个账号，添加延迟
                    print("等待5秒，避免API请求限制...")
                    time.sleep(5)
            
            if all_tweets:
                print(f"发现 {len(all_tweets)} 条新推文，开始AI处理...\n")
                
                for idx, tweet in enumerate(all_tweets, start=1):
                    print(f"{'='*60}")
                    print(f"处理推文 {idx}/{len(all_tweets)}")
                    print(f"{'='*60}")
                    
                    # 基本信息
                    tweet_id = tweet.get('id') or tweet.get('id_str')
                    tweet_url = f"https://twitter.com/{tweet['author']}/status/{tweet_id}"
                    original_text = tweet.get('text', '')
                    
                    print(f"作者：{tweet['author']}")
                    print(f"发布时间：{tweet.get('createdAt')}")
                    print(f"原文：{original_text}")
                    print(f"链接：{tweet_url}")
                    print()
                    
                    # AI处理
                    try:
                        print(f"🧠 开始AI处理推文 {idx}/{len(all_tweets)}")
                        ai_result = self.process_tweet_with_ai(original_text)
                        
                        # 检查AI处理结果质量
                        if any("处理异常" in str(v) or "翻译异常" in str(v) or "解读异常" in str(v) for v in ai_result.values()):
                            print(f"⚠️ AI处理结果质量不佳，推文ID: {tweet_id}")
                            # 可以选择跳过保存或标记为低质量
                        
                    except Exception as e:
                        print(f"❌ AI处理推文失败: {str(e)}")
                        
                        # 检查是否是内容安全检查失败
                        if "data_inspection_failed" in str(e).lower() or "inappropriate content" in str(e).lower():
                            print("🚫 内容安全检查失败，使用备用处理策略...")
                            # 使用备用策略：简单的关键词提取和基本翻译
                            ai_result = self.fallback_processing(original_text)
                        else:
                            ai_result = {
                                'title': f"处理失败: {str(e)[:50]}",
                                'translation': f"原文: {original_text[:100]}{'...' if len(original_text) > 100 else ''}",
                                'analysis': f"AI处理失败: {str(e)}"
                            }
                    
                    print(f"AI标题：{ai_result['title']}")
                    print(f"AI翻译：{ai_result['translation']}")
                    print(f"AI解读：{ai_result['analysis']}")
                    print(f"{'='*60}\n")
                    
                    # 保存数据到JSON
                    tweet_data = {
                        'id': tweet_id,
                        'author': tweet['author'],
                        'created_at': tweet.get('createdAt'),
                        'original_text': original_text,
                        'tweet_url': tweet_url,
                        'ai_title': ai_result['title'],
                        'ai_translation': ai_result['translation'],
                        'ai_analysis': ai_result['analysis'],
                        'timestamp': datetime.utcnow().isoformat(),
                        'processed_date': datetime.now().strftime("%Y-%m-%d")
                    }
                    self.save_tweet_data(tweet_data)
                    
                    # 添加延迟避免API频率限制
                    time.sleep(2)
            else:
                print(f"{datetime.utcnow()} - 没有发现新推文。")
            
            last_checked_time = until_time
        
        print(f"开始监控账号: {', '.join(target_accounts)}")
        print(f"检查间隔: {check_interval} 秒")
        print(f"AI处理功能已启用\n")
        
        try:
            while True:
                check_and_process_tweets()
                print(f"等待 {check_interval} 秒后进行下次检查...")
                time.sleep(check_interval)
        except KeyboardInterrupt:
            print("监控已停止。")
    
    def monitor_and_process_with_status(self, target_accounts: list, check_interval: int = 300, hours: int = 1, status_dict: dict = None, exclude_replies: bool = False):
        """
        带状态更新的监控功能
        
        :param target_accounts: 要监控的账号列表
        :param check_interval: 检查间隔（秒）
        :param hours: 初始回溯时间（小时）
        :param status_dict: 状态字典，用于更新前端显示
        :param exclude_replies: 是否排除回复推文
        """
        last_checked_time = datetime.utcnow() - timedelta(hours=hours)
        
        def update_status(status, account="", result=""):
            if status_dict:
                status_dict["current_status"] = status
                status_dict["current_account"] = account
                status_dict["last_update"] = datetime.now().isoformat()
                if result:
                    status_dict["last_result"] = result
                # 计算下次检查时间
                next_time = datetime.now() + timedelta(seconds=check_interval)
                status_dict["next_check_time"] = next_time.isoformat()
        
        def check_and_process_tweets():
            nonlocal last_checked_time
            until_time = datetime.utcnow()
            since_time = last_checked_time
            
            all_tweets = []
            
            try:
                # 更新状态：开始抓取
                update_status("🔍 扫描中", f"{', '.join(target_accounts)}")
                
                for account in target_accounts:
                    try:
                        update_status(f"📡 正在抓取 @{account} 的推文...")
                        tweets = self.get_tweets_from_account(account, since_time, until_time, exclude_replies)
                        all_tweets.extend(tweets)
                        print(f"✅ 成功获取 @{account} 的 {len(tweets)} 条推文")
                        
                        # 添加5秒延迟，避免API限制
                        if account != target_accounts[-1]:  # 如果不是最后一个账号，添加延迟
                            print("等待5秒，避免API请求限制...")
                            time.sleep(5)
                            
                    except Exception as e:
                        print(f"❌ 获取 @{account} 推文失败: {str(e)}")
                        update_status(f"⚠️ @{account} 数据获取异常", result=f"错误: {str(e)}")
                        continue
            except Exception as e:
                print(f"❌ 推文扫描过程出错: {str(e)}")
                update_status(f"⚠️ 扫描过程异常", result=f"错误: {str(e)}")
                return
            
            if all_tweets:
                update_status(f"🤖 发现 {len(all_tweets)} 条新推文，AI分析中...", result=f"找到 {len(all_tweets)} 条新推文")
                
                for idx, tweet in enumerate(all_tweets, start=1):
                    # 基本信息
                    tweet_id = tweet.get('id') or tweet.get('id_str')
                    tweet_url = f"https://twitter.com/{tweet['author']}/status/{tweet_id}"
                    original_text = tweet.get('text', '')
                    
                    # 更新状态：AI处理中
                    update_status(f"🧠 AI处理中... ({idx}/{len(all_tweets)})", f"@{tweet['author']}")
                    
                    # AI处理
                    try:
                        print(f"🧠 开始AI处理推文 {idx}/{len(all_tweets)}")
                        ai_result = self.process_tweet_with_ai(original_text)
                        
                        # 检查AI处理结果质量
                        if any("处理异常" in str(v) or "翻译异常" in str(v) or "解读异常" in str(v) for v in ai_result.values()):
                            print(f"⚠️ AI处理结果质量不佳，推文ID: {tweet_id}")
                            # 可以选择跳过保存或标记为低质量
                        
                    except Exception as e:
                        print(f"❌ AI处理推文失败: {str(e)}")
                        ai_result = {
                            'title': f"处理失败: {str(e)[:50]}",
                            'translation': f"原文: {original_text[:100]}{'...' if len(original_text) > 100 else ''}",
                            'analysis': f"AI处理失败: {str(e)}"
                        }
                    
                    # 保存数据到JSON
                    tweet_data = {
                        'id': tweet_id,
                        'author': tweet['author'],
                        'created_at': tweet.get('createdAt'),
                        'original_text': original_text,
                        'tweet_url': tweet_url,
                        'ai_title': ai_result['title'],
                        'ai_translation': ai_result['translation'],
                        'ai_analysis': ai_result['analysis'],
                        'timestamp': datetime.utcnow().isoformat(),
                        'processed_date': datetime.now().strftime("%Y-%m-%d")
                    }
                    self.save_tweet_data(tweet_data)
                    
                    # 更新处理计数
                    if status_dict:
                        status_dict["processed_tweets"] = status_dict.get("processed_tweets", 0) + 1
                    
                    # 添加延迟避免API频率限制
                    time.sleep(2)
                
                update_status("✅ 处理完成", result=f"成功处理 {len(all_tweets)} 条推文")
            else:
                update_status("⭐ 智能待机中", result="未发现新推文，继续监控中...")
            
            last_checked_time = until_time
        
        update_status("🚀 Neural Network 已启动", f"监控 {len(target_accounts)} 个账号")
        print(f"🚀 监控启动成功，目标账号: {target_accounts}")
        
        try:
            while status_dict and status_dict.get("running", False):
                print(f"🔄 开始新一轮检查循环...")
                check_and_process_tweets()
                
                # 倒计时等待
                for remaining in range(check_interval, 0, -10):
                    if not status_dict.get("running", False):
                        print("🛑 收到停止信号，退出监控")
                        break
                    update_status(f"⏱️ 下次扫描倒计时 {remaining}s", result=status_dict.get("last_result", ""))
                    time.sleep(10)
                    
        except KeyboardInterrupt:
            print("🛑 监控被中断")
            update_status("🛑 Neural Network 已停止")
        except Exception as e:
            print(f"❌ 监控过程出现异常: {str(e)}")
            update_status("❌ 监控异常停止", result=f"错误: {str(e)}")
            if status_dict:
                status_dict["running"] = False

    def fallback_processing(self, tweet_text: str) -> dict:
        """
        备用处理策略：当AI处理失败时，提供基本的信息提取
        
        :param tweet_text: 推文内容
        :return: 基本的处理结果
        """
        print("🔄 启用备用处理策略...")
        
        try:
            # 简单的关键词提取
            import re
            
            # 提取URL
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet_text)
            
            # 提取@用户名
            usernames = re.findall(r'@(\w+)', tweet_text)
            
            # 提取#话题标签
            hashtags = re.findall(r'#(\w+)', tweet_text)
            
            # 提取数字
            numbers = re.findall(r'\d+', tweet_text)
            
            # 简单的长度统计
            word_count = len(tweet_text.split())
            char_count = len(tweet_text)
            
            # 生成基本信息
            title = f"推文分析 (备用处理)"
            
            # 生成基本翻译（保持原文，添加说明）
            translation = f"原文内容: {tweet_text[:200]}{'...' if len(tweet_text) > 200 else ''}"
            
            # 生成基本分析
            analysis_parts = []
            if urls:
                analysis_parts.append(f"包含链接: {len(urls)} 个")
            if usernames:
                analysis_parts.append(f"提及用户: {', '.join(usernames)}")
            if hashtags:
                analysis_parts.append(f"话题标签: {', '.join(hashtags)}")
            if numbers:
                analysis_parts.append(f"数字信息: {', '.join(numbers)}")
            
            analysis_parts.append(f"文本长度: {word_count} 词, {char_count} 字符")
            
            analysis = f"备用分析结果: {'; '.join(analysis_parts)}。由于内容安全检查失败，无法进行AI深度分析。"
            
            print("✅ 备用处理完成")
            return {
                'title': title,
                'translation': translation,
                'analysis': analysis
            }
            
        except Exception as e:
            print(f"❌ 备用处理也失败: {str(e)}")
            return {
                'title': '处理失败',
                'translation': f'原文: {tweet_text[:100]}{"..." if len(tweet_text) > 100 else ""}',
                'analysis': f'AI处理和备用处理均失败: {str(e)}'
            }


# 主程序
if __name__ == "__main__":
    # 从配置文件加载配置
    config_file = "config.json"
    
    # 默认配置
    default_config = {
        "TWITTER_API_KEY": "b74c1eefe1004xxx3c6b82c4ee5",
        "LLM_URL": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "LLM_API_KEY": "sk-bf2a9bf3xxxb344d8bbe5fbdc",
        "TARGET_ACCOUNTS": ["OpenAI"],
        "CHECK_INTERVAL": 300,
        "INITIAL_HOURS": 64,
        "EXCLUDE_REPLIES": False, # 新增配置项
        "DINGTALK_WEBHOOK": "", # 新增配置项
        "DINGTALK_SECRET": "", # 新增配置项
        "ENABLE_DINGTALK": False # 新增配置项
    }
    
    # 读取配置文件
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 合并默认配置
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
        except Exception as e:
            print(f"读取配置文件失败，使用默认配置: {e}")
            config = default_config
    else:
        print("配置文件不存在，使用默认配置")
        config = default_config
    
    # 提取配置参数
    TWITTER_API_KEY = config["TWITTER_API_KEY"]
    LLM_URL = config["LLM_URL"]
    LLM_API_KEY = config["LLM_API_KEY"]
    TARGET_ACCOUNTS = config["TARGET_ACCOUNTS"]
    CHECK_INTERVAL = config["CHECK_INTERVAL"]
    INITIAL_HOURS = config["INITIAL_HOURS"]
    EXCLUDE_REPLIES = config["EXCLUDE_REPLIES"] # 从配置加载
    DINGTALK_WEBHOOK = config["DINGTALK_WEBHOOK"]
    DINGTALK_SECRET = config["DINGTALK_SECRET"]
    ENABLE_DINGTALK = config["ENABLE_DINGTALK"]
    
    print(f"开始监控账号: {', '.join(TARGET_ACCOUNTS)}")
    print(f"检查间隔: {CHECK_INTERVAL}秒")
    print(f"初始回溯: {INITIAL_HOURS}小时")
    print(f"是否排除回复: {EXCLUDE_REPLIES}") # 打印配置
    print(f"是否启用钉钉推送: {ENABLE_DINGTALK}") # 打印配置
    
    # 创建监控器并开始监控
    monitor = TwitterAIMonitor(TWITTER_API_KEY, LLM_URL, LLM_API_KEY, 
                                dingtalk_webhook=DINGTALK_WEBHOOK, 
                                dingtalk_secret=DINGTALK_SECRET, 
                                enable_dingtalk=ENABLE_DINGTALK)
    monitor.monitor_and_process(TARGET_ACCOUNTS, CHECK_INTERVAL, INITIAL_HOURS, EXCLUDE_REPLIES) 