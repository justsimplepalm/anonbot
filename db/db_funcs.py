import sqlite3
from sqlite3.dbapi2 import Cursor

db = sqlite3.connect('db/database.sqlite', check_same_thread=False)
sql: Cursor = db.cursor()


def new_user(tg_id, username, sex):
    sql.execute(f"INSERT INTO 'users' ('tg_id', 'username', 'sex') VALUES ('{tg_id}', '{username}', '{sex}')")
    db.commit()


def user_exists(tg_id):
    user_exi = sql.execute(f"SELECT id FROM 'users' WHERE tg_id = {tg_id}").fetchone()
    return bool(user_exi)


def check_queue(tg_id):
    user_in_search = sql.execute(f"SELECT in_search FROM 'users' WHERE tg_id = {tg_id}").fetchone()
    return user_in_search[0]


def select_conn_with(tg_id):
    conn_with = sql.execute(f"SELECT conn_with FROM 'users' WHERE tg_id = {tg_id}").fetchone()
    return conn_with


def select_conn_with_self(tg_id):
    conn_with_self = sql.execute(f"SELECT tg_id FROM 'users' WHERE conn_with = {tg_id}").fetchone()
    return conn_with_self


def exit_queue(tg_id):
    sql.execute(f"UPDATE 'users' SET in_search = 'False' WHERE tg_id = {tg_id}")
    sql.execute(f"UPDATE 'users' SET sex_to_search = 'none' WHERE tg_id = {tg_id}")
    db.commit()


def update_conn_with(tg_id, conn_with):
    sql.execute(f"UPDATE 'users' SET conn_with = {conn_with} WHERE tg_id = {tg_id}")
    db.commit()


def update_count(tg_id):
    sql.execute(f"UPDATE 'users' SET all_message = all_message + 1 WHERE tg_id = {tg_id}")
    db.commit()


def add_to_queue(tg_id, sex_to_search=None, in_search=True):
    sql.execute(f"UPDATE 'users' SET sex_to_search = '{sex_to_search}' WHERE tg_id = {tg_id}")
    sql.execute(f"UPDATE 'users' SET in_search = '{in_search}' WHERE tg_id = {tg_id}")
    db.commit()


def search():
    search_result = sql.execute("SELECT tg_id FROM 'users' WHERE in_search = 'True'").fetchone()
    try:
        return search_result[0]
    except TypeError:
        pass


def count():
    count_users = sql.execute("SELECT COUNT(*) FROM 'users'").fetchone()
    return count_users[0]
