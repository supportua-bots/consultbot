import os
import sys
import sqlite3
import traceback
from sqlite3 import Error
from loguru import logger


@logger.catch
def post_sql_query(sql_query):
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
                        (chat_id TEXT,
                        circle_paid INTEGER,
                        circle_free INTEGER);'''
    post_sql_query(query)


@logger.catch
def add_user(chat_id):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"chat_id = '{chat_id}';"
    rows = post_sql_query(sql_selection)
    if not rows:
        query = f"INSERT INTO DATA (chat_id, circle_paid, circle_free) VALUES ('{chat_id}', '0', '1');"
        logger.info(post_sql_query(query))


@logger.catch
def check_user(chat_id):
    sql_selection = f"SELECT * FROM DATA WHERE "\
                        f"chat_id = '{chat_id}';"
    rows = post_sql_query(sql_selection)
    return rows[0]
