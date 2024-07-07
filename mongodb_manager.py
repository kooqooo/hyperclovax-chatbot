from bson import ObjectId
import logging
import os
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pymongo import ReturnDocument, errors
from motor.motor_asyncio import AsyncIOMotorClient
import pytz
import requests

from config import *

from typing import Any, List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4
from utils.seoul_time import get_current_time_str 

class Attendee(BaseModel):
    name: str
    email: Optional[str] = None
    role: Optional[str] = None

class Meeting(BaseModel):
    title: Optional[str] = ''
    # date: datetime # 회의 날짜 # 였는데 업로드된 파일의 메타데이터를 읽어오는 것이 어려움
    attendees: Optional[List[Attendee]] = []
    transcript: Optional[str] = None  # 대화 내용을 저장할 필드
    audio_file_id: Optional[str] = None  # GridFS에 저장된 음성 파일의 ID
    faiss_file_id: Optional[str] = None  # GridFS에 저장된 Faiss 파일의 ID
    # faiss_vector: Optional[List[float]] = None  # Faiss에 저장된 벡터
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=pytz.timezone('Asia/Seoul'))) # DB에 저장 기준 시간
    # updated_at: datetime = Field(default_factory=datetime.now)

def create_meeting(meeting: Meeting):
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        result = collection.insert_one(meeting.model_dump())
        created_meeting = collection.find_one({"_id": result.inserted_id})
        return Meeting(**created_meeting)
    except errors.PyMongoError as e:
        logging.error(f"Failed to create meeting: {e}")
        raise HTTPException(status_code=500, detail="Failed to create meeting")
    finally:
        client.close()


def save_to_mongoDB(page_content, title=get_current_time_str(), created_date=get_current_time_str()):
    uuid = uuid4().hex
    meeting = Meeting(
        title=title,
        transcript=page_content,
        audio_file_id=uuid, # mp3 파일 저장 시 필요
        faiss_file_id=uuid,
        created_at=created_date,
    )
    create_meeting(meeting)
    return uuid


def delete_mongoDB_data(doc_id: str):
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        deleted_meeting = collection.find_one_and_delete({"_id": ObjectId(doc_id)})
        if deleted_meeting:
            return Meeting(**deleted_meeting)
        else:
            raise HTTPException(status_code=404, detail="Meeting not found")
    except errors.PyMongoError as e:
        logging.error(f"Failed to delete meeting: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete meeting")
    finally:
        client.close()