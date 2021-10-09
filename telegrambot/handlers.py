import os
import time
import requests
import locale
import json
import jsonpickle
import glob
# import pprint
from pathlib import Path
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, Update,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton)
from telegram.ext import CallbackContext, ConversationHandler
from textskeyboards import texts as resources
from jivochat import sender as jivochat
from jivochat.utils import resources as jivosource
from bitrix.calendar_tools import schedule_matcher, add_event, add_to_crm, add_comment, upload_image, chat_availability_check
from textskeyboards import telegramkeyboards as kb


dotenv_path = os.path.join(Path(__file__).parent.parent, 'config/.env')
load_dotenv(dotenv_path)
# pp = pprint.PrettyPrinter(indent=4)
TOKEN = os.getenv("TOKEN")

locale.setlocale(locale.LC_TIME, 'uk_UA.UTF-8')
NAME, PHONE, CATEGORY, SERIAL_NUMBER, PHOTOS, REASON, CHAT = range(7)


def choice_definer(update):
    keyboard = update.callback_query.message.reply_markup.inline_keyboard
    choice = ''
    for item in keyboard:
        if item[0].callback_data == update.callback_query.data:
            choice = item[0].text
    return choice


def save_message_to_history(message, type):
    text = ''
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    if type == 'bot':
        text += 'Bot '
    else:
        text += 'User '
    text += f'{now}: {message}\n'
    return text


def workdays(d, end, excluded=(6, 7)):
    days = []
    while d.date() <= end.date():
        if d.isoweekday() not in excluded:
            days.append(d)
        d += timedelta(days=1)
    return days[1:21]


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def greetings_handler(update: Update, context: CallbackContext):
    menu_handler(update, context)


def menu_handler(update: Update, context: CallbackContext):
    if 'NAME' not in context.user_data:
        context.user_data['NAME'] = 'TelegramUser'
    context.user_data['HISTORY'] = ''
    inline_keyboard = [
        [
            InlineKeyboardButton(text=kb.menu_keyboard[0],
                                 callback_data='video')
        ], [
            InlineKeyboardButton(text=kb.menu_keyboard[1],
                                 callback_data='operator'),
        ],
    ]
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    try:
        request = update.callback_query
        choice = choice_definer(update)
        context.user_data['HISTORY'] += save_message_to_history(choice, 'user')
        update.callback_query.edit_message_text(
            text=update.callback_query.message.text
        )
        context.bot.send_message(chat_id=update.callback_query.message.chat.id,
                                 text=resources.greeting_message,
                                 reply_markup=inline_buttons)
    except AttributeError:
        request = update.message
        context.bot.send_message(chat_id=update.message.from_user.id,
                                 text=resources.greeting_message,
                                 reply_markup=inline_buttons)
    context.user_data['HISTORY'] += save_message_to_history(
        resources.greeting_message, 'bot')
    return ConversationHandler.END


