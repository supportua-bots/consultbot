import os
import logging
import requests
from pathlib import Path
from dotenv import load_dotenv
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import (ViberFailedRequest,
                                         ViberConversationStartedRequest,
                                         ViberMessageRequest,
                                         ViberSubscribedRequest)
from loguru import logger
from vibertelebot.handlers import user_message_handler
from vibertelebot.utils.tools import keyboard_consctructor
from textskeyboards import texts as resources
from textskeyboards import viberkeyboards as kb
from db_func.database import add_user, check_user, paid_consults


dotenv_path = os.path.join(Path(__file__).parent.parent, 'config/.env')
load_dotenv(dotenv_path)

viber = Api(BotConfiguration(
    name='ConsultBot',
    avatar=kb.LOGO,
    auth_token=os.getenv('VIBER_TOKEN')
))

logger.add(
    "logs/info.log",
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="100 MB",
    compression="zip",
)


@logger.catch
def main(request):
    viber_request = viber.parse_request(request.get_data())
    # Defining type of the request and replying to it
    if isinstance(viber_request, ViberMessageRequest):
        user_message_handler(viber, viber_request)
    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.user.id, [
            TextMessage(text="Дякую!")
        ])
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn(
            "client failed receiving message. failure: {viber_request}")
    elif isinstance(viber_request, ViberConversationStartedRequest):
        # First touch, sending to user keyboard with phone sharing button
        reply_keyboard = kb.start
        reply_text = resources.description
        viber.send_messages(viber_request.user.id, [
            TextMessage(
                text=reply_text,
                keyboard=reply_keyboard)
            ]
        )
