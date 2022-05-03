from general import Commander
import user
import admin
import conf

if __name__ == '__main__':
    config = conf.LocalConfig()
    bot = Commander(config.TOKEN, config.WORKERS, config.CONVERSATION_POINTS)
    admin_commands = admin.Admin(bot.Updater, config.DATABASE_URL, bot.conversations)
    user_commands = user.User(bot.Updater, config.DATABASE_URL, bot.conversations)
    bot.add_commands(admin_commands,user_commands)
    bot.start_webhook(config.PORT, config.TOKEN, config.HEROKU_PROJECT_LINK)