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
/paid - <i>список оплативших</i>
/writeall - <i>сделать всем рассылку.</i>
После нажатия команды, бот попросит ввести текст, который будет отправлен пользователям.
Текст можно форматировать используя <a href="https://core.telegram.org/api/entities">HTML разметку</a>
/addpair - <i>добавить символ пары</i>
с помощью команды, админ может добавить в список доступных пар новую
/delpair - <i>удалить символ пары</i>
с помощью команды, админ может удалить из списка доступных пар старую и ненужную,
/edittext - изменить настройки бота (реквизиты, текст сообщений бота, длительность подписки, стоимость)
/adddays - <i>добавить дни клиенту</i>
для удаления дней введите отрицательное число. 
/whois - узнать id_пользователя
/login - залогиниться
/addadmin - добавить администратора
/deladmin - удалить администратора
    """

    PAY_DECLINED = 'Оплата от пользователя <a href="tg://user?id={user_id}">id{user_id}</a> отклонена'
    PAY_ACCEPTED = 'Оплата успешно одобрена. Пользователь <a href="tg://user?id={user_id}">id{user_id}</a> получил уведомление, его подписка доступна до {date_str}'
    PAY_RECEIVED = 'Поступил запрос на оплату от пользователя <a href="tg://user?id={user_id}">id{user_id}</a>'
    PAY_BUTTONS = {'Принять оплату': 'ADMINPAYACCEPT {user_id}', 'Отклонить оплату': 'ADMINPAYDECLINE {user_id}'}
    INLINE_COMMAND = 'Неправильное использование. Пример: <code>/{command} {example}</code>'
    SCREENSHOT_CAPTION = """Скриншот оплаты от пользователя <a href="tg://user?id={user_id}">id{user_id}</a>"""
    ANSWER_REQUEST = 'Введите Ваше сообщение. Если бот, после введения Вашего ответа не подтвердит доставку, повторите операцию.'
    ANSWER_RESPONSE = 'Ответ доставлен.'
    MESSAGE_FROM_USER = """Сообщение от пользователя <a href="tg://user?id={user_id}">id{user_id}</a>
<i>"{message}"</i>
    """
    REPLY_BUTTON = {'Ответить': 'REPLYTO {user_id}'}
    ADMIN_SUCCESS = 'Команда удачно выполнена {command} {data}'
    WRITEALL_REQUEST = 'Напишите сообщение, которое хотите всем доставить. Напоминаю, что бот поддерживает <a href="https://core.telegram.org/api/entities">HTML разметку</a>. Форматирование сообщения в telegram не будет считано.'
    MESSAGE_DELIVERED = 'Сообщение доставлено <a href="tg://user?id={user_id}">id{user_id}</a>: \n <i>{message}</i>'
    MESSAGE_DELIVERY_ERROR = 'Ошибка доставки сообщения к <a href="tg://user?id={user_id}">id{user_id}</a>'
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
    EXAMPLES = {'addpair':'OANDA:USDJPY',
                'delpair':'OANDA:USDJPY',
                'addadmin':'198273982',
                'deladmin':'198273982',
                'adddays':'198273982 -20',
                'login':'admin 123456',
                'answer_request_by_id':'/answer 12345672'}

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

    RANGES = {
        "minutes": {
            "1 minute": "1",
            "3 minutes": "3",
            "5 minutes": "5",
            "15 minutes": "15",
            "30 minutes": "30",
            "45 minutes": "45"
        },
        "hours": {
            "1 hour": "60",
            "2 hours": "120",
            "3 hours": "180",
            "4 hours": "240"
        },
        "days": {
            "1 day": "1D",
            "1 week": "1W",
            "1 month": "1M"
        },
        "ranges": {
            "1 range": "1R",
            "10 range": "10R",
            "100 ranges": "100R",
            "1000 ranges": "1000R"
        }
    }