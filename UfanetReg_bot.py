import telebot
from telebot import types
import pymysql
import re
import datetime
token='5344038250:AAGWruxJDA9craFmiDqPynedlcQ-6E8Qagc'
bot = telebot.TeleBot(token)
num=0
a={'user':'',
        'datereg':'',
        'starttime':'',
        'endtime':'',
        'dateres':''}


#cursor = con.cursor()

@bot.message_handler(content_types=['text'])#обрабаытвает сообщения
def get_text_messages(message):
    if message.text == "Резервирование":
       # bot.send_message(message.from_user.id, "Выберите переговорную комнату: ")
        markup=types.InlineKeyboardMarkup(row_width=1)
        #cursor = con.cursor()
        #n=cursor.execute("SELECT COUNT(*) as count FROM room1")
        for i in range(4):
            item=types.InlineKeyboardButton("Переговорная комната "+str(i+1),callback_data=str(i+1))
            markup.add(item)
        bot.send_message(message.from_user.id, "Выберите переговорную комнату: ", reply_markup=markup)
        #cursor.close()
    elif re.search("\d{2}:\d{2}[\s-]\d{2}:\d{2}",message.text)!=None:
        start,end=message.text.split("-")
        if start>end:
            start,end=end,start
        bot.send_message(message.from_user.id, "Вы выбрали комнату {}\nна время: {} - {}".format(str(num),str(start),str(end)))

        #with con:

            #cursor = con.cursor()
        con = pymysql.connect(host='localhost',user='user',password='user',database='rooms',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
        cursor = con.cursor()
        sql="SELECT * FROM room1  WHERE roomnumber={} AND dateres={}".format(str(num),str(a['dateres']))
        cursor.execute(sql)
        rows = cursor.fetchall()
        start=str(start)
        end=str(end)
        start=start.replace(":","")
        end=end.replace(":","")
        cursor.close()
        con.close()
        con = pymysql.connect(host='localhost',user='user',password='user',database='rooms',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
        cursor = con.cursor()
        sql="SELECT * FROM room1  WHERE fio={} AND dateres={} AND starttime={} AND endtime={}".format(str(message.from_user.id),str(a['dateres']),start,end)
        cursor.execute(sql)
        rows1 = cursor.fetchall()
        fl=1
        if len(rows1):
            bot.send_message(message.from_user.id, "одновременное бронирование нескольких комнат невозможно ")
            fl=0

        dat=str(datetime.datetime.now().date()).replace("-","")

        for row in rows:
            if str(a['dateres'])==str(row["dateres"]).replace("-",""):
                if (start+"00"<=str(row["starttime"]).replace(":","") and end+"00">str(row["starttime"]).replace(":","")) or(start+"00"<=str(row["starttime"]).replace(":","") and end+"00">=str(row["endtime"]).replace(":","")) or(start+"00">=str(row["starttime"]).replace(":","") and start+"00"<=str(row["endtime"]).replace(":","")) or (start+"00">=str(row["starttime"]).replace(":","") and end+"00"<=str(row["endtime"]).replace(":","")):
                    bot.send_message(message.from_user.id, "ошибка со временем ")
                    fl=0
                    break
                #cursor.close()

        if len(rows)==0 or fl:
            #bot.send_message(message.from_user.id, "вы забронировали комнату "+str(num))
            cursor.close()
            con.close()
            con=pymysql.connect(host='localhost',user='user',password='user',database='rooms',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
            cursor = con.cursor()
            sql="INSERT INTO room1 (fio,datereg,starttime,endtime,roomnumber,dateres) VALUES({},{},{},{},{},{})".format(str(message.from_user.id),dat,start+"00",end+"00",str(num),str(a['dateres']))

            if cursor.execute(sql):
                #bot.send_message(message.from_user.id,"вы забронировали комнату")
                fl=1
            con.commit()
            #bot.send_message(message.from_user.id, "{},{},{},{},{},{}".format(str(message.from_user.id),dat,start+"00",end+"00",str(num),str(a['dateres'])))

        if fl:
            bot.send_message(message.from_user.id, "вы забронировали комнату "+str(a['dateres']))
        else:
            bot.send_message(message.from_user.id, "неудалось забронировать комнату")


        cursor.close()
        con.close()
    elif re.search("\d{4}-\d{2}-\d{2}",message.text):
        bot.send_message(message.from_user.id, "На какое время желаете забронировать(формат: HH:MM-HH:MM)?")
        a['dateres']= str(message.text).replace("-","")

    else:
        bot.send_message(message.from_user.id, "Я вас не понимаю. Напиши /help.")

@bot.callback_query_handler(func=lambda call: True)#обрабатывает кнопки
def callback_inline(call):
    try:
        if call.message:
            global num
            num=call.data
            #запрос в таблицу с номером num
            #with con:
            con = pymysql.connect(host='localhost',user='user',password='user',database='rooms',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
            cursor = con.cursor()
            cursor.execute("SELECT * FROM room1 WHERE roomnumber="+str(num))

            #получение всех записей (занятое время)
            rows = cursor.fetchall()
            #вывод всех записей
            s=""
            for row in rows:
                s+="("+str(row["starttime"])+" - "+str(row["endtime"])+") "+str(row["dateres"])+"\n"
            cursor.close()
            bot.send_message(call.message.chat.id, "На данный момент комната зарезервирована на следующее время:\n"+s)
            bot.send_message(call.message.chat.id, "На какую дату хотите зарезервировать комнату(Формат:YYYY-MM-DD):")

            cursor.close()
            con.close()
    except Exception as e:
        bot.send_message(call.message.chat.id, "Возникла ошибка: "+repr(e))


bot.polling(none_stop=True, interval=0)

