"""Author: @maxseats
mongoDB와 연동하여 데이터를 삽입/삭제/조회/초기화하는 로직을 이곳에 모아서 추가했어요.
main.py와 request_test.py에서 사용해요.
"""
import logging
import json

from bson.json_util import dumps
from fastapi import HTTPException
from pymongo import errors
from motor.motor_asyncio import AsyncIOMotorClient

from backend.meeting_model import Meeting
from config import *
from utils.seoul_time import get_current_time_str 

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


async def save_to_mongoDB(uuid, page_content, title=get_current_time_str(), created_date=get_current_time_str()):    
    meeting = Meeting(
        title=title,
        transcript=page_content,
        audio_file_id=uuid, # mp3 파일 저장 시 필요
        faiss_file_id=uuid,
        created_at=created_date,
    )
    await create_meeting(meeting)
    return

async def delete_mongoDB_data(doc_id: str):
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        deleted_meeting = await collection.find_one_and_delete({"audio_file_id": doc_id})
        if deleted_meeting:
            return Meeting(**deleted_meeting)
        else:
            return None
            raise HTTPException(status_code=404, detail="Meeting not found")
    except errors.PyMongoError as e:
        logging.error(f"Failed to delete meeting: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete meeting")
    finally:
        client.close()

async def init_mongoDB():
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        result = await collection.delete_many({})
        if result.deleted_count > 0:
            return {"status": "success", "deleted_count": result.deleted_count}
        else:
            return None
    except errors.PyMongoError as e:
        logging.error(f"Failed to delete all documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete all documents")
    finally:
        client.close()
        
async def show_mongoDB_data():
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        cursor = collection.find({})
        documents = await cursor.to_list(length=None)  # 모든 문서를 리스트로 변환
        result = json.loads(dumps(documents))
        print(result)
        return {"documents": result}
    except errors.PyMongoError as e:
        logging.error(f"Failed to retrieve documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve documents")
    finally:
        client.close()