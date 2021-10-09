import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import date, datetime, timedelta


dotenv_path = os.path.join(Path(__file__).parent.parent, 'config/.env')
load_dotenv(dotenv_path)

MAIN_COLOR = os.getenv("COLOR")


def keyboard_consctructor(items: list) -> dict:
    """Pasting infromation from list of items to keyboard menu template."""
    if len(items) > 12:
        width = 1
    elif len(items) == 3:
        width = 2
    elif len(items) > 1:
        width = 3
    else:
        width = 6
    keyboard = {
        "DefaultHeight": False,
        "BgColor": '#f7f9fc',
        "Type": "keyboard",
        "Buttons": [{
                "Columns": width,
                "Rows": 1,
                "BgColor": MAIN_COLOR,
                "BgLoop": True,
                "ActionType": "reply",
                "ActionBody": item[1],
                "ReplyType": "message",
                "Text": item[0],
                # "TextOpacity": 0,
        } for item in items]
    }
    return keyboard


def save_message_to_history(message, type, chat_id):
    text = ''
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    if type == 'bot':
        text += 'Bot '
    else:
        text += 'User '
    text += f'{now}: {message}\n'
    if not os.path.exists(f'media/{chat_id}'):
        os.makedirs(f'media/{chat_id}')
    try:
        history_file = open(f'media/{chat_id}/history.txt', 'a')
    except:
        history_file = open(f'media/{chat_id}/history.txt', 'w')
    history_file.write(text)
    history_file.close()
    return text


def workdays(d, end, excluded=(6, 7)):
    days = []
    while d.date() <= end.date():
        if d.isoweekday() not in excluded:
            days.append(d)
        d += timedelta(days=1)
    return days[1:19]


def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]
