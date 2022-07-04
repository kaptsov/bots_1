import requests
import json
from time import sleep


if __name__ == "__main__":

    headers = {
        'Authorization': 'Token b8b99ace3392933ee675167a51a3799c3b7222d9'
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
        except requests.exceptions.ReadTimeout:
            print('Read timeout')
        except requests.exceptions.ConnectionError:
            print('Connnection error')
            sleep(timeout)
