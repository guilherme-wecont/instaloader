
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
import instaloader
import os
import uuid

app = FastAPI()

# Cookies diretamente inseridos no código
COOKIES = {
    "sessionid": "73156571524%3A0u03Se-os1LGQRZ%3A%3AAyD0fxq_G1r-N83f8XafFUT8L4z6Q3YTLPzk92O-AqwA",
    "ds_user_id": "73156571524"
}

@app.post("/download-reel/")
async def download_reel(request: Request):
    try:
        data = await request.json()
        url = data.get("url")

        if not url:
            raise HTTPException(status_code=400, detail="URL do Reels não fornecida.")

        shortcode = url.strip("/").split("/")[-1]
        loader = instaloader.Instaloader(dirname_pattern="downloads", download_video_thumbnails=False)

        # Usar cookies diretamente
        loader.context.cookies.update({
            "sessionid": COOKIES["sessionid"],
            "ds_user_id": COOKIES["ds_user_id"]
        })

        profile = instaloader.Profile.from_id(loader.context, int(COOKIES["ds_user_id"]))
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        loader.download_post(post, target=str(uuid.uuid4()))

        for root, dirs, files in os.walk("downloads"):
            for file in files:
                if file.endswith(".mp4"):
                    return FileResponse(path=os.path.join(root, file), media_type="video/mp4", filename=file)

        raise HTTPException(status_code=404, detail="Vídeo não encontrado após o download.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
