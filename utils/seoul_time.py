from datetime import datetime
import pytz


def get_current_time_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def str_to_datetime(timestamp_str: str) -> datetime:
    """주어진 타임스탬프 문자열을 datetime 객체로 변환"""
    return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

def datetime_to_str(dt: datetime) -> str:
    """datetime 객체를 문자열 형식으로 변환"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def seoul_now() -> datetime:
    """현재 시간을 서울 시간대로 반환"""
    return datetime.now(tz=pytz.timezone('Asia/Seoul'))

def mongodb_to_datetime(mongodb_timestamp: str) -> datetime:
    """MongoDB의 타임스탬프 문자열을 datetime 객체로 변환"""
    if mongodb_timestamp[-1] == 'Z':
        mongodb_timestamp = mongodb_timestamp[:-1]
    return datetime.strptime(mongodb_timestamp, "%Y-%m-%dT%H:%M:%S.%f")

def convert_utc_to_seoul(utc_dt: datetime) -> datetime:
    utc_dt = utc_dt.replace(tzinfo=pytz.UTC)  # UTC 시간대 설정
    seoul_tz = pytz.timezone("Asia/Seoul")   # 서울 시간대
    seoul_dt = utc_dt.astimezone(seoul_tz)   # 서울 시간대로 변환
    return seoul_dt

if __name__ == "__main__":
    dt = mongodb_to_datetime("1970-01-01T00:00:00.000")
    seoul_dt = convert_utc_to_seoul(dt)
    datetime_str = datetime_to_str(seoul_dt)
    print(datetime_str)