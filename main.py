import logging
import os
from time import sleep, time

import requests
import telegram
from jinja2 import Template


def main():

    telegram_token = os.environ['BOT_API_KEY']
    devman_token = os.environ['DEVMAN_API_KEY']
    chat_id = os.environ["TELEGRAM_CHAT_NAME"]
    bot = telegram.Bot(token=telegram_token)
    logging.basicConfig(
        filename='logging.log',
        format='%(asctime)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        encoding='utf-8',
        level=logging.INFO
    )

    headers = {
        'Authorization': devman_token
    }
    params = {
        'timestamp': time()
    }

    timeout = 90
    logging.info('Опрос запущен')
    while True:
        try:
            response = requests.get('https://dvmn.org/api/long_polling/',
                                    headers=headers,
                                    params=params)
            response.raise_for_status()

            review_data = response.json()
            if review_data['status'] == 'timeout':
                logging.info('Продолжаем обновление..')
                params = {
                    'timestamp': review_data['timestamp_to_request']
                }

            elif review_data['status'] == 'found':
                logging.info('Есть обновление')

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
                        'timestamp': review_data["last_attempt_timestamp"]
                    }

        except requests.exceptions.ReadTimeout:
            logging.warning('Read timeout')
        except requests.exceptions.ConnectionError:
            logging.warning(f'Ошибка подключения, следующая попытка через {timeout} сек.')
            sleep(timeout)
            logging.warning('Продолжение опроса...')
        except Exception:
            logging.exception('Во время выполнения скипта возникло исключение.')


if __name__ == "__main__":
    main()
