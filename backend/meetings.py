from bson import ObjectId
import logging
import os
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, responses
from pymongo import ReturnDocument, errors
from motor.motor_asyncio import AsyncIOMotorClient
import pytz
import requests

from config import *
from backend.meeting_model import Meeting


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
        return responses.JSONResponse(content={"_id": str(result.inserted_id)})
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

# 테스트용 함수, 요청 예시
def upload_meeting(audio_file_id: str, faiss_file_id: str = None):
    seoul_now = datetime.now(tz=pytz.timezone('Asia/Seoul'))
    seoul_now_str = seoul_now.strftime("%Y-%m-%d %H:%M:%S")

    meeting = Meeting(
        title=seoul_now_str,
        transcript="진짜 긴내용\n\n",
        audio_file_id=audio_file_id,
        faiss_file_id=faiss_file_id if faiss_file_id else audio_file_id, # 이 부분은 Merge 이후 수정
        created_at=seoul_now,
    )
    
    request_data = meeting.model_dump_json()
    result = requests.post("http://localhost:8000/meetings/", data=request_data)
    return result.json()