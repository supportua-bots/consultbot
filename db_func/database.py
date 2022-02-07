import os
import sys
import sqlite3
import traceback
from sqlite3 import Error
from loguru import logger


@logger.catch
def post_sql_query(sql_query):
    logger.info(sql_query)
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'my.db')
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(sql_query)
        except Error as er:
            logger.info(sql_query)
            logger.info('SQLite error: %s' % (' '.join(er.args)))
            logger.info("Exception class is: ", er.__class__)
            logger.info('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            logger.info(traceback.format_exception(
                exc_type, exc_value, exc_tb))
            pass
        result = cursor.fetchall()
        return result


@logger.catch
def create_table():
    query = '''CREATE TABLE IF NOT EXISTS DATA
                        (chat_id_viber TEXT,
                        circle_paid INTEGER,
                        circle_free INTEGER,
                        stage TEXT,
                        counter INTEGER,
                        phone TEXT,
                        chat_id_telegram TEXT);'''
    post_sql_query(query)
    query = '''CREATE TABLE IF NOT EXISTS NOTIFICATION
                        (chat_id TEXT,
                        platform TEXT,
                        stage TEXT,
                        counter INTEGER);'''
    post_sql_query(query)


@logger.catch
def export_all():
    sql_selection = "SELECT chat_id_telegram, chat_id_viber, circle_paid, circle_free, phone FROM DATA;"
    rows = post_sql_query(sql_selection)
    return rows


@logger.catch
def notification_list():
    sql_selection = f"SELECT * FROM NOTIFICATION;"
    rows = post_sql_query(sql_selection)
    return rows


@logger.catch
def delete_task_for_notification(chat_id):
    query = f"DELETE FROM NOTIFICATION WHERE chat_id = '{chat_id}';"
    logger.info(post_sql_query(query))


@logger.catch
def add_task_for_notification_viber(chat_id):
    query = f"INSERT INTO NOTIFICATION (chat_id, platform, stage, counter) VALUES ('{chat_id}', 'viber', '1', '0');"
    logger.info(post_sql_query(query))


@logger.catch
def add_task_for_notification_telegram(chat_id):
    query = f"INSERT INTO NOTIFICATION (chat_id, platform, stage, counter) VALUES ('{chat_id}', 'telegram', '1', '0');"
    logger.info(post_sql_query(query))


@logger.catch
def plus_wait_notification_viber(chat_id):
    sql_selection = f"SELECT * FROM DATA NOTIFICATION "\
                        f"chat_id = '{chat_id}';"
    rows = post_sql_query(sql_selection)
    if rows:
        updated_field = int(rows[0][3]) + 1
        query = f"UPDATE DATA SET counter = '{updated_field}' WHERE chat_id = '{chat_id}';"
        post_sql_query(query)


@logger.catch
def plus_wait_notification_telegram(chat_id):
    sql_selection = f"SELECT * FROM DATA NOTIFICATION "\
                        f"chat_id = '{chat_id}';"
    rows = post_sql_query(sql_selection)
    if rows:
        updated_field = int(rows[0][3]) + 1
        query = f"UPDATE DATA SET counter = '{updated_field}' WHERE chat_id = '{chat_id}';"
        post_sql_query(query)


@logger.catch
def add_user_viber(chat_id, phone):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"phone = '{phone}';"
    rows = post_sql_query(sql_selection)
    if not rows:
        query = f"INSERT INTO DATA (chat_id_viber, circle_paid, circle_free, stage, counter, phone) VALUES ('{chat_id}', '0', '1', 'chat', '0', '{phone}');"
        logger.info(post_sql_query(query))
    else:
        query = f"UPDATE DATA SET chat_id_viber = '{chat_id}' WHERE phone = '{phone}';"
        logger.info(post_sql_query(query))


@logger.catch
def add_user_telegram(chat_id, phone):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"phone = '{phone}';"
    rows = post_sql_query(sql_selection)
    if not rows:
        query = f"INSERT INTO DATA (chat_id_telegram, circle_paid, circle_free, stage, counter, phone) VALUES ('{chat_id}', '0', '1', 'chat', '0', '{phone}');"
        logger.info(post_sql_query(query))
    else:
        query = f"UPDATE DATA SET chat_id_telegram = '{chat_id}' WHERE phone = '{phone}';"
        logger.info(post_sql_query(query))


@logger.catch
def check_user_viber(chat_id):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"chat_id_viber = '{chat_id}';"
    rows = post_sql_query(sql_selection)
    return rows[0]


@logger.catch
def check_user_telegram(chat_id):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"chat_id_telegram = '{chat_id}';"
    rows = post_sql_query(sql_selection)
    return rows[0]


@logger.catch
def minus_free_consult_viber(chat_id):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"chat_id_viber = '{chat_id}';"
    rows = post_sql_query(sql_selection)
    if rows:
        updated_field = int(rows[0][2]) - 1
        query = f"UPDATE DATA SET circle_free = '{updated_field}' WHERE chat_id_viber = '{chat_id}';"
        post_sql_query(query)


