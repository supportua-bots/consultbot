import os
from pathlib import Path
from datetime import time
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import (CallbackQueryHandler, Updater, MessageHandler,
                          CommandHandler, ConversationHandler, Filters)
from telegram.utils.request import Request
from .handlers import (echo_handler, greetings_handler, menu_handler,
                      video_handler,acceptance_handler, name_handler,
                      phone_handler, category_handler, brand_handler,
                      serial_number_handler, photos_handler, reason_handler,
                      date_handler, time_handler, operator_handler,
                      chat_handler)
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
NAME, PHONE, CATEGORY, SERIAL_NUMBER, PHOTOS, REASON, CHAT = range(7)

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
            CommandHandler('start', greetings_handler),
            CallbackQueryHandler(menu_handler,
                                            pattern=r'^start$',
                                            pass_user_data=True),
            CallbackQueryHandler(video_handler,
                                            pattern=r'^video$',
                                            pass_user_data=True),
            CallbackQueryHandler(acceptance_handler,
                                            pattern=r'^continue$',
                                            pass_user_data=True),
            CallbackQueryHandler(date_handler,
                                            pattern=r'^date',
                                            pass_user_data=True),
            CallbackQueryHandler(time_handler,
                                            pattern=r'^time',
                                            pass_user_data=True),
            CallbackQueryHandler(brand_handler,
                                            pattern=r'^brand',
                                            pass_user_data=True),
            CallbackQueryHandler(photos_handler,
                                            pattern=r'^upload',
                                            pass_user_data=True),
            CallbackQueryHandler(operator_handler,
                                            pattern=r'^operator',
                                            pass_user_data=True),
            CallbackQueryHandler(reason_handler,
                                            pattern=r'^reason',
                                            pass_user_data=True),
        ],
        states={
            NAME: [MessageHandler(Filters.regex("Зв'язок з оператором"), operator_handler,
                                    pass_user_data=True),
                MessageHandler(Filters.all, name_handler,
                                    pass_user_data=True)],
            PHONE: [MessageHandler(Filters.regex("Зв'язок з оператором"), operator_handler,
                                    pass_user_data=True),
                    MessageHandler(Filters.all, phone_handler,
                                    pass_user_data=True)],
            CATEGORY: [CallbackQueryHandler(category_handler,
                                            pattern=r'^category',
                                            pass_user_data=True),
                        MessageHandler(Filters.regex("Зв'язок з оператором"), operator_handler,
                                    pass_user_data=True),
                       MessageHandler(Filters.all, category_handler,
                                    pass_user_data=True)],
            SERIAL_NUMBER: [MessageHandler(Filters.regex("Зв'язок з оператором"), operator_handler,
                                    pass_user_data=True),
                            MessageHandler(Filters.all, serial_number_handler,
                                    pass_user_data=True)],
            PHOTOS: [MessageHandler(Filters.regex("Продовжити"), photos_handler,
                                    pass_user_data=True),
                     MessageHandler(Filters.regex("Зв'язок з оператором"), operator_handler,
                                    pass_user_data=True),
                     MessageHandler(Filters.all, photos_handler,
                                    pass_user_data=True),
                     CallbackQueryHandler(photos_handler,
                                                     pattern=r'^upload',
                                                     pass_user_data=True)],
            REASON: [MessageHandler(Filters.regex("Зв'язок з оператором"), operator_handler,
                                    pass_user_data=True),
                     MessageHandler(Filters.all, reason_handler,
                                    pass_user_data=True)],
            CHAT: [MessageHandler(Filters.all, chat_handler,
                                    pass_user_data=True),
                   CallbackQueryHandler(menu_handler,
                                                   pattern=r'^start$',
                                                   pass_user_data=True),],
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
