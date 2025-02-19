import telebot
from telebot import types
import traceback
import re
import datetime
import connector

from DB_Worker import DB_Wroker
from secrets import Secrets

Secret_token = Secrets()
token = Secret_token.get_token()
bot = telebot.TeleBot(token)

db_worker = DB_Wroker()

num = 0
a = {'starttime': '',
     'endtime': '',
     'dateres': str(datetime.datetime.now().date()).replace("-", ""),
     'k': 0,
     'd': 0}
rooms = db_worker.get_room_count()

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.from_user.id,
                     "я бот для резервирования переговорных комнат \n"
                     "чтобы начать зарезервировать комнату напишите 'Резервирование' \n"
                     "дату и время необходимо вводить в строго заданном формате во избежании проблем \n"
                     "Для резервирования комнаты выполните команду: /reserve")

#@bot.message_handler(content_types=['text'])
def time_res(message):  #обрабаытвает сообщения
    global db_worker
    global a
    if re.search("\d{2}[\/., : ]*\d{2}[ -]*\d{2}[\/., : ]*\d{2}", message.text) != None:  # выбор времени резервирования
        fl = 1
        start = re.findall("\d{2}[\/., : ]*\d{2}[ -]*",message.text)[0]
        end = re.findall( "(?s:.*)\d{2}[\/., : ]*\d{2}",message.text)[-1]
        try:
            start_h ,start_m = re.split("[\/\.\,s:]", start)
            start = datetime.time(start_h ,start_m, 0)
            end_h, end_m = re.split("[\/\.\,s:]", end)
            end = datetime.time(end_h, end_m, 0)
            bot.send_message(message.from_user.id, "время: " + str(start) + " - " + str(end))
            if start > end:
                start, end = end, start
            bot.send_message(message.from_user.id,
                             "Вы выбрали комнату {}\nна время: {} - {}\n{}".format(str(num), str(start),
                                                                                   str(end),
                                                                                   str(a['dateres']).replace("-", "")))
        except Exception as e:
            traceback.print_exc()
            bot.send_message(message.from_user.id, "неверный формат времени " + repr(e))
            fl = 0
        dat = str(datetime.datetime.now().date()).replace("-", "")
        if fl:
            rows = db_worker.cursor.reserve_room()
            #привести время начала и конца резервирования в единую строку для запроса в бд
            start = str(start)
            end = str(end)
            start = start.replace(":", "")
            end = end.replace(":", "")

            sql = "SELECT * FROM room  WHERE fio={} AND dateres={} AND starttime={} AND endtime={}".format(
                str(message.from_user.id), str(a['dateres']), start, end)

            rows1 = connector.my_request(sql)

            if len(rows1):
                bot.send_message(message.from_user.id, "одновременное бронирование нескольких комнат невозможно ")
                fl = 0

            for row in rows:
                if str(a['dateres']) == str(row["dateres"]).replace("-", ""):
                    if (start <= str(row["starttime"]).replace(":", "") and end > str(row["starttime"]).replace(":",
                                                                                                                "")) or (
                            start <= str(row["starttime"]).replace(":", "") and end >= str(row["endtime"]).replace(":",
                                                                                                                   "")) or (
                            start >= str(row["starttime"]).replace(":", "") and start <= str(row["endtime"]).replace(
                            ":", "")) or (
                            start >= str(row["starttime"]).replace(":", "") and end <= str(row["endtime"]).replace(":",
                                                                                                                   "")):
                        bot.send_message(message.from_user.id, "ошибка со временем ")
                        fl = 0
                        break
            if len(rows) == 0 or fl:
                sql = "INSERT INTO meeting_room (fio,datereg,starttime,endtime,roomnumber,dateres) VALUES({},{},{},{},{},{})".format(
                    str(message.from_user.id), dat, start, end, str(num), str(a['dateres']))
                if connector.my_request(sql):
                    fl = 1
        if fl:
            bot.send_message(message.from_user.id,
                             "вы забронировали комнату" + str(num) + " на дату:" + str(a['dateres']))
        else:
            bot.send_message(message.from_user.id, "неудалось забронировать комнату")
    else:
        bot.send_message(message.from_user.id, "Неверный формат времени" )



def date_res(message):
    global db_worker
    if re.search("\d{2}[\/., ]*\d{2}[\/., ]*\d{4}", message.text) != None:  # дата резервирования
        try:
            d, m, y = map(int, re.split("[\/., ]", message.text))
            reserve_date = datetime.datetime(y, m, d).date()
            current_date = datetime.datetime.now().date()
            if current_date > reserve_date:
                bot.send_message(message.from_user.id, "Нельзя забронировать комнату на прошедший день. Введите другую дату.")
                bot.register_next_step_handler(message, date_res)
                return
            bot.send_message(message.from_user.id, "На какое время желаете забронировать\n(Формат: HH:MM-HH:MM)?")
            bot.register_next_step_handler(message, time_res)
        except Exception as e:
            bot.send_message(message.from_user.id, "Неверный формат даты" + repr(e))

    else:
        bot.send_message(message.from_user.id, "Я вас не понимаю. Напишите /help.")


@bot.message_handler(commands=['reserve'])
def reserve(message):
    global db_worker
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i in range(db_worker.rooms_count):
        item = types.InlineKeyboardButton("Переговорная комната " + str(i + 1), callback_data=str(i + 1))
        markup.add(item)
    bot.send_message(message.from_user.id, "Выберите переговорную комнату: ", reply_markup=markup)
    bot.register_next_step_handler(message, date_res)


@bot.callback_query_handler(func=lambda call: True)  #обрабатывает кнопки
def callback_inline(call):
    global db_worker
    try:
        if call.message:
            roomNumber = call.data
            rows = db_worker.get_reserved_time(roomNumber)
            s = ""
            for row in rows:
                s += "(" + str(row["starttime"]) + " - " + str(row["endtime"]) + ") " + str(row["dateres"]) + "\n"
            bot.send_message(call.message.chat.id, "На данный момент комната зарезервирована на следующее время:\n" + s)
            bot.send_message(call.message.chat.id, "На какую дату хотите зарезервировать комнату\n(Формат: ДД.ММ.ГГГГ):")


    except Exception as e:
        traceback.print_exc()
        bot.send_message(call.message.chat.id, "Возникла ошибка: " + repr(e))


bot.polling(none_stop=True, interval=0)
