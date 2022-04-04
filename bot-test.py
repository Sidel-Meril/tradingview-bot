#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup
from telegram.ext import Updater, MessageHandler, ConversationHandler, CommandHandler, CallbackQueryHandler, \
    CallbackContext
from telegram.ext.dispatcher import run_async
import json
from telegram.ext.filters import Filters
import numpy as np
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

#Init bot
updater = Updater(variables['telegram']['token'], workers=10, use_context=True)
PORT = int(os.environ.get('PORT', '8443'))

#Conversations
PAY_RESPONSE,ASK_RESPONSE,ANSWER_RESPONSE, WRITEALL_RESPONSE, EDITTEXT_LABEL_REQUEST, EDITTEXT_TEXT_RESPONSE, \
EDITTEXT_TEXT_REQUEST, GET_SCREENSHOT = range(8)

#Globals
user_id_to_response = None
setting_label_to_edit = None

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

        result = func(update, contex, *args, **kwargs)
        return result
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
            else:
                if datetime.now().timestamp()>data[users.index(user_id)][3]:
                    db.edit_user_by_id(user_id,'free',0,0)
                    updater.bot.send_message(user_id,
                                             'Ваша подписка истекла. Нажмите /pay, чтобы оплатить.')

                    return False
        db.close()
        result = func(update, contex, *args, **kwargs)
        return result

    return check_user

def admin(func):
    def check_user(update, context, *args, **kwargs):
        user_id = update.message.chat.id
        db = sqlcon.Database(database_url=variables['database']['link'])
        admin_ids = [row[0] for row in db.get_admins()]
        db.close()
        if user_id not in admin_ids:
            return None
        print('Hi, Admin')
        res = func(update, context, admin_id = user_id, *args, **kwargs)
        return res
    return check_user

@common_user
def start(update, context):
    user_id = update.message.chat.id
    db = sqlcon.Database(database_url=variables['database']['link'])
    admin_ids = [row[0] for row in db.get_admins()]
    db.close()
    if user_id in admin_ids:
        admin_help(update, context)
    else:
        user_help(update, context)

@common_user
def listpairs(update, context):
    user_id = update.message.chat.id
    db = sqlcon.Database(database_url=variables['database']['link'])
    data = db.get_pairs()
    db.close()
    message_rows = [f"""<pre>{exchange}:{symbol}</pre>""" for symbol, exchange in data]
    message = f"""
<pre>Всего пар: {len(data)}</pre>

Пары, по которым доступен поиск:

    """ + ('\n').join(message_rows)

    updater.bot.send_message(chat_id=user_id, text=message, parse_mode='HTML')

def req(update, context):
    user_id = update.message.chat.id
    message = """Введите правильно название пары и таймфрейм.
    """
    updater.bot.send_message(chat_id=user_id, text=message, parse_mode='HTML')
    return GET_SCREENSHOT


@paid_plane_user
def get_screenshot(update, context):
    user_id = update.message.chat.id
    db = sqlcon.Database(database_url=variables['database']['link'])
    data = db.get_cookies()

    cookies = json.loads(data)

    try:
        pair, timeframe = update.message.text.split(' ')
        updater.bot.send_message(chat_id=user_id, text=f"Ищу <i>{pair}</i> <b>{timeframe}</b>", parse_mode='HTML')
        pairs = db.get_pairs()
        pair_index = [row[0] for row in pairs].index(pair)
        pair_exchange = pairs[pair_index][1]
        screenshot = selenium_get_screen.get_screenshot(f"{pair_exchange}:{pair}",timeframe,cookies)
        updater.dispatcher.bot.send_photo(chat_id=user_id, photo=screenshot)

    except Exception as e:
        print(e)
        updater.bot.send_message(chat_id=user_id, text="Ничего не найдено :( Введите название пары/таймфрейма правильно", parse_mode='HTML')
    db.close()
    return ConversationHandler.END

@common_user
def ask_request(update, context):
    user_id = update.message.chat.id
    updater.bot.send_message(chat_id=user_id, text="""Введите ваше сообщение для администрации.""",
                             parse_mode='HTML')
    return ASK_RESPONSE


