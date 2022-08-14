import logging
from time import sleep, time

import requests
import telegram
from jinja2 import Template
from environs import Env


logger = logging.getLogger(__file__)

class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def main():

    env = Env()
    env.read_env()

    telegram_token = env('BOT_API_KEY')
    devman_token = env('DEVMAN_API_KEY')
    chat_id = env('TELEGRAM_CHAT_NAME')
    bot = telegram.Bot(token=telegram_token)
    logging.basicConfig(
        format='%(asctime)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        encoding='utf-8',
        level=logging.INFO
    )
    logger.addHandler(TelegramLogsHandler(bot, chat_id))

    headers = {
        'Authorization': devman_token
    }
    params = {
        'timestamp': time()
    }

    timeout = 90
    logger.info('Опрос запущен')
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
                logger.info('Есть обновление')

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
            logger.warning('Read timeout')
        except requests.exceptions.ConnectionError:
            logger.warning(f'Ошибка подключения, следующая попытка через {timeout} сек.')
            sleep(timeout)
            logger.warning('Продолжение опроса...')
        except Exception:
            logger.exception('Во время выполнения скипта возникло исключение.')


if __name__ == "__main__":
    main()
