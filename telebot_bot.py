import telebot
from telebot import types

bot = telebot.TeleBot('5406422363:AAE77P3ZW-Jg3MRelYigygP_5LUfFNXVrQA')

start_spor = False  # активация начала спора
activ_pari = ''  # Пари которое выбрали с кнопки
activ_members = 0
mnenie = {}
stat_mem = 0
spor = None
winners = {}
win = False  # активация выбора победителя


@bot.message_handler(commands=['help'])
def show_help(message):
    bot.send_message(message.chat.id, 'Этот бот позволяет записывать споры и вести общий счёт. \n'
                                      'Наберите одну из следующих команд \n'
                                      ' /add_player - для добовления себя в список участников\n'
                                      ' /remove_player - если хотите убрать себя из участников и сбросить свой счёт\n'
                                      ' /show_stat - показать статистику\n'
                                      ' /add_pari - добавить спор\n'
                                      ' /show_pari - показать активные споры и выбрать победителя', parse_mode='html')

# добавляем участника
@bot.message_handler(commands=['add_player'])
def add_player(message):
    members = read_from_file(message.chat.id)
    if members.get(message.from_user.username) != None:
        mess = ('Эй ты уже в списках')
    else:
        members[message.from_user.username] = 0
        mess = f'{message.from_user.username} ты в деле'
    bot.send_message(message.chat.id, mess, parse_mode='html')
    write_from_file(members, message.chat.id)


# удаляем участника
@bot.message_handler(commands=['remove_player'])
def remove_player(message):
    members = read_from_file(message.chat.id)
    members.pop(message.from_user.username, [True])
    mess = f'Привет {message.from_user.first_name}, ты исключен из участников'
    bot.send_message(message.chat.id, mess, parse_mode='html')
    write_from_file(members, message.chat.id)


# показать статистику
@bot.message_handler(commands=['show_stat'])
def show_stat(message):
    mess = '<b>Текущий счёт</b> \n'
    members = read_from_file(message.chat.id)
    if len(members) == 0:
        bot.send_message(message.chat.id, "Тут пока пусто!", parse_mode='html')
    else:
        for key, value in members.items():
            mess += f' {key} : {value}\n'
        bot.send_message(message.chat.id, mess, parse_mode='html')


# Добавить пари
@bot.message_handler(commands=['add_pari'])
def new_pari(message):
    global start_spor, activ_members, mnenie, stat_mem
    members = read_from_file(message.chat.id)
    if start_spor != True:
        if message.from_user.username in members:
            bot.send_message(message.chat.id, 'И о чём ты хочешь поспорить?', parse_mode='html')
            start_spor = True  # спор начат
            activ_members = len(members)  # кол-во спорщиков
            mnenie = members.copy()  # список спорщиков
            for key in mnenie.keys():  # очищаем словарь
                mnenie[key] = None
            stat_mem = message.from_user.username  # зачинщик спора
        else:
            bot.send_message(message.chat.id, 'Сначала нужно зарегистрироваться!', parse_mode='html')
    else:
        bot.send_message(message.chat.id, 'Алё, спор уже начали!', parse_mode='html')


