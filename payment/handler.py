import os
import re
import time
import requests
import json
import urllib.parse
import base64
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
from db_func.database import plus_paid_consult_viber, plus_paid_consult_telegram, check_user_viber, check_user_telegram
from textskeyboards import texts as resources
from textskeyboards import viberkeyboards as kb
from liqpay.liqpay import LiqPay
from textskeyboards import telegramkeyboards as tgkb


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
        if platform == 'viber':
            plus_paid_consult_viber(chat_id, amount)
            tracking_data = {'HISTORY': '', 'CHAT_MODE': 'off'}
            tracking_data = json.dumps(tracking_data)
            user_data = check_user_viber(chat_id)
            logger.info(user_data)
            if user_data[1] > 0:
                reply_keyboard = kb.paid_consult
                reply_text = resources.successfull_payment.replace(
                    '[counter]', str(amount))
            else:
                reply_keyboard = kb.buy_consult
                reply_text = resources.greeting_message
            viber.send_messages(chat_id, [TextMessage(text=reply_text,
                                                      keyboard=reply_keyboard,
                                                      tracking_data=tracking_data)])
        else:
            plus_paid_consult_telegram(chat_id, amount)
            user_data = check_user_telegram(chat_id)
            logger.info(user_data)
            if user_data[1] > 0:
                reply_keyboard = tgkb.paid_consult
                reply_text = resources.successfull_payment.replace(
                    '[counter]', str(amount))
            else:
                reply_keyboard = tgkb.buy_consult
                reply_text = resources.greeting_message
            with open(f'media/{chat_id}/paymessage.txt', 'r') as f:
                message_id = f.read()
            bot.delete_message(chat_id=chat_id,
                               message_id=message_id)
            bot.send_message(
                        chat_id=chat_id,
                        text=reply_text,
                        reply_markup=reply_keyboard)


def liqpay_main(data):
    liqpay = LiqPay(os.getenv('LIQPAY_PUBLIC'),
                    os.getenv('LIQPAY_PRIVATE'))
    decoded_data = json.loads(json.dumps(urllib.parse.parse_qs(data)))
    clean_data = json.loads(base64.b64decode(decoded_data['data'][0]).decode())
    chat_id = str(clean_data['order_id'].split('%%')[0])
    platform = str(clean_data['order_id'].split('%%')[2])
    count = int(clean_data['amount'])
    amount = 0
    if count == 49:
        amount = 1
    if count == 99:
        amount = 3
    if count == 149:
        amount = 5
    payment_status = str(clean_data['status'])
    logger.info(clean_data)
    if payment_status == 'success':
        if platform == 'viber':
            plus_paid_consult_viber(chat_id, amount)
            tracking_data = {'HISTORY': '', 'CHAT_MODE': 'off'}
            tracking_data = json.dumps(tracking_data)
            user_data = check_user_viber(chat_id)
            logger.info(user_data)
            if user_data[1] > 0:
                reply_keyboard = kb.paid_consult
                reply_text = resources.successfull_payment.replace(
                    '[counter]', str(amount))
            else:
                reply_keyboard = kb.buy_consult
                reply_text = resources.greeting_message
            viber.send_messages(chat_id, [TextMessage(text=reply_text,
                                                      keyboard=reply_keyboard,
                                                      tracking_data=tracking_data)])
        else:
            plus_paid_consult_telegram(chat_id, amount)
            user_data = check_user_telegram(chat_id)
            logger.info(user_data)
            if user_data[1] > 0:
                reply_keyboard = tgkb.paid_consult
                reply_text = resources.successfull_payment.replace(
                    '[counter]', str(amount))
            else:
                reply_keyboard = tgkb.buy_consult
                reply_text = resources.greeting_message
            with open(f'media/{chat_id}/paymessage.txt', 'r') as f:
                message_id = f.read()
            bot.delete_message(chat_id=chat_id,
                               message_id=message_id)
            bot.send_message(
                        chat_id=chat_id,
                        text=reply_text,
                        reply_markup=reply_keyboard)
