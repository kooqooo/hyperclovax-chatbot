# README.md 작성하기

# 📝 Project 소개


저희 팀 “빅뱅”은 AI를 활용해 수많은 회의를 효과적으로 관리하자는 목표로 활동하였습니다. 주된 기능으로는 음성 파일에 STT 모델을 이용하여 자동 전사할 수 있고, 전사된 문서에서 질의응답 기능을 통해 원하는 정보를 빠르게 찾을 수 있습니다.


### 👀 Back-ground

> 기업 내, 기업 간 회의가 많아지면서 회의를 효과적으로 관리할 수 있는 AI 회의록 서비스가 등장하고 있지만 음성에서 텍스트로 변환하면서 오차가 많이 발생했으며 문서를 찾아보는 데 시간이 걸린다는 문제점들이 존재했습니다.
따라서 저희 “빅뱅”은 아래와 같은 방식으로 기존 서비스들의 문제점을 보완하여 회의를 효과적으로 관리하며 찾아볼 수 있도록 도움이 되고자합니다.
> 

**기존 서비스들과의 차별점**

1. 사용자에게 `음성 파일`을 입력으로 받아 `STT된 회의록`을 전달
2. 회의록 내용 중 특정 정보를 빠르게 찾을 수 있도록 `질의응답` 기능 추가
3. `한국어에 특화`되어 보다 정확한 회의록 전사 서비스
4. `Retriever 모델`을 기반으로 `LLM Generation`의 환각 축소

### 👆🏻위 내용들 거의 비슷하게 따라한거라 변형이 필요합니다.

# **👨‍👩‍👧‍👦 Members** 소개

### 💁🏻‍♂️ Members

| 구희찬 | 김민석 | 이상수 | 최예진 |
| --- | --- | --- | --- |
| <img src='https://avatars.githubusercontent.com/u/67735022?v=4' height=100 width=100></img> | <img src='https://avatars.githubusercontent.com/u/63552400?v=4' height=100 width=100></img> | <img src='https://github.com/boostcampaitech6/level2-klue-nlp-04/assets/118837517/344540c3-a093-4cb8-a694-61164a7380f8' height=100 width=100></img> | <img src='https://avatars.githubusercontent.com/u/69586041?v=4' height=100 width=100></img> |
| <a href="https://github.com/kooqooo" target="_blank"><img src="https://img.shields.io/badge/Github-black.svg?&style=round&logo=github"/></a> | <a href="https://github.com/maxseats" target="_blank"><img src="https://img.shields.io/badge/Github-black.svg?&style=round&logo=github"/></a> | <a href="https://github.com/SangSusu-git" target="_blank"><img src="https://img.shields.io/badge/Github-black.svg?&style=round&logo=github"/></a> | <a href="https://github.com/yeh-jeans" target="_blank"><img src="https://img.shields.io/badge/Github-black.svg?&style=round&logo=github"/></a> |

### 💁🏻‍♀️ 역할 소개

| 이름 | 역할 |
| --- | --- |
| 구희찬 | Git Repository 관리, FastAPI로 Back-End 개발, 챗봇용 Chat Completion 클래스 구현, 벡터 데이터베이스 탐색 및 Retrieval 구현, MongoDB CRUD 구현, 음성 및 텍스트 분할 구현, STT 파인튜닝 코드 작성, MLflow 로깅  코드 작성, API 요청 테스트 코드 작성 |
| 김민석 | FastAPI로 Back-End 개발, Gradio-FastAPI 통신, 데이터 라벨링, STT 모델 파인튜닝, 평가지표 제작 |
| 이상수 | Gradio로 Front-End 개발, Gradio-FastAPI 통신, 한국어 음성 데이터셋 탐색  및 구축, 음성 데이터 샘플링 레이트 전처리, 발화자를 자동으로 분리하여 발화자 기반 회의록 작성, STT 모델 파인튜닝, Retrieval(DPR) & Reader 모델 구현, RAG |
| 최예진 | Project Manager, 요구사항 명세서 작성, 협업 툴 관리, Gradio로 Front-End 개발, STT 모델 파인튜닝,  |

