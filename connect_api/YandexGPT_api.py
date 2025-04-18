from project_web.data.config import API_KEY_YA as A
# файл в gitingore, поэтому вам нужно создать файл config.py(как config_example.py) и закунить туда ключи из тг
from project_web.data.config import DIRECTORY_ID_YA as D

API_KEY_YA = A  # кину вам в тг ключи
DIRECTORY_ID_YA = D  # кину вам в тг ключи


# обращение к яндекс гпт, передаем пожелания и продукты
def gpt(product, wish=""):
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
                ингредиентов, также вводится его пожелания. Если пользователь пишет какую-то хрень, 
                а не еду, то дай ответ: ничего не понял. 
                Если совсем мало ингредиентов можешь дописать свои, 
                но это в крайних случиях. Страйся не писать одинавое ответы подряд. Не пиши лишних символов, 
                после варината и ингредиинтов пиши 
                устую строку.
                Пример синтаксиса при вводе еды пользователем:
1. Яблочный салат:
   - Ингредиенты: яблоко, морковь, лимонный сок, мёд.
   - Приготовление: яблоко и морковь натереть на крупной тёрке, добавить лимонный сок и мёд по вкусу, перемешать.

2. Яблочные оладьи:
   - Ингредиенты: яблоко, мука, яйцо, сахар, растительное масло.
   - Приготовление: яблоко натереть на мелкой тёрке, добавить муку, яйцо, сахар и перемешать до получения однородной 
   массы. Жарить оладьи на растительном масле.

3. Запечённое яблоко с орехами:
   - Ингредиенты: яблоко, грецкие орехи, мёд, корица.
   - Приготовление: яблоко разрезать пополам, удалить сердцевину, наполнить орехами, полить мёдом и посыпать корицей. 
   Запекать в духовке до мягкости яблока."""
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
