import sys
import os
import traceback
import sqlite3
from sqlite3 import Error

class Database:

    DB_FILE = 'database/osintbot.db'
    USER_TABLE = """CREATE TABLE IF NOT EXISTS user (
                    id integer PRIMARY KEY,
                    tbl_guild_id text NOT NULL,
                    tbl_guild_name text NOT NULL,
                    tbl_user_id text NOT NULL,
                    tbl_user_name text NOT NULL,
                    tbl_user_role text NOT NULL,
                    tbl_user_lastused text DEFAULT CURRENT_TIMESTAMP,
                    tbl_user_response_mode text DEFAULT "mm"
                );"""
    CONF_TABLE = """CREATE TABLE IF NOT EXISTS conf (
                    id integer PRIMARY KEY,
                    tbl_guild_id text NOT NULL,
                    tbl_guild_name text NOT NULL,
                    tbl_global_response_mode text DEFAULT "off"
                );"""



 

    def __init__(self):
        connection = sqlite3.connect(':memory:')
        connection.set_trace_callback(lambda x: print(f"Traceback (most recent call last):\n  File '{x[0]}', line {x[1]}"))
        if not os.path.isfile(self.DB_FILE):
            os.makedirs(os.path.dirname(self.DB_FILE), exist_ok=True)
        self.db_create()

    def db_connect(self):
        try:
            connect = sqlite3.connect(self.DB_FILE)
            return connect
        except Error as e:
            print(e)
        return None
    
    def db_close(self, connect):
        if connect:
            connect.close()
    
    def db_create(self):
        try:
            connect = self.db_connect()
            cursor = connect.cursor()
            cursor.execute(self.USER_TABLE)
            cursor.execute(self.CONF_TABLE)
        except Error as e:
            print(e)
        finally:
            self.db_close(connect)

    def db_run_query(self, query, params = ()):
        try:
            connect = self.db_connect()
            cursor = connect.cursor()
            cursor.execute(query, params)
            connect.commit()
        except Error as e:
            print('SQLite error: %s' % (' '.join(e.args)))
            print("Exception class is: ", e.__class__)
            print("Query was: ", query)
            print("Params with type: ", params, type(params))
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
        finally:
            self.db_close(connect)

    def db_run_read_query(self, query, params = ()) -> list:
        try:
            connect = self.db_connect()
            cursor = connect.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        except Error as e:
            print('SQLite error: %s' % (' '.join(e.args)))
            print("Exception class is: ", e.__class__)
            print("Query was: ", query)
            print("Params with type: ", params, type(params))
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
        finally:
            self.db_close(connect)

    def db_insert_user(self, user_id: str, user_name: str, guild_id: str, guild_name: str) -> None:
        self.db_run_query(
            "INSERT INTO user (tbl_user_id, tbl_user_name, tbl_guild_id, tbl_guild_name, tbl_user_role) VALUES (?, ?, ?, ?, ?) ON CONFLICT DO NOTHING",
            (user_id, user_name, guild_id, guild_name, "user")
        )

    def db_insert_leader(self, user_id: str, user_name: str, guild_id: str, guild_name: str) -> None:
        self.db_run_query(
            "INSERT INTO user (tbl_user_id, tbl_user_name, tbl_guild_id, tbl_guild_name, tbl_user_role) VALUES (?, ?, ?, ?, ?) ON CONFLICT DO NOTHING",
            (user_id, user_name, guild_id, guild_name, "lead")
        )

    def db_insert_global_config(self, guild_id: str, guild_name: str) -> None:
        self.db_run_query(
            "INSERT INTO conf (tbl_guild_id, tbl_guild_name) VALUES (?, ?) ON CONFLICT DO NOTHING",
            (guild_id, guild_name)
        )

    def db_set_global_config(self, guild_id: str, user_id: str, config: str, value: str) -> None:
        self.db_run_query(
            f"UPDATE conf SET {config} = ? WHERE tbl_guild_id = ?",
            (value, guild_id)
        )

    def db_set_user_config(self, user_id: str, guild_id: str, config: str, value: str) -> None:
        self.db_run_query(
            f"UPDATE user SET {config} = ? WHERE tbl_user_id = ? AND tbl_guild_id = ?",
            (value, user_id, guild_id)
        )

    def db_get_global_config(self, guild_id: str, config: str = None) -> str:
        if config is None:
            config = self.db_run_read_query(
                "SELECT * FROM conf WHERE tbl_guild_id = ?",
                (guild_id,)
            )
            columns = self.db_run_read_query(
                "PRAGMA table_info(conf)"
            )
            response = {}
            config_dict = {}
            for i in range(len(columns)):
                config_dict[columns[i][1]] = config[0][i]
            config_dict.pop("id")
            config_dict.pop("tbl_guild_id")
            guild_name = config_dict.pop("tbl_guild_name")
            response[guild_name] = config_dict
            return response
        return self.db_run_read_query(
            f"SELECT {config} FROM conf WHERE tbl_guild_id = ?",
            (guild_id,)
        )[0][0]

    def db_get_user_config(self, user_id: str, guild_id: str, config: str = None) -> str:
        if config is None:
            config = self.db_run_read_query(
                "SELECT * FROM user WHERE tbl_user_id = ? AND tbl_guild_id = ?",
                (user_id, guild_id,)
            )
            columns = self.db_run_read_query(
                "PRAGMA table_info(user)"
            )
            response = {}
            config_dict = {}
            for i in range(len(columns)):
                config_dict[columns[i][1]] = config[0][i]
            config_dict.pop("id")
            config_dict.pop("tbl_guild_id")
            config_dict.pop("tbl_guild_name")
            config_dict.pop("tbl_user_id")
            config_dict.pop("tbl_user_role")
            config_dict.pop("tbl_user_lastused")
            user_name = config_dict.pop("tbl_user_name")
            response[user_name] = config_dict
            return response
        return self.db_run_read_query(
            f"SELECT {config} FROM user WHERE tbl_user_id = ? AND tbl_guild_id = ?",
            (user_id, guild_id,)
        )[0][0]





    def db_isleader(self, user_id: str, guild_id: str) -> bool:
        role = self.db_run_read_query("SELECT tbl_user_role FROM user WHERE tbl_user_id = ? AND tbl_guild_id = ?", (user_id, guild_id))
        role = role[0][0]
        if role == "lead":
            return True
        else:
            return False

    def db_dump(self, guild_id: str, table: str) -> str:
        if table == "user":
            dump = self.db_run_read_query("SELECT * FROM user WHERE tbl_guild_id = ?", (guild_id,))
        elif table == "conf":
            dump = self.db_run_read_query("SELECT * FROM conf WHERE tbl_guild_id = ?", (guild_id,))
        db_str = ""
        for row in dump:
            db_str += f"{row}\n"
        return db_str