---

## 🧠 Product-Serving Architecture

프로젝트는 Gradio와 FastAPI를 사용하여 프론트엔드와 백엔드를 구축했습니다. 사용자는 Gradio를 통해 음성 파일을 업로드 할 수 있으며 STT 모델로 전사된 Text에서 질의응답 챗봇을 통해 원하는 정보를 빠르게 검색할 수 있습니다. DB는 Text의 원문을 저장하는 MongoDB와 Text가 청킹된 문서를 임베딩하여 벡터 형태로 저장하는 FAISS를 사용하였습니다. 이를 통해 사용자는 빠르고 편리하게 저장된 문서를 찾아볼 수 있습니다.

### **👀 Overview**

1. 음성 파일을 업로드합니다.
2. 긴 음성 파일은 STT가 어려우므로 10초 내외의 길이로 나누게 됩니다.
   - 이 과정에서 대화가 오가지 않는 침묵이 흐르는 부분은 포함되지 않습니다.
   - 따라서 분할된 음성 파일의 총합은 원본 파일보다 짧습니다.
3.  STT를 진행하고 결과로 회의 전문 텍스트가 나오게 됩니다.
4. 이 텍스트와 기타 메타데이터를 기반으로 MongoDB에 저장되어 관리됩니다.
5. 그리고 텍스트를 임베딩하는 과정이 필요한데 긴 텍스트는 임베딩이 어려우므로 적절하게 다시 분할합니다.
   - 임베딩은 사람이 이해할 수 있는 개체를 기계가 이해할 수 있는 벡터의 형태로 바꾸는 것입니다.
6. 임베딩된 벡터를 FAISS 벡터 데이터베이스에 저장합니다.
   - FAISS는 Facebook AI팀에서 개발한 유사도 검색을 위한 벡터 저장소입니다. CUDA 가속을 사용할 수 있어서 빠른 유사도 검색이 가능하다는 특징을 가지고 있습니다.
7. 위의 모든 준비 과정을 마치게 되면 사용자의 질문을 입력받습니다.
8. 입력된 사용자의 질문 또한 임베딩하여 벡터 데이터베이스에 있는 문서와 유사도가 높은 k개의 문서를 찾습니다.
9. 클로바 모델이 검색된 문서를 기반으로 사용자의 질문을 답변을 생성합니다.

### 구조도
<img src="https://github.com/future-tomorrow-work-experience-project/hyperclovax-chatbot/assets/67735022/b0e9e979-0e4b-4a34-9bae-b8d6ce21b98e" width="80%" height="80%"/>

<img src="https://github.com/future-tomorrow-work-experience-project/hyperclovax-chatbot/assets/67735022/6cf6807c-21ef-4240-9f4a-837ec6c71e2a" width="80%" height="80%"/>


## **📊 Model**

**1️⃣ STT fine-tuning**

- 허깅페이스에 업로드된 `openai/whisper-small` 모델을 한국어에 맞게 fine-tuning한 `SungBeom/whisper-small-ko` 모델에 추가적으로 fine-tuning한 모델을 사용

## **💿 Data**

- AI Hub에서 회의와 관련된 음성데이터를 api를 활용해 약 1TB 다운받고, 한 분야에 편향되지 않도록 섞어주었으며, Whisper 모델이 학습했던 샘플링 레이트 16kHz로 전처리 하여 학습 데이터셋 구축.
- STT 모델이 전사한 Text 데이터를 HyperClova X의 청킹 클래스를 활용하여 맥락에 맞는 문서로 분리해주어 Retriever에 활용

**2️⃣ Generation Model**

- 한국어에 특화된 네이버의 HyperClova X 사용
- Langchain을 이용하여 텍스트 분할 → 임베딩 → FAISS 벡터 데이터 베이스 관리
- Prompt Engineering 활용
    
    **✅ RAG**
    
   - FAISS Vector Database를 사용하여 사용자의 질의(query)에 유사도가 높은 Top-K의 문서를 검색
    
    **✅  LLM**
    
  - HyperClova X 모델은 검색된 문서를 기반으로 prompt에 맞게 답변 생성


