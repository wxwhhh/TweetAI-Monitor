from openai import OpenAI

def get_model_response(url: str, api_key: str, prompt: str) -> str:
    """
    调用 Qwen 模型返回文字内容

    :param url: 模型 base_url
    :param api_key: API Key
    :param prompt: 用户输入的文本
    :return: 模型返回的文字内容
    """
    client = OpenAI(
        api_key=api_key,
        base_url=url,
    )

    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        # 如果需要，可启用或禁用思考过程
        # extra_body={"enable_thinking": False},
    )

    # 只返回文字内容
    return completion.choices[0].message.content

# 示例调用
if __name__ == "__main__":
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    api_key = "sk-bf2a9bsssc"
    prompt = "你是谁？"

    text = get_model_response(url, api_key, prompt)
    print(text)
