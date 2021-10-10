import sqlite3
from sqlite3.dbapi2 import Cursor

db = sqlite3.connect('db/database.sqlite', check_same_thread=False)
sql: Cursor = db.cursor()


def new_user(tg_id, username, sex):
    sql.execute(f"""INSERT INTO 'users' (tg_id, username, sex) VALUES ('{tg_id}', '{username}', '{sex}')""")
    db.commit()


def add_to_queue(tg_id, sex):
    sql.execute(f"""INSERT INTO 'queue' (tg_id, sex) VALUES ('{tg_id}', '{sex}')""")
    db.commit()


def remove_from_queue(tg_id):
    sql.execute(f"""DELETE FROM 'queue' WHERE tg_id = '{tg_id}'""")
    db.commit()


def search(sex=None):
    if sex is None:
        user = sql.execute(f"""SELECT tg_id FROM 'queue'""").fetchone()
    else:
        user = sql.execute(f"""SELECT tg_id FROM 'queue' WHERE sex = {sex}""").fetchone()
    db.commit()
    return user


def queue_exists(tg_id):
    user_exist = sql.execute(f"""SELECT tg_id FROM 'queue' WHERE tg_id = {tg_id}""").fetchall()
    return bool(len(user_exist))


def users_exists(tg_id):
    user_exist = sql.execute(f"""SELECT tg_id FROM 'users' WHERE tg_id = {tg_id}""").fetchall()
    return bool(len(user_exist))


def update_connection(tg_id, conn_with):
    sql.execute(f"""UPDATE 'users' SET conn_with = {conn_with} WHERE tg_id = {tg_id}""")
    db.commit()


def select_conn_with_self(tg_id):
    conn_with_self = sql.execute(f"""SELECT tg_id FROM 'users' WHERE conn_with = {tg_id}""").fetchall()
    db.commit()
    return conn_with_self


def select_conn_with(tg_id):
    conn_with = sql.execute(f"""SELECT conn_with FROM 'users' WHERE tg_id = {tg_id}""").fetchall()
    db.commit()
    return conn_with


def get_user_sex(tg_id):
    sex = sql.execute(f"""SELECT sex FROM 'users' WHERE tg_id = {tg_id}""").fetchone()
    db.commit()
    return sex


def count_users():
    count = sql.execute("SELECT COUNT(*) FROM 'users'").fetchone()
    db.commit()
    return count[0]
