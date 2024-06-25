import os

def load_data(data_dir):
    documents = []

    for filename in os.listdir(data_dir):
        if filename.endswith(".txt"):
            with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as file:
                content = file.read()
                # 문장 단위로 나누기
                sentences = content.split('.')
                documents.extend([sentence.strip() for sentence in sentences if sentence.strip()])

    return documents
# # 화자별 오디오 클립을 STT로 변환하여 출력
# for speaker_file in os.listdir('speaker_segments'):
#     if speaker_file.endswith('.wav'):
#         speaker_audio_path = os.path.join('speaker_segments', speaker_file)
#         result = model.transcribe(speaker_audio_path)
#         print(f"Transcription for {speaker_file}:")
#         print(result["text"])
