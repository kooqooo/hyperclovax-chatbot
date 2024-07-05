import os
import sys
from datetime import datetime
from uuid import uuid4

from dotenv import load_dotenv
from bson.objectid import ObjectId
import torch
from tqdm import tqdm
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

from backend.meetings import router as meeting_router
from backend.meetings import Attendee, Meeting
from backend.mongo_config import *
from backend.ip_addresses import get_public_ip, get_private_ip
from stt_inference import transcribe_audio_files_in_directory_with_model, transcribe_audio, atranscribe_audio_with_model
from audio_splitter import split_audio


load_dotenv()
PATH = os.path.dirname(os.path.abspath(__file__))
audio_files_path = os.path.join(PATH, "audio_files")

model_name = os.getenv("MODEL_NAME")
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = WhisperProcessor.from_pretrained(model_name)
model = WhisperForConditionalGeneration.from_pretrained(model_name).to(device)

async def upload_to_gridfs(file: UploadFile, bucket: AsyncIOMotorGridFSBucket) -> str:
    grid_in = bucket.open_upload_stream(file.filename)
    file_content = await file.read()
    await grid_in.write(file_content)
    await grid_in.close()
    return str(grid_in._id)

app = FastAPI()
app.include_router(meeting_router, prefix="/meetings", tags=["meetings"])

    
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/files")
async def upload_file(file: UploadFile = File(...)):
    # GridFS에 파일 업로드
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DATABASE_NAME]
    bucket = AsyncIOMotorGridFSBucket(db)
    
    file_id = await upload_to_gridfs(file, bucket)
    client.close()
    await file.seek(0)
    
    # 로컬에 임시 저장
    uuid = uuid4().hex
    uuid_path = os.path.join(audio_files_path, uuid)
    print("uuid_path:", uuid_path)
    os.makedirs(uuid_path, exist_ok=True)
    with open(os.path.join(uuid_path, file.filename), "wb") as f:
        f.write(await file.read())
    
    return JSONResponse(status_code=200, content={"file_id": str(file_id), "uuid": uuid})

@app.post("/segment/{uuid}")
async def segment_audio(uuid: str):
    uuid_path = os.path.join(audio_files_path, uuid)
    if not os.path.exists(uuid_path):
        raise HTTPException(status_code=404, detail="UUID not found")
    file_name = os.listdir(uuid_path)[0]
    file_path = os.path.join(uuid_path, file_name)
    output_dir = os.path.join(uuid_path, "outputs")
    try:
        num_files = split_audio(file_path, output_dir=output_dir)
        return JSONResponse(status_code=200, content={"num_files": num_files})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stt/{uuid}")
async def stt(uuid: str):
    uuid_path = os.path.join(audio_files_path, uuid)
    if not os.path.exists(uuid_path):
        raise HTTPException(status_code=404, detail="UUID not found")
    file_path = os.path.join(uuid_path, "outputs")
    try:
        transcriptions = transcribe_audio_files_in_directory_with_model(
            file_path,
            model=model,
            processor=processor,
            device=device
        )
        transcriptions = "\n\n".join(transcriptions)
        return JSONResponse(status_code=200, content={"transcript": transcriptions})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{file_id}")
async def download_file(file_id: str):
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DATABASE_NAME]
    bucket = AsyncIOMotorGridFSBucket(db)
    
    try:
        file_id = ObjectId(file_id) 
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    try:
        grid_out = await bucket.open_download_stream(file_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    finally:
        client.close()
    
    async def file_iterator():
        while True:
            chunk = await grid_out.readchunk()
            if not chunk:
                break
            yield chunk

    headers = {
        'Content-Disposition': f'attachment; filename="{grid_out.filename}"'
    }

    return StreamingResponse(file_iterator(), media_type='application/octet-stream', headers=headers)
    

if __name__ == "__main__":
    # private_ip = get_private_ip()
    uvicorn.run(app, host="0.0.0.0", port=8000)