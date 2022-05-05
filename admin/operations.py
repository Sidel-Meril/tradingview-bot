import random

import interfaces.postgres as pg
from interfaces.localtelegram import operations as tg
from messages import UserMessages as Text
from messages import AdminMessages as AdminText
from datetime import datetime, date
from functools import wraps, partial
import interfaces.tradingview
import json
class Admin:
    def __init__(self, updater, db_url, conversations):
        self.Text = Text()
        self.conversations = conversations
        self.updater = updater
        self.msg = tg.Messages(updater.bot)
        self.board = tg.Keyboards()
        self.db = db_url
        self.ldb = None
        self.pairs = None
        self.user_id_to_response = None
        self.setting_label_to_edit = None


    def get_admins(self):
        self.ldb = pg.Database(self.db)
        _admins = self.ldb.get_admins()
        self.ldb.close()
        self.admins = [row[0] for row in _admins]
        return self.admins

    def simple_request(func):

        def wrapper(self,update, _,*args, **kwargs):
            admin_id = update.message.chat.id
            self.ldb = pg.Database(self.db)
            try:
                data = func(self,update, _,*args, **kwargs)
                self.msg.send_message(admin_id,AdminText.ADMIN_SUCCESS.format(command = func.__name__, data=' '.join(data)))
            except Exception as e:
                print(e)
                examp = AdminText.EXAMPLES[func.__name__]
                if '{user_id}' in examp: examp = examp.format(user_id = random.choice(self.admins))
                self.msg.send_message(admin_id,
                                      AdminText.INLINE_COMMAND.format(command = func.__name__,
                                                                      example = examp))
            finally:
                self.ldb.close()

        return wrapper

    def open_db(func):
        def wrapper(self, *args, **kwargs):
            self.ldb = pg.Database(self.db)
            data = None
            try:
                data = func(self, *args, **kwargs)
            except Exception as e:
                print('Request failed.', e)
            finally:
                self.ldb.close()
                return data

        return wrapper

    def help(self, update, _):
        user_id = update.message.chat.id
        self.updater.bot.send_message(user_id, AdminText.HELP.format(user_id=user_id), parse_mode='HTML')

    @simple_request
    def whois(self, update, _, example = ''):
        admin_id = update.message.chat.id
        user_id = update.message.reply_to_message.forward_from.id
        info = self.ldb.get_users_id()
        if user_id in self.admins:
            type_user = 'администратор'
        elif user_id in info:
            type_user = 'пользователь зарегистрирован ботом'
        else:
            type_user = 'пользователь не использовал бота'
        self.msg.send_message(admin_id, f"id <code>{user_id}</code> ({type_user})")
        return " ", " "

    @simple_request
    def delpair(self,  update, _, example='OANDA USDJPY'):
        _, symbol = update.message.text.split(' ')
        self.ldb.del_pair(symbol)

        return ' ', symbol

    @simple_request
    def deladmin(self, update, _):
        _, user_id = update.message.text.split(' ')
        self.ldb.del_admin(user_id)
        return (user_id)

    @simple_request
    def addadmin(self, update, _):
        _, user_id = update.message.text.split(' ')
        self.ldb.add_admin(int(user_id))
        return str(user_id), ' '

    @simple_request
    def addpair(self, update, _):
        _, exchange, symbol = update.message.text.split(' ')
        self.ldb.add_pair(exchange, symbol)
        return exchange, symbol

    @simple_request
    def adddays(self, update, _):
        _, user_id, days = update.message.text.split(' ')
        _days = int(days) * 86280
        data = self.ldb.get_users()
        user_index = [row[0] for row in data].index(int(user_id))
        self.ldb.edit_user_end_by_id(int(user_id), data[user_index][3] + _days)
        return user_id, days

    @simple_request
    def deladmin(self, update, _):
        _, user_id = update.message.text.split(' ')
        self.ldb.del_admin(int(user_id))
        return str(user_id), ' '

    def edittext(self, update, _):
        admin_id = update.message.chat.id
        self.ldb = pg.Database(self.db)
        data = self.ldb.get_settings()
        settings_label = [row[0] for row in data]
        markup_key = self.board.inline_keyboard_markup(settings_label)
        self.msg.send_message(admin_id, AdminText.EDIT_TEXT, markup=markup_key)

        return self.conversations['EDITTEXT_LABEL_REQUEST']

    @open_db
    def accept(self, user_id):
        self.ldb = pg.Database(self.db)
        price, duration, payment_data = int(self.ldb.get_setting('price')), \
                                        int(self.ldb.get_setting('term')), \
                                        self.ldb.get_setting('payment')
        _duration = duration * 86280
        self.ldb.edit_user_by_id(int(user_id), 'paid', int(datetime.now().timestamp()), int(datetime.now().timestamp()) + _duration)
        self.ldb.close()
        self.msg.send_message(user_id,
                              self.Text.PAY_ACCEPTED.format(
                                  date_str = date.fromtimestamp(int(datetime.now().timestamp()) + _duration).isoformat()
                              )
                              )
        for admin_id in self.admins:
            self.msg.send_message(admin_id,
                                     AdminText.PAY_ACCEPTED.format(user_id=user_id,
                                                                   date_str = date.fromtimestamp(int(datetime.now().timestamp()) + _duration).isoformat()))

    @open_db
    def decline(self, user_id):
        self.msg.send_message(user_id,
                                 self.Text.PAY_DECLINED)
        for admin_id in self.admins:
            self.msg.send_message(admin_id,
                                     AdminText.PAY_DECLINED.format(user_id=user_id))

    @open_db
    def accept(self, user_id):
        self.ldb = pg.Database(self.db)
        price, duration, payment_data = int(self.ldb.get_setting('price')), \
                                        int(self.ldb.get_setting('term')), \
                                        self.ldb.get_setting('payment')
        _duration = duration * 86280
        self.ldb.edit_user_by_id(int(user_id), 'paid', int(datetime.now().timestamp()), int(datetime.now().timestamp()) + _duration)
        self.ldb.close()
        self.msg.send_message(user_id,
                              self.Text.PAY_ACCEPTED.format(
                                  date_str = date.fromtimestamp(int(datetime.now().timestamp()) + _duration).isoformat()
                              )
                              )
        for admin_id in self.admins:
            self.msg.send_message(admin_id,
                                     AdminText.PAY_ACCEPTED.format(user_id=user_id,
                                                                   date_str = date.fromtimestamp(int(datetime.now().timestamp()) + _duration).isoformat()))

    @open_db
    def gift(self, user_id, gift):
        self.ldb = pg.Database(self.db)
        price, _, payment_data = int(self.ldb.get_setting('price')), \
                                        int(self.ldb.get_setting('term')), \
                                        self.ldb.get_setting('payment')
        _duration = int(gift) * 86280
        self.ldb.edit_user_by_id(int(user_id), 'paid', int(datetime.now().timestamp()), int(datetime.now().timestamp()) + _duration)
        self.ldb.close()
        self.msg.send_message(user_id,
                              AdminText.PAY_GIFTED.format(days = gift,
                                  date_str = date.fromtimestamp(int(datetime.now().timestamp()) + _duration).isoformat()
                              )
                              )
        for admin_id in self.admins:
            self.msg.send_message(admin_id,
                                     AdminText.PAY_ACCEPTED.format(user_id=user_id,
                                                                   date_str = date.fromtimestamp(int(datetime.now().timestamp()) + _duration).isoformat()))

    def accept_pay(self, update, _):
        _, user_id = update.message.text.split(' ')
        self.accept(user_id)

    def decline_pay(self, update, _):
        _, user_id = update.message.text.split(' ')
        self.decline(user_id)

    def gift_pay(self, update, _):
        _, user_id, days = update.message.text.split(' ')
        self.gift(user_id, days)


    @open_db
    def get_paid(self, admin_id):
        data = self.ldb.get_users()
        paid_users = list(filter(lambda x: x != None, [row if row[1] == 'paid' else None for row in data]))
        message_rows = ["""
<a href="tg://user?id=%i">пользователь</a> <code>%i</code>:
<b>%s / %s</b>
<b>Oсталось</b>: %i %s

        """
                        % (user, user, date.fromtimestamp(start).isoformat(), date.fromtimestamp(end).isoformat(),
                           int((end - datetime.now().timestamp()) / 86280),
                           'дня' if str(int((end - datetime.now().timestamp()) / 86280))[-1] == '2' or
                                    str(int((end - datetime.now().timestamp()) / 86280))[-1] == '3' or
                                    str(int((end - datetime.now().timestamp()) / 86280))[-1] == '4' else 'дней')
                        for user, _, start, end in paid_users]
        message = f"""
<b>Статистика использования бота</b>
<b>Всего пользователей:</b> {len(data)}
<b>Платных подписок:</b> {len(paid_users)}

<b>Нажмите на id пользователя, чтобы скопировать его.</b>

Пользователи, у которых оформлена подписка:

    """ + ('\n').join(message_rows)

        self.msg.send_message(admin_id, message)

    def paid(self, update, _):
        self.get_paid(update.message.chat.id)

    def writeall(self, update, _):
        admin_id = update.message.chat.id
        self.msg.send_message(admin_id, AdminText.WRITEALL_REQUEST)
        return self.conversations['WRITEALL_RESPONSE']

    def writeall_response(self,update, _):
        admin_id = update.message.chat.id
        self.ldb = pg.Database(self.db)
        users = self.ldb.get_users_id()
        self.ldb.close()
        res_text = update.message.text
        for user_id in users:
            try:
                self.msg.send_message(user_id[0], res_text)
                self.msg.send_message(admin_id,
                                         AdminText.MESSAGE_DELIVERED.format(user_id = user_id[0]))
            except Exception as e:
                print(e)
                self.msg.send_message(admin_id,
                                         AdminText.MESSAGE_DELIVERY_ERROR.format(user_id=user_id[0], error = e))
            finally:
                self.msg.send_message(admin_id, AdminText.ADMIN_SUCCESS.format(command = 'writeall', data=''))
        return self.conversations['END']

    def edittext_label_request(self,update, _):
        admin_id = update.message.chat.id
        self.setting_label_to_edit = update.message.text
        self.ldb = pg.Database(self.db)
        value = self.ldb.get_setting(self.setting_label_to_edit)
        self.ldb.close()
        self.msg.send_message(admin_id, AdminText.CURRENT_VALUE.format(setting_label = self.setting_label_to_edit,
                                                                          value = value), parse_mode='Markdown')
        return self.conversations['EDITTEXT_TEXT_REQUEST']


    def edittext_text_request(self,update, _):
        value = update.message.text
        admin_id = update.message.chat.id
        self.ldb = pg.Database(self.db)
        self.ldb.change_settings(self.setting_label_to_edit, value)
        self.ldb.close()
        self.updater.bot.send_message(admin_id, AdminText.TEXT_EDITED.format(setting_label = self.setting_label_to_edit, value = value))
        self.Text = Text()
        return self.conversations['END']

    @simple_request
    def login(self,update,_, example='Admin 123@_45'):
        _, username, password = update.message.text.split(' ')

        self.msg.send_message(update.message.chat.id, AdminText.LOGIN.format(username=username))
        value = json.dumps(interfaces.tradingview.log_in(username, password))
        self.ldb = pg.Database(self.db)
        self.ldb.change_cookies(value)
        self.ldb.close()
        self.msg.send_message(update.message.chat.id, AdminText.LOGIN_SUCCESS)

    def answer_request(self, user_id):
        self.msg.send_message(user_id, AdminText.ANSWER_REQUEST.format(user_id=self.user_id_to_response))

    def answer(self, update, _):
        primary_admin_id = update.message.chat.id
        try:
            _, user_id = update.message.text.split(' ')
            self.user_id_to_response = user_id
            for admin_id in self.admins:
                self.msg.send_message(admin_id, AdminText.ANSWER_REQUEST.format(user_id=self.user_id_to_response))
        except:
            self.msg.send_message(primary_admin_id,
                                  AdminText.INLINE_COMMAND.format(command='answer',
                                                                  example=
                                                                  AdminText.EXAMPLES['answer'].
                                                                  format(user_id = random.choice(self.admins))))
        return self.conversations['ANSWER_RESPONSE']

    def answer_response(self, update, _):
        admin_id = update.message.chat.id
        answer = update.message.text
        try:
            self.msg.send_message(self.user_id_to_response, self.Text.MESSAGE_RECEIVED.format(message=answer))
            for admin_id in self.admins:
                self.msg.send_message(admin_id, AdminText.MESSAGE_DELIVERED.format(user_id=self.user_id_to_response, message=answer))
        except Exception as e:
            print(e)
            self.msg.send_message(admin_id, AdminText.MESSAGE_DELIVERY_ERROR.format(user_id=self.user_id_to_response))

        self.user_id_to_response = None
        return self.conversations['END']

    def answer_response_with_photo(self, update, _):
        admin_id = update.message.chat.id

        try:
            file_id = update.message.photo[-1].file_id
            answer = update.message.caption
        except:
            file_id = update.message.reply_to_message.photo[-1].file_id
            answer = update.message.reply_to_message.caption

        try:
            self.msg.send_photo(self.user_id_to_response, file_id,
                                   self.Text.MESSAGE_RECEIVED.format(message = answer))
            self.msg.send_message(admin_id, AdminText.MESSAGE_DELIVERED.format(self.user_id_to_response))

        except:
            self.msg.send_message(admin_id, AdminText.MESSAGE_DELIVERY_ERROR.format(self.user_id_to_response))

        self.user_id_to_response = None
        return self.conversations['END']

