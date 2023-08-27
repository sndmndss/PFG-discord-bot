import sqlite3

from config import settings


class DataBase:
    def __init__(self):  # creates a connection with guild id database
        self.conn = conn = sqlite3.connect(f"../DataBases/guilds")
        self.c = conn.cursor()
        self.c.execute(""" CREATE TABLE IF NOT EXISTS id_table (
                                                guild_id integer PRIMARY KEY,
                                                logs_channel_id integer,
                                                microphone_channel_id integer
                                            ); """)
        self.extract()

    def create_statistic_table(self):
        self.c.execute(""" CREATE TABLE IF NOT EXISTS statistic (
                                                guild_id integer,
                                                category char(255),
                                                number integer,
                                                UNIQUE(guild_id, category)
                                            ); """)

    def save_statistic(self, category: str,
                       guild_id: int):
        self.c.execute('''INSERT OR IGNORE INTO statistic 
                       (guild_id, category, number) 
                       VALUES ((?), (?), 0)
                       ''', (guild_id, category,))
        self.c.execute(
            '''
                       UPDATE statistic SET number = number + 1 WHERE guild_id = (?) AND category = (?)
                       ''', (guild_id, category,))
        self.conn.commit()

    def save_id(self,
                guild_id: int,
                logs_channel_id: int | None,
                microphone_channel_id: int | None,
                statistic_channel_id: int | None):

        self.c.execute(f'''
            INSERT OR IGNORE INTO id_table (guild_id)

                    VALUES
                    ({guild_id})
                ''')
        if logs_channel_id is not None:
            self.c.execute(f'''
                UPDATE id_table SET logs_channel_id = (?) WHERE guild_id = {guild_id}
                    ''', (logs_channel_id,))
        if microphone_channel_id is not None:
            self.c.execute(f'''
                UPDATE id_table SET microphone_channel_id = (?) WHERE guild_id = {guild_id}
                ''', (microphone_channel_id,))
        if statistic_channel_id is not None:
            self.c.execute(f'''
                UPDATE id_table SET statistic_channel_id = (?) WHERE guild_id = {guild_id}
                ''', (statistic_channel_id,))
        self.conn.commit()
        self.extract()

    def reset(self,
              guild_id: int):  # resets from database row with guild id
        self.c.execute(f'''
                DELETE FROM id_table WHERE guild_id = (?)
                    ''', (guild_id,))
        self.extract()

    def extract(self):
        """creates 2 dicts like:
        guild_id, channel_id = int
        logs, mic_logs = dict({guild_id: channel_id})
        """
        self.c.execute('''
            SELECT *
            FROM id_table a
            ''')
        logs = dict()
        mic_logs = dict()
        for guild in self.c.fetchall():
            logs[guild[0]] = guild[1]
            mic_logs[guild[0]] = guild[2]

        self._update(logs, mic_logs)

    @staticmethod
    def _update(logs: dict,
                mic_logs: dict):  # saves 2 dicts to settings
        settings.LOGS_GUILD_LIST, settings.MICROPHONE_GUILD_LIST = logs, mic_logs

    def get_statistic(self):
        self.c.execute('''SELECT *
                        FROM statistic
                                ''')
        statistic = self.c.fetchall()
        yield statistic

    def _renew(self):
        self.c.execute('''DROP TABLE statistic;''')
        self.create_statistic_table()

    def get_id(self, guild_id: int) -> list[tuple]:
        self.c.execute('''SELECT statistic_channel_id 
                        FROM id_table 
                        WHERE guild_id = (?)
                        ''', (guild_id,))
        channel_id = []
        for _ in self.c.fetchall():
            channel_id.append(_)
        return channel_id
