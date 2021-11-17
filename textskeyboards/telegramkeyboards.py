from telegrambot.utils.tools import tg_keyboard_constructor
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton


free_consult = tg_keyboard_constructor([
            ('Воспользоваться бесплатной консультацией', 'free_consult')
            ])

clarificational_consult = tg_keyboard_constructor([
            ('Продолжить общение', 'consult'),
            ('Завершить диалог', 'issue_solved'),
            ])

paid_consult = tg_keyboard_constructor([
            ('Проконсультироваться', 'paid_consult')
            ])

buy_consult = tg_keyboard_constructor([
            ('Приобрести пакет консультаций', 'buy_consult')
            ])

payment_proceed = [
            ('Оплата', ''),
            ('Ссылка устарела?', 'link'),
            ('Проблема с оплатой?', 'consult'),
            ]

payment_check = tg_keyboard_constructor([
            ('Проверить статус оплаты', 'payment_completed')
            ])

buy_amount = tg_keyboard_constructor([
            ('1', 'purchase_1'),
            ('2', 'purchase_2'),
            ('3', 'purchase_3'),
            ('4', 'purchase_4'),
            ('5', 'purchase_5'),
            ('6', 'purchase_6'),
            ])


def payment_keyboard_generator(items: list, link: str):
    inline_keyboard = [
        [InlineKeyboardButton(text=items[0][0],
                              url=link)],
        [InlineKeyboardButton(text=items[1][0],
                              callback_data=items[1][1])],
        [InlineKeyboardButton(text=items[2][0],
                              callback_data=items[2][1])],

    ]
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return inline_buttons
