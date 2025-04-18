from project_web.data.config import SERVER_KEY as S
# файл в gitingore, поэтому вам нужно создать файл config.py(как config_example.py) и закунить туда ключи из тг
SERVER_KEY = S  # кину вам в тг ключи


# проверка капчи на сервере яндекса
def check_captcha(token, user_ip):
    import requests
    import json
    import sys

    resp = requests.post(
        "https://smartcaptcha.yandexcloud.net/validate",
        data={
            "secret": SERVER_KEY,
            "token": token,
            "ip": user_ip
        },
        timeout=5
    )
    server_output = resp.content.decode()
    if resp.status_code != 200:
        print(f"Allow access due to an error: code={resp.status_code}; message={server_output}", file=sys.stderr)
        return False
    return json.loads(server_output)["status"] == "ok"
