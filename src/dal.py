import sqlite3
import datetime
from gateway import conn
from gateway import cursor

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)


def db_table_val(user_id: int, username: str, name: str, nickname: str, role: str, town: str):
    cursor.execute('INSERT INTO user (user_id, username, name, nickname, role, town) VALUES (?, ?, ?, ?, ?, ?)', (user_id, username, name, nickname, role, town))
    conn.commit()


def get_obj_description(obj_id):  # возвращает описание конкретного выбранного объекта
    try:
        obj_description = str(cursor.execute(f"SELECT description FROM object WHERE object_id = {obj_id} ").fetchone()[0])
        return obj_description
    except:
        return None


def check_name(userid):
    try:
        a = str(cursor.execute(f"SELECT nickname FROM user WHERE user_id = {userid} ").fetchone()[0])
        return a
    except:
        return None


def get_obj_id(obj_name):
    try:
        obj_id = str(cursor.execute(f"SELECT object_id FROM object WHERE name = '{obj_name}' ").fetchone()[0])
        return obj_id
    except:
        return None


def reserve_obj(usid, name_from_db, name_obj, obj_id, date, time):
    slot_db = "time_slot"
    cursor.execute(f'INSERT INTO book (user_id, nickname, name_object, object_id, date, {slot_db}) VALUES (?, ?, ?, ?, ?, ?)',
                   (usid, name_from_db, name_obj, obj_id, date, time))
    conn.commit()


def reservation(date, time, us_id, name_obj):
    name_from_db = check_name(us_id)
    obj_id = get_obj_id(name_obj)
    reserve_obj(us_id, name_from_db, name_obj, obj_id, date, time)


def check_role(userid):
    try:
        user_role = str(cursor.execute(f"SELECT role FROM user WHERE user_id = {userid} ").fetchone()[0])
        return user_role
    except:
        return None


def get_objects(userid, obj_type):  # возвращает список объектов выбранного типа
    try:
        user_city = str(cursor.execute(f"SELECT town FROM user WHERE user_id = {userid} ").fetchone()[0])
        result = list(cursor.execute(f"SELECT name FROM object WHERE city = '{user_city}' AND type IN ('{obj_type}')").fetchall())
        return (list(map(lambda x: x[0], result)))
    except:
        return None


def get_free_slots(obj_id, date):  # возвращает список свободных слотов по выбранной дате для определенного объекта
    try:
        all_fields = cursor.execute(f"SELECT * FROM book WHERE object_id = {obj_id} AND date = {date}").fetchall()
        busy_slots = [field for fields in all_fields for field in fields[6:] if field != None]
        busy_slots.sort(reverse=True)
        free_slots = []
        i = 10
        if not busy_slots:
            while i < 19:
                free_slots.append(i)
                i += 1
        else:
            busy_slot = busy_slots.pop()
            while i < 19:
                if i != busy_slot:
                    free_slots.append(i)
                else:
                    if(len(busy_slots)):
                        busy_slot = busy_slots.pop()
                i += 1
        return free_slots
    except:
        return None


def get_my_book(userid):
    try:
        books = cursor.execute(f"SELECT name_object, date, time_slot FROM book WHERE user_id = {userid} ").fetchall()
        return books
    except:
        return None


def get_book_id(name_obj, date, time):
    try:
        book_id = str(cursor.execute(f"SELECT book_id FROM book WHERE name_object = '{name_obj}' AND date = '{date}' AND time_slot = '{time}'").fetchone()[0])
        return book_id
    except:
        return None


def get_nickname_from_db(name_obj, date, time):
    try:
        nickname = str(cursor.execute(f"SELECT nickname FROM book WHERE name_object = '{name_obj}' AND date = '{date}' AND time_slot = '{time}'").fetchone()[0])
        return nickname
    except:
        return None


def get_busy_slots(obj_id, date):
    try:
        all_fields = cursor.execute(f"SELECT * FROM book WHERE object_id = {obj_id} AND date = {date}").fetchall()
        busy_slots = [field for fields in all_fields for field in fields[6:] if field != None]
        busy_slots.sort(reverse=False)
        return busy_slots
    except:
        return None


def delete_my_book(bookid):
    try:
        cursor.execute(f"DELETE FROM book WHERE book_id = {bookid}")
        conn.commit()
        return 1
    except:
        return 0
