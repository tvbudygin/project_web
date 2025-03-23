SERVER_KEY = 'ysc2_ribObevsh6D1T4efGfvJlKb0WKhaDLB5N7YCol3y1bd90f01'


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
        timeout=1
    )
    server_output = resp.content.decode()
    if resp.status_code != 200:
        print(f"Allow access due to an error: code={resp.status_code}; message={server_output}", file=sys.stderr)
        return False
    return json.loads(server_output)["status"] == "ok"
