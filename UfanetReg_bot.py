import telebot
from telebot import types
import pymysql
import re
import datetime
import time
import connector
from secrets import Secrets
token = Secrets()
token = token.get_token()
bot = telebot.TeleBot(token)
num=0
a={'starttime':'',
'endtime':'',
'dateres':str(datetime.datetime.now().date()).replace("-",""),
'k':0,
'd':0}

rooms=4
@bot.message_handler(content_types=['text'])
def get_text_messages(message):#обрабаытвает сообщения
    if message.text == "Резервирование":#начало резервирования
        a['k']=1
        markup=types.InlineKeyboardMarkup(row_width=1)
        for i in range(rooms):
            item=types.InlineKeyboardButton("Переговорная комната "+str(i+1),callback_data=str(i+1))
            markup.add(item)
        bot.send_message(message.from_user.id, "Выберите переговорную комнату: ", reply_markup=markup)

    elif re.search("\d{2}:\d{2}-\d{2}:\d{2}",message.text)!=None and a['k'] and a['d']:# выбор времени резервирования
        fl=1
        start,end=message.text.split("-")
        try:
            #if int(start[:start.find(":")])>23 or int(start[:start.find(":")])<0 or int(start[start.find(":")+1:])>59 or int(start[start.find(":")+1:])<0:
            #    fl=0
            #if int(end[:end.find(":")])>23 or int(end[:end.find(":")])<0 or int(end[end.find(":")+1:])>59 or int(end[end.find(":")+1:])<0:
            #    fl=0
            h=int(start[:start.find(":")])
            m=int(start[start.find(":")+1:])
            start= str(datetime.time(h,m,0))
            #a['starttime']=datetime.time(h,m,0)
            h=int(end[:end.find(":")])
            m=int(end[end.find(":")+1:])

            end=str(datetime.time(h,m,0))
            bot.send_message(message.from_user.id,"время: "+str(start)+" - "+str(end))
        except Exception as e:
            bot.send_message(message.from_user.id,"неверный формат времени "+ repr(e))
            fl=0
        if start>end:
            start,end=end,start
        a['dateres']=str(a['dateres']).replace("-","")
        bot.send_message(message.from_user.id, "Вы выбрали комнату {}\nна время: {} - {}\n{}".format(str(num),str(start),str(end),str(a['dateres']).replace("-","")))

        sql="SELECT * FROM room1  WHERE roomnumber={} AND dateres={}".format(str(num),str(a['dateres']).replace("-",""))
        dat=str(datetime.datetime.now().date()).replace("-","")
        if fl:
            rows =connector.my_request(sql)
        #привести время начала и конца резервирования в единую строку для запроса в бд
            start=str(start)
            end=str(end)
            start=start.replace(":","")
            end=end.replace(":","")

            sql="SELECT * FROM room1  WHERE fio={} AND dateres={} AND starttime={} AND endtime={}".format(str(message.from_user.id),str(a['dateres']),start,end)

            rows1=connector.my_request(sql)

            if len(rows1):
                bot.send_message(message.from_user.id, "одновременное бронирование нескольких комнат невозможно ")
                fl=0



            for row in rows:
                if str(a['dateres'])==str(row["dateres"]).replace("-",""):
                    if (start<=str(row["starttime"]).replace(":","") and end>str(row["starttime"]).replace(":","")) or(start<=str(row["starttime"]).replace(":","") and end>=str(row["endtime"]).replace(":","")) or(start>=str(row["starttime"]).replace(":","") and start<=str(row["endtime"]).replace(":","")) or (start>=str(row["starttime"]).replace(":","") and end<=str(row["endtime"]).replace(":","")):
                        bot.send_message(message.from_user.id, "ошибка со временем ")
                        fl=0
                        break
            if len(rows)==0 or fl:
                sql="INSERT INTO room1 (fio,datereg,starttime,endtime,roomnumber,dateres) VALUES({},{},{},{},{},{})".format(str(message.from_user.id),dat,start,end,str(num),str(a['dateres']))
                if connector.my_request(sql):
                    fl=1
        if fl:
            bot.send_message(message.from_user.id, "вы забронировали комнату"+str(num)+" на дату:"+str(a['dateres']))
        else:
            bot.send_message(message.from_user.id, "неудалось забронировать комнату")



    elif re.search("\d{4}-\d{2}-\d{2}",message.text) and a['k']:# дата резервирования
        try:
            y,m,d=map(int, message.text.split("-"))
            a['dateres']=datetime.datetime(y,m,d).date()
            #str(message.text).replace("-","")
            bot.send_message(message.from_user.id, "На какое время желаете забронировать\n(Формат: HH:MM-HH:MM)?")
            a['d']=1
        except Exception as e:
            bot.send_message(message.from_user.id,"Неверный формат даты"+ repr(e))
    elif message.text=="/help":
         bot.send_message(message.from_user.id, "я бот для резервирования переговорных комнат \nчтобы начать зарезервировать комнату напишите 'Резервирование' \nдату и время необходимо вводить в строго заданном формате во избежании проблем ")

    else:
        bot.send_message(message.from_user.id, "Я вас не понимаю. Напишите /help.")

@bot.callback_query_handler(func=lambda call: True)#обрабатывает кнопки
def callback_inline(call):
    try:
        if call.message:
            global num
            num=call.data
            sql="SELECT * FROM room1 WHERE roomnumber="+str(num)
            rows=connector.my_request(sql)
            s=""
            for row in rows:
                s+="("+str(row["starttime"])+" - "+str(row["endtime"])+") "+str(row["dateres"])+"\n"
            bot.send_message(call.message.chat.id, "На данный момент комната зарезервирована на следующее время:\n"+s)
            bot.send_message(call.message.chat.id, "На какую дату хотите зарезервировать комнату\n(Формат:YYYY-MM-DD):")


    except Exception as e:
        bot.send_message(call.message.chat.id, "Возникла ошибка: "+repr(e))


bot.polling(none_stop=True, interval=0)

