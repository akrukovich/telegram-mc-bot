import sqlite3

__connection = None


def get_connection():
    global __connection

    if not __connection:
        __connection = sqlite3.connect('bot_db.db', check_same_thread=False)

    return __connection


def init_db(force: bool = None):
    conn = get_connection()

    cursor = conn.cursor()

    if force:
        cursor.execute('DROP TABLE IF EXISTS users')
        cursor.execute('DROP TABLE IF EXISTS shows')

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
         user_id     INTEGER PRIMARY KEY,
         first_name        TEXT NOT NULL
         ) 
         """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shows(
             id          INTEGER PRIMARY KEY,
             user_id          INTEGER NOT NULL,
             title          TEXT NOT NULL,
             season     INTEGER NOT NULL,
             episode        INTEGER NOT NULL,
             FOREIGN KEY(user_id) REFERENCES users(user_id)
             ) 
             """)

    conn.commit()


def add_user(user_id: int, first_name: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute('Select * from users where user_id = ?', (user_id,))
    user = c.fetchone()

    if not user:

        c.execute('INSERT INTO users(user_id,first_name) VALUES  (?,?)', (user_id, first_name))
        conn.commit()

    else:
        pass


def add_show(title: str, user_id: int, season: int, episode: int):
    title = title.title()
    conn = get_connection()
    c = conn.cursor()
    c.execute('Select * FROM shows WHERE title = ? and user_id = ?; ', (title, user_id))
    data = c.fetchone()
    if not data:

        c.execute('INSERT INTO shows(title, user_id,season,episode) VALUES  (?,?,?,?)',
                  (title, user_id, season, episode))
        conn.commit()
    else:
        pass


def update_show(title: str, user_id: int, season: int, episode: int):
    title = title.title()
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE shows set season = ?,episode = ? WHERE user_id = ? and title = ?',
              (season, episode, user_id, title))
    conn.commit()


def delete_show(title: str, user_id: int):
    title = title.title()
    conn = get_connection()
    c = conn.cursor()
    c.execute('Select * From shows where title = ?;', (title,))
    shows = c.fetchall()

    if not shows:
        raise ValueError

    c.execute('DELETE FROM shows WHERE user_id = ? and title = ? ;',
              (user_id, title))
    conn.commit()


def get_all_shows(user_id: int):
    conn = get_connection()
    c = conn.cursor()
    data = c.execute('Select * From shows where user_id = ?;', (user_id,))
    data = data.fetchall()

    return data
