from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton


def tg_keyboard_constructor(buttons: list):
    inline_keyboard = []
    for button in buttons:
        inline_keyboard.append([InlineKeyboardButton(
                                    text=button[0],
                                    callback_data=button[1])])
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return inline_buttons
