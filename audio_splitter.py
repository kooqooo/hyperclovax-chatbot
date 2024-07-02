import os

from tqdm import tqdm
from pydub import AudioSegment
from pydub.silence import split_on_silence

def split_audio(file_path, min_silence_len=500, silence_thresh=-40, chunk_length=10000, output_dir="output"):
    # 파일 확장자에 따라 AudioSegment 로드
    audio = AudioSegment.from_file(file_path)
    
    # 음성 파일을 지정된 길이와 침묵 구간을 기준으로 분할
    chunks = split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=200  # 침묵 구간을 잘라낼 때 약간의 침묵을 유지
    )
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    chunk_start = 0
    part_number = 1
    current_chunk = AudioSegment.empty()

    for chunk in tqdm(chunks):
        current_chunk += chunk
        if len(current_chunk) >= chunk_length:
            chunk_filename = os.path.join(output_dir, f"part_{part_number}.mp3")
            current_chunk.export(chunk_filename, format="mp3")
            part_number += 1
            current_chunk = AudioSegment.empty()

    # 마지막 남은 조각 저장
    if len(current_chunk) > 0:
        chunk_filename = os.path.join(output_dir, f"part_{part_number}.mp3")
        current_chunk.export(chunk_filename, format="mp3")

    print(f"파일이 {part_number}개의 부분으로 분할되었습니다. 출력 디렉토리: {output_dir}")

# 스크립트 실행 예시
if __name__ == "__main__":
    file_path = "discord.mp3"  # 입력 파일 경로
    split_audio(file_path)