import requests
import time
from datetime import datetime, timedelta

def monitor_tweets(api_key: str, target_accounts: list, check_interval: int = 300, hours: int = 1):
    """
    监控指定 Twitter 账号的新推文，并以中文格式输出信息
    
    :param api_key: TwitterAPI.io API Key
    :param target_accounts: 要监控的账号列表
    :param check_interval: 检查间隔（秒）
    :param hours: 初始回溯时间（小时）
    """
    last_checked_time = datetime.utcnow() - timedelta(hours=hours)
    
    def check_for_new_tweets():
        nonlocal last_checked_time
        until_time = datetime.utcnow()
        since_time = last_checked_time
        
        since_str = since_time.strftime("%Y-%m-%d_%H:%M:%S_UTC")
        until_str = until_time.strftime("%Y-%m-%d_%H:%M:%S_UTC")
        
        all_tweets = []
        
        for account in target_accounts:
            query = f"from:{account} since:{since_str} until:{until_str} include:nativeretweets"
            url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
            params = {"query": query, "queryType": "Latest"}
            headers = {"X-API-Key": api_key}
            
            next_cursor = None
            while True:
                if next_cursor:
                    params["cursor"] = next_cursor
                response = requests.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    data = response.json()
                    tweets = data.get("tweets", [])
                    if tweets:
                        for t in tweets:
                            t['author'] = account  # 添加作者信息
                        all_tweets.extend(tweets)
                    if data.get("has_next_page", False) and data.get("next_cursor","") != "":
                        next_cursor = data.get("next_cursor")
                        continue
                    else:
                        break
                else:
                    print(f"错误: {response.status_code} - {response.text}")
                    break
        
        if all_tweets:
            for idx, tweet in enumerate(all_tweets, start=1):
                tweet_id = tweet.get('id') or tweet.get('id_str')
                tweet_url = f"https://twitter.com/{tweet['author']}/status/{tweet_id}"
                print(f"信息{idx}：")
                print(f"作者：{tweet['author']}")
                print(f"发布时间：{tweet.get('createdAt')}")
                print(f"内容：{tweet.get('text')}")
                print(f"链接：{tweet_url}\n")
        else:
            print(f"{datetime.utcnow()} - 没有新的推文。")
        
        last_checked_time = until_time
    
    print(f"开始监控账号: {', '.join(target_accounts)}")
    print(f"检查间隔: {check_interval} 秒\n")
    
    try:
        while True:
            check_for_new_tweets()
            time.sleep(check_interval)
    except KeyboardInterrupt:
        print("监控已停止。")

# 示例调用
if __name__ == "__main__":
    API_KEY = "x'x'x'xxxxxee5"
    TARGET_ACCOUNT = ["OpenAI"]
    CHECK_INTERVAL = 300  # 5 分钟
    HOURS = 70  # 初始回溯 70 小时
    
    monitor_tweets(API_KEY, TARGET_ACCOUNT, CHECK_INTERVAL, HOURS)
