import requests


ADMIN = 453529592
BOT_TOKEN = '8144296084:AAH2oHo9rGEkPg49uVX7KwugJnPKt7bNDuA'

def send_tg_message(message):
    telegram_api_url = (
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    )

    data = {"chat_id": ADMIN, "text": message}
    response = requests.post(telegram_api_url, data=data)

