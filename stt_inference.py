import os
import io

from transformers import WhisperForConditionalGeneration, WhisperProcessor
from fastapi import UploadFile
import torchaudio
import torch
from tqdm import tqdm

def transcribe_audio_files_in_directory(directory_path, model_name="maxseats/SungBeom-whisper-small-ko-set9"):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    processor = WhisperProcessor.from_pretrained(model_name)
    model = WhisperForConditionalGeneration.from_pretrained(model_name).to(device)
    model.eval()

    def process_file(audio_path):
        waveform, sample_rate = torchaudio.load(audio_path)
        
        # 필요한 경우 샘플링 레이트를 16kHz로 변환합니다.
        if sample_rate != 16000:
            transform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
            waveform = transform(waveform)
        
        # 오디오 파일을 Whisper 입력 형식으로 변환합니다.
        input_features = processor(waveform.squeeze().numpy(), sampling_rate=16000, return_tensors="pt").input_features.to("cuda")
        
        # 모델을 사용하여 추론합니다.
        with torch.no_grad():
            predicted_ids = model.generate(input_features)
            transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        
        # 텍스트 파일로 저장합니다.
        text_file_name = os.path.splitext(audio_path)[0] + ".txt"
        with open(text_file_name, "w", encoding="utf-8") as text_file:
            text_file.write(transcription)
        
        # print(f"Transcribed {audio_path} to {text_file_name}")

    def process_directory(path):
        # 디렉토리 내 모든 파일과 폴더를 확인합니다.
        for root, dirs, files in os.walk(path):
            for file_name in tqdm(files, desc=f"Processing files in {root}"):
                if file_name.endswith(".mp3") or file_name.endswith(".wav"):
                    audio_path = os.path.join(root, file_name)
                    process_file(audio_path)

    process_directory(directory_path)
    
    
def transcribe_audio_files_in_directory_with_model(
    directory_path,
    model: WhisperForConditionalGeneration,
    processor: WhisperProcessor,
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
    
    model.eval()

    transcriptions = []

    def process_file(audio_path):
        waveform, sample_rate = torchaudio.load(audio_path)
        
        # 필요한 경우 샘플링 레이트를 16kHz로 변환합니다.
        if sample_rate != 16000:
            transform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
            waveform = transform(waveform)
        
        # 오디오 파일을 Whisper 입력 형식으로 변환합니다.
        input_features = processor(waveform.squeeze().numpy(), sampling_rate=16000, return_tensors="pt").input_features.to(device)
        
        # 모델을 사용하여 추론합니다.
        with torch.no_grad():
            predicted_ids = model.generate(input_features)
            transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        
        # transcription을 리스트에 추가합니다.
        transcriptions.append(transcription)

    def process_directory(path):
        # 디렉토리 내 모든 파일과 폴더를 확인합니다.
        for root, dirs, files in os.walk(path):
            for file_name in tqdm(files, desc=f"Processing files in {root}"):
                if file_name.endswith(".mp3") or file_name.endswith(".wav"):
                    audio_path = os.path.join(root, file_name)
                    process_file(audio_path)

    process_directory(directory_path)
    
    return transcriptions


if __name__ == "__main__":
    directory_path = "output"
    transcribe_audio_files_in_directory(directory_path)
