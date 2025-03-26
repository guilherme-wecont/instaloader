
import subprocess
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
import os

app = FastAPI()

@app.post("/download")
async def download_video(request: Request):
    data = await request.json()
    url = data.get("url")
    if not url:
        return {"detail": "URL is required"}

    output_file = "output.mp4"

    command = [
        "yt-dlp",
        "--cookies", "cookies.txt",
        "-o", output_file,
        url
    ]

    try:
        subprocess.run(command, check=True)
        return FileResponse(output_file, filename=output_file)
    except subprocess.CalledProcessError as e:
        return {"detail": f"Download failed: {e}"}
