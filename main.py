from fastapi import FastAPI, Request
from pydantic import BaseModel
import subprocess
import json

app = FastAPI()

class ReelRequest(BaseModel):
    url: str

@app.post("/download")
async def download_reel(request: ReelRequest):
    result = subprocess.run(
        ["yt-dlp", "-f", "mp4", "--cookies", "cookies.txt", "-j", request.url],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return {"detail": result.stderr}

    try:
        data = json.loads(result.stdout)
        video_url = data.get("url")
        return {"video_url": video_url}
    except Exception as e:
        return {"detail": f"Erro ao extrair URL do vídeo: {str(e)}"}
