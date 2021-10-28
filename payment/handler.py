import os
import re
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from telegram import Bot
from telegram.utils.request import Request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.picture_message import PictureMessage
from viberbot.api.viber_requests import (ViberFailedRequest,
                                         ViberConversationStartedRequest,
                                         ViberMessageRequest,
                                         ViberSubscribedRequest)
from vibertelebot.utils.tools import keyboard_consctructor
from vibertelebot.main import viber
from flask import Flask, request, Response, json, jsonify
from loguru import logger
from db_func.database import plus_paid_consult, check_user
from textskeyboards import texts as resources
from textskeyboards import viberkeyboards as kb


dotenv_path = os.path.join(Path(__file__).parent.parent, 'config/.env')
load_dotenv(dotenv_path)

TOKEN = os.getenv("TOKEN")
bot = Bot(token=os.getenv("TOKEN"))


logger.add(
    "logs/info.log",
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="100 MB",
    compression="zip",
)


@logger.catch
def main(data):
    logger.info(data)
    chat_id = str(data['orderReference'].split('%%')[0])
    platform = str(data['orderReference'].split('%%')[2])
    amount = int(data['products'][0]['count'])
    payment_status = data['transactionStatus']
    if payment_status == 'Approved':
        plus_paid_consult(chat_id, amount)
        if platform == 'viber':
            tracking_data = {'HISTORY': '', 'CHAT_MODE': 'off'}
            tracking_data = json.dumps(tracking_data)
            user_data = check_user(chat_id)
            logger.info(user_data)
            if user_data[1] > 0:
                reply_keyboard = kb.paid_consult
                reply_text = resources.successfull_payment
            else:
                reply_keyboard = kb.buy_consult
                reply_text = resources.greeting_message
            viber.send_messages(chat_id, [TextMessage(text=reply_text,
                                                      keyboard=reply_keyboard,
                                                      tracking_data=tracking_data)])
