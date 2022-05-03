from interfaces.postgres import Database
from interfaces.postgres.operations import Database
from conf.config import LocalConfig

class UserMessages:

    def format_buttons(self, buttons, user_id):
        for key in buttons.keys():
            buttons[key] = buttons[key].format(user_id = user_id)
        return buttons

    def HELP(self, user_type):
        if user_type == "paid":
            return self.USER__PAID
        else:
            return self.USER__UNPAID

    def __init__(self):
        DB = Database(LocalConfig.DATABASE_URL)

        self.USER__PAID = DB.get_setting('USER__PAID')
        self.USER__UNPAID = DB.get_setting('USER__UNPAID')

        self.STOP_MESSAGE = DB.get_setting('STOP_MESSAGE') #'STOPED'
        self.ACCESS_DENIED = DB.get_setting('ACCESS_DENIED')#'ACCESS_DENIED'

        self.PAY = DB.get_setting('PAY')
        # """PAY
        # PRICE: {price}
        # PAYMENT DATA: {payment_data}
        # DURATION: {duration}
        # SUBSCRIPTION WILL BE AVALIABLE FROM {date_start} TO {date_end}
        # """

        self.PAY_PAID = DB.get_setting('PAY_PAID')#'PAID'
        self.GET_SCREENSHOT = DB.get_setting('GET_SCREENSHOT')#'GET_SCREENSHOT'
        self.PAY_DECLINED = DB.get_setting('PAY_DECLINED')
        self.PAY_RECEIVED = DB.get_setting('PAY_RECEIVED')
        self.PAY_POSTPONED = DB.get_setting('PAY_POSTPONED')
        self.TEXT_NOT_ALLOWED = DB.get_setting('TEXT_NOT_ALLOWED')
        self.PAY_ACCEPTED = DB.get_setting('PAY_ACCEPTED')
        self.PAY_BUTTONS = {DB.get_setting('PAY_BUTTON_ACCEPT'): 'PAYREQACCEPTED {user_id}',
                       DB.get_setting('PAY_BUTTON_DECLINE'): 'PAYREQDECLINED {user_id}'}
        self.SUBSCRIBE_EXPIRED = DB.get_setting('SUBSCRIBE_EXPIRED')

        self.REQUEST = DB.get_setting('REQUEST')
        self.REQUEST_RECEIVED = DB.get_setting('REQUEST_RECEIVED')

        self.LISTPAIRS_TITLE = DB.get_setting('LISTPAIRS_TITLE')

        self.ASK_REQUEST = DB.get_setting('ASK_REQUEST')
        self.ASK_RESPONSE = DB.get_setting('ASK_RESPONSE')

        self.MESSAGE_RECEIVED = DB.get_setting('MESSAGE_RECEIVED')

        self.ERROR = DB.get_setting('ERROR')
        self.CANCELED = DB.get_setting('CANCELED')

        self.ANSWER = DB.get_setting('ANSWER')
        DB.close()

