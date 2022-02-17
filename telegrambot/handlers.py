import os
import csv
import time
import requests
import locale
import json
import jsonpickle
import glob
from loguru import logger
from pathlib import Path
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, Update,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton)
from telegram.ext import CallbackContext, ConversationHandler
from textskeyboards import texts as resources
from jivochat import sender as jivochat
from jivochat.utils import resources as jivosource
from textskeyboards import telegramkeyboards as kb
from db_func.database import get_phone_telegram, export_all, add_user_telegram, check_user_telegram, minus_free_consult_telegram, minus_paid_consult_telegram, plus_paid_consult_telegram, change_stage_to_chat_telegram, reset_counter_telegram, paid_consults_telegram, add_task_for_notification_telegram, delete_task_for_notification
from payment.generator import get_payment_link, get_liqpay_link


dotenv_path = os.path.join(Path(__file__).parent.parent, 'config/.env')
load_dotenv(dotenv_path)
# pp = pprint.PrettyPrinter(indent=4)
TOKEN = os.getenv("TOKEN")

locale.setlocale(locale.LC_TIME, 'uk_UA.UTF-8')
CHAT, MENU = range(2)


logger.add(
    "logs/info.log",
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="100 MB",
    compression="zip",
)


@logger.catch
def save_message_to_history(message, type):
    text = ''
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    if type == 'bot':
        text += 'Bot '
    else:
        text += 'User '
    text += f'{now}: {message}\n'
    return text


@logger.catch
def choice_definer(update):
    keyboard = update.callback_query.message.reply_markup.inline_keyboard
    choice = ''
    for item in keyboard:
        if item[0].callback_data == update.callback_query.data:
            choice = item[0].text
    return choice


@logger.catch
def greetings_handler(update: Update, context: CallbackContext):
    state = phone_handler(update, context)
    return state


def phone_handler(update: Update, context: CallbackContext):
    contact_keyboard = [[KeyboardButton('Поділитися номером телефону',
                                        request_contact=True,)]]

    reply_markup = ReplyKeyboardMarkup(keyboard=contact_keyboard,
                                       resize_keyboard=True,
                                       one_time_keyboard=True)
    context.bot.send_message(chat_id=update.message.from_user.id,
                             text=resources.phone_message,
                             reply_markup=reply_markup)
    return MENU


@logger.catch
def menu_handler(update: Update, context: CallbackContext):
    context.user_data['HISTORY'] = ''
    try:
        chat_id = update.callback_query.message.chat.id
    except AttributeError:
        chat_id = update.message.from_user.id
    try:
        phone = update.message.contact.phone_number
    except:
        phone = None
    if phone:
        add_user_telegram(str(chat_id), phone)
    user_data = check_user_telegram(chat_id)
    logger.info(user_data)
    if user_data:
        if user_data[2] > 0:
            reply_keyboard = kb.free_consult
            reply_text = resources.free_consult_message
            add_task_for_notification_telegram(chat_id)
        elif user_data[1] > 0:
            counter = paid_consults_telegram(chat_id)
            reply_keyboard = kb.paid_consult
            reply_text = resources.greeting_message.replace(
                '[counter]', str(counter))
        else:
            reply_keyboard = kb.buy_consult
            reply_text = resources.greeting_message.replace(
                '[counter]', '0')
    else:
        state = phone_handler(update, context)
        return state
    reply_markup = ReplyKeyboardRemove()
    context.bot.send_message(
                chat_id=chat_id,
                text=phone,
                reply_markup=reply_markup)
    time.sleep(1)
    try:
        request = update.callback_query.message
        choice = choice_definer(update)
        context.user_data['HISTORY'] += save_message_to_history(choice, 'user')
        update.callback_query.edit_message_text(
            text=update.callback_query.message.text
        )
        context.bot.send_message(chat_id=update.callback_query.message.chat.id,
                                 text=reply_text,
                                 reply_markup=reply_keyboard)
        logger.info('Callback Message')
    except AttributeError:
        request = update.message
        context.bot.send_message(chat_id=update.message.from_user.id,
                                 text=reply_text,
                                 reply_markup=reply_keyboard)
        logger.info('Reply Message')
    context.user_data['HISTORY'] += save_message_to_history(
        resources.greeting_message, 'bot')
    return ConversationHandler.END


@logger.catch
def operator_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
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
    user_phone = get_phone_telegram(chat_id)
    jivochat.send_message(chat_id,
                          str(user_phone),
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
                        chat_id, 'TelegramUser', link, name, 'telegram')
                else:
                    jivochat.send_document(
                        chat_id, 'TelegramUser', link, name, 'telegram')
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


