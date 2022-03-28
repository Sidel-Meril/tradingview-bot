#!/usr/bin/python
# -*- coding: UTF-8 -*-

import telegram.ext
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram.ext.dispatcher import run_async
import json
import random
from datetime import datetime, date
import sqlcon
import os
import selenium_get_screen

variables = {
  "telegram": {
    "token": os.environ['TELEGRAM_TOKEN'],
    "admin_id": int(os.environ['ADMIN_ID'])
  },
  "database": {
    "link": os.environ['DATABASE_URL'],
  }
}

#init bot
updater = Updater(variables['telegram']['token'], workers=10, use_context=True)
PORT = int(os.environ.get('PORT', '8443'))

def common_user(func):
    def check_user(update, contex, *args, **kwargs):
        user_id = update.message.chat.id
        db = sqlcon.Database(database_url=variables['database']['link'])
        data = db.get_users()
        users = [user[0] for user in data]
        user_plans = [user[1] for user in data]

        if user_id not in users:
            print('User undefined')
            try:
                db.add_user(user_id, plan='free')
            except Exception as e:
                print(e)
                pass
        else:
            print('User recognized, plan: %s' %(user_plans[users.index(user_id)]) )
        db.close()

        func(update, contex, *args, **kwargs)

    return check_user

def paid_plane_user(func):
    def check_user(update, contex, *args, **kwargs):
        user_id = update.message.chat.id
        db = sqlcon.Database(database_url=variables['database']['link'])
        data = db.get_users()
        users = [user[0] for user in data]
        user_plans = [user[1] for user in data]
        if user_id not in users:
            print('User undefined')
            try:
                db.add_user(user_id, plan='free')
            except:
                pass
        else:
            if user_plans[users.index(user_id)] != 'paid':
                updater.bot.send_message(user_id,'Эта функция доступна только пользователям с платной подпиской. Нажмите /pay, чтобы оплатить.')
                return False
        db.close()
        func(update, contex, *args, **kwargs)

    return check_user

def admin(func):
    def wrapper(update, context, *args, **kwargs):
        user_id = update.message.chat.id
        print(user_id, variables['telegram']['admin_id'], user_id == variables['telegram']['admin_id'])
        if user_id != variables['telegram']['admin_id']:
            return None
        print('Hi, my little queen Sidel Meril')
        res = func(update, context, *args, **kwargs)
        return res
    return wrapper

@common_user
def start(update, context):
    user_id = update.message.chat.id
    if user_id == variables['telegram']['admin_id']:
        admin_help(update, context)
    else:
        user_help(update, context)

def listpairs():
    pass

def req(update, context):
    user_id = update.message.chat.id
    message = """Введите правильно название пары и таймфрейм.
<pre>Список таймфреймов:
    
minutes:
1 minute: 1
3 minutes: 3
5 minutes: 5
15 minutes: 15
30 minutes: 30
45 minutes: 45

hours
1 hour: 60
2 hours: 120
3 hours: 180
4 hours: 240

days: 
1 hour: 1D
2 hour: 1W
3 hour: 1M

ranges
1 range: 1R,
10 range: 10R
100 ranges: 100R
1000 ranges: 1000R
    </pre>
    """
    updater.bot.send_message(chat_id=user_id, text=message, parse_mode='HTML')
    dp.add_handler(MessageHandler(telegram.ext.filters.Filters.text, get_screenshot))

@paid_plane_user
def get_screenshot(update, context):
    user_id = update.message.chat.id

    try:
        pair, timeframe = update.message.text.split(' ')
        updater.bot.send_message(chat_id=user_id, text=f"Ищу <i>{pair}</i> <b>{timeframe}</b>", parse_mode='HTML')
        screenshot = selenium_get_screen.get_screenshot(pair,timeframe)
        updater.dispatcher.bot.send_photo(chat_id=user_id, photo=screenshot)
    except Exception as e:
        print(e)
        updater.bot.send_message(chat_id=user_id, text="Ничего не найдено :( Введите название пары/таймфрейма правильно", parse_mode='HTML')

def ask():
    pass


