from datetime import datetime, timedelta
from typing import Union

def to_datetime(dt: str) -> datetime:
    return datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S.%fZ')

def to_iso(dt: datetime) -> str:
    return dt.isoformat(sep='T', timespec='milliseconds') + 'Z'

def to_unix_timestamp(dt:str) -> int:
    if not dt:
        return 0
    return int(datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())

def update_datetime_by_seconds(dt: Union[str, datetime], seconds: int) -> datetime:
    if type(dt) == str:
        dt = to_datetime(dt)
    new_dt = dt + timedelta(seconds=seconds)
    return new_dt
