import telebot

#Bot_id
bot = telebot.TeleBot('5406422363:AAE77P3ZW-Jg3MRelYigygP_5LUfFNXVrQA')

start_spor=False
activ_members=0
mnenie={}
stat_mem=0
spor=None


#добавляем участника
@bot.message_handler(commands=['add_player'])
def add_player(message):
    members=read_from_file(message.chat.id)
    if members.get(message.from_user.username)!=None:
        mess=('Эй ты уже в списках')
    else:
        members[message.from_user.username]=0
        mess=f'{message.from_user.username} ты в деле'
    bot.send_message(message.chat.id, mess, parse_mode='html')
    write_from_file(members,message.chat.id)

#удаляем участника
@bot.message_handler(commands=['remove_player'])
def remove_player(message):
    members = read_from_file(message.chat.id)
    members.pop(message.from_user.username,[True])
    mess= f'Привет {message.from_user.first_name}, ты исключен из участников'
    bot.send_message(message.chat.id, mess, parse_mode='html')
    write_from_file(members, message.chat.id)

#показать статистику
@bot.message_handler(commands=['show_stat'])
def show_stat(message):
    mess='<b>Текущий счёт</b> \n'
    members = read_from_file(message.chat.id)
    if len(members)==0:
        bot.send_message(message.chat.id, "Тут пока пусто!", parse_mode='html')
    else:
        for key,value in members.items():
            mess+=f' {key} : {value}\n'
        bot.send_message(message.chat.id, mess, parse_mode='html')

#Добавить пари
@bot.message_handler(commands=['add_pari'])
def new_pari(message):
    global start_spor,activ_members,mnenie,stat_mem
    members = read_from_file(message.chat.id)
    if start_spor!=True:
        if message.from_user.username in members:
            bot.send_message(message.chat.id, 'И о чём ты хочешь поспорить?', parse_mode='html')
            start_spor=True                                 #спор начат
            activ_members=len(members)                      #кол-во спорщиков
            mnenie=members.copy()                           #список спорщиков
            for key in mnenie.keys():                #очищаем словарь
                mnenie[key]=None
            stat_mem=message.from_user.username           #зачинщик спора
        else:
            bot.send_message(message.chat.id,'Сначала нужно зарегистрироваться!' ,parse_mode='html')
    else:bot.send_message(message.chat.id,'Алё, спор уже начали!' ,parse_mode='html')

#Показать пари
@bot.message_handler(commands=['show_pari'])
def show_pari(message):
    bot.send_message(message.chat.id, read_pari_from_file(message.chat.id),parse_mode='html')

#объявляем победителя
@bot.message_handler(commands=['winner'])
def check_winer(message):
    members = read_from_file(message.chat.id)
    members[message.from_user.username] += 1
    bot.send_message(message.chat.id, f'Победил {message.from_user.username}', parse_mode='html')
    write_from_file(members,message.chat.id)










#обработка текста, регистрируем пари
@bot.message_handler(content_types=['text'])
def handle_text(message):
    global spor,activ_members,start_spor
    if (start_spor==True): #спор запущен?
        if spor!=None: #уже известно о чём спорить?
            if message.from_user.username in mnenie: #юзер участвует в спорах?
                if mnenie[message.from_user.username]==None: #юзер уже говорил?
                    mnenie[message.from_user.username]=message.text #записываем
                    bot.send_message(message.chat.id, f'{message.from_user.username}, считает что {spor} будет {message.text}',parse_mode='html')
                    activ_members-=1
                    if activ_members == 0:  #закончились спорщики?
                        bot.send_message(message.chat.id, 'Ставки сделаны, ставок больше нет', parse_mode='html')
                        write_pari_from_file(spor,mnenie,message.chat.id) #пишем
                        to_null() #обнуляем
                else:bot.send_message(message.chat.id, f"Слышь {message.from_user.username} ты уже высказывался",parse_mode='html')
            else:bot.send_message(message.chat.id, f"Слышь {message.from_user.username} ты не участвуешь",parse_mode='html')
        elif message.from_user.username ==stat_mem: #говорит зачинщик?
            spor = message.text
            bot.send_message(message.chat.id, f"{message.from_user.username} говорит спорим что {spor}", parse_mode='html')
        else:bot.send_message(message.chat.id, f"Слышь {message.from_user.username} пусть {stat_mem} сначала скажет о чём базар",parse_mode='html')
    else:bot.send_message(message.chat.id, 'Мы тут не лясы точим а споры спорим!')

#читаем файл участников
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

#пишем в файл участников
def write_from_file(write_dict,chat_id):
    open_file = open(f'{chat_id}', 'w')
    out_txt = ''
    for key, value in write_dict.items():
        out_txt += f'{key}-{value};'
    open_file.write(out_txt[:-1])
    open_file.close()

#читаем файл пари
def read_pari_from_file(chat_id):
    message = 'СПИСОК АКТИВНЫХ ПАРИ \n выбери интересующее \n'
    pari = ''
    actual_pari = {}
    file1 = open(f'{chat_id}_pari', 'r')
    count = 0
    while True:
        pari = file1.readline()
        if not pari:
            break
        actual_pari[count] = pari.strip()
        count += 1
        file1.readline()
        message += f'№{count} ' + pari
    return (message)

#пишем в файл пари
def write_pari_from_file(pari,mnenie,chat_id):
    open_file=open(f'{chat_id}_pari','a+')
    out_txt =""
    for key, value in mnenie.items():
        out_txt += f'{key}-{value};'
    open_file.write(f'{pari}\n{out_txt[:-1]}\n')

#обнуляем данные
def to_null():
    global start_spor,activ_members,mnenie,stat_mem,spor
    start_spor = False
    activ_members = 0
    mnenie = {}
    stat_mem = 0
    spor = None

#запуск бота на постоянку
bot.polling(none_stop=True)









# @bot.message_handler(commands=['print'])
# def print_value(message):
#     bot.send_message(message.chat.id,f'start_spor={start_spor}\n'
#                                      f'start_mem={stat_mem}\n'
#                                      f'spor={spor}\n'
#                                      f'activ_mem={activ_members}\n'
#                                      f'mnenie={mnenie}',parse_mode='html')