def operator_handler(update: Update, context: CallbackContext):
    if 'NAME' not in context.user_data:
        context.user_data['NAME'] = 'TelegramUser'
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    chat_available = chat_availability_check()
    if chat_available:
        contact_keyboard = KeyboardButton('Завершити чат')
        reply_markup = ReplyKeyboardMarkup(keyboard=[[contact_keyboard]],
                                           resize_keyboard=True)
        context.user_data['HISTORY'] += save_message_to_history(
            resources.operator_message, 'bot')
        try:
            request = update.callback_query
            chat_id = update.callback_query.message.chat.id
            update.callback_query.edit_message_text(
                text=update.callback_query.message.text
            )
            context.bot.send_message(chat_id=update.callback_query.message.chat.id,
                                     text=resources.operator_message,
                                     reply_markup=reply_markup)
        except:
            request = update.message
            chat_id = update.message.from_user.id
            context.bot.send_message(chat_id=update.message.from_user.id,
                                     text=resources.operator_message,
                                     reply_markup=reply_markup)
        jivochat.send_message(chat_id,
                              context.user_data['NAME'],
                              context.user_data['HISTORY'],
                              'telegram')
        try:
            with open(f'media/{chat_id}/links.txt', 'r') as f:
                content = f.read()
                links = content.split(',')
                for link in links:
                    name = link.split('/')[-1]
                    if name[-3:] == 'jpg':
                        jivochat.send_photo(
                            chat_id, context.user_data['NAME'], link, name, 'telegram')
                    else:
                        jivochat.send_document(
                            chat_id, context.user_data['NAME'], link, name, 'telegram')
        except IOError:
            print("File not accessible")
        context.user_data['HISTORY'] = ''
        all_filenames = [i for i in glob.glob(f'media/{chat_id}/*.jpg')]
        for i in all_filenames:
            f = open(i, 'rb')
            os.remove(i)
        try:
            open(f'media/{chat_id}/links.txt', 'w').close()
        except:
            pass
        return CHAT
    else:
        inline_keyboard = [
            [
                InlineKeyboardButton(text=kb.menu_keyboard[0],
                                     callback_data='video')
            ], [
                InlineKeyboardButton(text=kb.menu_keyboard[1],
                                     callback_data='operator'),
            ],
        ]
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        reply_markup = ReplyKeyboardRemove()
        context.bot.send_message(chat_id=update.callback_query.message.chat.id,
                                 text=resources.operator_unavailable,
                                 reply_markup=reply_markup)
        time.sleep(1)
        context.bot.send_message(chat_id=update.callback_query.message.chat.id,
                                 text=resources.greeting_message,
                                 reply_markup=inline_buttons)
        return ConversationHandler.END


def chat_handler(update: Update, context: CallbackContext):
    reply = update.message.text
    payload = json.loads(jsonpickle.encode(update.message))
    chat_id = update.message.from_user.id
    # pp.pprint(payload)
    if payload and payload['photo'] and not payload['video']:
        file = context.bot.get_file(
            update.message.photo[-1].file_id)['file_path']
        name = file.split('/')[-1]
        jivochat.send_photo(
            chat_id, context.user_data['NAME'], file, name, 'telegram')
        return CHAT
    elif payload and payload['document']:
        file = context.bot.get_file(
            update.message.document.file_id)['file_path']
        name = file.split('/')[-1]
        jivochat.send_document(
            chat_id, context.user_data['NAME'], file, name, 'telegram')
        return CHAT
    elif payload and payload['video']:
        file = context.bot.get_file(
            update.message.video.file_id)['file_path']
        name = file.split('/')[-1]
        jivochat.send_video(
            chat_id, context.user_data['NAME'], file, name, 'telegram')
        return CHAT
    elif reply == 'Завершити чат':
        inline_keyboard = [
            [
                InlineKeyboardButton(text=kb.menu_keyboard[0],
                                     callback_data='video')
            ], [
                InlineKeyboardButton(text=kb.menu_keyboard[1],
                                     callback_data='operator'),
            ],
        ]
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        reply_markup = ReplyKeyboardRemove()
        jivochat.send_message(update.message.from_user.id,
                              context.user_data['NAME'],
                              jivosource.user_ended_chat,
                              'telegram')
        context.bot.send_message(chat_id=update.message.from_user.id,
                                 text=resources.chat_ending,
                                 reply_markup=reply_markup)
        time.sleep(1)
        context.bot.send_message(chat_id=update.message.from_user.id,
                                 text=resources.greeting_message,
                                 reply_markup=inline_buttons)
        return ConversationHandler.END
    else:
        jivochat.send_message(update.message.from_user.id,
                              context.user_data['NAME'],
                              reply,
                              'telegram')
        return CHAT


def echo_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    message = update.message.text
    context.user_data['HISTORY'] += save_message_to_history(message, 'user')
    update.message.reply_text(
        resources.echo_message,
    )
    context.user_data['HISTORY'] += save_message_to_history(
        resources.echo_message, 'bot')
    return ConversationHandler.END


