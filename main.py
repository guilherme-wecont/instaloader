import os
import uvicorn
import base64
import tempfile
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from instaloader import Instaloader, Post

app = FastAPI()

class ReelRequest(BaseModel):
    url: str

@app.post("/download-reel")
async def download_reel(request: ReelRequest):
    try:
        url = request.url
        shortcode = url.rstrip("/").split("/")[-1]

        # Setup instaloader
        loader = Instaloader(dirname_pattern=tempfile.gettempdir(), save_metadata=False, download_comments=False)
        
        post = Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target=shortcode)

        # Encontra o vídeo baixado
        folder = os.path.join(tempfile.gettempdir(), shortcode)
        video_path = next((os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".mp4")), None)

        if not video_path:
            raise Exception("Vídeo não encontrado")

        with open(video_path, "rb") as video_file:
            video_base64 = base64.b64encode(video_file.read()).decode("utf-8")

        # Limpeza
        for f in os.listdir(folder):
            os.remove(os.path.join(folder, f))
        os.rmdir(folder)

        return {
            "status": "success",
            "filename": os.path.basename(video_path),
            "video": f"data:video/mp4;base64,{video_base64}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000)