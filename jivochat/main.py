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
from jivochat.utils import resources
from loguru import logger
from textskeyboards import texts
from textskeyboards import viberkeyboards
from textskeyboards import telegramkeyboards
from db_func.database import change_stage_to_await


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
def main(data, source):
    logger.info(data)
    if 'event_name' not in data:
        if data['message']['type'] == 'text':
            user = data['recipient']['id']
            print(user)
            text = data['message']['text']
            print(text)
            if source == 'telegram':
                bot.send_message(user, text)
            else:
                tracking_data = {'NAME': user, 'HISTORY': '',
                                 'CHAT_MODE': 'on', 'STAGE': 'menu'}
                tracking_data = json.dumps(tracking_data)
                keyboard = [('Завершити чат', 'end_chat')]
                reply_keyboard = keyboard_consctructor(keyboard)
                viber.send_messages(user, [TextMessage(text=text,
                                                       keyboard=reply_keyboard,
                                                       tracking_data=tracking_data)])
        if data['message']['type'] == 'photo':
            user = data['recipient']['id']
            print(user)
            link = data['message']['file']
            if source == 'telegram':
                bot.send_photo(user, link)
            else:
                tracking_data = {'NAME': user, 'HISTORY': '',
                                 'CHAT_MODE': 'on', 'STAGE': 'menu'}
                tracking_data = json.dumps(tracking_data)
                keyboard = [('Завершити чат', 'end_chat')]
                reply_keyboard = keyboard_consctructor(keyboard)
                viber.send_messages(user, [PictureMessage(text='',
                                                          keyboard=reply_keyboard,
                                                          tracking_data=tracking_data,
                                                          media=link)])
    else:
        if data['event_name'] == 'chat_finished':
            if source == 'telegram':
                user_id = int(re.findall(
                    f'\[(.*?)\]', data['visitor']['name'])[0])
                reply_markup = ReplyKeyboardRemove()
                bot.send_message(
                            chat_id=user_id,
                            text=texts.operator_ended_chat,
                            reply_markup=telegramkeyboards.clarificational_consult)
            else:
                user_id = str(re.findall(
                    f'\[(.*?)\]', data['visitor']['name'])[0])
                tracking_data = {'HISTORY': '', 'CHAT_MODE': 'off'}
                tracking_data = json.dumps(tracking_data)
                change_stage_to_await(user_id)
                viber.send_messages(user_id, [TextMessage(text=texts.operator_ended_chat,
                                                          keyboard=viberkeyboards.clarificational_consult,
                                                          tracking_data=tracking_data)])
    returned_data = {'result': 'ok'}
    return returned_data
