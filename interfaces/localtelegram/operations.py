from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup
import numpy as np
from telegram.ext.dispatcher import run_async

class Keyboards:
    def inline_keyboard_markup(self, keys):
        if len(keys)>=3:
            rows, last_row = keys[:-(len(keys) % 3)], keys[-(len(keys) % 3):]
            rows = np.array(rows).reshape((len(keys) // 3), 3).tolist()
            rows.append(last_row)
        else:
            rows = [keys]
        reply_keyboard = rows
        markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        return markup_key

    def inline_keyboard_button(self, buttons):
        rows = [[InlineKeyboardButton(button, callback_data=callback_data)
                 for button, callback_data in buttons.items()]]
        reply_markup = InlineKeyboardMarkup(rows)
        return reply_markup

from telegram.ext import Updater

class Messages:
    def __init__(self, bot):
        self.bot = bot

    @run_async
    def send_message(self, user_id, message_text, markup=None, parse_mode='HTML'):
        self.bot.send_message(chat_id=user_id, text=message_text, parse_mode=parse_mode, reply_markup = markup)

    @run_async
    def send_photo(self, user_id, photo, message_text = ' ', markup=None):
        self.bot.send_photo(chat_id=user_id, photo = photo, caption=message_text, parse_mode='HTML', reply_markup = markup)