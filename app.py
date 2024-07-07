import gradio as gr
import json
import requests

# 서버 URL
server_url = "http://127.0.0.1:8000/"

# api 받아오기
def get_answer(query: str, history) -> str:
    url = server_url + 'answer'
    response = requests.get(url, params={"query": query})
    return response.json()['result']

# ChatInterface 설정
iface = gr.ChatInterface(
        fn = get_answer,
        textbox=gr.Textbox(placeholder="질문을 입력하세요.", container=False, scale=7),
        title="질의응답 챗봇",
        description="질문에 답변합니다.",
        theme="soft",
        examples=[["다음 회의는 언제지?"], ["파이썬을 어디서 관리하는가?"], ["다음 회의까지 어떤 업무를 수행해야 하는가?"]],
        retry_btn="다시 보내기 ↩",
        undo_btn="이전 채팅 삭제 ❌",
        clear_btn="전체 채팅 삭제 💫"
)

# ChatInterface 실행
iface.launch()
