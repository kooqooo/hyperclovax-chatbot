import os
import io

from fastapi import UploadFile
from tqdm import tqdm
from pydub import AudioSegment
from pydub.silence import split_on_silence

from utils.file_info_reader import get_file_stats, get_creation_time_from_file_stats, convert_timestamp_to_readable


def split_audio(file_path, min_silence_len=500, silence_thresh=-40, chunk_length=10000, output_dir="output"):
    filename = os.path.basename(file_path)
    filename, _ = os.path.splitext(filename)
    
    # 파일 확장자에 따라 AudioSegment 로드
    audio = AudioSegment.from_file(file_path)
    
    # 음성 파일을 지정된 길이와 침묵 구간을 기준으로 분할
    chunks = split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=200  # 침묵 구간을 잘라낼 때 약간의 침묵을 유지
    )
    
    if len(chunks) < 2:
        return 0
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    part_number = 1
    current_chunk = AudioSegment.empty()

    for chunk in tqdm(chunks):
        current_chunk += chunk
        if len(current_chunk) >= chunk_length:
            chunk_filename = os.path.join(output_dir, f"{filename}_{part_number:03d}.mp3")
            current_chunk.export(chunk_filename, format="mp3")
            part_number += 1
            current_chunk = AudioSegment.empty()

    # 마지막 남은 조각 저장
    if len(current_chunk) > 0:
        chunk_filename = os.path.join(output_dir, f"{filename}_{part_number:03d}.mp3")
        current_chunk.export(chunk_filename, format="mp3")

    print(f"파일이 {part_number}개의 부분으로 분할되었습니다. 출력 디렉토리: {output_dir}")
    return part_number

async def asplit_audio(file: UploadFile, min_silence_len=500, silence_thresh=-40, chunk_length=10000):
    # 업로드된 파일을 메모리에서 로드
    audio_data = await file.read()
    audio = AudioSegment.from_file(io.BytesIO(audio_data))
    
    # 음성 파일을 지정된 길이와 침묵 구간을 기준으로 분할
    chunks = split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=200  # 침묵 구간을 잘라낼 때 약간의 침묵을 유지
    )
    
    split_audio_files = []
    part_number = 1
    current_chunk = AudioSegment.empty()

    for chunk in tqdm(chunks):
        current_chunk += chunk
        if len(current_chunk) >= chunk_length:
            chunk_io = io.BytesIO()
            current_chunk.export(chunk_io, format="mp3")
            chunk_io.seek(0)
            split_audio_files.append(chunk_io)
            part_number += 1
            current_chunk = AudioSegment.empty()

    # 마지막 남은 조각 저장
    if len(current_chunk) > 0:
        chunk_io = io.BytesIO()
        current_chunk.export(chunk_io, format="mp3")
        chunk_io.seek(0)
        split_audio_files.append(chunk_io)

    print(f"파일이 {part_number}개의 부분으로 분할되었습니다.")
    return split_audio_files


# 스크립트 실행 예시
if __name__ == "__main__":
    file_path = "discord.mp3"  # 입력 파일 경로
    
    file_stats = get_file_stats(file_path)
    creation_time = get_creation_time_from_file_stats(file_stats)
    readable_creation_time = convert_timestamp_to_readable(creation_time)
    ctime = readable_creation_time.replace(" ", "_").replace(":", "-")
    
    output_dir = os.path.join("output", ctime)
    split_audio(file_path, output_dir=output_dir)