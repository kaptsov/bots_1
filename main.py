import json
import os
from time import sleep, time

import requests
import telegram
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

env = Environment(
    loader=FileSystemLoader('templates'),
)


if __name__ == "__main__":

    load_dotenv()
    telegram_token = os.getenv('BOT_API_KEY')
    devman_token = os.getenv('DEVMAN_API_KEY')
    chat_id = os.getenv("TELEGRAM_CHAT_NAME")
    bot = telegram.Bot(token=telegram_token)

    headers = {
        'Authorization': devman_token
    }
    params = {
        'timestamp': time()
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
            if response_json['new_attempts'][0]['is_negative']:
                success_text = 'К сожалению, нашлись ошибки.'
            else:
                success_text = 'Преподавателю все понравилось! Ошибок нет.'

            template = env.get_template('message_template.txt')
            text = template.render({
                'lesson_title':
                    response_json["new_attempts"][0]["lesson_title"],
                'lesson_url':
                    response_json["new_attempts"][0]["lesson_url"],
                'success_text': success_text
            })
            bot.send_message(chat_id=chat_id,
                             text=text,
                             parse_mode=telegram.ParseMode.MARKDOWN,
                             reply_markup=None)

            params = {
                'timestamp': f'{response_json["last_attempt_timestamp"]}'
            }

        except requests.exceptions.ReadTimeout:
            print('Продолжаем обновление..')
        except requests.exceptions.ConnectionError:
            print('Connnection error')
            sleep(timeout)
