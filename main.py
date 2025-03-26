from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import subprocess

app = FastAPI()

@app.get("/download")
def download_video(link: str = Query(..., description="URL do Reels do Instagram")):
    try:
        result = subprocess.run(
            ["yt-dlp", "--cookies", "cookies.txt", "--print", "url", link],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return JSONResponse(status_code=500, content={"detail": result.stderr.strip()})
        return JSONResponse(content={"video_url": result.stdout.strip()})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})