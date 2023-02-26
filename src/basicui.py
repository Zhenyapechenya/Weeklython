from telebot import types
import datetime
import dal
from gateway import bot
from gateway import conn
from gateway import cursor

import admin

type_of_object = ''
obj = ''
week_day = ''
slots = ''
us_id = ''

name_obj = ""
role_adm = ""

slot_name = ""

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)

def ui():

    def db_table_val(user_id: int, username: str, name: str, nickname: str, role: str,  town: str):
        cursor.execute('INSERT INTO user (user_id, username, name, nickname, role, town) VALUES (?, ?, ?, ?, ?, ?)',
                       (user_id, username, name, nickname, role, town))
        conn.commit()

    @bot.callback_query_handler(func=lambda call: call.data.startswith('slot_'))
    def succes_booking(call):
        global obj
        date = obj.split("_")[1]
        obj = call.data
        time = obj.split("_")[1]
        nick_peer = dal.get_nickname_from_db(name_obj, date, time)
        if role_adm == 'adm':
            admin.delete_book_adm(name_obj, date, time)
            bot.delete_message(call.from_user.id, call.message.message_id)
            bot.send_message(call.from_user.id, 'Получилось! ;)\nТы удалил бронирование: ' +
                             name_obj+'\nОсвободился слот на: '+time+":00 ("+date+' – '+str(nick_peer)+')')
        else:
            dal.reservation(date, time, us_id, name_obj)
            bot.delete_message(call.from_user.id, call.message.message_id)
            bot.send_message(call.from_user.id, 'Получилось! ;)\nТы забронировал: ' +
                             name_obj+'\nНачало брони: '+time+":00 ("+date+')')

    # четвертый уровень:

    @bot.callback_query_handler(func=lambda call: call.data.startswith('date_'))
    def choose_day_week(call):
        menu = types.InlineKeyboardMarkup()
        global obj
        obj = call.data
        date = obj.split("_")[1]

        obj_id = dal.get_obj_id(name_obj)
        if role_adm == 'adm':
            list_slots = dal.get_busy_slots(obj_id, date)
        else:
            list_slots = dal.get_free_slots(obj_id, date)

        for slot in list_slots:
            name_with_pref = "slot_" + str(slot)
            if role_adm == 'adm':
                nick_peer = dal.get_nickname_from_db(name_obj, date, slot)
                slot_name = str(slot)+":00 – "+str((slot+1)) + \
                    ":00 ("+str(nick_peer)+")"
            else:
                slot_name = str(slot)+":00 – "+str((slot+1))+":00"
            slot_button = types.InlineKeyboardButton(
                text=f'{slot_name}', callback_data=f'{name_with_pref}')
            menu.add(slot_button)

        if not list_slots:
            if role_adm == 'adm':
                text_date = 'На выбранный день забронированных слотов нет.'
            else:
                text_date = 'К сожалению, на выбранный день свободных слотов нет.'
            bot.send_message(call.from_user.id,
                             text=f'{text_date}', reply_markup=menu)
        else:
            text = 'Выбери время:'
            bot.send_message(call.from_user.id, text=text, reply_markup=menu)

    @bot.callback_query_handler(func=lambda call: call.data == 'book')
    def booking_level(call):
        week = types.InlineKeyboardMarkup()
        i = 1
        while i <= 7:
            day = today + datetime.timedelta(days=i)
            numb = str(day.day)+"."+str(day.month)
            numb_with_pref = "date_" + numb
            day_button = types.InlineKeyboardButton(
                text=f'{numb}', callback_data=f'{numb_with_pref}')
            week.add(day_button)
            i += 1

        text = 'Выбери дату'
        bot.send_message(call.from_user.id, text=text, reply_markup=week)

    # Карточки объектов:

    @bot.callback_query_handler(func=lambda call: call.data.startswith('s21_'))
    def cards_list(call):
        global obj
        obj = call.data
        global name_obj
        name_obj = obj.split("_")[1]

        menu = types.InlineKeyboardMarkup()
        if role_adm == 'adm':
            text_book = 'Забронированные слоты'
        else:
            text_book = 'Свободные слоты'
        book = types.InlineKeyboardButton(
            text=f'{text_book}', callback_data='book')
        menu.add(book)

        desc = dal.get_obj_description(dal.get_obj_id(name_obj))
        info = "Вы выбрали: "+name_obj+"\nИнформация: " + str(desc)
        bot.send_message(call.from_user.id, info, reply_markup=menu)

    def cards(call):
        cards_list = types.InlineKeyboardMarkup()
        nfd = dal.get_objects(us_id, type_of_object)
        if not nfd:
            bot.send_message(call.from_user.id, text="К сожалению, в выбранной категории «" +
                             type_of_object+"» нет объектов.", reply_markup=cards_list)
        else:
            for str_db in nfd:
                name_with_pref = "s21_" + str_db
                name_button = types.InlineKeyboardButton(
                    text=f'{str_db}', callback_data=f'{name_with_pref}')
                cards_list.add(name_button)
            question = 'Подробнее:'
            bot.send_message(call.from_user.id, text=question,
                             reply_markup=cards_list)


    # Описание бота
    @bot.message_handler(commands=['help'])
    def bot_description(message):
        bot.send_message(message.from_user.id, '/start Приветствие и доброе слово.\n')
        bot.send_message(message.from_user.id, '/help Инструкция к боту.\n')
        bot.send_message(message.from_user.id, '/registration Простая регистрация за четыре шага.\n')
        bot.send_message(message.from_user.id, '/reset_reg Сброс учетки (полезно, если выбрал не тот город или опечатался).\n')
        bot.send_message(message.from_user.id, '/booking Бронирование школьных объектов. Каждый слот равен часу, слотов можно выбирать несколько.\n')
        bot.send_message(message.from_user.id, '/my_booking Просмотр и удаление своих броней.\n')
        bot.send_message(message.from_user.id, '/admin Доступно только для сотрудников. Можно удалить любую бронь.\n')


    @bot.message_handler(commands=['start'])
    def bot_description(message):
        bot.send_message(message.from_user.id, 'Привет! Тебя приветствует бот «Школы 21», который поможет тебе забронировать школьные объекты.')
        bot.send_message(message.from_user.id, 'Внизу слева есть меню со всеми командами и кратким описанием. По команде /help можешь узнать немного подробней.\n')

    # Обнуление регистрации:
    @bot.callback_query_handler(func=lambda call: call.data.startswith('reset_'))
    def reset_reg(call):
        us_id = call.from_user.id
        if call.data == 'reset_yes':
            try:
                cursor.execute(f"DELETE FROM user WHERE user_id = {us_id}")
                conn.commit()
                bot.send_message(call.from_user.id, text="Готово!")
                bot.delete_message(call.from_user.id, call.message.message_id)
                return 1
            except:
                return 0   
        else:
            bot.send_message(call.from_user.id, text="Я в тебе не сомневался!")
        bot.delete_message(call.from_user.id, call.message.message_id)

    @bot.message_handler(commands=['reset_reg'])
    def reset(message):
        us_id = message.from_user.id
        name = dal.check_name(us_id)
        if name != None:    
            keyboard = types.InlineKeyboardMarkup()
            yes = types.InlineKeyboardButton(text='Да', callback_data='reset_yes')
            no = types.InlineKeyboardButton(text='Нет', callback_data='reset_no')
            keyboard.add(yes,no)
            bot.send_message(message.chat.id, text="Обнулить регистрацию?", reply_markup=keyboard)
        else: 
            bot.send_message(message.chat.id, text="Обнулять нечего! Сначала зарегистрируйся. /registration")


    # Главное меню:
    @bot.message_handler(commands=['booking', 'admin'])
    def booking(message):
        global us_id, role_adm
        us_id = message.from_user.id
        role = dal.check_role(us_id)

        if message.text == '/admin' and role == 'employee':
            role_adm = 'adm'
        else:
            role_adm = 'noadm'

        if role_adm == 'adm' or message.text == '/booking':
            keyboard = types.InlineKeyboardMarkup()  # Создаем клавиатуру
            key_conf = types.InlineKeyboardButton(
                text='Переговорная комната', callback_data='conf_room')  # Создаем кнопку переговорки
            keyboard.add(key_conf)  # Добавляем кнопку в клавиатуру
            if role != None:
                if role != 'abiturient':  # Добавляем еще две кнопки, если роль не абитур
                    key_sport = types.InlineKeyboardButton(
                        text='Спортивный инвентарь', callback_data='key_sport')
                    key_game = types.InlineKeyboardButton(
                        text='Настольная игра', callback_data='key_game')
                    keyboard.add(key_sport)
                    keyboard.add(key_game)
                if role == 'employee':  # Добавляем кнопку, если роль - работник
                    key_kitchen = types.InlineKeyboardButton(
                        text='Кухня', callback_data='key_kitchen')
                    keyboard.add(key_kitchen)
                if role_adm == 'noadm':
                    question = 'Что ты хочешь забронировать?'
                else:
                    question = 'Бронь какого объекта ты хочешь удалить?'
                bot.send_message(message.from_user.id,
                                 text=question, reply_markup=keyboard)
            else:  # Проверяем, что есть регистрация
                reg = types.ReplyKeyboardMarkup(
                    resize_keyboard=True, one_time_keyboard=True)
                reg_button = types.KeyboardButton("/registration")
                reg.add(reg_button)
                bot.send_message(
                    message.chat.id, text="Сначала регистрация:)", reply_markup=reg)
        else:
            bot.send_message(message.from_user.id,
                             'Cорри, ты зашел не в тот раздел!')


    # Все брони + отмена брони:
    @bot.callback_query_handler(func=lambda call: call.data.startswith('myslots_'))
    def cancel_booking(call):
        book_id = call.data.split("_")[1]
        dal.delete_my_book(book_id)
        bot.delete_message(call.from_user.id, call.message.message_id)
        bot.send_message(call.from_user.id, 'Получилось! ;)\nТы удалил слот.')

    @bot.message_handler(commands=['my_booking'])
    def show_booking(message):
        us_id = message.from_user.id
        my_booking = dal.get_my_book(us_id)

        if not my_booking:
            bot.send_message(message.from_user.id, 'У вас нет броней :(')
        else:
            keyboard = types.InlineKeyboardMarkup()
            for str_db in my_booking:
                obj = f'{str_db[0]}'
                time_start = f'{str_db[2]}'
                time_end = f'{str_db[2] + 1}'
                date = f'{str_db[1]}'

                str_new = obj+', '+time_start+':00-'+time_end+':00, '+date
                book_id = dal.get_book_id(str_db[0], str_db[1], str_db[2])
                name_with_pref = "myslots_" + str(book_id)
                slot = types.InlineKeyboardButton(
                    text=f'{str_new}', callback_data=f'{name_with_pref}')
                keyboard.add(slot)

            text = 'Это список всех ваших броней.\nЧтобы отменить запись, нажмите на конкретный слот.'
            bot.send_message(message.from_user.id, text=text,
                             reply_markup=keyboard)

    ### РЕГИСТРАЦИЯ ###

    @bot.message_handler(content_types=['text'])
    def start(message):
        if message.text == '/registration':
            us_id = message.from_user.id
            name = dal.check_name(us_id)
            if name != None:
                bot.send_message(message.from_user.id, "Рад снова вас видеть, " + name + '.\nРегистрироваться снова не нужно, просто нажми /booking для бронирования.')
            else:
                bot.send_message(message.from_user.id, "Нам нужно познакомиться. Я – BookBot21, главный помощник «Школы 21».")
                bot.send_message(message.from_user.id, "Как тебя зовут?")
                bot.register_next_step_handler(message, get_name)
        else:
            bot.send_message(message.from_user.id, 'Напиши /help, я тебя не понял :(')


    def get_name(message):  # получаем имя
        global name
        name = message.text
        bot.send_message(message.from_user.id, 'Твой школьный ник?')
        bot.register_next_step_handler(message, get_nickname)

    def get_nickname(message):
        global nickname
        nickname = message.text

        keyboard = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True)

        enrollee = types.KeyboardButton(text='Абитуриент')
        student = types.KeyboardButton(text='Студент')
        staff = types.KeyboardButton(text='Сотрудник')

        keyboard.add(enrollee, student)
        keyboard.add(staff)

        bot.send_message(message.from_user.id,
                         'Твоя роль в школе?', reply_markup=keyboard)
        bot.register_next_step_handler(message, get_role)

    def get_role(message):
        global role
        role = message.text

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

        novosib = types.InlineKeyboardButton(text='Новосибирск')
        kazan = types.InlineKeyboardButton(text='Казань')
        msk = types.InlineKeyboardButton(text='Москва')

        keyboard.add(novosib, kazan)
        keyboard.add(msk)

        bot.send_message(message.from_user.id,
                         'Из какого ты города?', reply_markup=keyboard)
        bot.register_next_step_handler(message, get_town)

    
    def get_town(message):
        global town
        town = message.text
        us_id = message.from_user.id
        username = message.from_user.username 
        global role
        # Меняем роль с русского на англ для БД
        if role == 'Абитуриент':
            role = 'abiturient'
        elif role == 'Студент':
            role = 'student'
        elif role == 'Сотрудник':
            role = 'employee'
        else:
            role = 'err'

        # Меняем город с русского на англ для БД
        if town == 'Новосибирск':
            town = 'novosibirsk'
        elif town == 'Москва':
            town = 'moscow'
        elif town == 'Казань':
            town = 'kazan'
        else:
            town = 'err'

        if role == 'err' or town == 'err':
            txt = 'Странные названия, мне не нравится! Давай заново. /registration'
        else:    
            db_table_val(user_id=us_id, username=username, name=name, nickname=nickname, role=role, town=town) # Закидываем данные в БД
            bot.send_message(message.chat.id, 'Запомню :)')
            txt = 'Теперь можно бронировать.\nНажимай /booking'

        a = types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, f'{txt}', reply_markup=a)

    # Типы данных:
    @bot.callback_query_handler(func=lambda call: True)
    def second_level(call):
        global type_of_object
        if call.data == 'conf_room':
            type_of_object = 'meeting_room'
        elif call.data == 'key_sport':
            type_of_object = 'sport_equipment'
        elif call.data == 'key_game':
            type_of_object = 'game'
        elif call.data == 'key_kitchen':
            type_of_object = 'kitchen'

        cards(call)

    bot.polling()
