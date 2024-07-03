from datetime import datetime
import pytz
from pydantic import BaseModel, Field


def str_to_datetime(timestamp_str: str) -> datetime:
    """주어진 타임스탬프 문자열을 datetime 객체로 변환"""
    return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

def get_seoul_timezone() -> datetime.tzinfo:
    """서울 시간대 (Asia/Seoul)를 반환"""
    return pytz.timezone("Asia/Seoul")

def localize_to_seoul(timestamp: datetime, timezone: datetime.tzinfo) -> datetime:
    """naive datetime 객체를 서울 시간대 기준으로 aware datetime 객체로 변환"""
    return timezone.localize(timestamp)

def format_datetime(dt: datetime) -> str:
    """datetime 객체를 문자열 형식으로 변환"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def seoul_now() -> datetime:
    """현재 시간을 서울 시간대로 반환"""
    seoul_tz = get_seoul_timezone()
    return datetime.now(seoul_tz)

class TimeModel(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=pytz.timezone('Asia/Seoul')))

    @classmethod
    def create_with_timestamp(cls, timestamp_str: str):
        """주어진 타임스탬프 문자열로 인스턴스를 생성"""
        timestamp = str_to_datetime(timestamp_str)
        seoul_tz = get_seoul_timezone()
        timestamp_seoul = localize_to_seoul(timestamp, seoul_tz)
        return cls(updated_at=timestamp_seoul)
    
if __name__ == "__main__":
    # 예시로 모델 인스턴스를 생성하여 현재 시간 확인
    instance1 = TimeModel()
    print(f"Formatted Updated_at (default): {format_datetime(instance1.created_at)}")

    # 명시적으로 입력할 경우
    timestamp_str = "1970-01-01 00:00:00"
    timestamp = str_to_datetime(timestamp_str)
    seoul_tz = get_seoul_timezone()
    timestamp_seoul = localize_to_seoul(timestamp, seoul_tz)

    instance2 = TimeModel(updated_at=timestamp_seoul)
    print(f"Formatted Updated_at (specified): {format_datetime(instance2.created_at)}")
