import json
import os
from time import sleep, time

import requests
import telegram
from dotenv import load_dotenv
from jinja2 import Template


def main():

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

    timeout = 90

    while True:
        try:
            response = requests.get('https://dvmn.org/api/long_polling/',
                                    headers=headers,
                                    params=params)
            response.raise_for_status()

            review_data = response.json()
            if review_data['status'] == 'timeout':
                print('Продолжаем обновление..')
                params = {'timestamp': review_data['timestamp_to_request']}

            elif review_data['status'] == 'found':
                print('Есть обновление')

                for attempt in review_data['new_attempts']:
                    if attempt['is_negative']:
                        attempt_result_text = 'К сожалению, нашлись ошибки.'
                    else:
                        attempt_result_text = 'Преподавателю все понравилось! Ошибок нет.'

                    with open('templates/message_template.txt') as template_file:
                        template = Template(template_file.read())

                    text = template.render({
                        'lesson_title':
                            attempt["lesson_title"],
                        'lesson_url':
                            attempt["lesson_url"],
                        'attempt_result_text': attempt_result_text
                    })
                    bot.send_message(chat_id=chat_id,
                                     text=text,
                                     parse_mode=telegram.ParseMode.MARKDOWN,
                                     reply_markup=None)

                    params = {
                        'timestamp': {review_data["last_attempt_timestamp"]}
                    }

        except requests.exceptions.ReadTimeout:
            print('Продолжаем обновление..')
        except requests.exceptions.ConnectionError:
            print(f'Ошибка подключения, следующая попытка через {timeout} сек.')
            sleep(timeout)


if __name__ == "__main__":
    main()