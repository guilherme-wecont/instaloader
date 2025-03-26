from fastapi import FastAPI, Request
from pydantic import BaseModel
import subprocess
import uuid
import os
import shutil
from yt_dlp import YoutubeDL
import json

app = FastAPI()

# Rota para baixar o vídeo do Instagram
class ReelInput(BaseModel):
    url: str

@app.post("/download")
async def download_reel(data: ReelInput):
    url = data.url
    output_path = f"downloads/{uuid.uuid4()}"
    os.makedirs(output_path, exist_ok=True)

    ydl_opts = {
        "outtmpl": f"{output_path}/video.%(ext)s",
        "cookiesfrombrowser": ("chrome",),
        "quiet": True,
        "no_warnings": True,
        "format": "mp4"
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_url = info.get("url", "")

    return {"video_url": video_url}

# Rota para processar o vídeo: extrair áudio e imagens
@app.post("/process-video")
async def process_video(data: ReelInput):
    url = data.url
    session_id = str(uuid.uuid4())
    temp_dir = f"temp/{session_id}"
    os.makedirs(temp_dir, exist_ok=True)

    # Baixar o vídeo com yt-dlp
    video_path = f"{temp_dir}/video.mp4"
    ydl_opts = {
        "outtmpl": video_path,
        "cookiesfrombrowser": ("chrome",),
        "quiet": True,
        "no_warnings": True,
        "format": "mp4"
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Extrair áudio com ffmpeg
    audio_path = f"{temp_dir}/audio.wav"
    try:
        subprocess.run([
            "ffmpeg", "-i", video_path, "-vn",
            "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", audio_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        return {"detail": str(e)}

    # Extrair imagens com ffmpeg
    image1 = f"{temp_dir}/frame1.jpg"
    image2 = f"{temp_dir}/frame2.jpg"

    subprocess.run(["ffmpeg", "-i", video_path, "-ss", "00:00:01.000", "-vframes", "1", image1])
    subprocess.run(["ffmpeg", "-i", video_path, "-ss", "00:00:02.000", "-vframes", "1", image2])

    # Retorno com caminhos para o áudio e imagens
    return {
        "audio": f"https://your-domain.com/{audio_path}",
        "images": [
            f"https://your-domain.com/{image1}",
            f"https://your-domain.com/{image2}"
        ]
    }
