
import subprocess
import shutil
from pathlib import Path

# --------------------------------------------------
# AYARLAR
# --------------------------------------------------

VIDEO_DIR = Path("shorts_vertical")
SUBTITLE_DIR = Path("subtitles")
OUTPUT_DIR = Path("shorts_captioned")

OUTPUT_DIR.mkdir(exist_ok=True)

# Sadece yeni 8 Shorts
videos = [
    VIDEO_DIR / f"short_{i:02d}.mp4"
    for i in range(1, 9)
]

subtitles = [
    SUBTITLE_DIR / f"short_{i:02d}.srt"
    for i in range(1, 9)
]

# --------------------------------------------------
# KONTROLLER
# --------------------------------------------------

if shutil.which("ffmpeg") is None:
    print("❌ FFmpeg bulunamadı.")
    raise SystemExit(1)

print()
print("=" * 70)
print("🔥 PLAYREX - ALTYAZIYI VİDEOYA GÖMME")
print("=" * 70)
print()

success = 0

# --------------------------------------------------
# VİDEOLARI İŞLE
# --------------------------------------------------

for index, (video, subtitle) in enumerate(
    zip(videos, subtitles),
    start=1
):

    print("-" * 70)
    print(f"🎬 {index}/8")
    print(f"Video    : {video}")
    print(f"Altyazı  : {subtitle}")

    if not video.exists():
        print("   ❌ Video bulunamadı.")
        continue

    if not subtitle.exists():
        print("   ❌ SRT bulunamadı.")
        continue

    output = OUTPUT_DIR / f"short_{index:02d}.mp4"

    # Windows FFmpeg subtitle filtresi için
    subtitle_path = subtitle.resolve().as_posix()
    subtitle_path = subtitle_path.replace(":", "\\:")

    # --------------------------------------------------
    # ALTYAZI STİLİ
    #
    # FontSize  : 18
    # Beyaz     : yazı
    # Siyah     : kalın kenarlık
    # Alignment : 2 = alt orta
    # MarginV   : 260
    #
    # 1080x1920 Shorts için.
    # --------------------------------------------------

    subtitle_filter = (
        f"subtitles='{subtitle_path}':"
        "force_style="
        "'FontName=Arial,"
        "FontSize=18,"
        "PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,"
        "BorderStyle=1,"
        "Outline=4,"
        "Shadow=1,"
        "Alignment=2,"
        "MarginV=260'"
    )

    command = [
        "ffmpeg",
        "-y",

        "-i",
        str(video),

        "-vf",
        subtitle_filter,

        "-c:v",
        "libx264",

        "-preset",
        "veryfast",

        "-crf",
        "20",

        "-c:a",
        "aac",

        "-b:a",
        "128k",

        "-pix_fmt",
        "yuv420p",

        "-movflags",
        "+faststart",

        str(output)
    ]

    try:

        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        if result.returncode == 0 and output.exists():

            size_mb = output.stat().st_size / (1024 * 1024)

            print("   ✅ ALTYAZI VİDEOYA GÖMÜLDÜ")
            print(f"   📦 Boyut: {size_mb:.2f} MB")

            success += 1

        else:

            print("   ❌ FFmpeg HATASI")
            print()
            print(result.stderr[-2500:])

    except Exception as e:

        print("   ❌ Python hatası:")
        print(e)


# --------------------------------------------------
# SONUÇ
# --------------------------------------------------

print()
print("=" * 70)
print("🏁 ALTYAZI İŞLEMİ TAMAMLANDI")
print("=" * 70)

print(f"Toplam video : 8")
print(f"Başarılı     : {success}")
print(f"Başarısız    : {8 - success}")
print(f"Çıkış klasörü: {OUTPUT_DIR.resolve()}")

if success == 8:

    print()
    print("🔥🔥🔥 8 SHORTS ALTYAZILI OLARAK HAZIR!")

else:

    print()
    print("⚠️ Bazı videolarda hata oluştu.")

print()

