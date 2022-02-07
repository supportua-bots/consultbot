import os
import time
import json
from pathlib import Path
from dotenv import load_dotenv
from db_func.database import (await_list, plus_wait_counter_viber,
                              plus_wait_counter_telegram, reset_counter_viber,
                              reset_counter_telegram, check_user_telegram,
                              check_user_viber, change_stage_to_chat_telegram,
                              change_stage_to_chat_viber, paid_consults_telegram,
                              paid_consults_viber, plus_wait_notification_viber,
                              plus_wait_notification_telegram, notification_list,
                              delete_task_for_notification)
from viberbot.api.messages.text_message import TextMessage
from vibertelebot.main import viber
from telegram import Bot
from telegram.utils.request import Request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler
from textskeyboards import viberkeyboards as kb
from textskeyboards import telegramkeyboards as tgkb
from textskeyboards import texts as resources
from vibertelebot.handlers import operator_connection
from loguru import logger


dotenv_path = os.path.join(Path(__file__).parent.parent, 'config/.env')
load_dotenv(dotenv_path)

TOKEN = os.getenv("TOKEN")

bot = Bot(token=os.getenv("TOKEN"))


def send_message_to_user(user_id):
    tracking_data = {'HISTORY': '', 'CHAT_MODE': 'off'}
    tracking_data = json.dumps(tracking_data)
    try:
        telegram_check = int(user_id)
        user_data = check_user_telegram(user_id)
        change_stage_to_chat_telegram(user_id)
    except:
        user_data = check_user_viber(user_id)
        change_stage_to_chat_viber(user_id)
    if user_data != []:
        logger.info(user_data)
    if user_data[2] > 0:
        reply_keyboard = kb.free_consult
        reply_text = resources.greeting_message
    elif user_data[1] > 0:
        try:
            telegram_check = int(user_id)
            counter = paid_consults_telegram(user_id)
        except:
            counter = paid_consults_viber(user_id)
        reply_keyboard = kb.paid_consult
        reply_text = resources.greeting_message.replace(
            '[counter]', str(counter))
    else:
        reply_keyboard = kb.buy_consult
        reply_text = resources.greeting_message
    viber.send_messages(user_id, [TextMessage(text=reply_text,
                                              keyboard=reply_keyboard,
                                              tracking_data=tracking_data)])


@logger.catch
def task_checker():
    while 1:
        try:
            tasks = await_list()
            logger.info(tasks)
            for item in tasks:
                if int(item[4]) == 59:
                    send_message_to_user(item[0])
                    try:
                        telegram_check = int(item[0])
                        reset_counter_telegram(item[0])
                    except:
                        reset_counter_viber(item[0])
                else:
                    try:
                        telegram_check = int(item[0])
                        plus_wait_counter_telegram(item[0])
                    except:
                        plus_wait_counter_viber(item[0])
        except Exception as e:
            logger.warning(e)
        finally:
            time.sleep(60)


@logger.catch
def send_notification(user_id, platform, text):
    tracking_data = {'HISTORY': '', 'CHAT_MODE': 'off'}
    tracking_data = json.dumps(tracking_data)
    if platform == 'telegram':
        bot.send_message(
                    chat_id=user_id,
                    text=text,
                    reply_markup=tgkb.free_consult)
    else:
        viber.send_messages(user_id, [TextMessage(text=text,
                                                  keyboard=kb.free_consult,
                                                  tracking_data=tracking_data)])


@logger.catch
def notifiers():
    while 1:
        try:
            tasks = notification_list()
            logger.info(tasks)
            for item in tasks:
                if item[1] == 'telegram':
                    plus_wait_notification_telegram(item[0])
                else:
                    plus_wait_notification_viber(item[0])
                if int(item[3]) == 1440:
                    text = resources.push_text_1
                    send_notification(item[0], item[1], text)
                if int(item[3]) == 2880:
                    text = resources.push_text_2
                    send_notification(item[0], item[1], text)
                if int(item[3]) == 4320:
                    text = resources.push_text_3
                    send_notification(item[0], item[1], text)
                    delete_task_for_notification(item[0])
        except Exception as e:
            logger.warning(e)
        finally:
            time.sleep(60)
