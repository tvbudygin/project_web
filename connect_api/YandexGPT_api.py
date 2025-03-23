API_KEY_YA = '..'
DIRECTORY_ID_YA = ".."


def gpt(product, wish):
    import requests
    import json

    auth_headers = {
        'Authorization': f'Api-Key {API_KEY_YA}',
    }
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
    data = {
        "modelUri": f'gpt://{DIRECTORY_ID_YA}/yandexgpt-lite',
        "completionOptions": {
            "stream": False,
            "temperature": 0.1,
            "maxTokens": "1000"
        },
        "messages": [
            {
                "role": "system",
                "text": f"""Напиши 3 возможные варианта рецепта еды из предоставленных пользователем 
                ингредиентов, также вводится его пожелания. Если совсем мало ингредиентов можешь дописать свои, 
                но в крайних случиях. Также присылай ссулку на фотку"""
            },
            {
                "role": "user",
                "text": f"{product}\t{wish}"
            }
        ]
    }
    data = json.dumps(data)
    resp = requests.post(url, headers=auth_headers, data=data)

    if resp.status_code == 200:
        result = json.loads(resp.text)
        result = result['result']['alternatives'][0]['message']['text']
        return result
    return "No answer from yandexGPT."


if __name__ == '__main__':
    print(gpt("яблоко", "обед"))
