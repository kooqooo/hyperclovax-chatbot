"""Author: @kooqooo
pip install -U konlpy tiktoken sentence-transformers langchain_openai
위의 네 라이브러리를 추가적으로 설치해야 합니다.
"""

from langchain.text_splitter import (CharacterTextSplitter,
                                     KonlpyTextSplitter, 
                                     RecursiveCharacterTextSplitter,
                                     TokenTextSplitter,
                                     SentenceTransformersTokenTextSplitter,)
from transformers import BertTokenizerFast
# from langchain_experimental.text_splitter import SemanticChunker
# from langchain_openai.embeddings import OpenAIEmbeddings


def print_chunks(chunks):
    for i, chunk in enumerate(chunks):
        print(f"{i+1}:\n{chunk}\n")

character_splitter = CharacterTextSplitter(
    # separator="\n",    # 청크를 나눌 때 사용할 구분자, 기본값 = "\n\n"
    chunk_size=250,    # 각 청크의 최대 길이
    chunk_overlap=5   # 청크 간의 겹침 부분
)

recursive_character_splitter = RecursiveCharacterTextSplitter(
    separators=["\n", " "],
    chunk_size=100, # 차이를 보기 위해 작은 값으로 설정
    chunk_overlap=5
)

konlpy_splitter = KonlpyTextSplitter(
    separator="\n",    # 청크를 나눌 때 사용할 구분자, 기본값 = "\n\n"
    chunk_size=250,    # 각 청크의 최대 길이
    chunk_overlap=5   # 청크 간의 겹침 부분
)

tiktoken_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base",    # 기본값 "gpt2"
    chunk_size=250,    # 각 청크의 최대 길이
    chunk_overlap=5   # 청크 간의 겹침 부분
)

token_splitter = TokenTextSplitter(
    # encoding_name="gpt2",    
    chunk_size=250,    # 각 청크의 최대 길이
    chunk_overlap=5   # 청크 간의 겹침 부분
)

hf_tokenizer = BertTokenizerFast.from_pretrained("klue/roberta-small")
hf_token_splitter = CharacterTextSplitter.from_huggingface_tokenizer(
    hf_tokenizer, 
    chunk_size=250, 
    chunk_overlap=5
)

sentece_transformers_token_splitter = SentenceTransformersTokenTextSplitter(chunk_overlap=0)

def get_split_docs(data_path, doc_id):
    split_docs = TextLoader(data_path, encoding='utf-8').load_and_split(character_splitter)
    for idx, split_doc in enumerate(split_docs):
        split_docs[idx].metadata['doc_id'] = doc_id
    return split_docs

def main():
    # 예제 텍스트
    text = """
파이썬(영어: Python)은 1991년 네덜란드계 소프트웨어 엔지니어인 귀도 반 로섬이 발표한 고급 프로그래밍 언어로, '인터프리터를 사용하는 객체지향 언어'이자 플랫폼에 독립적인, 동적 타이핑(dynamically typed) 대화형 언어이다.

파이썬이라는 이름은 귀도가 좋아하는 코미디인〈Monty Python's Flying Circus〉에서 따온 것이다. 
이름에서 고대신화에 나오는 커다란 뱀을 연상하는 경우도 있겠지만 이와는 무관하다. 다만 로고에는 뱀 두마리가 형상화되어 있다.
간결하고 읽기 쉬운 문법이 특징인 프로그래밍 언어로 데이터 분석, 웹 개발, 인공지능 등 다양한 분야에서 활용된다.

파이썬은 비영리의 파이썬 소프트웨어 재단이 관리하는 개방형, 공동체 기반 개발 모델을 가지고 있다.

[출처] 위키백과
"""


    character_chunks = character_splitter.split_text(text)
    recursive_character_chunks = recursive_character_splitter.split_text(text)
    konlpy_chunks = konlpy_splitter.split_text(text)
    tiktoken_chunks = tiktoken_splitter.split_text(text)
    token_chunks = token_splitter.split_text(text)
    hf_token_chunks = hf_token_splitter.split_text(text)

    print("[Character Text Splitter]")
    print_chunks(character_chunks)
    print("="*80)

    print("[Recursive Character Text Splitter]")
    print_chunks(recursive_character_chunks) # 차이를 보기 위해 chunk_size를 작은 값으로 설정
    print("="*80)

    print("[Konlpy Text Splitter]")
    print_chunks(konlpy_chunks)
    print("="*80)

    print("[Tiktoken Text Splitter]")
    print_chunks(tiktoken_chunks)
    print("="*80)

    print("[Token Text Splitter]")
    print_chunks(token_chunks)
    print("="*80)

    print("[RoBERTa Token Text Splitter]")
    print_chunks(hf_token_chunks)
    print("="*80)

    print("[Sentence Transformers Token Text Splitter]")
    print(f"len of text: {len(text)}")
    print(f"len of words: {len(text.split())}")
    print(f"len of tokens: {sentece_transformers_token_splitter.count_tokens(text=text)-2}")


    # # Semantic Chunker
    # semantic_chunker = SemanticChunker(
    #     OpenAIEmbeddings(),
    #     breakpoint_threshold_type="percentile", # "standard_deviation", "interquartile"
    #     breakpoint_threshold_amount=70,
    # )
if __name__ == "__main__":
    main()
