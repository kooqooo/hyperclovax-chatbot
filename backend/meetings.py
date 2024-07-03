from bson import ObjectId
import logging
import os
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pymongo import ReturnDocument, errors
from motor.motor_asyncio import AsyncIOMotorClient
import pytz

from mongo_config import *

from typing import Any, List, Optional
from pydantic import BaseModel, Field


class Attendee(BaseModel):
    name: str
    email: Optional[str] = None
    role: Optional[str] = None


class Meeting(BaseModel):
    title: Optional[str] = ''
    # date: datetime # 회의 날짜 # 였는데 업로드된 파일의 메타데이터를 읽어오는 것이 어려움
    attendees: Optional[List[Attendee]] = []
    transcript: Optional[str] = None  # 대화 내용을 저장할 필드
    audio_file_id: Optional[ObjectId] = None  # GridFS에 저장된 음성 파일의 ID
    faiss_file_id: Optional[ObjectId] = None  # GridFS에 저장된 Faiss 파일의 ID
    # faiss_vector: Optional[List[float]] = None  # Faiss에 저장된 벡터
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=pytz.timezone('Asia/Seoul'))) # DB에 저장 기준 시간
    # updated_at: datetime = Field(default_factory=datetime.now)


router = APIRouter()

@router.get("/", response_model=List[Meeting])
async def read_meetings():
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        meetings = collection.find({})
        documents = await meetings.to_list(length=None)  # Fetch all documents
        return documents
    except errors.PyMongoError as e:
        logging.error(f"Failed to read meetings: {e}")
        raise HTTPException(status_code=500, detail="Failed to read meetings")
    finally:
        client.close()

@router.post("/")
async def create_meeting(meeting: Meeting):
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        result = await collection.insert_one(meeting.model_dump())
        created_meeting = await collection.find_one({"_id": result.inserted_id})
        return Meeting(**created_meeting)
    except errors.PyMongoError as e:
        logging.error(f"Failed to create meeting: {e}")
        raise HTTPException(status_code=500, detail="Failed to create meeting")
    finally:
        client.close()

@router.get("/{meeting_id}", response_model=Meeting)
async def read_meeting(meeting_id: str):
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        meeting = await collection.find_one({"_id": ObjectId(meeting_id)})
        if meeting:
            return Meeting(**meeting)
        else:
            raise HTTPException(status_code=404, detail="Meeting not found")
    except errors.PyMongoError as e:
        logging.error(f"Failed to read meeting: {e}")
        raise HTTPException(status_code=500, detail="Failed to read meeting")
    finally:
        client.close()

@router.put("/{meeting_id}", response_model=Meeting)
async def update_meeting(meeting_id: str, meeting: Meeting):
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        updated_meeting = await collection.find_one_and_update(
            {"_id": ObjectId(meeting_id)},
            {"$set": meeting.model_dump()},
            return_document=ReturnDocument.AFTER
        )
        if updated_meeting:
            return Meeting(**updated_meeting)
        else:
            raise HTTPException(status_code=404, detail="Meeting not found")
    except errors.PyMongoError as e:
        logging.error(f"Failed to update meeting: {e}")
        raise HTTPException(status_code=500, detail="Failed to update meeting")
    finally:
        client.close()

@router.delete("/{meeting_id}", response_model=Meeting)
async def delete_meeting(meeting_id: str):
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        deleted_meeting = await collection.find_one_and_delete({"_id": ObjectId(meeting_id)})
        if deleted_meeting:
            return Meeting(**deleted_meeting)
        else:
            raise HTTPException(status_code=404, detail="Meeting not found")
    except errors.PyMongoError as e:
        logging.error(f"Failed to delete meeting: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete meeting")
    finally:
        client.close()
