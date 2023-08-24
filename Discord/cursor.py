import sqlite3
import pandas as pd
from sys import path
from config import settings

# TODO: Searching row in database by name or id

class DataBase:
    def __init__(self): # creates a connection with guild id database
        self.conn = conn = sqlite3.connect(f'guilds')
        self.c = conn.cursor()
        self.c.execute(""" CREATE TABLE IF NOT EXISTS statistic (
                                        category char(255) PRIMARY KEY,
                                        number integer
                                    ); """)
        
    def save_statistic(self, category: str):
        self.c.execute('''INSERT OR IGNORE INTO statistic 
                       (category, number) 
                       VALUES ((?), 0)
                       ''', (category,))
        self.c.execute(
                       '''
                       UPDATE statistic SET number = number + 1 WHERE category = (?)
                       ''',(category,))
        self.conn.commit()
        
    


    def save_id(self, 
                guild_id: int, 
                logs_channel_id: int, 
                microphone_channel_id: int):
        
        self.c.execute(f'''
            INSERT OR IGNORE INTO id_table (guild_id)

                    VALUES
                    ({guild_id})
                ''')
        if logs_channel_id != None:
            self.c.execute(f'''
                UPDATE id_table SET logs_channel_id = (?) WHERE guild_id = {guild_id}
                    ''', (logs_channel_id,))
        if microphone_channel_id != None:
            self.c.execute(f'''
                UPDATE id_table SET microphone_channel_id = (?) WHERE guild_id = {guild_id}
                ''',(microphone_channel_id,))
        self.conn.commit()
        self._extract()


    def reset(self, 
              guild_id: int): # resets from database row with guild id
        self.c.execute(f'''
                DELETE FROM id_table WHERE guild_id = (?)
                    ''', (guild_id,))
        self._extract()
        

    def _extract(self): 
        '''creates 2 dicts like:
        guild_id, channel_id = int
        logs, mic_logs = dict({guild_id: channel_id})
        '''
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


    def _update(self, logs: dict, mic_logs: dict): # saves 2 dicts to settings
        settings.LOGS_GUILD_LIST, settings.MICROPHONE_GUILD_LIST = logs, mic_logs

    
        

    def show_table(self)-> pd.DataFrame: 
        self.c.execute('''
            SELECT *
            FROM statistic a
            ''')
        df = pd.DataFrame(self.c.fetchall())
        return df
    
    def delete_table(self):
        self.c.execute('''DROP TABLE statistic;''')
    

