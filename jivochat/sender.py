import os
from pathlib import Path
import requests
from dotenv import load_dotenv
from loguru import logger


dotenv_path = os.path.join(Path(__file__).parent.parent, 'config/.env')
load_dotenv(dotenv_path)
TELEGRAM_URL = os.getenv("JIVO_TELEGRAM_WEBHOOK_URL")
VIBER_URL = os.getenv("JIVO_VIBER_WEBHOOK_URL")

logger.add(
    "logs/info.log",
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="100 MB",
    compression="zip",
)


@logger.catch
def send_message(user_id, name, text, source):
    if source == 'telegram':
        URL = TELEGRAM_URL
    else:
        URL = VIBER_URL
    input = {
        "sender":
            {
                "id": str(user_id),
                "name": f'{name} [{user_id}]',
            },
            "message":
            {
                "type": "text",
                "id": "customer_message_id",
                "text": text
            }
    }
    print(input)
    print(URL)
    x = requests.post(URL,
                      json=input,
                      headers={'content-type': 'application/json'})
    try:
        print(x.json())
    except:
        print(x.text)


@logger.catch
def send_photo(user_id, name, file, filename, source):
    if source == 'telegram':
        URL = TELEGRAM_URL
    else:
        URL = VIBER_URL
    input = {
        "sender":
            {
                "id": str(user_id),
                "name": f'{name} [{user_id}]',
            },
            "message":
            {
                "type": "photo",
                "file": file,
                "file_name": filename
            }
    }
    logger.info(input)
    logger.info(URL)
    x = requests.post(URL,
                      json=input,
                      headers={'content-type': 'application/json'})
    logger.info(x.text)


@logger.catch
def send_video(user_id, name, file, filename, source):
    if source == 'telegram':
        URL = TELEGRAM_URL
        message = {
            "type": "video",
            "file": file,
            "file_name": filename
        }
    else:
        URL = VIBER_URL
        message = {
            "type": "text",
            "id": "customer_message_id",
            "text": str(file)
        }
    input = {
        "sender":
            {
                "id": str(user_id),
                "name": f'{name} [{user_id}]',
            },
            "message": message
    }
    logger.info(input)
    x = requests.post(URL,
                      json=input,
                      headers={'content-type': 'application/json'})


@logger.catch
def send_document(user_id, name, file, filename, source):
    if source == 'telegram':
        URL = TELEGRAM_URL
    else:
        URL = VIBER_URL
    input = {
        "sender":
            {
                "id": user_id,
                "name": f'{name} [{user_id}]',
            },
            "message":
            {
                "type": "document",
                "file": file,
                "file_name": name
            }
    }
    x = requests.post(URL,
                      json=input,
                      headers={'content-type': 'application/json'})


if __name__ == '__main__':
    URL = 'https://wh.jivosite.com/IF6YK0nYgC56npYB/acdHNf3xhl'
    input = {
        "sender":
        {
            "id": "12345",
            "name": "John Doe"
        },
        "message":
        {
            "type": "photo",
            "file": "https://api.telegram.org/file/bot1831293641:AAErIH3bFXlhn7FStlk3A7Q0zbyhpgFKXCI/photos/file_100.jpg",
            "file_name": "150.png"
        }
        }
    logger.info(input)
    logger.info(URL)
    x = requests.post(URL,
                      json=input,
                      headers={'content-type': 'application/json'})
    logger.info(x.text)
