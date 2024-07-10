import os
from typing import Annotated
from uuid import uuid4
import json

from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from fastapi import FastAPI, File, UploadFile, HTTPException, Header
from fastapi.responses import JSONResponse, StreamingResponse, RedirectResponse
import httpx
import uvicorn
import shutil

from config import *
from text_splitters import character_splitter, get_split_docs
from rag import main as rag_main
from backend.meetings import router as meeting_router
from backend.mongo_config import *
from stt_inference import transcribe_audio_files_in_directory_with_model
from audio_splitter import split_audio
from mongodb_manager import save_to_mongoDB, delete_mongoDB_data, init_mongoDB, show_mongoDB_data
from utils.seoul_time import get_current_time_str
from vectordb_manager import (
    load_faiss_index,
    save_faiss_index,
    create_faiss_index_from_documents,
    init_and_save_faiss_index,
    show_faiss_index,
    delete_faiss_index, 
    create_documents_from_texts,
    put_metadata_to_documents,
    add_documents_to_faiss_index
)

audio_files_path = os.path.join(PATH, "audio_files")

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

def init_local_data():
    try:
        shutil.rmtree(audio_files_path)
    except FileNotFoundError:
        print(f"The directory {audio_files_path} does not exist.")
    os.makedirs(audio_files_path, exist_ok=True)

@app.delete("/initialization")
async def read_root():
    init_and_save_faiss_index()
    await init_mongoDB()
    init_local_data()
    return {"Init": "Complete"}

@app.get("/success")
async def success():
    return {"status": "success", "detail": "방금 했던 요청 성공"}

@app.get("/showdb")
async def show_data():
    result = {"data":  {"FAISS": show_faiss_index(), "MongoDB": await show_mongoDB_data() } }
    return result

@app.get("/answer")
async def get_anawer(query: str):
    if query is None:
        raise HTTPException(status_code=400, detail="Query header not found")
    result = rag_main(query, 10)  # k개의 문서를 검색합니다.
    return {"result": result}

@app.put("/documents") # init or merge FAISS index
async def put_meeting_data(data: Annotated[str | None, Header()] = None):

    if data is None:
        raise HTTPException(status_code=400, detail="Data header not found")
    try:
        data = json.loads(data)
        transcript = data.get("transcript")
        time = data.get("time") # <class 'str'>
        meeting_id = data.get("meeting_id")

        faiss = load_faiss_index()

        transcripts = character_splitter.split_text(transcript)
        documents = create_documents_from_texts(transcripts)
        metadata = {"time": time, "meeting_id": meeting_id}
        documents = put_metadata_to_documents(documents, metadata)
        new_faiss = create_faiss_index_from_documents(documents)

        if faiss.index.ntotal > 0:
            new_faiss.merge_from(faiss)

        try:
            save_faiss_index(new_faiss)
        except Exception as e:
            print("Error:", e)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return RedirectResponse(url="/success", status_code=303)

@app.put("/document") # add
async def add_meeting_data(data: Annotated[str | None, Header()] = None):

    try:
        data = json.loads(data)
        uuid = data.get("uuid"); title = data.get("title"); created_date = data.get("created_date"); txt_path = data.get("txt_path")
        page_content=''
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                page_content = file.read()
        except FileNotFoundError:
            print(f"The file {txt_path} does not exist.")

        await save_to_mongoDB(uuid, page_content, title, created_date)
        add_documents_to_faiss_index(get_split_docs(txt_path, uuid))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    return {"file_id": uuid, "detail": "Upload Success"}

def delete_local_data(doc_id, audio_files_path):
    try:
        shutil.rmtree(os.path.join(audio_files_path, doc_id))
    except FileNotFoundError:
        print(f"The directory {doc_id} does not exist.")

@app.delete("/documents") # delete
async def delete_document(doc_id: Annotated[str | None, Header(convert_underscores=False)] = None):
    if doc_id is None:
        raise HTTPException(status_code=400, detail="doc_id header not found")  
    try:
        delete_faiss_index(doc_id)
        await delete_mongoDB_data(doc_id)
        delete_local_data(doc_id, audio_files_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return RedirectResponse(url="/success", status_code=303)

def save_audio_to_local(file: UploadFile, save_path):
    try:
        uuid = uuid4().hex
        uuid_path = os.path.join(audio_files_path, uuid)
        os.makedirs(uuid_path, exist_ok=True)
        with open(os.path.join(uuid_path, file.filename), "wb") as f:
            shutil.copyfileobj(file.file, f)
    
        return uuid, os.path.join(uuid_path, file.filename)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))   

def segment_and_STT(file_path) -> str:
    try:
        # Segment
        output_path = os.path.join(os.path.dirname(file_path), "outputs")
        num_files = split_audio(file_path, output_dir=output_path)   # mp3파일 위치, 분할된 파일 저장 폴더

        # STT
        transcriptions = transcribe_audio_files_in_directory_with_model(
            output_path,
            model=STT_MODEL,
            processor=PROCESSOR,
            device=DEVICE
        )
        transcriptions = "\n\n".join(transcriptions)

        # 확장자를 .txt로 변경해서 회의록 저장
        base, _ = os.path.splitext(file_path)
        txt_file_path = base + '.txt'
        with open(txt_file_path, 'w', encoding='utf-8') as file:
            file.write(transcriptions)
        
        return transcriptions, txt_file_path
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))   

@app.post("/process")
async def process_all(file: UploadFile = File(...)):
    '''
    유저가 mp3를 업로드
    mp3 로컬에 저장
    로컬에 저장한 경로를 참조해서 mp3 파일 분할
    분할된 파일 STT 수행 -> 전체 회의록 텍스트 제작
    data_path, title, created_date 선언
    이후의 로직 수행(save_to_mondoDB, add_faiss_document~)
    '''
    
    try:
        audio_files_directory = 'audio_files'    # 전역 변수로 뺄 수도 있음
        
        # 로컬에 저장
        uuid, file_path = save_audio_to_local(file, audio_files_directory)
        
        # 분할, STT 수행 + 제목, 생성일 지정
        page_content, txt_path = segment_and_STT(file_path)
        title = os.path.basename(file_path) # mp3파일 이름을 title로 지정
        created_date = get_current_time_str()

        # 요청 데이터 준비
        data= {
            "uuid": uuid,
            "page_content": page_content,
            "title": title,
            "created_date": created_date,
            "txt_path": txt_path
        }
        
        headers = {"Content-Type": "application/json", "data": json.dumps(data)}       
        async with httpx.AsyncClient() as client:
            response = await client.put("http://127.0.0.1:8000/document", headers=headers) #, headers=json.dumps(headers))

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e)) 
    return {"response": response.json()}
    # return RedirectResponse(url="/success", status_code=303)

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
            model=STT_MODEL,
            processor=PROCESSOR,
            device=DEVICE
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
    uvicorn.run(app, host="0.0.0.0", port=8000)