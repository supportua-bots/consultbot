import os
import glob
import json
import jsonpickle
import time
import base64
import requests
from liqpay.liqpay import LiqPay
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from textskeyboards import texts as resources
from vibertelebot.utils.tools import keyboard_consctructor, save_message_to_history, workdays, divide_chunks
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.contact_message import ContactMessage
from viberbot.api.messages.location_message import LocationMessage
from viberbot.api.messages.rich_media_message import RichMediaMessage
from viberbot.api.messages.picture_message import PictureMessage
from viberbot.api.messages.url_message import URLMessage
from viberbot.api.messages.video_message import VideoMessage
from jivochat import sender as jivochat
from jivochat.utils import resources as jivosource
from textskeyboards import viberkeyboards as kb
from db_func.database import get_phone_viber, add_user_viber, check_user_viber, minus_free_consult_viber, minus_paid_consult_viber, plus_paid_consult_viber, change_stage_to_chat_viber, reset_counter_viber, paid_consults_viber, add_task_for_notification_viber, delete_task_for_notification
from payment.generator import get_payment_link, get_liqpay_link


dotenv_path = os.path.join(Path(__file__).parent.parent, 'config/.env')
load_dotenv(dotenv_path)


logger.add(
    "logs/info.log",
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="100 MB",
    compression="zip",
)


@logger.catch
def upload_image(path):
    url = "https://api.imgbb.com/1/upload"
    api_key = os.getenv('IMAGE_API')
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    params = {
        'key': api_key,
        'image': encoded_string
    }
    r = requests.post(url, data=params)
    return r.json()['data']['url']


@logger.catch
def operator_connection(chat_id, tracking_data, consultancy):
    with open(f'media/{chat_id}/history.txt', 'r') as f:
        history = f.read()
    user_phone = get_phone_viber(chat_id)
    jivochat.send_message(chat_id,
                          str(user_phone),
                          f'{history}\n\n{consultancy}',
                          'viber')
    try:
        with open(f'media/{chat_id}/links.txt', 'r') as f:
            content = f.read()
            if content:
                links = content.split(',')
                for link in links:
                    link = link.split('@')[-1]
                    name = link.split('/')[-1]
                    jivochat.send_photo(
                        chat_id, 'ViberUser', link, name, 'viber')
    except IOError:
        logger.info("File not accessible")
    all_filenames = [i for i in glob.glob(f'media/{chat_id}/*.jpg')]
    for i in all_filenames:
        f = open(i, 'rb')
        os.remove(i)
    try:
        open(f'media/{chat_id}/links.txt', 'w').close()
        open(f'media/{chat_id}/history.txt', 'w').close()
    except:
        pass