@common_user
def pay(update, context):
    user_id = update.message.chat.id
    db = sqlcon.Database(database_url=variables['database']['link'])
    data = db.get_users()
    users = [user[0] for user in data]
    user_plans = [user[1] for user in data]
    _, price, duration, payment_data = db.get_settings()[0]
    db.close()
    if user_plans[users.index(user_id)] == 'paid':
        message = """Вы уже оформили подписку. Нажмите /help, чтобы узнать список доступных команд.
        """
        updater.bot.send_message(chat_id=user_id, text=message, parse_mode='HTML')

    message=f"""Стоимость подписки на <b>{duration} дней</b> составляет <b>{price} долларов</b>.
    
Реквизиты:
<pre>{payment_data}</pre>

Пришлите скриншот оплаты (квитанцию) боту в чат, и он активирует Вам доступ.
    """
    updater.bot.send_message(chat_id=user_id, text=message, parse_mode='HTML')
    updater.dispatcher.add_handler(MessageHandler(telegram.ext.filters.Filters.photo, check_pay))

@common_user
def check_pay(update, context):
    user_id = update.message.chat.id
    updater.bot.forward_message(variables['telegram']['admin_id'], user_id, update.message.message_id)
    updater.bot.send_message(user_id, "Скриншот отправлен на рассмотрение оператору. Ожидайте ответа.")
    dp.add_handler(CommandHandler("accept", accept))
    dp.add_handler(CommandHandler("decline", decline))

@admin
def accept(update, context):
    user_id = update.message.reply_to_message.forward_from.id
    db = sqlcon.Database(database_url=variables['database']['link'])
    _, price, duration, payment_data = db.get_settings()[0]
    _duration = duration*86280
    db.edit_user_by_id(user_id, 'paid', int(datetime.now().timestamp()), int(datetime.now().timestamp())+_duration)
    updater.bot.send_message(user_id, "Оператор рассмотрел вашу заявку, оплата принята")
    updater.bot.send_message(variables['telegram']['admin_id'],
                             "Запрос принят. Уведомление успешно доставлено пользователю %i." % (user_id))

@admin
def decline(update, context):
    user_id = update.message.reply_to_message.forward_from.id
    updater.bot.send_message(user_id, "Оператор рассмотрел вашу заявку, что-то пошло не так :( \nОтправьте вашу заявку еще раз.")
    updater.bot.send_message(variables['telegram']['admin_id'], "Запрос отклонен. Уведомление успешно доставлено пользователю %i." %(user_id))

@admin
def admin_help(update, context):
    user_id = update.message.chat.id
    help_message = """
    /paid - список оплативших - показывает когда и кто оплачивал и (в скобках желательно писать сколько кому осталось)
    /writeall - сделать всем рассылку - можно разослать какую-либо новость всем и сразу
    /addpair - добавить символ пары - с помощью команды, админ может добавить в список доступных пар новую
    /deletepair - удалить символ пары - с помощью команды, админ может удалить из списка доступных пар старую и ненужную,
    /chngprice - сменить цену подписки - бот пишет после нажатия: Введите новую цену в долл. Админ пишет xx и отправляет. Бот пишет: цена изменена.
    /chngpayment - сменить реквизиты оплаты - аналогично как с ценой.
    /adddays - добавить дни клиенту - возможность по логину, имени, id-юзера добавить некое количество дней, к примеру в подарок или как компенсация.
    /whois - узнать id_пользователя
    """

    updater.bot.send_message(chat_id=user_id, text=help_message)

@common_user
def user_help(update, context):
    user_id = update.message.chat.id
    help_message = """
    /listpairs - список торговых пар
    /pay - оплатить подписку
    /request - запросить скриншот
    /ask - задать вопрос
    """
    # set parse message mood

    updater.bot.send_message(chat_id=user_id, text=help_message)

