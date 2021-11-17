import os
from pathlib import Path
from dotenv import load_dotenv
from vibertelebot.utils.tools import keyboard_consctructor

LOGO = 'https://i.ibb.co/82bQQtt/download.png'
MAIN_COLOR = os.getenv("COLOR")

free_consult = keyboard_consctructor([
            ('Воспользоваться бесплатной консультацией', 'free_consult', '')
            ])

clarificational_consult = keyboard_consctructor([
            ('Продолжить общение', 'consult', ''),
            ('Завершить диалог', 'issue_solved', ''),
            ])

paid_consult = keyboard_consctructor([
            ('Проконсультироваться', 'paid_consult', '')
            ])

buy_consult = keyboard_consctructor([
            ('Приобрести пакет консультаций', 'buy_consult', '')
            ])

end_chat_keyboard = keyboard_consctructor([
            ('Завершити чат', 'end_chat', '')
            ])

payment_proceed = [
            ('Оплата', '', ''),
            ('Ссылка устарела?', 'link', ''),
            ('Проблема с оплатой?', 'consult', ''),
            ]

payment_check = keyboard_consctructor([
            ('Проверить статус оплаты', 'payment_completed', '')
            ])

buy_amount = keyboard_consctructor([
            ('1', 'purchase_1', ''),
            ('2', 'purchase_2', ''),
            ('3', 'purchase_3', ''),
            ('4', 'purchase_4', ''),
            ('5', 'purchase_5', ''),
            ('6', 'purchase_6', ''),
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
