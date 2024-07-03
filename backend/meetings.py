import logging
import os
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pymongo import ReturnDocument, errors
from motor.motor_asyncio import AsyncIOMotorClient

# from managers.account_models import User, Record
from backend.mongo_config import *

from typing import Any, List, Optional
from pydantic import BaseModel, Field


class Attendee(BaseModel):
    name: str
    email: Optional[str] = None
    role: Optional[str] = None


class Meeting(BaseModel):
    id: Optional[str] = Field(None, alias="_id")  # MongoDB의 _id 필드와 매핑
    title: str
    date: datetime # 회의 날짜
    attendees: Optional[List[Attendee]] = []
    transcript: Optional[str] = None  # 대화 내용을 저장할 필드
    audio_file_id: Optional[str] = None  # GridFS에 저장된 음성 파일의 ID
    created_at: datetime = Field(default_factory=datetime.now) # DB에 저장 기준 시간
    updated_at: datetime = Field(default_factory=datetime.now)


router = APIRouter()

@router.get("/")
async def read_meetings():
    pass

@router.post("/")
async def create_meeting():
    meeting: Meeting
    return "hello"
    return meeting

@router.get("/{meeting_id}")
async def read_meeting(meeting_id: str):
    pass

@router.put("/{meeting_id}")
async def update_meeting(meeting_id: str):
    pass

@router.delete("/{meeting_id}")
async def delete_meeting(meeting_id: str):
    pass