def user_message_handler(viber, viber_request):
    """Receiving a message from user and sending replies."""
    logger.info(viber_request)
    message = viber_request.message
    tracking_data = message.tracking_data
    chat_id = viber_request.sender.id
    # Data for usual TextMessage
    reply_text = ''
    reply_keyboard = {}

    if tracking_data is None:
        tracking_data = {'HISTORY': '', 'CHAT_MODE': 'off'}
    else:
        tracking_data = json.loads(tracking_data)
    if isinstance(message, ContactMessage):
        # Handling reply after user shared his contact infromation
        tracking_data['PHONE'] = message.contact.phone_number
        print(message.contact)
        add_user_viber(viber_request.sender.id, message.contact.phone_number)
        user_data = check_user_viber(viber_request.sender.id)
        logger.info(user_data)
        if user_data:
            if user_data[2] > 0:
                reply_keyboard = kb.free_consult
                reply_text = resources.free_consult_message
                add_task_for_notification_viber(viber_request.sender.id)
            elif user_data[1] > 0:
                counter = paid_consults_viber(chat_id)
                reply_keyboard = kb.paid_consult
                reply_text = resources.greeting_message.replace(
                    '[counter]', str(counter))
            else:
                reply_keyboard = kb.buy_consult
                reply_text = resources.greeting_message.replace(
                    '[counter]', '0')
            try:
                open(f'media/{chat_id}/history.txt', 'w').close()
            except:
                pass
        else:
            reply_keyboard = kb.phone_keyboard
            reply_text = 'За цим номером вже створений інший аккаунт.'
        tracking_data = json.dumps(tracking_data)
        reply = [TextMessage(text=reply_text,
                             keyboard=reply_keyboard,
                             tracking_data=tracking_data,
                             min_api_version=3)]
        viber.send_messages(chat_id, reply)
    elif isinstance(message, VideoMessage):
        if tracking_data['CHAT_MODE'] == 'on':
            jivochat.send_video(chat_id, 'ViberUser',
                                viber_request.message.media,
                                viber_request.message_token,
                                'viber')
    elif isinstance(message, URLMessage):
        logger.info('User sent URL')
    elif isinstance(message, PictureMessage):
        response = requests.get(viber_request.message.media)
        if not os.path.exists(f'media/{chat_id}'):
            os.makedirs(f'media/{chat_id}')
        img_path = f"media/{chat_id}/{viber_request.message_token}.jpg"
        with open(img_path, 'wb') as f:
            f.write(response.content)
        link = upload_image(img_path)
        if tracking_data['CHAT_MODE'] == 'on':
            payload = json.loads(jsonpickle.encode(viber_request.message))
            jivochat.send_photo(chat_id, 'ViberUser',
                                link,
                                'user_image',
                                'viber')
    else:
        text = viber_request.message.text
        save_message_to_history(text, 'user', chat_id)
        if text == 'end_chat':
            tracking_data['CHAT_MODE'] = 'off'
        if tracking_data['CHAT_MODE'] == 'on':
            payload = json.loads(jsonpickle.encode(viber_request.message))
            if 'media' in payload:
                jivochat.send_photo(chat_id, 'ViberUser',
                                    viber_request.message.media,
                                    viber_request.message_token,
                                    'viber')
            else:
                user_phone = get_phone_viber(chat_id)
                jivochat.send_message(chat_id, str(user_phone),
                                      text,
                                      'viber')
            reply_keyboard = kb.end_chat_keyboard
        else:
            if text == 'end_chat':
                user_phone = get_phone_viber(chat_id)
                jivochat.send_message(chat_id,
                                      str(user_phone),
                                      jivosource.user_ended_chat,
                                      'viber')
                answer = [TextMessage(text=resources.chat_ending)]
                viber.send_messages(chat_id, answer)
                user_data = check_user_viber(viber_request.sender.id)
                logger.info(user_data)
                link = os.getenv('FEEDBACK_LINK')
                if user_data[2] > 0:
                    reply_keyboard = kb.solved_keyboard_generator(
                        kb.solved_free_consult, link)
                    reply_text = resources.user_finished.replace(
                        '[counter]', '0')
                elif user_data[1] > 0:
                    counter = paid_consults_viber(chat_id)
                    reply_text = resources.user_finished.replace(
                        '[counter]', str(counter))
                    reply_keyboard = kb.solved_keyboard_generator(
                        kb.solved_paid_consult, link)
                else:
                    reply_text = resources.user_finished.replace(
                        '[counter]', '0')
                    reply_keyboard = kb.solved_keyboard_generator(
                        kb.solved_buy_consult, link)
                time.sleep(1)
            elif text == 'issue_solved':
                change_stage_to_chat_viber(chat_id)
                answer = [TextMessage(text=resources.chat_ending)]
                viber.send_messages(chat_id, answer)
                user_data = check_user_viber(viber_request.sender.id)
                link = os.getenv('FEEDBACK_LINK')
                logger.info(user_data)
                if user_data[2] > 0:
                    reply_keyboard = kb.solved_keyboard_generator(
                        kb.solved_free_consult, link)
                    reply_text = resources.free_consult_message
                elif user_data[1] > 0:
                    counter = paid_consults_viber(chat_id)
                    reply_keyboard = kb.solved_keyboard_generator(
                        kb.solved_paid_consult, link)
                    reply_text = resources.greeting_message.replace(
                        '[counter]', str(counter))
                else:
                    reply_keyboard = kb.solved_keyboard_generator(
                        kb.solved_buy_consult, link)
                    reply_text = resources.greeting_message.replace(
                        '[counter]', '0')
                time.sleep(1)
            elif text == 'questions':
                reply_text = resources.faq
                user_data = check_user_viber(viber_request.sender.id)
                logger.info(user_data)
                if user_data[2] > 0:
                    reply_keyboard = kb.solo_free_consult
                elif user_data[1] > 0:
                    counter = paid_consults_viber(chat_id)
                    reply_keyboard = kb.solo_paid_consult
                else:
                    reply_keyboard = kb.solo_buy_consult
            elif text == 'start':
                reply_keyboard = kb.phone_keyboard
                reply_text = resources.phone_message
            elif text == 'free_consult':
                delete_task_for_notification(chat_id)
                tracking_data['CHAT_MODE'] = 'on'
                operator_connection(chat_id, tracking_data,
                                    'Бесплатная консультация')
                minus_free_consult_viber(chat_id)
                reply_keyboard = kb.end_chat_keyboard
                reply_text = resources.operator_message
            elif text == 'consult':
                change_stage_to_chat_viber(chat_id)
                reset_counter_viber(chat_id)
                tracking_data['CHAT_MODE'] = 'on'
                operator_connection(chat_id, tracking_data,
                                    'Уточнение')
                reply_keyboard = kb.end_chat_keyboard
                reply_text = resources.operator_message
            elif text == 'paid_consult':
                tracking_data['CHAT_MODE'] = 'on'
                operator_connection(chat_id, tracking_data,
                                    'Платная консультация')
                minus_paid_consult_viber(chat_id)
                reply_keyboard = kb.end_chat_keyboard
                reply_text = resources.operator_message
            elif text == 'buy_consult':
                user_data = check_user_viber(chat_id)
                amount = user_data[1]
                reply_keyboard = kb.buy_amount
                reply_text = resources.select_amount.replace(
                    '[counter]', str(amount))
            # elif text[:8] == 'purchase':
            #     amount = int(text.split('_')[1])
            #     tracking_data['AMOUNT'] = amount
            #     link = get_payment_link(amount, chat_id, 'viber')
            #     reply_keyboard = kb.payment_keyboard_generator(
            #         kb.payment_proceed, link)
            #     reply_text = resources.please_pay
            elif text[:8] == 'purchase':
                amount = int(text.split('_')[1])
                tracking_data['AMOUNT'] = amount
                phone = check_user_viber(chat_id)[5]
                link = get_liqpay_link(amount, chat_id, 'viber', phone)
                reply_keyboard = kb.payment_keyboard_generator(
                    kb.payment_proceed, link)
                reply_text = resources.please_pay
            elif text[:8] == 'link':
                if 'AMOUNT' in tracking_data:
                    amount = tracking_data['AMOUNT']
                else:
                    amount = 1
                phone = check_user_viber(chat_id)[5]
                link = get_liqpay_link(amount, chat_id, 'viber', phone)
                tracking_data['LINK'] = link
                reply_keyboard = kb.payment_keyboard_generator(
                    kb.payment_proceed, link)
                reply_text = resources.new_link
            elif text == 'payment_completed':
                reply_keyboard = kb.payment_check
                reply_text = resources.please_wait
            elif text[:5] == 'https':
                return logger.info('reply URL')
            else:
                user_data = check_user_viber(chat_id)
                logger.info(user_data)
                if user_data:
                    if user_data[2] > 0:
                        reply_keyboard = kb.free_consult
                        reply_text = resources.free_consult_message
                    elif user_data[1] > 0:
                        counter = paid_consults_viber(chat_id)
                        reply_keyboard = kb.paid_consult
                        reply_text = resources.greeting_message.replace(
                            '[counter]', str(counter))
                    else:
                        reply_keyboard = kb.buy_consult
                        reply_text = resources.greeting_message.replace(
                            '[counter]', '0')
            save_message_to_history(reply_text, 'bot', chat_id)
            logger.info(tracking_data)
            tracking_data = json.dumps(tracking_data)
            reply = [TextMessage(text=reply_text,
                                 keyboard=reply_keyboard,
                                 tracking_data=tracking_data,
                                 min_api_version=6)]
            viber.send_messages(chat_id, reply)
