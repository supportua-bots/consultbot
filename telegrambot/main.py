import os
from pathlib import Path
from datetime import time
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import (CallbackQueryHandler, Updater, MessageHandler,
                          CommandHandler, ConversationHandler, Filters)
from telegram.utils.request import Request
from .handlers import (echo_handler, greetings_handler, menu_handler,
                       operator_handler, chat_handler, issue_solved_handler,
                       free_consult_handler, paid_consult_handler,
                       consult_handler, buy_consult_handler, purchase_handler,
                       link_handler, payment_completed_handler, phone_handler,
                       questions_handler, file_handler)
from loguru import logger

dotenv_path = os.path.join(Path(__file__).parent.parent, 'config/.env')
load_dotenv(dotenv_path)

logger.add(
    "logs/info.log",
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="100 MB",
    compression="zip",
)


TOKEN = os.getenv("TOKEN")
CHAT, MENU = range(2)
ALLOWED_USERS = os.getenv('ALLOWED_USERS').split(',')


@logger.catch
def main():
    '''Setting up all needed to launch bot'''
    logger.info('Started')

    req = Request(
        connect_timeout=30.0,
        read_timeout=5.0,
        con_pool_size=8,
    )
    bot = Bot(
        token=TOKEN,
        request=req,
    )
    updater = Updater(
        bot=bot,
        use_context=True,
    )

    # Проверить что бот корректно подключился к Telegram API
    info = bot.get_me()
    logger.info('Bot info: %s', info)

    # Навесить обработчики команд
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('data', file_handler, Filters.user(
                username=ALLOWED_USERS)),
            CommandHandler('start', menu_handler),
            CallbackQueryHandler(questions_handler,
                                 pattern=r'^questions$',
                                 pass_user_data=True),
            CallbackQueryHandler(menu_handler,
                                 pattern=r'^start$',
                                 pass_user_data=True),
            CallbackQueryHandler(free_consult_handler,
                                 pattern=r'^free_consult$',
                                 pass_user_data=True),
            CallbackQueryHandler(consult_handler,
                                 pattern=r'^consult$',
                                 pass_user_data=True),
            CallbackQueryHandler(paid_consult_handler,
                                 pattern=r'^paid_consult',
                                 pass_user_data=True),
            CallbackQueryHandler(buy_consult_handler,
                                 pattern=r'^buy_consult',
                                 pass_user_data=True),
            CallbackQueryHandler(payment_completed_handler,
                                 pattern=r'^payment_completed',
                                 pass_user_data=True),
            CallbackQueryHandler(purchase_handler,
                                 pattern=r'^purchase',
                                 pass_user_data=True),
            CallbackQueryHandler(issue_solved_handler,
                                 pattern=r'^issue_solved',
                                 pass_user_data=True)
        ],
        states={
            CHAT: [MessageHandler(Filters.all, chat_handler,
                                  pass_user_data=True),
                   CallbackQueryHandler(menu_handler,
                                        pattern=r'^start$',
                                        pass_user_data=True),
                   CallbackQueryHandler(consult_handler,
                                        pattern=r'^consult$',
                                        pass_user_data=True),
                   CallbackQueryHandler(issue_solved_handler,
                                        pattern=r'^issue_solved',
                                        pass_user_data=True)],
            MENU: [MessageHandler(Filters.all, menu_handler,
                                  pass_user_data=True)]
        },
        fallbacks=[
            CommandHandler('cancel', greetings_handler),
        ],
    )
    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(MessageHandler(
                                    Filters.regex("Зв'язок з оператором"),
                                    operator_handler,
                                    pass_user_data=True))
    updater.dispatcher.add_handler(MessageHandler(Filters.all, echo_handler))

    updater.start_polling()
    updater.idle()
    logger.info('Stopped')


if __name__ == '__main__':
    main()
