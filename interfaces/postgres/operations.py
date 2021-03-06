import psycopg2

class Database:
    def _conn(func):
        def wrapper(self, *args, **kwargs):
            self.cur = self.conn.cursor()
            result = func(self, *args, **kwargs)
            self.cur.close()
            return result
        return wrapper

    def __init__(self, database_url):
        try:
            self.conn = psycopg2.connect(database_url, sslmode = 'require' )
        except Exception as e:
            print(f"Error occurred when connecting to database: {e}")



    @_conn
    def create_tables(self, table, param):
        # Create user table
        query="""CREATE TABLE %s(
%s
        )""" %(table, '\n'.join(param))
        self.cur.execute(query)
        self.conn.commit()

    @_conn
    def get_user_by_id(self, user_id):
        query = """SELECT * FROM users WHERE user_id = %i;
        """ % (user_id)
        self.cur.execute(query)
        data = self.cur.fetchall()
        return data


    @_conn
    def add_cookies(self, value, id=1):
        query = """INSERT INTO cookies(id, value) VALUES ('%s', '%s')
        """ % (id, value)
        self.cur.execute(query)
        self.conn.commit()

    @_conn
    def change_cookies(self, value, id=1):
        query = """UPDATE cookies
            SET value = '%s' WHERE id = '%i';
            """ % (value, id)
        self.cur.execute(query)
        self.conn.commit()

    @_conn
    def get_cookies(self):
        query = """SELECT * FROM cookies
            """
        self.cur.execute(query)
        value = self.cur.fetchall()
        return value[0][1]

    @_conn
    def add_settings(self, setting_name, value):
        query = """INSERT INTO bot_settings(setting_name, value) VALUES ('%s', '%s')
        """ % (setting_name, value)
        self.cur.execute(query)
        self.conn.commit()

    @_conn
    def change_settings(self, setting_name, value):
        query = """UPDATE bot_settings
        SET value = '%s' WHERE setting_name = '%s';
        """ % (value, setting_name)
        self.cur.execute(query)
        self.conn.commit()

    @_conn
    def get_setting(self, setting_name):
        query = """SELECT * FROM bot_settings WHERE setting_name = '%s'
        """ % (setting_name)
        self.cur.execute(query)
        value = self.cur.fetchall()
        return value[0][1]

    @_conn
    def another_query(self):
        query = """DROP TABLE users;
        """
        # query="""ALTER TABLE sources DROP CONSTRAINT ix_sources;
        # """
        # query = """SELECT name, current_setting(name)
        # FROM pg_settings;
        #         """
        # query = """ALTER SYSTEM SET block_size = '1073741824';
        # """
        self.cur.execute(query)
        # result = self.cur.fetchall()
        # print(result)
        self.conn.commit()

    @_conn
    def edit_user_by_id(self, user_id, plan, start, expires):
        query = """UPDATE users
        SET plan = '%s' WHERE user_id = %i;
        """ % (plan, user_id)

        self.cur.execute(query)

        query = """UPDATE users
        SET start = %i WHERE user_id = %i;
        """ % (start, user_id)

        self.cur.execute(query)

        query = """UPDATE users
        SET expired = %i WHERE user_id = %i;
        """ % (expires, user_id)

        self.cur.execute(query)
        self.conn.commit()

    @_conn
    def edit_user_end_by_id(self, user_id, expires):
        query = """UPDATE users
        SET expired = %i WHERE user_id = %i;
        """ % (expires, user_id)

        self.cur.execute(query)
        self.conn.commit()

    @_conn
    def add_user(self, user_id, plan):
        query = """INSERT INTO users (user_id, plan) VALUES (%i, '%s')
        """ %(user_id, plan)

        self.cur.execute(query)
        self.conn.commit()

    @_conn
    def add_pair(self, exchange, symbol):
        query = """INSERT INTO sources (EXCHANGE, SYMBOL) VALUES ('%s', '%s')
        """ %(exchange, symbol)

        self.cur.execute(query)
        self.conn.commit()

    @_conn
    def del_pair(self, symbol):
        query="""DELETE FROM sources WHERE symbol = '%s';
        """ %symbol

        self.cur.execute(query)
        self.conn.commit()

    @_conn
    def get_users(self):

        query = """SELECT * FROM users
        """

        self.cur.execute(query)
        result = self.cur.fetchall()

        return result

    @_conn
    def get_users_id(self):

        query = """SELECT user_id FROM users
        """

        self.cur.execute(query)
        result = self.cur.fetchall()

        return result


    @_conn
    def get_pairs(self):

        query = """SELECT * FROM Sources
        """

        self.cur.execute(query)
        result = self.cur.fetchall()

        return result

    @_conn
    def get_settings(self):

        query = """SELECT * FROM bot_settings
        """

        self.cur.execute(query)
        result = self.cur.fetchall()

        return result

    @_conn
    def get_admins(self):

        query = """SELECT * FROM admins
        """

        self.cur.execute(query)
        result = self.cur.fetchall()

        return result

    @_conn
    def add_admin(self, admin):

        query = """INSERT INTO admins(admin_id) VALUES ('%i')
        """ % (admin)

        self.cur.execute(query)
        self.conn.commit()

    @_conn
    def del_admin(self, admin):

        query="""DELETE FROM admins WHERE admin_id = '%s';
        """ %admin

        self.cur.execute(query)
        self.conn.commit()


    def close(self):
            self.conn.close()
