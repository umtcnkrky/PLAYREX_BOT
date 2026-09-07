import re
import subprocess
from pathlib import Path

VIDEO = "BF6_LIVE_PS5.mp4"
CANDIDATES = Path("clip_candidates.txt")
OUT_DIR = Path("shorts")

OUT_DIR.mkdir(exist_ok=True)

text = CANDIDATES.read_text(encoding="utf-8")

# START / END bilgilerini oku
matches = re.findall(
    r"START\s*:?\s*(\d+(?:\.\d+)?)\s*\n"
    r"END\s*:?\s*(\d+(?:\.\d+)?)",
    text
)

if not matches:
    print("ADAY BULUNAMADI!")
    raise SystemExit

print()
print("=" * 70)
print("PLAYREX ADAY KLİPLERİ OLUŞTURULUYOR")
print("=" * 70)

for i, (start, end) in enumerate(matches[:6], 1):

    start = float(start)
    end = float(end)
    duration = end - start

    output = OUT_DIR / f"candidate_{i}.mp4"

    print()
    print(f"ADAY {i}")
    print(f"Başlangıç : {start:.2f}")
    print(f"Bitiş     : {end:.2f}")
    print(f"Süre      : {duration:.1f}s")
    print(f"Dosya     : {output}")

    command = [
        "ffmpeg",
        "-y",

        # Kesim noktasına doğru şekilde git
        "-ss", f"{start:.2f}",
        "-i", VIDEO,

        # Süre
        "-t", f"{duration:.2f}",

        # Yeniden encode
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",

        # Ses
        "-c:a", "aac",
        "-b:a", "192k",

        # MP4 başlangıcını optimize et
        "-movflags", "+faststart",

        str(output)
    ]

    print("FFmpeg çalışıyor...")

    result = subprocess.run(command)

    if result.returncode == 0:
        print("✓ KLİP HAZIR")
    else:
        print("✗ KLİP OLUŞTURULAMADI")

print()
print("=" * 70)
print("TÜM ADAY KLİPLER HAZIR")
print("=" * 70)