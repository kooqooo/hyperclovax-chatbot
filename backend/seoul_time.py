from datetime import datetime
import pytz


def str_to_datetime(timestamp_str: str) -> datetime:
    """주어진 타임스탬프 문자열을 datetime 객체로 변환"""
    return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

def datetime_to_str(dt: datetime) -> str:
    """datetime 객체를 문자열 형식으로 변환"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def seoul_now() -> datetime:
    """현재 시간을 서울 시간대로 반환"""
    return datetime.now(tz=pytz.timezone('Asia/Seoul'))