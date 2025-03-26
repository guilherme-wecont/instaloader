from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yt_dlp
import uuid
import subprocess
from pathlib import Path

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

@app.post("/process-video")
async def process_video(request: VideoRequest):
    video_id = str(uuid.uuid4())
    output_dir = Path("temp") / video_id
    output_dir.mkdir(parents=True, exist_ok=True)

    video_path = output_dir / "video.mp4"
    audio_path = output_dir / "audio.wav"
    image1_path = output_dir / "image1.jpg"
    image2_path = output_dir / "image2.jpg"

    try:
        ydl_opts = {
            'outtmpl': str(video_path),
            'cookiefile': 'cookies.txt'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([request.url])

        try:
            subprocess.run([
                'ffmpeg', '-i', str(video_path), '-vn',
                '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', str(audio_path)
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"FFmpeg error: {e.stderr.decode()}")

        try:
            subprocess.run([
                'ffmpeg', '-i', str(video_path), '-ss', '00:00:01.000', '-vframes', '1', str(image1_path)
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run([
                'ffmpeg', '-i', str(video_path), '-ss', '00:00:02.000', '-vframes', '1', str(image2_path)
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"FFmpeg image error: {e.stderr.decode()}")

        return {
            "audio": f"/{audio_path}",
            "images": [f"/{image1_path}", f"/{image2_path}"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))