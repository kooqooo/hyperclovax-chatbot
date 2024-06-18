""" Author: @kooqooo
LangChain Document Loader를 활용하여 HTML 파일을 로딩하는 예제입니다.
Raw Data에서 전처리하는 과정을 담고 있습니다.
"""

import os 
import json
import subprocess
from pathlib import Path
from typing import Any, List

from langchain_community.document_loaders.html import UnstructuredHTMLLoader


def txt_to_html():
    """
    txt -> html 및 원본 주소 mapping
    """
    url_to_filename_map = {}
    
    with open("clovastudiourl.txt", "r") as file:
        urls = [url.strip() for url in file.readlines()]

    folder_path = "clovastudioguide"

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for url in urls:
        filename = url.split("/")[-1] + ".html"
        file_path = os.path.join(folder_path, filename)
        subprocess.run(
            [
                "wget",
                "--user-agent='Mozilla/5.0'",
                "-O",
                file_path,
                url
            ],
            check=True)
        url_to_filename_map[url] = filename

    with open("url_to_filename_map.json", "w") as map_file:
        json.dump(url_to_filename_map, map_file, indent=4)

def load_html_with_langchain() -> List[List[Any]]:
    """
    LangChain으로 HTML 로딩
    """
    html_files_dir = Path(os.path.join(os.path.dirname(__file__),"clovastudioguide"))

    html_files = list(html_files_dir.glob("*.html"))
    
    clovastudiodatas = []
    
    for html_file in html_files:
        loader = UnstructuredHTMLLoader(str(html_file))
        document_data = loader.load()
        clovastudiodatas.append(document_data)
        # print(f"Processed {html_file}")
    
    return clovastudiodatas

def convert_metadata_source_to_url(clovastudiodatas: List[List[Any]]) -> List[Any]:
    """
    Mapping 정보를 활용해 'source'를 실제 URL로 수정
    """
    with open("url_to_filename_map.json", "r") as map_file:
        url_to_filename_map = json.load(map_file)
    
    filename_to_url_map = {v: k for k, v in url_to_filename_map.items()}
    
    # clovastudiodatas 리스트의 각 Document 객체의 'source' 수정
    for doc_list in clovastudiodatas:
        for doc in doc_list:
            extracted_filename = doc.metadata["source"].split("/")[-1]
            if extracted_filename in filename_to_url_map:
                doc.metadata["source"] = filename_to_url_map[extracted_filename]
            else:
                print(f"Warning: {extracted_filename}에 해당하는 URL을 찾을 수 없습니다.")


    # 이중 리스트를 풀어서 하나의 리스트로 만드는 작업
    clovastudiodatas_flattened = [item for sublist in clovastudiodatas for item in sublist]
    return clovastudiodatas_flattened


def main():
    txt_to_html()
    clovastudiodatas = load_html_with_langchain()
    clovastudiodatas_flattened = convert_metadata_source_to_url(clovastudiodatas)
    return clovastudiodatas_flattened

if __name__ == "__main__":
    clovastudiodatas_flattened = main()
    print("Done!")
