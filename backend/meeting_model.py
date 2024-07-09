from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field
import pytz


class Attendee(BaseModel):
    name: str
    email: Optional[str] = None
    role: Optional[str] = None


class Meeting(BaseModel):
    title: Optional[str] = ''
    attendees: Optional[List[Attendee]] = []
    transcript: Optional[str] = None  # 대화 내용을 저장할 필드
    audio_file_id: Optional[str] = None  # GridFS에 저장된 음성 파일의 ID
    faiss_file_id: Optional[str] = None  # GridFS에 저장된 Faiss 파일의 ID
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=pytz.timezone('Asia/Seoul'))) # DB에 저장 기준 시간