
import subprocess
import shutil
from pathlib import Path

# --------------------------------------------------
# AYARLAR
# --------------------------------------------------

INPUT_DIR = Path("shorts_vertical")
AUDIO_DIR = Path("subtitle_audio")
SUBTITLE_DIR = Path("subtitles")

AUDIO_DIR.mkdir(exist_ok=True)
SUBTITLE_DIR.mkdir(exist_ok=True)

# Sadece YENİ 8 aday
clips = [
    INPUT_DIR / f"short_{i:02d}.mp4"
    for i in range(1, 9)
]

# --------------------------------------------------
# KONTROLLER
# --------------------------------------------------

if shutil.which("ffmpeg") is None:
    print("❌ FFmpeg bulunamadı.")
    raise SystemExit(1)

existing = [clip for clip in clips if clip.exists()]

if not existing:
    print("❌ short_01.mp4 - short_08.mp4 bulunamadı.")
    raise SystemExit(1)

print()
print("=" * 65)
print("🎤 PLAYREX - ALTYAZI HAZIRLIK")
print("=" * 65)
print(f"İşlenecek video : {len(existing)}")
print()

# --------------------------------------------------
# VİDEOLARDAN SES ÇIKAR
# --------------------------------------------------

success = 0

for index, video in enumerate(existing, start=1):

    audio = AUDIO_DIR / f"short_{index:02d}.wav"

    print("-" * 65)
    print(f"🎬 {index}/{len(existing)}")
    print(f"Video : {video}")
    print(f"Ses   : {audio}")

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(video),

        # Whisper için temiz mono WAV
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",

        str(audio)
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

        if result.returncode == 0 and audio.exists():

            size_mb = audio.stat().st_size / (1024 * 1024)

            print("   ✅ SES ÇIKARILDI")
            print(f"   📦 Boyut: {size_mb:.2f} MB")

            success += 1

        else:

            print("   ❌ FFmpeg HATASI")
            print(result.stderr[-1500:])

    except Exception as e:

        print("   ❌ Python hatası:")
        print(e)

# --------------------------------------------------
# SONUÇ
# --------------------------------------------------

print()
print("=" * 65)
print("🏁 SES HAZIRLAMA TAMAMLANDI")
print("=" * 65)

print(f"Toplam video : {len(existing)}")
print(f"Başarılı     : {success}")
print(f"Ses klasörü  : {AUDIO_DIR.resolve()}")

if success == len(existing):

    print()
    print("🔥 TÜM SESLER WHISPER'A HAZIR!")

else:

    print()
    print("⚠️ Bazı ses dosyaları oluşturulamadı.")

print()

