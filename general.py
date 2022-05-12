from telegram.ext import Updater, ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, Filters

class Commander:
    def __init__(self, token, workers,conversations):
        self.Updater = Updater(token, workers=workers, use_context=True)
        self.job_queue = self.Updater.job_queue
        self.dp = self.Updater.dispatcher
        self.conversations = conversations
        self.conversations['END']=ConversationHandler.END

    def add_commands(self,Admin, User):
        self.User = User
        self.Admin = Admin
        self.Admin.get_admins()
        self.User.admins = self.Admin.admins

    def buttons(self, update, _):
        query = update.callback_query
        query.answer()
        user_id = update.callback_query.from_user.id
        command, data_id = query.data.split(' ')
        if command == 'PAYREQACCEPTED':
            self.User.pay_request(data_id)
            return self.conversations['PAY_RESPONSE']
        elif command == 'PAYREQDECLINED':
            self.User.pay_declined(data_id)
            return self.conversations['END']

    def _add_conversations(self):
        self.admin_filter = Filters.chat()
        _ = [self.admin_filter.add_chat_ids(admin_id) for admin_id in self.Admin.admins]

        self.request_conversation = ConversationHandler(
            entry_points=[CommandHandler("request", self.User.request)],
            states={
                self.conversations['GET_SCREENSHOT']: [CommandHandler('cancel', self.User.cancel),
                                                       MessageHandler(Filters.text, self.User.request_response)]
            },
            fallbacks=[CommandHandler('cancel', self.User.cancel)]
        )

        self.pay_conversation = ConversationHandler(entry_points=[CallbackQueryHandler(self.buttons)],
                                               states={
                                                   self.conversations['PAY_RESPONSE']: [CommandHandler('cancel', self.User.cancel),
                                                                  MessageHandler(Filters.photo, self.User.pay_response),
                                                                MessageHandler(Filters.text, self.User.pay_response_text)]
                                               },
                                               fallbacks=[CommandHandler('cancel', self.User.cancel)]
                                               )
        self.ask_conversation = ConversationHandler(entry_points=[CommandHandler("ask",  self.User.ask_request)],
                                               states={
                                                   self.conversations['ASK_RESPONSE']: [CommandHandler('cancel', self.User.cancel),
                                                                  MessageHandler(Filters.photo,
                                                                                 self.User.ask_response_with_photo),
                                                                  MessageHandler(Filters.text, self.User.ask_response)],
                                               },
                                               fallbacks=[CommandHandler('cancel', self.User.cancel)]
                                               )
        self.answer_conversation = ConversationHandler(entry_points=[CommandHandler("answer", self.Admin.answer, filters=self.admin_filter)],
                                                  states={
                                                      self.conversations['ANSWER_RESPONSE']: [
                                                          CommandHandler('cancel', self.User.cancel),
                                                                        MessageHandler(Filters.photo,
                                                                                       self.Admin.answer_response_with_photo),
                                                                        MessageHandler(Filters.text, self.Admin.answer_response)],
                                                  },
                                                  fallbacks=[CommandHandler('cancel', self.User.cancel)]
                                                  )

        self.writeall_conversation = ConversationHandler(entry_points=[CommandHandler('writeall', self.Admin.writeall)],
                                                    states={
                                                        self.conversations['WRITEALL_RESPONSE']: [
                                                            MessageHandler(Filters.text, self.Admin.writeall_response),
                                                            CommandHandler('cancel', self.User.cancel)]
                                                    },
                                                    fallbacks=[CommandHandler('cancel', self.User.cancel)]
                                                    )
        self.edittext_conversation = ConversationHandler(
            entry_points=[CommandHandler('edittext', self.Admin.edittext)],
            states={
                self.conversations['EDITTEXT_LABEL_REQUEST']: [MessageHandler(Filters.text, self.Admin.edittext_label_request),
                                         CommandHandler('cancel', self.User.cancel)],
                self.conversations['EDITTEXT_TEXT_REQUEST']: [CommandHandler('cancel', self.User.cancel),
                                        MessageHandler(Filters.text, self.Admin.edittext_text_request)]
            },
            fallbacks=[CommandHandler('cancel', self.User.cancel)]
        )

    def check_updates(self,dp):
        print('Checking...')
        self.User.alarm_paid(dp)

    def _init_handlers(self):
        self._add_conversations()

        self.dp.add_handler(CommandHandler("help", self.User.help))
        self.dp.add_handler(CommandHandler("start", self.User.help))
        self.dp.add_handler(CommandHandler("pay", self.User.pay))
        self.dp.add_handler(CommandHandler("listpairs", self.User.listpairs))
        self.dp.add_handler(CommandHandler("time_help", self.User.get_time_frames))


        self.dp.add_handler(self.pay_conversation)
        self.dp.add_handler(self.ask_conversation)
        self.dp.add_handler(self.answer_conversation)
        self.dp.add_handler(self.writeall_conversation)
        self.dp.add_handler(self.edittext_conversation)
        self.dp.add_handler(self.request_conversation)

        # admin commands
        self.dp.add_handler(CommandHandler("admin_help", self.Admin.help, filters=self.admin_filter))
        self.dp.add_handler(CommandHandler("paid", self.Admin.paid, filters=self.admin_filter))
        self.dp.add_handler(CommandHandler("writeall", self.Admin.writeall, filters=self.admin_filter))
        self.dp.add_handler(CommandHandler("addpair", self.Admin.addpair, filters=self.admin_filter))
        self.dp.add_handler(CommandHandler("delpair", self.Admin.delpair, filters=self.admin_filter))
        self.dp.add_handler(CommandHandler("adddays", self.Admin.adddays, filters=self.admin_filter))
        self.dp.add_handler(CommandHandler("login", self.Admin.login, filters=self.admin_filter))
        self.dp.add_handler(CommandHandler("addadmin", self.Admin.addadmin, filters=self.admin_filter))
        self.dp.add_handler(CommandHandler("deladmin", self.Admin.deladmin, filters=self.admin_filter))
        self.dp.add_handler(CommandHandler("decline", self.Admin.decline_pay, filters=self.admin_filter))
        self.dp.add_handler(CommandHandler("accept", self.Admin.accept_pay, filters=self.admin_filter))
        self.dp.add_handler(CommandHandler("gift", self.Admin.gift_pay, filters=self.admin_filter))
        self.dp.add_handler(CommandHandler("whois", self.Admin.whois, filters=self.admin_filter))

    def _init_queue(self):
        job_queue = self.Updater.job_queue
        job_queue.run_daily(self.check_updates,self.User.alarm_time[0])
        job_queue.run_daily(self.check_updates,self.User.alarm_time[1])

    def start_polling(self):
        self._init_queue()
        self._init_handlers()
        self.Updater.start_polling(5)
        self.Updater.idle()

    def start_webhook(self, port, token, url):
        self._init_queue()
        self._init_handlers()
        self.Updater.start_webhook(listen="0.0.0.0",
                              port=port,
                              url_path=token,
                              webhook_url= url)

        self.Updater.idle()


