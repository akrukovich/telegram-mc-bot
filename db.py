import sqlite3

__connection = None


def get_connection():
    global __connection

    if not __connection:
        __connection = sqlite3.connect('bot_db.db',check_same_thread=False)

    return __connection


def init_db(force: bool = None):
    conn = get_connection()

    cursor = conn.cursor()

    if force:
        cursor.execute('DROP TABLE IF EXISTS user_message')

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_message(
         id          INTEGER PRIMARY KEY,
         user_id     INTEGER NOT NULL,
         text        TEXT NOT NULL
         ) 
         """)

    conn.commit()


def add_message(user_id: int, text: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO user_message (user_id,text) VALUES  (?,?)', (user_id, text))
    conn.commit()


def get_info():
    conn = get_connection()
    c = conn.cursor()
    c.execute('Select * from user_message')
    data = c.fetchall()

    return data

init_db(True)