@logger.catch
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
            chat_id, 'TelegramUser', file, name, 'telegram')
        return CHAT
    elif payload and payload['document']:
        file = context.bot.get_file(
            update.message.document.file_id)['file_path']
        name = file.split('/')[-1]
        jivochat.send_document(
            chat_id, 'TelegramUser', file, name, 'telegram')
        return CHAT
    elif payload and payload['video']:
        file = context.bot.get_file(
            update.message.video.file_id)['file_path']
        name = file.split('/')[-1]
        jivochat.send_video(
            chat_id, 'TelegramUser', file, name, 'telegram')
        return CHAT
    elif reply == 'Завершити чат':
        reply_markup = ReplyKeyboardRemove()
        user_phone = get_phone_telegram(update.message.from_user.id)
        jivochat.send_message(update.message.from_user.id,
                              str(user_phone),
                              jivosource.user_ended_chat,
                              'telegram')
        context.bot.send_message(chat_id=update.message.from_user.id,
                                 text=resources.chat_ending,
                                 reply_markup=reply_markup)
        user_data = check_user_telegram(update.message.from_user.id)
        logger.info(user_data)
        link = os.getenv('FEEDBACK_LINK')
        if user_data[2] > 0:
            reply_text = resources.user_finished.replace(
                '[counter]', '0')
            reply_keyboard = kb.solved_keyboard_generator(
                kb.solved_free_consult, link)
        elif user_data[1] > 0:
            counter = paid_consults_telegram(update.message.from_user.id)
            reply_text = resources.user_finished.replace(
                '[counter]', str(counter))
            reply_keyboard = kb.solved_keyboard_generator(
                kb.solved_paid_consult, link)
        else:
            reply_text = resources.user_finished.replace(
                '[counter]', '0')
            reply_keyboard = kb.solved_keyboard_generator(
                kb.solved_buy_consult, link)
        context.bot.send_message(chat_id=update.message.from_user.id,
                                 text=reply_text,
                                 reply_markup=reply_keyboard)
        return ConversationHandler.END
    else:
        user_phone = get_phone_telegram(update.message.from_user.id)
        jivochat.send_message(update.message.from_user.id,
                              str(user_phone),
                              reply,
                              'telegram')
        return CHAT


@logger.catch
def echo_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    message = update.message.text
    context.user_data['HISTORY'] += save_message_to_history(message, 'user')
    if message == 'Завершити чат':
        reply_markup = ReplyKeyboardRemove()
        user_phone = get_phone_telegram(update.message.from_user.id)
        jivochat.send_message(update.message.from_user.id,
                              str(user_phone),
                              jivosource.user_ended_chat,
                              'telegram')
        # context.bot.send_message(chat_id=update.message.from_user.id,
        #                          text=resources.chat_ending,
        #                          reply_markup=reply_markup)
        # time.sleep(1)
        user_data = check_user_telegram(update.message.from_user.id)
        logger.info(user_data)
        link = os.getenv('FEEDBACK_LINK')
        if user_data[2] > 0:
            reply_text = resources.user_finished.replace(
                '[counter]', '0')
            reply_keyboard = kb.solved_keyboard_generator(
                kb.solved_free_consult, link)
        elif user_data[1] > 0:
            counter = paid_consults_telegram(update.message.from_user.id)
            reply_text = resources.user_finished.replace(
                '[counter]', str(counter))
            reply_keyboard = kb.solved_keyboard_generator(
                kb.solo_paid_consult, link)
        else:
            reply_text = resources.user_finished.replace(
                '[counter]', '0')
            reply_keyboard = kb.solved_keyboard_generator(
                kb.solo_buy_consult, link)
        context.bot.send_message(chat_id=update.message.from_user.id,
                                 text=reply_text,
                                 reply_markup=reply_keyboard)
    else:
        user_data = check_user_telegram(update.message.from_user.id)
        logger.info(user_data)
        link = os.getenv('FEEDBACK_LINK')
        if user_data[2] > 0:
            reply_text = resources.echo_message
            reply_keyboard = kb.solo_free_consult
        elif user_data[1] > 0:
            counter = paid_consults_telegram(update.message.from_user.id)
            reply_text = resources.echo_message
            reply_keyboard = kb.solo_paid_consult
        else:
            reply_text = resources.echo_message
            reply_keyboard = kb.solo_buy_consult
        context.bot.send_message(chat_id=update.message.from_user.id,
                                 text=reply_text,
                                 reply_markup=reply_keyboard)
        context.user_data['HISTORY'] += save_message_to_history(
            resources.echo_message, 'bot')
    return ConversationHandler.END


