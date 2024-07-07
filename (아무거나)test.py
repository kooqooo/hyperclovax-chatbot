# 테스트용 함수, 요청 예시
# def upload_meeting(audio_file_id: str, faiss_file_id: str = None):
def upload_meeting(audio_file_path: str, title: str, created_at: str):
    seoul_now_str = get_current_time()

    meeting = Meeting(
        title=seoul_now_str,
        transcript="회의록 전체 txt 경로",
        audio_file_id=audio_file_id,
        faiss_file_id=faiss_file_id if faiss_file_id else audio_file_id, # 이 부분은 Merge 이후 수정
        created_at=seoul_now,
    )
    
    request_data = meeting.model_dump_json()
    result = requests.post("http://localhost:8000/meetings/", data=request_data)
    return result.json()








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
    
    
    
    
    
    
    
    
    
######################### DELETE 부분 구현 시도 ################


def delete_mongoDB_data(doc_id: str):
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        deleted_meeting = await collection.find_one_and_delete({"_id": ObjectId(doc_id)})
        if deleted_meeting:
            return Meeting(**deleted_meeting)
        else:
            raise HTTPException(status_code=404, detail="Meeting not found")
    except errors.PyMongoError as e:
        logging.error(f"Failed to delete meeting: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete meeting")
    finally:
        client.close()



    