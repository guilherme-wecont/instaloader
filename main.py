
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import subprocess
import os
import uuid
import shutil
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Libera CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

@app.post("/process-video")
async def process_video(data: VideoRequest):
    url = data.url
    try:
        uid = str(uuid.uuid4())
        temp_dir = f"temp/{uid}"
        os.makedirs(temp_dir, exist_ok=True)

        video_path = f"{temp_dir}/video.mp4"
        audio_path = f"{temp_dir}/audio.m4a"
        audio_wav_path = f"{temp_dir}/audio.wav"
        image1_path = f"{temp_dir}/thumb1.jpg"
        image2_path = f"{temp_dir}/thumb2.jpg"

        # Baixar vídeo
        subprocess.run([
            "yt-dlp", "-f", "bv[ext=mp4]", "-o", video_path, "--cookies", "cookies.txt", url
        ], check=True)

        # Baixar áudio
        subprocess.run([
            "yt-dlp", "-f", "ba", "-o", audio_path, "--cookies", "cookies.txt", url
        ], check=True)

        # Converter áudio m4a para wav
        subprocess.run([
            "ffmpeg", "-i", audio_path, "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", audio_wav_path
        ], check=True)

        # Captura de imagens do vídeo
        subprocess.run(["ffmpeg", "-i", video_path, "-ss", "00:00:01.000", "-vframes", "1", image1_path], check=True)
        subprocess.run(["ffmpeg", "-i", video_path, "-ss", "00:00:02.500", "-vframes", "1", image2_path], check=True)

        return {
            "audio": f"/static/{uid}/audio.wav",
            "images": [
                f"/static/{uid}/thumb1.jpg",
                f"/static/{uid}/thumb2.jpg"
            ]
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"FFmpeg error: {str(e)}"})

@app.get("/static/{uid}/{filename}")
async def serve_static(uid: str, filename: str):
    file_path = f"temp/{uid}/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse(status_code=404, content={"detail": "Arquivo não encontrado"})
