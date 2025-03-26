from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import yt_dlp
import uuid
import os

app = FastAPI()

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

class VideoRequest(BaseModel):
    url: str

@app.post("/download")
async def download_video(req: VideoRequest):
    video_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_DIR, f"{video_id}.%(ext)s")

    ydl_opts = {
        "outtmpl": output_template,
        "format": "mp4",
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.download([req.url])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Encontrar o arquivo baixado
    for file in os.listdir(DOWNLOAD_DIR):
        if file.startswith(video_id):
            return {"file_path": f"/{DOWNLOAD_DIR}/{file}"}

    raise HTTPException(status_code=500, detail="Arquivo não encontrado.")