@admin
def paid(update, context):
    db = sqlcon.Database(database_url=variables['database']['link'])
    data = db.get_users()
    db.close()
    paid_users = list(filter(lambda x: x != None, [row if row[1] == 'paid' else None for row in data]))
    message_rows = [ """<a href="tg://user?id=%i">id%i</a>:
<b>%s / %s</b>
<b>Oсталось</b>: %i %s
    
    """
                     %(user, user, date.fromtimestamp(start).isoformat(),date.fromtimestamp(end).isoformat(),
                       int((end-datetime.now().timestamp())/86280),
                       'дня' if str(int((end - datetime.now().timestamp())/86280))[-1] == '2' or
                                str(int((end - datetime.now().timestamp())/86280))[-1] == '3' or
                                str(int((end - datetime.now().timestamp()) / 86280))[-1] == '4'else 'дней')
    for user, _, start, end in paid_users]
    message=f"""
<b>Статистика использования бота</b>
<pre>Всего пользователей: {len(data)}</pre>
<pre>Платных подписок: {len(paid_users)}</pre>

Пользователи, у которых оформлена подписка:

"""+('\n').join(message_rows)

    updater.bot.send_message(chat_id=variables['telegram']['admin_id'], text=message, parse_mode = 'HTML')


@admin
def writeall(update, context):
    db = sqlcon.Database(database_url=variables['database']['link'])
    users = db.get_users()
    users = [user[0] for user in users]
    db.close()
    res_text = update.message.text.replace('/writeall', '')
    for user_id in users:
        try:
            updater.bot.send_message(chat_id=user_id, text=res_text, parse_mode='HTML')
            updater.bot.send_message(chat_id=variables['telegram']['admin_id'],
                                     text="""Сообщение пользователю <a href="tg://user?id=%i">id%i</a> досталено.""" % user_id,
                                     parse_mode='HTML')
        except:
            updater.bot.send_message(chat_id=variables['telegram']['admin_id'],
                                     text="""Пользователь <a href="tg://user?id=%i">id%i</a> удалил бота, но останется в базе для статистики.""" % user_id,
                                     parse_mode='HTML')


@admin
def addpair(update, context):
    pass

@admin
def whois(update, context):
    try:
        user_id = update.message.reply_to_message.forward_from.id
        db = sqlcon.Database(database_url=variables['database']['link'])
        data = db.get_users()
        all_users = [row[0] for row in data]
        db.close()
        user_row = all_users.index(user_id) if user_id in all_users else None

        if user_row != None:
            if data[user_row][1] == 'paid':
                user, _, start, end = data[user_row]
                updater.bot.send_message(variables['telegram']['admin_id'],
                                         """Пользователь <a href="tg://user?id=%i">id%i</a> найден в базе:
                                         <pre>Подписка оформлена</pre>
                                         <pre>%s / %s</pre>
                                         <pre>Oсталось: %i %s</pre>""" %(user, user, date.fromtimestamp(start).isoformat(),date.fromtimestamp(end).isoformat(),
                                   int((end-datetime.now().timestamp())/86280),
                                   'дня' if str(int((end - datetime.now().timestamp())/86280))[-1] == '2' or
                                            str(int((end - datetime.now().timestamp())/86280))[-1] == '3' or
                                            str(int((end - datetime.now().timestamp()) / 86280))[-1] == '4'else 'дней')
                                         , parse_mode='HTML')

            else:
                updater.bot.send_message(variables['telegram']['admin_id'],
                                         """Пользователь <a href="tg://user?id=%i">id%i</a> найден в базе:
                                         <pre>Подписка не оформлена</pre>""" % (user_id, user_id), parse_mode='HTML')
        else:
            updater.bot.send_message(variables['telegram']['admin_id'],
                                     """Пользователь <a href="tg://user?id=%i">id%i</a> не найден в базе.""" % (user_id,user_id)
                                     , parse_mode='HTML')
    except:
        updater.bot.send_message(variables['telegram']['admin_id'],
                                 """Данную команду нужно использовать как ответ на сообщение интересующего вас пользователя."""
                                 , parse_mode='HTML')

@admin
def deletepair(update, context):
    pass

