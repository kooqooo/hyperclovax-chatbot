import os
import sys

import uvicorn
from fastapi import FastAPI, Request, Response, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from backend.meetings import router as meeting_router
from backend.ip_addresses import get_public_ip, get_private_ip

app = FastAPI()
app.include_router(meeting_router, prefix="/meetings", tags=["meetings"])

    
@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    # private_ip = get_private_ip()
    uvicorn.run(app, host="0.0.0.0", port=8000)