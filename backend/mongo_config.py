import os
from dotenv import load_dotenv

# 환경 변수로부터 MongoDB 설정 읽기
load_dotenv()
username = os.getenv("MONGO_USERNAME", "admin")
password = os.getenv("MONGO_PASSWORD", "password")

# MongoDB connection URI
MONGO_URI = f"mongodb://{username}:{password}@localhost:27017/"
DATABASE_NAME = "database"
COLLECTION_NAME = "meetings"