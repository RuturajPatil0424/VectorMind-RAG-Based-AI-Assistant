# Converts videos to mp3
import subprocess
import re
import unicodedata
import hashlib
from pathlib import Path

# VIDEO_DIR = Path("src/video")
# AUDIO_DIR = Path("src/audio")
#
# VIDEO_DIR.mkdir(parents=True, exist_ok=True)
# AUDIO_DIR.mkdir(parents=True, exist_ok=True)
#
# available_files = [f for f in VIDEO_DIR.iterdir() if f.is_file()]
# print([f.name for f in available_files])


def normalize_filename(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = name.lower()
    name = re.sub(r"[^\w\s-]", "", name)
    name = re.sub(r"[\s_-]+", "_", name)
    return name.strip("_")


def short_hash(text: str, length: int = 8) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:length]


def convert_name(file_path: Path) -> str:
    base_name = file_path.stem
    ext = file_path.suffix
    normalized = normalize_filename(base_name)
    hash_id = short_hash(base_name)
    return f"{normalized}__{hash_id}{ext}"


def name_list(files):
    return {file.name: convert_name(file) for file in files}


def format_converter(file_map, VIDEO_DIR, AUDIO_DIR, output_format="mp3"):
    for original, renamed in file_map.items():
        input_path = VIDEO_DIR / original
        output_path = AUDIO_DIR / f"{renamed}.{output_format}"

        subprocess.run(
            ["ffmpeg", "-i", str(input_path), str(output_path)],
            check=True
        )



