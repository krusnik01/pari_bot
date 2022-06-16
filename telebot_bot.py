import telebot

#Bot_id
bot = telebot.TeleBot('5406422363:AAE77P3ZW-Jg3MRelYigygP_5LUfFNXVrQA')

start_spor=False
activ_members=0
mnenie={}
stat_mem=0

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
    global start_spor,activ_members,mnenie,start_spor
    members = read_from_file(message.chat.id)
    if message.from_user.username in members:
        bot.send_message(message.chat.id, 'И о чём ты хочешь поспорить?', parse_mode='html')
        start_spor=True                                 #спор начат
        activ_members=len(members)                      #кол-во спорщиков
        mnenie=members.copy()                           #список спорщиков
        start_spor=message.from_user.username           #зачинщик спора
    else:
        bot.send_message(message.chat.id,'Сначала нужно зарегистрироваться!' ,parse_mode='html')



@bot.message_handler(content_types='text')
def handle_text(message):
    if (start_spor==True): #спор запущен?
        if activ_members>0: #кто не высказался?
            print('1')

        bot.send_message(message.chat.id, f'Вы написали: {message.text}')



#читаем файл
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

# пишем в файл
def write_from_file(write_dict,chat_id):
    open_file = open(f'{chat_id}', 'w')
    out_txt = ''
    for key, value in write_dict.items():
        out_txt += f'{key}-{value};'
    open_file.write(out_txt[:-1])
    open_file.close()

#запуск бота на постоянку
bot.polling(none_stop=True)
