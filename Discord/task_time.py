import asyncio 
from datetime import datetime, time, timedelta
import main

async def delay():
    time_now = datetime.now()
    time_now = time_now.strftime('%H')
    delay = datetime.now().strftime('%M %S')
    delay = int(delay[:2])*60+int(delay[3:])
    return delay

        