@logger.catch
def issue_solved_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    context.user_data['ID'] = update.callback_query.message.chat.id
    change_stage_to_chat_telegram(context.user_data['ID'])
    choice = choice_definer(update)
    context.user_data['HISTORY'] += save_message_to_history(choice, 'user')
    update.callback_query.edit_message_text(
        text=f'{update.callback_query.message.text}\nВаш вибір: {choice}')
    context.bot.send_message(chat_id=context.user_data['ID'],
                             text=resources.chat_ending)
    user_data = check_user_telegram(context.user_data['ID'])
    link = os.getenv('FEEDBACK_LINK')
    logger.info(user_data)
    if user_data[2] > 0:
        reply_keyboard = kb.solved_keyboard_generator(
            kb.solved_free_consult, link)
        reply_text = resources.user_finished.replace(
            '[counter]', '0')
    elif user_data[1] > 0:
        counter = paid_consults_telegram(context.user_data['ID'])
        reply_keyboard = kb.solved_keyboard_generator(
            kb.solved_paid_consult, link)
        reply_text = resources.user_finished.replace(
            '[counter]', str(counter))
    else:
        reply_keyboard = kb.solved_keyboard_generator(
            kb.solved_buy_consult, link)
        reply_text = resources.user_finished.replace(
            '[counter]', '0')
    time.sleep(1)
    context.bot.send_message(chat_id=context.user_data['ID'],
                             text=reply_text,
                             reply_markup=reply_keyboard)
    context.user_data['HISTORY'] += save_message_to_history(reply_text, 'bot')
    return ConversationHandler.END


@logger.catch
def free_consult_handler(update: Update, context: CallbackContext):
    delete_task_for_notification(update.callback_query.message.chat.id)
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    choice = choice_definer(update)
    context.user_data['HISTORY'] += save_message_to_history(choice, 'user')
    minus_free_consult_telegram(update.callback_query.message.chat.id)
    user_phone = get_phone_telegram(update.callback_query.message.chat.id)
    jivochat.send_message(update.callback_query.message.chat.id,
                          str(user_phone),
                          'Бесплатная консультация',
                          'telegram')
    operator_handler(update, context)
    return CHAT


@logger.catch
def paid_consult_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    choice = choice_definer(update)
    context.user_data['HISTORY'] += save_message_to_history(choice, 'user')
    minus_paid_consult_telegram(update.callback_query.message.chat.id)
    user_phone = get_phone_telegram(update.callback_query.message.chat.id)
    jivochat.send_message(update.callback_query.message.chat.id,
                          str(user_phone),
                          'Платная консультация',
                          'telegram')
    operator_handler(update, context)
    return CHAT


@logger.catch
def consult_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    choice = choice_definer(update)
    context.user_data['HISTORY'] += save_message_to_history(choice, 'user')
    reset_counter_telegram(update.callback_query.message.chat.id)
    user_phone = get_phone_telegram(update.callback_query.message.chat.id)
    jivochat.send_message(update.callback_query.message.chat.id,
                          str(user_phone),
                          'Уточнение',
                          'telegram')
    operator_handler(update, context)
    return CHAT


@logger.catch
def buy_consult_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    context.user_data['ID'] = update.callback_query.message.chat.id
    change_stage_to_chat_telegram(context.user_data['ID'])
    choice = choice_definer(update)
    context.user_data['HISTORY'] += save_message_to_history(choice, 'user')
    update.callback_query.edit_message_text(
        text=f'{update.callback_query.message.text}\nВаш вибір: {choice}')
    user_data = check_user_telegram(update.callback_query.message.chat.id)
    amount = user_data[1]
    reply_keyboard = kb.buy_amount
    reply_text = resources.select_amount.replace(
        '[counter]', str(amount))
    context.bot.send_message(chat_id=context.user_data['ID'],
                             text=reply_text,
                             reply_markup=reply_keyboard)
    context.user_data['HISTORY'] += save_message_to_history(reply_text, 'bot')
    return ConversationHandler.END