class AdminMessages:
    HELP = """
<b>Полный набор команд для администратора бота. </b>
Ваш id - <a href="tg://user?id={user_id}">{user_id}</a>
Для получения пользовательских команд нажмите /help

/paid - <i>список оплативших</i>

/writeall - <i>сделать всем рассылку.</i>
После нажатия команды, бот попросит ввести текст, который будет отправлен пользователям.
Текст можно форматировать используя <a href="https://core.telegram.org/api/entities">HTML разметку</a>

/addpair - <i>добавить символ пары</i>
с помощью команды, админ может добавить в список доступных пар новую
<code>/addpair EXCHANGE_TEST SYMBOL_TEST</code> - добавит пару с именем SYMBOL_TEST

/delpair - <i>удалить символ пары</i>
с помощью команды, админ может удалить из списка доступных пар старую и ненужную,
<code>/delpair SYMBOL_TEST</code> - ударит пару с именем SYMBOL_TEST

/edittext - <i>изменить настройки бота</i>
Редактирование реквизитов, текстов сообщений бота, выводимых пользователю; длительность подписки, стоимость.

/adddays - <i>добавить дни клиенту</i>
для удаления дней введите отрицательное число. 
Попробуйте для своего <a href="tg://user?id={user_id}">id пользователя</a>:
 <code>/adddays {user_id} -1</code> - уменьшит количество дней Вашей подписки на 1 день.

/login - <i>залогиниться</i>
Пример использования:
 <code>/login tradingview_login tradingview_password</code>
Скопируйте эту команду и подставьте значения. <b>После появления сообщения бота о начале авторизации у вас будет 60 секунд, чтобы подтвердить авторизацию в браузере, в противном случае авторизация завершится неудачно и процесс придется повторить снова!</b>
 
/addadmin - <i>добавить администратора</i>
Пример использования с Вашим <a href="tg://user?id={user_id}">id пользователя</a>:
 <code>/addadmin {user_id}</code>
 - бот ответит, что в вашем сообщении ошибка 
 
/deladmin - <i>удалить администратора</i>
Пример использования с Вашим <a href="tg://user?id={user_id}">id пользователя</a>:
 <b> ! - не используйте пример, если не хотите потерять доступ к админпанели </b>
 <code>/deladmin {user_id}</code>
 
/answer - <i>ответить пользователю по id</i>
Пример использования с Вашим <a href="tg://user?id={user_id}">id пользователя</a>:
 <code>/answer {user_id}</code> - Вы ответите самому себе от лица администратора.
 
/whois - <i>узнать id пользователя</i>
Бот указывает id пользователя при пересылке сообщений администратору, однако Вы можете ответить на пересланное сообщение от пользователя в чат бота данной командой и получить его id:
1. Перешлите любое сообщение пользователя боту (бот не ответит на пересланное сообщение)
2. Ответьте на это сообщение командой <code>/whois</code>
    """

    PAY_DECLINED = 'Оплата от <a href="tg://user?id={user_id}">пользователя</a> <code>{user_id}</code> отклонена'
    PAY_ACCEPTED = 'Оплата успешно одобрена. Пользователь <a href="tg://user?id={user_id}">пользователя</a> <code>{user_id}</code> получил уведомление, его подписка доступна до {date_str}'
    PAY_RECEIVED = 'Поступил запрос на оплату от пользователя <a href="tg://user?id={user_id}">пользователя</a> <code>{user_id}</code>'
    PAY_BUTTONS = {'Принять оплату': 'ADMINPAYACCEPT {user_id}', 'Отклонить оплату': 'ADMINPAYDECLINE {user_id}'}
    INLINE_COMMAND = 'Неправильное использование. Пример: <code>/{command} {example}</code>'
    SCREENSHOT_CAPTION = """Скриншот оплаты от <a href="tg://user?id={user_id}">пользователя</a> <code>{user_id}</code>"""
    ANSWER_REQUEST = 'Введите Ваше сообщение <a href="tg://user?id={user_id}">пользователю</a> <code>{user_id}</code>. <b>Внимание! Если бот, после введения Вашего ответа, не подтвердит доставку, повторите операцию.</b>'
    ANSWER_RESPONSE = 'Ответ доставлен.'
    MESSAGE_FROM_USER = """Сообщение от пользователя <a href="tg://user?id={user_id}">пользователя</a> <code>{user_id}</code>
<i>"{message}"</i>
    """
    REPLY_BUTTON = {'Ответить': 'REPLYTO {user_id}'}
    ADMIN_SUCCESS = 'Команда удачно выполнена {command} {data}'
    WRITEALL_REQUEST = 'Напишите сообщение, которое хотите всем доставить. Напоминаю, что бот поддерживает <a href="https://core.telegram.org/api/entities">HTML разметку</a>. Форматирование сообщения в telegram не будет считано.'
    MESSAGE_DELIVERED = 'Сообщение доставлено <a href="tg://user?id={user_id}">id{user_id}</a>: \n <i>{message}</i>'
    MESSAGE_DELIVERY_ERROR = 'Ошибка доставки сообщения к <a href="tg://user?id={user_id}">id{user_id}</a>. Ошибка: {error}'
    LOGIN = """
Выполняю вход на сайт от имени <b>{username}</b>...
Откройте <a href="https://www.tradingview.com/">TradingView</a>, где уже выполнен вход от имени <b>{username}</b> и подтвердите авторизацию.
                                """
    LOGIN_SUCCESS = "Процесс авторизиции закончен."
    EDIT_TEXT = "Выберите настройку бота или текст, который хотите отредактировать. Бот может не оправить текущее значение настройки в ответ на это сообщение."
    TEXT_EDITED ="""
<b>Новое значение настройки {setting_label}:</b>
{value}
            """
    CURRENT_VALUE ="""
Значение настройки {setting_label}:
{value}

Введите текст ниже, если хотите изменить значение или нажмите /cancel для того, чтобы оставить без изменений.
            """
    EXAMPLES = {'addpair':'EXCHANGE SYMBOL',
                'delpair':'SYMBOL',
                'addadmin':'{user_id}',
                'deladmin':'{user_id}',
                'adddays':'{user_id} -20',
                'login':'admin 123456',
                'answer':'{user_id}',
                'whois': ' '}

    TIMEFRAME = "❌ Неправильный таймфрейм/рендж. Ознакомиться со справкой по таймфреймам/ренджам 👉/timeframe"
    SYMBOL = "❌ Неправильно указанная пара. Ознакомиться со списком пар 👉/listpairs"
    TIMES ="""
<b>Минуты:</b>
1 минута - <code>1</code>
3 минуты - <code>3</code>
5 минут -  <code>5</code>
15 минут - <code>15</code>
30 минут - <code>30</code>
45 минут - <code>45</code>
    
<b>Часы:</b>
1 час - <code>60</code>
2 часов -  <code>120</code>
3 часов -  <code>180</code>
4 часов -  <code>240</code>

<b>Дни:</b>
1 день -  <code>1D</code>
1 неделя -  <code>1W</code>
1 месяц -  <code>1M</code>

<b>Ренджи:</b>
1 range - <code>1R</code>
10 range - <code>10R</code>
100 ranges - <code>100R</code>
1000 ranges - <code>1000R</code>
    
<b>Попробуйте!</b>
Нажмите /request, а затем введите <code>NZDUSD 10R</code>.

"""

    RANGES = [
    "3",
    "5",
    "15",
    "30",
    "45",
    "60",
    "120",
    "180",
    "240",
    "1D",
    "1W",
    "1M",
    "1R",
    "10R",
    "100R",
    "1000R"
    ]