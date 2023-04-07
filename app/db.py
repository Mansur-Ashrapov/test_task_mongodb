import datetime
import json
import math

def _month_range(from_dt, to_dt):
    to_dt = datetime.datetime(to_dt.year, to_dt.month, to_dt.day, to_dt.hour, to_dt.minute, second=59)
    current = datetime.datetime(from_dt.year, from_dt.month, from_dt.day)
    next_date = datetime.datetime(from_dt.year, ((from_dt.month % 12) + 1), 1, hour=23, minute=59, second=59) - datetime.timedelta(days=1)

    diff = math.ceil(((to_dt - from_dt).days)/30)

    for _ in range(diff):
        if next_date > to_dt:
            break
        
        yield current, next_date    

        current = datetime.datetime(next_date.year, next_date.month, next_date.day) + datetime.timedelta(days=1)
        if current.month < 12:
            next_date = datetime.datetime(current.year, current.month + 1, 1, hour=23, minute=59, second=59) - datetime.timedelta(days=1)
        else:
            next_date = datetime.datetime(current.year + 1, 1, 1, hour=23, minute=59, second=59) - datetime.timedelta(days=1)

def _day_range(from_dt:datetime.datetime, to_dt:datetime.datetime):
    current = datetime.datetime(from_dt.year, from_dt.month, from_dt.day)
    next_date = datetime.datetime(from_dt.year, from_dt.month, from_dt.day) + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)

    diff = to_dt - from_dt
    ds = int(diff.days)

    while next_date < to_dt:

        yield current, next_date

        current = datetime.datetime(next_date.year, next_date.month, next_date.day) + datetime.timedelta(days=1)
        next_date = datetime.datetime(next_date.year, next_date.month, next_date.day) + datetime.timedelta(days=2) - datetime.timedelta(seconds=1)
    
    yield current, to_dt

def _hour_range(from_dt:datetime.datetime, to_dt:datetime.datetime):
    current = datetime.datetime(from_dt.year, from_dt.month, from_dt.day, from_dt.hour, from_dt.minute, from_dt.second) 
    next_date = current + datetime.timedelta(hours=1)

    diff = to_dt - from_dt
    diff_hours = int(math.ceil(diff.seconds/3600 + (diff.days * 24)))

    for _ in range(diff_hours + 1):
        if next_date > to_dt:
            yield current, to_dt
            break
        
        yield current, next_date

        if next_date == to_dt:
            yield next_date, to_dt
            break

        current = datetime.datetime(next_date.year, next_date.month, next_date.day, next_date.hour)
        next_date = current + datetime.timedelta(hours=1)

async def get_payments(dt_from, dt_to, type, client):
    range_types = {
        'hour': _hour_range,
        'month': _month_range,
        'day': _day_range
    }

    try:
        res = {'dataset':[], 'labels':[]}
        custom_range = range_types[type]

        for fr, t in custom_range(dt_from, dt_to):
            colls = await client.mydb["sample_collection"].find({"dt": {"$gte": fr, "$lt": t}}).to_list(10000000000)
            sum_ = sum((item['value'] for item in colls))
            res["dataset"].append(sum_)
            res["labels"].append(datetime.datetime.isoformat(fr))
            
        return json.dumps(res)

    except Exception as e:
        print(e)
