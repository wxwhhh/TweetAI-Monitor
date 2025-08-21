import requests
import json
import time

# 加载配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

api_key = config['TWITTER_API_KEY']
print(f"使用API密钥: {api_key[:5]}...{api_key[-5:]}")

# 测试函数
def test_account(account_name):
    print(f"\n测试{account_name}账号:")
    url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
    params = {"query": f"from:{account_name}", "queryType": "Latest"}
    headers = {"X-API-Key": api_key}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            tweets = data.get("tweets", [])
            print(f"获取到 {len(tweets)} 条{account_name}推文")
            return len(tweets)
        else:
            print(f"API请求失败: {response.text}")
            return 0
    except Exception as e:
        print(f"请求出错: {str(e)}")
        return 0

# 测试Google账号
google_count = test_account("Google")

# 等待5秒，避免API限制
print("等待5秒，避免API请求限制...")
time.sleep(5)

# 测试OpenAI账号
openai_count = test_account("OpenAI")

print("\n总结:")
print(f"Google: {google_count}条推文")
print(f"OpenAI: {openai_count}条推文") 