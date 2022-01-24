from telegrambot.utils.tools import tg_keyboard_constructor
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton


free_consult = tg_keyboard_constructor([
            ('Під’єднати оператора 👨‍💻', 'free_consult'),
            ('Популярні питання ❓', 'questions')
            ])

clarificational_consult = tg_keyboard_constructor([
            ('Так, маю ще питання', 'consult'),
            ('Ні, дякую!', 'issue_solved'),
            ])

paid_consult = tg_keyboard_constructor([
            ('Під’єднати оператора 👨‍💻', 'paid_consult'),
            ('Популярні питання ❓', 'questions')
            ])

buy_consult = tg_keyboard_constructor([
            ('Під’єднати оператора 👨', 'buy_consult'),
            ('Популярні питання ❓', 'questions')
            ])


solo_free_consult = tg_keyboard_constructor([
            ('Під’єднати оператора 👨‍💻', 'free_consult')
            ])

solo_paid_consult = tg_keyboard_constructor([
            ('Під’єднати оператора 👨‍💻', 'paid_consult')
            ])

solo_buy_consult = tg_keyboard_constructor([
            ('Під’єднати оператора 👨', 'buy_consult')
            ])


solved_free_consult = [
            ('Залишити відгук 🚀', ''),
            ('Під’єднати оператора 👨‍💻', 'free_consult'),
            ('Популярні питання ❓', 'questions')
            ]

solved_paid_consult = [
            ('Залишити відгук 🚀', ''),
            ('Під’єднати оператора 👨‍💻', 'paid_consult'),
            ('Популярні питання ❓', 'questions')
            ]

solved_buy_consult = [
            ('Залишити відгук 🚀', ''),
            ('Під’єднати оператора 👨', 'buy_consult'),
            ('Популярні питання ❓', 'questions')
            ]

payment_proceed = [
            ('Оплата', ''),
            ('Посилання застаріло?', 'link'),
            ('Проблема з оплатою?', 'consult'),
            ]

payment_check = tg_keyboard_constructor([
            ('Проверить статус оплаты', 'payment_completed')
            ])

buy_amount = tg_keyboard_constructor([
            ('1', 'purchase_1'),
            ('3', 'purchase_3'),
            ('5', 'purchase_5')
            ])


def payment_keyboard_generator(items: list, link: str):
    inline_keyboard = [
        [InlineKeyboardButton(text=items[0][0],
                              url=link)]

    ]
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return inline_buttons


def solved_keyboard_generator(items: list, link: str):
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
