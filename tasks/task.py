import time
import json
from db_func.database import await_list, plus_wait_counter_viber, plus_wait_counter_telegram, reset_counter_viber, reset_counter_telegram, check_user_telegram, check_user_viber, change_stage_to_chat, paid_consults
from viberbot.api.messages.text_message import TextMessage
from vibertelebot.main import viber
from textskeyboards import viberkeyboards as kb
from textskeyboards import texts as resources
from vibertelebot.handlers import operator_connection
from loguru import logger


def send_message_to_user(user_id):
    change_stage_to_chat(user_id)
    tracking_data = {'HISTORY': '', 'CHAT_MODE': 'off'}
    tracking_data = json.dumps(tracking_data)
    try:
        telegram_check = int(user_id)
        user_data = check_user_telegram(user_id)
    except:
        user_data = check_user_viber(user_id)
    if user_data != []:
        logger.info(user_data)
    if user_data[2] > 0:
        reply_keyboard = kb.free_consult
        reply_text = resources.greeting_message
    elif user_data[1] > 0:
        counter = paid_consults(user_id)
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