@logger.catch
def purchase_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    context.user_data['ID'] = update.callback_query.message.chat.id
    change_stage_to_chat_telegram(context.user_data['ID'])
    choice = choice_definer(update)
    context.user_data['HISTORY'] += save_message_to_history(choice, 'user')
    update.callback_query.edit_message_text(
        text=f'{update.callback_query.message.text}\nВаш вибір: {choice}')
    amount = int(choice)
    context.user_data['AMOUNT'] = amount
    phone = check_user_telegram(str(context.user_data['ID']))[5]
    link = get_liqpay_link(amount, str(
        context.user_data['ID']), 'telegram', phone)
    reply_keyboard = kb.payment_keyboard_generator(
        kb.payment_proceed, link)
    reply_text = resources.please_pay
    message = context.bot.send_message(chat_id=context.user_data['ID'],
                                       text=reply_text,
                                       reply_markup=reply_keyboard)
    print(message.message_id)
    if not os.path.exists(f'media/{context.user_data["ID"]}'):
        os.makedirs(f'media/{context.user_data["ID"]}')
    with open(f'media/{context.user_data["ID"]}/paymessage.txt', 'w') as f:
        f.write(str(message.message_id))
    context.user_data['HISTORY'] += save_message_to_history(reply_text, 'bot')
    return ConversationHandler.END


@logger.catch
def link_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    context.user_data['ID'] = update.callback_query.message.chat.id
    change_stage_to_chat_telegram(context.user_data['ID'])
    choice = choice_definer(update)
    context.user_data['HISTORY'] += save_message_to_history(choice, 'user')
    update.callback_query.edit_message_text(
        text=f'{update.callback_query.message.text}\nВаш вибір: {choice}')
    if 'AMOUNT' in context.user_data:
        amount = context.user_data['AMOUNT']
    else:
        amount = 1
    phone = check_user_telegram(str(context.user_data['ID']))[5]
    link = get_liqpay_link(amount, str(
        context.user_data['ID']), 'telegram', phone)
    context.user_data['LINK'] = link
    reply_keyboard = kb.payment_keyboard_generator(
        kb.payment_proceed, link)
    reply_text = resources.new_link
    message = context.bot.send_message(chat_id=context.user_data['ID'],
                                       text=reply_text,
                                       reply_markup=reply_keyboard)
    print(message.message_id)
    if not os.path.exists(f'media/{context.user_data["ID"]}'):
        os.makedirs(f'media/{context.user_data["ID"]}')
    with open(f'media/{context.user_data["ID"]}/paymessage.txt', 'w') as f:
        f.write(str(message.message_id))
    context.user_data['HISTORY'] += save_message_to_history(reply_text, 'bot')
    return ConversationHandler.END


@logger.catch
def payment_completed_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    context.user_data['ID'] = update.callback_query.message.chat.id
    change_stage_to_chat_telegram(context.user_data['ID'])
    choice = choice_definer(update)
    context.user_data['HISTORY'] += save_message_to_history(choice, 'user')
    update.callback_query.edit_message_text(
        text=f'{update.callback_query.message.text}\nВаш вибір: {choice}')
    reply_keyboard = kb.payment_check
    reply_text = resources.please_wait
    context.bot.send_message(chat_id=context.user_data['ID'],
                             text=reply_text,
                             reply_markup=reply_keyboard)
    context.user_data['HISTORY'] += save_message_to_history(reply_text, 'bot')
    return ConversationHandler.END


@logger.catch
def questions_handler(update: Update, context: CallbackContext):
    if 'HISTORY' not in context.user_data:
        context.user_data['HISTORY'] = ''
    choice = choice_definer(update)
    context.user_data['ID'] = update.callback_query.message.chat.id
    chat_id = update.callback_query.message.chat.id
    context.user_data['HISTORY'] += save_message_to_history(choice, 'user')
    reply_text = resources.faq
    user_data = check_user_telegram(chat_id)
    logger.info(user_data)
    if user_data[2] > 0:
        reply_keyboard = kb.solo_free_consult
    elif user_data[1] > 0:
        reply_keyboard = kb.solo_paid_consult
    else:
        reply_keyboard = kb.solo_buy_consult
    context.bot.send_message(chat_id=chat_id,
                             text=reply_text,
                             reply_markup=reply_keyboard)
    context.user_data['HISTORY'] += save_message_to_history(reply_text, 'bot')
    return ConversationHandler.END


def file_handler(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Файл готовиться и будет отправлен в следующем сообщении.')
    data = export_all()
    try:
        os.remove('data.csv')
    except FileNotFoundError:
        logger.info('File not found')
    with open('data.csv', 'w+', newline='') as file:
        wr = csv.writer(file, quoting=csv.QUOTE_ALL)
        wr.writerow(['chat_id_telegram', 'chat_id_viber',
                     'circle_paid', 'circle_free', 'phone'])
        wr.writerows(data)
    with open('data.csv', 'rb') as file:
        context.bot.send_document(chat_id=update.effective_chat.id,
                                  document=file,
                                  filename='data.csv')
        time.sleep(1)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Для возвращения нажмите /restart')

    return ConversationHandler.END