def ask_response(update, message):
    user_id = update.message.chat.id
    user_message = update.message.text
    keyboard = [[InlineKeyboardButton('Ответить', callback_data=f'reply_to {user_id} 0')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    db = sqlcon.Database(database_url=variables['database']['link'])
    admin_ids = [row[0] for row in db.get_admins()]
    db.close()
    for admin_id in admin_ids:
        updater.bot.send_message(admin_id, text="""<b>Сообщение от пользователя</b>
    %s

    <i>%s</i>    
        """ % (get_info(user_id), user_message), parse_mode='HTML',
                             reply_markup=reply_markup)
    updater.bot.send_message(user_id, "Вопрос отправлен на рассмотрение администратору. Ожидайте ответа.")
    return ConversationHandler.END

def ask_response_with_photo(update, message):
    user_id = update.message.chat.id
    keyboard = [[InlineKeyboardButton('Ответить', callback_data=f'reply_to {user_id} 0')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    db = sqlcon.Database(database_url=variables['database']['link'])
    admin_ids = [row[0] for row in db.get_admins()]
    db.close()
    try:
        file_id = update.message.photo[-1].file_id
        user_message = update.message.caption
    except:
        file_id = update.message.reply_to_message.photo[-1].file_id
        user_message = update.message.reply_to_message.caption


    for admin_id in admin_ids:
        updater.bot.send_photo(admin_id, photo=file_id,caption="""<b>Сообщение от пользователя</b>
    %s

    <i>%s</i>    
        """ % (get_info(user_id), user_message), parse_mode='HTML',
                             reply_markup=reply_markup)
    updater.bot.send_message(user_id, "Вопрос отправлен на рассмотрение администратору. Ожидайте ответа.")
    return ConversationHandler.END

@common_user
def pay_request(update, context):
    user_id = update.message.chat.id
    db = sqlcon.Database(database_url=variables['database']['link'])
    data = db.get_users()
    users = [user[0] for user in data]
    user_plans = [user[1] for user in data]
    price, duration, payment_data = int(db.get_setting('price')), int(db.get_setting('term')), db.get_setting('payment')
    if user_plans[users.index(user_id)] == 'paid':
        message = f"""Вы уже оформили подписку. Нажмите /help, чтобы узнать список доступных команд.
Ваша подписка действительна до {date.fromtimestamp(data[users.index(user_id)][3]).isoformat()}
        """
        updater.bot.send_message(chat_id=user_id, text=message, parse_mode='HTML')
        return ConversationHandler.END

    message=f"%s" %(db.get_setting('payment_message'))
    db.close()

    keyboard = [[InlineKeyboardButton('Оплатить', callback_data=f'pay {user_id} 0'), InlineKeyboardButton('Я пока еще подумаю...', callback_data=f'decline_pay {user_id} 0')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    updater.bot.send_message(chat_id=user_id, text=message, parse_mode='HTML', reply_markup = reply_markup)
    return PAY_RESPONSE

def pay_response(update, context):
    user_id = update.message.chat.id
    updater.bot.send_message(user_id, "Пришлите скриншот оплаты (квитанцию) боту в чат, и он активирует Вам доступ.")
    keyboard = [[InlineKeyboardButton('Принять', callback_data=f'accept {user_id} 0'),
                 InlineKeyboardButton('Отклонить',callback_data=f'decline {user_id} 0')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        db = sqlcon.Database(database_url=variables['database']['link'])
        admin_ids = [row[0] for row in db.get_admins()]
        db.close()
        for admin_id in admin_ids:
            updater.bot.send_photo(admin_id, photo=update.message.photo[-1].file_id,
                               caption="""Скриншот оплаты от пользователя <a href="tg://user?id=%i">id%i</a>""" %(user_id, user_id), parse_mode='HTML', reply_markup=reply_markup)
        updater.bot.send_message(user_id, "Скриншот отправлен на рассмотрение оператору. Ожидайте ответа.")
    except Exception as e:
        print(e)
        updater.bot.send_message(user_id, "Что-то пошло не так :( Попробуйте еще раз отправить скриншот.")
    return ConversationHandler.END

def cancel(update, context):
    user_id = update.message.chat.id
    updater.bot.send_message(user_id, "Текущая операция отменена.")
    return ConversationHandler.END

def pay_buttons(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    admin_id = update.callback_query.from_user.id
    print('Button ', admin_id)
    query.answer()
    if 'accept' in query.data:
        _, user_id, __ = query.data.split(' ')
        accept(int(user_id))
    elif 'decline_pay' in query.data:
        _, user_id, __ = query.data.split(' ')
        updater.bot.send_message(chat_id=admin_id, text="""Хорошо, воспользуйтесь /pay, когда передумаете. 
    Если у Вас остались вопросы нажмите /ask, чтобы задать их администрации.""", parse_mode='HTML')
        return ConversationHandler.END
    elif 'decline' in query.data:
        _, user_id, __ = query.data.split(' ')
        decline(int(user_id))
    elif 'pay' in query.data:
        _, user_id, __ = query.data.split(' ')
        return PAY_RESPONSE
    elif 'reply_to' in query.data:
        global user_id_to_response
        _, user_id_to_response, __ = query.data.split(' ')
        updater.bot.send_message(chat_id=admin_id, text="""Введите ответ пользователю.""", parse_mode='HTML')
        return ANSWER_RESPONSE

@admin
def answer_response(update, context, admin_id):
    global user_id_to_response
    answer = update.message.text
    try:
        updater.bot.send_message(chat_id=user_id_to_response, text="<b>Ответ администратора на Ваше сообщение</b>\n"+answer,
                                 parse_mode='HTML')
        updater.bot.send_message(chat_id=admin_id, text=f"""Вы ответили пользователю <a href="tg://user?id={user_id_to_response}">id{user_id_to_response}</a>""",
                                 parse_mode='HTML')
    except:
        pass
    user_id_to_response = None
    return ConversationHandler.END

@admin
def answer_response_with_photo(update, context, admin_id):
    global user_id_to_response


    try:
        file_id = update.message.photo[-1].file_id
        answer = update.message.caption
    except:
        file_id = update.message.reply_to_message.photo[-1].file_id
        answer = update.message.reply_to_message.caption

    try:
        updater.bot.send_photo(chat_id=user_id_to_response, photo=file_id, caption="<b>Ответ администратора на Ваше сообщение</b>\n"+answer,
                                 parse_mode='HTML')
        updater.bot.send_message(chat_id=admin_id, text=f"""Вы ответили пользователю <a href="tg://user?id={user_id_to_response}">id{user_id_to_response}</a>""",
                                 parse_mode='HTML')
    except:
        pass
    user_id_to_response = None
    return ConversationHandler.END


def accept(user_id):
    db = sqlcon.Database(database_url=variables['database']['link'])
    price, duration, payment_data = int(db.get_setting('price')), int(db.get_setting('term')), db.get_setting('payment')
    _duration = duration*86280
    db.edit_user_by_id(user_id, 'paid', int(datetime.now().timestamp()), int(datetime.now().timestamp())+_duration)
    admin_ids = [row[0] for row in db.get_admins()]
    db.close()
    updater.bot.send_message(user_id, "Оператор рассмотрел вашу заявку, оплата принята."
                                      "\nВаша подписка действительна до "
                                      f"{date.fromtimestamp(int(datetime.now().timestamp())+_duration).isoformat()}")
    for admin_id in admin_ids:
        updater.bot.send_message(admin_id,
                             f"""Запрос принят. Уведомление успешно доставлено пользователю <a href="tg://user?id={user_id}">id{user_id}</a>""", parse_mode='HTML')

def decline(user_id):
    updater.bot.send_message(user_id, "Оператор рассмотрел вашу заявку, что-то пошло не так :( \nОтправьте вашу заявку еще раз.")
    db = sqlcon.Database(database_url=variables['database']['link'])
    admin_ids = [row[0] for row in db.get_admins()]
    db.close()
    for admin_id in admin_ids:
        updater.bot.send_message(admin_id, f"""Запрос отклонен. Уведомление успешно доставлено пользователю <a href="tg://user?id={user_id}">id{user_id}</a>""",
                             parse_mode = 'HTML')

@admin
def admin_help(update, context, admin_id):
    help_message = """
Список комманд администратора:
    
/paid - список оплативших - показывает когда и кто оплачивал и (в скобках желательно писать сколько кому осталось)
/writeall - сделать всем рассылку - можно разослать какую-либо новость всем и сразу
/addpair - добавить символ пары - с помощью команды, админ может добавить в список доступных пар новую
/deletepair - удалить символ пары - с помощью команды, админ может удалить из списка доступных пар старую и ненужную,
/edittext - изменить настройки бота (реквизиты, текст сообщений бота, длительность подписки, стоимость)
/adddays - добавить дни клиенту - возможность по логину, имени, id-юзера добавить некое количество дней, к примеру в подарок или как компенсация.
/whois - узнать id_пользователя
/login - залогиниться
/addadmin - добавить администратора
/deleteadmin - удалить администратора
    """

    updater.bot.send_message(chat_id=admin_id, text=help_message)

@common_user
def user_help(update, context):
    user_id = update.message.chat.id
    db = sqlcon.Database(database_url=variables['database']['link'])
    help_message = db.get_setting('help_user_text')
    db.close()

    updater.bot.send_message(chat_id=user_id, text=help_message, parse_mode = "HTML")

@admin
def paid(update, context, admin_id):
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
<b>Всего пользователей:</b> {len(data)}
<b>Платных подписок:</b> {len(paid_users)}

Пользователи, у которых оформлена подписка:

"""+('\n').join(message_rows)

    updater.bot.send_message(chat_id=admin_id, text=message, parse_mode = 'HTML')

@admin
def writeall(update, context, admin_id):
    message = """Введите ваше сообщение для пользователей."""
    updater.bot.send_message(chat_id = admin_id, text = message)
    return WRITEALL_RESPONSE

@admin
def writeall_response(update, context, admin_id):
    db = sqlcon.Database(database_url=variables['database']['link'])
    users = db.get_users()
    users = [user[0] for user in users]
    db.close()
    res_text = update.message.text
    for user_id in users:
        try:
            updater.bot.send_message(chat_id=user_id, text=res_text, parse_mode='HTML')
            updater.bot.send_message(chat_id=admin_id,
                                     text="""Сообщение пользователю <a href="tg://user?id=%i">id%i</a> досталено.""" % (user_id,user_id),
                                     parse_mode='HTML')
        except:
            updater.bot.send_message(chat_id=admin_id,
                                     text="""Пользователь <a href="tg://user?id=%i">id%i</a> удалил бота, но останется в базе для статистики.""" % (user_id,user_id),
                                     parse_mode='HTML')
    return ConversationHandler.END

@admin
def login(update, context, admin_id):
    try:
        _, username, password = update.message.text.split(' ')
        message = f"""
Выполняю вход на сайт от имени <b>{username}</b>...
Откройте <a href="https://www.tradingview.com/">TradingView</a>, где уже выполнен вход от имени <b>{username}</b> и подтвердите авторизацию.
                        """
        updater.bot.send_message(chat_id=admin_id, text=message, parse_mode='HTML')
        value = json.dumps(selenium_get_screen.log_in(username, password))
        db = sqlcon.Database(database_url=variables['database']['link'])
        db.change_cookies(value)
        db.close()
        message = """
Пользователь успешно залогинен.
                """
        updater.bot.send_message(chat_id=admin_id, text=message, parse_mode='HTML')
    except Exception as e:
        print(e)
        message = """
Введите запрос в формате:
<pre>/login username password</pre>
                """
        updater.bot.send_message(chat_id=admin_id, text=message, parse_mode='HTML')


@admin
def addpair(update, context, admin_id):
    db = sqlcon.Database(database_url=variables['database']['link'])
    try:
        _, exchange, symbol = update.message.text.split(' ')
        db.add_pair(exchange, symbol)
        message = """
Пара <b>%s:%s</b> добавлена.
                """ % (exchange, symbol)
        updater.bot.send_message(chat_id=admin_id, text=message, parse_mode='HTML')
    except:
        message = """
Введите запрос в формате:
<pre>/addpair exchange symbol</pre>
                """
        updater.bot.send_message(chat_id=admin_id, text=message, parse_mode='HTML')
    finally:
        db.close()


def get_info(user_id):
    db = sqlcon.Database(database_url=variables['database']['link'])
    data = db.get_users()
    all_users = [row[0] for row in data]
    db.close()
    user_row = all_users.index(user_id) if user_id in all_users else None

    if user_row != None:
        if data[user_row][1] == 'paid':
            user, _, start, end = data[user_row]
            info = """
Пользователь <a href="tg://user?id=%i">id%i</a> найден в базе:
<b>Подписка оформлена</b>
%s / %s
<b>Oсталось:</b> %i %s""" % (
            user, user, date.fromtimestamp(start).isoformat(), date.fromtimestamp(end).isoformat(),
            int((end - datetime.now().timestamp()) / 86280),
            'дня' if str(int((end - datetime.now().timestamp()) / 86280))[-1] == '2' or
                     str(int((end - datetime.now().timestamp()) / 86280))[-1] == '3' or
                     str(int((end - datetime.now().timestamp()) / 86280))[-1] == '4' else 'дней')
        else:
            info = """
Пользователь <a href="tg://user?id=%i">id%i</a> найден в базе:
<b>Подписка не оформлена</b>""" % (user_id, user_id)
    else:
        info = """Пользователь <a href="tg://user?id=%i">id%i</a> не найден в базе.""" % (user_id, user_id)

    return info

@admin
def edittext(update, context, admin_id):
    message_label_request = "Выберите настройку бота или текст, который хотите отредактировать"
    db = sqlcon.Database(database_url=variables['database']['link'])
    data = db.get_settings()
    settings_label = [row[0] for row in data]
    rows, last_row = settings_label[:-(len(settings_label)%3)], settings_label[-(len(settings_label)%3):]
    rows = np.array(rows).reshape((len(settings_label)//3),3).tolist()
    rows.append(last_row)
    reply_keyboard = rows
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    updater.bot.send_message(admin_id, message_label_request, reply_markup = markup_key)
    return EDITTEXT_LABEL_REQUEST

@admin
def edittext_label_request(update, context, admin_id):
    global setting_label_to_edit
    setting_label_to_edit = update.message.text
    db = sqlcon.Database(database_url=variables['database']['link'])
    value = db.get_setting(setting_label_to_edit)
    db.close()
    message = f"""
<b>Текущее значение настройки {setting_label_to_edit}:</b>
<pre>{value}</pre>

Введите текст ниже, если хотите изменить значение или нажмите /cancel для того, чтобы оставить без изменений.
    """
    updater.bot.send_message(admin_id, message, parse_mode = 'HTML')
    return EDITTEXT_TEXT_REQUEST

@admin
def edittext_text_request(update, context, admin_id):
    global setting_label_to_edit
    value = update.message.text
    db = sqlcon.Database(database_url=variables['database']['link'])
    db.change_settings(setting_label_to_edit, value)
    db.close()

    message = f"""
    <b>Новое значение настройки {setting_label_to_edit}:</b>
    <pre>{value}</pre>
        """
    updater.bot.send_message(admin_id, message, parse_mode = 'HTML')

    return ConversationHandler.END


@admin
def whois(update, context, admin_id):
    try:
        user_id = update.message.reply_to_message.forward_from.id
        info = get_info(user_id)
        updater.bot.send_message(admin_id, info, parse_mode='HTML')
    except:
        updater.bot.send_message(admin_id,
                                 """Данную команду нужно использовать как ответ на сообщение интересующего вас пользователя."""
                                 , parse_mode='HTML')

@admin
def deletepair(update, context, admin_id):
    try:
        _, exchange, symbol = update.message.text.split(' ')
        db = sqlcon.Database(database_url=variables['database']['link'])
        db.del_pair(symbol)
        db.close()
        message = """
Пара удалена. <pre>%s:%s</pre> 
                """ % (exchange, symbol)
        updater.bot.send_message(chat_id=admin_id, text=message, parse_mode='HTML')
    except:
        message = """
Введите запрос в формате:
<pre>/deletepair exchange symbol</pre>
                """
        updater.bot.send_message(chat_id=admin_id, text=message, parse_mode='HTML')

# @admin
# def chngprice(update, context, admin_id):
#     try:
#         _, price = update.message.text.split(' ')
#         price = int(price)
#         db = sqlcon.Database(database_url=variables['database']['link'])
#         db.change_settings('price',str(price))
#         db.close()
#         message = """
# Цена подписки теперь <b>%i долларов</b>.
#                 """ % (price)
#         updater.bot.send_message(chat_id=admin_id, text=message, parse_mode='HTML')
#     except Exception as e:
#         print(e)
#         message = """
# Введите запрос в формате:
# <pre>/chngprice цена(только число)</pre>
#                 """
#         updater.bot.send_message(chat_id=admin_id, text=message, parse_mode='HTML')
#
# @admin
# def chngpayment(update, context, admin_id):
#     try:
#         payment = update.message.text.replace('/chngpayment','')
#         db = sqlcon.Database(database_url=variables['database']['link'])
#         db.change_settings('payment', payment)
#         db.close()
#         message = """
#     Реквизиты для оплаты обновлены:
#      <pre>%s/pre>.
#                 """ % (payment)
#         updater.bot.send_message(chat_id=admin_id, text=message, parse_mode='HTML')
#     except Exception as e:
#         print(e)
#         message = """
#             Введите запрос в формате:
#             <pre>/chngpayment реквизиты</pre>
#                 """
#         updater.bot.send_message(chat_id=admin_id, text=message, parse_mode='HTML')
#

@admin
def adddays(update, context, admin_id):
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
        updater.bot.send_message(chat_id=admin_id, text=message, parse_mode='HTML')
    except:
        message = """
            Введите запрос в формате:
            <pre>/adddays id_пользователя(только число) количество_дней</pre>
                """
        updater.bot.send_message(chat_id=admin_id, text=message, parse_mode='HTML')

@admin
def addadmin(update, _, admin_id):
    db = sqlcon.Database(database_url=variables['database']['link'])
    try:
        _, user_id = update.message.text.split(' ')
        db.add_admin(user_id)
        message = """
Пользователь <a href="tg://user?id=%i">id%i</a> получил права администратора.
                    """ % (user_id, user_id)
        updater.bot.send_message(chat_id=admin_id, text=message, parse_mode='HTML')
    except:
        message = """
Введите запрос в формате:
<pre>/addadmin user_id</pre>
                    """
        updater.bot.send_message(chat_id=admin_id, text=message, parse_mode='HTML')
    finally:
        db.close()


@admin
def deleteadmin(update, _, admin_id):
    db = sqlcon.Database(database_url=variables['database']['link'])
    try:
        _, user_id = update.message.text.split(' ')
        db.del_admin(user_id)
        message = """
Пользователь <a href="tg://user?id=%i">id%i</a> лишен прав администратора.
                        """ %(user_id, user_id)
        updater.bot.send_message(chat_id=admin_id, text=message, parse_mode='HTML')
    except:
        message = """
Введите запрос в формате:
<pre>/deleteadmin user_id</pre>
                        """
        updater.bot.send_message(chat_id=admin_id, text=message, parse_mode='HTML')
    finally:
        db.close()


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

    request_conversation = ConversationHandler(
        entry_points=[CommandHandler("request", req)],
        states={
        GET_SCREENSHOT: [MessageHandler(Filters.text, get_screenshot)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    pay_conversation = ConversationHandler(entry_points=[CommandHandler("pay", pay_request)],
                                           states={
                                               PAY_RESPONSE:[MessageHandler(Filters.photo, pay_response), CommandHandler('cancel', cancel)]
                                           },
                                           fallbacks=[CommandHandler('cancel', cancel)]
                                           )
    ask_conversation = ConversationHandler(entry_points=[CommandHandler("ask", ask_request)],
                                           states={
                                               ASK_RESPONSE:[CommandHandler('cancel', cancel),
                                                             MessageHandler(Filters.photo, ask_response_with_photo),
                                                             MessageHandler(Filters.text, ask_response)],
                                           },
                                           fallbacks = [CommandHandler('cancel',cancel)]
                                           )
    answer_conversation = ConversationHandler(entry_points=[CallbackQueryHandler(pay_buttons)],
                                           states={
                                               ANSWER_RESPONSE:[CommandHandler('cancel', cancel),
                                                                MessageHandler(Filters.photo, answer_response_with_photo),
                                                                MessageHandler(Filters.text, answer_response)],
                                           },
                                           fallbacks = [CommandHandler('cancel',cancel)]
                                           )
    writeall_conversation = ConversationHandler(entry_points=[CommandHandler('writeall', writeall)],
                                                              states = {
                                                                  WRITEALL_RESPONSE: [MessageHandler(Filters.text, writeall_response),CommandHandler('cancel', cancel)]
                                                              },
                                                fallbacks = [CommandHandler('cancel', cancel)]
                                                )
    edittext_conversation = ConversationHandler(
        entry_points= [CommandHandler('edittext', edittext)],
        states = {
            EDITTEXT_LABEL_REQUEST:[MessageHandler(Filters.text, edittext_label_request),CommandHandler('cancel', cancel)],
            EDITTEXT_TEXT_REQUEST: [CommandHandler('cancel', cancel), MessageHandler(Filters.text, edittext_text_request)]
        },
        fallbacks = [CommandHandler('cancel', cancel)]
    )


    dp.add_handler(pay_conversation)
    dp.add_handler(ask_conversation)
    dp.add_handler(answer_conversation)
    dp.add_handler(writeall_conversation)
    dp.add_handler(edittext_conversation)
    dp.add_handler(request_conversation)

#admin commands

    dp.add_handler(CommandHandler("admin_help", admin_help))
    dp.add_handler(CommandHandler("paid", paid))
    dp.add_handler(CommandHandler("writeall", writeall))
    dp.add_handler(CommandHandler("addpair", addpair))
    dp.add_handler(CommandHandler("deletepair", deletepair))
    dp.add_handler(CommandHandler("adddays", adddays))
    dp.add_handler(CommandHandler("whois", whois))
    dp.add_handler(CommandHandler("login", login))
    dp.add_handler(CommandHandler("addadmin", addadmin))
    dp.add_handler(CommandHandler("deleteadmin", deleteadmin))

    """
    /paid - список оплативших - показывает когда и кто оплачивал и (в скобках желательно писать сколько кому осталось)
    /writeall - сделать всем рассылку - можно разослать какую-либо новость всем и сразу
    /addpair - добавить символ пары - с помощью команды, админ может добавить в список доступных пар новую
    /deletepair - удалить символ пары - с помощью команды, админ может удалить из списка доступных пар старую и ненужную,
    /edittext - изменить настройки бота (реквизиты, текст сообщений бота, длительность подписки, стоимость)
    /adddays - добавить дни клиенту - возможность по логину, имени, id-юзера добавить некое количество дней, к примеру в подарок или как компенсация.
    /whois - узнать id_пользователя
    /login - залогиниться
    /addadmin - добавить администратора
    /deleteadmin - удалить администратора
    
    """

    updater.dispatcher.add_handler(CallbackQueryHandler(pay_buttons))

    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=variables['telegram']['token'],
                        webhook_url = 'https://murmuring-inlet-95645.herokuapp.com/' + variables['telegram']['token'])
    updater.idle()


