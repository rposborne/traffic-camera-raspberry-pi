import json
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
import os
import time

from traffic_camera.radar_status import RADAR_STATUS_PATH

from fastapi.staticfiles import StaticFiles
from datetime import timedelta

# set the root directory for python as the current directory
os.chdir(os.path.dirname(__file__))


app = FastAPI()

LPR_PHOTOS_DIR = "/home/rposborne/LPR_Speed_Photos"

app.mount("/public", StaticFiles(directory="public"), name="public")


@app.get("/api/radar")
async def radar_status():
    """Return the latest radar sample and whether the camera is still reporting."""
    try:
        with open(RADAR_STATUS_PATH, encoding="utf-8") as status_file:
            status = json.load(status_file)
    except (OSError, ValueError):
        return {"online": False, "last_speed": None, "last_seen": None}

    if not isinstance(status, dict):
        return {"online": False, "last_speed": None, "last_seen": None}

    heartbeat = status.get("heartbeat")
    online = isinstance(heartbeat, (int, float)) and 0 <= time.time() - heartbeat < 15
    return {
        "online": online,
        "last_speed": status.get("last_speed"),
        "last_seen": status.get("last_seen"),
    }


@app.get("/photos")
async def list_photos():
    try:
        files = os.listdir(LPR_PHOTOS_DIR)
        photos = [
            file for file in files if file.endswith((".jpg", ".jpeg", ".png", ".json"))
        ]
        return JSONResponse(content={"photos": photos})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/days")
async def list_days():
    try:
        files = os.listdir(LPR_PHOTOS_DIR)
        days = [
            file for file in files if os.path.isdir(os.path.join(LPR_PHOTOS_DIR, file))
        ]
        days.sort(reverse=True)  # Sort days in descending order (newest first)

        return JSONResponse(content={"days": days})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/images/{day}/{event}/{photo}")
async def get_image(day: str, event: str, photo: str):
    try:
        file_path = os.path.join(LPR_PHOTOS_DIR, day, event, photo)
        response = FileResponse(file_path)
        response.headers["Cache-Control"] = (
            f"public, max-age={int(timedelta(days=365).total_seconds())}"
        )
        return response
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/events/{day}")
async def list_events(day: str):
    try:
        files = os.listdir(os.path.join(LPR_PHOTOS_DIR, day))
        events = [
            {
                "name": file,
                "path": f"/event_details/{day}/{file}",
                "photos": [
                    {
                        "name": photo,
                        "type": "image"
                        if photo.endswith((".jpg", ".jpeg", ".png"))
                        else "json",
                        "path": f"/images/{day}/{file}/{photo}",
                        "metadata": json.load(
                            open(os.path.join(LPR_PHOTOS_DIR, day, file, photo))
                        )
                        if photo.endswith(".json")
                        else None,
                    }
                    for photo in os.listdir(os.path.join(LPR_PHOTOS_DIR, day, file))
                    if photo.endswith((".jpg", ".jpeg", ".png"))
                ],
            }
            for file in files
            if os.path.isdir(os.path.join(LPR_PHOTOS_DIR, day, file))
        ]

        return JSONResponse(content={"events": events})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/")
async def root():
    # serve the index.html file
    return FileResponse("public/index.html")


@app.get("/api/event_details/{day}/{event}")
async def event_details(day: str, event: str):
    try:
        photos = [
            {
                "name": photo,
                "type": "image"
                if photo.endswith((".jpg", ".jpeg", ".png"))
                else "json",
                "path": f"/images/{day}/{event}/{photo}",
                "metadata": get_metadata_for_photo(day=day, event=event, photo=photo),
            }
            for photo in os.listdir(os.path.join(LPR_PHOTOS_DIR, day, event))
            if photo.endswith(
                (
                    ".jpg",
                    ".jpeg",
                    ".png",
                )
            )
        ]

        return JSONResponse(content={"photos": photos, "name": event})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/event_details/{day}/{event}")
async def event_detail():
    return FileResponse("public/event_detail.html")


def get_metadata_for_photo(day, event, photo):
    try:
        return json.load(
            open(os.path.join(LPR_PHOTOS_DIR, day, event, photo))
            if photo.endswith(".json")
            else {}
        )
    except Exception:
        return {}
