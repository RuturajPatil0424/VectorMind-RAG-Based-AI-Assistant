# Converts the video to mp3
import os
import subprocess
import re
import unicodedata
import hashlib
from pathlib import Path

VIDEO_DIR = "src/video"
AUDIO_DIR = "src/audio"
# META_FILE = "src/metadata/file_map.json"

os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
# os.makedirs(os.path.dirname(META_FILE), exist_ok=True)

avalable_files = os.listdir(VIDEO_DIR)
print(avalable_files)

def normalize_filename(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s_-]+", "_", name)
    return name.strip("_")

def short_hash(text: str, length: int = 8) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:length]

def convert_name(file_path: str) -> str:
    p = Path(file_path)
    base_name = p.stem          # original filename (no extension)
    ext = p.suffix              # original extension (.mp4, .mkv, etc.)
    normalized = normalize_filename(base_name)
    hash_id = short_hash(base_name)
    return f"{normalized}__{hash_id}{ext}"

def name_list(avalable_files):
    file_list = {}
    for file in avalable_files:
        new_name = convert_name(file)
        file_list[file] = new_name
    return file_list

def format_converter(file_dic, format="mp3"):
    for key, value in file_dic.items():
        subprocess.run(["ffmpeg", "-i", f"{VIDEO_DIR}/{key}", f"{AUDIO_DIR}/{value}.{format}"])

file_dic = name_list(avalable_files)
format_converter(file_dic, "mp3")

