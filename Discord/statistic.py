import asyncio 
from datetime import datetime, time, timedelta

async def background_task():
    WHEN = time(23,59,59)
    now = datetime.utcnow()
    if now.time() > WHEN:  
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        seconds = (tomorrow - now).total_seconds()  
        await asyncio.sleep(seconds)   
    while True:
        now = datetime.utcnow() 
        target_time = datetime.combine(now.date(), WHEN)  
        seconds_until_target = (target_time - now).total_seconds()
        await asyncio.sleep(seconds_until_target)  
        await called_once_a_day()  
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        seconds = (tomorrow - now).total_seconds()
        await asyncio.sleep(seconds)

        