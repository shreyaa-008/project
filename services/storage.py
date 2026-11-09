from pathlib import Path
from datetime import datetime
from PIL import Image
import io, re

ROOT=Path(__file__).resolve().parents[1]
UPLOADS=ROOT/"data"/"uploads"
VERSIONS=ROOT/"data"/"versions"
UPLOADS.mkdir(parents=True,exist_ok=True)
VERSIONS.mkdir(parents=True,exist_ok=True)

def safe_name(name):
    return re.sub(r"[^a-zA-Z0-9_-]+","_",Path(name).stem)[:60] or "image"

def save_upload(data,filename):
    image=Image.open(io.BytesIO(data)).convert("RGB")
    path=UPLOADS/f"{datetime.now():%Y%m%d_%H%M%S_%f}_{safe_name(filename)}.jpg"
    image.save(path,"JPEG",quality=92,optimize=True)
    return path

def save_version(data,image_id):
    folder=VERSIONS/str(image_id); folder.mkdir(parents=True,exist_ok=True)
    path=folder/f"edit_{datetime.now():%Y%m%d_%H%M%S_%f}.png"
    Image.open(io.BytesIO(data)).save(path,"PNG")
    return path