def video_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    context.user_data['ID'] = update.callback_query.message.chat.id
    choice = choice_definer(update)
    context.user_data['HISTORY'] += save_message_to_history(choice, 'user')
    inline_keyboard = [
        [
            InlineKeyboardButton(text=kb.continue_keyboard[0],
                                 callback_data='continue')
        ], [
            InlineKeyboardButton(text=kb.continue_keyboard[1],
                                 callback_data='start'),
        ],
    ]
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    update.callback_query.edit_message_text(
        text=f'{update.callback_query.message.text}\nВаш вибір: {choice}')
    context.bot.send_message(chat_id=context.user_data['ID'],
                             text=resources.video_acceptance_message,
                             reply_markup=inline_buttons)
    context.user_data['HISTORY'] += save_message_to_history(
        resources.video_acceptance_message, 'bot')
    return ConversationHandler.END


def acceptance_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    choice = choice_definer(update)
    context.user_data['HISTORY'] += save_message_to_history(choice, 'user')
    contact_keyboard = KeyboardButton("Зв'язок з оператором")
    reply_markup = ReplyKeyboardMarkup(keyboard=[[contact_keyboard]],
                                       resize_keyboard=True)
    update.callback_query.edit_message_text(
        text=f'{update.callback_query.message.text}\nВаш вибір: {choice}'
    )
    context.bot.send_message(chat_id=context.user_data['ID'],
                             text=resources.name_message,
                             reply_markup=reply_markup)
    context.user_data['HISTORY'] += save_message_to_history(
        resources.name_message, 'bot')
    return NAME


def name_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    context.user_data['NAME'] = update.message.text
    message = update.message.text
    context.user_data['HISTORY'] += save_message_to_history(message, 'user')
    contact_keyboard = [[KeyboardButton(kb.phone_keyboard[0],
                                        request_contact=True,)],
                        [KeyboardButton(kb.phone_keyboard[1])]]

    reply_markup = ReplyKeyboardMarkup(keyboard=contact_keyboard,
                                       resize_keyboard=True,
                                       one_time_keyboard=True)
    update.message.reply_text(
                    text=resources.phone_message,
                    reply_markup=reply_markup)
    context.user_data['HISTORY'] += save_message_to_history(
        resources.phone_message, 'bot')
    return PHONE


