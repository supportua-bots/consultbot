import os
import glob
import json
import jsonpickle
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from datetime import date, datetime, timedelta
from textskeyboards import texts as resources
from vibertelebot.utils.tools import keyboard_consctructor, save_message_to_history, workdays, divide_chunks
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.contact_message import ContactMessage
from viberbot.api.messages.location_message import LocationMessage
from viberbot.api.messages.rich_media_message import RichMediaMessage
from viberbot.api.messages.picture_message import PictureMessage
from viberbot.api.messages.video_message import VideoMessage
from jivochat import sender as jivochat
from jivochat.utils import resources as jivosource
from textskeyboards import viberkeyboards as kb


dotenv_path = os.path.join(Path(__file__).parent.parent, 'config/.env')
load_dotenv(dotenv_path)


def user_message_handler(viber, viber_request):
    """Receiving a message from user and sending replies."""
    logger.info(viber_request)
    message = viber_request.message
    tracking_data = message.tracking_data
    chat_id = viber_request.sender.id
    # Data for usual TextMessage
    reply_text = ''
    reply_keyboard = {}
    # Data for RichMediaMessage
    reply_alt_text = ''
    reply_rich_media = {}

    if tracking_data is None:
        tracking_data = {'NAME': 'ViberUser', 'HISTORY': '',
                         'CHAT_MODE': 'off', 'STAGE': 'menu'}
    else:
        tracking_data = json.loads(tracking_data)

    if isinstance(message, ContactMessage):
        # Handling reply after user shared his contact infromation
        tracking_data['PHONE'] = message.contact.phone_number
        reply_keyboard = kb.category_keyboard
        reply_text = resources.category_message
        tracking_data['STAGE'] = 'category'
        tracking_data = json.dumps(tracking_data)
        reply = [TextMessage(text=reply_text,
                             keyboard=reply_keyboard,
                             tracking_data=tracking_data,
                             min_api_version=3)]
        viber.send_messages(chat_id, reply)
    elif isinstance(message, VideoMessage):
        if tracking_data['CHAT_MODE'] == 'on':
            jivochat.send_video(chat_id, tracking_data['NAME'],
                                viber_request.message.media,
                                viber_request.message_token,
                                'viber')
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
            jivochat.send_photo(chat_id, tracking_data['NAME'],
                                link,
                                'user_image',
                                'viber')
        else:
            file_links = open(f'media/{chat_id}/links.txt', 'a')
            file_links.write(f'{link},')
            file_links.close()
            if tracking_data['STAGE'] == 'photo_serial':
                reply_keyboard = kb.opeartor_keyboard
                reply_text = resources.photo_guarantee_message
                tracking_data['STAGE'] = 'photo_guarantee'
            elif tracking_data['STAGE'] == 'photo_guarantee':
                reply_keyboard = kb.opeartor_keyboard
                reply_text = resources.photo_check_message
                tracking_data['STAGE'] = 'photo_check'
            elif tracking_data['STAGE'] == 'photo_check':
                reply_text = resources.reason_message
                tracking_data['STAGE'] = 'reason'
                keyboard = kb.opeartor_keyboard
            else:
                reply_keyboard = kb.opeartor_keyboard
                reply_text = resources.photo_error
            save_message_to_history(reply_text, 'bot', chat_id)
            logger.info(tracking_data)
            tracking_data = json.dumps(tracking_data)
            reply = [TextMessage(text=reply_text,
                                 keyboard=reply_keyboard,
                                 tracking_data=tracking_data,
                                 min_api_version=3)]
            viber.send_messages(chat_id, reply)
    else:
        text = viber_request.message.text
        save_message_to_history(text, 'user', chat_id)
        if text == 'end_chat':
            tracking_data['CHAT_MODE'] = 'off'
        if tracking_data['CHAT_MODE'] == 'on':
            payload = json.loads(jsonpickle.encode(viber_request.message))
            if 'media' in payload:
                jivochat.send_photo(chat_id, tracking_data['NAME'],
                                    viber_request.message.media,
                                    viber_request.message_token,
                                    'viber')
            else:
                jivochat.send_message(chat_id, tracking_data['NAME'],
                                      text,
                                      'viber')
            reply_keyboard = kb.end_chat_keyboard

        else:
            if text == 'menu':
                reply_keyboard = kb.menu_keyboard
                reply_text = resources.greeting_message
                try:
                    open(f'media/{chat_id}/history.txt', 'w').close()
                except:
                    pass
            elif text == 'end_chat':
                jivochat.send_message(chat_id,
                                      tracking_data['NAME'],
                                      jivosource.user_ended_chat,
                                      'viber')
                answer = [TextMessage(text=resources.chat_ending)]
                viber.send_messages(chat_id, answer)
                reply_keyboard = kb.menu_keyboard
                reply_text = resources.greeting_message
                time.sleep(1)
            elif text == 'operator':
                chat_available = chat_availability_check()
                if chat_available:
                    tracking_data['CHAT_MODE'] = 'on'
                    reply_keyboard = kb.end_chat_keyboard
                    reply_text = resources.operator_message
                    with open(f'media/{chat_id}/history.txt', 'r') as f:
                        history = f.read()
                    jivochat.send_message(chat_id,
                                          tracking_data['NAME'],
                                          history,
                                          'viber')
                    try:
                        with open(f'media/{chat_id}/links.txt', 'r') as f:
                            content = f.read()
                            links = content.split(',')
                            for link in links:
                                name = link.split('/')[-1]
                                jivochat.send_photo(
                                    chat_id, tracking_data['NAME'], link, name, 'viber')
                    except IOError:
                        print("File not accessible")
                    tracking_data['HISTORY'] = ''
                    all_filenames = [i for i in glob.glob(
                        f'media/{chat_id}/*.jpg')]
                    for i in all_filenames:
                        f = open(i, 'rb')
                        os.remove(i)
                    try:
                        open(f'media/{chat_id}/links.txt', 'w').close()
                        open(f'media/{chat_id}/history.txt', 'w').close()
                    except:
                        pass
                else:
                    answer = [TextMessage(text=resources.operator_unavailable)]
                    viber.send_messages(chat_id, answer)
                    reply_keyboard = kb.menu_keyboard
                    reply_text = resources.greeting_message
                    time.sleep(1)
            elif text == 'video':
                reply_keyboard = kb.confirmation_keyboard
                reply_text = resources.video_acceptance_message
            elif text == 'continue':
                reply_keyboard = kb.opeartor_keyboard
                reply_text = resources.name_message
                tracking_data['STAGE'] = 'name'
            elif text[:5] == 'brand':
                tracking_data['BRAND'] = text.split('-')[1]
                reply_keyboard = kb.opeartor_keyboard
                reply_text = resources.serial_number_message
                tracking_data['STAGE'] = 'serial'
            elif text[:8] == 'category':
                pick = ''
                for item in kb.categories:
                    if item[1] == text:
                        pick = item[0]
                tracking_data['CATEGORY'] = pick
                reply_keyboard = kb.brand_keyboard
                reply_text = resources.brand_message
                tracking_data['STAGE'] = 'menu'
            elif text == 'reason':
                list_of_dates = schedule_matcher()[:18]
                beautified_dates = [(datetime.strptime(
                    x[0], '%Y-%m-%d').strftime('%d.%m'), f'date%{x[0]}', '') for x in list_of_dates]
                reply_keyboard = keyboard_consctructor(beautified_dates)
                reply_text = resources.date_message
                tracking_data['STAGE'] = 'menu'
            elif text[:4] == 'date':
                choosed_date = text.split('%')[1]
                tracking_data['DATE'] = choosed_date
                choosed_item = []
                list_of_dates = schedule_matcher()[:18]
                for dates in list_of_dates:
                    if dates[0] == choosed_date:
                        choosed_item = dates
                keyboard = [(x[0], f'time%{x[0]}', '')
                            for x in choosed_item[1]]
                keyboard.append(kb.back_to_date)
                reply_keyboard = keyboard_consctructor(keyboard)
                reply_text = resources.time_message
            elif text[:4] == 'time':
                tracking_data['TIME'] = text.split('%')[1]
                answer = ''
                if 'NAME' in tracking_data.keys():
                    answer += f"Прiзвище та Ім'я: {tracking_data['NAME']}\n"
                if 'PHONE' in tracking_data.keys():
                    answer += f'Номер: {tracking_data["PHONE"]}\n'
                if 'CATEGORY' in tracking_data.keys():
                    answer += f'Категорiя: {tracking_data["CATEGORY"]}\n'
                if 'BRAND' in tracking_data.keys():
                    answer += f'Бренд: {tracking_data["BRAND"]}\n'
                if 'SERIAL_NUMBER' in tracking_data.keys():
                    answer += f'Серiйний номер: {tracking_data["SERIAL_NUMBER"]}\n'
                if 'REASON' in tracking_data.keys():
                    answer += f'Причина: {tracking_data["REASON"]}\n'
                if 'DATE' in tracking_data.keys():
                    answer += f'Дата: {tracking_data["DATE"]}\n'
                if 'TIME' in tracking_data.keys():
                    answer += f'Час: {tracking_data["TIME"]}\n'
                datetime_string = f'{tracking_data["DATE"]} {tracking_data["TIME"]}'
                beautified_date = datetime.strptime(
                    datetime_string, '%Y-%m-%d %H:%M')
                deal_id = add_to_crm(category=tracking_data["CATEGORY"],
                                     reason=tracking_data["REASON"],
                                     phone=tracking_data["PHONE"],
                                     brand=tracking_data["BRAND"],
                                     serial=tracking_data["SERIAL_NUMBER"],
                                     name=tracking_data['NAME'],
                                     date=tracking_data["DATE"],
                                     time=beautified_date)
                viber.send_messages(chat_id, [TextMessage(text=answer)])
                timestamp_start = datetime.timestamp(beautified_date)
                timestamp_end = datetime.timestamp(
                    beautified_date + timedelta(minutes=30))
                add_event(timestamp_start, timestamp_end,
                          f'Вiдео дзiнок з {tracking_data["NAME"]}', deal_id)
                tracking_data['HISTORY'] = ''
                reply_keyboard = kb.return_keyboard
                reply_text = resources.final_message_viber
                all_filenames = [i for i in glob.glob(
                    f'media/{chat_id}/*.jpg')]
                for i in all_filenames:
                    f = open(i, 'rb')
                    # context.bot.send_document(chat_id=update.callback_query.message.chat.id, document=f)
                    os.remove(i)
                with open(f'media/{chat_id}/links.txt', 'r') as links:
                    text = links.read()
                    for link in text.split(','):
                        if link != '':
                            add_comment(deal_id, link)
                open(f'media/{chat_id}/links.txt', 'w').close()
            else:
                if tracking_data['STAGE'] == 'name':
                    tracking_data['NAME'] = text
                    reply_keyboard = addkb.SHARE_PHONE_KEYBOARD
                    reply_text = resources.phone_message
                    tracking_data['STAGE'] = 'phone'
                elif tracking_data['STAGE'] == 'phone':
                    if text[:3] == '380' and len(text) == 12:
                        tracking_data['PHONE'] = text
                        # keyboard = [("Зв'язок з оператором", 'operator', 'https://i.ibb.co/6ZZqWPM/image.png')]
                        reply_keyboard = kb.category_keyboard
                        reply_text = resources.category_message
                        tracking_data['STAGE'] = 'category'
                    else:
                        reply_keyboard = addkb.SHARE_PHONE_KEYBOARD
                        reply_text = resources.phone_error
                elif tracking_data['STAGE'] == 'serial':
                    text = text.replace(' ', '')
                    if len(text) == 16 and text.isdecimal() and text[0] == '3':
                        tracking_data['SERIAL_NUMBER'] = text
                        reply_keyboard = kb.opeartor_keyboard
                        reply_text = resources.photo_serial_message
                        tracking_data['STAGE'] = 'photo_serial'
                    else:
                        reply_keyboard = kb.opeartor_keyboard
                        reply_text = resources.serial_number_error
                        tracking_data['STAGE'] = 'serial'
                elif tracking_data['STAGE'] == 'photo_serial':
                    reply_keyboard = kb.opeartor_keyboard
                    reply_text = resources.photo_error
                elif tracking_data['STAGE'] == 'photo_guarantee':
                    reply_keyboard = kb.opeartor_keyboard
                    reply_text = resources.photo_error
                elif tracking_data['STAGE'] == 'photo_check':
                    reply_keyboard = kb.opeartor_keyboard
                    reply_text = resources.photo_error
                elif tracking_data['STAGE'] == 'reason':
                    tracking_data['REASON'] = text
                    list_of_dates = schedule_matcher()[:18]
                    beautified_dates = [(datetime.strptime(
                        x[0], '%Y-%m-%d').strftime('%a, %d %b'), f'date%{x[0]}', '') for x in list_of_dates]
                    reply_keyboard = keyboard_consctructor(beautified_dates)
                    reply_text = resources.date_message
                    tracking_data['STAGE'] = 'menu'
                else:
                    reply_keyboard = kb.return_keyboard
                    reply_text = resources.echo_message_viber
            save_message_to_history(reply_text, 'bot', chat_id)
            counter = 0
            for item in tracking_data.keys():
                counter += len(item)
                counter += len(tracking_data[item])
            logger.info(counter)
            logger.info(tracking_data)
            tracking_data = json.dumps(tracking_data)
            reply = [TextMessage(text=reply_text,
                                 keyboard=reply_keyboard,
                                 tracking_data=tracking_data,
                                 min_api_version=6)]
            viber.send_messages(chat_id, reply)