@logger.catch
def minus_free_consult_telegram(chat_id):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"chat_id_telegram = '{chat_id}';"
    rows = post_sql_query(sql_selection)
    if rows:
        updated_field = int(rows[0][2]) - 1
        query = f"UPDATE DATA SET circle_free = '{updated_field}' WHERE chat_id_telegram = '{chat_id}';"
        post_sql_query(query)


@logger.catch
def minus_paid_consult_viber(chat_id):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"chat_id_viber = '{chat_id}';"
    rows = post_sql_query(sql_selection)
    if rows:
        updated_field = int(rows[0][1]) - 1
        query = f"UPDATE DATA SET circle_paid = '{updated_field}' WHERE chat_id_viber = '{chat_id}';"
        post_sql_query(query)


@logger.catch
def minus_paid_consult_telegram(chat_id):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"chat_id_telegram = '{chat_id}';"
    rows = post_sql_query(sql_selection)
    if rows:
        updated_field = int(rows[0][1]) - 1
        query = f"UPDATE DATA SET circle_paid = '{updated_field}' WHERE chat_id_telegram = '{chat_id}';"
        post_sql_query(query)


@logger.catch
def plus_paid_consult_viber(chat_id, amount):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"chat_id_viber = '{chat_id}';"
    rows = post_sql_query(sql_selection)
    if rows:
        updated_field = int(rows[0][1]) + int(amount)
        query = f"UPDATE DATA SET circle_paid = '{updated_field}' WHERE chat_id_viber = '{chat_id}';"
        post_sql_query(query)


@logger.catch
def plus_paid_consult_telegram(chat_id, amount):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"chat_id_telegram = '{chat_id}';"
    rows = post_sql_query(sql_selection)
    if rows:
        updated_field = int(rows[0][1]) + int(amount)
        query = f"UPDATE DATA SET circle_paid = '{updated_field}' WHERE chat_id_telegram = '{chat_id}';"
        post_sql_query(query)


@logger.catch
def change_stage_to_await_viber(chat_id):
    query = f"UPDATE DATA SET stage = 'await' WHERE chat_id_viber = '{chat_id}';"
    post_sql_query(query)


@logger.catch
def change_stage_to_await_telegram(chat_id):
    query = f"UPDATE DATA SET stage = 'await' WHERE chat_id_telegram = '{chat_id}';"
    post_sql_query(query)


@logger.catch
def change_stage_to_chat_viber(chat_id):
    query = f"UPDATE DATA SET stage = 'chat' WHERE chat_id_viber = '{chat_id}';"
    post_sql_query(query)


@logger.catch
def change_stage_to_chat_telegram(chat_id):
    query = f"UPDATE DATA SET stage = 'chat' WHERE chat_id_telegram = '{chat_id}';"
    post_sql_query(query)


@logger.catch
def await_list():
    sql_selection = f"SELECT * FROM DATA WHERE stage = 'await';"
    rows = post_sql_query(sql_selection)
    return rows


@logger.catch
def plus_wait_counter_viber(chat_id):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"chat_id_viber = '{chat_id}';"
    rows = post_sql_query(sql_selection)
    if rows:
        updated_field = int(rows[0][4]) + 1
        query = f"UPDATE DATA SET counter = '{updated_field}' WHERE chat_id_viber = '{chat_id}';"
        post_sql_query(query)


@logger.catch
def plus_wait_counter_telegram(chat_id):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"chat_id_telegram = '{chat_id}';"
    rows = post_sql_query(sql_selection)
    if rows:
        updated_field = int(rows[0][4]) + 1
        query = f"UPDATE DATA SET counter = '{updated_field}' WHERE chat_id_telegram = '{chat_id}';"
        post_sql_query(query)


@logger.catch
def reset_counter_viber(chat_id):
    query = f"UPDATE DATA SET counter = '0' WHERE chat_id_viber = '{chat_id}';"
    post_sql_query(query)


@logger.catch
def reset_counter_telegram(chat_id):
    query = f"UPDATE DATA SET counter = '0' WHERE chat_id_telegram = '{chat_id}';"
    post_sql_query(query)


@logger.catch
def paid_consults_viber(chat_id):
    query = f"SELECT * FROM DATA WHERE chat_id_viber = '{chat_id}';"
    rows = post_sql_query(query)
    return rows[0][1]


@logger.catch
def paid_consults_telegram(chat_id):
    query = f"SELECT * FROM DATA WHERE chat_id_telegram = '{chat_id}';"
    rows = post_sql_query(query)
    return rows[0][1]


@logger.catch
def get_phone_telegram(chat_id):
    query = f"SELECT phone FROM DATA WHERE chat_id_telegram = '{chat_id}';"
    rows = post_sql_query(query)
    return rows[0][0]


@logger.catch
def get_phone_viber(chat_id):
    query = f"SELECT phone FROM DATA WHERE chat_id_viber = '{chat_id}';"
    rows = post_sql_query(query)
    return rows[0][0]


if __name__ == '__main__':
    logger.info(get_phone_telegram('389609639'))