@admin
def chngprice(update, context):
    try:
        _, price = update.message.text.split(' ')
        price = int(price)
        db = sqlcon.Database(database_url=variables['database']['link'])
        db.change_settings_price(user_id, price)
        db.close()
        message = """
    Цена подписки теперь <b>%i долларов</b>.
                """ % (price)
        updater.bot.send_message(chat_id=variables['telegram']['admin_id'], text=message, parse_mode='HTML')
    except:
        message = """
            Введите запрос в формате:
            <pre>/chngprice цена(только число)</pre>
                """
        updater.bot.send_message(chat_id=variables['telegram']['admin_id'], text=message, parse_mode='HTML')

@admin
def chngpayment(update, context):
    try:
        _, payment = update.message.text.repalce('/chngpayment','')
        db = sqlcon.Database(database_url=variables['database']['link'])
        db.change_settings_payment(payment)
        db.close()
        message = """
    Реквизиты для оплаты обновлены:
     <pre>%s/pre>.
                """ % (payment)
        updater.bot.send_message(chat_id=variables['telegram']['admin_id'], text=message, parse_mode='HTML')
    except:
        message = """
            Введите запрос в формате:
            <pre>/chngpayment реквизиты</pre>
                """
        updater.bot.send_message(chat_id=variables['telegram']['admin_id'], text=message, parse_mode='HTML')


@admin
def adddays(update, context):
    try:
        _, user_id, days = update.message.text.split(' ')
        user_id, days = int(user_id), int(days)
        _days = days * 86280
        db = sqlcon.Database(database_url=variables['database']['link'])
        data = db.get_users()
        user_index = [row[0] for row in data].index(user_id)
        db.edit_user_end_by_id(user_id, data[user_index][3] + _days)
        db.close()
        message = """
    Подписка пользователя <a href="tg://user?id=%i">id%i</a> изменена на %i дней
                """ % (user_id, user_id, days)
        updater.bot.send_message(chat_id=variables['telegram']['admin_id'], text=message, parse_mode='HTML')
    except:
        message = """
            Введите запрос в формате:
            <pre>/adddays id_пользователя(только число) количество_дней</pre>
                """
        updater.bot.send_message(chat_id=variables['telegram']['admin_id'], text=message, parse_mode='HTML')



if __name__=="__main__":
    job_queue = updater.job_queue
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

#user commands
    """
    /listpairs - список торговых пар
    /pay - оплатить подписку
    /request - запросить скриншот
    /ask - задать вопрос
    """
    dp.add_handler(CommandHandler("help", user_help))
    dp.add_handler(CommandHandler("listpairs", listpairs))
    dp.add_handler(CommandHandler("pay", pay))
    dp.add_handler(CommandHandler("request", req))
    dp.add_handler(CommandHandler("ask", ask))

#admin commands
    dp.add_handler(CommandHandler("admin_help", admin_help))
    dp.add_handler(CommandHandler("paid", paid))
    dp.add_handler(CommandHandler("writeall", writeall))
    dp.add_handler(CommandHandler("addpair", addpair))
    dp.add_handler(CommandHandler("deletepair", deletepair))
    dp.add_handler(CommandHandler("chngprice", chngprice))
    dp.add_handler(CommandHandler("chngpayment", chngpayment))
    dp.add_handler(CommandHandler("adddays", adddays))
    dp.add_handler(CommandHandler("whois", whois))

    """
    /paid - список оплативших - показывает когда и кто оплачивал и (в скобках желательно писать сколько кому осталось)
    /writeall - сделать всем рассылку - можно разослать какую-либо новость всем и сразу
    /addpair - добавить символ пары - с помощью команды, админ может добавить в список доступных пар новую
    /deletepair - удалить символ пары - с помощью команды, админ может удалить из списка доступных пар старую и ненужную,
    /chngprice - сменить цену подписки - бот пишет после нажатия: Введите новую цену в долл. Админ пишет xx и отправляет. Бот пишет: цена изменена.
    /chngpayment - сменить реквизиты оплаты - аналогично как с ценой.
    /adddays - добавить дни клиенту - возможность по логину, имени, id-юзера добавить некое количество дней, к примеру в подарок или как компенсация.
    /whois - узнать id_пользователя
    
    """
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=variables['telegram']['token'],
                        webhook_url = 'https://murmuring-inlet-95645.herokuapp.com/' + variables['telegram']['token'])
    updater.idle()


