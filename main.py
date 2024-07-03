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
    return {"Hello": "World"}

@app.delete("/initalization")
async def read_root():
    init_faiss_index()
    return {"Init": "Complete"}

@app.get("/answer")
async def get_anawer(query: str):
    if query is None:
        raise HTTPException(status_code=400, detail="Query header not found")
    result = rag_main(query, 5)  # k개의 문서를 검색합니다.
    return {"result": result}

@app.delete("/document") # delete
# 아직 미완성. 이 함수는 구현 예정입니다.
async def delete_document(doc_id: Annotated[str | None, Header(convert_underscores=False)] = None):    
    print('doc_id:', doc_id)
    if doc_id is None:
        raise HTTPException(status_code=400, detail="doc_id header not found")  
    try: 
        delete_faiss_index(doc_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "success", "detail": "Document deleted"}

@app.put("/document") # add
async def add_meeting_data(data: Annotated[str | None, Header()] = None):

    if data is None:
        raise HTTPException(status_code=400, detail="Data header not found")
    try:
        data = json.loads(data)
        data_path = data.get("data_path"); title = data.get("title"); created_date = data.get("created_date")
        print('data_path:', data_path, 'title:', title, 'created_date:', created_date)
        '''
        mongoDB_id = save_to_mongoDB(page_content, title, created_date)   # 몽고디비 저장 로직 진행 -> vectordb_manager.py에서 구현?
        '''
        mongoDB_id = 1  # 임시로 설정
        data['doc_id'] = str(mongoDB_id)
        
        
        split_docs = get_split_docs(data_path, mongoDB_id)
        
        
        add_documents_to_faiss_index(split_docs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    return RedirectResponse(url="/success", status_code=303)

@app.get("/success")
async def success():
    # return {"status": "success", "detail": "Documents added to the FAISS index"}
    return {"status": "success", "detail": "방금 했던 요청 성공"}

@app.get("/faissdb")
async def show_data():
    return show_faiss_index()