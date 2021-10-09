"""Scipt for setting a webhook for a Viber bot."""
import os
import requests
import json
import logging
from pathlib import Path
from dotenv import load_dotenv


dotenv_path = os.path.join(Path(__file__).parent.parent.parent, 'config/.env')
load_dotenv(dotenv_path)

# Loading Environment variables
URL = os.getenv("URL_HOOK")
# URL = 'https://chatbots2021.support.ua/'

logger = logging.getLogger()
logger.setLevel('DEBUG')

# Setting up webhook parameters
auth_token = os.getenv("VIBER_TOKEN")

hook = 'https://chatapi.viber.com/pa/set_webhook'
headers = {'X-Viber-Auth-Token': auth_token}
body = dict(url=URL + '/viber',
            event_types=['unsubscribed',
                         'conversation_started',
                         'message',
                         'seen',
                         'delivered'])

# Sending POST request to apply a webhook, and printing results
r = requests.post(hook, json.dumps(body), headers=headers)
print(r.json())
logger.info(r.json())
