import os
from typing import List, Optional, Annotated
from datetime import datetime
from uuid import uuid4
import json

from bson.objectid import ObjectId
from dotenv import load_dotenv
import torch
from tqdm import tqdm
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.responses import JSONResponse, StreamingResponse, RedirectResponse
import uvicorn

from vectordb_manager import init_and_save_faiss_index, add_documents_to_faiss_index, show_faiss_index, delete_faiss_index
from text_splitters import character_splitter, get_split_docs
from rag import main as rag_main
from backend.meetings import router as meeting_router
from backend.mongo_config import *
from stt_inference import transcribe_audio_files_in_directory_with_model
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

@app.on_event("startup")
async def startup_event():
    print("Server is starting up...")   # 시작 시 설정 있으면 구현 예정
    
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.delete("/initalization")
async def read_root():
    init_and_save_faiss_index()
    # init_mongoDB()    # 필요 시 구현 예정입니다.
    return {"Init": "Complete"}

@app.get("/success")
async def success():
    return {"status": "success", "detail": "방금 했던 요청 성공"}

@app.get("/faissdb")
async def show_data():
    return show_faiss_index()

@app.get("/answer")
async def get_anawer(query: str):
    if query is None:
        raise HTTPException(status_code=400, detail="Query header not found")
    result = rag_main(query, 5)  # k개의 문서를 검색합니다.
    return {"result": result}

@app.put("/document") # add
async def add_meeting_data(data: Annotated[str | None, Header()] = None):

    if data is None:
        raise HTTPException(status_code=400, detail="Data header not found")
    try:
        data = json.loads(data)
        data_path = data.get("data_path"); title = data.get("title"); created_date = data.get("created_date")
        
        # mongoDB_id = save_to_mongoDB(page_content, title, created_date)   # 몽고디비 저장 로직 진행 -> vectordb_manager.py에서 구현?
        # 임시로 설정(mongoDB의 회의록 id)
        mongoDB_id = '1'
        data['doc_id'] = mongoDB_id
        
        add_documents_to_faiss_index(get_split_docs(data_path, mongoDB_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    return RedirectResponse(url="/success", status_code=303)

@app.delete("/document") # delete
async def delete_document(doc_id: Annotated[str | None, Header(convert_underscores=False)] = None):
    if doc_id is None:
        raise HTTPException(status_code=400, detail="doc_id header not found")  
    try:
        delete_faiss_index(doc_id)
        # delete_mongoDB_Data(doc_id) # 몽고디비에서도 삭제를 해야 합니다.
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return RedirectResponse(url="/success", status_code=303)

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
