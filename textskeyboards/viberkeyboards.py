import os
from pathlib import Path
from dotenv import load_dotenv
from vibertelebot.utils.tools import keyboard_consctructor

LOGO = 'https://i.ibb.co/82bQQtt/download.png'
MAIN_COLOR = os.getenv("COLOR")


start = keyboard_consctructor([
            ('Старт', 'start', '')
            ])

free_consult = keyboard_consctructor([
            ('Під’єднати оператора 👨‍💻', 'free_consult', ''),
            ('Популярні питання ❓', 'questions', '')
            ])

clarificational_consult = keyboard_consctructor([
            ('Так, маю ще питання', 'consult', ''),
            ('Ні, дякую!', 'issue_solved', ''),
            ])

paid_consult = keyboard_consctructor([
            ('Під’єднати оператора 👨‍💻', 'paid_consult', ''),
            ('Популярні питання ❓', 'questions', '')
            ])

buy_consult = keyboard_consctructor([
            ('Придбати пакет консультацій', 'buy_consult', ''),
            ('Популярні питання ❓', 'questions', '')
            ])


solved_free_consult = [
            ('Залишити відгук 🚀', '', ''),
            ('Під’єднати оператора 👨‍💻', 'free_consult', ''),
            ('Популярні питання ❓', 'questions', '')
            ]

solved_paid_consult = [
            ('Залишити відгук 🚀', '', ''),
            ('Під’єднати оператора 👨‍💻', 'paid_consult', ''),
            ('Популярні питання ❓', 'questions', '')
            ]

solved_buy_consult = [
            ('Залишити відгук 🚀', '', ''),
            ('Придбати пакет консультацій', 'buy_consult', ''),
            ('Популярні питання ❓', 'questions', '')
            ]


end_chat_keyboard = keyboard_consctructor([
            ('Завершити чат', 'end_chat', '')
            ])

payment_proceed = [
            ('Оплата', '', ''),
            ('Посилання застаріло?', 'link', ''),
            ('Проблема з оплатою?', 'consult', ''),
            ]

payment_check = keyboard_consctructor([
            ('Проверить статус оплаты', 'payment_completed', '')
            ])

buy_amount = keyboard_consctructor([
            ('1', 'purchase_1', ''),
            ('3', 'purchase_3', ''),
            ('5', 'purchase_5', '')
            ])


def payment_keyboard_generator(items: list, link: str) -> dict:
    """Pasting infromation from list of items to keyboard menu template."""
    keyboard = {
        "DefaultHeight": False,
        "BgColor": '#f7f9fc',
        "Type": "keyboard",
        "Buttons": [{"Columns": 6,
                     "Rows": 1,
                     "BgColor": MAIN_COLOR,
                     "BgLoop": True,
                     "ActionType": "open-url",
                     "ActionBody": link,
                     "ReplyType": "message",
                     "OpenURLType": "internal",
                     "Text": items[0][0]},
                    {"Columns": 3,
                     "Rows": 1,
                     "BgColor": MAIN_COLOR,
                     "BgLoop": True,
                     "ActionType": "reply",
                     "ActionBody": items[1][1],
                     "ReplyType": "message",
                     "Text": items[1][0]},
                    {"Columns": 3,
                     "Rows": 1,
                     "BgColor": MAIN_COLOR,
                     "BgLoop": True,
                     "ActionType": "reply",
                     "ActionBody": items[2][1],
                     "ReplyType": "message",
                     "Text": items[2][0]}]
    }
    return keyboard


phone_keyboard = {
        "DefaultHeight": False,
        "BgColor": '#f7f9fc',
        "Type": "keyboard",
        "Buttons": [
            {
                "Columns": 6,
                "Rows": 1,
                "BgColor": MAIN_COLOR,
                "BgLoop": True,
                "ActionType": "share-phone",
                "ActionBody": "phone_reply",
                "ReplyType": "message",
                "Text": "Поділитися номером телефону",
            },
        ]
    }


def solved_keyboard_generator(items, link):
    keyboard = {
        "DefaultHeight": False,
        "BgColor": '#f7f9fc',
        "Type": "keyboard",
        "Buttons": [{"Columns": 6,
                     "Rows": 1,
                     "BgColor": MAIN_COLOR,
                     "BgLoop": True,
                     "ActionType": "open-url",
                     "ActionBody": link,
                     "ReplyType": "message",
                     "OpenURLType": "internal",
                     "Text": items[0][0]},
                    {"Columns": 6,
                     "Rows": 1,
                     "BgColor": MAIN_COLOR,
                     "BgLoop": True,
                     "ActionType": "reply",
                     "ActionBody": items[1][1],
                     "ReplyType": "message",
                     "Text": items[1][0]},
                    {"Columns": 6,
                     "Rows": 1,
                     "BgColor": MAIN_COLOR,
                     "BgLoop": True,
                     "ActionType": "reply",
                     "ActionBody": items[2][1],
                     "ReplyType": "message",
                     "Text": items[2][0]}]
    }
    return keyboard
