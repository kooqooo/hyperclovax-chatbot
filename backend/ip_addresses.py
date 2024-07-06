import os
import socket
import requests
from dotenv import load_dotenv


def get_public_ip():
    response = requests.get('https://checkip.amazonaws.com')
    public_ip = response.text.strip()
    return public_ip


def get_private_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        private_ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        hostname = socket.gethostname()
        private_ip = socket.gethostbyname(hostname)
    return private_ip


if __name__ == "__main__":
    load_dotenv()
    print(f"PUBLIC_IP: {os.getenv('PUBLIC_IP', get_public_ip())}")
    print(f"PRIVATE_IP: {os.getenv('PRIVATE_IP', get_private_ip())}")