def phone_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    inline_keyboard = [
        [InlineKeyboardButton(text=kb.category_keyboard[0][0],
                              callback_data=kb.category_keyboard[0][1]),
         InlineKeyboardButton(text=kb.category_keyboard[1][0],
                              callback_data=kb.category_keyboard[1][1])],
        [InlineKeyboardButton(text=kb.category_keyboard[2][0],
                              callback_data=kb.category_keyboard[2][1]),
         InlineKeyboardButton(text=kb.category_keyboard[3][0],
                              callback_data=kb.category_keyboard[3][1])],
        [InlineKeyboardButton(text=kb.category_keyboard[4][0],
                              callback_data=kb.category_keyboard[4][1]),
         InlineKeyboardButton(text=kb.category_keyboard[5][0],
                              callback_data=kb.category_keyboard[5][1])],
        [InlineKeyboardButton(text=kb.category_keyboard[6][0],
                              callback_data=kb.category_keyboard[6][1]),
         InlineKeyboardButton(text=kb.category_keyboard[7][0],
                              callback_data=kb.category_keyboard[7][1])],
        [InlineKeyboardButton(text=kb.category_keyboard[8][0],
                              callback_data=kb.category_keyboard[8][1]),
         InlineKeyboardButton(text=kb.category_keyboard[9][0],
                              callback_data=kb.category_keyboard[9][1])],
        [InlineKeyboardButton(text=kb.category_keyboard[10][0],
                              callback_data=kb.category_keyboard[10][1]),
         InlineKeyboardButton(text=kb.category_keyboard[11][0],
                              callback_data=kb.category_keyboard[11][1])],
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    try:
        context.user_data['PHONE'] = update.message.contact.phone_number
        message = update.message.contact.phone_number
        context.user_data['HISTORY'] += save_message_to_history(
            message, 'user')
        update.message.reply_text(
            text=resources.category_message,
            reply_markup=reply_markup
        )
        context.user_data['HISTORY'] += save_message_to_history(
            resources.category_message, 'bot')
        return CATEGORY
    except AttributeError:
        if update.message.text[:3] == '380' and len(update.message.text) == 12:
            context.user_data['PHONE'] = update.message.text
            message = update.message.text
            context.user_data['HISTORY'] += save_message_to_history(
                message, 'user')
            update.message.reply_text(
                text=resources.category_message,
                reply_markup=reply_markup
            )
            context.user_data['HISTORY'] += save_message_to_history(
                resources.category_message, 'bot')
            return CATEGORY
        else:
            update.message.reply_text(
                text=resources.phone_error
            )
            context.user_data['HISTORY'] += save_message_to_history(
                resources.phone_error, 'bot')
            return PHONE


def category_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    pick = ''
    for item in kb.category_keyboard:
        if item[1] == update.callback_query.data:
            pick = item[0]
    context.user_data['CATEGORY'] = pick
    context.user_data['HISTORY'] += save_message_to_history(pick, 'user')
    update.callback_query.edit_message_text(
        text=f'{update.callback_query.message.text}\nВаш вибір: {pick}'
    )
    inline_keyboard = [
        [
            InlineKeyboardButton(text=kb.brand_keyboard[0],
                                 callback_data='brand-Candy')
        ], [
            InlineKeyboardButton(text=kb.brand_keyboard[1],
                                 callback_data='brand-Hoover'),
        ], [
            InlineKeyboardButton(text=kb.brand_keyboard[2],
                                 callback_data='brand-Rosieres'),
        ],
    ]
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    context.bot.send_message(chat_id=update.callback_query.message.chat.id,
                             text=resources.brand_message,
                             reply_markup=inline_buttons
                             )
    context.user_data['HISTORY'] += save_message_to_history(
        resources.brand_message, 'bot')
    return ConversationHandler.END


def brand_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    context.user_data['BRAND'] = update.callback_query.data.split('-')[1]
    choice = choice_definer(update)
    context.user_data['HISTORY'] += save_message_to_history(choice, 'user')
    update.callback_query.edit_message_text(
        text=f'{update.callback_query.message.text}\nВаш вибір: {choice}'
    )
    contact_keyboard = KeyboardButton("Зв'язок з оператором")
    reply_markup = ReplyKeyboardMarkup(keyboard=[[contact_keyboard]],
                                       resize_keyboard=True)
    context.bot.send_message(chat_id=update.callback_query.message.chat.id,
                             text=resources.serial_number_message,
                             reply_markup=reply_markup)
    context.user_data['HISTORY'] += save_message_to_history(
        resources.serial_number_message, 'bot')
    return SERIAL_NUMBER


def serial_number_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    message = update.message.text.replace(' ', '')
    if len(message) == 16 and message.isdecimal() and message[0] == '3':
        context.user_data['SERIAL_NUMBER'] = update.message.text
        context.user_data['HISTORY'] += save_message_to_history(
            message, 'user')
        contact_keyboard = [[KeyboardButton("Зв'язок з оператором")]]
        reply_markup = ReplyKeyboardMarkup(keyboard=contact_keyboard,
                                           resize_keyboard=True)
        update.message.reply_text(
            text=resources.photo_serial_message,
            reply_markup=reply_markup)
        context.user_data['HISTORY'] += save_message_to_history(
            resources.photo_serial_message, 'bot')
        context.user_data['STAGE'] = 'photo_serial'
        return PHOTOS
    else:
        context.user_data['HISTORY'] += save_message_to_history(
            message, 'user')
        contact_keyboard = [[KeyboardButton("Зв'язок з оператором")]]
        reply_markup = ReplyKeyboardMarkup(keyboard=contact_keyboard,
                                           resize_keyboard=True)
        update.message.reply_text(
            text=resources.serial_number_error,
            reply_markup=reply_markup)
        context.user_data['HISTORY'] += save_message_to_history(
            resources.serial_number_error, 'bot')
        return SERIAL_NUMBER


def photos_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    # context.user_data['PHOTOS'] = update.message.photo
    try:
        request = update.message
        user_id = update.message.from_user.id
    except AttributeError:
        request = update
        user_id = update.callback_query.message.chat.id
    payload = json.loads(jsonpickle.encode(request))
    if not os.path.exists(f'media/{user_id}'):
        os.makedirs(f'media/{user_id}')
    file_downloaded = False
    if payload and payload['photo']:
        tele_file = context.bot.get_file(update.message.photo[-1].file_id)
        file_path = tele_file['file_path']
        path = f'media/{user_id}/photo{update.message.message_id}.jpg'
        tele_file.download(path)
        link = upload_image(path)
        file_links = open(f'media/{user_id}/links.txt', 'a')
        file_links.write(f'{link},')
        file_links.close()
        file_downloaded = True
    if payload and payload['document']:
        tele_file = context.bot.get_file(update.message.document.file_id)
        file_path = str(tele_file['file_path'])
        path = f'media/{user_id}/photo{update.message.message_id}.jpg'
        tele_file.download(path)
        link = upload_image(path)
        file_links = open(f'media/{user_id}/links.txt', 'a')
        file_links.write(f'{link},')
        file_links.close()
        file_downloaded = True
    if file_downloaded:
        if context.user_data['STAGE'] == 'photo_serial':
            contact_keyboard = [[KeyboardButton("Зв'язок з оператором")]]
            reply_markup = ReplyKeyboardMarkup(keyboard=contact_keyboard,
                                               resize_keyboard=True)
            update.message.reply_text(text=resources.photo_guarantee_message,
                                      reply_markup=reply_markup)
            context.user_data['HISTORY'] += save_message_to_history(
                resources.photo_guarantee_message, 'bot')
            context.user_data['STAGE'] = 'photo_guarantee'
            return PHOTOS
        elif context.user_data['STAGE'] == 'photo_guarantee':
            contact_keyboard = [[KeyboardButton("Зв'язок з оператором")]]
            reply_markup = ReplyKeyboardMarkup(keyboard=contact_keyboard,
                                               resize_keyboard=True)
            update.message.reply_text(text=resources.photo_check_message,
                                      reply_markup=reply_markup)
            context.user_data['HISTORY'] += save_message_to_history(
                resources.photo_check_message, 'bot')
            context.user_data['STAGE'] = 'photo_check'
            return PHOTOS
        else:
            contact_keyboard = [[KeyboardButton("Зв'язок з оператором")]]
            reply_markup = ReplyKeyboardMarkup(keyboard=contact_keyboard,
                                               resize_keyboard=True)
            update.message.reply_text(text=resources.reason_message,
                                      reply_markup=reply_markup)
            context.user_data['HISTORY'] += save_message_to_history(
                resources.reason_message, 'bot')
            return REASON
    else:
        update.message.reply_text(text=resources.photo_error)
        context.user_data['HISTORY'] += save_message_to_history(
            resources.photo_error, 'bot')
        return PHOTOS


def reason_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    list_of_dates = schedule_matcher()[:20]
    beautified_dates = [(f'date%{x[0]}', datetime.strptime(
        x[0], '%Y-%m-%d').strftime('%d.%m')) for x in list_of_dates]
    sorted_dates = list(divide_chunks(beautified_dates, 4))
    inline_keyboard = [[InlineKeyboardButton(text=x[1],
                                             callback_data=f'{x[0]}') for x in item] for item in sorted_dates]
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    try:
        context.user_data['REASON'] = update.message.text
        message = update.message.text
        context.user_data['HISTORY'] += save_message_to_history(
            message, 'user')
        update.message.reply_text(
            text=resources.date_message,
            reply_markup=inline_buttons,
        )
    except:
        update.callback_query.edit_message_text(
            text=resources.date_message,
            reply_markup=inline_buttons,
        )
    context.user_data['HISTORY'] += save_message_to_history(
        resources.date_message, 'bot')
    return ConversationHandler.END


def date_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    print(update.callback_query.data)
    date = update.callback_query.data.split('%')[1]
    context.user_data['DATE'] = date
    context.user_data['HISTORY'] += save_message_to_history(date, 'user')
    choosed_item = []
    list_of_dates = schedule_matcher()[:20]
    for dates in list_of_dates:
        if dates[0] == date:
            choosed_item = dates
    sorted_dates = list(divide_chunks(choosed_item[1], 2))
    inline_keyboard = [[InlineKeyboardButton(text=x[0],
                                             callback_data=f'time%{x[0]}') for x in item] for item in sorted_dates]
    inline_keyboard.append(
            [
             InlineKeyboardButton(
                 text=kb.back_to_date,
                 callback_data='reason'),
            ])
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    update.callback_query.edit_message_text(
        text=date
    )
    context.bot.send_message(chat_id=update.callback_query.message.chat.id,
                             text=resources.time_message,
                             reply_markup=inline_buttons)
    context.user_data['HISTORY'] += save_message_to_history(
        resources.time_message, 'bot')
    return ConversationHandler.END


def time_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    time = update.callback_query.data.split('%')[1]
    context.user_data['TIME'] = time
    context.user_data['HISTORY'] += save_message_to_history(time, 'user')
    inline_keyboard = [
        [
            InlineKeyboardButton(text='Меню',
                                 callback_data='start'),
        ],
    ]
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    update.callback_query.edit_message_text(
        text=update.callback_query.data.split('%')[1]
    )
    data_list = [str(context.user_data[key])
                 for key in context.user_data.keys()]
    text = ''
    if 'NAME' in context.user_data.keys():
        text += f"Прiзвище та Ім'я: {context.user_data['NAME']}\n"
    if 'PHONE' in context.user_data.keys():
        text += f'Номер: {context.user_data["PHONE"]}\n'
    if 'CATEGORY' in context.user_data.keys():
        text += f'Категорiя: {context.user_data["CATEGORY"]}\n'
    if 'BRAND' in context.user_data.keys():
        text += f'Бренд: {context.user_data["BRAND"]}\n'
    if 'SERIAL_NUMBER' in context.user_data.keys():
        text += f'Серiйний номер: {context.user_data["SERIAL_NUMBER"]}\n'
    if 'REASON' in context.user_data.keys():
        text += f'Причина: {context.user_data["REASON"]}\n'
    if 'DATE' in context.user_data.keys():
        text += f'Дата: {context.user_data["DATE"]}\n'
    if 'TIME' in context.user_data.keys():
        text += f'Час: {context.user_data["TIME"]}\n'
    datetime_string = f'{context.user_data["DATE"]} {context.user_data["TIME"]}'
    beautified_date = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M')
    deal_id = add_to_crm(category=context.user_data["CATEGORY"],
                         reason=context.user_data["REASON"],
                         phone=context.user_data["PHONE"],
                         brand=context.user_data["BRAND"],
                         serial=context.user_data["SERIAL_NUMBER"],
                         name=context.user_data['NAME'],
                         date=context.user_data["DATE"],
                         time=beautified_date)
    timestamp_start = datetime.timestamp(beautified_date)
    timestamp_end = datetime.timestamp(beautified_date + timedelta(minutes=30))
    add_event(timestamp_start, timestamp_end,
              f'Вiдео дзiнок з {context.user_data["NAME"]}', deal_id)
    reply_markup = ReplyKeyboardRemove()
    context.bot.send_message(chat_id=update.callback_query.message.chat.id,
                             text=text,
                             reply_markup=reply_markup)
    context.user_data['HISTORY'] += save_message_to_history(text, 'bot')
    context.bot.send_message(chat_id=update.callback_query.message.chat.id,
                             text=resources.final_message_telegram,
                             reply_markup=inline_buttons,
                             disable_web_page_preview=True,
                             parse_mode='html')
    context.user_data['HISTORY'] += save_message_to_history(
        resources.final_message_telegram, 'bot')
    context.user_data['HISTORY'] = ''
    all_filenames = [i for i in glob.glob(
        f'media/{update.callback_query.message.chat.id}/*.jpg')]
    for i in all_filenames:
        f = open(i, 'rb')
        # context.bot.send_document(chat_id=update.callback_query.message.chat.id, document=f)
        os.remove(i)
    with open(f'media/{update.callback_query.message.chat.id}/links.txt', 'r') as links:
        text = links.read()
        for link in text.split(','):
            if link != '':
                add_comment(deal_id, link)
    open(f'media/{update.callback_query.message.chat.id}/links.txt', 'w').close()
    return ConversationHandler.END