# Показать пари
@bot.message_handler(commands=['show_pari'])
def show_pari(message):
    keyboard = types.InlineKeyboardMarkup()  # создаём кнопки
    all_pari=read_pari_from_file(message.chat.id)
    if len(all_pari)>0:
        for pari in read_pari_from_file(message.chat.id):
            print(pari)
            button = types.InlineKeyboardButton(text=pari, callback_data=pari)  # кнопки с названием пари
            keyboard.add(button)
        bot.send_message(message.chat.id, 'Итак ниже активные пари, выбери интересующее', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Нет активных споров')

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global winners, win, activ_pari
    if win == False:
        keyboard = types.InlineKeyboardMarkup()
        count = 1
        message = 'Варианты ответов:\n'
        activ_pari = call.data
        file = seach_pari_from_file(call.message.chat.id, call.data)
        if file!=None:
            for key, value in file.items():
                message += f'№{count}:{value}\n'
                button = types.InlineKeyboardButton(text=count, callback_data=key)  # кнопки с ответами
                keyboard.add(button)
                winners[count] = key
                count += 1
            message += 'Выберите победителя'
            win = True
            bot.send_message(call.message.chat.id, f'{message}', reply_markup=keyboard)
    else:  # здесь мы должны удалить пари
        all_stat = (read_from_file(call.message.chat.id))
        all_stat[call.data] += 1  # увеличиваем счёт победителя
        write_from_file(all_stat, call.message.chat.id)
        bot.send_message(call.message.chat.id, f'Победитель определен, это {call.data}')
        win = False
        print(activ_pari)
        del_pari_from_file(call.message.chat.id, activ_pari)


# обработка текста, регистрируем пари
@bot.message_handler(content_types=['text'])
def handle_text(message):
    global spor, activ_members, start_spor
    if (start_spor == True):  # спор запущен?
        if spor != None:  # уже известно о чём спорить?
            if message.from_user.username in mnenie:  # юзер участвует в спорах?
                if mnenie[message.from_user.username] == None:  # юзер уже говорил?
                    mnenie[message.from_user.username] = message.text  # записываем
                    bot.send_message(message.chat.id,
                                     f'{message.from_user.username}, считает что {spor} будет {message.text}',
                                     parse_mode='html')
                    activ_members -= 1
                    if activ_members == 0:  # закончились спорщики?
                        bot.send_message(message.chat.id, 'Ставки сделаны, ставок больше нет', parse_mode='html')
                        write_pari_from_file(spor, mnenie, message.chat.id)  # пишем
                        to_null()  # обнуляем
                else:
                    bot.send_message(message.chat.id, f"Слышь {message.from_user.username} ты уже высказывался",
                                     parse_mode='html')
            else:
                bot.send_message(message.chat.id, f"Слышь {message.from_user.username} ты не участвуешь",
                                 parse_mode='html')
        elif message.from_user.username == stat_mem:  # говорит зачинщик?
            spor = message.text
            if (message.text == 'пас') or (message.text == 'pass'):
                bot.send_message(message.chat.id, f'{message.from_user.username} пасует')
            else:
                bot.send_message(message.chat.id, f"{message.from_user.username} говорит спорим что {spor}",
                                 parse_mode='html')
        else:
            bot.send_message(message.chat.id,
                             f"Слышь {message.from_user.username} пусть {stat_mem} сначала скажет о чём базар",
                             parse_mode='html')
    #else:
    elif message.from_user.username=='krusnik01':
        print('хозяин написал')
    else:
        bot.send_message(message.chat.id, 'Мы тут не лясы точим а споры спорим!')


# читаем файл участников
def read_from_file(chat_id):
    open_file = open(f'{chat_id}', 'a+')
    open_file.seek(0)
    read_string = open_file.readline()
    open_file.close()
    if len(read_string) > 0:
        return (
            dict((a.strip(), int(b.strip())) for a, b in (element.split('-') for element in read_string.split(';'))))
    else:
        return {}


# пишем в файл участников
def write_from_file(write_dict, chat_id):
    open_file = open(f'{chat_id}', 'w')
    out_txt = ''
    for key, value in write_dict.items():
        out_txt += f'{key}-{value};'
    open_file.write(out_txt[:-1])
    open_file.close()


# Ищем пари
def seach_pari_from_file(chat_id, pari_name):
    open_file = open(f'{chat_id}_pari', 'r')
    while True:
        line1 = open_file.readline().strip()
        if not line1:
            break
        if pari_name == line1:
            read_string = open_file.readline()
            open_file.close()
            if len(read_string) > 0:
                return (
                    dict((a.strip(), (b.strip())) for a, b in
                         (element.split('-') for element in read_string.split(';'))))
            else:
                return {}
        else:
            open_file.readline()


# Удаляем пари по имени
def del_pari_from_file(chat_id, pari_name):
    search_line = 'Gucci?'
    con = 0
    with open(f'{chat_id}_pari', 'r') as file:
        lines = file.readlines()
    for line in lines:
        if (line.strip() == pari_name):
            break
        con += 1
    del lines[con]
    del lines[con]
    with open(f'{chat_id}_pari', "w") as file:
        file.writelines(lines)


# читаем файл список пари, отсекаем результаты
def read_pari_from_file(chat_id):
    message = []
    pari = ''
    actual_pari = {}
    file1 = open(f'{chat_id}_pari', 'r')
    count = 0
    while True:
        pari = file1.readline().strip()
        if not pari:
            break
        actual_pari[count] = pari.strip()
        count += 1
        file1.readline()
        message.append(pari)
        # message += f'№{count} ' + pari
    file1.close()
    return (message)


# пишем в файл пари
def write_pari_from_file(pari, mnenie, chat_id):
    open_file = open(f'{chat_id}_pari', 'a+')
    out_txt = ""
    for key, value in mnenie.items():
        out_txt += f'{key}-{value};'
    open_file.write(f'{pari}\n{out_txt[:-1]}\n')


# обнуляем данные
def to_null():
    global start_spor, activ_members, mnenie, stat_mem, spor
    start_spor = False
    activ_members = 0
    mnenie = {}
    stat_mem = 0
    spor = None


# запуск бота на постоянку
bot.polling(none_stop=True)

