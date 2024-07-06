import os

from dotenv import load_dotenv

from src.chat_completions import CompletionExecutor, RequestData, parse_response
from src.prompt_template import Prompts
from vectordb_manager import faiss_inference
from config import executor


def chat_with_rag(query: str, executor: CompletionExecutor = executor, k: int = 1) -> str:
    retrieval_result = faiss_inference(query, k)
    
    text = "- 너의 역할은 사용자의 질문에 reference를 바탕으로 답변하는거야. \n- 너가 가지고있는 지식은 모두 배제하고, 주어진 reference의 내용만을 바탕으로 답변해야해. \n- 만약 사용자의 질문이 reference와 관련이 없다면, {제가 가지고 있는 정보로는 답변할 수 없습니다.}라고만 반드시 말해야해."
    preset_prompts = Prompts.from_message("system", text)
    for retrieved in retrieval_result:
        preset_prompts.add_message("system", f"reference: {retrieved}")
    preset_prompts.add_message("user", query)

    request_data = RequestData(messages=preset_prompts.to_dict()).to_dict()
    result = executor.execute(request_data)
    
    return parse_response(result)

def main(query: str, k: int =1):

    result = chat_with_rag(query, executor, k)
    print(result)
    
    return result

if __name__ == "__main__":
    main()