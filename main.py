import os
import sys
from datetime import datetime

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from gridfs import GridFSBucket
from motor.motor_asyncio import AsyncIOMotorClient

from backend.meetings import router as meeting_router
from backend.meetings import Attendee, Meeting
from backend.mongo_config import MONGO_URI, DATABASE_NAME, COLLECTION_NAME
from backend.ip_addresses import get_public_ip, get_private_ip
from stt_inference import transcribe_audio
from audio_splitter import asplit_audio

app = FastAPI()
app.include_router(meeting_router, prefix="/meetings", tags=["meetings"])

    
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/")
async def upload_file(file: UploadFile = File(...)):
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    bucket = GridFSBucket(db)
    try:
        # 오디오 파일 분할
        split_files = await asplit_audio(file)
        
        # STT
        transcriptions = []
        for split_file in split_files:
            transcription = transcribe_audio(split_file)
            transcriptions.append(transcription)
        
         # GridFS에 파일 업로드
        grid_in = bucket.open_upload_stream(file.filename)
        await grid_in.write(file.file.read())
        await grid_in.close()
        file_id = grid_in._id
        
        # 회의 정보 저장
        meeting = Meeting(
            title=file.filename,
            audio_file_id=file_id,
            transcript="\n\n".join(transcriptions)
        )
        collection.insert_one(meeting)
        
        return JSONResponse(status_code=200, content={"file_id": str(file_id), "transcriptions": transcriptions})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        client.close()

if __name__ == "__main__":
    # private_ip = get_private_ip()
    uvicorn.run(app, host="0.0.0.0", port=8000)