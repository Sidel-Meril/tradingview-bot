import interfaces.postgres as pg
import interfaces.tradingview
from interfaces.localtelegram import operations as tg
from messages import UserMessages as Text
from messages import AdminMessages as AdminText
from datetime import datetime, date
import json
import interfaces.tradingview as tradingview

class User:
    def __init__(self, updater, db_url, conversations):
        self.Text = Text()
        self.conversations = conversations
        self.updater = updater
        self.msg = tg.Messages(updater.bot)
        self.board = tg.Keyboards()
        self.db = db_url
        self.ldb = None
        self.admins = None
        self.pairs = None
    def _open_db(func):
        def wrapper(self,update, _, *args, **kwargs):
            admin_id = update.message.chat.id
            self.ldb = pg.Database(self.db)
            data = None
            try:
                data = func(self, *args, **kwargs)
            except:
                self.msg.send_message(admin_id,
                                      AdminText.INLINE_COMMAND.format(command = func.__name__, example = ' '))
            finally:
                self.ldb.close()
                return data

        return wrapper

    def _get_user(func):
        def check_user(self, update, _, *args, **kwargs):
            self.ldb = pg.Database(self.db)
            try:
                user_data = self.ldb.get_user_by_id(update.message.chat.id)[0]
                if self.pairs == None:
                    self.pairs = self.ldb.get_pairs()
            except:
                self.ldb.add_user(update.message.chat.id, plan='free')
                user_data = self.ldb.get_user_by_id(update.message.chat.id)[0]
            finally:
                self.ldb.close()
                self.ldb = None

                res = func(self, update, _, user_data = user_data, *args, **kwargs)
                return res
        return check_user


    def access_denied(self, user_id):
        self.msg.send_message(user_id, self.Text.ACCESS_DENIED)

    @_get_user
    def start(self, update, _, user_data):
        self.help(update, _, user_data)

    @_get_user
    def help(self, update, _, user_data):
        user_id = update.message.chat.id
        self.msg.send_message(user_id, self.Text.HELP(user_data[1]))

    @_get_user
    def pay(self, update, _, user_data):
        user_id = update.message.chat.id
        if user_data[1] == 'paid':
            self.msg.send_message(user_id, self.Text.PAY_PAID)
        else:
            self.ldb = pg.Database(self.db)
            price, duration, payment_data = int(self.ldb.get_setting('price')), \
                                            int(self.ldb.get_setting('term')), \
                                            self.ldb.get_setting('payment')
            _duration = duration * 86280
            self.ldb.close()
            date_start = int(datetime.now().timestamp())
            date_end = int(datetime.now().timestamp()) + _duration
            date_start, date_end = date.fromtimestamp(date_start).isoformat(), date.fromtimestamp(date_end).isoformat()

            buttons = self.Text.format_buttons(self.Text.PAY_BUTTONS, user_id=user_id)
            keyboard = self.board.inline_keyboard_button(buttons)
            self.msg.send_message(user_id, self.Text.PAY.format(
                price = price,
                payment_data = payment_data,
                duration = duration,
                date_start = date_start,
                date_end = date_end
            ), markup= keyboard)

    def pay_request(self, user_id):
        self.msg.send_message(user_id, self.Text.GET_SCREENSHOT)

    def pay_response(self, update, _):
        user_id = update.message.chat.id
        print(user_id)
        keyboard = self.Text.format_buttons(AdminText.PAY_BUTTONS, user_id)
        reply_markup = self.board.inline_keyboard_button(keyboard)
        try:
            for admin_id in self.admins:
                self.msg.send_photo(admin_id, update.message.photo[-1].file_id,
                                   AdminText.PAY_RECEIVED.format(user_id=user_id), markup=reply_markup)
                print(f'Screenshot send to {admin_id}')
            self.msg.send_message(user_id, self.Text.PAY_RECEIVED)
        except Exception as e:
            print(e)
            self.msg.send_message(user_id, self.Text.ERROR)
        return self.conversations['END']

    def pay_response_text(self, update, _):
        user_id = update.message.chat.id
        try:
            self.msg.send_message(user_id, self.Text.TEXT_NOT_ALLOWED)
            self.msg.send_message(user_id, self.Text.REQUEST)
        except Exception as e:
            print(e)
            self.msg.send_message(user_id, self.Text.ERROR)
        return self.conversations['PAY_RESPONSE']

    def pay_declined(self, user_id):
        self.msg.send_message(user_id, self.Text.PAY_POSTPONED)

    def cancel(self, update, _):
        user_id = update.message.chat.id
        self.msg.send_message(user_id, self.Text.CANCELED)
        return self.conversations['END']

    @_get_user
    def request(self, update, _, user_data):
        if datetime.now().timestamp() > user_data[3]:
            self.ldb = pg.Database(self.db)
            self.ldb.edit_user_by_id(update.message.chat.id, 'free', 0, 0)
            self.ldb.close()
            self.msg.send_message(update.message.chat.id,
                                  self.Text.SUBSCRIBE_EXPIRED)
            return self.conversations['END']
        else:
            self.msg.send_message(update.message.chat.id, self.Text.REQUEST)
            return self.conversations['GET_SCREENSHOT']

    def tets(self, update, _):
        user_id = update.message.chat.id
        self.msg.send_message(user_id, user_id)

    def request_response(self, update, _):
        user_id = update.message.chat.id
        self.ldb = pg.Database(self.db)
        data = self.ldb.get_cookies()
        self.ldb.close()
        cookies = json.loads(data)

        try:
            pair, timeframe = update.message.text.split(' ')
            self.msg.send_message(user_id, self.Text.REQUEST_RECEIVED.format(data=f"{pair} {timeframe}"))
            pair_index = [row[0] for row in self.pairs].index(pair)
            pair_exchange = self.pairs[pair_index][1]
            screenshot = tradingview.get_screenshot(f"{pair_exchange}:{pair}", timeframe, cookies)
            self.msg.send_photo(user_id, screenshot)

        except Exception as e:
            print(e)
            self.msg.send_message(user_id,self.Text.ERROR)

        return self.conversations['END']

    def listpairs(self, update, _):
        user_id = update.message.chat.id
        message_rows = [f"""<pre>{exchange}:{symbol}</pre>""" for symbol, exchange in self.pairs]
        self.msg.send_message(user_id, self.Text.LISTPAIRS_TITLE.format(pairs_list='\n'.join(message_rows)))

    @_get_user
    def ask_request(self, update, _, user_data):
        user_id = update.message.chat.id
        self.msg.send_message(user_id, self.Text.ASK_REQUEST)
        return self.conversations['ASK_RESPONSE']


    def ask_response(self, update, _):
        user_id = update.message.chat.id
        user_message = update.message.text
        keyboard = self.board.inline_keyboard_button(self.Text.format_buttons(AdminText.REPLY_BUTTON, user_id))

        for admin_id in self.admins:
            self.msg.send_message(admin_id, AdminText.MESSAGE_FROM_USER.format(user_id = user_id, message = user_message),
                                  markup=keyboard)
        self.msg.send_message(user_id, self.Text.ASK_RESPONSE)
        return self.conversations['END']


    def ask_response_with_photo(self, update, _):
        user_id = update.message.chat.id
        user_message = update.message.text
        keyboard = self.board.inline_keyboard_button(self.Text.format_buttons(AdminText.REPLY_BUTTON, user_id))

        try:
            file_id = update.message.photo[-1].file_id
            user_message = update.message.caption
        except:
            file_id = update.message.reply_to_message.photo[-1].file_id
            user_message = update.message.reply_to_message.caption

        for admin_id in self.admin:
            self.msg.send_photo(admin_id, file_id, AdminText.MESSAGE_FROM_USER.format(user_id = user_id, message = user_message),
                                   markup=keyboard)
        self.msg.send_message(user_id, self.Text.ASK_RESPONSE)
        return self.conversations['END']

    def get_time_frames(self, update, _):
        user_id = update.message.chat.id
        self.msg.send_message(user_id, AdminText.TIMES)

