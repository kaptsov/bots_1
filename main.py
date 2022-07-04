import requests
import json
from time import sleep
from dotenv import load_dotenv
import os
import telegram


if __name__ == "__main__":

    load_dotenv()
    telegram_token = os.getenv('BOT_API_KEY')
    devman_token = os.getenv('DEVMAN_API_KEY')
    chat_name = os.getenv("TELEGRAM_CHAT_NAME")
    bot = telegram.Bot(token=telegram_token)
    chat_id = (bot.get_updates())[-1].message.chat_id

    headers = {
        'Authorization': devman_token
    }
    params = {
        'timestamp': '1644999130.418411'
    }
    timeout = 5
    while True:
        try:
            response = requests.get('https://dvmn.org/api/long_polling/',
                                    headers=headers,
                                    params=params,
                                    timeout=timeout)
            response.raise_for_status()
            response_json = response.json()
            print(json.dumps(response_json, indent=4, sort_keys=True))
            bot.send_message(chat_id=chat_id, text="Преподаватель проверил работу!")

            params = {
                'timestamp': f'{response_json["last_attempt_timestamp"]}'
            }

        except requests.exceptions.ReadTimeout:
            print('Read timeout')
        except requests.exceptions.ConnectionError:
            print('Connnection error')
            sleep(timeout)
