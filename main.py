from typing import Optional
from fastapi import FastAPI, Header, HTTPException
from chat_completions_with_rag import rag_main

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # 서버 초기화 작업 (예: 데이터베이스 연결, 캐시 설정 등)
    print("Server is starting up... / 초기화 작업 여기서!")

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/answer")
async def get_anawer(query: str):
    if query is None:
        raise HTTPException(status_code=400, detail="Query header not found")
    
    print('받은 query:', query)
    
    result = rag_main(query)
    return {"result": result}