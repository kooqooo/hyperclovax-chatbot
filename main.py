from typing import List, Optional, Annotated
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
import faiss, json, requests
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

from vectordb_manager import faiss_inference, init_faiss_index, add_documents_to_faiss_index, get_current_time, show_faiss_index, delete_faiss_index
from text_splitters import character_splitter, get_split_docs
from chat_completions_with_rag import rag_main

app = FastAPI()
faiss_store_name = "./faiss_index"
server_url = "http://127.0.0.1:8000/"

@app.on_event("startup")
async def startup_event():
    print("Server is starting up...")   # 시작 시 설정 있으면 구현 예정

@app.get("/")
async def read_root():
    return {"Hello": "Frontend!"}

@app.delete("/initalization")
async def read_root():
    init_faiss_index()
    # init_mongoDB()    # 필요 시 구현 예정입니다.
    return {"Init": "Complete"}

@app.get("/answer")
async def get_anawer(query: str):
    if query is None:
        raise HTTPException(status_code=400, detail="Query header not found")
    result = rag_main(query, 5)  # k개의 문서를 검색합니다.
    return {"result": result}

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

@app.put("/document") # add
async def add_meeting_data(data: Annotated[str | None, Header()] = None):

    if data is None:
        raise HTTPException(status_code=400, detail="Data header not found")
    try:
        data = json.loads(data)
        data_path = data.get("data_path"); title = data.get("title"); created_date = data.get("created_date")
        
        # mongoDB_id = save_to_mongoDB(page_content, title, created_date)   # 몽고디비 저장 로직 진행 -> vectordb_manager.py에서 구현?
        # 임시로 설정(mongoDB의 회의록 id)
        mongoDB_id = 1
        data['doc_id'] = str(mongoDB_id)
        
        add_documents_to_faiss_index(get_split_docs(data_path, mongoDB_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    return RedirectResponse(url="/success", status_code=303)

@app.get("/success")
async def success():
    return {"status": "success", "detail": "방금 했던 요청 성공"}

@app.get("/faissdb")
async def show_data():
    return show_faiss_index()